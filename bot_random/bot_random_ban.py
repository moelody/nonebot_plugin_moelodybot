
import random

from nonebot import on_fullmatch
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, GROUP_ADMIN, GROUP_OWNER


from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="随机禁言",
    description="抽卡式禁言",
    usage='''抽禁言''',
    extra={
        "version": __version__,
        "license": "MIT",
        "author": "yueli",
        "command": ["抽禁言"],
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


random_ban = on_fullmatch(
    msg="抽禁言",
    priority=10, block=True
)


@random_ban.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    ranges = [(0, 0, 1),
              (1, 1, 4),
              (2, 10, 10),
              (11, 25, 15),
              (26, 75, 50),
              (76, 90, 14),
              (90, 90, 1)]
    award = ["哥就是传说", "玩的就是心跳!", "下次还敢!",
             "在作死的边缘试探", "还敢皮么?", "快来笑TA!", "OHHH MY GOD"]
    level = ["神话级", "传说级", "史诗级", "卓越级", "普通级", "非酋级", "天谴级"]

    random_range = random.choices(
        ranges, weights=[x[2] for x in ranges])[0]

    # 从选择的范围中随机生成一个整数
    random_num = random.randint(random_range[0], random_range[1])
    chosen_range_index = ranges.index(random_range)

    user_info = await bot.get_stranger_info(user_id=event.user_id)
    username = event.user_id
    if user_info:
        username = user_info.get('nickname', 'unknown')

    await random_ban.send(f"{award[chosen_range_index]} 恭喜{username}获得「{level[chosen_range_index]}」禁言卡,将在{random_num}分钟后解禁")

    if not await GROUP_ADMIN(bot, event) and not await GROUP_OWNER(bot, event):
        await bot.set_group_ban(group_id=event.group_id, user_id=event.user_id, duration=random_num * 60)
