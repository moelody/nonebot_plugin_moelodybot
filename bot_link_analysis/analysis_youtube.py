# https://www.youtube.com/watch?v=_P4P38X-8O4&ab_channel=KrisKong
import re

import aiohttp
from nonebot import on_regex
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from nonebot.params import EventPlainText

from ..bot_utils.translator import translate_youdao
from ..bot_utils import generate_cache_image_path, text_to_image


from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="youtube解析",
    description="",
    usage='''被动技能''',
    extra={
        "version": __version__,
        "license": "MIT",
        "author": "yueli",
        "command": [],
        "type": 0,
        "group": "链接解析"
    },
)

ytb = on_regex(
    r"(youtube.com)",
    flags=re.I, priority=99,
)

# 请更换自己的key, 可以免费申请
youtube_key = "AIzaSyDvKk4zrOCcF4MJEZeerPt9MdLNaUuw6Vs"


async def get_ytb_info(video_id: str, api_key: str):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={api_key}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, proxy='http://127.0.0.1:10809') as response:

            if response.status == 200:
                data = await response.json()

                title = data["items"][0]["snippet"]["title"]
                description = await translate_youdao(data["items"][0]["snippet"]["description"].replace("\n", "|"))
                assert description
                description = description.replace("|", "\n")
                if len(description) > 200:
                    description = f"{description[:200]}......"
                thumbnail_url = data["items"][0]["snippet"]["thumbnails"]["standard"]["url"]
                img = await session.get(thumbnail_url, proxy='http://127.0.0.1:10809')
                content = await img.read()
                target = generate_cache_image_path()

                with open(target, 'wb') as f:
                    f.write(content)
                img2 = text_to_image(
                    [f"链接：https://www.youtube.com/watch?v={video_id}", f"标题：{title}", "简介：{description}"])
                return MS.image(target) + MS.image(img2)


@ytb.handle()
async def _(bot: Bot, event: GroupMessageEvent, msg=EventPlainText()):

    pattern = "(?<=youtube\.com\/watch\?v=)[^&]+"
    if match := re.search(pattern, msg):
        video_id = match[0]
        msgs = await get_ytb_info(video_id, youtube_key)
        try:
            await ytb.finish(msgs)
        except Exception:
            await ytb.finish("获取失败喵")
