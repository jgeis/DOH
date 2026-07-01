# db_utils.py
"""
Database utility functions supporting both SQLite and MSSQL connections.
Automatically selects the appropriate database based on configuration.
"""
import sqlite3
import pandas as pd
from config import USE_MSSQL, SQLITE_DB_PATH, get_mssql_connection_string, get_connection_info

# Only import pyodbc if we're using MSSQL
if USE_MSSQL:
    import pyodbc

def get_connection():
    """
    Get database connection (SQLite or MSSQL based on config).
    
    Returns:
        Connection object (sqlite3.Connection or pyodbc.Connection)
    """
    try:
        if USE_MSSQL:
            conn_str = get_mssql_connection_string()
            conn = pyodbc.connect(conn_str)
            print("[db_utils] Successfully connected to MSSQL database")
        else:
            # 1. Define the logic to extract parts from SQLite's YYYY-MM-DD string format
            def extract_year(date_string):
                return int(date_string[:4]) if date_string else None

            def extract_month(date_string):
                return int(date_string[5:7]) if date_string else None

            def extract_day(date_string):
                return int(date_string[8:10]) if date_string else None

            conn = sqlite3.connect(SQLITE_DB_PATH)
        
            # 3. Bind the functions to the connection
            conn.create_function("YEAR", 1, extract_year)
            conn.create_function("MONTH", 1, extract_month)
            conn.create_function("DAY", 1, extract_day)

            print(f"[db_utils] Successfully connected to SQLite database: {SQLITE_DB_PATH}")
        return conn
    except Exception as e:
        print(f"[db_utils] Error connecting to database: {e}")
        info = get_connection_info()
        print(f"[db_utils] Connection info: {info}")
        raise

def execute_query(query):
    """
    Execute a SQL query and return results as DataFrame.
    Works with both SQLite and MSSQL.
    
    Args:
        query (str): SQL query to execute
        
    Returns:
        pd.DataFrame: Query results as DataFrame
    """
    # Create a dictionary of 'wrong_value': 'correct_value'
    substance_corrections = {
        "Benzodiazepine": "Benzodiazepines",
    }
    county_corrections = {
        "Hawaii": "Hawaiʻi",
        "East_Hawaii": "East Hawaiʻi",
        "West_Hawaii": "West Hawaiʻi",
        "Windward_Oahu": "Windward Oʻahu",
        "Central_Oahu": "Central Oʻahu",
        "Kauai": "Kauaʻi",
        "Molokai": "Molokaʻi",
        "Lanai": "Lānaʻi",
        "Niihau": "Niʻihau",
        "Kahoolawe": "Kahoʻolawe",
    }
    try:
        with get_connection() as conn:
            print(f"[db_utils] Loading: {query}")
            df = pd.read_sql_query(query, conn)
            db_type = "MSSQL" if USE_MSSQL else "SQLite"
            print(f"[db_utils] Query returned {len(df):,} rows from {db_type}")
            # Apply the corrections to the dataframe
            if "substance" in df.columns:
                df["substance"] = df["substance"].replace(substance_corrections)
            if "county" in df.columns:
                df["county"] = df["county"].replace(county_corrections)
            if "facility" in df.columns:
                df["facility"] = df["facility"].replace(county_corrections)
            return df
    except Exception as e:
        print(f"[db_utils] Error executing query: {e}")
        print(f"[db_utils] Query: {query[:200]}...")  # Print first 200 chars
        raise


def test_connection():
    """Test database connection and print connection details."""
    try:
        info = get_connection_info()
        print(f"[db_utils] Testing {info['type']} connection...")
        
        with get_connection() as conn:
            cursor = conn.cursor()
            
            if USE_MSSQL:
                cursor.execute("SELECT @@VERSION")
                version = cursor.fetchone()[0]
                print(f"[db_utils] Connected successfully!")
                print(f"[db_utils] SQL Server version: {version[:100]}...")
            else:
                cursor.execute("SELECT sqlite_version()")
                version = cursor.fetchone()[0]
                print(f"[db_utils] Connected successfully!")
                print(f"[db_utils] SQLite version: {version}")
            
            return True
    except Exception as e:
        print(f"[db_utils] Connection test failed: {e}")
        return False
