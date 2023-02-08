import mysql.connector
from nonebot.log import logger


class BotSql:

    def __init__(self):
        self.conn = mysql.connector.connect(
            host='127.0.0.1',
            user='bot',
            passwd='AfiEPyeHrMdE8XBx',
            db='bot',
            charset='utf8',
            autocommit=True  # 开启自动提交后，增删改操作无需手动调用connection.commit()
        )

    def close(self):
        self.conn.close()
        logger.info("数据库关闭！")

    @classmethod
    def close_db(cls):
        BotSql().close()

    def add_data(self, sql, *query):
        cur = self.conn.cursor()
        try:

            cur.execute(sql, (*query, ))
            return True, 1
        except Exception as e:
            return False, e
        finally:
            cur.close()

    def delete_data(self, sql, *query):
        cur = self.conn.cursor()
        try:

            cur.execute(sql, (*query, ))
            return True, 1
        except Exception as e:
            return False, e
        finally:
            cur.close()

    def get_data(self, sql, *query):
        cur = self.conn.cursor()
        rest = (False, "")
        try:
            cur.execute(sql, query)
            rest = (True, cur.fetchall())
        except Exception as e:
            rest = (False, e)
        finally:
            cur.close()
            return rest


if __name__ == '__main__':
    ...
