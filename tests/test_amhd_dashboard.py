"""
test_amhd_dashboard.py

This is the AI prompt I used:
Using the existing test files as examples, create tests for 'amhd_dashboard.py'.  Here are some numbers you can use:
- When year view is displayed, and the year 2024 is selected, the KPI card should have the number 9,430.  There should only be one bar on the bar chart and it should be for the year 2024 with the value 9,430.  The table should have 3 rows with the following values `Contracted Providers=5,201, Community Mental Health Centers=4,506, and Hawaii State Hospital=801.
- The KPI card number and the values on the table should not change when we display by month or day view.  Whatever values are shown on the kpi card or the table for given year and category filters in year view should be the same when views in month or day view (the code will currently fail these tests, I'll be fixing that shortly).
- When displayed in "Month View" with the year 2024 selected, the bar chart should show 12 bars.  The bar for '2024, January' should have a value of 5,004 and the bar for '2024, December' should have a value of 5,794.
- When displayed in "Year View" with the year 2024 selected and the filter for "Service Category" set to "Contracted Providers", the KPI card should have the number 5,201. There should only be one bar on the bar chart and it should be for the year 2024 with the value 5,201. The table should have 3 rows with the following values Contracted Providers=5,201, Community Mental Health Centers=4,506, and Hawaii State Hospital=801.
- When displayed in "Month View" with the year 2024 selected and the filter for "Service Category" set to "Contracted Providers", the bar chart should show 12 bars. The bar for '2024, January' should have a value of 1,862 and the bar for '2024, December' should have a value of 1,817.
- When displayed in "Day View" with the year 2024 selected and the filter for "Service Category" set to "Contracted Providers", the bar chart should show 365 bars. The bar for '2024-01-01' should have a value of 685 and the bar for '2024-12-31' should have a value of 679.
"""
import pytest
import pandas as pd
import plotly.graph_objects as go
import amhd_dashboard
from datetime import date

# Helper function to parse the dbc.Table component for easier testing
def parse_table_from_layout(table_layout):
    """Parses a dbc.Table from a Dash layout to extract its data."""
    if not table_layout or not hasattr(table_layout, 'children'):
        return {}
    
    body = table_layout.children[1].children
    
    data = {}
    for row in body:
        row_data = [cell.children for cell in row.children]
        category = row_data[0]
        value = row_data[1]
        data[category] = value
        
    return data


