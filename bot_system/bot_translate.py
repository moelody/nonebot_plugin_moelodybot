

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from nonebot.params import CommandArg

from ..bot_utils.translator import translate_youdao

tran = on_command("translate", aliases={"翻译"}, priority=9, block=True)


@tran.handle()
async def _(bot: Bot, event: GroupMessageEvent, args=CommandArg()):
    if arg := args.extract_plain_text():
        text = await translate_youdao(arg)
        msg = MS.text(text)
        await bot.send_group_msg(group_id=event.group_id, message=msg)
