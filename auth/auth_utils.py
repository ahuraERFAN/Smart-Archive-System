# auth/auth_utils.py

from utils.security import verify_password
from database.db import get_connection


def authenticate_user(username: str, password: str):
    """
    بررسی نام کاربری و رمز عبور
    در صورت موفقیت:
        (True, "ورود موفق", user_dict)
    در غیر این صورت:
        (False, "پیام خطا", None)
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, full_name, username, password_hash, role
        FROM users
        WHERE username = ?
    """, (username,))

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return False, "کاربری با این نام کاربری وجود ندارد", None

    user_id, full_name, db_username, db_password_hash, role = row

    # بررسی رمز عبور
    if not verify_password(password, db_password_hash):
        return False, "رمز عبور اشتباه است", None

    # اطلاعات کاربر لاگین‌شده
    user_data = {
        "id": user_id,
        "full_name": full_name,
        "username": db_username,
        "role": role
    }

    return True, "ورود موفق", user_data
