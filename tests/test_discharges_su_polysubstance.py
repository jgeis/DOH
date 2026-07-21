"""
Tests for discharges_su_polysubstance_dashboard.py and /discharges-su page.

Tests cover:
- Page loading and initialization
- Filter functionality with real data
- Data validation across all visuals
- Specific test case: Alcohol, 2024, Honolulu, 18-44, Male showing 1,473 discharges

These tests use REAL DATA from the database to verify:
- Queries are working correctly
- Visuals load as expected
- Filters work correctly with actual data
"""
import pytest
import pandas as pd
import plotly.graph_objects as go
import discharges_su_polysubstance_dashboard
from tests.test_utils import assert_returned_tables_sort_order

class TestPageStructure:
    """Test basic page structure and initialization."""
    
    def test_discharges_su_polysubstance_page_registered(self):
        """Test that discharges-su-polysubstance page is registered."""
        from dash import page_registry
        import multi_dashboard  # Ensures pages are registered
        
        paths = [page['path'] for page in page_registry.values()]
        assert '/discharges-su-polysubstance' in paths, "discharges-su-polysubstance page should be registered"
    
    def test_discharges_su_polysubstance_page_has_layout(self):
        """Test that discharges-su-polysubstance page has a layout."""
        from pages import discharges_su_polysubstance
        assert hasattr(discharges_su_polysubstance, 'layout'), "Page should have layout attribute"
        assert discharges_su_polysubstance.layout is not None, "Layout should not be None"
    
    def test_discharges_su_polysubstance_imports_correctly(self):
        """Test that discharges_su_polysubstance_dashboard module can be imported."""
        assert hasattr(discharges_su_polysubstance_dashboard, 'layout'), "Module should have layout"
        assert hasattr(discharges_su_polysubstance_dashboard, 'update'), "Module should have update callback"

    def test_callback_returns_tables_in_canonical_order(self):
        """Verify the update_dashboard callback returns tables sorted by dashboard_utils."""
        assert_returned_tables_sort_order(discharges_su_polysubstance_dashboard)

class TestDataLoading:
    """Test data loading and initialization with real data."""
    
    def test_load_discharge_dataframe_from_db(self):
        """Test that data loading function works correctly with real data."""
        df = discharges_su_polysubstance_dashboard.df_raw
        assert not df.empty, "Real data should not be empty"
        assert 'substance' in df.columns, "Should have substance column"
        assert 'county' in df.columns, "Should have county column"
        assert 'year' in df.columns, "Should have year column"
        assert 'age_group' in df.columns, "Should have age_group column"
        assert 'sex' in df.columns, "Should have sex column"
        assert 'record_id' in df.columns, "Should have record_id column"
        assert len(df) > 0, "Should have at least some rows of data"
    
    def test_year_column_is_numeric(self):
        """Test that year column is numeric in real data."""
        df = discharges_su_polysubstance_dashboard.df_raw
        assert pd.api.types.is_numeric_dtype(df['year']), "Year column should be numeric"
    
    def test_county_column_has_no_trailing_whitespace(self):
        """Test that county column values are trimmed (regression test for county filter bug)."""
        df = discharges_su_polysubstance_dashboard.df_raw
        if 'county' in df.columns:
            county_values = df['county'].unique()
            for county in county_values:
                county_str = str(county)
                assert county_str == county_str.strip(), f"County '{county}' should not have trailing whitespace"

    def test_sex_column_has_no_trailing_whitespace(self):
        """Test that sex column values are trimmed (regression test for sex filter bug)."""
        df = discharges_su_polysubstance_dashboard.df_raw
        if 'sex' in df.columns:
            sex_values = df['sex'].unique()
            for sex in sex_values:
                sex_str = str(sex)
                assert sex_str == sex_str.strip(), f"Sex '{sex}' should not have trailing whitespace"

    def test_substance_column_has_no_trailing_whitespace(self):
        """Test that substance column values are trimmed (regression test for substance filter bug)."""
        df = discharges_su_polysubstance_dashboard.df_raw
        if 'substance' in df.columns:
            substance_values = df['substance'].unique()
            for substance in substance_values:
                substance_str = str(substance)
                assert substance_str == substance_str.strip(), f"Substance '{substance}' should not have trailing whitespace"

    def test_age_column_has_no_trailing_whitespace(self):
        """Test that age column values are trimmed (regression test for age filter bug)."""
        df = discharges_su_polysubstance_dashboard.df_raw
        if 'age_group' in df.columns:
            age_values = df['age_group'].unique()
            for age in age_values:
                age_str = str(age)
                assert age_str == age_str.strip(), f"Age '{age}' should not have trailing whitespace"

