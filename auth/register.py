from utils.security import hash_password
from database.db import get_connection

def register_user(full_name, national_id, username, password, role="user"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        conn.close()
        return False, "این نام کاربری قبلاً ثبت شده است."
        
    password_hash = hash_password(password)
    cursor.execute("""
        INSERT INTO users (full_name, national_id, username, password_hash, role)
        VALUES (?, ?, ?, ?, ?)
    """, (full_name, national_id, username, password_hash, role))
    conn.commit()
    conn.close()
    return True, "ثبت‌نام با موفقیت انجام شد."
