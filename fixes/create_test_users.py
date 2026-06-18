from utils.security import hash_password
from database.db import get_connection

def create_test_users():
    conn = get_connection()
    cursor = conn.cursor()

    users_to_create = [
        ("کارمند تست", "1111111111", "staff_test", "1234", "staff"),
        ("کاربر تست", "2222222222", "user_test", "1234", "user")
    ]

    for full_name, national_id, username, password, role in users_to_create:
        # بررسی اینکه آیا کاربر از قبل وجود دارد
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            print(f"[-] کاربر {username} از قبل وجود دارد.")
            continue
            
        hashed = hash_password(password)
        cursor.execute("""
        INSERT INTO users (full_name, national_id, username, password_hash, role)
        VALUES (?, ?, ?, ?, ?)
        """, (full_name, national_id, username, hashed, role))
        print(f"[+] کاربر {username} با نقش {role} ساخته شد.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_test_users()
