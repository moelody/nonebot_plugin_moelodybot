from difflib import SequenceMatcher
import random
import re

from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent

from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="复读",
    description="复读群友消息",
    usage='''被动技能''',
    extra={
        "version": __version__,
        "license": "MIT",
        "author": "yueli",
        "command": [],
        "type": 0,
        "group": "娱乐功能"
    },
)
from ..config import commands

repeater_group = ["all"]  # 支持复读的群号,str[]
shortest = 2  # 最短复读字符
shortest_times = 2  # 最短复读次数
blacklist = []  # 违禁词
banlist = [680653092, 761708854]  # 在机器人后面复读的 都禁言

m = on_message(priority=10, block=False)

last_message = {}
message_times = {}


def similarity(s1, s2):
    try:
        return SequenceMatcher(None, s1, s2).ratio()
    except:
        return 0


# 消息预处理
def message_preprocess(message: str):
    raw_message = message
    images = re.findall(r'\[CQ:image.*?]', message)
    contained_images = {
        i: [
            re.findall(r'url=(.*?)[,\]]', i)[0][0],
            re.findall(r'file=(.*?)[,\]]', i)[0][0],
        ]
        for i in images
    }
    for i in contained_images:
        message = message.replace(i, f'[{contained_images[i][1]}]')
    return message, raw_message


@m.handle()
async def repeater(bot: Bot, event: GroupMessageEvent):
    # 检查是否在黑名单中 以及过滤掉机器人命令

    if event.raw_message in blacklist or event.raw_message in commands:
        return

    gid = str(event.group_id)
    if gid in repeater_group or "all" in repeater_group:
        global last_message, message_times
        message, raw_message = message_preprocess(str(event.message))

        similar = similarity(message, last_message.get(gid))
   
        # 如果当前消息与记录消息不符合
        if message != last_message.get(gid):
            message_times[gid] = 1
        elif similar >= 0.9:
            message_times[gid] += 1
        else:
            message_times[gid] += 1

        if message_times.get(gid) == shortest_times:
            await bot.send_group_msg(group_id=event.group_id, message=raw_message, auto_escape=False)
        elif message_times.get(gid, 1) > shortest_times and event.group_id in banlist:

            ranges = [(1, 5, 5), (6, 15, 20), (16, 45, 75),
                      (46, 75, 75), (76, 85, 20), (86, 90, 5)]
            award = ["SSR", "SR", "R", "R", "SR", "SSR"]

            random_range = random.choices(
                ranges, weights=[x[2] for x in ranges])[0]

            # 从选择的范围中随机生成一个整数
            random_num = random.randint(random_range[0], random_range[1])
            chosen_range_index = ranges.index(random_range)

            await bot.set_group_ban(group_id=event.group_id, user_id=event.user_id, duration=random_num * 60)

            user_info = await bot.get_stranger_info(user_id=event.user_id)
            username = event.user_id
            if user_info:
                username = user_info.get('nickname', 'unknown')

            print(award[chosen_range_index])

            await m.send(f"恭喜{username}获得「{award[chosen_range_index]}级」禁言卡,将在{random_num}分钟后解禁")

        last_message[gid] = message
