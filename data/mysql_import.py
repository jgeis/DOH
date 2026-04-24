import os
import json
import pandas as pd
from sqlalchemy import create_engine

# ---------------------------------------------------------
# 1. Configuration: Set your database and file details here
# ---------------------------------------------------------    
#dir = "/Users/jgeis/Work/DOH/plotly/data/"
dir = os.path.dirname(os.path.abspath(__file__))
# Build the exact paths to the files by combining the script's directory and the filenames
#CSV_FILE = 'dose_data.csv'
#CSV_FILE = 'discharge_data_view_demographics.csv'
#CSV_FILE = 'discharge_data_view_diag_mh.csv'
#CSV_FILE = 'discharge_data_view_diag_su.csv'
#CSV_FILE = 'discharge_data_view_diagnosis.csv'
#CSV_FILENAME = 'discharge_data_view.csv'
CSV_FILENAME = 'sudors_data_view_demographics$.csv'

CSV_FILE = os.path.join(dir, CSV_FILENAME)
CREDENTIALS_FILE = os.path.join(dir, 'credentials.json')

def import_csv_to_mysql():
    try:
        # ---------------------------------------------------------
        # 2. Load Database Credentials
        # ---------------------------------------------------------
        print("Loading credentials...")
        with open(CREDENTIALS_FILE, 'r') as file:
            creds = json.load(file)
            
        db_user = creds['mysql_username']
        db_pass = creds['mysql_password']
        db_name = creds['mysql_database']
        db_host = creds.get('db_host', 'localhost') # Defaults to localhost if not specified in JSON

        # ---------------------------------------------------------
        # 2. Dynamically Generate the Table Name
        # ---------------------------------------------------------
        # os.path.basename gets the file name from the path (e.g., 'employee_data.csv')
        # os.path.splitext splits the name and extension, returning a tuple: ('employee_data', '.csv')
        # We grab the first item [0] from that tuple.
        base_name = os.path.basename(CSV_FILE)
        table_name = os.path.splitext(base_name)[0]
        
        print(f"File detected. Data will be imported into table: '{table_name}'")

        # ---------------------------------------------------------
        # 3. Read and Analyze the CSV
        # ---------------------------------------------------------
        print(f"Reading and analyzing {CSV_FILE}...")
        
        df = pd.read_csv(CSV_FILE)
        
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(0)
            else:
                df[col] = df[col].fillna("")

        print(f"Successfully analyzed {len(df.columns)} columns and {len(df)} rows.")

        # ---------------------------------------------------------
        # 4. Connect to MySQL
        # ---------------------------------------------------------
        print("Connecting to the database...")
        connection_string = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}"
        engine = create_engine(connection_string)

        # ---------------------------------------------------------
        # 5. Create Table and Import Data
        # ---------------------------------------------------------
        print(f"Creating table (if needed) and inserting data...")
        
        df.to_sql(name=table_name, con=engine, if_exists='append', index=False, chunksize=1000)

        print("Success! All data has been imported.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    import_csv_to_mysql()