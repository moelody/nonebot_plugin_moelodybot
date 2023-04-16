# https://music.163.com/#/song?id=399249&userid=132242222
import re
import time

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from playwright.async_api import async_playwright


from ..bot_utils.util import generate_cache_image_path


from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="CSDN解析",
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


csdn = on_regex(
    r"(music.163.com)",
    flags=re.I, priority=99,
)


@csdn.handle()
async def _(event: GroupMessageEvent):
    text = str(event.message).strip()
    url = text

    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=r"/opt/google/chrome/chrome", headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url)
        time.sleep(2)

        top = page.locator(".blog-content-box")
        "f-ff2"
        out = generate_cache_image_path()

        await top.screenshot(path=out)

        await context.close()
        await browser.close()
        await csdn.finish(MS.image(out))
