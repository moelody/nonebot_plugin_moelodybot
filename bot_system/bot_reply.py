
from nonebot import get_driver, on_command, on_message
from nonebot.adapters.onebot.v11 import (GROUP_ADMIN, GROUP_OWNER, Bot,
                                         GroupMessageEvent)
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from nonebot.params import EventPlainText
from nonebot.log import logger

from ..bot_api.bot_sql import sql_manage
from ..bot_api.bot_type import UserCreate, Reply


from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="自动问答",
    description="管理bot自动问答",
    usage="""请在网页端管理 bot.yuelili.com""",
    extra={
        "version": __version__,
        "license": "MIT",
        "author": "yueli",
        "command": ["更新回复", "添加用户"],
        "group": "群管理"
    },
)

driver = get_driver()
reply_data = {}
refresh_reply = on_command("更新回复", priority=10, block=True)
add_user = on_command("添加用户", priority=10, block=True)
reply = on_message(priority=9, block=False)


# 在qq群添加用户
@add_user.handle()
async def _(bot: Bot, event: GroupMessageEvent, msg=EventPlainText()):
    if await GROUP_OWNER(bot, event):
        try:
            command, username, qq_groups = msg.strip().split(" ")
            sql_manage.create_user(
                UserCreate(username=username, password="admin", qq_groups=qq_groups))
            await refresh_reply.send("添加成功")

        except Exception as e:
            print(e)
            await refresh_reply.send("添加失败")


@refresh_reply.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if await GROUP_ADMIN(bot, event) or await GROUP_OWNER(bot, event):
        refresh_reply_data()

        await refresh_reply.send("更新字典成功")


@reply.handle()
async def handle_reply(event: GroupMessageEvent, msg=EventPlainText()):
    msg = msg.strip().lower()

    if res := reply_data.get(f"{msg}|{str(event.group_id)}") or reply_data.get(
        msg
    ):
        await reply.finish(MS.text(res))


def refresh_reply_data():
    """更新字典"""
    global reply_data
    reply_data.clear()
    try:
        with sql_manage.cnxpool.get_connection() as cnx:
            return _extracted_from_refresh_reply_data(cnx, reply_data)
    except Exception as e:
        logger.error(e)
        return {"status_code": 200, "msg": "刷新失败"}


def _extracted_from_refresh_reply_data(cnx, reply_data, username="", usertype="admin"):
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM `replydata`")

    if not (result := cursor.fetchall()):
        return {"status_code": 200, "msg": "没有数据"}

    headers = [i[0]
               for i in cursor.description]
    sqldata = [dict(zip(headers, row)) for row in result]

    for data in sqldata:
        keys = data['keyword'].split(",")
        suffix = f"{data['qq_groups']}" if data["qq_groups"] else ""
        for key in keys:
            reply = data['reply'].replace(
                "{}", key) if '{}' in data['reply'] else data['reply']
            reply_data[(key + suffix).lower()] = reply
    return {"status_code": 200, "sqldata": sqldata}


def get_reply_data(cnx, username="", isAdmin=True):
    cursor = cnx.cursor()
    if isAdmin:
        cursor.execute("SELECT * FROM `replydata`")
    else:
        cursor.execute(
            f"SELECT * FROM `replydata` WHERE `username`='{username}'")
    if not (result := cursor.fetchall()):
        return {"status_code": 400, "msg": "没有数据"}

    headers = [i[0]
               for i in cursor.description]
    sqldata = [dict(zip(headers, row)) for row in result]

    return {"status_code": 200, "sqldata": sqldata}


def add_reply_data(cnx, reply: Reply):
    cursor = cnx.cursor()
    query = "INSERT INTO `replydata` ( `username`, `keyword`, `reply`, `qq_groups`) VALUES ( %s,%s, %s,%s);"
    cursor.execute(query, (reply.username, reply.keyword, reply.reply,
                   reply.qq_groups,))
    return {"status_code": 200, "msg": "添加成功"}


def update_reply_data(cnx, reply: Reply):
    cursor = cnx.cursor()
    query = "UPDATE `replydata` SET `keyword` = %s, `reply` = %s, `qq_groups` = %s WHERE `replydata`.`ID` = %s;"

    cursor.execute(query, (reply.keyword, reply.reply,
                   reply.qq_groups, reply.ID,))
    return {"status_code": 200, "msg": "更新成功"}


def delete_reply_data(cnx, reply_id: str):
    cursor = cnx.cursor()
    query = "DELETE FROM `replydata` WHERE `id` = %s;"
    cursor.execute(query, (reply_id,))
    relpy_id = cursor.lastrowid
    return {"status_code": 200, "msg": "删除成功", "relpy_id": relpy_id}


if __name__ == '__main__':
    ...
