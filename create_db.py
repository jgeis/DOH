import pandas as pd
import sqlite3

# Load CSVs
df_diag = pd.read_csv("discharge_data_view_diag_su.csv")
df_demo = pd.read_csv("discharge_data_view_demographics.csv")

# Rename columns
df_diag.columns = ["record_id", "substance", "placeholder"]
df_demo.columns = ["record_id", "county", "region", "zip", "residency", "age_group", "sex", "calendar_year"]

# Create SQLite DB
conn = sqlite3.connect("discharges.db")

# Save as tables
df_diag.to_sql("diagnoses", conn, if_exists="replace", index=False)
df_demo.to_sql("demographics", conn, if_exists="replace", index=False)

conn.close()

print("Database created: discharges.db")
