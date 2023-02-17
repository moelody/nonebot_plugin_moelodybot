# pip install pyjwt
import jwt
# import bcrypt

from .bot_sql import BotSql
from ..config import JWT_SECRET_KEY, JWT_ALGORITHM
from nonebot.log import logger

sql_manage = BotSql()


class AuthHandler():
    _expire_message = dict(code=401, msg="token 已经失效")
    _unknown_error_message = dict(code=401, msg="token 解析失败")

    @classmethod
    def verify_password(cls, username: str, password: str):

        sql = """SELECT * FROM `userdata` WHERE `username` =%s"""
        status, user_info = sql_manage.get_data(sql, username)

        # 返回usertype 和 groups
        if status and user_info[0]["password"] == password:
            return True, user_info[0]["user_type"], user_info[0]["groups"]
        else:
            return False, 0, 0

    # 生成token
    @classmethod
    def generate_token(cls, data: dict) -> str:
        headers = dict(typ="jwt", alg=JWT_ALGORITHM)
        return jwt.encode(
            payload=data, key=JWT_SECRET_KEY, algorithm=JWT_ALGORITHM, headers=headers
        )

    # 解析token
    @classmethod
    def parse_token(cls, cache_token: str) -> dict:
        try:
            payload_data = jwt.decode(
                cache_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            status = True
            data = payload_data
        except jwt.ExpiredSignatureError:
            status = False
            data = cls._expire_message
        except Exception:
            logger.error(cls._unknown_error_message)
            status = False
            data = cls._unknown_error_message

        return status, data


if __name__ == '__main__':

    expire_seconds = 3600