@pytest.mark.integration
class TestFiltering:
    """Test filter functionality with real data."""
    
    def test_filter_by_substance_alcohol(self):
        """Test filtering by Alcohol substance with real data."""
        result = discharges_su_polysubstance_dashboard.update(
            substance=['Alcohol'],
            county=None,
            year=None,
            age=None,
            sex=None
        )
        # Result should be a tuple with 11 elements
        print(result)
        assert len(result) == 11, f"Should return 11 elements, got {len(result)}"
        # KPI should show some value
        kpi = result[0]
        assert kpi is not None, "KPI should not be None"
        assert '1' in str(kpi) or '2' in str(kpi), "KPI should show numeric value"

    def test_filter_by_year_2024(self):
        """Test filtering by year 2024 with real data."""
        result = discharges_su_polysubstance_dashboard.update(
            substance=None,
            county=None,
            year=[2024],
            age=None,
            sex=None
        )
        #print(result)
        kpi, substance_type_bar_title, substance_line_title, substance_bar_title, bar_fig, substance_line, county_line, table_county, table_year, table_age, table_sex = result
        print(f"kpi: {kpi}")
        print(f"substance_type_bar_title: {substance_type_bar_title}")
        print(f"substance_line_title: {substance_line_title}")
        print(f"substance_bar_title: {substance_bar_title}")
        print(f"bar_fig: {bar_fig}")
        print(f"substance_line: {substance_line}")

        print(f"county_line: {county_line}")
        print(f"table_county: {table_county}")
        print(f"table_year: {table_year}")
        print(f"table_sex: {table_sex}")
        print(f"table_age: {table_age}")


        # Line charts should only show 2024 data
        if len(substance_line.data) > 0:
            for trace in substance_line.data:
                if len(trace.x) > 0:
                    assert all(x == 2024 for x in trace.x), f"All years should be 2024, got {trace.x}"
        # Year table should show 3,232 for year 2024
        assert table_year is not None, "Year table should not be None"
        table_year_str = str(table_year)
        assert '3,232' in table_year_str or '3232' in table_year_str, f"Year table should contain 3,232, got: {table_year_str}"
        assert '2024' in table_year_str, f"Year table should contain 2024, got: {table_year_str}"     

    def test_filter_by_county_honolulu(self):
        """Test filtering by Honolulu county with real data."""
        result = discharges_su_polysubstance_dashboard.update(
            substance=None,
            county=['Honolulu'],
            year=[2024],
            age=None,
            sex=None
        )
        kpi, substance_type_bar_title, substance_line_title, substance_bar_title, bar_fig, substance_line, county_line, table_county, table_year, table_age, table_sex = result
        # Bar chart should have data
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        # KPI card should show 1,895 
        assert '1,895' in kpi or '1895' in kpi, f"KPI should contain '1,895', got: {kpi}"
        # County table should show 1,895 for county Honolulu
        assert table_county is not None, "County table should not be None"
        table_county_str = str(table_county)
        assert '1,895' in table_county_str or '1895' in table_county_str, f"County table should contain 1,895, got: {table_county_str}"
        assert 'Honolulu' in table_county_str, f"County table should contain Honolulu, got: {table_county_str}"
        # Year table should show 1,895 for year 2024
        assert table_year is not None, "Year table should not be None"
        table_year_str = str(table_year)
        assert '1,895' in table_year_str or '1895' in table_year_str, f"Year table should contain 1,895, got: {table_year_str}"
        assert '2024' in table_year_str, f"Year table should contain 2024, got: {table_year_str}"       

    def test_filter_by_age_group_18_44(self):
        """Test filtering by age group 18-44 with real data."""
        result = discharges_su_polysubstance_dashboard.update(
            substance=None,
            county=None,
            year=[2024],
            age=['18-44'],
            sex=None
        )
        kpi, substance_type_bar_title, substance_line_title, substance_bar_title, bar_fig, substance_line, county_line, table_county, table_year, table_age, table_sex = result
        # Bar chart should have data
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        # KPI card should show 1,660
        assert '1,660' in kpi or '1660' in kpi, f"KPI should contain '1,660', got: {kpi}"
        # Age table should show 1,660 for age group 18-44
        assert table_age is not None, "Age table should not be None"
        table_age_str = str(table_age)
        assert '1,660' in table_age_str or '1660' in table_age_str, f"Age table should contain 1,660, got: {table_age_str}"
        assert '18-44' in table_age_str, f"Age table should contain 18-44, got: {table_age_str}"

    def test_filter_by_sex_male(self):
        """Test filtering by sex Male with real data."""
        result = discharges_su_polysubstance_dashboard.update(
            substance=None,
            county=None,
            year=[2024],
            age=None,
            sex=['Male']
        )
        kpi, substance_type_bar_title, substance_line_title, substance_bar_title, bar_fig, substance_line, county_line, table_county, table_year, table_age, table_sex = result
        # Bar chart should have data
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        # KPI card should show 2,320
        assert '2,320' in kpi or '2320' in kpi, f"KPI should contain '2,320', got: {kpi}"
        # Sex table should show 2,320 for Male
        assert table_sex is not None, "Sex table should not be None"
        table_sex_str = str(table_sex)
        assert '2,320' in table_sex_str or '2320' in table_sex_str, f"Sex table should contain 2,320, got: {table_sex_str}"
        assert 'Male' in table_sex_str, f"Sex table should contain Male, got: {table_sex_str}"


