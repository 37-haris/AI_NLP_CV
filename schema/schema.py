from pydantic import BaseModel, Field
from datetime import datetime


# ── Requests ──────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username:  str = Field(..., min_length=3,  max_length=50)
    firstname: str = Field(..., min_length=1,  max_length=50)
    lastname:  str = Field(..., min_length=1,  max_length=50)
    password:  str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


# ── Responses ─────────────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    id:        int
    username:  str
    firstname: str
    lastname:  str
    created_at: str


class RegisterResponse(BaseModel):
    message: str


class LoginResponse(BaseModel):
    message: str
    user:    UserResponse