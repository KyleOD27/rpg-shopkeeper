import sqlite3

# Connect to DB (creates it if it doesn't exist)
with sqlite3.connect('rpg-shopkeeper.db') as conn:
    with open('database/schema.sql', 'r') as f:
        sql_script = f.read()
    conn.executescript(sql_script)

print("Database created successfully!")

with sqlite3.connect('rpg-shopkeeper.db') as conn:
    with open('database/seed_data.sql', 'r') as f:
        sql_script = f.read()
    conn.executescript(sql_script)

print("Database seeded with test data!")
