from nonebot import on_command
# from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11.message import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="复述",
    description="复述指令",
    usage="""echo + 需要机器人重复的内容""",
    extra={
        "version": __version__,
        "license": "MIT",
        "author": "yueli",
        "command": ["echo"],
        "group": "娱乐功能"
    },
)

bot_echo = on_command("echo", priority=10, block=True)


@bot_echo.handle()
async def _(args: Message = CommandArg()):
    if arg := args.extract_plain_text():
        await bot_echo.finish(arg)
