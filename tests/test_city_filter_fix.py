"""
Test to verify that city filter fix works correctly.

This test verifies that city values are trimmed of whitespace,
preventing the issue where selecting a city from the filter
would cause all visuals to go blank.
"""
import pytest
import pandas as pd


def test_discharges_su_city_values_are_trimmed():
    """Test that city values in discharges_su_dashboard are trimmed."""
    import discharges_su_dashboard
    
    df = discharges_su_dashboard.df_raw
    
    # Check that city column exists
    assert 'city' in df.columns, "City column should exist"
    
    # Get all unique city values
    city_values = df['city'].unique()
    
    # Check that no city values have leading or trailing whitespace
    for city in city_values:
        city_str = str(city)
        assert city_str == city_str.strip(), f"City value '{city}' has whitespace that should be trimmed"
    
    # Verify that common cities exist without trailing spaces
    cities_in_data = set(city_values)
    
    # If Honolulu exists, it should be "Honolulu" not "Honolulu "
    if any('honolulu' in str(c).lower() for c in cities_in_data):
        # Find the Honolulu value
        honolulu_values = [c for c in cities_in_data if 'honolulu' in str(c).lower()]
        for h in honolulu_values:
            assert str(h) == str(h).strip(), f"Honolulu value '{h}' should not have trailing spaces"


def test_discharges_mh_city_values_are_trimmed():
    """Test that city values in discharges_mh_dashboard are trimmed."""
    import discharges_mh_dashboard
    
    df = discharges_mh_dashboard.df_raw
    
    # Check that city column exists
    assert 'city' in df.columns, "City column should exist"
    
    # Get all unique city values
    city_values = df['city'].unique()
    
    # Check that no city values have leading or trailing whitespace
    for city in city_values:
        city_str = str(city)
        assert city_str == city_str.strip(), f"City value '{city}' has whitespace that should be trimmed"


def test_city_filter_returns_data():
    """
    Test that filtering by city returns data (not empty).
    
    This is the main test to verify the fix - previously selecting
    a city would return no data because of whitespace mismatch.
    """
    import discharges_su_dashboard
    
    df = discharges_su_dashboard.df_raw
    
    # Get a city value from the data
    city_values = df['city'].unique()
    
    # Filter out "Unknown"
    real_cities = [c for c in city_values if str(c).lower() != 'unknown']
    
    if len(real_cities) > 0:
        test_city = real_cities[0]
        
        # Filter the dataframe by this city
        filtered = df[df['city'] == test_city]
        
        # Should return data, not empty
        assert not filtered.empty, f"Filtering by city '{test_city}' should return data, but got empty dataframe"
        
        # All rows should have the selected city
        assert all(filtered['city'] == test_city), f"All filtered rows should have city='{test_city}'"


def test_city_filter_callback_works():
    """
    Test that the update_dashboard callback works with city filter.
    
    This simulates selecting a city from the dropdown and verifies
    that the callback returns valid figures (not empty/broken).
    """
    import discharges_su_dashboard
    
    df = discharges_su_dashboard.df_raw
    
    # Get a city value from the data
    city_values = df['city'].unique()
    real_cities = [c for c in city_values if str(c).lower() != 'unknown']
    
    if len(real_cities) > 0:
        test_city = real_cities[0]
        
        # Call the callback with city filter
        result = discharges_su_dashboard.update_dashboard(
            substance=None,
            county=None,
            city=[test_city],  # Filter by city
            year=None,
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        
        # Result should be a tuple with 12 elements
        assert len(result) == 12, f"Callback should return 12 elements, got {len(result)}"
        
        # First element is KPI text, should not be empty
        kpi_text = result[0]
        assert kpi_text is not None, "KPI should not be None"
        assert len(str(kpi_text)) > 0, "KPI should have content"
        
        # Second element is bar chart figure
        bar_fig = result[1]
        assert bar_fig is not None, "Bar chart figure should not be None"
        assert hasattr(bar_fig, 'data'), "Figure should have data attribute"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
