import sqlite3

conn = sqlite3.connect("archive.db")
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")
    print("is_active column added")
except:
    print("column already exists")

conn.commit()
conn.close()
