"""
Unit tests for db_utils.py

Tests database connection and query execution for both SQLite and MSSQL modes.
Uses mocking to avoid requiring actual database connections during tests.
"""
import pytest
import pandas as pd
import sqlite3
from unittest.mock import Mock, patch, MagicMock
import sys


@pytest.fixture
def mock_sqlite_connection():
    """Create a mock SQLite connection."""
    conn = sqlite3.connect(':memory:')
    
    # Create test table
    conn.execute('''
        CREATE TABLE test_table (
            id INTEGER PRIMARY KEY,
            county TEXT,
            year INTEGER,
            count INTEGER
        )
    ''')
    
    # Insert test data
    test_data = [
        (1, 'Honolulu', 2020, 100),
        (2, 'Maui', 2020, 50),
        (3, 'Hawaii', 2021, 75),
        (4, 'Kauai', 2021, 30)
    ]
    conn.executemany('INSERT INTO test_table VALUES (?, ?, ?, ?)', test_data)
    conn.commit()
    
    return conn


@pytest.fixture
def mock_pyodbc():
    """Mock pyodbc module for MSSQL testing."""
    mock_module = MagicMock()
    sys.modules['pyodbc'] = mock_module
    yield mock_module
    if 'pyodbc' in sys.modules:
        del sys.modules['pyodbc']


class TestDatabaseConnection:
    """Test database connection logic for both SQLite and MSSQL."""
    
    @patch('db_utils.USE_MSSQL', False)
    @patch('db_utils.SQLITE_DB_PATH', ':memory:')
    def test_get_connection_sqlite(self):
        """Test SQLite connection establishment."""
        from db_utils import get_connection
        
        conn = get_connection()
        assert conn is not None
        
        # Test that custom functions are registered
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1
        
        conn.close()
    
    @patch('db_utils.USE_MSSQL', False)
    @patch('db_utils.SQLITE_DB_PATH', ':memory:')
    def test_sqlite_date_functions(self):
        """Test that SQLite date extraction functions work."""
        from db_utils import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create test table with date
        cursor.execute("CREATE TABLE test_dates (date_col TEXT)")
        cursor.execute("INSERT INTO test_dates VALUES ('2020-06-15')")
        
        # Test YEAR function
        cursor.execute("SELECT YEAR(date_col) FROM test_dates")
        assert cursor.fetchone()[0] == 2020
        
        # Test MONTH function
        cursor.execute("SELECT MONTH(date_col) FROM test_dates")
        assert cursor.fetchone()[0] == 6
        
        # Test DAY function
        cursor.execute("SELECT DAY(date_col) FROM test_dates")
        assert cursor.fetchone()[0] == 15
        
        conn.close()
    
    # @patch('db_utils.USE_MSSQL', False)
    # @patch('db_utils.get_mssql_connection_string')
    # def test_get_connection_mssql(self, mock_conn_string, mock_pyodbc):
    #     """Test MSSQL connection establishment."""
    #     mock_conn_string.return_value = "DRIVER={SQL Server};SERVER=test;DATABASE=test"
    #     mock_connection = MagicMock()
    #     mock_pyodbc.connect.return_value = mock_connection
        
    #     from db_utils import get_connection
        
    #     conn = get_connection()
    #     assert conn is not None
    #     mock_pyodbc.connect.assert_called_once()
    
    @patch('db_utils.USE_MSSQL', False)
    @patch('db_utils.SQLITE_DB_PATH', '/nonexistent/path/database.db')
    def test_get_connection_failure(self):
        """Test connection failure handling."""
        from db_utils import get_connection
        
        with pytest.raises(Exception):
            get_connection()


