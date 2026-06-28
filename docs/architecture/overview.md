# Architecture Overview

VisionChat follows a **layered architecture** pattern, separating concerns across distinct layers. Each layer only communicates with the layer directly below it.

## Layer Responsibilities

| Layer | Files | Responsibility |
|---|---|---|
| **Controller** | `controller/*.py` | HTTP routing, request/response handling |
| **Service** | `service/*.py` | Business logic, validation, hashing |
| **Repository** | `repositories/*.py` | All database queries |
| **Model** | `models/*.py` | SQL table definitions |
| **Schema** | `schemas/*.py` | Pydantic request/response validation |
| **Database** | `database/db.py` | SQLite connection, table creation |

## Call Chain

```
HTTP Request
     ↓
Controller      ← validates request shape (Pydantic schema)
     ↓
Service         ← business logic (hashing, JWT, error raising)
     ↓
Repository      ← raw SQL queries only
     ↓
Database        ← SQLite connection
```

## Key Design Decisions

!!! info "Why SQLite?"
    The app is a single-user demo project. SQLite requires zero configuration and ships with Python. Switching to PostgreSQL later requires only changing the connection string in `database/db.py`.

!!! info "Why httponly cookies for JWT?"
    Storing the JWT in `localStorage` or `sessionStorage` exposes it to XSS attacks. An `httponly` cookie cannot be read by JavaScript, making token theft much harder.

!!! info "Why save images to disk?"
    Storing binary image data in SQLite bloats the database and slows queries. Saving to `static/uploads/{user_id}/` keeps the DB lean and lets FastAPI serve images directly as static files.