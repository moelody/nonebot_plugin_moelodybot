

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from ..bot_utils.util import tran_deepl_pro


# import langid
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="翻译",
    description="",
    usage='''翻译 + 要翻译的内容(=> 中文)''',
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
        res = tran_deepl_pro(arg)
        await tran.send(res)
