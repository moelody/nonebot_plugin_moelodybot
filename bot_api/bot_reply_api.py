
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from nonebot import get_app, get_driver
from nonebot.log import logger

from .bot_reply import refresh_reply_data, get_reply_data, add_reply_data, update_reply_data, delete_reply_data
from .bot_sql import sql_manage
from .bot_auth import get_user_from_token
from .bot_type import Reply

driver = get_driver()


@driver.on_startup
async def init_reply():

    refresh_reply_data()
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

    @app.get("/api/reply/list")
    async def _(token: str):
        userinfo = await get_user_from_token(token)
        if userinfo:
            try:
                with sql_manage.cnxpool.get_connection() as cnx:

                    if userinfo["user_type"] == "admin":
                        sql_response = get_reply_data(
                            cnx=cnx, username=userinfo["username"])
                    else:
                        sql_response = get_reply_data(
                            cnx=cnx, username=userinfo["username"], isAdmin=False)

                    return sql_response
            except Exception as e:
                logger.error(f"{e} 错误行数为:{str(e.__traceback__.tb_lineno)}")
                return {"status_code": 400, "msg": "获取失败"}
                # 不是管理员获取个人数据

    @app.post("/api/reply/update")
    async def add_reply(token: str, username: str, qq_groups: str, reply_id: int = 0, key: str = "", reply: str = ""):

        userinfo = await get_user_from_token(token)
        if userinfo:
            try:
                with sql_manage.cnxpool.get_connection() as cnx:
                    reply_obj = Reply(
                        ID=reply_id,
                        username=username,
                        keyword=key,
                        reply=reply,
                        qq_groups=qq_groups
                    )
                    if reply_id == 0:
                        sql_response = add_reply_data(
                            cnx, reply_obj)
                    else:
                        sql_response = update_reply_data(cnx, reply_obj)
                    return sql_response
            except Exception as err:
                logger.info(err)
                return {"status_code": 400, "msg": "数据库添加失败"}
        else:
            return {"status_code": 400, "msg": "用户验证添加失败"}

    @app.delete("/api/reply/delete")
    async def _(token: str, reply_id: str):
        userinfo = await get_user_from_token(token)
        if userinfo:
            try:
                with sql_manage.cnxpool.get_connection() as cnx:
                    sql_response = delete_reply_data(cnx, reply_id)
                    return sql_response
            except Exception:
                logger.info(Exception)
                return {"status_code": 400, "msg": "删除失败"}


if __name__ == '__main__':
    ...
