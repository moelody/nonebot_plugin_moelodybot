# https://m.weibo.cn/5406347304/4865375575212157
# https://weibo.com/1855501681/Ms2fgBU9Q


from nonebot.plugin import PluginMetadata
import re

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from playwright.async_api import async_playwright
from ..bot_utils.util import generate_cache_image_path, clean_link

analysis_weibo = on_regex(
    r"(weibo.com)|(weibo.cn)",
    flags=re.I, priority=99,
)


__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="微博解析",
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


@analysis_weibo.handle()
async def _(event: GroupMessageEvent):
    text = event.get_plaintext().strip()
    url = clean_link(text)

    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=r"/opt/google/chrome/chrome", headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url)

        # 获取所有li 使用locator
        if "https://m.weibo" in url:
            await page.evaluate("""() => {
            document.querySelector('.lite-topbar').style.display = 'none';
                }""")
            await page.evaluate("""() => {
                document.querySelector('.lite-page-editor').style.display = 'none';
                }""")
            top = page.locator(".f-weibo")
        elif "https://weibo" in url:
            top = page.locator("article.woo-panel-top")
        else:
            top = ""
        out = generate_cache_image_path()
        assert top
        await top.screenshot(path=out)

        await browser.close()
        await analysis_weibo.finish(MS.image(out))
