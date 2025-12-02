import pandas as pd
from db_utils import get_connection

# Load CSVs
print("Loading CSV files...")
df_diag = pd.read_csv("discharge_data_view_diag_su.csv")
df_demo = pd.read_csv("discharge_data_view_demographics.csv")

# Rename columns
df_diag.columns = ["record_id", "substance", "placeholder"]
df_demo.columns = ["record_id", "county", "region", "zip", "residency", "age_group", "sex", "calendar_year"]

print(f"Loaded {len(df_diag):,} diagnosis records and {len(df_demo):,} demographic records")

# Connect to MSSQL
print("Connecting to MSSQL database...")
conn = get_connection()

try:
    # Save as tables (if_exists='replace' will drop and recreate tables)
    print("Creating 'diagnoses' table...")
    df_diag.to_sql("diagnoses", conn, if_exists="replace", index=False, schema="dbo")
    
    print("Creating 'demographics' table...")
    df_demo.to_sql("demographics", conn, if_exists="replace", index=False, schema="dbo")
    
    print("✅ Database tables created successfully in MSSQL")
    print(f"  - diagnoses: {len(df_diag):,} rows")
    print(f"  - demographics: {len(df_demo):,} rows")
finally:
    conn.close()
