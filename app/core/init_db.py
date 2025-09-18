# 테이블 생성 (초기화 스크립트)
# python -m app.core.init_db 로 실행
from app.core.db import get_connection


# ------------------------------
# member, attendance table 생성
# ------------------------------
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # member
    cursor.execute("""
        CREATE TABLE member(
            id INTEGER PRIMARY KEY AUTOINCREMENT
            , employee_id TEXT UNIQUE NOT NULL
            , name TEXT NOT NULL
            , reg_date TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)

    # attendance
    cursor.execute("""
        CREATE TABLE attendance(
            id INTEGER PRIMARY KEY AUTOINCREMENT
            , employee_id TEXT NOT NULL
            , check_date TEXT NOT NULL
            , check_in TEXT
            , check_out TEXT
            , check_in_method TEXT
            , check_out_method TEXT
            , check_in_img TEXT
            , check_out_img TEXT
            , reg_date TEXT DEFAULT (datetime('now', 'localtime'))
            , memo TEXT
            , FOREIGN KEY (employee_id) REFERENCES member(employee_id)
        )
    """)

    conn.commit()
    conn.close()
    print("!!! DB 초기화 완료")


# -----------------------------------
# member, attendance test table 생성
# -----------------------------------
def create_test_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # member_test
    cursor.execute("""
        CREATE TABLE member_test (
            id INTEGER PRIMARY KEY AUTOINCREMENT
            , employee_id TEXT UNIQUE NOT NULL
            , name TEXT NOT NULL
            , reg_date TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)

    # attendance
    cursor.execute("""
        CREATE TABLE attendance_test(
            id INTEGER PRIMARY KEY AUTOINCREMENT
            , employee_id TEXT NOT NULL
            , check_date TEXT NOT NULL
            , check_in TEXT
            , check_out TEXT
            , check_in_method TEXT
            , check_out_method TEXT
            , check_in_img TEXT
            , check_out_img TEXT
            , reg_date TEXT DEFAULT (datetime('now', 'localtime'))
            , memo TEXT
            , FOREIGN KEY (employee_id) REFERENCES member(employee_id)
        )
    """)

    conn.commit()
    conn.close()
    print("!!! test_DB 초기화 완료")


# ------------
# drop
# ------------
def drop_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DROP TABLE member_test;
    """)
    print("!!! drop 완료")




if __name__ == "__main__":
    create_tables()