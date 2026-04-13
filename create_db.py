import pandas as pd
import sqlite3

# Database name
DB_NAME = "DOH_AMHD_NO_PII.db"

# Load CSVs
print("Loading CSV files...")
df_diag_su = pd.read_csv("data/discharge_data_view_diag_su.csv")
df_diag_mh = pd.read_csv("data/discharge_data_view_diag_mh.csv")
df_demo = pd.read_csv("data/discharge_data_view_demographics.csv")
df_dose = pd.read_csv("data/dose_data.csv")
df_sudors_demo = pd.read_csv("data/sudors_data_view_demographics$.csv", on_bad_lines='skip')
df_sudors_diag_su = pd.read_csv("data/sudors_data_view_diag_su$.csv")
df_wonder_overview = pd.read_csv("data/wonder_overview.csv")
df_wonder_substance = pd.read_csv("data/wonder_substance.csv")
df_wonder_race = pd.read_csv("data/wonder_race.csv")
df_wonder_age_group = pd.read_csv("data/wonder_age_group.csv")
df_wonder_gender = pd.read_csv("data/wonder_gender.csv")

df_sudors_demo = df_sudors_demo.dropna()

# Clean column names (lowercase and strip whitespace)
df_diag_su.columns = df_diag_su.columns.str.lower().str.strip()
df_diag_mh.columns = df_diag_mh.columns.str.lower().str.strip()
df_demo.columns = df_demo.columns.str.lower().str.strip()
df_dose.columns = df_dose.columns.str.lower().str.strip()
df_sudors_demo.columns = df_sudors_demo.columns.str.lower().str.strip()
df_sudors_diag_su.columns = df_sudors_diag_su.columns.str.lower().str.strip()
df_wonder_overview.columns = df_wonder_overview.columns.str.lower().str.strip()
df_wonder_substance.columns = df_wonder_substance.columns.str.lower().str.strip()
df_wonder_race.columns = df_wonder_race.columns.str.lower().str.strip()
df_wonder_age_group.columns = df_wonder_age_group.columns.str.lower().str.strip()
df_wonder_gender.columns = df_wonder_gender.columns.str.lower().str.strip()

print(f"Loaded {len(df_diag_su):,} diag_su records, {len(df_diag_mh):,} diag_mh records, {len(df_demo):,} demographics records, {len(df_dose)} overdose poisoning records, {len(df_sudors_demo):,} sudors demographics records, and {len(df_sudors_diag_su):,} sudors diag_su records.")
print(f"diag_su columns: {df_diag_su.columns.tolist()}")
print(f"diag_mh columns: {df_diag_mh.columns.tolist()}")
print(f"demographics columns: {df_demo.columns.tolist()}")
print(f"overdose poisonings columns: {df_dose.columns.tolist()}")
print(f"sudors demographics columns: {df_sudors_demo.columns.tolist()}")
print(f"sudors diag_su columns: {df_sudors_diag_su.columns.tolist()}")
print(f"wonder_overview columns: {df_wonder_overview.columns.tolist()}")
print(f"wonder_substance columns: {df_wonder_substance.columns.tolist()}")
print(f"wonder_race columns: {df_wonder_race.columns.tolist()}")
print(f"wonder_age_group columns: {df_wonder_age_group.columns.tolist()}")
print(f"wonder_gender columns: {df_wonder_gender.columns.tolist()}")

# Connect to SQLite (local development database)
print(f"\nConnecting to SQLite database ({DB_NAME})...")
conn = sqlite3.connect(DB_NAME)

try:
    # Save as tables - table names match CSV filenames (without .csv extension)
    print("Creating 'discharge_data_view_diag_su' table...")
    df_diag_su.to_sql("discharge_data_view_diag_su", conn, if_exists="replace", index=False)
    
    print("Creating 'discharge_data_view_diag_mh' table...")
    df_diag_mh.to_sql("discharge_data_view_diag_mh", conn, if_exists="replace", index=False)

    print("Creating 'discharge_data_view_demographics' table...")
    df_demo.to_sql("discharge_data_view_demographics", conn, if_exists="replace", index=False)
    
    print("Creating 'dose_data' table...")
    df_dose.to_sql("dose_data", conn, if_exists="replace", index=False)

    print("Creating 'sudors_data_view_demographics$' table...")
    df_sudors_demo.to_sql("sudors_data_view_demographics$", conn, if_exists="replace", index=False)

    print("Creating 'sudors_data_view_diag_su$' table...")
    df_sudors_diag_su.to_sql("sudors_data_view_diag_su$", conn, if_exists="replace", index=False)

    print("Creating 'wonder_overview' table...")
    df_wonder_overview.to_sql("wonder_overview", conn, if_exists="replace", index=False)

    print("Creating 'wonder_substance' table...")
    df_wonder_substance.to_sql("wonder_substance", conn, if_exists="replace", index=False)

    print("Creating 'wonder_race' table...")
    df_wonder_race.to_sql("wonder_race", conn, if_exists="replace", index=False)

    print("Creating 'wonder_age_group' table...")
    df_wonder_age_group.to_sql("wonder_age_group", conn, if_exists="replace", index=False)

    print("Creating 'wonder_gender' table...")
    df_wonder_gender.to_sql("wonder_gender", conn, if_exists="replace", index=False)


    print(f"\n✅ Database tables created successfully in {DB_NAME}")
    print(f"  - discharge_data_view_diag_su: {len(df_diag_su):,} rows")
    print(f"  - discharge_data_view_diag_mh: {len(df_diag_mh):,} rows")
    print(f"  - discharge_data_view_demographics: {len(df_demo):,} rows")
    print(f"  - dose_data: {len(df_dose):,} rows")
    print(f"  - sudors_data_view_demographics$: {len(df_sudors_demo):,} rows")
    print(f"  - sudors_data_view_diag_su$: {len(df_sudors_diag_su):,} rows")
    print(f"  - wonder_overview: {len(df_wonder_overview):,} rows")
    print(f"  - wonder_substance: {len(df_wonder_substance):,} rows")
    print(f"  - wonder_race: {len(df_wonder_race):,} rows")
    print(f"  - wonder_age_group: {len(df_wonder_age_group):,} rows")
    print(f"  - wonder_gender: {len(df_wonder_gender):,} rows")

finally:
    conn.close()

# Verify table structure
print("\nVerifying table structure...")
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

for table in ['discharge_data_view_diag_su', 'discharge_data_view_diag_mh', 'discharge_data_view_demographics', 'dose_data', 'sudors_data_view_demographics$', 'sudors_data_view_diag_su$', 'wonder_overview', 'wonder_substance', 'wonder_race', 'wonder_age_group', 'wonder_gender']:
    cursor.execute(f"PRAGMA table_info({table})")
    print(f"\n{table} columns:")
    for row in cursor.fetchall():
        print(f"  - {row[1]}")

conn.close()

# python -c "import sqlite3; conn = sqlite3.connect('DOH_AMHD_NO_PII.db'); cursor = conn.cursor(); cursor.execute('PRAGMA table_info(discharge_data_view_demographics)'); print('discharge_data_view_demographics columns:'); [print(f\"  {row[1]}\") for row in cursor.fetchall()]; conn.close()"