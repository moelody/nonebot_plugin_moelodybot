from datetime import datetime, timedelta
from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from nonebot import get_app, get_bot, get_driver, on_command, on_message
from nonebot.adapters.onebot.v11 import (GROUP_ADMIN, GROUP_OWNER, Bot,
                                         GroupMessageEvent)
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from nonebot.adapters.onebot.v11.message import Message
from nonebot.params import EventPlainText

from .bot_auth import AuthHandler
from .bot_sql import BotSql

driver = get_driver()
reply_data = {}
refresh_reply = on_command("更新回复", priority=10, block=True)
add_user = on_command("添加用户", priority=10, block=True)
reply = on_message(priority=9, block=False)

sql_manage = BotSql()


@add_user.handle()
async def _(bot: Bot, event: GroupMessageEvent, msg: Message = EventPlainText()):
    if await GROUP_OWNER(bot, event):
        try:
            command, username, groups = msg.strip().split(" ")
            sql = """INSERT INTO `userdata` ( `username`, `groups`) VALUES ( %s, %s)"""

            res, data = sql_manage.add_data(sql, username, groups)
            if res:
                await refresh_reply.send("添加成功")

            else:
                await refresh_reply.send("添加失败")
        except Exception as e:
            print(e)
            await refresh_reply.send("添加失败")


@refresh_reply.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if await GROUP_ADMIN(bot, event) or await GROUP_OWNER(bot, event):
        refresh_reply_data()

        await refresh_reply.send("更新字典成功")


@reply.handle()
async def handle_reply(bot: Bot, event: GroupMessageEvent, msg: Message = EventPlainText()):
    msg = msg.strip().lower()

    if res := reply_data.get(f"{msg}|{str(event.group_id)}") or reply_data.get(
        msg
    ):

        await reply.finish(MS.text(res))


def refresh_reply_data():
    global reply_data
    reply_data.clear()
    status, sqldata = sql_manage.get_data("SELECT * FROM `msgdata`")
    print(sqldata)
    for data in sqldata:
        keys = data[2].split(",")
        suffix = f"|{data[4]}" if data[4] else ""
        for key in keys:
            reply = data[3].replace("{}", key) if '{}' in data[3] else data[3]
            reply_data[(key + suffix).lower()] = reply

    return status, sqldata


@driver.on_startup
async def init_web():

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

    # 验证-------------------------------------------------------------
    @app.get("/api/auth")
    async def _(username: str, password: str):
        status, usertype, user_groups = AuthHandler.verify_password(
            username, password)
        if status:
            expire_seconds = 3600 * 24 * 7
            data = dict(username=username,
                        exp=datetime.utcnow() + timedelta(seconds=expire_seconds),
                        usertype=usertype,
                        groups=user_groups
                        )
            token = AuthHandler.generate_token(data)
            return {"status": 200, "username": username, "token": token}
        else:
            return {"status": 401, "username": username}

    @app.get("/api/parse_token")
    async def _(token: str):
        res, data = AuthHandler.parse_token(token)
        if res:
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
            res, data = AuthHandler.parse_token(token)
            username = data.get('username')
        elif username and password:
            status, usertype, user_groups = AuthHandler.verify_password(
                username, password)
        else:
            return {"status": 401, "msg": "更改失败,缺少token或者username与password"}

        if res:
            sql = "UPDATE `userdata` SET `password`='%s' WHERE `username` = '%s'"

            sql_manage.add_data(sql, new_password, username)
            return {"status": 200, "msg": "更改成功", "token": token}
        else:
            return {"status": 401, "msg": "更改失败"}

    @app.get("/api/add_user")
    async def _(username: str, groups: str):
        sql = """INSERT INTO `userdata` ( `username`, `groups`) VALUES ( %s, %s)"""
        print(sql, username, groups)
        res, data = sql_manage.add_data(sql, username, groups)
        return {"status": 200, "msg": data} if res else {"status": 401, "msg": data}

    @app.get("/api/reply/all_reply_list")
    async def _():
        status, sqldata = refresh_reply_data()
        return {"status": 200, "msg": "获取成功", "sqldata": sqldata}

    @app.get("/api/reply/list")
    async def _(token: str):

        res, data = AuthHandler.parse_token(token)

        if res:
            if (data.get("usertype") == "admin"):
                status, sqldata = refresh_reply_data()
                return {"status": 200, "msg": "获取成功", "token": token, "sqldata": sqldata}

            sql = """SELECT * FROM `msgdata` WHERE `username` = %s"""
            status, sqldata = sql_manage.get_data(sql, data.get('username'))
            if sqldata == []:

                sql2 = """SELECT * FROM `userdata` WHERE `username` = %s"""
                status2, sqldata2 = sql_manage.get_data(
                    sql2, data.get('username'))

                sqldata = [
                    [0, data.get('username'), "", "", sqldata2[0][4], ""]]
            return {"status": 200, "msg": "获取成功", "token": token, "sqldata": sqldata}
        else:
            return {"status": 401, "msg": "获取失败"}

    @app.get("/api/reply/add")
    async def _(token: str, key: str, reply: str, groups: str):

        res, data = AuthHandler.parse_token(token)

        if not groups:
            groups = data.get("groups")

        if not key or not reply:
            return {"status": 401, "msg": "key 与 reply 不可以为空"}
        if res:
            sql = """INSERT INTO `msgdata` (`ID`, `username`, `keyword`, `reply`, `groups`) VALUES (NULL, %s, %s, %s,%s);""".replace(
                "'None',", "null,").replace("None,", "null,")
            status, msg = sql_manage.add_data(
                sql, data.get('username'), key, reply, groups)
            if status:
                return {"status": 200, "msg": "添加成功"}
            else:
                return {"status": 401, "msg": msg}
        else:
            return {"status": 401, "msg": "添加失败"}

    @app.get("/api/reply/update")
    async def _(token: str, key: str, reply: str, groups: str, reply_id: str):

        res, data = AuthHandler.parse_token(token)

        if not groups:
            groups = data.get("groups")

        if not key or not reply:
            return {"status": 401, "msg": "key 与 reply 不可以为空"}
        if res:
            sql = "UPDATE `msgdata` SET `keyword` = %s, `reply` = %s, `groups` = %s WHERE `msgdata`.`ID` = %s;".replace(
                "'None',", "null,").replace("None,", "null,")
            status, msg = sql_manage.add_data(
                sql, key, reply, groups, reply_id)
            if status:
                return {"status": 200, "msg": "添加成功"}
            else:
                return {"status": 401, "msg": msg}
        else:
            return {"status": 401, "msg": "添加失败"}

    @app.get("/api/reply/delete")
    async def _(token: str, reply_id: str):

        res, data = AuthHandler.parse_token(token)
        # 没有判断用户, 可以加个是管理员 可以无视用户
        if res:
            sql = "DELETE FROM `msgdata` WHERE `id` = %s;"
            status, msg = sql_manage.delete_data(
                sql, reply_id)
            if status:
                return {"status": 200, "msg": "删除成功"}
            else:
                return {"status": 401, "msg": msg}
        else:
            return {"status": 401, "msg": "删除失败"}


@driver.on_shutdown
async def close_db():
    sql_manage.close()


if __name__ == '__main__':
    ...
