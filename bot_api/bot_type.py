from pydantic import BaseModel
from typing import Optional, Union


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
    qq_groups: Union[str, None] = None


class Reply(BaseModel):
    ID: Union[int, None] = None
    username: Union[str, None] = None
    keyword: str = ""
    reply: str = ""
    qq_groups: Union[list[str], str, None] = None


rep = Reply()

