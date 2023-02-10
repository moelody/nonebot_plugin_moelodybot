
import traceback

import aiohttp
from aiohttp import TCPConnector
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from nonebot.log import logger
from nonebot.params import RawCommand

from ..bot_utils import handle_image, get_root_path, convert_to_uri

get_image = on_command("moe", aliases={"二次元"}, priority=9, block=True)
get_setu = on_command(
    "setu", aliases={"st", "r18", "涩图"}, priority=9, block=True)

setu_group = []


@get_setu.handle()
async def get_setuu(bot: Bot, event: GroupMessageEvent, cmd: str = RawCommand()):
    gid = event.group_id
    if gid in setu_group:

        img_path = await get_url2("https://api.lolicon.app/setu/v2?tag=萝莉|少女&tag=白丝|黑丝", cmd)
        print(img_path)
        if not img_path:
            get_setu.finish("获取失败喵，图片失效")

        try:
            file_path = await handle_image(img_path)
            msg = MS.image(convert_to_uri(file_path))
            await bot.send_group_msg(group_id=gid, message=msg)
        except Exception as e:
            msg = MS.text("获取失败喵")
            await bot.send_group_msg(group_id=gid, message=msg)
            logger.error(traceback.print_exc(), '错误信息为', e)

    else:
        await get_setu.finish(MS.text("就会看涩图? 满脑子都是什么 (敲)"))


async def get_url(url):
    async with aiohttp.ClientSession(connector=TCPConnector(ssl=False)) as session:
        async with session.get(url) as response:
            return response.url


async def get_url2(url, cmd):
    params = {"r18": 1} if cmd == "r18" else {}
    async with aiohttp.ClientSession(connector=TCPConnector(ssl=True)) as session:
        async with session.get(url, params=params) as response:
            try:
                json = await response.json()
                tar_url = json["data"][0]["urls"]["original"]
                name = json["data"][0]["pid"]
                print(tar_url)
                img = await session.get(tar_url, proxy='http://127.0.0.1:10809')
                content = await img.read()
                target = (
                    f"{get_root_path()}/data/images/setu/{str(name)}."
                    + tar_url.split(".")[-1]
                )

                with open(target, 'wb') as f:
                    f.write(content)
            except Exception:
                target = False

            return target


@get_image.handle()
async def get_imagee():

    try:
        msg = await get_url("https://api.ixiaowai.cn/api/api.php")
        await get_image.finish(MS.image(str(msg)))
    except Exception as e:
        logger.error(traceback.print_exc(), '错误信息为', e)
        msg = await get_url("https://www.dmoe.cc/random.php")

    await get_image.finish(MS.image(str(msg)))
