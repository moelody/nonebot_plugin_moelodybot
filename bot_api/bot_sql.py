from mysql.connector.pooling import MySQLConnectionPool
from nonebot.log import logger


class BotSql:
    def __init__(self):
        self.conn_pool = MySQLConnectionPool(
            pool_name="bot_pool", pool_size=5,
            host='127.0.0.1',
            user='bot',
            passwd='AfiEPyeHrMdE8XBx',
            db='bot',
            charset='utf8',
            autocommit=True  # 开启自动提交后，增删改操作无需手动调用connection.commit()
        )
        logger.info("连接数据库成功！")

    def close(self):
        del self.conn_pool
        logger.info("数据库关闭！")

    @classmethod
    def close_db(cls):
        BotSql().close()

    def get_cur(self):
        conn = self.conn_pool.get_connection()
        cur = conn.cursor()
        return conn, cur

    def execute_sql(self, sql, *params):
        with self.conn_pool.get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(sql, params)
                    return True, cur.rowcount
                except Exception as e:
                    return False, str(e)

    def get_data(self, sql, *query):
        with self.conn_pool.get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(sql, query)
                    headers = [i[0] for i in cur.description]
                    results = [dict(zip(headers, row))
                               for row in cur.fetchall()]
                    return True, results
                except Exception as e:
                    return False, str(e)


if __name__ == '__main__':
    ...