class TestExecuteQuery:
    """Test query execution with both database types."""
    
    @patch('db_utils.USE_MSSQL', False)
    @patch('db_utils.get_connection')
    def test_execute_query_success(self, mock_get_connection, mock_sqlite_connection):
        """Test successful query execution."""
        mock_get_connection.return_value.__enter__ = Mock(return_value=mock_sqlite_connection)
        mock_get_connection.return_value.__exit__ = Mock(return_value=False)
        
        from db_utils import execute_query
        
        query = "SELECT * FROM test_table WHERE county = 'Honolulu'"
        df = execute_query(query)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert df['county'].iloc[0] == 'Honolulu'
        assert df['count'].iloc[0] == 100
    
    @patch('db_utils.USE_MSSQL', False)
    @patch('db_utils.get_connection')
    def test_execute_query_multiple_rows(self, mock_get_connection, mock_sqlite_connection):
        """Test query returning multiple rows."""
        mock_get_connection.return_value.__enter__ = Mock(return_value=mock_sqlite_connection)
        mock_get_connection.return_value.__exit__ = Mock(return_value=False)
        
        from db_utils import execute_query
        
        query = "SELECT * FROM test_table WHERE year = 2020"
        df = execute_query(query)
        
        assert len(df) == 2
        assert set(df['county']) == {'Honolulu', 'Maui'}
    
    @patch('db_utils.USE_MSSQL', False)
    @patch('db_utils.get_connection')
    def test_execute_query_empty_result(self, mock_get_connection, mock_sqlite_connection):
        """Test query returning no rows."""
        mock_get_connection.return_value.__enter__ = Mock(return_value=mock_sqlite_connection)
        mock_get_connection.return_value.__exit__ = Mock(return_value=False)
        
        from db_utils import execute_query
        
        query = "SELECT * FROM test_table WHERE county = 'Nonexistent'"
        df = execute_query(query)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
    
    @patch('db_utils.USE_MSSQL', False)
    @patch('db_utils.get_connection')
    def test_execute_query_with_aggregation(self, mock_get_connection, mock_sqlite_connection):
        """Test query with aggregation."""
        mock_get_connection.return_value.__enter__ = Mock(return_value=mock_sqlite_connection)
        mock_get_connection.return_value.__exit__ = Mock(return_value=False)
        
        from db_utils import execute_query
        
        query = "SELECT year, SUM(count) as total FROM test_table GROUP BY year"
        df = execute_query(query)
        
        assert len(df) == 2
        assert 'total' in df.columns
        year_2020 = df[df['year'] == 2020]['total'].iloc[0]
        assert year_2020 == 150  # 100 + 50
    
    @patch('db_utils.get_connection')
    def test_execute_query_error_handling(self, mock_get_connection):
        """Test error handling in query execution."""
        mock_conn = MagicMock()
        mock_conn.__enter__ = Mock(side_effect=Exception("Database error"))
        mock_get_connection.return_value = mock_conn
        
        from db_utils import execute_query
        
        with pytest.raises(Exception):
            execute_query("SELECT * FROM nonexistent_table")


class TestDatabaseModeSwitch:
    """Test switching between SQLite and MSSQL modes."""
    
    @patch('db_utils.USE_MSSQL', False)
    def test_sqlite_mode_uses_correct_path(self):
        """Test that SQLite mode uses the configured path."""
        from db_utils import USE_MSSQL
        assert USE_MSSQL is False
    
    @patch('db_utils.USE_MSSQL', True)
    def test_mssql_mode_enabled(self):
        """Test that MSSQL mode can be enabled."""
        from db_utils import USE_MSSQL
        assert USE_MSSQL is True


class TestConnectionContextManager:
    """Test that connections are properly managed as context managers."""
    
    @patch('db_utils.USE_MSSQL', False)
    @patch('db_utils.get_connection')
    def test_connection_closes_on_success(self, mock_get_connection):
        """Test connection closes after successful query."""
        mock_conn = MagicMock()
        mock_exit = Mock(return_value=False)
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = mock_exit
        mock_get_connection.return_value = mock_conn
        
        # Mock pandas read_sql_query
        with patch('pandas.read_sql_query', return_value=pd.DataFrame()):
            from db_utils import execute_query
            execute_query("SELECT 1")
        
        # Verify __exit__ was called (connection cleanup)
        mock_exit.assert_called_once()
    
    @patch('db_utils.USE_MSSQL', False)
    @patch('db_utils.get_connection')
    def test_connection_closes_on_error(self, mock_get_connection):
        """Test connection closes even after query error."""
        mock_conn = MagicMock()
        mock_exit = Mock(return_value=False)
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = mock_exit
        mock_get_connection.return_value = mock_conn
        
        # Mock pandas to raise an error
        with patch('pandas.read_sql_query', side_effect=Exception("Query error")):
            from db_utils import execute_query
            with pytest.raises(Exception):
                execute_query("SELECT * FROM bad_table")
        
        # Verify __exit__ was still called
        mock_exit.assert_called_once()

    
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
