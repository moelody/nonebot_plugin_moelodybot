from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None
    hashed_password: str


class UserLogin(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    password: str
    nickname: Optional[str] = None
