
import random

from nonebot import get_driver, on_message, on_notice
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, PokeNotifyEvent
from nonebot.rule import to_me

config = get_driver().config

at_reply = ["我在呐~", "干神马！"]
at_super_reply = ["主人主人~", "主人我在呐~"]
poke_reply = ["不要再戳啦!!", "再戳我可生气了!", "我在呢~"]
poke_super_reply = ["主人干嘛呀~"]

poke = on_notice(priority=11, block=True)
at = on_message(priority=10, block=False, rule=to_me())


@poke.handle()
async def _poke(bot: Bot, event: PokeNotifyEvent):

    if str(event.target_id) == bot.self_id:

        if str(event.user_id) in config.superusers:
            msg = random.choice(poke_super_reply)
        else:
            msg = random.choice(poke_reply)

        await bot.send_msg(group_id=event.group_id, message=msg)

    # await bot.send_group_msg(group_id=event.group_id,message=msg)


@at.handle()
async def _(event: GroupMessageEvent):

    if event.user_id == 1255029890:
        return
    if str(event.user_id) in config.superusers:
        await at.finish(random.choice(at_super_reply))
    else:
        await at.finish(random.choice(at_reply))
