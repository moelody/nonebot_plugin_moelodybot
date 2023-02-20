import random
import os
import aiohttp

from nonebot import on_message, on_keyword
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as MS

from ..bot_utils import generate_cache_image_path, is_dragon, convert_to_uri, get_root_path

dragon = on_message(priority=20, block=False)
dragon_group = [444282933, 303281689, 680653092, 567072663]

dragon_cmd = on_keyword(
    keywords={"龙图"},
    priority=10, block=True
)
dragon_folder = f"{get_root_path()}/data/images/dragon_images"


@dragon_cmd.handle()
async def _(event: GroupMessageEvent):
    if event.group_id not in dragon_group:
        return
    random_file = f"{dragon_folder}/{random.choice(os.listdir(dragon_folder))}"
    await dragon_cmd.finish(MS.image(convert_to_uri(random_file)))


@dragon.handle()
async def _(event: GroupMessageEvent):
    if event.group_id not in dragon_group:
        return
    for segment in event.get_message():
        if segment.type == "image":
            if url := segment.data.get("url"):
                url = url.split("?")[0]
                file_path = generate_cache_image_path()
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            with open(file_path, 'wb') as f:
                                while True:
                                    chunk = await resp.content.read(1024)
                                    # 判断是不是gif 是则跳过
                                    if chunk[:6] in (b'GIF87a', b'GIF89a'):
                                        return
                                    if chunk:
                                        f.write(chunk)

                                    else:
                                        break
                            if is_dragon(file_path):
                                random_file = f"{dragon_folder}/{random.choice(os.listdir(dragon_folder))}"
                                await dragon.finish(MS.image(convert_to_uri(random_file)))
