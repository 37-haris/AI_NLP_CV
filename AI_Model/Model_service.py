import io
import os
import pickle

import numpy as np
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from groq import Groq
from dotenv import load_dotenv

# ── Device ────────────────────────────────────────────────────────────────────
if torch.backends.mps.is_available():
    DEVICE = torch.device("mps")
elif torch.cuda.is_available():
    DEVICE = torch.device("cuda")
else:
    DEVICE = torch.device("cpu")

# ── Load tokenizer ────────────────────────────────────────────────────────────
_BASE     = os.path.dirname(os.path.abspath(__file__))
_TOK_PATH = os.path.join(_BASE, "..", "../image analysis/AI_Model/tokenizer.pkl")

with open(_TOK_PATH, "rb") as f:
    tok = pickle.load(f)

WORD2IDX   = tok["word2idx"]
IDX2WORD   = tok["idx2word"]
MAX_LENGTH = tok["max_length"]
VOCAB_SIZE = len(WORD2IDX)

# ── Model architecture (must match training exactly) ──────────────────────────
FEATURE_DIM = 4096
EMBED_DIM   = 256
LSTM_UNITS  = 256
DROPOUT     = 0.5

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

        self.output = nn.Linear(EMBED_DIM, VOCAB_SIZE)

    def forward(self, img_feat, cap_seq):
        x = self.img_bn(img_feat)
        x = self.img_drop(x)
        x = self.img_relu(self.img_dense(x))
        x = self.img_drop2(x)

        e = self.cap_drop(self.embedding(cap_seq))
        lstm_out, _ = self.lstm(e)
        h = self.cap_drop2(lstm_out[:, -1, :])

        return self.output(x + h)

# ── Load best_model.pt ────────────────────────────────────────────────────────
_MODEL_PATH = os.path.join(_BASE, "..", "../image analysis/AI_Model/best_model.pt")

model = CaptionModel().to(DEVICE)
model.load_state_dict(torch.load(_MODEL_PATH, map_location=DEVICE))
model.eval()

# ── VGG16 to extract image features (same as training) ───────────────────────
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

# ── Groq for French translation ───────────────────────────────────────────────
load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY", "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"))

# ── Public functions called by the controller ─────────────────────────────────
def describe_image(image_bytes: bytes) -> str:
    """Extract VGG16 features then run beam search with best_model.pt."""
    image  = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = img_transform(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        features = feature_extractor(tensor).squeeze(0).cpu().numpy()

    features = features / (np.linalg.norm(features) + 1e-8)

    return _beam_search(features)


def _beam_search(features: np.ndarray, beam_width: int = 7) -> str:
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

                logits = model(feat, cap_t)
                probs  = torch.softmax(logits, dim=-1)[0].cpu().numpy()

                for idx in np.argsort(probs)[-beam_width:]:
                    candidates.append((
                        score + np.log(probs[idx] + 1e-10),
                        seq + [int(idx)]
                    ))

            if not candidates:
                break

            beams = sorted(candidates, key=lambda x: x[0], reverse=True)[:beam_width]

    completed.extend(beams)
    best = max(completed, key=lambda x: x[0] / len(x[1]))[1]

    skip  = {start_idx, end_idx, 0}
    words = [IDX2WORD.get(i, "") for i in best if i not in skip]
    return " ".join(w for w in words if w).strip() or "No caption generated."


def translate_to_french(text: str) -> str:
    chat = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a professional translator. Translate to French. Return ONLY the translation."
            },
            {"role": "user", "content": text},
        ],
        temperature=0.3,
        max_tokens=512,
    )
    return chat.choices[0].message.content.strip()