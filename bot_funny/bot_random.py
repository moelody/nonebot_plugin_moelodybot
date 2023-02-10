
import random
import os
import re

from nonebot import on_command, on_regex
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from nonebot.params import RawCommand

from ..bot_utils import get_root_path, convert_to_uri

# 菜单来源: https://github.com/Cvandia/nonebot-plugin-whateat-pic

random_member = on_command(
    "抽群友", aliases={"抽女群友", "抽男群友"}, priority=10, block=True)

random_eat = on_regex(
    r"(吃什么)|(吃啥)|(饿)",
    flags=re.I
)

random_drink = on_regex(
    r"(喝什么)|(喝啥)",
    flags=re.I
)

random_reply_list = [
    "emmm,要不试试「{}」",
    "来点「{}」!",
    "来尝尝「{}」吧",
    "月灵觉得「{}」不错哟~",
    "就决定是你了!「{}」!",
]


@ random_member.handle()
async def _(bot: Bot, event: GroupMessageEvent, cmd: str = RawCommand()):

    group_info = await bot.get_group_member_list(group_id=event.group_id, no_cache=True)

    if cmd == "抽群友":
        group_info = sorted(
            group_info, key=lambda x: x["last_sent_time"])[-50:]
        member_info = random.choice(group_info)
    elif cmd == "抽女群友":
        group_info = [mem for mem in group_info if mem.get('sex') == 'female']
        member_info = random.choice(group_info)
    elif cmd == "抽男群友":
        group_info = [mem for mem in group_info if mem.get('sex') == 'male']
        member_info = random.choice(group_info)

    user_id = member_info.get("user_id")
    nickname = member_info.get("nickname")
    msg = MS.text(f"你抽到的群友是:{nickname}\n")
    msg += MS.image(
        f"https://q.qlogo.cn/headimg_dl?dst_uin={user_id}&spec=640")

    await random_member.finish(message=msg, at_sender=True)


@ random_eat.handle()
async def _():
    random_folder = f"{get_root_path()}/data/images/eat_pic"
    filename = random.choice(
        os.listdir(random_folder))
    random_file = f"{random_folder}/{filename}"

    text = random.choice(random_reply_list).format(filename.split(".")[0])
    await random_eat.finish(MS.text(text) + MS.image(convert_to_uri(random_file)))


@ random_drink.handle()
async def _():
    random_folder = f"{get_root_path()}/data/images/drink_pic"
    filename = random.choice(
        os.listdir(random_folder))
    random_file = f"{random_folder}/{filename}"

    text = random.choice(random_reply_list).format(filename.split(".")[0])
    await random_drink.finish(MS.text(text) + MS.image(convert_to_uri(random_file)))
