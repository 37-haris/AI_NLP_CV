# Project Structure

```
image analysis/
│
├── main.py                          # FastAPI app entry point
├── mkdocs.yml                       # Documentation config
├── users.db                         # SQLite database (auto-created)
│
├── controller/                      # HTTP layer — routes only
│   ├── page_controller.py           # GET / and GET /chat
│   ├── user_controller.py           # /auth/* endpoints
│   └── chat_controller.py           # /chats/* endpoints
│
├── service/                         # Business logic layer
│   ├── services.py                  # PageService — template rendering
│   ├── user_service.py              # Auth logic, JWT, hashing
│   └── chat_service.py              # Chat & image saving logic
│
├── repositories/                    # Database query layer
│   ├── user_repository.py           # User CRUD queries
│   └── chat_repository.py           # Chat & message queries
│
├── models/                          # SQL table definitions
│   ├── user_model.py                # CREATE TABLE users
│   └── chat_model.py                # CREATE TABLE chats + messages
│
├── schemas/                         # Pydantic validation models
│   ├── user_schema.py               # Register/Login request+response
│   └── chat_schema.py               # Chat/Message request+response
│
├── database/
│   └── db.py                        # SQLite connection + init_db()
│
├── AI_Model/
│   └── Model_service.py             # describe_image() + translate_to_french()
│
├── template/                        # Jinja2 HTML templates
│   ├── index.html                   # Login / Register page
│   └── landing.html                 # Chat page
│
├── static/                          # Static assets
│   ├── style.css                    # Chat page styles
│   ├── login.css                    # Login page styles
│   ├── script.js                    # Chat page JS
│   ├── login.js                     # Login/register JS
│   └── uploads/                     # Saved user images
│       └── {user_id}/
│           └── {uuid}.jpg
│
└── docs/                            # MkDocs documentation
    ├── index.md
    ├── architecture/
    │   ├── overview.md
    │   ├── flow.md
    │   ├── sequences.md
    │   └── database.md
    ├── api/
    │   ├── auth.md
    │   ├── chat.md
    │   └── predict.md
    └── guides/
        ├── getting-started.md
        └── structure.md
```

## Naming Conventions

| Type | Convention | Example |
|---|---|---|
| Files | `snake_case` | `chat_service.py` |
| Classes | `PascalCase` | `ChatService` |
| Functions | `snake_case` | `get_user_chats()` |
| DB tables | `snake_case` | `chats`, `messages` |
| API routes | `kebab-case` | `/auth/register` |
| JS functions | `camelCase` | `loadChatList()` |