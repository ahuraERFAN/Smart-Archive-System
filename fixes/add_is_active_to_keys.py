# add_is_active_to_keys.py
from database.db import get_connection

def add_column():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("ALTER TABLE archive_keys ADD COLUMN is_active INTEGER DEFAULT 1;")
        conn.commit()
        print("ستون is_active با موفقیت به جدول archive_keys اضافه شد.")
    except Exception as e:
        print(f"خطا (شاید ستون از قبل وجود دارد): {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_column()
