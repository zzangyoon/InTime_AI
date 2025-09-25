from datetime import datetime
from pathlib import Path
from automation.db.db_access import get_attendance_data
from automation.llm.llm_client import generate_report
import pandas as pd

STANDARD_TIME = "09:00:00"
BASE_DIR = Path(__file__).resolve().parents[2]  # automation/
PROMPT_DIR = BASE_DIR / "automation" / "llm" / "prompts"
# COLUMN_LIST = [
#     "employee_id", "name", "check_date", "check_in", "check_out",
#     "check_in_method", "check_out_method", "memo"
# ]

def make_attendance_report(date: str = None) -> str:
    """
    주어진 날짜의 근태 데이터를 요약 보고서 형태로 생성
    """
  
    # 1. 날짜 지정
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    print(f"date ::: {date}")

    # 2. DB 데이터 조회
    rows = get_attendance_data(date)

    if not rows:
        return f"{date}의 근태 데이터가 없습니다."
    
    # 3. DataFrame 변환
    data_frame = pd.DataFrame(rows, columns=[
        "employee_id", "name", "check_date", "check_in", "check_out",
        "check_in_method", "check_out_method", "memo"
    ])

    # 4. 전처리 및 가공
    df = merge_records(data_frame)

    ## 지각 & 근무시간 확인
    df["is_late"] = df["check_in"].apply(lambda t: t > f"{date} {STANDARD_TIME}")
    # df["working_hours"] = (df["check_out"] - df["check_in"]).dt.total_seconds() / 3600

    print(f"df ::: {df.columns.tolist()}")
    
    columns=[
        "employee_id", "name", "check_date", "check_in", "check_in_method", 
        "check_out", "check_out_method", "memo_in", "memo_out", "is_late"
    ]
    print(f"colums ::: {columns}")

    attendance_summary = df[columns].to_string(index=False)
    system_prompt = load_prompt("system.txt")
    user_prompt = load_prompt("user.txt")

    user_prompt = user_prompt.format(
        date = date,
        attendance_summary = attendance_summary
    )

    # local LLM
    response = generate_report(system_prompt, user_prompt)
    print(response)
    print(response.message.content)


def merge_records(df: pd.DataFrame) -> pd.DataFrame:
    """
    출근/퇴근 데이터가 분리된 상태에서
    날짜 + 사원별로 하나의 row로 병합된 DataFrame을 리턴.
    - 출근 : 가장 이른 시간
    - 퇴근 : 가장 늦은 시간
    """
    df_checkin = (
        df[df["check_in"].notna()]
        .sort_values(["employee_id", "check_date", "check_in"])
        .groupby(["employee_id", "check_date"], as_index = False)
        .first()
    )

    df_checkout = (
        df[df["check_out"].notna()]
        .sort_values(["employee_id", "check_date", "check_out"])
        .groupby(["employee_id", "check_date"], as_index = False)
        .last()
    )

    df_merged = pd.merge(
        df_checkin,
        df_checkout,
        on = ["employee_id", "check_date"],
        suffixes = ("_in", "_out"),
        how = "outer"
    )

    # merge 후 컬럼 정리
    df_final = df_merged[[
        "employee_id",
        "name_in",
        "check_date",
        "check_in_in",
        "check_in_method_in",
        "check_out_out",
        "check_out_method_out",
        "memo_in",
        "memo_out"
    ]]

    # 컬럼 rename
    df_final = df_final.rename(columns={
        "name_in" : "name",
        "check_in_in" : "check_in",
        "check_in_method_in" : "check_in_method",
        "check_out_out" : "check_out",
        "check_out_method_out" : "check_out_method"
    })

    return df_final

def load_prompt(filename: str) -> str:
    return (PROMPT_DIR / filename).read_text(encoding="utf-8")