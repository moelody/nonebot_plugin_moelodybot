# https://behance.com/...
# @ https://www.behance.net/gallery/161360299/Cosmoses-?tracking_source=project_owner_other_projects

import re

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from playwright.async_api import async_playwright
import aiohttp
import aiofiles

from ..bot_utils.util import clean_link, generate_cache_image_path

from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="Behance解析",
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
    pattern=r"(behance.net)",
    flags=re.I
)


@github.handle()
async def _(event: GroupMessageEvent):
    text = str(event.message).strip()
    url = clean_link(text)
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=r"/opt/google/chrome/chrome", headless=True, proxy={"server": "http://127.0.0.1:10809"})
        page = await browser.new_page()

        await page.goto(url)

        cover_element = await page.wait_for_selector('meta[property="og:image"]', state="attached", timeout=10000)

        if cover_element:
            cover_url = await cover_element.get_attribute('content')

            if cover_url:
                title = await page.title()
                out = generate_cache_image_path()
                async with aiohttp.ClientSession() as session:
                    async with session.get(cover_url, proxy="http://127.0.0.1:10809") as response:
                        if response.status == 200:
                            # 使用异步I/O保存文件
                            async with aiofiles.open(out, "wb") as f:
                                async for data in response.content.iter_chunked(1024):
                                    await f.write(data)
                            print(f"封面已保存到本地：{out}")
                            await github.send(MS.text(title) + MS.image(file=out))

        await browser.close()