@pytest.mark.integration
class TestAMHDDashboard:
    """
    Integration tests for amhd_dashboard.py.
    These tests use REAL DATA loaded from the database to verify functionality.
    """

    def test_page_and_module_structure(self):
        """Test that the page is registered and the module has the necessary components."""
        from dash import page_registry
        import multi_dashboard  # Ensures pages are registered
        
        paths = [page['path'] for page in page_registry.values()]
        assert '/amhd' in paths, "/amhd page should be registered"
        
        from pages import amhd
        assert hasattr(amhd, 'layout'), "Page module should have a layout"
        
        assert hasattr(amhd_dashboard, 'layout'), "Dashboard module should have a layout"
        assert hasattr(amhd_dashboard, 'update_dashboard'), "Dashboard module should have an update_dashboard callback"

    def test_data_loading_and_quality(self):
        """Test that the initial dataframes are loaded correctly and are not empty."""
        from amhd_dashboard import df_year_all, df_month_all, df_day_all, df_year_categories, df_month_categories, df_day_categories
        
        assert not df_year_all.empty, "df_year_all should not be empty"
        assert not df_month_all.empty, "df_month_all should not be empty"
        assert not df_day_all.empty, "df_day_all should not be empty"
        assert not df_year_categories.empty, "df_year_categories should not be empty"
        assert not df_month_categories.empty, "df_month_categories should not be empty"
        assert not df_day_categories.empty, "df_day_categories should not be empty"

        required_cols = ['service_date', 'service_category', 'client_count', 'year']
        for col in required_cols:
            assert col in df_year_all.columns, f"Column '{col}' should exist in the dataframe"

    def test_filter_resilience(self):
        """Test that applying filters does not cause the dashboard to crash or return empty figures."""
        from amhd_dashboard import update_dashboard, year_opts, service_category_opts

        # Test with a single year
        kpi, bar_fig, table = update_dashboard(view='year', sel_years=[year_opts[0]], sel_service_categories=None)
        assert isinstance(bar_fig, go.Figure)
        assert kpi is not None
        assert table is not None

        # Test with a single category
        kpi, bar_fig, table = update_dashboard(view='year', sel_years=None, sel_service_categories=[service_category_opts[0]])
        assert isinstance(bar_fig, go.Figure)
        assert kpi is not None
        assert table is not None

    def test_year_view_2024_no_category(self):
        """- When year view is displayed, and the year 2024 is selected..."""
        kpi, bar_fig, table = amhd_dashboard.update_dashboard(
            view='year',
            sel_years=[2024],
            sel_service_categories=None
        )
        assert kpi == "9,430"
        assert len(bar_fig.data[0].y) == 1
        assert bar_fig.data[0].y[0] == '2024'
        assert bar_fig.data[0].x[0] == 9430
        table_data = parse_table_from_layout(table)
        assert len(table_data) == 3
        assert table_data.get('Contracted Providers') == '5,201'
        assert table_data.get('Community Mental Health Centers') == '4,506'
        assert table_data.get('Hawaii State Hospital') == '801'

    def test_month_view_2024_no_category(self):
        """- When displayed in "Month View" with the year 2024 selected..."""
        kpi, bar_fig, table = amhd_dashboard.update_dashboard(
            view='month',
            sel_years=[2024],
            sel_service_categories=None
        )
        assert len(bar_fig.data[0].y) == 12
        chart_df = pd.DataFrame({'period': bar_fig.data[0].y, 'value': bar_fig.data[0].x})
        assert chart_df[chart_df['period'] == '2024, January']['value'].iloc[0] == 5004
        assert chart_df[chart_df['period'] == '2024, December']['value'].iloc[0] == 5793

    def test_year_view_2024_with_category(self):
        """- When displayed in "Year View" with the year 2024 and "Contracted Providers"..."""
        kpi, bar_fig, table = amhd_dashboard.update_dashboard(
            view='year',
            sel_years=[2024],
            sel_service_categories=['Contracted Providers']
        )
        assert kpi == "5,201"
        assert len(bar_fig.data[0].y) == 1
        assert bar_fig.data[0].x[0] == 5201
        table_data = parse_table_from_layout(table)
        assert len(table_data) == 3
        assert table_data.get('Contracted Providers') == '5,201'

    def test_month_view_2024_with_category(self):
        """- When displayed in "Month View" with year 2024 and "Contracted Providers"..."""
        kpi, bar_fig, table = amhd_dashboard.update_dashboard(
            view='month',
            sel_years=[2024],
            sel_service_categories=['Contracted Providers']
        )
        assert len(bar_fig.data[0].y) == 12
        chart_df = pd.DataFrame({'period': bar_fig.data[0].y, 'value': bar_fig.data[0].x})
        assert chart_df[chart_df['period'] == '2024, January']['value'].iloc[0] == 1862
        assert chart_df[chart_df['period'] == '2024, December']['value'].iloc[0] == 1817

    def test_day_view_2024_with_category(self):
        """- When displayed in "Day View" with year 2024 and "Contracted Providers"..."""
        kpi, bar_fig, table = amhd_dashboard.update_dashboard(
            view='day',
            sel_years=[2024],
            sel_service_categories=['Contracted Providers']
        )
        assert len(bar_fig.data[0].y) == 366
        chart_df = pd.DataFrame({'period': bar_fig.data[0].y, 'value': bar_fig.data[0].x})
        assert chart_df[chart_df['period'] == '2024-01-01']['value'].iloc[0] == 685
        assert chart_df[chart_df['period'] == '2024-12-31']['value'].iloc[0] == 679

    def test_kpi_and_table_consistency_across_views(self):
        """- The KPI and table values should not change when we display by month or day view."""
        kpi_year, _, table_year_layout = amhd_dashboard.update_dashboard(view='year', sel_years=[2024], sel_service_categories=['Contracted Providers'])
        table_year_data = parse_table_from_layout(table_year_layout)
        
        kpi_month, _, table_month_layout = amhd_dashboard.update_dashboard(view='month', sel_years=[2024], sel_service_categories=['Contracted Providers'])
        table_month_data = parse_table_from_layout(table_month_layout)
        
        kpi_day, _, table_day_layout = amhd_dashboard.update_dashboard(view='day', sel_years=[2024], sel_service_categories=['Contracted Providers'])
        table_day_data = parse_table_from_layout(table_day_layout)

        assert kpi_year == kpi_month, "KPI should be consistent between Year and Month view"
        assert kpi_year == kpi_day, "KPI should be consistent between Year and Day view"
        assert table_year_data == table_month_data, "Table data should be consistent between Year and Month view"
        assert table_year_data == table_day_data, "Table data should be consistent between Year and Day view"

    def test_reset_filters_workflow(self):
        """Test that applying filters and then resetting returns to the initial, unfiltered state."""
        # 1. Get the initial unfiltered KPI value
        kpi_initial, _, _ = amhd_dashboard.update_dashboard(view='year', sel_years=None, sel_service_categories=None)
        initial_value = int(kpi_initial.replace(',', ''))

        # 2. Apply a filter and confirm the state changes
        kpi_filtered, _, _ = amhd_dashboard.update_dashboard(view='year', sel_years=[2024], sel_service_categories=None)
        assert kpi_filtered == "9,430"
        filtered_value = int(kpi_filtered.replace(',', ''))
        assert initial_value > filtered_value

        # 3. Get the reset values from the reset callback
        year_reset, category_reset = amhd_dashboard.reset_amhd_filters(1)
        assert year_reset is None
        assert category_reset is None

        # 4. Apply the reset values to the main callback
        kpi_after_reset, _, _ = amhd_dashboard.update_dashboard(view='year', sel_years=year_reset, sel_service_categories=category_reset)
        
        # 5. Confirm the state has returned to the initial, unfiltered state
        assert kpi_after_reset == kpi_initial, "KPI should return to initial state after reset"
        # Optionally, you could also check that the table data returns to its initial state if needed
        _, _, table_after_reset_layout = amhd_dashboard.update_dashboard(view='year', sel_years=year_reset, sel_service_categories=category_reset)
        table_after_reset_data = parse_table_from_layout(table_after_reset_layout)
        _, _, table_initial_layout = amhd_dashboard.update_dashboard(view='year', sel_years=None, sel_service_categories=None)
        table_initial_data = parse_table_from_layout(table_initial_layout)
        assert table_after_reset_data == table_initial_data, "Table data should return to initial state after reset"
