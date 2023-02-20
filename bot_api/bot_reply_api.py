
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from nonebot import get_app, get_driver
from nonebot.log import logger

from .bot_reply import refresh_reply_data, get_reply_data
from .bot_sql import sql_manage
from .bot_auth import get_user_from_token

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

    @app.get("/api/reply/add")
    async def _(token: str, key: str, reply: str, groups: str):

        ...
        # sql = """INSERT INTO `replydata` (`ID`, `username`, `keyword`, `reply`, `groups`) VALUES (NULL, %s, %s, %s,%s);""".replace(
        #     "'None',", "null,").replace("None,", "null,")
        # status, msg = sql_manage.get_data(
        #     sql, data.get('username'), key, reply, groups)

    @app.get("/api/reply/update")
    async def _(token: str, key: str, reply: str, groups: str, reply_id: str):

        ...
        # sql = "UPDATE `replydata` SET `keyword` = %s, `reply` = %s, `groups` = %s WHERE `replydata`.`ID` = %s;".replace(
        #     "'None',", "null,").replace("None,", "null,")
        # status, msg = sql_manage.get_data(
        #     sql, key, reply, groups, reply_id)

    @app.get("/api/reply/delete")
    async def _(token: str, reply_id: str):

        ...
        # sql = "DELETE FROM `replydata` WHERE `id` = %s;"
        # status, msg = sql_manage.get_data(
        #     sql, reply_id)


if __name__ == '__main__':
    ...
