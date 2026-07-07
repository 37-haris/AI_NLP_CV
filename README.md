# VisionChat — AI Image Captioning

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-0.137+-orange?style=flat-square&logo=fastapi" />
  <img src="https://img.shields.io/badge/Python-3.13-blue?style=flat-square&logo=python" />
  <img src="https://img.shields.io/badge/PyTorch-2.12+-red?style=flat-square&logo=pytorch" />
  <img src="https://img.shields.io/badge/Docker-ready-2496ED?style=flat-square&logo=docker" />
  <img src="https://img.shields.io/badge/Langfuse-traced-blueviolet?style=flat-square" />
</p>

A full-stack web application that uses a custom **VGG16 + LSTM** model to generate bilingual (English & French) captions for uploaded images. Built with FastAPI, secured with JWT authentication, and observable via Langfuse tracing.

---

## Demo

```
Upload image → AI generates English caption → Groq translates to French
             → Both displayed in a chat interface
             → Everything saved to history per user
```

---

## Features

- **AI Captioning** — Custom VGG16 + LSTM model with beam search (width=7)
- **Bilingual output** — English caption + French translation via Groq (LLaMA 3.1)
- **Authentication** — JWT stored in httponly cookies, auto-expiry after 1 hour
- **Chat history** — All conversations and images saved per user in SQLite
- **Observability** — Full tracing with Langfuse (BLEU, ROUGE, inference time, token usage)
- **Docs** — MkDocs documentation with flow diagrams and sequence diagrams
- **Docker** — Single command deployment with `docker compose up --build`

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.13) |
| AI Model | VGG16 + LSTM (PyTorch) |
| Translation | Groq API (LLaMA 3.1 8B) |
| Database | SQLite |
| Auth | JWT (`python-jose`) |
| Tracing | Langfuse |
| Frontend | Vanilla JS, HTML, CSS |
| Docs | MkDocs + Material theme |
| Deployment | Docker + Docker Compose |

---

## Project Structure

```
image-analysis/
├── main.py                    # FastAPI entry point
├── Dockerfile
├── docker-compose.yml
├── .env                       # secrets (never committed)
│
├── controller/                # HTTP routing
│   ├── page_controller.py     # GET /, GET /chat
│   ├── user_controller.py     # /auth/*
│   └── chat_controller.py     # /chats/*
│
├── service/                   # Business logic
│   ├── services.py            # Page rendering
│   ├── user_service.py        # Auth, JWT
│   └── chat_service.py        # Chat & image saving
│
├── repositories/              # DB queries
│   ├── user_repository.py
│   └── chat_repository.py
│
├── models/                    # SQL table definitions
│   ├── user_model.py
│   └── chat_model.py
│
├── schemas/                   # Pydantic models
│   ├── user_schema.py
│   └── chat_schema.py
│
├── database/
│   └── db.py                  # SQLite connection + init
│
├── AI_Model/
│   ├── Model_service.py       # VGG16 + LSTM inference + Langfuse
│   ├── best_model.pt          # Trained model weights
│   └── tokenizer.pkl          # Vocabulary
│
├── template/
│   ├── index.html             # Login / Register page
│   └── landing.html           # Chat page
│
├── static/
│   ├── style.css
│   ├── login.css
│   ├── script.js
│   ├── login.js
│   └── uploads/               # Saved user images
│
└── docs/                      # MkDocs documentation
```

---

## Getting Started

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker (optional, for containerized deployment)

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/image-analysis.git
cd "image analysis"

# 2. Install dependencies
uv sync

# 3. Set up environment variables
cp .env.example .env
# Edit .env and fill in your keys (see Environment Variables section)

# 4. Run the server
uvicorn main:app --reload

# 5. Open in browser
open http://127.0.0.1:8000
```

### Docker Setup

```bash
# Build and start all services
docker compose up --build -d

# App:      http://localhost:8000
# MLflow:   http://localhost:5001
```

---

## Environment Variables

Create a `.env` file at the project root:

```env
# JWT Secret — generate with: python3 -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your-secret-key-here

# Groq API — get from https://console.groq.com
GROQ_API_KEY=gsk_...

# Langfuse — get from https://cloud.langfuse.com
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

> **Never commit `.env` to Git.** Use `.env.example` as a template.

---

## Architecture

### Prediction Pipeline

```
User uploads image
      ↓
POST /auth/predict
      ↓
VGG16 feature extraction (4096-dim vector)
      ↓
LSTM beam search (width=7) → English caption
      ↓
Groq LLaMA 3.1 → French translation
      ↓
Save image to static/uploads/{user_id}/
Save messages to SQLite
      ↓
Return { en, fr, image_path }
```

### Layered Architecture

```
Controller → Service → Repository → Database
```

Each layer only communicates with the layer directly below it.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Login / Register page |
| `GET` | `/chat` | Chat page (auth required) |
| `POST` | `/auth/register` | Create account |
| `POST` | `/auth/login` | Login → sets JWT cookie |
| `GET` | `/auth/logout` | Logout → deletes cookie |
| `POST` | `/auth/predict` | Upload image → get captions |
| `GET` | `/chats/` | Get all user chats |
| `POST` | `/chats/` | Create new chat |
| `GET` | `/chats/{id}/messages` | Get chat history |
| `POST` | `/chats/{id}/messages` | Save message |
| `DELETE` | `/chats/{id}` | Delete chat |
| `GET` | `/documentation` | MkDocs site |
| `GET` | `/swagger` | Swagger UI |

---

## Observability

Every prediction is traced in **Langfuse** with:

- `feature_extraction_time` — VGG16 inference time
- `beam_search_time` — caption generation time
- `total_inference_time` — end-to-end
- `bleu_1`, `bleu_2`, `bleu_4` — BLEU scores
- `rouge_1_f`, `rouge_2_f`, `rouge_l_f` — ROUGE scores
- `prompt_tokens`, `completion_tokens` — Groq usage
- `translation_time_s` — Groq latency

View traces at [cloud.langfuse.com](https://cloud.langfuse.com).

---

## Documentation

```bash
# Serve docs locally
mkdocs serve --dev-addr 127.0.0.1:8001

# Build static docs
mkdocs build
```

Docs include architecture overview, flow diagrams, sequence diagrams, database schema, and full API reference.

---

## Database Schema

```
users
  └── chats (id, user_id, title, created_at)
        └── messages (id, chat_id, role, content, image_path, created_at)
```

---

## Contact

haris.karimi.fr@gmail.com