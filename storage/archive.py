import os
import sqlite3
from pathlib import Path

# مسیر دیتابیس
DB_PATH = Path(__file__).resolve().parent.parent / 'database' / 'archive.db'

class ArchiveService:
    def __init__(self):
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()
        
    def save_document(self, document_id, document_path, user_id):
        """ذخیره‌سازی سند."""
        try:
            self.cursor.execute("""
                INSERT INTO documents (id, path, user_id)
                VALUES (?, ?, ?)
            """, (document_id, document_path, user_id))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error saving document: {e}")
            return False

    def retrieve_document(self, document_id):
        """بازگرداندن سند بر اساس ID."""
        self.cursor.execute("SELECT path FROM documents WHERE id = ?", (document_id,))
        return self.cursor.fetchone()

    def close(self):
        """بستن اتصال به دیتابیس."""
        self.cursor.close()
        self.connection.close()
