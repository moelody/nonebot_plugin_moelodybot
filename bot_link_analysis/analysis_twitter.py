# https://twitter.com/seoamigo/status/1623199963210719232
import re
import time

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from playwright.async_api import async_playwright


from ..bot_utils.util import generate_cache_image_path, clean_link


from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="Twitter解析",
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


twitter = on_regex(
    r"(twitter.com)",
    flags=re.I, priority=99,
)


@twitter.handle()
async def _(event: GroupMessageEvent):
    text = event.get_plaintext().strip()
    url = clean_link(text)
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=r"/opt/google/chrome/chrome", headless=True, proxy={"server": "http://127.0.0.1:10809"})
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url)
        time.sleep(2)
        await page.evaluate("""() => {
            document.querySelector('.css-1dbjc4n.r-aqfbo4.r-gtdqiz.r-1gn8etr.r-1g40b8q').style.display = 'none';
                }""")

        top = page.locator("main .r-16y2uox.r-1wbh5a2.r-1ny4l3l")
        out = generate_cache_image_path()

        await top.screenshot(path=out)

        await browser.close()
        await twitter.finish(MS.image(out))
