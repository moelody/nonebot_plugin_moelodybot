from mysql.connector.pooling import MySQLConnectionPool
from ..config import database_password
from passlib.context import CryptContext

from .bot_type import UserCreate


# 初始化密码哈希工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 定义 MySQL 类


class BOT_SQL:
    def __init__(self):
        dbconfig = {
            "pool_name": "bot_pool",
            "pool_size": 5,
            "host": '127.0.0.1',
            "user": 'bot',
            "passwd": database_password,
            "db": 'bot',
            "charset": 'utf8',
            "autocommit": True  # 开启自动提交后，增删改操作无需手动调用connection.commit()
        }
        self.cnxpool = MySQLConnectionPool(**dbconfig)

    def close(self):
        self.cnxpool.close()
    # 获取数据库连接

    def get_connection(self):
        return self.cnxpool.get_connection()

    # 查询用户
    def get_user(self, username: str):
        with self.cnxpool.get_connection() as cnx:
            cursor = cnx.cursor()
            cursor.execute(
                f"SELECT * FROM `userdata` WHERE `username` = '{username}'")
            if result := cursor.fetchone():
                headers = [i[0]
                           for i in cursor.description]  # get column names

                return dict(zip(headers, result))

    # 创建用户
    def create_user(self, user: UserCreate):
        hashed_password = pwd_context.hash(user.password)
        with self.cnxpool.get_connection() as cnx:
            cursor = cnx.cursor()
            cursor.execute(
                f"INSERT INTO userdata (username, password) VALUES ('{user.username}', '{hashed_password}')")
            cnx.commit()


# 初始化 MySQL 实例
sql_manage = BOT_SQL()
