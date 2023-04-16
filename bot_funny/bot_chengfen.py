from nonebot import on_command
from nonebot.adapters.onebot.v11.message import Message
from nonebot.params import CommandArg
from nonebot.log import logger

from playwright.async_api import async_playwright

import asyncio
from ..bot_utils.util import generate_cache_image_path
from nonebot.adapters.onebot.v11 import MessageSegment as MS
import time

from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="成分查看",
    description="查看B站用户成分",
    usage="""查成分 + B站uid""",
    extra={
        "version": __version__,
        "license": "MIT",
        "author": "yueli",
        "command": ["查成分"],
        "group": "娱乐功能"
    },
)

bt = on_command("成分", aliases={"成分查看"}, priority=9, block=True)


@bt.handle()
async def _(args: Message = CommandArg()):
    now = time.time()
    arg = args.extract_plain_text()
    if len(arg) < 2:
        return
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=r"/opt/google/chrome/chrome", headless=True)

        page = await browser.new_page()
        await page.goto(f'https://laplace.live/user/{arg}')
        # 异步等待
        await asyncio.sleep(4)

        top = page.locator('main [class*="Home_xl"]')

        # 使用.nth(0) 获取第一个元素
        img_path = generate_cache_image_path()
        await top.nth(0).screenshot(path=img_path)
        await browser.close()
        logger.info(time.time() - now)
        await bt.finish(MS.image(img_path))
