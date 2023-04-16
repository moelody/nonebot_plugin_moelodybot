
import random
import aiohttp

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from nonebot.params import RegexStr

from ..bot_utils.text_to_image import text_to_image


from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="随机教程/视频",
    description="根据关键词搜索b站视频",
    usage='''来点xx教程/来点xx视频)''',
    extra={
        "version": __version__,
        "license": "MIT",
        "author": "yueli",
        "command": [],
        "group": "随机功能"
    },
)

random_reply_list = [
    "emmm,要不试试「{}」",
    "来试试「{}」吧",
    "月灵觉得「{}」不错哟~",
    "就决定是你了!「{}」!",
    "月灵想要「{}」!",
]


random_tutorial = on_regex(
    r"(来点.+教程)|(来点.+视频)",
    priority=10, block=True
)


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
            await random_tutorial.send(MS.image("https:" + video["pic"]) + MS.image(img) + MS.text(f'链接:{video["arcurl"]}'))
