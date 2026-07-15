
import sqlite3
import hashlib
import json
from datetime import datetime

from config import DB_PATH


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL, detail TEXT NOT NULL,
        timestamp TEXT NOT NULL, prev_hash TEXT NOT NULL, hash TEXT NOT NULL)""")
    conn.commit()
    conn.close()


def get_last_hash():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT hash FROM audit_log ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row[0] if row else "0" * 64


def add_audit_entry(action: str, detail: str):
    prev_hash = get_last_hash()
    timestamp = datetime.now().isoformat()
    payload = json.dumps({
        "action": action, "detail": detail,
        "timestamp": timestamp, "prev_hash": prev_hash
    })
    current_hash = hashlib.sha256(payload.encode()).hexdigest()
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO audit_log (action,detail,timestamp,prev_hash,hash) VALUES (?,?,?,?,?)",
        (action, detail, timestamp, prev_hash, current_hash)
    )
    conn.commit()
    conn.close()


def fetch_all_logs():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM audit_log ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    return rows
