from nonebot import on_command
# from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11.message import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='echo',
    description='复述指令',
    usage='''echo + 需要机器人重复的内容''',
    extra={'version': '0.0.1'}
)

bot_echo = on_command("echo", priority=10, block=True)


@bot_echo.handle()
async def _(args: Message = CommandArg()):
    if arg := args.extract_plain_text():
        await bot_echo.finish(arg)
