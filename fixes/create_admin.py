from utils.security import hash_password
from database.db import get_connection


def create_admin():

    conn = get_connection()
    cursor = conn.cursor()

    username = "admin"
    password = "1234"

    hashed = hash_password(password)

    cursor.execute("""
    INSERT INTO users (full_name, national_id, username, password_hash, role)
    VALUES (?, ?, ?, ?, ?)
    """, ("Admin", "0000000000", username, hashed, "manager"))

    conn.commit()
    conn.close()

    print("Admin created")


if __name__ == "__main__":
    create_admin()
