from datetime import datetime, timedelta, timezone
from typing import Union
import bcrypt
from fastapi import FastAPI, request
from fastapi.middleware.cors import CORSMiddleware
from nonebot import get_app, get_driver

from .bot_auth import AuthHandler
from .bot_sql import BotSql

driver = get_driver()
sql_manage = BotSql()


users_db = {
    "Alice": {
        "password": bcrypt.hashpw("password123".encode(), bcrypt.gensalt()),
        "id": 1
    },
    "Bob": {
        "password": bcrypt.hashpw("password456".encode(), bcrypt.gensalt()),
        "id": 2
    }
}


@driver.on_startup
async def _():

    app: FastAPI = get_app()

    # 2、声明一个 源 列表；重点：要包含跨域的客户端 源
    origins = ["*"]

    # 3、配置 CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # 允许访问的源
        allow_credentials=True,  # 支持 cookie
        allow_methods=["*"],  # 允许使用的请求方法
        allow_headers=["*"]  # 允许携带的 Headers
    )

    # 验证-------------------------------------------------------------
    @app.get("/api/auth")
    async def _(username: str, password: str):
        status, usertype, user_groups = AuthHandler.verify_password(
            username, password)
        if status:
            expire_seconds = 3600 * 24 * 7
            data = dict(
                username=username,
                exp=datetime.now(timezone.utc)
                + timedelta(seconds=expire_seconds),
                usertype=usertype,
                groups=user_groups,
            )
            token = AuthHandler.generate_token(data)
            return {"status": 200, "username": username, "token": token}
        else:
            return {"status": 401, "username": username}

    @app.get("/api/parse_token")
    async def _(token: str):
        status, data = AuthHandler.parse_token(token)
        print(data)
        if status:
            return {"status": 200, "username": data.get("username"), "usertype": data.get("usertype")}
        else:
            return {"status": 401, }

    @app.get("/api/change_password")
    async def _(new_password, token: Union[str, None] = None, username: Union[str, None] = None, password: Union[str, None] = None):
        """
        new_password:
        token / username+password
        """
        if token:
            status, data = AuthHandler.parse_token(token)
            username = data.get('username')
        elif username and password:
            status, usertype, user_groups = AuthHandler.verify_password(
                username, password)
        else:
            return {"status": 401, "msg": "更改失败,缺少token或者username与password"}

        if status:
            sql = "UPDATE `userdata` SET `password`='%s' WHERE `username` = '%s'"

            sql_manage.add_data(sql, new_password, username)
            return {"status": 200, "msg": "更改成功", "token": token}
        else:
            return {"status": 401, "msg": "更改失败"}

    # 1. 用户注册
    @app.route('/api/register', methods=['POST'])
    def register():
        username = request.json['username']
        password = request.json['password']

        # 对密码进行哈希处理
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        # 将用户名和哈希密码保存到数据库中
        users_db[username] = {
            "password": hashed_password,
            "id": len(users_db) + 1
        }

        return 'User registered successfully'

    @app.get("/api/add_user")
    async def _(username: str, groups: str):
        sql = """INSERT INTO `userdata` ( `username`, `groups`) VALUES ( %s, %s)"""
        status, data = sql_manage.add_data(sql, username, groups)
        return {"status": 200, "msg": data} if status else {"status": 401, "msg": data}


@driver.on_shutdown
async def close_db():
    sql_manage.close()


if __name__ == '__main__':
    ...
