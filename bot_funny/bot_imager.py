
import traceback

import aiohttp
from aiohttp import TCPConnector
from nonebot import on_command, on_regex
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from nonebot.log import logger
from nonebot.params import RawCommand

from ..bot_utils import handle_image, get_root_path, convert_to_uri

get_moe = on_regex(
    r"(moe)|(二次元)|(召唤老婆)|(我老婆呢)|(我的爱人)",
    priority=60, block=True)


get_setu = on_command(
    "setu", aliases={"st", "r18", "涩图"}, priority=60, block=True)

setu_group = []


@get_setu.handle()
async def get_setuu(bot: Bot, event: GroupMessageEvent, cmd: str = RawCommand()):
    gid = event.group_id
    if gid in setu_group:

        img_path = await get_st_url("https://api.lolicon.app/setu/v2?tag=萝莉|少女&tag=白丝|黑丝", cmd)
        if not img_path:
            await get_setu.finish("获取失败喵，图片失效")

        try:
            file_path = await handle_image(img_path)
            msg = MS.image(convert_to_uri(file_path))
            await get_setu.finish(msg)
        except Exception as e:
            msg = MS.text("获取失败喵")
            logger.error(traceback.print_exc(), '错误信息为', e)
            await get_setu.finish(msg)

    else:
        await get_setu.finish(MS.text("就会看涩图? 满脑子都是什么 (敲)"))


async def get_moe_url(url):
    async with aiohttp.ClientSession(connector=TCPConnector(ssl=False)) as session:
        async with session.get(url) as response:
            return response.url


async def get_st_url(url, cmd):
    params = {"r18": 1} if cmd == "r18" else {}
    async with aiohttp.ClientSession(connector=TCPConnector(ssl=True)) as session:
        async with session.get(url, params=params) as response:
            try:
                json = await response.json()
                tar_url = json["data"][0]["urls"]["original"]
                name = json["data"][0]["pid"]

                img = await session.get(tar_url, proxy='http://127.0.0.1:10809')
                content = await img.read()
                suffix = tar_url.split(".")[-1]
                target = (
                    f"{get_root_path()}/data/images/setu/{str(name)}.{suffix}"
                )

                with open(target, 'wb') as f:
                    f.write(content)
            except Exception:
                target = False

            return target


@get_moe.handle()
async def get_imagee():

    try:
        msg = await get_moe_url("https://api.ixiaowai.cn/api/api.php")
        await get_moe.finish(MS.image(str(msg)))
    except Exception:
        msg = await get_moe_url("https://www.dmoe.cc/random.php")
        await get_moe.finish(MS.image(str(msg)))
