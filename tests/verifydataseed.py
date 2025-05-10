import sqlite3
conn = sqlite3.connect('../grizzlebeard.db')
cur = conn.cursor()
cur.execute('SELECT * FROM items')
print(cur.fetchall())
cur.execute('SELECT * FROM parties')
print(cur.fetchall())
