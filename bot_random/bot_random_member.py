
import random

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from nonebot.params import RegexStr


from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="抽群友",
    description="",
    usage='''抽群友/抽男群友/抽女群友/抽老婆/抽老公''',
    extra={
        "version": __version__,
        "license": "MIT",
        "author": "yueli",
        "command": ["抽群友", "抽男群友", "抽女群友", "抽老婆", "抽老公"],
        "group": "随机功能"
    },
)


random_member = on_regex(
    pattern="(抽.*群友)|(抽老婆)|(抽老公)",
    priority=9, block=True)


@random_member.handle()
async def random_mem(bot: Bot, event: GroupMessageEvent, cmd: str = RegexStr()):
    if "抽" not in cmd:
        return

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

    await random_member.finish(message=msg, at_sender=True)
