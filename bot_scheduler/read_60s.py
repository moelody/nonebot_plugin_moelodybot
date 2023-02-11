import json

import aiohttp
import nonebot
from nonebot import require
from nonebot.adapters.onebot.v11 import Message
from pydantic import BaseSettings, Field

global_config = nonebot.get_driver().config


class Time(BaseSettings):
    hour: int = Field(0, alias="HOUR")
    minute: int = Field(0, alias="MINUTE")

    class Config:
        extra = "allow"
        case_sensitive = False
        anystr_lower = True


plugin_config = {
    "read_qq_friends": [],
    "read_qq_groups": [680653092, 151998078],
    "read_inform_time": {"HOUR": 8, "MINUTE": 0}
}


scheduler = require("nonebot_plugin_apscheduler").scheduler


def remove_upprintable_chars(s):
    return ''.join(x for x in s if x.isprintable())  # 去除imageUrl可能存在的不可见字符


async def read60s():
    msg = await suijitu()
    for qq in plugin_config.get("read_qq_friends"):
        await nonebot.get_bot().send_private_msg(user_id=qq, message=Message(msg))

    for qq_group in plugin_config.get("read_qq_groups"):
        # MessageEvent可以使用CQ发图片
        await nonebot.get_bot().send_group_msg(group_id=qq_group, message=Message(msg))


async def suijitu():
    try:
        url = "https://api.2xb.cn/zaob"  # 备用网址
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                resp = await response.text()
                resp = remove_upprintable_chars(resp)
                retdata = json.loads(resp)
                lst = retdata['imageUrl']
                return f"今日60S读世界已送达\n[CQ:image,file={lst}]"
    except:
        url = "https://api.iyk0.com/60s"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                resp = await response.text()
                resp = remove_upprintable_chars(resp)
                retdata = json.loads(resp)
                lst = retdata['imageUrl']
                return f"今日60S读世界已送达\n[CQ:image,file={lst}]"

scheduler.add_job(read60s, "cron",
                  hour=plugin_config["read_inform_time"]["HOUR"],
                  minute=plugin_config["read_inform_time"]["MINUTE"],
                  id="yuelibo_read_60s")
