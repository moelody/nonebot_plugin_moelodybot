# from nonebot import require

# 定时任务
# scheduler = require("nonebot_plugin_apscheduler").scheduler


# @scheduler.scheduled_job("cron", hour=0, minute=0,id="xx")
# async def _():
#     print("每日零点重置任务")


# @scheduler.scheduled_job("interval",minutes=2, id="xxx")
# async def run_every_2_hour():
#     bot: Bot = get_bot()
#     await bot.send_group_msg(group_id=761708854,message="测试定时任务")
