
import random
import os

from nonebot import on_regex, on_keyword
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from nonebot.params import RegexStr

from ..bot_utils import get_root_path

from pathlib import Path

# 菜单来源: https://github.com/Cvandia/nonebot-plugin-whateat-pic


from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="随机插件",
    description="",
    usage='''抽群友关键词 抽群友/抽..女群友/抽..男群友/抽老婆/抽老公
\t\t抽菜单关键词 吃什么, 吃啥, 饿饿, 换一个吃, 想吃''',
    extra={
        "version": __version__,
        "license": "MIT",
        "author": "yueli",
        "command": ["群友", "吃什么", "吃啥", "饿饿", "换一个吃", "想吃"],
        "group": "娱乐功能"
    },
)

random_reply_list = [
    "emmm,要不试试「{}」",
    "来点「{}」!",
    "来尝尝「{}」吧",
    "月灵觉得「{}」不错哟~",
    "就决定是你了!「{}」!",
    "月灵想吃「{}」!",
]

random_sel_member = on_regex(
    pattern="(抽.*群友)|(抽然然)|(抽老婆)|(抽老公)",
    priority=9, block=True)

random_eat = on_keyword(
    keywords={"吃什么", "吃啥", "饿饿", "换一个吃", "想吃"},
    priority=5, block=True
)

random_drink = on_regex(
    r"(喝什么)|(喝啥)|(渴)|(换一个喝)",
    priority=10, block=True
)


@random_sel_member.handle()
async def random_mem(bot: Bot, event: GroupMessageEvent, cmd: str = RegexStr()):
    if "抽" not in cmd:
        return
    # if cmd == "抽然然":
    #     msg = MS.text("你抽到的群友是:傻然\n")
    #     msg += MS.image(
    #         "https://q.qlogo.cn/headimg_dl?dst_uin=21615991&spec=640")
    #     await random_sel_member.finish(message=msg, at_sender=True)

    group_info = await bot.get_group_member_list(group_id=event.group_id, no_cache=True)

    if "杀群友" in cmd:
        return

    elif any(keys in cmd for keys in ["女群友", "老婆"]):
        group_info = [mem for mem in group_info if mem.get('sex') == 'female']
    elif any(keys in cmd for keys in ["男群友", "老公"]):
        group_info = [mem for mem in group_info if mem.get('sex') == 'male']

    group_info = sorted(
        group_info, key=lambda x: x["last_sent_time"])[-50:]

    member_info = random.choice(group_info)
    user_id = member_info.get("user_id")
    nickname = member_info.get("nickname")

    msg = MS.text(f"你抽到的群友是:{nickname}\n")
    msg += MS.image(
        f"https://q.qlogo.cn/headimg_dl?dst_uin={user_id}&spec=640")

    await random_sel_member.finish(message=msg, at_sender=True)


@random_eat.handle()
async def _():
    random_folder = f"{get_root_path()}/data/images/eat_pic"
    filename = random.choice(
        os.listdir(random_folder))
    random_file = f"{random_folder}/{filename}"

    text = random.choice(random_reply_list).format(filename.split(".")[0])
    await random_eat.finish(MS.text(text) + MS.image(Path(random_file)))


@random_drink.handle()
async def _():
    random_folder = f"{get_root_path()}/data/images/drink_pic"
    filename = random.choice(
        os.listdir(random_folder))
    random_file = f"{random_folder}/{filename}"

    text = random.choice(random_reply_list).format(filename.split(".")[0])
    await random_drink.finish(MS.text(text) + MS.image(Path(random_file)))
