# https://m.weibo.cn/5406347304/4865375575212157
# https://weibo.com/1855501681/Ms2fgBU9Q


import re

from nonebot import on_regex
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from playwright.async_api import async_playwright
from ..bot_utils import generate_cache_image_path, clean_link,  convert_to_uri

analysis_weibo = on_regex(
    r"(weibo.com)|(weibo.cn)",
    flags=re.I, priority=99,
)


@analysis_weibo.handle()
async def _(event: Event):
  text = str(event.message).strip()
  url = clean_link(text)

  async with async_playwright() as p:
    browser = await p.chromium.launch(executable_path=r"/opt/google/chrome/chrome", headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto(url)

    # 获取所有li 使用locator
    if url.startswith("https://m.weibo"):
      await page.evaluate("""() => {
            document.querySelector('.lite-topbar').style.display = 'none';
                }""")
      await page.evaluate("""() => {
                document.querySelector('.lite-page-editor').style.display = 'none';
                }""")
      top = page.locator(".f-weibo")
    elif url.startswith("https://weibo"):
      top = page.locator("article.woo-panel-top")
    out = generate_cache_image_path()

    await top.screenshot(path=out)

    await browser.close()
    await analysis_weibo.finish(MS.image(convert_to_uri(out)))
