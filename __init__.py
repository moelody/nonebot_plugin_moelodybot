import os
from pathlib import Path

from nonebot import load_all_plugins

src = "src.plugins."
load_all_plugins(

    [
        f"{src}nonebot_plugin_yuelibot.bot_link_analysis",
        f"{src}nonebot_plugin_yuelibot.bot_api",
        f"{src}nonebot_plugin_yuelibot.bot_utils"
    ],
    [
        "src/plugins/nonebot_plugin_yuelibot/bot_system",
        'src/plugins/nonebot_plugin_yuelibot/bot_funny',
        "src/plugins/nonebot_plugin_yuelibot/bot_scheduler",
        "src/plugins/nonebot_plugin_yuelibot/bot_random",
    ]
)

# 初始化项目(创建一些文件夹)

folder_list = [
    "cache", "fonts", "images", "qqgroup"
]
for folder in folder_list:
    to_create = Path().resolve() / "data" / folder
    if not to_create.exists():
        os.makedirs(str(to_create))


# 机器人忘记挂后台 重启前请打开

# from nonebot.message import event_preprocessor

# @event_preprocessor
# async def _():
#     raise "跳过"

# sudo supervisorctl restart bot1:bot1_00
# sudo supervisorctl stop bot1:bot1_00 && cd /www/wwwroot/project/Robot/nobot1 && nb run --reload

# sudo supervisorctl stop cq1:cq1_00 &&cd /www/wwwroot/project/Robot/nobot1/go-cqhttp && /www/wwwroot/project/Robot/nobot1/go-cqhttp/go-cqhttp
