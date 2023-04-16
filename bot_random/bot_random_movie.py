
import random
import aiohttp

from nonebot import on_fullmatch
from nonebot.adapters.onebot.v11 import MessageSegment as MS


from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="随机电影",
    description="B站高分榜随机抽电影",
    usage='''看什么电影/看啥电影''',
    extra={
        "version": __version__,
        "license": "MIT",
        "author": "yueli",
        "command": ["看什么电影", "看啥电影"],
        "group": "随机功能"
    },
)


random_movie = on_fullmatch(
    msg=("看什么电影", "看啥电影"),
    priority=10, block=True
)


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
