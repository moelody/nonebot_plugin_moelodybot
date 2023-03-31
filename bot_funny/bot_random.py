
import random
import os
import aiohttp
import random

from nonebot import on_regex, on_keyword
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from nonebot.params import RegexStr

from ..bot_utils import get_root_path
from ..bot_utils import text_to_image
from pathlib import Path

# 菜单来源: https://github.com/Cvandia/nonebot-plugin-whateat-pic


from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="随机插件",
    description="",
    usage='''抽群友关键词 抽群友/抽..女群友/抽..男群友/抽老婆/抽老公
\t\t抽菜单关键词 吃什么, 吃啥, 饿饿, 换一个吃, 想吃''',
    extra={
        "version": __version__,
        "license": "MIT",
        "author": "yueli",
        "command": ["群友", "吃什么", "吃啥", "饿饿", "换一个吃", "想吃"],
        "group": "娱乐功能"
    },
)

random_reply_list = [
    "emmm,要不试试「{}」",
    "来试试「{}」吧",
    "月灵觉得「{}」不错哟~",
    "就决定是你了!「{}」!",
    "月灵想要「{}」!",
]

random_sel_member = on_regex(
    pattern="(抽.*群友)|(抽然然)|(抽老婆)|(抽老公)",
    priority=9, block=True)

random_eat = on_keyword(
    keywords={"吃什么", "吃啥", "饿饿", "换一个吃", "想吃"},
    priority=5, block=True
)

random_drink = on_regex(
    r"(喝什么)|(喝啥)|(渴)|(换一个喝)",
    priority=10, block=True
)
random_play = on_regex(
    r"(玩什么)|(玩啥)|(换一个玩)",
    priority=10, block=True
)

random_bangumi = on_regex(
    r"(看什么番)|(看啥番)|(看啥动漫)",
    priority=10, block=True
)

random_movie = on_regex(
    r"(看什么电影)|(看啥电影)",
    priority=10, block=True
)

random_tutorial = on_regex(
    r"(看.+教程)|(来点.+教程)|(来点.+视频)|(我想看*)",
    priority=10, block=True
)


@random_sel_member.handle()
async def random_mem(bot: Bot, event: GroupMessageEvent, cmd: str = RegexStr()):
    if "抽" not in cmd:
        return
    # if cmd == "抽然然":
    #     msg = MS.text("你抽到的群友是:傻然\n")
    #     msg += MS.image(
    #         "https://q.qlogo.cn/headimg_dl?dst_uin=21615991&spec=640")
    #     await random_sel_member.finish(message=msg, at_sender=True)

    group_info = await bot.get_group_member_list(group_id=event.group_id, no_cache=True)

    if "杀群友" in cmd:
        return

    elif any(keys in cmd for keys in ["女群友", "老婆"]):
        group_info = [mem for mem in group_info if mem.get('sex') == 'female']
    elif any(keys in cmd for keys in ["男群友", "老公"]):
        group_info = [mem for mem in group_info if mem.get('sex') == 'male']

    group_info = sorted(
        group_info, key=lambda x: x["last_sent_time"])[-50:]

    member_info = random.choice(group_info)
    user_id = member_info.get("user_id")
    nickname = member_info.get("nickname")

    msg = MS.text(f"你抽到的群友是:{nickname}\n")
    msg += MS.image(
        f"https://q.qlogo.cn/headimg_dl?dst_uin={user_id}&spec=640")

    await random_sel_member.finish(message=msg, at_sender=True)


@random_eat.handle()
async def _():
    random_folder = f"{get_root_path()}/data/images/eat_pic"
    filename = random.choice(
        os.listdir(random_folder))
    random_file = f"{random_folder}/{filename}"

    text = random.choice(random_reply_list).format(filename.split(".")[0])
    await random_eat.finish(MS.text(text) + MS.image(Path(random_file)))


@random_drink.handle()
async def _():
    random_folder = f"{get_root_path()}/data/images/drink_pic"
    filename = random.choice(
        os.listdir(random_folder))
    random_file = f"{random_folder}/{filename}"

    text = random.choice(random_reply_list).format(filename.split(".")[0])
    await random_drink.finish(MS.text(text) + MS.image(Path(random_file)))


