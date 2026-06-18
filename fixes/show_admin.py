import sqlite3

conn = sqlite3.connect("database/archive.db")
c = conn.cursor()

c.execute("SELECT id, username, password_hash, role FROM users")
rows = c.fetchall()

for r in rows:
    print(r)

conn.close()
