"""
Tests for wonder_overview_dashboard.py and /wonder-overview page.

Tests cover:
- Page loading and initialization
- Filter functionality (county and year)
- Data aggregation and display
- Chart data validation
- Specific test case: 2019 Honolulu filters showing 196 deaths

These tests use REAL DATA from the database/CSV files to verify:
- Queries are working correctly
- Visuals load as expected
- Filters work correctly with actual data
"""
import pytest
import pandas as pd
import plotly.graph_objects as go
import wonder_overview_dashboard


class TestWonderOverviewPageStructure:
    """Test basic page structure and initialization."""
    
    def test_wonder_overview_page_registered(self):
        """Test that wonder-overview page is registered."""
        from dash import page_registry
        import multi_dashboard  # Ensures pages are registered
        
        paths = [page['path'] for page in page_registry.values()]
        assert '/wonder-overview' in paths
    
    def test_wonder_overview_page_has_layout(self):
        """Test that wonder-overview page has a layout."""
        from pages import wonder_overview
        
        assert hasattr(wonder_overview, 'layout')
        assert wonder_overview.layout is not None
    
    def test_wonder_overview_imports_correctly(self):
        """Test that wonder_overview_dashboard module can be imported."""
        import wonder_overview_dashboard
        
        assert hasattr(wonder_overview_dashboard, 'layout')
        assert hasattr(wonder_overview_dashboard, 'update_dashboard')


class TestWonderOverviewDataLoading:
    """Test data loading and initialization with real data."""
    
    def test_load_wonder_overview_df_from_db(self):
        """Test that data loading function works correctly with real data."""
        # Load real data from database
        df = wonder_overview_dashboard.df_raw
        
        assert not df.empty, "Real data should not be empty"
        assert 'county' in df.columns, "Should have county column"
        assert 'year' in df.columns, "Should have year column"
        assert 'deaths' in df.columns, "Should have deaths column"
        assert len(df) > 0, "Should have at least some rows of data"
    
    def test_year_column_is_numeric(self):
        """Test that year column is converted to numeric in real data."""
        df = wonder_overview_dashboard.df_raw
        
        assert pd.api.types.is_numeric_dtype(df['year']), "Year column should be numeric"
    
    def test_real_data_has_honolulu_2019(self):
        """Test that real data includes the Honolulu 2019 record we're testing."""
        df = wonder_overview_dashboard.df_raw
        
        # Filter for Honolulu 2019
        honolulu_2019 = df[(df['county'] == 'Honolulu') & (df['year'] == 2019)]
        
        assert not honolulu_2019.empty, "Real data should have Honolulu 2019 record"
        assert honolulu_2019['deaths'].sum() == 196.0, "Honolulu 2019 should have 196 deaths"


@pytest.mark.integration
class TestWonderOverviewFiltering:
    """Test filter functionality with real data."""
    
    def test_filter_by_county_honolulu(self):
        """Test filtering by Honolulu county with real data."""
        # Use the real update_dashboard callback
        kpi, line_fig, bar_fig = wonder_overview_dashboard.update_dashboard(
            county=['Honolulu'], 
            year=[]
        )
        
        # Check that filtering worked - should only have Honolulu data
        bar_data = bar_fig.data[0]
        assert len(bar_data.y) == 1, "Should only show Honolulu county"
        assert bar_data.y[0] == 'Honolulu', "County should be Honolulu"
    
    def test_filter_by_year_2019(self):
        """Test filtering by year 2019 with real data."""
        # Use the real update_dashboard callback
        kpi, line_fig, bar_fig = wonder_overview_dashboard.update_dashboard(
            county=[], 
            year=[2019]
        )
        
        # Check line chart data - all years should be 2019
        line_data = line_fig.data
        for trace in line_data:
            # All x values should be 2019
            assert all(x == 2019 for x in trace.x), f"All years should be 2019, got {trace.x}"
    
    def test_filter_by_honolulu_and_2019(self):
        """
        Test filtering by both Honolulu county and year 2019 with real data.
        
        This is the specific test case requested: should show 196 deaths.
        """
        # Use the real update_dashboard callback
        kpi, line_fig, bar_fig = wonder_overview_dashboard.update_dashboard(
            county=['Honolulu'], 
            year=[2019]
        )
        
        # Verify bar chart shows correct data
        bar_data = bar_fig.data[0]
        assert len(bar_data.y) == 1, "Should only show one county (Honolulu)"
        assert bar_data.y[0] == 'Honolulu', "County should be Honolulu"
        assert bar_data.x[0] == 196.0, f"Should be 196 deaths, got {bar_data.x[0]}"
        
        # Verify line chart shows single point
        line_data = line_fig.data
        assert len(line_data) == 1, "Should only have one county series"
        
        honolulu_trace = line_data[0]
        assert len(honolulu_trace.x) == 1, "Should have single point"
        assert honolulu_trace.x[0] == 2019, f"Year should be 2019, got {honolulu_trace.x[0]}"
        assert honolulu_trace.y[0] == 196.0, f"Deaths should be 196, got {honolulu_trace.y[0]}"


