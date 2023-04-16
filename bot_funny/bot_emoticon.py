import traceback
from pathlib import Path

from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as MS

from nonebot.log import logger
from nonebot.typing import T_State


from ..bot_utils.util import get_root_path


from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="表情包生成",
    description="",
    usage='''表情包指令:查看所有指令''',
    extra={
        "version": __version__,
        "license": "MIT",
        "author": "yueli",
        "command": ["表情包指令"],
        "type": 1,
        "group": "娱乐功能"
    },
)


show_pet = on_command("pet", aliases={"表情包指令"}, priority=10, block=True)
record = on_message(priority=13, block=False)


daxiaojie_last_time = 0
luwei_last_time = 0


@record.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    if event.group_id != 444282933:
        return

    if event.user_id == 446480506:
        last_sent_time = await bot.get_group_member_info(group_id=event.group_id, user_id=446480506, no_cache=True)
        global daxiaojie_last_time

        if last_sent_time["last_sent_time"] - daxiaojie_last_time > 3600:

            daxiaojie_last_time = last_sent_time["last_sent_time"]
            img = Path(
                f"{get_root_path()}/data/images/daxiaojie.gif")
            await record.finish(MS.image(img))

    if event.user_id == 963036493:
        last_sent_time = await bot.get_group_member_info(group_id=event.group_id, user_id=446480506, no_cache=True)
        global luwei_last_time

        if last_sent_time["last_sent_time"] - luwei_last_time > 3600:
            luwei_last_time = last_sent_time["last_sent_time"]
            img = Path(
                f"{get_root_path()}/data/images/start_dragon.jpg")
            await record.finish(MS.text("芦苇大小姐嫁到") + MS.image(img))


@show_pet.handle()
async def handle_pet(bot: Bot, event: GroupMessageEvent):
    try:

        msg = MS.image(Path(
            f"{get_root_path()}/data/images/表情包指令.jpg"))
        await show_pet.send(message=msg)
    except Exception as e:
        await bot.send_group_msg(group_id=event.group_id, message="获取失败喵")
        traceback.print_exc()
        logger.error(e)
