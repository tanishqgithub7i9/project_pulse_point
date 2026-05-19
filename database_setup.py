import sqlite3 # This is built into Python, no pip install needed!

# 1. Connect to a database file (It will create it if it doesn't exist)
connection = sqlite3.connect('pulse_point.db')

# 2. Create a "Cursor" (This is like a pen to write in the database)
cursor = connection.cursor()

# 3. Create the table using SQL commands
cursor.execute('''
    CREATE TABLE IF NOT EXISTS bitcoin_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        price REAL
    )
''')

# 4. Save and Close
connection.commit()
connection.close()

print("Database and Table created successfully!")