@pytest.mark.regression
class TestRegressionScenarios:
    """Regression tests for known scenarios using real data."""
    def test_empty_filters_shows_all_data(self):
        """Regression: Empty filters should show all data from real database."""
        result = discharges_su_polysubstance_dashboard.update(
            substance=None,
            county=None,
            year=None,
            age=None,
            sex=None
        )
        
        (kpi, substance_type_bar_title, substance_line_title, substance_bar_title, 
         bar_fig, substance_line, county_line, 
         table_county, table_year, table_age, table_sex) = result
                
        # Should have data for multiple substances
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        
        bar_data = bar_fig.data[0]
        assert len(bar_data.y) > 1, f"Should show multiple substances, got {len(bar_data.y)}"
    
    def test_multiple_years_selected(self):
        """Regression: Multiple year selection should work with real data."""
        result = discharges_su_polysubstance_dashboard.update(
            substance=['Alcohol'],
            county=['Honolulu'],
            year=[2023, 2024],
            age=['18-44'],
            sex=['Male']
        )
        
        (kpi, substance_type_bar_title, substance_line_title, substance_bar_title, 
         bar_fig, substance_line, county_line, 
         table_county, table_year, table_age, table_sex) = result
                
        # Line charts should show both years
        if len(substance_line.data) > 0:
            alcohol_trace = substance_line.data[0]
            years_shown = set(alcohol_trace.x)
            assert 2023 in years_shown and 2024 in years_shown, "Should show both of the selected years"

