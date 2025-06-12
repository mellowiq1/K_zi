import sqlite3
from typing import Optional, Tuple

DB_PATH = "db/users.db"

def connect_db():
    """DB接続を返す"""
    return sqlite3.connect(DB_PATH)

def init_user(user_id: str):
    """ユーザーがなければ新規作成"""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, balance, bank, win_rate) VALUES (?, 0, 0, 1.0)", (user_id,))
    conn.commit()
    conn.close()

def get_balance(user_id: str) -> int:
    """ユーザーの所持金を取得。なければ0を返す"""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        return 0
    return row[0]

def get_bank(user_id: str) -> int:
    """ユーザーの金庫残高を取得。なければ0を返す"""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT bank FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        return 0
    return row[0]

def get_win_rate(user_id: str) -> float:
    """ユーザーの勝率倍率を取得。なければ1.0を返す"""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT win_rate FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        return 1.0
    return row[0]

def update_balance(user_id: str, amount: int):
    """所持金を増減(amountは正負可)"""
    init_user(user_id)
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def update_bank(user_id: str, amount: int):
    """金庫残高を増減(amountは正負可)"""
    init_user(user_id)
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET bank = bank + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def transfer_to_bank(user_id: str, amount: int) -> bool:
    """所持金から金庫へ移動。成功ならTrue, 不足ならFalse"""
    if amount <= 0:
        return False
    if get_balance(user_id) < amount:
        return False
    update_balance(user_id, -amount)
    update_bank(user_id, amount)
    return True

def transfer_from_bank(user_id: str, amount: int) -> bool:
    """金庫から所持金へ移動。成功ならTrue, 不足ならFalse"""
    if amount <= 0:
        return False
    if get_bank(user_id) < amount:
        return False
    update_bank(user_id, -amount)
    update_balance(user_id, amount)
    return True

def get_leaderboard(limit: int = 10) -> list[Tuple[str, int]]:
    """
    所持金+金庫の合計でランキング上位を取得。  
    戻り値は [(user_id, total_amount), ...] のリスト。
    """
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT user_id, (balance + bank) as total FROM users ORDER BY total DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

def set_win_rate(user_id: str, rate: float):
    """勝率倍率を設定"""
    init_user(user_id)
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET win_rate = ? WHERE user_id = ?", (rate, user_id))
    conn.commit()
    conn.close()
