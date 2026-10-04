from typing import Optional
from pydantic import BaseModel


class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    role: str = "SOC_ANALYST"


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str
    expires_in_minutes: int


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool
