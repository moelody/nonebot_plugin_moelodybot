import re

from nonebot import on_command, get_driver
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, GROUP_ADMIN, GROUP_OWNER
from nonebot.params import CommandArg


from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="不活跃群员管理",
    description="",
    usage='''杀群友''',
    extra={
        "version": __version__,
        "license": "MIT",
        "author": "yueli",
        "command": ["杀群友"],
        "type": 1,
        "group": "群管理"
    },
)


kill_member = on_command("杀群友", priority=10, block=True)


config = get_driver().config


ban = on_command("禁言", permission=SUPERUSER | GROUP_ADMIN |
                 GROUP_OWNER, priority=10, block=True)


@ban.handle()
async def _(bot: Bot, event: GroupMessageEvent, args=CommandArg()):

    if not await GROUP_ADMIN(bot, event) and not await GROUP_OWNER(bot, event):
        await ban.finish("小小群员 岂容你放肆!")

    if (at := args["at"]) and (msg_match := re.search(r'\[CQ:at,qq=\d+\]\s*(.*)', str(args))):
        qq_num = at[0].data["qq"]
        ban_num = msg_match[1]
        await bot.set_group_ban(group_id=event.group_id, user_id=int(qq_num), duration=int(ban_num) * 60)
