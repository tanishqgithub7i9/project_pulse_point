import sqlite3

conn = sqlite3.connect('pulse_point.db')
cursor = conn.cursor()

try:
    # Adding a new column for sentiment scores (REAL means a decimal number)
    cursor.execute("ALTER TABLE bitcoin_prices ADD COLUMN sentiment REAL")
    conn.commit()
    print("Database upgraded! Added 'sentiment' column.")
except sqlite3.OperationalError:
    print("Column already exists or database error.")

conn.close()