import os
import sqlite3
import threading
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'honeypot.db')
_lock = threading.Lock()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        service TEXT NOT NULL,
        src_ip TEXT NOT NULL,
        event_type TEXT NOT NULL,
        username TEXT,
        password TEXT,
        command TEXT,
        extra TEXT)''')
    conn.commit()
    conn.close()

def log_event(service, src_ip, event_type, username=None, password=None,
              command=None, extra=None):
    ts = datetime.now(timezone.utc).isoformat(timespec='seconds')
    with _lock:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.execute(
            'INSERT INTO events (timestamp, service, src_ip, event_type, '
            'username, password, command, extra) VALUES (?,?,?,?,?,?,?,?)',
            (ts, service, src_ip, event_type, username, password, command, extra))
        conn.commit()
        conn.close()
    print(f'[{ts}] {service} {src_ip} {event_type} '
          f'{username or ""} {password or ""} {command or ""}')