@pytest.mark.integration
class TestWonderOverviewCharts:
    """Test chart generation and data validation with real data."""
    
    def test_bar_chart_structure(self):
        """Test that bar chart has correct structure with real data."""
        kpi, line_fig, bar_fig = wonder_overview_dashboard.update_dashboard(
            county=[], 
            year=[2019]
        )
        
        # Should be a bar chart
        assert isinstance(bar_fig, go.Figure), "Should be a Plotly Figure"
        assert len(bar_fig.data) > 0, "Should have at least one trace"
        assert bar_fig.data[0].type == 'bar', "Should be a bar chart"
        
        # Bar chart should be horizontal (orientation='h')
        assert bar_fig.data[0].orientation == 'h', "Bar chart should be horizontal"
    
    def test_line_chart_structure(self):
        """Test that line chart has correct structure with real data."""
        kpi, line_fig, bar_fig = wonder_overview_dashboard.update_dashboard(
            county=['Honolulu'], 
            year=[]
        )
        
        # Should be a line chart
        assert isinstance(line_fig, go.Figure), "Should be a Plotly Figure"
        assert len(line_fig.data) > 0, "Should have at least one trace"
        
        # Line chart should have scatter traces with lines
        for trace in line_fig.data:
            assert trace.type == 'scatter', "Should be scatter type"
            assert trace.mode in ['lines+markers', 'lines+markers+text'], f"Unexpected mode: {trace.mode}"
    
    def test_bar_chart_displays_death_counts(self):
        """Test that bar chart shows actual death counts with real data."""
        kpi, line_fig, bar_fig = wonder_overview_dashboard.update_dashboard(
            county=[], 
            year=[2019]
        )
        
        bar_data = bar_fig.data[0]
        
        # Check that x values (deaths) are positive numbers
        for x_val in bar_data.x:
            assert x_val > 0, f"Death count should be positive, got {x_val}"
    
    def test_line_chart_displays_death_counts(self):
        """Test that line chart shows actual death counts with real data."""
        kpi, line_fig, bar_fig = wonder_overview_dashboard.update_dashboard(
            county=['Honolulu'], 
            year=[]
        )
        
        # Check that y values (deaths) are positive numbers
        for trace in line_fig.data:
            for y_val in trace.y:
                assert y_val > 0, f"Death count should be positive, got {y_val}"


@pytest.mark.integration
class TestWonderOverviewKPI:
    """Test KPI (Key Performance Indicator) display with real data."""
    
    def test_kpi_shows_filtered_total(self):
        """Test that KPI shows correct total for filtered data."""
        kpi, line_fig, bar_fig = wonder_overview_dashboard.update_dashboard(
            county=['Honolulu'], 
            year=[2019]
        )
        
        # KPI should show 196 (Honolulu 2019 total)
        assert '196' in kpi, f"KPI should contain '196', got: {kpi}"
    
    def test_kpi_shows_statewide_when_no_county_filter(self):
        """Test that KPI defaults to statewide when no county is selected."""
        kpi, line_fig, bar_fig = wonder_overview_dashboard.update_dashboard(
            county=[], 
            year=[2019]
        )
        
        # Should show statewide total (261 based on real data)
        assert '261' in kpi, f"KPI should contain statewide total '261', got: {kpi}"


