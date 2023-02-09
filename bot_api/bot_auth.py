# pip install pyjwt
from datetime import datetime, timedelta

import jwt

from .bot_sql import BotSql

sql_manage = BotSql()


class AuthHandler():
    _salt = "@^4_00wedv**pi)+(!w1rwi=d3q4l=ie=g-u$s8jevmj*zgg2"
    _expire_message = dict(code=401, msg="token 已经失效")
    _unknown_error_message = dict(code=401, msg="token 解析失败")

    @classmethod
    def verify_password(cls, username: str, password: str):

        sql = """SELECT * FROM `userdata` WHERE `username` =%s"""
        status, user_info = sql_manage.get_data(sql, username)

        # 密码是3号位 如果修改数据库类型 请更改
        # 返回usertype 和 groups
        if status and user_info[0][2] == password:
            return True, user_info[0][3], user_info[0][4]
        else:
            return False, 0, 0

    # 生成token
    @classmethod
    def generate_token(cls, data: dict) -> str:
        headers = dict(typ="jwt", alg="HS256")
        result = jwt.encode(payload=data, key=cls._salt, algorithm="HS256",
                            headers=headers)
        return result

    # 解析token
    @classmethod
    def parse_token(cls, cache_token: str) -> tuple:
        verify_status = False
        try:
            payload_data = jwt.decode(
                cache_token, cls._salt, algorithms=['HS256'])
            verify_status = True
        except jwt.ExpiredSignatureError:
            payload_data = cls._expire_message
        except Exception as _err:
            print(_err)
            payload_data = cls._unknown_error_message
        return verify_status, payload_data


if __name__ == '__main__':

    expire_seconds = 3600
