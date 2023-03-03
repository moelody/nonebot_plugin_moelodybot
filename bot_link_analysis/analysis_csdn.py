# https://blog.csdn.net/...
import re
import time

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from playwright.async_api import async_playwright


from ..bot_utils.util import clean_link, generate_cache_image_path


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


github = on_regex(
    r"(blog.csdn.net)",
    flags=re.I, priority=99,
)


@github.handle()
async def _(event: GroupMessageEvent):
    text = str(event.message).strip()
    url = clean_link(text)

    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=r"/opt/google/chrome/chrome", headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url)
        time.sleep(4)
        await page.evaluate("""() => {
            document.querySelector('#blogColumnPayAdvert').style.display = 'none';
                }""")
        await page.evaluate("""() => {
        document.querySelector('.toolbar-btn-login').remove();
            }""")
        top = page.locator(".blog-content-box")

        out = generate_cache_image_path()

        await top.screenshot(path=out)

        await context.close()
        await browser.close()
        await github.finish(MS.image(out))