@pytest.mark.integration
class TestCharts:
    """Test chart generation and data validation with real data."""
    
    def test_bar_chart_structure(self):
        """Test that bar chart has correct structure with real data."""
        result = discharges_su_polysubstance_dashboard.update(
            substance=None,
            county=None,
            year=[2024],
            age=None,
            sex=None
        )
        (kpi, substance_type_bar_title, substance_line_title, substance_bar_title, 
         bar_fig, substance_line, county_line, 
         table_county, table_year, table_age, table_sex) = result
                
        # Should be a bar chart
        assert isinstance(bar_fig, go.Figure), "Should be a Plotly Figure"
        assert len(bar_fig.data) > 0, "Should have at least one trace"
        assert bar_fig.data[0].type == 'bar', "Should be a bar chart"

        # Bar chart should be horizontal (orientation='h')
        assert bar_fig.data[0].orientation == 'h', "Bar chart should be horizontal"

    
    def test_line_chart_structure(self):
        """Test that line charts have correct structure with real data."""
        result = discharges_su_polysubstance_dashboard.update(
            substance=['Alcohol'],
            county=None,
            year=None,
            age=None,
            sex=None
        )
        
        (kpi, substance_type_bar_title, substance_line_title, substance_bar_title, 
         bar_fig, substance_line, county_line, 
         table_county, table_year, table_age, table_sex) = result
                
        # Substance line should be a line chart
        assert isinstance(substance_line, go.Figure), "Should be a Plotly Figure"
        if len(substance_line.data) > 0:
            for trace in substance_line.data:
                assert trace.type == 'scatter', "Should be scatter type"

        # County line should be a line chart
        assert isinstance(county_line, go.Figure), "Should be a Plotly Figure"
        if len(county_line.data) > 0:
            for trace in county_line.data:
                assert trace.type == 'scatter', "Should be scatter type"
    



class TestTables:
    """Test table generation with real data."""
    
    def test_tables_are_not_none(self):
        """Test that all tables are generated."""
        result = discharges_su_polysubstance_dashboard.update(
            substance=['Alcohol'],
            county=None,
            year=[2024],
            age=None,
            sex=None
        )
        
        (kpi, substance_type_bar_title, substance_line_title, substance_bar_title, 
         bar_fig, substance_line, county_line, 
         table_county, table_year, table_age, table_sex) = result

        assert table_year is not None, "Year table should not be None"
        assert table_county is not None, "County table should not be None"
        assert table_age is not None, "Age table should not be None"
        assert table_sex is not None, "Sex table should not be None"

class TestResetFilters:
    """Test filter reset functionality."""
    
    def test_reset_filters_callback_exists(self):
        """Test that reset filters callback is defined."""
        assert hasattr(discharges_su_polysubstance_dashboard, 'reset_filters'), "Should have reset_discharges_filters function"
        assert callable(discharges_su_polysubstance_dashboard.reset_filters), "reset_discharges_filters should be callable"
    
    def test_reset_filters_returns_none_values(self):
        """Test that reset filters returns None for all filter values."""
        result = discharges_su_polysubstance_dashboard.reset_filters(1)
        
        # Should return 5 None values (one for each filter)
        assert len(result) == 5, f"Should return 5 values, got {len(result)}"
        assert all(len(v) == 0 for v in result), "All filter values should be empty lists after reset"


@pytest.mark.integration
class TestDataConsistency:
    """Test data consistency across different visuals."""
    
    def test_kpi_matches_filtered_data_count(self):
        """Test that KPI value matches the actual filtered data count."""
        # Get raw data and apply same filters
        df = discharges_su_polysubstance_dashboard.df_raw.copy()
        
        # Apply filters manually
        df_filtered = df[
            (df['substance'] == 'Alcohol') &
            (df['county'] == 'Honolulu') &
            (df['year'] == 2024) &
            (df['age_group'] == '18-44') &
            (df['sex'] == 'Male')
        ]
        
        expected_count = df_filtered['record_id'].nunique()
        
        # Now call the dashboard callback
        result = discharges_su_polysubstance_dashboard.update(
            substance=['Alcohol'],
            county=['Honolulu'],
            year=[2024],
            age=['18-44'],
            sex=['Male']
        )
        
        kpi_text = result[0]
        
        # Extract number from KPI text
        import re
        numbers = re.findall(r'[\d,]+', kpi_text)
        if numbers:
            kpi_value = int(numbers[0].replace(',', ''))
            assert kpi_value == expected_count, f"KPI should show {expected_count}, got {kpi_value}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])