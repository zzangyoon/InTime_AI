# Query
from app.core.db import get_connection
from datetime import datetime
from zoneinfo import ZoneInfo

# ---------------------------------------
# insert
# ---------------------------------------
# member
def insert_member(employee_id: str, name: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO member_test(employee_id, name)
        VALUES(?, ?)
    """, (employee_id, name))

    conn.commit()
    conn.close()

# attendance
def insert_attendance(employee_id: str, method: str, img_filename: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 현재 시간(KST)
        now_datetime = datetime.now(ZoneInfo("Asia/Seoul"))
        now_kst = now_datetime.strftime("%Y-%m-%d %H:%M:%S")

        # 날짜만 뽑기
        today = now_datetime.date()

        cursor.execute("""
            INSERT INTO attendance_test(
                employee_id
                , check_date
                , check_in
                , check_in_method
                , check_in_img
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            employee_id
            , today
            , now_kst
            , method
            , img_filename
        ))
        conn.commit()
        return {"success" : True, "message" : "등록 성공"}

    except Exception as e:
        return {"success" : False, "message" : str(e)}
    
    finally:
        conn.close()


# ---------------------------------------
# select
# ---------------------------------------
# member
def get_all_members():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM member_test")
    result = cursor.fetchall()

    conn.close()
    return result

# attendance
def get_all_attendance():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM attendance_test")
    result = cursor.fetchall()

    conn.close()
    return result

# ocr 결과 확인
def check_member(name: str, id: str):
    rlt = 0
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM member_test WHERE employee_id = ? and name = ?", (id, name))
    result = cursor.fetchall()

    if result:
        rlt = 1

    conn.close()

    return rlt

# member 이름 확인
def check_member_name(id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name from member_test WHERE employee_id = ?", (id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        return None



# ---------------------------------------
# update
# ---------------------------------------
# attendance
def update_check_out(check_out: str, method: str, check_out_img: str, employee_id: str, check_date: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE attendance_test
        SET check_out = ?
            , check_out_method = ?
            , check_out_img = ?
        WHERE id = (
            SELECT id FROM attendance_test
            WHERE employee_id = ?
                AND check_date = ?
            ORDER BY reg_date DESC
            LIMIT 1
        )
    """, (check_out, method, check_out_img, employee_id, check_date))

    conn.commit()
    affected = cursor.rowcount
    conn.close()

    # affected > 0 : update 성공
    return affected > 0


# ---------------------------------------
# template
# ---------------------------------------
# def update_state():
#     conn = get_connection()
#     cursor = conn.cursor()

#     cursor.execute("""

#     """)

#     conn.commit()
#     conn.close()
