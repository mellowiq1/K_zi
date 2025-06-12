# db/init_db.py
import sqlite3
import os

def create_users_table():
    os.makedirs("db", exist_ok=True)  # dbフォルダがない場合は作成
    conn = sqlite3.connect("db/users.db")
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        balance INTEGER DEFAULT 1000,
        bank INTEGER DEFAULT 0,
        win_rate REAL DEFAULT 1.0
    )
    """)
    conn.commit()
    conn.close()
