"""
CSV to MySQL Batch Importer
===========================

A utility script designed to automate the ingestion of multiple CSV datasets 
into a MySQL database. It reads the raw data using Pandas, sanitizes missing 
values (NaN/Null) based on column data types, and safely uploads the data 
to the database using SQLAlchemy.

Key Features:
-------------
* Batch Processing: Iterates through a configurable list of CSV files.
* Data Sanitization: Automatically replaces missing numeric values with 0, 
  and missing string values with empty strings ("").
* Safety Toggle: Includes a global `OVERWRITE_TABLE` flag to prevent 
  accidental data loss when encountering existing tables.
* Fault Tolerance: Gracefully catches file and database errors on individual 
  files without crashing the entire batch queue.

Prerequisites:
--------------
The following third-party libraries must be installed in your environment:
    pip install pandas sqlalchemy pymysql

Configuration:
--------------
Before running, ensure the following global variables are set:
    1. CSV_FILENAMES: A list of the exact CSV filenames to import.
    2. OVERWRITE_TABLE: Set to True to replace existing tables, False to skip.
    3. CREDENTIALS_FILE: A JSON file containing your database connection details.

Expected format for credentials.json:
    {
        "mysql_username": "your_username",
        "mysql_password": "your_password",
        "mysql_database": "your_database_name",
        "db_host": "localhost" 
    }
"""
import os
import json
import pandas as pd
from sqlalchemy import create_engine, inspect

# ---------------------------------------------------------
# 1. Configuration: Set your database and file details here
# ---------------------------------------------------------    
dir = os.path.dirname(os.path.abspath(__file__))

# Set to True to overwrite existing tables, False to skip them
OVERWRITE_TABLE = True

# files to import into the db
CSV_FILENAMES = [
    #'dose_data.csv',
    #'discharge_data_view_demographics.csv',
    #'discharge_data_view_demographics_test.csv',
    #'discharge_data_view_diag_mh.csv',
    #'discharge_data_view_diag_su.csv',
    #'discharge_data_view_diagnosis.csv',
    #'discharge_data_view.csv',
    #'sudors_data_view_demographics$.csv',
    #'sudors_data_view_diag_su$.csv',
    #'cares_calls_clean_text_chat.csv',
    #'cares_calls_volume_view_test.csv',
    #'AMHD_Crisis_Mobile_Outreach.csv',
    #'adad_service_view.csv',
    #'AMHD_dates_of_service.csv',
    #'AMHD_Crisis_Stabilization_Bed.csv',
    #'AMHD_Licensed_Crisis_Residential_Services.csv',
    #'AMHD_service_category_CO_patid.csv',
    #'amhd_mh_services_view.csv',
    #'amhd_aggregate_month_reporting.csv',
    #'amhd_aggregate_year_reporting.csv',
    #'amhd_aggregate_day_reporting.csv',
    #'amhd_dashboard_fact.csv',
    #'camhd_co_mh_su_view.csv',
    #'camhd_service_view_test.csv',
    #'amhd_aggregate_view.csv',
    #'amhd_aggregate_reporting.csv',
    #'adad_service_view_test.csv',
    #'wonder_age_group.csv',
    #'wonder_gender.csv',
    #'wonder_overview.csv',
    #'wonder_race.csv',
    #'wonder_substance.csv',
    'BH808_Crisis_Bed_Occupancy_LCRS.csv',
    'BH808_Crisis_Bed_Occupancy_SICM.csv',
    'BH808_Overview_Call_Nature.csv',
    'BH808_Overview_CMO_Dispatches.csv',
    'BH808_Overview_Crisis_Volume.csv',
    'BH808_Overview_Top_Box.csv',
    'BH808_CMO_Referral_Destinations.csv'
]
CREDENTIALS_FILE = os.path.join(dir, 'credentials.json')

def import_csvs_to_mysql(filenames):
    try:
        # ---------------------------------------------------------
        # 2. Load Database Credentials & Connect to MySQL FIRST
        # ---------------------------------------------------------
        print("Loading credentials and connecting to the database...")
        with open(CREDENTIALS_FILE, 'r') as file:
            creds = json.load(file)

        db_user = creds['mysql_username']
        db_pass = creds['mysql_password']
        db_name = creds['mysql_database']
        db_host = creds.get('db_host', 'localhost') 

        connection_string = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}"
        engine = create_engine(connection_string)
        inspector = inspect(engine)

        # ---------------------------------------------------------
        # 3. Loop through each file in the provided list
        # ---------------------------------------------------------
        for filename in filenames:
            print(f"\n{'-'*50}\nProcessing: {filename}\n{'-'*50}")
            
            csv_path = os.path.join(dir, filename)
            base_name = os.path.basename(csv_path)
            table_name = os.path.splitext(base_name)[0]

            try:
                # ---------------------------------------------------------
                # 4. Check if the Table Already Exists
                # ---------------------------------------------------------
                print(f"Checking for existing table named '{table_name}'...")
                
                if inspector.has_table(table_name):
                    if not OVERWRITE_TABLE:
                        print(f"⚠️ WARNING: The table '{table_name}' already exists.")
                        print("Skipping to the next file (OVERWRITE_TABLE = False).")
                        continue # Skips to the next file
                    else:
                        print(f"⚠️ WARNING: The table '{table_name}' already exists.")
                        print("Preparing to overwrite it (OVERWRITE_TABLE = True).")

                # ---------------------------------------------------------
                # 5. Read and Analyze the CSV
                # ---------------------------------------------------------
                print(f"Reading and analyzing {filename}...")
                
                df = pd.read_csv(csv_path)
                
                for col in df.columns:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        df[col] = df[col].fillna(0)
                    else:
                        df[col] = df[col].fillna("")

                print(f"Successfully analyzed {len(df.columns)} columns and {len(df)} rows.")

                # ---------------------------------------------------------
                # 6. Create Table and Import Data
                # ---------------------------------------------------------
                print(f"Inserting data into '{table_name}'...")
                
                # Determine the behavior based on the global flag
                exist_behavior = 'replace' if OVERWRITE_TABLE else 'fail'
                
                df.to_sql(name=table_name, con=engine, if_exists=exist_behavior, index=False, chunksize=1000)

                print(f"✅ Success! '{filename}' has been imported.")

            except FileNotFoundError:
                print(f"❌ File Error: Could not find '{filename}'. Skipping to next file.")
            except Exception as e:
                print(f"❌ An error occurred while processing '{filename}': {e}. Skipping to next file.")

        print("\n🎉 All files have been processed!")

    except FileNotFoundError as fnf_error:
        print(f"Critical Error: Could not find credentials file '{fnf_error.filename}'. Script stopped.")
    except KeyError as key_error:
        print(f"JSON Error: Your credentials file is missing the required key: {key_error}. Script stopped.")
    except Exception as e:
        print(f"A critical database connection error occurred: {e}. Script stopped.")

if __name__ == "__main__":
    import_csvs_to_mysql(CSV_FILENAMES)