import traceback
import time

from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as MS

from nonebot.log import logger
from nonebot.typing import T_State


from ..bot_utils import text_to_image, get_root_path, convert_to_uri

test = on_command("test", priority=99, block=True)
show_pet = on_command("pet", aliases={"表情包指令"}, priority=10, block=True)
record = on_message(priority=13, block=False)


@test.handle()
async def handle_test(bot: Bot, event: GroupMessageEvent):
    text = ["思源黑体思源黑体是一套 OpenType/CFF 泛中日韩字体", "。这个开源项目不仅提供了可用的 OpenType 字体，还提供了利用 AFDKO 工具创建这些 OpenType 字体时的所有源文件。下载字体（OTF、OTC、Super OTC, Subset OTF 和 Variable OTF/TTF/WOFF2）",
            "本项目提供了为多种部署方式而设定的独立字体资源以及 ZIP 文件供下载：最新发布参考《官方字体 readme 文件》的 Configuratio", "ns（设置）部分，可以帮助您决定下载哪一套字体。推荐不熟悉 GitHub 的人士参照以英文、日文、韩文、简体中文、繁体中文提供的《思源字体官方下载指南》。", "您也可以两个 ZIP 文件形式下载整个 releases，内含所有设置。"]
    file = text_to_image(text)
    msg = MS.image(file)
    await test.finish(msg)


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
            img = convert_to_uri(
                get_root_path() + "/data/images/daxiaojie.gif")
            print(img)
            await record.finish(MS.image(img))

    if event.user_id == 963036493:
        last_sent_time = await bot.get_group_member_info(group_id=event.group_id, user_id=446480506, no_cache=True)
        global luwei_last_time

        if last_sent_time["last_sent_time"] - luwei_last_time > 3600:
            luwei_last_time = last_sent_time["last_sent_time"]
            await record.finish("芦苇大小姐嫁到")


@show_pet.handle()
async def handle_pet(bot: Bot, event: GroupMessageEvent):
    try:

        msg = MS.image(convert_to_uri(
            get_root_path() + "/data/images/表情包指令.jpg"))
        await bot.send_group_msg(group_id=event.group_id, message=msg)
    except Exception as e:
        await bot.send_group_msg(group_id=event.group_id, message="获取失败喵")
        logger.error(traceback.print_exc(), '错误信息为', e)
