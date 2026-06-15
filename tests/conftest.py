"""
Pytest configuration and shared fixtures for DOH Dashboard tests.
"""
import os
import sys
import pytest
import pandas as pd
from pathlib import Path

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set test environment variables before importing application code
os.environ['DASH_JUPYTER_MODE'] = 'off'
os.environ['USE_MSSQL'] = 'false'  # Use SQLite for tests
os.environ['SQLITE_DB_PATH'] = str(PROJECT_ROOT / 'DOH_AMHD_NO_PII.db')


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        'county': ['Honolulu', 'Maui', 'Hawaii', 'Kauai'],
        'year': [2020, 2020, 2021, 2021],
        'count': [100, 50, 75, 30],
        'rate': [10.5, 8.2, 9.1, 7.3]
    })


@pytest.fixture
def sample_dataframe_with_suppression():
    """Create a DataFrame with values below suppression threshold."""
    return pd.DataFrame({
        'category': ['A', 'B', 'C', 'D', 'E'],
        'count': [15, 8, 5, 25, 3],
        'percentage': [30.0, 16.0, 10.0, 50.0, 6.0]
    })


@pytest.fixture
def sample_filter_values():
    """Sample filter values for testing."""
    return {
        'county': ['Honolulu', 'Maui', 'Statewide'],
        'year': [2020, 2021, 2022],
        'age_group': ['0-17', '18-25', '26-34', '35-44', '45+']
    }


@pytest.fixture
def mock_db_connection(monkeypatch):
    """Mock database connection for testing without DB access."""
    import sqlite3
    
    # Create in-memory SQLite database
    conn = sqlite3.connect(':memory:')
    
    # Create sample table
    conn.execute('''
        CREATE TABLE test_data (
            id INTEGER PRIMARY KEY,
            county TEXT,
            year INTEGER,
            count INTEGER
        )
    ''')
    
    # Insert sample data
    conn.executemany(
        'INSERT INTO test_data (county, year, count) VALUES (?, ?, ?)',
        [
            ('Honolulu', 2020, 100),
            ('Maui', 2020, 50),
            ('Hawaii', 2021, 75),
        ]
    )
    conn.commit()
    
    # Mock get_connection to return our test connection
    def mock_get_connection():
        return conn
    
    monkeypatch.setattr('db_utils.get_connection', mock_get_connection)
    
    yield conn
    
    conn.close()


@pytest.fixture
def dash_app():
    """Create a Dash app instance for testing."""
    # Avoid circular imports
    import multi_dashboard
    from dash import Dash
    
    # Get the app instance
    app = multi_dashboard.app
    
    return app


@pytest.fixture
def dash_duo():
    """
    Fixture for Dash testing with Selenium.
    Requires pytest-dash to be installed.
    
    NOTE: pytest-dash may have compatibility issues with newer Selenium versions.
    If tests fail, mark them with @pytest.mark.skip or use dash.testing directly.
    """
    pytest.skip("dash_duo fixture requires pytest-dash with compatible Selenium version")
    return None


@pytest.fixture
def sample_query_result():
    """Sample query result DataFrame."""
    return pd.DataFrame({
        'county': ['Honolulu', 'Maui', 'Hawaii', 'Kauai', 'Honolulu', 'Maui'],
        'year': [2020, 2020, 2020, 2020, 2021, 2021],
        'substance': ['Alcohol', 'Opioids', 'Alcohol', 'Opioids', 'Alcohol', 'Opioids'],
        'count': [120, 85, 45, 30, 135, 90],
        'rate_per_100k': [12.5, 8.9, 10.2, 7.5, 13.1, 9.2]
    })


@pytest.fixture
def statewide_dataframe():
    """DataFrame with both county-level and statewide data."""
    return pd.DataFrame({
        'county': ['Honolulu', 'Maui', 'Hawaii', 'Statewide', 'Statewide'],
        'year': [2020, 2020, 2020, 2020, 2021],
        'count': [100, 50, 75, 225, 250],
    })


# Pytest hooks for custom behavior
def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Register custom markers
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as a regression test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Auto-mark tests based on file name
        if "test_dashboard_utils" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "test_db_utils" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "test_multi_dashboard" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "test_pages" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "test_regression" in str(item.fspath):
            item.add_marker(pytest.mark.regression)
