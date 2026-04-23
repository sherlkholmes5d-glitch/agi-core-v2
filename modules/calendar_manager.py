import sqlite3
import json
import datetime
from pathlib import Path

class CalendarManager:
    def __init__(self, db_path="data/calendar.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                start_time TEXT,
                end_time TEXT,
                event_type TEXT,
                priority INTEGER,
                status TEXT,
                tags TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def add_event(self, event_data):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO events 
            (id, title, description, start_time, end_time, event_type, priority, status, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event_data.get('id'), event_data.get('title'), event_data.get('description'),
            event_data.get('start_time'), event_data.get('end_time'),
            event_data.get('event_type'), event_data.get('priority'),
            event_data.get('status'), json.dumps(event_data.get('tags', []))
        ))
        conn.commit()
        conn.close()

    def get_events(self, date_str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Упрощенный поиск по дате
        c.execute('SELECT * FROM events WHERE start_time LIKE ?', (f"{date_str}%",))
        rows = c.fetchall()
        conn.close()
        return rows

if __name__ == "__main__":
    cm = CalendarManager()
    print("Менеджер календаря готов.")