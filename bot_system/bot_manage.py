import datetime
import time
import traceback

from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, GROUP_ADMIN, GROUP_OWNER
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from nonebot.adapters.onebot.v11.message import Message

from nonebot.log import logger
from nonebot.params import CommandArg, EventPlainText
from nonebot.typing import T_State


from ..bot_utils import text_to_image, get_root_path, convert_to_uri

test = on_command("test", priority=99, block=True)
bot_notice = on_command("通知", priority=10, block=True)
show_pet = on_command("pet", aliases={"表情包指令"}, priority=10, block=True)
kill_member = on_command("杀群友", priority=10, block=True)

record = on_message(priority=13, block=False)


@bot_notice.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    args = args.extract_plain_text()
    groups = await bot.get_group_list()
    msg = MS.text("通知: " + args)

    for group in groups:
        if group != str(event.group_id):
            await bot.send_group_msg(group_id=int(group.get("group_id")), message=msg)
            time.sleep(0.75)


@test.handle()
async def handle_test(bot: Bot, event: GroupMessageEvent):

    # rr = await bot.get_group_member_list(group_id=event.group_id, no_cache=False)
    # print(rr)

    text = ["思源黑体思源黑体是一套 OpenType/CFF 泛中日韩字体", "。这个开源项目不仅提供了可用的 OpenType 字体，还提供了利用 AFDKO 工具创建这些 OpenType 字体时的所有源文件。下载字体（OTF、OTC、Super OTC, Subset OTF 和 Variable OTF/TTF/WOFF2）",
            "本项目提供了为多种部署方式而设定的独立字体资源以及 ZIP 文件供下载：最新发布参考《官方字体 readme 文件》的 Configuratio", "ns（设置）部分，可以帮助您决定下载哪一套字体。推荐不熟悉 GitHub 的人士参照以英文、日文、韩文、简体中文、繁体中文提供的《思源字体官方下载指南》。", "您也可以两个 ZIP 文件形式下载整个 releases，内含所有设置。"]
    file = text_to_image(text)
    msg = MS.image(file)
    # msg = MS.text("已踢出 1255029890")
    await test.finish(msg)


@record.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    pass


def isKilled(timecode):
    today = datetime.datetime.today()
    six_months_ago = today - datetime.timedelta(days=180)
    timestamp = int(six_months_ago.timestamp())
    if timecode < timestamp:
        return True
    return False


@show_pet.handle()
async def handle_pet(bot: Bot, event: GroupMessageEvent):
    try:

        msg = MS.image(convert_to_uri(
            get_root_path() + "/data/images/表情包指令.jpg"))
        await bot.send_group_msg(group_id=event.group_id, message=msg)
    except Exception as e:
        await bot.send_group_msg(group_id=event.group_id, message="获取失败喵")
        logger.error(traceback.print_exc(), '错误信息为', e)


@kill_member.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State, mode: str = EventPlainText()):
    if await GROUP_ADMIN(bot, event) and await GROUP_OWNER(bot, event):
        await kill_member.send("小小群员 岂容你放肆!")

    else:
        group_info = await bot.get_group_member_list(group_id=event.group_id, no_cache=True)
        mems = [mem for mem in group_info if isKilled(
            mem.get('last_sent_time'))]

        msg = f"180天以上未发言的群友共有{len(mems)}个:\n"
        for m in mems:
            msg += str(m.get('user_id')) + '  ' + m.get('nickname') + '\n'
        if mems:

            state["kill_members"] = mems

            msg += "\n是否踢出(请回复 是/否)"
            print(msg)
            msg = MS.image(text_to_image(msg.split("\n")))
            await kill_member.pause(prompt=msg, at_sender=True)
        else:
            await kill_member.finish("群友都很活跃哦,没有潜水怪")


@kill_member.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State, mode: str = EventPlainText()):

    mems = state.get("kill_members", False)
    msg_success = "已成功踢出:\n"
    msg_fail = ""
    if mode == "是" and mems:
        for mem in mems:
            try:
                await bot.set_group_kick(group_id=event.group_id, user_id=mem.get('user_id'))
                time.sleep(0.5)
                msg_success += f"{mem.get('nickname')} {mem.get('user_id')}\n"
            except:
                msg_fail += f"{mem.get('nickname')} {mem.get('user_id')}\n"

        await kill_member.finish(msg_success + msg_fail)
    else:
        await kill_member.finish("已取消")
