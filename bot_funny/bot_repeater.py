import re

from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent

from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="复读",
    description="复读群友消息",
    usage='''被动技能''',
    extra={
        "version": __version__,
        "license": "MIT",
        "author": "yueli",
        "command": [],
        "type": 0,
        "group": "娱乐功能"
    },
)
from ..config import commands

repeater_group = ["all"]
shortest = 2
shortest_times = 2
blacklist = []

m = on_message(priority=10, block=False)

last_message = {}
message_times = {}


# 消息预处理
def message_preprocess(message: str):
    raw_message = message
    images = re.findall(r'\[CQ:image.*?]', message)
    contained_images = {
        i: [
            re.findall(r'url=(.*?)[,\]]', i)[0][0],
            re.findall(r'file=(.*?)[,\]]', i)[0][0],
        ]
        for i in images
    }
    for i in contained_images:
        message = message.replace(i, f'[{contained_images[i][1]}]')
    return message, raw_message


@m.handle()
async def repeater(bot: Bot, event: GroupMessageEvent):
    # 检查是否在黑名单中
    if event.raw_message in blacklist or event.raw_message in commands:
        return

    gid = str(event.group_id)
    if gid in repeater_group or "all" in repeater_group:
        global last_message, message_times
        message, raw_message = message_preprocess(str(event.message))

        if last_message.get(gid) != message:
            message_times[gid] = 1
        else:
            message_times[gid] += 1
        if message_times.get(gid) == shortest_times:
            await bot.send_group_msg(group_id=event.group_id, message=raw_message, auto_escape=False)
        last_message[gid] = message
