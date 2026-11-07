import sqlite3

conn = sqlite3.connect('links.db')
c = conn.cursor()

# Tabel link pendek
c.execute('''
CREATE TABLE IF NOT EXISTS links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shortcode TEXT UNIQUE,
    target_url TEXT,
    source TEXT
)
''')

# Tabel tracking klik
c.execute('''
CREATE TABLE IF NOT EXISTS clicks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shortcode TEXT,
    ip TEXT,
    user_agent TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    location TEXT
)
''')

conn.commit()
conn.close()
print("✅ Database initialized.")
