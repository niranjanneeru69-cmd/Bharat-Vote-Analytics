import sqlite3
import pandas as pd

conn = sqlite3.connect('election.db')
cursor = conn.cursor()

# Get list of tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# Inspect fact_election_results schema
print("\nSchema of fact_election_results:")
cursor.execute("PRAGMA table_info(fact_election_results);")
print(cursor.fetchall())

# Sample data
print("\nSample data from fact_election_results:")
df = pd.read_sql("SELECT * FROM fact_election_results LIMIT 5", conn)
print(df.to_string())

conn.close()
