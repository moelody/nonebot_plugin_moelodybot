import json
import aiohttp
import contextlib
import nonebot

from nonebot import require
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11 import MessageSegment


from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="每日60s新闻",
    description="",
    usage='''被动技能''',
    extra={
        "version": __version__,
        "license": "MIT",
        "author": "yueli",
        "command": [],
        "type": 0,
        "group": "实用功能"
    },
)


plugin_config = {
    "read_qq_friends": [435826135],
    "read_qq_groups": [680653092, 151998078],
    "read_inform_time": {"HOUR": 8, "MINUTE": 0}
}


scheduler = require("nonebot_plugin_apscheduler").scheduler


def remove_upprintable_chars(s):
    return ''.join(x for x in s if x.isprintable())  # 去除imageUrl可能存在的不可见字符


async def read60s():
    msg = await get_image()
    for qq in plugin_config.get("read_qq_friends", []):
        await nonebot.get_bot().send_private_msg(user_id=qq, message=Message(msg))

    # for qq_group in plugin_config.get("read_qq_groups", []):
    #     # MessageEvent可以使用CQ发图片
    #     await nonebot.get_bot().send_group_msg(group_id=qq_group, message=Message(msg))


async def get_image_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            resp = await response.text()
            resp = remove_upprintable_chars(resp)
            retdata = json.loads(resp)
            return retdata['imageUrl']


async def get_image():
    urls = ["https://api.2xb.cn/zaob", "https://api.iyk0.com/60s"]
    for url in urls:
        with contextlib.suppress(Exception):
            lst = await get_image_url(url)
            return "今日60S读世界已送达\n" + MessageSegment(lst)
    return "无法获取图片"


scheduler.add_job(read60s, "cron",
                  hour=plugin_config["read_inform_time"]["HOUR"],
                  minute=plugin_config["read_inform_time"]["MINUTE"],
                  id="yuelibo_read_60s")
