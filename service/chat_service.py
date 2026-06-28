import os
import uuid
from fastapi import HTTPException
from repositories.chat_repository import chat_repository

UPLOAD_DIR = "static/uploads"


def save_image(image_bytes: bytes, user_id: int, filename: str) -> str:
    """Save image to disk and return the relative path."""
    user_dir = os.path.join(UPLOAD_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)

    ext      = os.path.splitext(filename)[-1] or ".jpg"
    unique   = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(user_dir, unique)

    with open(filepath, "wb") as f:
        f.write(image_bytes)

    return f"/static/uploads/{user_id}/{unique}"


class ChatService:

    def get_user_chats(self, user_id: int) -> list:
        return chat_repository.get_user_chats(user_id)

    def create_chat(self, user_id: int, title: str) -> dict:
        chat_id = chat_repository.create_chat(user_id, title)
        return {"chat_id": chat_id, "title": title}

    def get_messages(self, chat_id: int) -> list:
        return chat_repository.get_messages(chat_id)

    def save_message(self, chat_id: int, role: str, content: str, image_path: str = None) -> dict:
        if role not in ("user", "ai"):
            raise HTTPException(status_code=400, detail="Role must be 'user' or 'ai'.")
        msg_id = chat_repository.add_message(chat_id, role, content, image_path)
        return {"id": msg_id, "chat_id": chat_id, "role": role, "content": content, "image_path": image_path}

    def update_title(self, chat_id: int, title: str):
        chat_repository.update_title(chat_id, title)
        return {"message": "Title updated."}

    def delete_chat(self, chat_id: int):
        chat_repository.delete_chat(chat_id)
        return {"message": "Chat deleted."}


chat_service = ChatService()