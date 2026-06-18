import sqlite3

def create_table():
    # مسیر مستقیم و دقیق دیتابیس شما
    db_path = r"C:\E\archive_system\database\archive.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # کوئری ساخت جدول فرم‌های ثبت شده
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registered_forms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                file_path TEXT NOT NULL,
                creator_id INTEGER NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ جدول 'registered_forms' با موفقیت در دیتابیس ساخته شد.")
        
    except Exception as e:
        print(f"❌ خطا در ساخت جدول: {e}")

if __name__ == '__main__':
    create_table()
