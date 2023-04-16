import time

from nonebot import on_command, get_driver
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from nonebot.params import CommandArg


from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="全服公告",
    description="",
    usage='''通知 + 内容''',
    extra={
        "version": __version__,
        "license": "MIT",
        "author": "yueli",
        "command": ["通知"],
        "type": 1,
        "group": "群管理"
    },
)

bot_notice = on_command("通知", priority=10, block=True)
config = get_driver().config


@bot_notice.handle()
async def _(bot: Bot, event: GroupMessageEvent, args=CommandArg()):
    if str(event.user_id) in config.superusers:
        args = args.extract_plain_text()
        groups = await bot.get_group_list()
        msg = MS.text(f"通知: {args}")

        for group in groups:
            if group != str(event.group_id):
                await bot_notice.send(message=msg)
                time.sleep(0.75)
