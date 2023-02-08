# https://twitter.com/seoamigo/status/1623199963210719232
import re
import time

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from playwright.async_api import async_playwright


from ..bot_utils.util import generate_timestamp, get_root_path, clean_link, convert_to_uri


twitter = on_regex(
    r"(twitter.com)",
    flags=re.I,
)


@twitter.handle()
async def _(event: GroupMessageEvent):
    text = str(event.message).strip()
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
        out = get_root_path() + "/data/cache/" + generate_timestamp() + ".jpg"

        await top.screenshot(path=out)

        await browser.close()
        await twitter.finish(MS.image(convert_to_uri(out)))
