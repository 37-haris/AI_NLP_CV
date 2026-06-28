# Getting Started

## Prerequisites

- Python 3.13+
- `uv` package manager

## Installation

```bash
# Clone the project
git clone <your-repo-url>
cd "image analysis"

# Create virtual environment and install dependencies
uv add fastapi uvicorn python-jose[cryptography] jinja2 python-multipart

# Generate a secure secret key
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Configuration

Set your secret key in `service/user_service.py`:

```python
SECRET_KEY = "paste-your-generated-key-here"
```

!!! warning "Never commit your SECRET_KEY to Git"
    Add it to a `.env` file and load it with `python-dotenv` for production.

## Running

```bash
uvicorn main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000)

## First Use

1. Go to `http://127.0.0.1:8000`
2. Click **S'inscrire** to register
3. Fill in your details and submit
4. Log in with your credentials
5. Upload an image in the chat
6. Receive English and French captions

## Database

The SQLite database (`users.db`) is created automatically on first startup. If you add new tables, run the migration manually:

```bash
sqlite3 users.db "ALTER TABLE messages ADD COLUMN image_path TEXT DEFAULT NULL;"
```

Or delete `users.db` and restart to recreate all tables from scratch.