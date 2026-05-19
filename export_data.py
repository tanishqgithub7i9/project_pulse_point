import sqlite3
import pandas as pd

# 1. Connect to your database
conn = sqlite3.connect('pulse_point.db')

# 2. Read the data into a table (DataFrame)
df = pd.read_sql_query("SELECT * FROM bitcoin_prices", conn)

# 3. Save it as a CSV file
df.to_csv('crypto_data_export.csv', index=False)

conn.close()
print("Success! 'crypto_data_export.csv' created. Open this in Power BI!")