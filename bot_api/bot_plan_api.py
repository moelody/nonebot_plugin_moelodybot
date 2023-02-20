
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from nonebot import get_app, get_driver

from .bot_auth import AuthHandler
from .bot_plan import refresh_plan_data
from .bot_sql import sql_manage

import datetime

driver = get_driver()


def timestamp2mysqltime(timestamp):
    """
    结束日期默认为'NULL' 则返回None 进sql 为NULL
    起始日期默认为"" 则返回当前时间
    """
    if timestamp == 'NULL':
        return None
    timestamp = (
        float(timestamp) if timestamp else datetime.datetime.now().timestamp()
    )
    timestamp = float(timestamp)
    my_datetime = datetime.datetime.fromtimestamp(timestamp)
    return my_datetime.strftime('%Y-%m-%d %H:%M:%S')


@driver.on_startup
async def init_plan():

    refresh_plan_data()
    app: FastAPI = get_app()

    # 2、声明一个 源 列表；重点：要包含跨域的客户端 源
    origins = ["*"]

    # 3、配置 CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # 允许访问的源
        allow_credentials=True,  # 支持 cookie
        allow_methods=["*"],  # 允许使用的请求方法
        allow_headers=["*"]  # 允许携带的 Headers
    )

    @app.get("/api/plan/all_plan_list")
    async def _():
        state, sqldata = refresh_plan_data()
        return {"status": 200, "msg": "获取成功", "sqldata": sqldata}

    @app.get("/api/plan/list")
    async def _(token: str):

        token_state, data = AuthHandler.parse_token(token)

        if token_state:
            if (data.get("usertype") == "admin"):
                admin_status, sqldata = refresh_plan_data()
                return {"status": 200, "msg": "获取成功", "token": token, "sqldata": sqldata}

        else:
            return {"status": 401, "msg": "获取失败"}

    @app.get("/api/plan/add")
    async def _(token: str, title: str, content: str = "NULL", period: str = "task", create_date: str = "", finish_date: str = 'NULL', category: str = "NULL", tag: str = "NULL", status: str = "draft", priority: str = "1"):
        if not title:
            return {"status": 401, "msg": "title不可以为空"}

        state, data = AuthHandler.parse_token(token)
        if state:

            sql = """INSERT INTO `plandata` (`title`, `content`, `period`, `create_date`, `finish_date`, `category`, `tag`, `status`, `priority`) VALUES (%s, %s, %s,%s,%s, %s, %s,%s,%s);"""
            state, msg = sql_manage.get_data(
                sql, title, content, period, timestamp2mysqltime(create_date), timestamp2mysqltime(finish_date), category, tag, status, priority)
            return {"status": 200, "msg": "添加成功"} if state else {"status": 401, "msg": msg}
        else:
            return {"status": 401, "msg": "添加失败"}

    @app.get("/api/plan/update")
    async def _(token: str, plan_id: str, title: str, content: str = "NULL", period: str = "task", finish_date='NULL', category: str = "NULL", tag: str = "NULL", status: str = "draft", priority: str = "1"):
        # todo 感觉不用加
        if not title or not token:
            return {"status": 401, "msg": "token plan_id 和 title 不可以为空"}

        state, data = AuthHandler.parse_token(token)

        if state:
            sql = "UPDATE `plandata` SET `title` = %s, `content` = %s, `period` = %s , `finish_date` = %s, `category` = %s, `tag` = %s, `status` = %s ,`priority` = %s  WHERE `plandata`.`ID` = %s;"
            status, msg = sql_manage.get_data(
                sql, title, content, period, timestamp2mysqltime(finish_date), category, tag, status, priority, plan_id)
            if status:
                return {"status": 200, "msg": "添加成功"}
            else:
                return {"status": 401, "msg": msg}
        else:
            return {"status": 401, "msg": "添加失败"}

    @app.get("/api/plan/delete")
    async def _(token: str, plan_id: str):

        status, data = AuthHandler.parse_token(token)
        # 没有判断用户, 可以加个是管理员 可以无视用户
        if status:
            sql = "DELETE FROM `plandata` WHERE `id` = %s;"
            status, msg = sql_manage.get_data(
                sql, plan_id)
            if status:
                return {"status": 200, "msg": "删除成功"}
            else:
                return {"status": 401, "msg": msg}
        else:
            return {"status": 401, "msg": "删除失败"}


@driver.on_shutdown
async def close_db():
    sql_manage.close()


if __name__ == '__main__':
    ...
