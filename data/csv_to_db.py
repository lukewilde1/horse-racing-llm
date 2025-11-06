import sqlite3
import pandas as pd

db_name = 'nsw_racing.db'
data = pd.read_csv(r'data\final_combined_racing_data.csv', parse_dates=['Date'])

# Get data size
row_count_len = len(data)
print(f"Number of rows (using len()): {row_count_len}")

conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Drop table so its fresh
print("\n===== Dropping Table =====\n")
cursor.execute("DROP TABLE IF EXISTS races;")

with open(r'utils\db_schema.sql', 'r') as f:
    sql_schema = f.read()
cursor.executescript(sql_schema)
conn.commit()

# Insert to table
data.to_sql('races', conn, if_exists='append', index=False)

# Verify count of rows
cursor.execute("SELECT COUNT(*) AS count FROM races")
count = cursor.fetchone()[0]
print("Total rows in DB:", count)

# Close the connection
conn.close()