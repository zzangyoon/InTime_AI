from app.core.db import get_connection

def get_attendance_data(date: str):
    """
    주어진 날짜의 근태 데이터를 DB에서 조회하는 함수
    """

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            a.employee_id
            , m.name
            , a.check_date
            , a.check_in
            , a.check_out
            , a.check_in_method
            , a.check_out_method
            , a.memo
        FROM attendance a
        JOIN member m ON a.employee_id = m.employee_id
        WHERE a.check_date = ?
    """

    cursor.execute(query, (date,))
    rows = cursor.fetchall()
    conn.close()

    return rows

