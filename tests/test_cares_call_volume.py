"""
Query used to generate these tests:
Using test_adad.py as an example, create tests for 'cares_call_volume_dashboard.py'.  Here are some numbers you can use:
- When year view is displayed, and the year 2024 is selected, the KPI card should have the number 129K.  
There should only be one bar on the bar chart and it should be for the year 2024 with the value 128,733.  
- The KPI card number and the values on the table should not change when we display by month or day view.  Whatever values are shown on the kpi card or the table for given year and category filters in year view should be the same when views in month or day view.
- When displayed in "Month View" with the year 2024 selected, the bar chart should show 12 bars.  The bar for '2024, January' should have a value of 11,379 and the bar for '2024, December' should have a value of 9,845.
- When displayed in "Month View" with the year 2024 selected and the crisis line set to "911", the kpi card should show 821, the bar chart should show 12 bars.  The bar for '2024, January' should have a value of 167 and the bar for '2024, December' should have a value of 52, and the crisis line table should only have one row with the value of 821 for "911".
- When displayed in "Month View" with the year 2024 selected, the crisis line set to "911", and the month set to "January", the kpi card should show 167, the bar chart should show 1 bar.  The bar for '2024, January' should have a value of 167, and the crisis line table should only have one row with the value of 167 for "911".
- Verify the "Reset all filters" button resets back to the original state.
"""
import pytest
import pandas as pd
import plotly.graph_objects as go
import cares_call_volume_dashboard

# Helper function to parse the dbc.Table component for easier testing
def parse_table_from_layout(table_layout):
    """Parses a dbc.Table from a Dash layout to extract its data."""
    if not table_layout or not hasattr(table_layout, 'children'):
        return {}
    
    try:
        body = table_layout.children[1].children
        data = {}
        for row in body:
            row_data = [cell.children for cell in row.children]
            category = row_data[0]
            value = row_data[1]
            data[category] = value
        return data
    except (IndexError, AttributeError):
        return {}

