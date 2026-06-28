CREATE_CHATS_TABLE = """
    CREATE TABLE IF NOT EXISTS chats (
        id         INTEGER  PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER  NOT NULL,
        title      TEXT     NOT NULL DEFAULT 'New conversation',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
"""

CREATE_MESSAGES_TABLE = """
    CREATE TABLE IF NOT EXISTS messages (
        id         INTEGER  PRIMARY KEY AUTOINCREMENT,
        chat_id    INTEGER  NOT NULL,
        role       TEXT     NOT NULL CHECK(role IN ('user', 'ai')),
        content    TEXT     NOT NULL,
        image_path TEXT     DEFAULT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (chat_id) REFERENCES chats(id)
    )
"""