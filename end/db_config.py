import pymysql
from contextlib import contextmanager

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',       # 你的MySQL用户名
    'password': '990923',
    'database': 'grading_system',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

@contextmanager
def get_db_connection():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()