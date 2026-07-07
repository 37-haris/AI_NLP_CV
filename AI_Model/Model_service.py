import io
import os
import time
import pickle

import numpy as np
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from groq import Groq
from dotenv import load_dotenv
from langfuse import observe, get_client
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer

# ── Load env ──────────────────────────────────────────────────────────────────
load_dotenv()

# ── Langfuse client ───────────────────────────────────────────────────────────
langfuse = get_client()

# ── Device ────────────────────────────────────────────────────────────────────
if torch.backends.mps.is_available():
    DEVICE = torch.device("mps")
elif torch.cuda.is_available():
    DEVICE = torch.device("cuda")
else:
    DEVICE = torch.device("cpu")

# ── Load tokenizer ────────────────────────────────────────────────────────────
_BASE     = os.path.dirname(os.path.abspath(__file__))
_TOK_PATH = os.path.join(_BASE, "tokenizer.pkl")

with open(_TOK_PATH, "rb") as f:
    tok = pickle.load(f)

WORD2IDX   = tok["word2idx"]
IDX2WORD   = tok["idx2word"]
MAX_LENGTH = tok["max_length"]
VOCAB_SIZE = len(WORD2IDX)

# ── Model architecture ────────────────────────────────────────────────────────
FEATURE_DIM = 4096
EMBED_DIM   = 256
LSTM_UNITS  = 256
DROPOUT     = 0.5
BEAM_WIDTH  = 7

class CaptionModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.img_bn    = nn.BatchNorm1d(FEATURE_DIM)
        self.img_drop  = nn.Dropout(DROPOUT)
        self.img_dense = nn.Linear(FEATURE_DIM, EMBED_DIM)
        self.img_relu  = nn.ReLU()
        self.img_drop2 = nn.Dropout(DROPOUT)
        self.embedding = nn.Embedding(VOCAB_SIZE, EMBED_DIM, padding_idx=0)
        self.cap_drop  = nn.Dropout(0.3)
        self.lstm      = nn.LSTM(EMBED_DIM, LSTM_UNITS, batch_first=True)
        self.cap_drop2 = nn.Dropout(0.3)
        self.output    = nn.Linear(EMBED_DIM, VOCAB_SIZE)

    def forward(self, img_feat, cap_seq):
        x = self.img_bn(img_feat)
        x = self.img_drop(x)
        x = self.img_relu(self.img_dense(x))
        x = self.img_drop2(x)
        e = self.cap_drop(self.embedding(cap_seq))
        lstm_out, _ = self.lstm(e)
        h = self.cap_drop2(lstm_out[:, -1, :])
        return self.output(x + h)

# ── Load model ────────────────────────────────────────────────────────────────
_MODEL_PATH = os.path.join(_BASE, "best_model.pt")
model = CaptionModel().to(DEVICE)
model.load_state_dict(torch.load(_MODEL_PATH, map_location=DEVICE))
model.eval()

# ── VGG16 feature extractor ───────────────────────────────────────────────────
_vgg = models.vgg16(weights=models.VGG16_Weights.IMAGENET1K_V1)
feature_extractor = nn.Sequential(
    *list(_vgg.children())[:-1],
    _vgg.avgpool,
    nn.Flatten(),
    _vgg.classifier[0],
    _vgg.classifier[1],
    _vgg.classifier[3],
    _vgg.classifier[4],
).to(DEVICE).eval()

img_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

# ── Groq client ───────────────────────────────────────────────────────────────
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))

# ── Scoring helper ────────────────────────────────────────────────────────────
def compute_scores(hypothesis: str, reference: str = None) -> dict:
    """
    Compute BLEU and ROUGE scores.
    If no reference is provided, uses the hypothesis itself as a self-reference
    (gives a baseline score of 1.0 — useful for logging without ground truth).
    In production you would pass the actual reference caption.
    """
    hyp_tokens = hypothesis.lower().split()
    ref_tokens = reference.lower().split() if reference else hyp_tokens

    # BLEU
    smoother  = SmoothingFunction().method1
    bleu1 = sentence_bleu([ref_tokens], hyp_tokens, weights=(1, 0, 0, 0), smoothing_function=smoother)
    bleu2 = sentence_bleu([ref_tokens], hyp_tokens, weights=(0.5, 0.5, 0, 0), smoothing_function=smoother)
    bleu4 = sentence_bleu([ref_tokens], hyp_tokens, weights=(0.25, 0.25, 0.25, 0.25), smoothing_function=smoother)

    # ROUGE
    scorer  = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    ref_str = reference if reference else hypothesis
    scores  = scorer.score(ref_str, hypothesis)

    return {
        "bleu_1":    round(bleu1, 4),
        "bleu_2":    round(bleu2, 4),
        "bleu_4":    round(bleu4, 4),
        "rouge_1_f": round(scores["rouge1"].fmeasure, 4),
        "rouge_2_f": round(scores["rouge2"].fmeasure, 4),
        "rouge_l_f": round(scores["rougeL"].fmeasure, 4),
    }


