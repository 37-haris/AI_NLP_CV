from pydantic import BaseModel
from typing import Optional


class NewChatRequest(BaseModel):
    title: str = "New conversation"


class NewChatResponse(BaseModel):
    chat_id: int
    title:   str


class MessageOut(BaseModel):
    id:         int
    role:       str
    content:    str
    image_path: Optional[str] = None


class ChatOut(BaseModel):
    id:    int
    title: str


class SaveMessageRequest(BaseModel):
    chat_id:    int
    role:       str
    content:    str
    image_path: Optional[str] = None


class UpdateTitleRequest(BaseModel):
    title: str