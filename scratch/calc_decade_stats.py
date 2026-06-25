import sqlite3
import pandas as pd
import json

conn = sqlite3.connect('election.db')

# Query to get average electors and votes by decade
# We join fact_election_results with dim_year to get the decade
query = """
    SELECT 
        y.decade, 
        AVG(f.electors) as avg_electors, 
        AVG(f.votes) as avg_votes
    FROM fact_election_results f
    JOIN dim_year y ON f.year_id = y.year_id
    GROUP BY y.decade
    ORDER BY y.decade
"""

df = pd.read_sql(query, conn)
conn.close()

# Convert to dictionary for easy frontend use
decade_averages = df.set_index('decade').to_dict('index')
# Round values
for decade in decade_averages:
    decade_averages[decade]['avg_electors'] = int(round(decade_averages[decade]['avg_electors']))
    decade_averages[decade]['avg_votes'] = int(round(decade_averages[decade]['avg_votes']))

print(json.dumps(decade_averages, indent=2))

# Save to a file that the web app can use
with open('decade_stats.json', 'w') as f:
    json.dump(decade_averages, f)
