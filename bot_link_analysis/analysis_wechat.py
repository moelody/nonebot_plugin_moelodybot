# https://mp.weixin.qq.com/s?__biz=MzI1
import re
import time


from nonebot import on_regex
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from playwright.async_api import async_playwright


from ..bot_utils.util import convert_to_uri, generate_cache_image_path


wechat = on_regex(
    r"(mp.weixin.qq)",
    flags=re.I, priority=99,
)


@wechat.handle()
async def _(event: GroupMessageEvent):

    url_regex = re.compile(r"(https?://[\w.-]+/\S*)")
    urls = url_regex.findall(str(event.get_message()))

    if urls == []:
        return
    else:
        url = urls[0]

    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=r"/opt/google/chrome/chrome", headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url)
        time.sleep(2)

        top = page.locator(".rich_media_wrp")
        await page.evaluate("""() => {
        sections = document.querySelectorAll("[data-tool=mdnice编辑器]")
        for (let index = 0; index < sections.length; index++) {
            if(index>8){
                sections[index].style.display="none"
            }
        }
        }""")

        out = generate_cache_image_path()

        await top.screenshot(path=out)

        await browser.close()
        await wechat.finish(MS.image(convert_to_uri(out)))