# ── Public functions ──────────────────────────────────────────────────────────
@observe(name="image_captioning")
def describe_image(image_bytes: bytes, reference: str = None) -> str:
    """
    Extract VGG16 features, run beam search, compute BLEU+ROUGE, log to Langfuse.
    Pass `reference` if you have a ground truth caption to compare against.
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Feature extraction
    t0     = time.time()
    tensor = img_transform(image).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        features = feature_extractor(tensor).squeeze(0).cpu().numpy()
    features  = features / (np.linalg.norm(features) + 1e-8)
    feat_time = round(time.time() - t0, 4)

    # Caption generation
    t1        = time.time()
    caption   = _beam_search(features)
    beam_time = round(time.time() - t1, 4)

    # Compute BLEU + ROUGE
    nlp_scores = compute_scores(caption, reference)

    langfuse.update_current_generation(
        output={"caption_en": caption},
        metadata={
            "device":                  str(DEVICE),
            "beam_width":              BEAM_WIDTH,
            "vocab_size":              VOCAB_SIZE,
            "feature_extraction_time": feat_time,
            "beam_search_time":        beam_time,
            "total_inference_time":    round(feat_time + beam_time, 4),
            "word_count":              len(caption.split()),
            # ── NLP metrics ──────────────────────────────────────────────────
            "bleu_1":                  nlp_scores["bleu_1"],
            "bleu_2":                  nlp_scores["bleu_2"],
            "bleu_4":                  nlp_scores["bleu_4"],
            "rouge_1_f":               nlp_scores["rouge_1_f"],
            "rouge_2_f":               nlp_scores["rouge_2_f"],
            "rouge_l_f":               nlp_scores["rouge_l_f"],
        },
    )

    return caption


def _beam_search(features: np.ndarray, beam_width: int = BEAM_WIDTH) -> str:
    feat      = torch.tensor(features, dtype=torch.float32).unsqueeze(0).to(DEVICE)
    start_idx = WORD2IDX["startseq"]
    end_idx   = WORD2IDX["endseq"]
    beams     = [(0.0, [start_idx])]
    completed = []

    with torch.no_grad():
        for _ in range(MAX_LENGTH):
            candidates = []
            for score, seq in beams:
                if seq[-1] == end_idx:
                    completed.append((score, seq))
                    continue
                pad_len = MAX_LENGTH - len(seq)
                padded  = [0] * pad_len + seq
                cap_t   = torch.tensor([padded], dtype=torch.long).to(DEVICE)
                logits  = model(feat, cap_t)
                probs   = torch.softmax(logits, dim=-1)[0].cpu().numpy()
                for idx in np.argsort(probs)[-beam_width:]:
                    candidates.append((
                        score + np.log(probs[idx] + 1e-10),
                        seq + [int(idx)]
                    ))
            if not candidates:
                break
            beams = sorted(candidates, key=lambda x: x[0], reverse=True)[:beam_width]

    completed.extend(beams)
    best  = max(completed, key=lambda x: x[0] / len(x[1]))[1]
    skip  = {start_idx, end_idx, 0}
    words = [IDX2WORD.get(i, "") for i in best if i not in skip]
    return " ".join(w for w in words if w).strip() or "No caption generated."


@observe(name="groq_translation", as_type="generation")
def translate_to_french(text: str) -> str:
    t0   = time.time()
    chat = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a professional translator and sentiment analysis. Translate to French. Return ONLY the translation and sentiment with an emoji and description."
            },
            {"role": "user", "content": text},
        ],
        temperature=0.3,
        max_tokens=512,
    )
    result = chat.choices[0].message.content.strip()

    langfuse.update_current_generation(
        model="llama-3.1-8b-instant",
        usage_details={
            "input":  chat.usage.prompt_tokens,
            "output": chat.usage.completion_tokens,
            "total":  chat.usage.total_tokens,
        },
        metadata={"translation_time_s": round(time.time() - t0, 4)},
    )

    return result