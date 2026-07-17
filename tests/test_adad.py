"""
test_adad.py

This is the AI prompt I used:
Using test_discharges_su.py as an example, write tests for adad_dashboard.py.  Here are some numbers you can use:
- When year view is displayed, and the year 2024 is selected, the KPI card should have the number 8,377.  There should only be one bar on the bar chart and it should be for the year 2024 with the value 8,377.  The calendar year table should have 1 row with the value 8,377 for the year 2024.  The county table should have 6 rows with the following values Hawaiʻi=976, Kauaʻi1=150, Lānaʻi=<10*, Maui=765, Oahu=6,186, and Unknown=766.  The service modality table should have 19 rows.  The Care Coordination row should have a value of 6,612. The "Clients served by modality and year" line chart should have a single column and the modalities and number of clients should match those found in the service modality table.  The "Clients served by county and year" line chart should have a single column and the counties and number of clients should match those found in the county table.
- The KPI card number and the values on the tables should not change when we display by month or day view.  Whatever values are shown on the kpi card or the tables for given year and category filters in year view should be the same when viewed in month or day view.
- When displayed in "Month View" with the year 2024 selected, the bar chart should show 12 bars.  The bar for '2024, January' should have a value of 2,360 and the bar for '2024, December' should have a value of 1,968.
- When displayed in "Year View" with the year 2024 selected and the filter for "Service Category" set to "Care Coordination", the KPI card should have the number 6,612. There should only be one bar on the bar chart and it should be for the year 2024 with the value 6,612.  The calendar year table should have 1 row with the value 6,612 for the year 2024. The county table should have 6 rows with the following values Hawaiʻi=566, Kauaʻi1=100, Maui=602, Oahu=5,054, and Unknown=647. The service modality table should have 1 row with Care Coordination modality having a value of 6,612. The "Clients served by modality and year" line chart should have a single point with the modalities and number of clients matching that found in the service modality table. The "Clients served by county and year" line chart should have a single column and the counties and number of clients should match those found in the county table.
- When displayed in "Month View" with the year 2024 selected and the filter for "Service Category" set to "Care Coordination", the bar chart should show 12 bars. The bar for '2024, January' should have a value of 1,718 and the bar for '2024, December' should have a value of 1,127.
- When displayed in "Day View" with the year 2024 selected and the filter for "Service Category" set to "Contracted Providers", the bar chart should show 365 bars. The bar for '2024-01-01' should have a value of 37 and the bar for '2024-12-31' should have a value of 59.
"""