@random_play.handle()
async def _():
    random_folder = f"{get_root_path()}/data/images/play_pic"
    filename = random.choice(
        os.listdir(random_folder))
    random_file = f"{random_folder}/{filename}"

    text = random.choice(random_reply_list).format(filename.split(".")[0])
    await random_play.finish(MS.text(text) + MS.image(Path(random_file)))


@random_bangumi.handle()
async def _():
    size = 800
    url = f'https://api.bilibili.com/pgc/season/index/result?order=4&sort=0&page=1&season_type=1&pagesize={size}&type=1'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.json()

            bangumi_id = random.randint(0, size)
            bangumi = content["data"]["list"][bangumi_id]
            await random_bangumi.send(MS.image(bangumi["cover"]) + MS.text(f'标题:{bangumi["title"]}\n链接:{bangumi["link"]}\n评分:{bangumi["score"]}\n发布:{bangumi["index_show"]}'))


@random_movie.handle()
async def _():
    size = 800
    url = f'https://api.bilibili.com/pgc/season/index/result?order=4&sort=0&page=1&season_type=2&pagesize={size}&type=1'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.json()
            bangumi_id = random.randint(0, size)
            bangumi = content["data"]["list"][bangumi_id]
            await random_movie.send(MS.image(bangumi["cover"]) + MS.text(f'标题:{bangumi["title"]}\n链接:{bangumi["link"]}\n评分:{bangumi["score"]}\n发布:{bangumi["index_show"]}'))


@random_tutorial.handle()
async def _(keyword=RegexStr()):
    cookie = "buvid3=7380002E-AC6C-7D99-6B92-C282D2DB4F6749511infoc; b_nut=1667477149; i-wanna-go-back=-1; _uuid=7476108D4-A238-E15A-EEEA-2D1DC1AA343850383infoc; buvid4=7F318D7B-F2AE-468C-BFC3-8C74C766BB7D50907-022110320-LN4tcKiizDOWmkssEpKBvA%3D%3D; buvid_fp_plain=undefined; DedeUserID=4279370; DedeUserID__ckMd5=2ae3c614d0814582; b_ut=5; nostalgia_conf=-1; balh_server_inner=__custom__; balh_is_closed=; hit-dyn-v2=1; LIVE_BUVID=AUTO5416677909752878; rpdid=|(u~||uRlRY|0J'uYY)lmllYR; dy_spec_agreed=1; blackside_state=1; CURRENT_BLACKGAP=0; CURRENT_FNVAL=4048; header_theme_version=CLOSE; fingerprint=6e87bb14c4e2656597cbde43ab6d8279; buvid_fp=76d5e614d080ff8d63fd86a21031fbf6; CURRENT_QUALITY=112; hit-new-style-dyn=1; SESSDATA=5e02777b%2C1694678103%2Cfc547%2A32; bili_jct=7254ae6e59c0e6ec16a9ac91a07740cf; sid=5hgl1o13; home_feed_column=5; bp_video_offset_4279370=774328487089537000; CURRENT_PID=fde67940-ca39-11ed-bd12-91a8b643da39; bp_t_offset_4279370=777726235702722593; innersign=1; b_lsid=B87CDBD1_187232F8AC8; PVID=1"

    for t in ["来点", "教程", "看", "视频"]:
        keyword = keyword.replace(t, "")

    page = random.randint(0, 30)
    video_id = random.randint(0, 19)
    url = f'https://api.bilibili.com/x/web-interface/wbi/search/all/v2?__refresh__=true&page_size=20&keyword={keyword}&page={page}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={'Cookie': cookie}) as response:
            content = await response.json()
            video = content["data"]["result"][10]["data"][video_id]
            title = video["title"].replace(
                r'<em class="keyword">', "").replace("</em>", "")

            img = text_to_image(
                [f'标题: {title}', f'作者: {video["author"]}', f'播放: {video["play"]}', f'时长: {video["duration"]}', f'简介: {video["description"]}'])
            await random_movie.send(MS.image("https:" + video["pic"]) + MS.image(img) + MS.text(f'链接:{video["arcurl"]}'))
