import datetime
import time

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, GROUP_ADMIN, GROUP_OWNER
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from nonebot.adapters.onebot.v11.message import Message

from nonebot.params import CommandArg, EventPlainText
from nonebot.typing import T_State


from ..bot_utils import text_to_image

bot_notice = on_command("通知", priority=10, block=True)
kill_member = on_command("杀群友", priority=10, block=True)


def isKilled(timecode):
  today = datetime.datetime.now()
  six_months_ago = today - datetime.timedelta(days=180)
  timestamp = int(six_months_ago.timestamp())
  return timecode < timestamp


@bot_notice.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
  args = args.extract_plain_text()
  groups = await bot.get_group_list()
  msg = MS.text(f"通知: {args}")

  for group in groups:
    if group != str(event.group_id):
      await bot.send_group_msg(group_id=int(group.get("group_id")), message=msg)
      time.sleep(0.75)


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
  if mode == "是" and mems:
    msg_success = "已成功踢出:\n"
    msg_fail = ""
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
