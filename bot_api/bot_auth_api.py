
from typing import Union
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from nonebot.log import logger

from .bot_sql import sql_manage


from nonebot import get_app, get_driver
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from .bot_type import UserCreate, UserLogin
from .bot_auth import get_user_from_token, create_access_token


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

    @app.get("/api/change_password")
    async def _(new_password, token: Union[str, None] = None, username: Union[str, None] = None, password: Union[str, None] = None):
        """
        new_password:
        token / username+password
        """
        if token:
            ...

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
                userinfo = await get_user_from_token(user.token)
            else:
                # 如果没有token 而且没有用户名和密码 直接返回
                if not user.username or not user.password:
                    return {"status_code": 400, "message": "Invalid username or password"}

                # 如果前端没有传递 token，则使用用户名密码进行登录
                userinfo = sql_manage.get_user(user.username)

                # 校验密码是否正确 数据库<userinfo>里的是hashed_password
                if not userinfo or not pwd_context.verify(user.password, userinfo["password"]):
                    return {"status_code": 400, "message": "Invalid username or password"}

            # 返回结果
            if userinfo:
                access_token = create_access_token(
                    username=userinfo["username"])
                return {
                    "status_code": 200,
                    "message": "Token login successful"
                    if user.token
                    else "登录成功",
                    "data": {
                        "username": userinfo["username"],
                        "groups": userinfo["qq_groups"],
                    },
                    "token": None if user.token else access_token,
                }
            else:
                return {"status_code": 400, "message": "Invalid or expired token" if user.token else "Invalid username or password"}

        except ExpiredSignatureError:
            return {"status_code": 400, "message": "Token expired"}
        except InvalidTokenError:
            return {"status_code": 400, "message": "Invalid or expired token"}
        except Exception as e:
            logger.error(e)
            return {"status_code": 400, "message": "Failed to login"}

    # 创建用户接口
    @app.get("/api/add_user")
    async def _(username: str, groups: str):
        try:
            sql_manage.create_user(
                UserCreate(username=username, password="admin", groups=groups))
            return {"status_code": 200, "message": "创建成功"}
        except Exception as e:
            logger.error(e)
            return {"status_code": 400, "message": f"创建失败{e}"}


if __name__ == '__main__':
    ...