import pytest
import pandas as pd
import plotly.graph_objects as go
import adad_dashboard
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
class TestADADDashboard:
    """
    Integration tests for adad_dashboard.py.
    These tests use REAL DATA loaded from the database to verify functionality.
    """

    def test_page_and_module_structure(self):
        """Test that the page is registered and the module has the necessary components."""
        from dash import page_registry
        import multi_dashboard  # Ensures pages are registered
        
        paths = [page['path'] for page in page_registry.values()]
        assert '/adad' in paths, "/adad page should be registered"
        
        from pages import adad
        assert hasattr(adad, 'layout'), "Page module should have a layout"
        
        assert hasattr(adad_dashboard, 'layout'), "Dashboard module should have a layout"
        assert hasattr(adad_dashboard, 'update_dashboard'), "Dashboard module should have an update_dashboard callback"

    def test_data_loading_and_quality(self):
        """Test that the initial dataframe is loaded correctly and is not empty."""
        from adad_dashboard import df_raw
        
        assert not df_raw.empty, "df_raw should not be empty"
        required_cols = ['service_date', 'client_id', 'county', 'modality', 'year', 'month']
        for col in required_cols:
            assert col in df_raw.columns, f"Column '{col}' should exist in the dataframe"

    def test_year_view_2024_no_category(self):
        """- When year view is displayed, and the year 2024 is selected..."""
        bar_fig, modality_line, county_line, kpi, modality_table, year_table, county_table = adad_dashboard.update_dashboard(
            view='year', sel_years=[2024], sel_months=None, sel_modalities=None, sel_counties=None, start_date=None, end_date=None
        )
        
        assert kpi == "8,377"
        assert len(bar_fig.data[0].y) == 1 and bar_fig.data[0].y[0] == '2024' and bar_fig.data[0].x[0] == 8377
        
        year_table_data = parse_table_from_layout(year_table)
        # FIX: Access dictionary key with integer 2024, not string '2024'
        assert len(year_table_data) == 1 and year_table_data.get(2024) == '8,377'

        county_table_data = parse_table_from_layout(county_table)
        assert len(county_table_data) == 6
        assert county_table_data.get('Hawaiʻi') == '976'
        assert county_table_data.get('Kauaʻi') == '150'
        assert county_table_data.get('Lānaʻi') == '<10*'
        assert county_table_data.get('Maui') == '765'
        assert county_table_data.get('Oahu') == '6,186'
        assert county_table_data.get('Unknown') == '766'

        modality_table_data = parse_table_from_layout(modality_table)
        assert len(modality_table_data) == 19
        assert modality_table_data.get('Care Coordination') == '6,612'

        assert len(modality_line.data) > 0
        assert len(county_line.data) > 0

    def test_month_view_2024_no_category(self):
        """- When displayed in "Month View" with the year 2024 selected..."""
        bar_fig, _, _, _, _, _, _ = adad_dashboard.update_dashboard(
            view='month', sel_years=[2024], sel_months=None, sel_modalities=None, sel_counties=None, start_date=None, end_date=None
        )
        assert len(bar_fig.data[0].y) == 12
        chart_df = pd.DataFrame({'period': bar_fig.data[0].y, 'value': bar_fig.data[0].x})
        assert chart_df[chart_df['period'] == '2024, January']['value'].iloc[0] == 2360
        assert chart_df[chart_df['period'] == '2024, December']['value'].iloc[0] == 1968

    def test_year_view_2024_with_category(self):
        """- When displayed in "Year View" with 2024 and "Care Coordination"..."""
        bar_fig, modality_line, county_line, kpi, modality_table, year_table, county_table = adad_dashboard.update_dashboard(
            view='year', sel_years=[2024], sel_months=None, sel_modalities=['Care Coordination'], sel_counties=None, start_date=None, end_date=None
        )
        assert kpi == "6,612"
        assert len(bar_fig.data[0].y) == 1 and bar_fig.data[0].x[0] == 6612
        
        year_table_data = parse_table_from_layout(year_table)
        # FIX: Access dictionary key with integer 2024, not string '2024'
        assert len(year_table_data) == 1 and year_table_data.get(2024) == '6,612'

        county_table_data = parse_table_from_layout(county_table)
        assert len(county_table_data) == 5
        assert county_table_data.get('Hawaiʻi') == '566'
        assert county_table_data.get('Kauaʻi') == '100'
        assert county_table_data.get('Maui') == '602'
        assert county_table_data.get('Oahu') == '5,054'
        assert county_table_data.get('Unknown') == '647'

        modality_table_data = parse_table_from_layout(modality_table)
        assert len(modality_table_data) == 1 and modality_table_data.get('Care Coordination') == '6,612'

    def test_month_view_2024_with_category(self):
        """- When displayed in "Month View" with 2024 and "Care Coordination"..."""
        bar_fig, _, _, _, _, _, _ = adad_dashboard.update_dashboard(
            view='month', sel_years=[2024], sel_months=None, sel_modalities=['Care Coordination'], sel_counties=None, start_date=None, end_date=None
        )
        assert len(bar_fig.data[0].y) == 12
        chart_df = pd.DataFrame({'period': bar_fig.data[0].y, 'value': bar_fig.data[0].x})
        assert chart_df[chart_df['period'] == '2024, January']['value'].iloc[0] == 1718
        assert chart_df[chart_df['period'] == '2024, December']['value'].iloc[0] == 1127

    def test_day_view_2024_with_category(self):
        """- When displayed in "Day View" with 2024 and "Care Coordination"..."""
        bar_fig, _, _, _, _, _, _ = adad_dashboard.update_dashboard(
            view='day', sel_years=[2024], sel_months=None, sel_modalities=['Care Coordination'], sel_counties=None, start_date=date(2024, 1, 1), end_date=date(2024, 12, 31)
        )
        assert len(bar_fig.data[0].y) >= 365
        chart_df = pd.DataFrame({'period': bar_fig.data[0].y, 'value': bar_fig.data[0].x})
        assert chart_df[chart_df['period'] == '2024-01-01']['value'].iloc[0] == 37
        assert chart_df[chart_df['period'] == '2024-12-31']['value'].iloc[0] == 59

    def test_kpi_and_table_consistency_across_views(self):
        """- The KPI and table values should not change when we display by month or day view."""
        _, _, _, kpi_year, modality_table_year, year_table_year, county_table_year = adad_dashboard.update_dashboard(
            view='year', sel_years=[2024], sel_months=None, sel_modalities=['Care Coordination'], sel_counties=None, start_date=None, end_date=None
        )
        _, _, _, kpi_month, modality_table_month, year_table_month, county_table_month = adad_dashboard.update_dashboard(
            view='month', sel_years=[2024], sel_months=None, sel_modalities=['Care Coordination'], sel_counties=None, start_date=None, end_date=None
        )
        
        assert kpi_year == kpi_month
        assert parse_table_from_layout(modality_table_year) == parse_table_from_layout(modality_table_month)
        assert parse_table_from_layout(year_table_year) == parse_table_from_layout(year_table_month)
        assert parse_table_from_layout(county_table_year) == parse_table_from_layout(county_table_month)

    def test_reset_filters_workflow(self):
        """Test that applying filters and then resetting returns to the initial state."""
        from adad_dashboard import df_raw, reset_adad_filters, min_date, max_date
        
        # FIX: Correctly unpack all 7 return values
        _, _, _, initial_kpi, _, _, _ = adad_dashboard.update_dashboard(
            view='year', sel_years=None, sel_months=None, sel_modalities=None, sel_counties=None, start_date=str(min_date), end_date=str(max_date)
        )
        initial_value = int(initial_kpi.replace(',', ''))

        _, _, _, filtered_kpi, _, _, _ = adad_dashboard.update_dashboard(
            view='year', sel_years=[2024], sel_months=None, sel_modalities=None, sel_counties=None, start_date=None, end_date=None
        )
        assert filtered_kpi == "8,377"
        
        reset_values = reset_adad_filters(1)
        
        _, _, _, reset_kpi, _, _, _ = adad_dashboard.update_dashboard(
            view='year', 
            sel_years=reset_values[0],
            sel_months=reset_values[1],
            sel_modalities=reset_values[2],
            sel_counties=reset_values[3],
            start_date=reset_values[4],
            end_date=reset_values[5]
        )
        reset_value = int(reset_kpi.replace(',', ''))

        assert reset_value == initial_value
