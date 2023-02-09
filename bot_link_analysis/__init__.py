from nonebot import load_all_plugins

load_all_plugins(

    [
        'src.plugins.nonebot_plugin_yuelibot.bot_link_analysis.analysis_bilibili',
        'src.plugins.nonebot_plugin_yuelibot.bot_link_analysis.analysis_youtube',
        'src.plugins.nonebot_plugin_yuelibot.bot_link_analysis.analysis_weibo',
        'src.plugins.nonebot_plugin_yuelibot.bot_link_analysis.analysis_wechat',
        'src.plugins.nonebot_plugin_yuelibot.bot_link_analysis.analysis_twitter',
        'src.plugins.nonebot_plugin_yuelibot.bot_link_analysis.analysis_github',
    ],
    []
)
