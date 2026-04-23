import sqlite3
import json
import datetime
from pathlib import Path

class SelfLearningPipeline:
    def __init__(self, db_path="data/self_learning.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                input_text TEXT,
                output_text TEXT,
                model_used TEXT,
                quality_score REAL DEFAULT 0.0,
                user_feedback TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def record(self, input_text, output_text, model_used="unknown"):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        ts = datetime.datetime.now().isoformat()
        c.execute('''
            INSERT INTO interactions (timestamp, input_text, output_text, model_used)
            VALUES (?, ?, ?, ?)
        ''', (ts, input_text, output_text, model_used))
        conn.commit()
        last_id = c.lastrowid
        conn.close()
        return last_id

    def feedback(self, interaction_id, score, correction=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        fb_json = json.dumps({"correction": correction}) if correction else "{}"
        c.execute('''
            UPDATE interactions SET quality_score=?, user_feedback=? WHERE id=?
        ''', (score, fb_json, interaction_id))
        conn.commit()
        conn.close()
        print(f"✅ Фидбек сохранен для записи #{interaction_id}")

    def prepare_dataset(self, min_score=0.7, output_path="data/dataset.jsonl"):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT input_text, output_text FROM interactions 
            WHERE quality_score >= ? AND user_feedback IS NOT NULL
        ''', (min_score,))
        
        rows = c.fetchall()
        conn.close()

        with open(output_path, 'w', encoding='utf-8') as f:
            for inp, out in rows:
                record = {"prompt": inp, "completion": out}
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        
        print(f"✅ Датасет сохранен: {output_path} ({len(rows)} записей)")
        return output_path

if __name__ == "__main__":
    # Тест
    sl = SelfLearningPipeline()
    print("Модуль самообучения готов.")