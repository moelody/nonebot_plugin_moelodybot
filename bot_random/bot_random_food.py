
import random
import os

from nonebot import on_fullmatch
from nonebot.adapters.onebot.v11 import MessageSegment as MS

from ..bot_utils.util import get_root_path
from pathlib import Path


from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="随机菜单",
    description="随机抽吃的",
    usage='''吃什么/吃啥/饿饿/换一个吃''',
    extra={
        "version": __version__,
        "license": "MIT",
        "author": "yueli",
        "command": ["吃什么", "吃啥", "饿饿", "换一个吃", "想吃"],
        "group": "随机功能"
    },
)

random_reply_list = [
    "emmm,要不试试「{}」",
    "来试试「{}」吧",
    "月灵觉得「{}」不错哟~",
    "就决定是你了!「{}」!",
    "月灵想要「{}」!",
]


random_food = on_fullmatch(
    msg=("吃什么", "吃啥", "饿饿", "换一个吃"),
    priority=5, block=True
)


@random_food.handle()
async def _():
    random_folder = f"{get_root_path()}/data/images/eat_pic"
    filename = random.choice(
        os.listdir(random_folder))
    random_file = f"{random_folder}/{filename}"

    text = random.choice(random_reply_list).format(filename.split(".")[0])
    await random_food.finish(MS.text(text) + MS.image(Path(random_file)))
