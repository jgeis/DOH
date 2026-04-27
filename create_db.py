import pandas as pd
import sqlite3
from pathlib import Path
from pandas.errors import ParserError

# Database name
DB_NAME = "DOH_AMHD_NO_PII.db"
DATA_DIR = Path("data")


def read_csv_safely(csv_path: Path) -> pd.DataFrame:
    """
    Read a CSV file with a fallback for malformed rows.

    Most files load normally. A few legacy exports may contain a bad line,
    so we retry with `on_bad_lines='skip'` when needed.
    """
    try:
        return pd.read_csv(csv_path)
    except ParserError:
        print(f"Warning: parser issue in '{csv_path.name}', retrying with bad-line skipping.")
        return pd.read_csv(csv_path, on_bad_lines="skip")

# Load all CSVs from the data directory
print("Loading CSV files...")
csv_files = sorted(DATA_DIR.glob("*.csv"))
if not csv_files:
    raise FileNotFoundError(f"No CSV files found in {DATA_DIR.resolve()}")

tables: dict[str, pd.DataFrame] = {}
for csv_file in csv_files:
    table_name = csv_file.stem
    df = read_csv_safely(csv_file)
    df.columns = df.columns.str.lower().str.strip()
    tables[table_name] = df
    print(f"Loaded {len(df):,} rows from {csv_file.name} -> table '{table_name}'")
    print(f"{table_name} columns: {df.columns.tolist()}")

# Connect to SQLite (local development database)
print(f"\nConnecting to SQLite database ({DB_NAME})...")
conn = sqlite3.connect(DB_NAME)

try:
    # Save as tables - names match CSV filenames without extension.
    for table_name, df in tables.items():
        print(f"Creating '{table_name}' table...")
        df.to_sql(table_name, conn, if_exists="replace", index=False)

    print(f"\n✅ Database tables created successfully in {DB_NAME}")
    for table_name, df in tables.items():
        print(f"  - {table_name}: {len(df):,} rows")

finally:
    conn.close()

# Verify table structure
print("\nVerifying table structure...")
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

for table in tables:
    cursor.execute(f"PRAGMA table_info({table})")
    print(f"\n{table} columns:")
    for row in cursor.fetchall():
        print(f"  - {row[1]}")

conn.close()

# python -c "import sqlite3; conn = sqlite3.connect('DOH_AMHD_NO_PII.db'); cursor = conn.cursor(); cursor.execute('PRAGMA table_info(discharge_data_view_demographics)'); print('discharge_data_view_demographics columns:'); [print(f\"  {row[1]}\") for row in cursor.fetchall()]; conn.close()"