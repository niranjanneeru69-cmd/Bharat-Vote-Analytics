import sqlite3
import pandas as pd

conn = sqlite3.connect('election.db')
cursor = conn.cursor()

# Inspect dim_turnout schema
print("Schema of dim_turnout:")
cursor.execute("PRAGMA table_info(dim_turnout);")
print(cursor.fetchall())

# Sample data from dim_turnout
print("\nSample data from dim_turnout:")
df = pd.read_sql("SELECT * FROM dim_turnout LIMIT 10", conn)
print(df.to_string())

conn.close()
