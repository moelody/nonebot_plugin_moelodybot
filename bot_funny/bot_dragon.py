import random
import os
import aiohttp

from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as MS

from ..bot_utils import generate_timestamp, get_root_path, is_dragon, convert_to_uri

dragon = on_message(priority=20, block=False)


@dragon.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    for segment in event.get_message():
        if segment.type == "image":

            url = segment.data.get("url").split("?")[0]

            file_path = get_root_path() + "/data/cache/" + generate_timestamp() + ".jpg"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        with open(file_path, 'wb') as f:
                            while True:
                                chunk = await resp.content.read(1024)
                                if not chunk:
                                    break
                                f.write(chunk)

                        if is_dragon(file_path):
                            dragon_folder = get_root_path() + "/data/images/dragon_images"
                            random_file = dragon_folder + "/" + random.choice(
                                os.listdir(dragon_folder))

                            await dragon.finish(MS.image(convert_to_uri(random_file)))
