import re

from nonebot import logger, on_regex
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from .analysis_bilibili_utils import b23_extract, bili_keyword, config

from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="b站链接解析",
    description="b站链接解析",
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

analysis_bili = on_regex(
    r"(b23.tv)|(bili(22|23|33|2233).cn)|(.bilibili.com)|(^(av|cv)(\d+))|(^BV([a-zA-Z0-9]{10})+)|"
    r"(\[\[QQ小程序\]哔哩哔哩\])|(QQ小程序&amp;#93;哔哩哔哩)|(QQ小程序&#93;哔哩哔哩)",
    flags=re.I, priority=99,
)

blacklist = getattr(config, "analysis_blacklist", [])
group_blacklist = getattr(config, "analysis_group_blacklist", [])


@analysis_bili.handle()
async def analysis_main(event: GroupMessageEvent) -> None:

    text = str(event.message).strip()
    if blacklist and int(event.get_user_id()) in blacklist:
        return
    if re.search(r"(b23.tv)|(bili(22|23|33|2233).cn)", text, re.I):
        # 提前处理短链接，避免解析到其他的
        text = await b23_extract(text)
    group_id = event.group_id if hasattr(event, "group_id") else None
    if group_id in group_blacklist:
        return
    msg = await bili_keyword(group_id, text)

    if msg:
        try:
            await analysis_bili.send(msg)
        except Exception as e:
            logger.exception(e)
            logger.warning(f"{msg}\n此次解析可能被风控，尝试去除简介后发送！")
            msg = re.sub(r"简介.*", "", str(msg))
            await analysis_bili.send(msg)
