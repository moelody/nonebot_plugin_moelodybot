from datetime import datetime, timedelta, timezone
from typing import Union
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from nonebot.log import logger

from .bot_sql import sql_manage
import jwt

from nonebot import get_app, get_driver
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from .bot_type import UserCreate, UserLogin
from .bot_auth import AuthHandler
from ..config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

driver = get_driver()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


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

    @app.get("/api/parse_token")
    async def _(token: str):
        status, data = AuthHandler.parse_token(token)

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
    @app.post("/api/register")
    async def register(user: UserCreate = Body(...)):
        try:
            # 如果用户名或密码为空，返回错误
            if not user.username or not user.password:
                return {"status_code": 400, "message": "Username and password cannot be empty"}

            # 查询用户是否已经存在

            if sql_manage.get_user(user.username):
                return {"status_code": 400, "message": "Username already exists"}
            # 创建用户
            sql_manage.create_user(user)

            # 返回创建成功信息
            return {"status_code": 200, "message": "User created successfully"}

        except Exception:
            return {"status_code": 400, "message": "Failed to create user"}

    # 登录接口
    @app.post("/api/login")
    async def login(user: UserLogin = Body(...)):
        try:
            # 如果前端传递了 token，那么直接解析 token 并判断是否有效
            if user.token:

                token_data = jwt.decode(
                    user.token, SECRET_KEY, algorithms=[ALGORITHM])
                username = token_data.get("sub")
                userinfo = sql_manage.get_user(username)

                return (
                    {
                        "status_code": 200,
                        "message": "Token login successful",
                        "data": {
                            "username": userinfo["username"],
                            "groups": userinfo["groups"],
                        },
                    }
                    if userinfo
                    else {"status_code": 400, "message": "Invalid token"}
                )
            # 如果前端没有传递 token，则使用用户名密码进行登录
            userinfo = sql_manage.get_user(user.username)

            if not userinfo:
                return {"status_code": 400, "message": "Invalid username or password"}

            # 校验密码是否正确 数据库里的是hashed_password
            if not pwd_context.verify(user.password, userinfo["password"]):
                return {"status_code": 400, "message": "Invalid username or password"}

            # 生成JWT
            access_token_expires = timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token_data = {
                "sub": user.username,
                "exp": datetime.now(timezone.utc) + access_token_expires,
            }

            access_token = jwt.encode(
                access_token_data, SECRET_KEY, algorithm=ALGORITHM)
            # 返回token
            return {"status_code": 200, "message": "登录成功", "token": access_token, "data": {"username": userinfo["username"], "groups": userinfo["groups"]}}

        except ExpiredSignatureError:
            return {"status_code": 400, "message": "Token expired"}
        except InvalidTokenError:
            return {"status_code": 400, "message": "Invalid or expired token"}
        except Exception as e:
            logger.error(e)
            return {"status_code": 400, "message": "Failed to login"}

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