class TestWonderOverviewAggregation:
    """Test data aggregation logic with real data."""
    
    def test_deaths_sum_by_county(self):
        """Test that deaths are correctly summed by county in real data."""
        kpi, line_fig, bar_fig = wonder_overview_dashboard.update_dashboard(
            county=[], 
            year=[2019]
        )
        
        bar_data = bar_fig.data[0]
        
        # Find Honolulu in the data
        honolulu_idx = list(bar_data.y).index('Honolulu')
        honolulu_deaths = bar_data.x[honolulu_idx]
        
        assert honolulu_deaths == 196.0, f"Honolulu 2019 should have 196 deaths, got {honolulu_deaths}"
    
    def test_deaths_sum_by_year(self):
        """Test that deaths are correctly summed by year in real data."""
        kpi, line_fig, bar_fig = wonder_overview_dashboard.update_dashboard(
            county=['Honolulu'], 
            year=[]
        )
        
        # Find the trace for Honolulu
        honolulu_trace = line_fig.data[0]
        
        # Find 2019 data point
        year_2019_idx = list(honolulu_trace.x).index(2019)
        deaths_2019 = honolulu_trace.y[year_2019_idx]
        
        assert deaths_2019 == 196.0, f"Honolulu 2019 should have 196 deaths, got {deaths_2019}"


class TestWonderOverviewStatewideBehavior:
    """Test statewide data handling with real data."""
    
    def test_statewide_appears_first_in_charts(self):
        """Test that Statewide appears first when present in real data."""
        kpi, line_fig, bar_fig = wonder_overview_dashboard.update_dashboard(
            county=[], 
            year=[2019]
        )
        
        bar_data = bar_fig.data[0]
        
        # Statewide should be first in the list
        assert bar_data.y[0] == 'Statewide', f"Statewide should be first, got {bar_data.y[0]}"


class TestWonderOverviewResetFilters:
    """Test filter reset functionality."""
    
    def test_reset_filters_callback_exists(self):
        """Test that reset filters callback is defined."""
        assert hasattr(wonder_overview_dashboard, 'reset_all_filters'), "Should have reset_all_filters function"
        assert callable(wonder_overview_dashboard.reset_all_filters), "reset_all_filters should be callable"
    
    def test_reset_filters_returns_empty_lists(self):
        """Test that reset filters returns empty filter values."""
        county, year = wonder_overview_dashboard.reset_all_filters(1)
        
        assert county == [], "County filter should reset to empty list"
        assert year == [], "Year filter should reset to empty list"


