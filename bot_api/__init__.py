from nonebot import load_all_plugins

load_all_plugins(

    [
        'src.plugins.nonebot_plugin_yuelibot.bot_api.bot_reply',
        "src.plugins.nonebot_plugin_yuelibot.bot_api.bot_reply_api",
        'src.plugins.nonebot_plugin_yuelibot.bot_api.bot_plan',
        "src.plugins.nonebot_plugin_yuelibot.bot_api.bot_plan_api",
        "src.plugins.nonebot_plugin_yuelibot.bot_api.bot_auth",
        "src.plugins.nonebot_plugin_yuelibot.bot_api.bot_auth_api",
    ],
    []
)
