
from nonebot import get_driver, on_command, on_message
from nonebot.adapters.onebot.v11 import (GROUP_ADMIN, GROUP_OWNER, Bot,
                                         GroupMessageEvent)
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from nonebot.adapters.onebot.v11.message import Message
from nonebot.params import EventPlainText

from .bot_sql import BotSql

driver = get_driver()
plan_data = {}
refresh_plan = on_command("更新任务", priority=10, block=True)

plan = on_message(priority=9, block=False)

sql_manage = BotSql()


@refresh_plan.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if await GROUP_ADMIN(bot, event) or await GROUP_OWNER(bot, event):
        refresh_plan_data()
        await refresh_plan.send("更新任务成功")


@plan.handle()
async def handle_plan(bot: Bot, event: GroupMessageEvent, msg: Message = EventPlainText()):
    msg = msg.strip().lower()

    if res := plan_data.get(f"{msg}|{str(event.group_id)}") or plan_data.get(
        msg
    ):

        await plan.finish(MS.text(res))


def refresh_plan_data():
    global plan_data
    plan_data.clear()
    status, sqldata = sql_manage.get_data("SELECT * FROM `plandata`")
    print(sqldata)
    for data in sqldata:
        ...

    return status, sqldata


@driver.on_shutdown
async def close_db():
    sql_manage.close()


if __name__ == '__main__':
    ...
