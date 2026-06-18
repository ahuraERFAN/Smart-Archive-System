# for testing database records
import sqlite3

conn = sqlite3.connect("database/archive.db")
c = conn.cursor()

c.execute("PRAGMA table_info(users)")
columns = c.fetchall()

for col in columns:
    print(col)

conn.close()
