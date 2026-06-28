from database.db import get_connection


class ChatRepository:

    def get_user_chats(self, user_id: int) -> list:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM chats WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def create_chat(self, user_id: int, title: str) -> int:
        conn = get_connection()
        cursor = conn.execute(
            "INSERT INTO chats (user_id, title) VALUES (?, ?)",
            (user_id, title)
        )
        chat_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return chat_id

    def update_title(self, chat_id: int, title: str):
        conn = get_connection()
        conn.execute("UPDATE chats SET title = ? WHERE id = ?", (title, chat_id))
        conn.commit()
        conn.close()

    def delete_chat(self, chat_id: int):
        conn = get_connection()
        conn.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
        conn.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
        conn.commit()
        conn.close()

    def add_message(self, chat_id: int, role: str, content: str, image_path: str = None) -> int:
        conn = get_connection()
        cursor = conn.execute(
            "INSERT INTO messages (chat_id, role, content, image_path) VALUES (?, ?, ?, ?)",
            (chat_id, role, content, image_path)
        )
        msg_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return msg_id

    def get_messages(self, chat_id: int) -> list:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM messages WHERE chat_id = ? ORDER BY created_at ASC",
            (chat_id,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]


chat_repository = ChatRepository()