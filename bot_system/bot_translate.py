

from nonebot import on_command
from nonebot.params import CommandArg

from ..bot_utils.translator import translate_youdao

from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="翻译",
    description="",
    usage='''翻译+英文''',
    extra={
        "version": __version__,
        "license": "MIT",
        "author": "yueli",
        "command": ["翻译"],
        "type": 1,
        "group": "实用功能"
    },
)

tran = on_command("translate", aliases={"翻译"}, priority=9, block=True)


@tran.handle()
async def _(args=CommandArg()):
    if arg := args.extract_plain_text():
        text = await translate_youdao(arg)
        if text:
            await tran.send(text)
