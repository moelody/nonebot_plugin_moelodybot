from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from ..bot_utils.text_to_image import text_to_image


test = on_command("test", priority=99, block=True)


@test.handle()
async def handle_test():
    text = ["思源黑体思推荐不熟两个 ZIP 文件形内含所有设置。"]
    file = text_to_image(text)
    msg = MS.image(file)
    await test.finish(msg)
