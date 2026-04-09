import pandas as pd
import pyodbc
import json
import os

dir = r"C:\Users\jgeis\DOH\doh_plotly\data"

# Load the credentials from the JSON file
try:
    with open(os.path.join(dir, "credentials.json"), 'r') as file:
        creds = json.load(file)
        
    server = creds['server']
    database = creds['database']
    username = creds['username']
    password = creds['password']
except FileNotFoundError:
    print("Error: 'credentials.json' file not found.")
    exit()
except KeyError as e:
    print(f"Error: Missing key {e} in 'credentials.json'.")
    exit()

# Set up the connection string
# Included 'Encrypt=yes' and 'TrustServerCertificate=no' 
# which are often required for Azure/Enterprise connections.
conn_str = (
    f'Driver={{ODBC Driver 17 for SQL Server}};'
    f'Server={server};'
    f'Database={database};'
    f'Uid={username};'
    f'Pwd={password};'
    'Encrypt=yes;'
    'TrustServerCertificate=no;'
    'Connection Timeout=30;'
)

# List all the tables you want to export here
table_names = [
    #"discharge_data_view_diag_su",
    #"discharge_data_view_demographics",
    #"sudors_data_view_demographics$",
    #"wonder_age_group",
    #"wonder_gender",
    #"wonder_overview",
    #"wonder_race",
    #"wonder_substance",
    "discharge_data_view_demographics_test",
]

try:
    # Open the database connection once
    conn = pyodbc.connect(conn_str)
    
    # Loop through each table in the list
    for table_name in table_names:
        print(f"Processing: {table_name}...")
        
        # Wrapped the table name in brackets to handle special characters like '$'
        query = f"SELECT * FROM dbo.[{table_name}]"
        
        # Read the data into a Pandas DataFrame
        df = pd.read_sql(query, conn)

        # Generate the dynamic output path
        output_path = os.path.join(dir, f'{table_name}.csv')

        # Export to CSV. 
        # Using utf-8-sig ensures Excel opens the file correctly 
        # and handles the diagnosis column encoding issues.
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f" -> Successfully exported to {output_path}")
        
    print("\nAll exports completed successfully!")

except Exception as e:
    print(f"Error: {e}")

finally:
    # Safely close the database connection when done
    if 'conn' in locals():
        conn.close()
        print("Database connection closed.")