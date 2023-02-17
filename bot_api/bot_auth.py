# pip install pyjwt
import jwt
import bcrypt

from .bot_sql import BotSql
from ..config import JWT_SECRET_KEY, JWT_ALGORITHM
from nonebot.log import logger

sql_manage = BotSql()


class AuthHandler():
    _expire_message = dict(code=401, msg="token 已经失效")
    _unknown_error_message = dict(code=401, msg="token 解析失败")

    @classmethod
    def verify_password(cls, username: str, password: str):
        # 从数据库中查询指定用户名的哈希密码
        hashed_password = sql_manage.get_password_hash(username)
        # 验证密码
        if hashed_password and bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            # 返回usertype 和 groups
            user_info = sql_manage.get_user_info(username)
            return True, user_info[0], user_info[1]
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
                cache_token, cls._salt, algorithms=['HS256'])
            status = True
            data = payload_data
        except jwt.ExpiredSignatureError:
            status = False
            data = cls._expire_message
        except Exception:
            logger.error("Token 解析失败")
            status = False
            data = cls._unknown_error_message

        return dict(status=status, data=data)


if __name__ == '__main__':

    expire_seconds = 3600
