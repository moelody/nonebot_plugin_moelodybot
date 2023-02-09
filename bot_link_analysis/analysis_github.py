# https://github.com/...
import re
import time

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from playwright.async_api import async_playwright


from ..bot_utils.util import clean_link, convert_to_uri, generate_cache_image_path


github = on_regex(
    r"(github.com)",
    flags=re.I,
)


@github.handle()
async def _(event: GroupMessageEvent):
    text = str(event.message).strip()
    url = clean_link(text)
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=r"/opt/google/chrome/chrome", headless=True, proxy={"server": "http://127.0.0.1:10809"})
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url)
        time.sleep(2)

        top = page.locator("readme-toc")
        out = generate_cache_image_path()

        await top.screenshot(path=out)

        await browser.close()
        await github.finish(MS.image(convert_to_uri(out)))
