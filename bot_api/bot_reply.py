
from nonebot import get_driver, on_command, on_message
from nonebot.adapters.onebot.v11 import (GROUP_ADMIN, GROUP_OWNER, Bot,
                                         GroupMessageEvent)
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from nonebot.adapters.onebot.v11.message import Message
from nonebot.params import EventPlainText

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
    status, sqldata = sql_manage.get_data("SELECT * FROM `replydata`")
    print(sqldata)
    for data in sqldata:
        keys = data[2].split(",")
        suffix = f"|{data[4]}" if data[4] else ""
        for key in keys:
            reply = data[3].replace("{}", key) if '{}' in data[3] else data[3]
            reply_data[(key + suffix).lower()] = reply

    return status, sqldata


@driver.on_shutdown
async def close_db():
    sql_manage.close()


if __name__ == '__main__':
    ...
