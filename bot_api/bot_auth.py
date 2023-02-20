from fastapi import HTTPException
import jwt
from ..config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from .bot_sql import sql_manage
from datetime import datetime, timedelta, timezone


async def get_user_from_token(token: str):
    try:
        token_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if username := token_data.get("sub"):
            return sql_manage.get_user(username)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return None


def create_access_token(username: str):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_data = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + access_token_expires,
    }
    return jwt.encode(access_token_data, SECRET_KEY, algorithm=ALGORITHM)
