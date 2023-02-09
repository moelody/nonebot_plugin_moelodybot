import random
import os
import aiohttp

from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as MS

from ..bot_utils import generate_cache_image_path, is_dragon, convert_to_uri, get_root_path

dragon = on_message(priority=20, block=False)
dragon_group = [444282933]


@dragon.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if event.group_id not in dragon_group:
        return
    for segment in event.get_message():
        if segment.type == "image":
            url = segment.data.get("url").split("?")[0]
            print(url)
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
                                if not chunk:
                                    break
                                f.write(chunk)

                        if is_dragon(file_path):
                            dragon_folder = get_root_path() + "/data/images/dragon_images"
                            random_file = dragon_folder + "/" + random.choice(
                                os.listdir(dragon_folder))

                            await dragon.finish(MS.image(convert_to_uri(random_file)))
