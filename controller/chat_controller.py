from fastapi import APIRouter, Request, HTTPException
from jose import jwt, JWTError
from service.chat_service import chat_service
from service.user_service import SECRET_KEY, ALGORITHM
from schema.chat_schema import (
    NewChatRequest, NewChatResponse,
    SaveMessageRequest, UpdateTitleRequest
)

router = APIRouter(prefix="/chats", tags=["Chats"])


def get_user_id(request: Request) -> int:
    """Extract user_id from JWT cookie."""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload.get("sub"))
    except (JWTError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token.")


@router.get("/")
def get_chats(request: Request):
    """Get all chats for the logged-in user."""
    user_id = get_user_id(request)
    return chat_service.get_user_chats(user_id)


@router.post("/", response_model=NewChatResponse, status_code=201)
def create_chat(request: Request, data: NewChatRequest):
    """Create a new chat."""
    user_id = get_user_id(request)
    return chat_service.create_chat(user_id, data.title)


@router.get("/{chat_id}/messages")
def get_messages(chat_id: int, request: Request):
    """Get all messages for a chat."""
    get_user_id(request)  # ensure authenticated
    return chat_service.get_messages(chat_id)


@router.post("/{chat_id}/messages", status_code=201)
def save_message(chat_id: int, data: SaveMessageRequest, request: Request):
    """Save a message to a chat."""
    get_user_id(request)
    return chat_service.save_message(chat_id, data.role, data.content)


@router.patch("/{chat_id}/title")
def update_title(chat_id: int, data: UpdateTitleRequest, request: Request):
    """Update a chat title."""
    get_user_id(request)
    return chat_service.update_title(chat_id, data.title)


@router.delete("/{chat_id}")
def delete_chat(chat_id: int, request: Request):
    """Delete a chat and all its messages."""
    get_user_id(request)
    return chat_service.delete_chat(chat_id)