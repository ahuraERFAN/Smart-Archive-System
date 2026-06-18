import sqlite3
import os

# تعیین مسیر دیتابیس (با توجه به ساختار پروژه شما که پوشه database دارد)
db_path = os.path.join("database", "archive.db") # اگر نام فایل دیتابیس چیز دیگری است، این خط را اصلاح کنید

def add_is_active_column():
    try:
        # اتصال به دیتابیس
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # اضافه کردن ستون is_active با مقدار پیش‌فرض 1 (یعنی کاربران فعلی به طور پیش‌فرض فعال باشند)
        cursor.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1;")
        conn.commit()
        
        print("ستون 'is_active' با موفقیت به جدول users اضافه شد.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ستون 'is_active' از قبل وجود دارد.")
        else:
            print(f"خطا در دیتابیس: {e}")
    except Exception as e:
        print(f"خطای نامشخص: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_is_active_column()
