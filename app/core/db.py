# DB 연결
import sqlite3
from pathlib import Path

DB_PATH = Path("app/data/app.db")

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    return conn