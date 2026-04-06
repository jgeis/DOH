import pandas as pd
import pyodbc
import json

# Load the credentials from the JSON file
try:
    with open('credentials.json', 'r') as file:
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

# Note: We added 'Encrypt=yes' and 'TrustServerCertificate=no' 
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

try:
    conn = pyodbc.connect(conn_str)
    #table_name = "discharge_data_view_diag_su"
    #table_name = "discharge_data_view_demographics"
    #table_name = "sudors_data_view_demographics$"
    table_name = "wonder_age_group"
    query = "SELECT * FROM dbo." +  table_name
    print(query)
    df = pd.read_sql(query, conn)

    # Using utf-8-sig ensures Excel opens the file correctly 
    # and handles the diagnosis column encoding issues.
    output_path = rf'C:\Users\jgeis\DOH\doh_plotly\{table_name}.csv'
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print("Export Successful!")

except Exception as e:
    print(f"Error: {e}")