import sqlite3

conn = sqlite3.connect("archive.db")
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS api_keys")

cur.execute("""
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    key TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT
)
""")

conn.commit()
conn.close()

print("api_keys table recreated")