@pytest.mark.regression
class TestWonderOverviewRegressionScenarios:
    """Regression tests for known scenarios and edge cases using real data."""
    
    def test_specific_scenario_honolulu_2019_196_deaths(self):
        """
        REGRESSION TEST: Specific test case for Honolulu 2019 with REAL DATA.
        
        When filtering for:
        - County: Honolulu
        - Year: 2019
        
        Expected results (verified from real data in wonder_overview.csv):
        - Bar chart should show 196 deaths for Honolulu
        - Line chart should show a single point with value 196 for year 2019
        - This verifies:
          * Query is working correctly
          * Visual loads as expected
          * Filters work correctly
        """
        # Apply the specific filters to real data
        kpi, line_fig, bar_fig = wonder_overview_dashboard.update_dashboard(
            county=['Honolulu'],
            year=[2019]
        )
        
        # TEST 1: Bar chart should show 196 deaths
        bar_data = bar_fig.data[0]
        assert len(bar_data.y) == 1, f"Bar chart should have exactly one county, got {len(bar_data.y)}"
        assert bar_data.y[0] == 'Honolulu', f"Bar chart should show Honolulu, got {bar_data.y[0]}"
        assert bar_data.x[0] == 196.0, f"Bar chart should show 196 deaths, got {bar_data.x[0]}"
        
        # TEST 2: Line chart should show single point
        assert len(line_fig.data) == 1, f"Line chart should have one trace (Honolulu), got {len(line_fig.data)}"
        
        honolulu_trace = line_fig.data[0]
        assert len(honolulu_trace.x) == 1, f"Line chart should have exactly one point, got {len(honolulu_trace.x)}"
        assert honolulu_trace.x[0] == 2019, f"Line chart x should be 2019, got {honolulu_trace.x[0]}"
        assert honolulu_trace.y[0] == 196.0, f"Line chart y should be 196, got {honolulu_trace.y[0]}"
        
        # TEST 3: KPI should show 196
        assert '196' in kpi, f"KPI should contain '196', got: {kpi}"
    
    def test_empty_filter_shows_all_data(self):
        """Regression: Empty filters should show all data from real database."""
        kpi, line_fig, bar_fig = wonder_overview_dashboard.update_dashboard(
            county=[], 
            year=[]
        )
        
        # Should have data for multiple counties
        bar_data = bar_fig.data[0]
        assert len(bar_data.y) > 1, f"Should show multiple counties, got {len(bar_data.y)}"
    
    def test_multiple_counties_selected(self):
        """Regression: Multiple county selection should work with real data."""
        kpi, line_fig, bar_fig = wonder_overview_dashboard.update_dashboard(
            county=['Honolulu', 'Maui'],
            year=[2019]
        )
        
        # Bar chart should show both counties
        bar_data = bar_fig.data[0]
        counties_shown = set(bar_data.y)
        assert 'Honolulu' in counties_shown, "Should show Honolulu"
        assert 'Maui' in counties_shown, "Should show Maui"
    
    def test_multiple_years_selected(self):
        """Regression: Multiple year selection should work with real data."""
        kpi, line_fig, bar_fig = wonder_overview_dashboard.update_dashboard(
            county=['Honolulu'],
            year=[2019, 2020]
        )
        
        # Line chart should show both years
        honolulu_trace = line_fig.data[0]
        years_shown = set(honolulu_trace.x)
        assert 2019 in years_shown, "Should show 2019"
        assert 2020 in years_shown, "Should show 2020"
    
    def test_real_data_maui_2019(self):
        """Regression: Verify Maui 2019 data from real CSV (32 deaths)."""
        kpi, line_fig, bar_fig = wonder_overview_dashboard.update_dashboard(
            county=['Maui'],
            year=[2019]
        )
        
        bar_data = bar_fig.data[0]
        assert bar_data.x[0] == 32.0, f"Maui 2019 should have 32 deaths, got {bar_data.x[0]}"
    
    def test_real_data_hawaii_county_2019(self):
        """Regression: Verify Hawaii county 2019 data from real CSV (16 deaths)."""
        # Use the correct county name with the ʻokina
        kpi, line_fig, bar_fig = wonder_overview_dashboard.update_dashboard(
            county=['Hawaiʻi'],
            year=[2019]
        )
        
        # Check that the bar figure is not empty before trying to access its data
        assert bar_fig.data, "Bar chart should have data for Hawaiʻi county"
        
        bar_data = bar_fig.data[0]
        assert bar_data.x[0] == 16.0, f"Hawaii county 2019 should have 16 deaths, got {bar_data.x[0]}"


@pytest.mark.integration
class TestWonderOverviewDisplayFormatting:
    """Test display formatting of counts with real data."""
    
    def test_bar_chart_shows_formatted_counts(self):
        """Test that bar chart displays formatted count text with real data."""
        kpi, line_fig, bar_fig = wonder_overview_dashboard.update_dashboard(
            county=['Honolulu'], 
            year=[2019]
        )
        
        bar_data = bar_fig.data[0]
        
        # Should have text attribute with formatted counts
        assert hasattr(bar_data, 'text'), "Bar chart should have text attribute"
        assert bar_data.text[0] == '196', f"Formatted count should be '196', got {bar_data.text[0]}"
    
    def test_line_chart_shows_formatted_counts(self):
        """Test that line chart displays formatted count text with real data."""
        kpi, line_fig, bar_fig = wonder_overview_dashboard.update_dashboard(
            county=['Honolulu'], 
            year=[2019]
        )
        
        honolulu_trace = line_fig.data[0]
        
        # Should have text attribute with formatted counts
        assert hasattr(honolulu_trace, 'text'), "Line chart should have text attribute"
        assert honolulu_trace.text[0] == '196', f"Formatted count should be '196', got {honolulu_trace.text[0]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
