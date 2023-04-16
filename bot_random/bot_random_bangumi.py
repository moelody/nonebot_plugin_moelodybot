
import random
import aiohttp

from nonebot import on_fullmatch
from nonebot.adapters.onebot.v11 import MessageSegment as MS


from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="随机番剧",
    description="从B站高评分获取的番剧",
    usage='''看什么番/看啥番/看啥动漫''',
    extra={
        "version": __version__,
        "license": "MIT",
        "author": "yueli",
        "command": ["看什么番", "看啥番", "看啥动漫"],
        "group": "随机功能"
    },
)

random_reply_list = [
    "emmm,要不试试「{}」",
    "来试试「{}」吧",
    "月灵觉得「{}」不错哟~",
    "就决定是你了!「{}」!",
    "月灵想看「{}」!",
]


random_bangumi = on_fullmatch(
    msg=("看什么番", "看啥番", "看啥动漫"),
    priority=10, block=True
)


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
