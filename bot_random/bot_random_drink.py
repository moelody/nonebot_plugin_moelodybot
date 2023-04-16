
import random
import os

from nonebot import on_fullmatch
from nonebot.adapters.onebot.v11 import MessageSegment as MS

from ..bot_utils.util import get_root_path
from pathlib import Path


from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="随机饮品",
    description="随机抽饮品",
    usage='''喝什么/喝啥/换一个喝''',
    extra={
        "version": __version__,
        "license": "MIT",
        "author": "yueli",
        "command": ["喝什么", "喝啥", "换一个喝"],
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


random_drink = on_fullmatch(
    msg=("喝什么", "喝啥", "换一个喝"),
    priority=10, block=True
)


@random_drink.handle()
async def _():
    random_folder = f"{get_root_path()}/data/images/drink_pic"
    filename = random.choice(
        os.listdir(random_folder))
    random_file = f"{random_folder}/{filename}"

    text = random.choice(random_reply_list).format(filename.split(".")[0])
    await random_drink.finish(MS.text(text) + MS.image(Path(random_file)))
