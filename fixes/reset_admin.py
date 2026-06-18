import sqlite3
from utils.security import hash_password

conn = sqlite3.connect("database/archive.db")
c = conn.cursor()

new_hash = hash_password("1234")

c.execute("""
UPDATE users
SET password_hash = ?
WHERE username = 'admin'
""", (new_hash,))

conn.commit()
conn.close()

print("Admin password reset successfully.")