@pytest.mark.integration
class TestCaresCallVolumeDashboard:
    """
    Integration tests for cares_call_volume_dashboard.py.
    These tests use REAL DATA loaded from the database to verify functionality.
    """

    def test_page_and_module_structure(self):
        """Test that the page is registered and the module has the necessary components."""
        from dash import page_registry
        import multi_dashboard  # Ensures pages are registered
        
        paths = [page['path'] for page in page_registry.values()]
        assert '/cares-call-volume' in paths, "/cares-call-volume page should be registered"
        
        from pages import cares_call_volume
        assert hasattr(cares_call_volume, 'layout'), "Page module should have a layout"
        
        assert hasattr(cares_call_volume_dashboard, 'layout'), "Dashboard module should have a layout"
        assert hasattr(cares_call_volume_dashboard, 'update_dashboard'), "Dashboard module should have an update_dashboard callback"

    def test_data_loading_and_quality(self):
        """Test that the initial dataframe is loaded correctly and is not empty."""
        from cares_call_volume_dashboard import df_raw
        
        assert not df_raw.empty, "df_raw should not be empty"

        required_cols = ['day', 'origin_of_call', 'count_of_users', 'year', 'month']
        for col in required_cols:
            assert col in df_raw.columns, f"Column '{col}' should exist in the dataframe"

    def test_filter_resilience(self):
        """Test that applying filters does not cause the dashboard to crash or return empty figures."""
        from cares_call_volume_dashboard import update_dashboard, year_opts

        # Test with a single year
        bar_fig, kpi, table = update_dashboard(view='year', sel_years=[year_opts[0]], sel_months=None, sel_crisis=None)
        assert isinstance(bar_fig, go.Figure)
        assert kpi is not None
        assert table is not None

    def test_year_view_2024(self):
        """- When year view is displayed, and the year 2024 is selected..."""
        bar_fig, kpi, table = cares_call_volume_dashboard.update_dashboard(
            view='year',
            sel_years=[2024],
            sel_months=None,
            sel_crisis=None
        )
        assert kpi == "129K"
        assert len(bar_fig.data[0].y) == 1
        assert bar_fig.data[0].y[0] == '2024'
        assert bar_fig.data[0].x[0] == 128733

    def test_month_view_2024(self):
        """- When displayed in "Month View" with the year 2024 selected..."""
        bar_fig, kpi, table = cares_call_volume_dashboard.update_dashboard(
            view='month',
            sel_years=[2024],
            sel_months=None,
            sel_crisis=None
        )
        assert len(bar_fig.data[0].y) == 12
        chart_df = pd.DataFrame({'period': bar_fig.data[0].y, 'value': bar_fig.data[0].x})
        assert chart_df[chart_df['period'] == '2024, January']['value'].iloc[0] == 11379
        assert chart_df[chart_df['period'] == '2024, December']['value'].iloc[0] == 9845

    def test_month_view_2024_with_crisis_line(self):
        """- When displayed in Month View, 2024 selected, and crisis line set to 911..."""
        bar_fig, kpi, table = cares_call_volume_dashboard.update_dashboard(
            view='month',
            sel_years=[2024],
            sel_months=None,
            sel_crisis=['911']
        )
        assert kpi == "821"
        assert len(bar_fig.data[0].y) == 12
        
        chart_df = pd.DataFrame({'period': bar_fig.data[0].y, 'value': bar_fig.data[0].x})
        assert chart_df[chart_df['period'] == '2024, January']['value'].iloc[0] == 167
        assert chart_df[chart_df['period'] == '2024, December']['value'].iloc[0] == 52

        table_data = parse_table_from_layout(table)
        assert len(table_data) == 1
        assert table_data.get('911') == '821'

    def test_month_view_2024_with_crisis_line_and_month(self):
        """- When displayed in Month View, 2024 selected, crisis line 911, and month January..."""
        bar_fig, kpi, table = cares_call_volume_dashboard.update_dashboard(
            view='month',
            sel_years=[2024],
            sel_months=['January'],
            sel_crisis=['911']
        )
        assert kpi == "167"
        assert len(bar_fig.data[0].y) == 1
        assert bar_fig.data[0].y[0] == '2024, January'
        assert bar_fig.data[0].x[0] == 167

        table_data = parse_table_from_layout(table)
        assert len(table_data) == 1
        assert table_data.get('911') == '167'

    def test_kpi_and_table_consistency_across_views(self):
        """- The KPI and table values should not change when we display by month view vs year view."""
        bar_year, kpi_year, table_year_layout = cares_call_volume_dashboard.update_dashboard(
            view='year', sel_years=[2024], sel_months=None, sel_crisis=['911']
        )
        table_year_data = parse_table_from_layout(table_year_layout)
        
        bar_month, kpi_month, table_month_layout = cares_call_volume_dashboard.update_dashboard(
            view='month', sel_years=[2024], sel_months=None, sel_crisis=['911']
        )
        table_month_data = parse_table_from_layout(table_month_layout)
        
        assert kpi_year == kpi_month, "KPI should be consistent between Year and Month view"
        assert table_year_data == table_month_data, "Table data should be consistent between Year and Month view"

    def test_reset_filters_workflow(self):
        """Test that applying filters and then resetting returns to the initial, unfiltered state."""
        # 1. Get the initial unfiltered KPI value
        bar_initial, kpi_initial, table_initial = cares_call_volume_dashboard.update_dashboard(
            view='year', sel_years=None, sel_months=None, sel_crisis=None
        )

        # 2. Apply a filter and confirm the state changes
        bar_filtered, kpi_filtered, _ = cares_call_volume_dashboard.update_dashboard(
            view='year', sel_years=[2024], sel_months=None, sel_crisis=None
        )
        assert kpi_filtered == "129K"
        assert kpi_initial != kpi_filtered

        # 3. Get the reset values from the reset callback
        year_reset, month_reset, crisis_reset = cares_call_volume_dashboard.reset_cares_filters(1)
        assert year_reset is None
        assert month_reset is None
        assert crisis_reset is None

        # 4. Apply the reset values to the main callback
        bar_after_reset, kpi_after_reset, table_after_reset = cares_call_volume_dashboard.update_dashboard(
            view='year', sel_years=year_reset, sel_months=month_reset, sel_crisis=crisis_reset
        )
        
        # 5. Confirm the state has returned to the initial, unfiltered state
        assert kpi_after_reset == kpi_initial, "KPI should return to initial state after reset"
        
        table_initial_data = parse_table_from_layout(table_initial)
        table_after_reset_data = parse_table_from_layout(table_after_reset)
        assert table_initial_data == table_after_reset_data, "Table data should return to initial state after reset"