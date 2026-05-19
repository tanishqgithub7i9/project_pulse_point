import sqlite3

conn = sqlite3.connect('pulse_point.db')
cursor = conn.cursor()

# SQL command to fetch all rows
cursor.execute("SELECT * FROM bitcoin_prices")
rows = cursor.fetchall()

print("--- Data inside pulse_point.db ---")
for row in rows:
    print(row)

conn.close()