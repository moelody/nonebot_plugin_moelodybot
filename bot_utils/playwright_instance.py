# # 创建 playwright 常驻后台
# import asyncio
from playwright.async_api import async_playwright


async def main2():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe", headless=False)
