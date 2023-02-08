import os
from pathlib import Path

from nonebot import load_all_plugins

src = "src.plugins."
load_all_plugins(

    [
        f"{src}nonebot_plugin_yuelibot.analysis",
        f"{src}nonebot_plugin_yuelibot.bot_api",
        f"{src}nonebot_plugin_yuelibot.bot_utils"
    ],
    [
        "src/plugins/nonebot_plugin_yuelibot/bot_system",
        'src/plugins/nonebot_plugin_yuelibot/bot_funny',
        "src/plugins/nonebot_plugin_yuelibot/bot_scheduler_work",
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
