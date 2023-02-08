from nonebot import load_all_plugins

load_all_plugins(

    [
        'src.plugins.nonebot_plugin_yuelibot.analysis.analysis_bilibili',
        'src.plugins.nonebot_plugin_yuelibot.analysis.analysis_youtube',
        'src.plugins.nonebot_plugin_yuelibot.analysis.analysis_weibo',
        'src.plugins.nonebot_plugin_yuelibot.analysis.analysis_twitter',
        'src.plugins.nonebot_plugin_yuelibot.analysis.analysis_github',
    ],
    []
)
