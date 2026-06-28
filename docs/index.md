# VisionChat — Image Captioning with AI

**VisionChat** is a web application that uses AI to generate bilingual (English & French) descriptions of uploaded images. Users authenticate securely, upload images in a chat interface, and receive AI-generated captions stored in a persistent chat history.

---

## Key Features

| Feature | Description |
|---|---|
| **Authentication** | JWT-based login/registration with secure httponly cookies |
| **Image Captioning** | AI model generates English descriptions from uploaded images |
| **Bilingual Output** | Descriptions are automatically translated to French |
| **Chat History** | All conversations and images are saved per user |
| **Session Security** | Automatic expiry, server-side logout, browser navigation blocked |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Database | SQLite |
| Auth | JWT via `python-jose` |
| Frontend | Vanilla JS, HTML, CSS |
| AI Model | Custom vision model + Groq translation |
| Docs | MkDocs + Material theme |

---

## Quick Start

```bash
# Install dependencies
uv add fastapi uvicorn python-jose[cryptography] jinja2 python-multipart

# Run the server
uvicorn main:app --reload

# Open in browser
open http://127.0.0.1:8000
```