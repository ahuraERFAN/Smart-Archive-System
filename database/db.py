import sqlite3
from pathlib import Path
import os

# مسیر اصلی پروژه
BASE_DIR = Path(os.path.abspath(os.path.dirname(__file__))).parent
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "archive.db"


def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # USERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        national_id TEXT UNIQUE,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # DOCUMENTS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,

        title TEXT,
        description TEXT,

        file_path TEXT,
        scan_path TEXT,

        ocr_text TEXT,
        extracted_json TEXT,

        signature_path TEXT,

        status TEXT DEFAULT 'pending',

        reviewed_by INTEGER,
        reviewed_by_role TEXT,
        reviewed_at TIMESTAMP,

        reject_reason TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (reviewed_by) REFERENCES users(id)
    )
    """)

    # TICKETS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        staff_id INTEGER,

        message TEXT NOT NULL,
        response TEXT,

        status TEXT DEFAULT 'open',

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (document_id) REFERENCES documents(id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (staff_id) REFERENCES users(id)
    )
    """)

    # ARCHIVE KEYS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS archive_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key_code TEXT UNIQUE,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    # Api KEYS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS api_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_name TEXT NOT NULL,
        api_key TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
