import random
import os
import aiohttp

from nonebot import on_message, on_keyword
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as MS

from ..bot_utils import generate_cache_image_path, is_dragon, get_root_path
from pathlib import Path


from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="龙图插件",
    description="使用龙图斗图",
    usage="""关键字含龙图,或者发送龙图""",
    extra={
        "version": __version__,
        "license": "MIT",
        "author": "yueli",
        "command": ["龙图"],
        "group": "娱乐功能"
    },
)

dragon = on_message(priority=20, block=False)
dragon_group = [444282933, 303281689, 680653092, 567072663, 761708854]
dragon_group2 = [444282933, 303281689,
                 680653092, 567072663, 761708854, 229514925]

dragon_cmd = on_keyword(
    keywords={"龙图"},
    priority=10, block=False
)
dragon_folder = f"{get_root_path()}/data/images/dragon_images"


@dragon_cmd.handle()
async def _(event: GroupMessageEvent):
    if event.group_id not in dragon_group2:
        return
    random_file = f"{dragon_folder}/{random.choice(os.listdir(dragon_folder))}"
    await dragon_cmd.finish(MS.image(Path(random_file)))


@dragon.handle()
async def _(event: GroupMessageEvent):
    if event.group_id not in dragon_group:
        return

    for segment in event.get_message():
        if segment.type != "image":
            continue

        url = segment.data.get("url")
        if not url:
            continue

        url = url.split("?")[0]
        file_path = generate_cache_image_path()

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    continue

                with file_path.open('wb') as f:
                    while True:
                        chunk = await resp.content.read(1024)
                        if chunk[:6] in (b'GIF87a', b'GIF89a'):
                            return

                        if not chunk:
                            break

                        f.write(chunk)

                if is_dragon(file_path):
                    random_file = f"{dragon_folder}/{random.choice(os.listdir(dragon_folder))}"
                    await dragon.finish(MS.image(Path(random_file)))
