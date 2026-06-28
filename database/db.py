import sqlite3

DB_PATH = "users.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # rows behave like dicts
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Called once at startup to create all tables."""
    from models.user_model import CREATE_USERS_TABLE
    from models.chat_model import CREATE_CHATS_TABLE, CREATE_MESSAGES_TABLE
    conn = get_connection()
    conn.execute(CREATE_USERS_TABLE,)
    conn.execute(CREATE_CHATS_TABLE,)
    conn.execute(CREATE_MESSAGES_TABLE,)
    conn.commit()
    conn.close()