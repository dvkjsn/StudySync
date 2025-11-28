# db.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("studysync.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dicts: row["email"]
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
