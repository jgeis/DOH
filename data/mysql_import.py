import os
import json
import pandas as pd
from sqlalchemy import create_engine, inspect

# ---------------------------------------------------------
# 1. Configuration: Set your database and file details here
# ---------------------------------------------------------    
dir = os.path.dirname(os.path.abspath(__file__))

# Build the exact paths to the files by combining the script's directory and the filenames
#CSV_FILENAME = 'dose_data.csv'
#CSV_FILENAME = 'discharge_data_view_demographics.csv'
#CSV_FILENAME = 'discharge_data_view_diag_mh.csv'
#CSV_FILENAME = 'discharge_data_view_diag_su.csv'
#CSV_FILENAME = 'discharge_data_view_diagnosis.csv'
#CSV_FILENAME = 'discharge_data_view.csv'
#CSV_FILENAME = 'sudors_data_view_demographics$.csv'
CSV_FILENAME = 'sudors_data_view_diag_su$.csv'
#CSV_FILENAME = 'cares_calls_clean_text_chat.csv'
#CSV_FILENAME = 'cares_calls_volume_view_test.csv'
#CSV_FILENAME = 'AMHD_Crisis_Mobile_Outreach.csv'
#CSV_FILENAME = 'adad_service_view.csv'
#CSV_FILENAME = 'AMHD_dates_of_service.csv'
#CSV_FILENAME = 'AMHD_Crisis_Stabilization_Bed.csv'
#CSV_FILENAME = 'AMHD_Licensed_Crisis_Residential_Services.csv'
#CSV_FILENAME = 'AMHD_service_category_CO_patid.csv'
#CSV_FILENAME = 'amhd_mh_services_view.csv'
#CSV_FILENAME = 'amhd_aggregate_month_reporting.csv'
#CSV_FILENAME = 'amhd_aggregate_year_reporting.csv'
#CSV_FILENAME = 'amhd_aggregate_day_reporting.csv'
#CSV_FILENAME = 'amhd_dashboard_fact.csv'
#CSV_FILENAME = 'camhd_co_mh_su_view.csv'
#CSV_FILENAME = 'camhd_service_view_test.csv'
#CSV_FILENAME = 'amhd_aggregate_view.csv'
#CSV_FILENAME = 'amhd_aggregate_reporting.csv'
#CSV_FILENAME = 'adad_service_view_test.csv'


CSV_FILE = os.path.join(dir, CSV_FILENAME)
CREDENTIALS_FILE = os.path.join(dir, 'credentials.json')

def import_csv_to_mysql():
    try:
        # ---------------------------------------------------------
        # 2. Load Database Credentials & Generate Table Name
        # ---------------------------------------------------------
        print("Loading credentials...")
        with open(CREDENTIALS_FILE, 'r') as file:
            creds = json.load(file)

        db_user = creds['mysql_username']
        db_pass = creds['mysql_password']
        db_name = creds['mysql_database']
        db_host = creds.get('db_host', 'localhost') # Defaults to localhost if not specified in JSON


        base_name = os.path.basename(CSV_FILE)
        table_name = os.path.splitext(base_name)[0]

        # ---------------------------------------------------------
        # 3. Connect to MySQL First
        # ---------------------------------------------------------
        print("Connecting to the database...")
        connection_string = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}"
        engine = create_engine(connection_string)

        # ---------------------------------------------------------
        # 4. Check if the Table Already Exists
        # ---------------------------------------------------------
        print(f"Checking for existing table named '{table_name}'...")
        inspector = inspect(engine)
        
        if inspector.has_table(table_name):
            print(f"\n⚠️ WARNING: The table '{table_name}' already exists in the database.")
            print("Exiting script without loading data to prevent duplication.")
            return # This stops the function entirely

        # ---------------------------------------------------------
        # 5. Read and Analyze the CSV (Only happens if table doesn't exist)
        # ---------------------------------------------------------
        print(f"Table not found. Reading and analyzing {CSV_FILE}...")
        
        df = pd.read_csv(CSV_FILE)
        
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(0)
            else:
                df[col] = df[col].fillna("")

        print(f"Successfully analyzed {len(df.columns)} columns and {len(df)} rows.")

        # ---------------------------------------------------------
        # 6. Create Table and Import Data
        # ---------------------------------------------------------
        print(f"Creating table '{table_name}' and inserting data...")
        
        # Changed if_exists to 'fail' just as an extra layer of safety, 
        # though our manual check above should catch it first.
        df.to_sql(name=table_name, con=engine, if_exists='fail', index=False, chunksize=1000)

        print("Success! All data has been imported.")

    except FileNotFoundError as fnf_error:
        print(f"File Error: Could not find '{fnf_error.filename}'. Please ensure it is in the same folder as this script.")
    except KeyError as key_error:
        print(f"JSON Error: Your credentials file is missing the required key: {key_error}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    import_csv_to_mysql()