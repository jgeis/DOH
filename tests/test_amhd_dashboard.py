import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import plotly.graph_objects as go
from datetime import date

# This helper function will be used to parse the dbc.Table component for easier testing
def parse_table_from_layout(table_layout):
    """Parses a dbc.Table from a Dash layout to extract its data."""
    if not table_layout or not hasattr(table_layout, 'children'):
        return {}
    
    # The table is usually nested inside other components    
    header = [h.children for h in table_layout.children[0].children]
    body = table_layout.children[1].children
    
    data = {}
    for row in body:
        row_data = [cell.children for cell in row.children]
        # Create a dictionary mapping header to row value
        # e.g., {'Service Category': 'Contracted Providers', 'Number of AMHD Consumers': '5,201'}
        category = row_data[0]
        value = row_data[1]
        data[category] = value
        
    return data


class TestAMHDDashboard(unittest.TestCase):

    @patch('amhd_dashboard.load_sql_query')
    @patch('amhd_dashboard.execute_query')
    def setUp(self, mock_execute_query, mock_load_sql_query):
        """Set up mock dataframes to simulate database queries."""

        # --- Create Fixture Data Based on Provided Numbers ---

        # 1. Data for Year View (All Categories)
        self.mock_year_all = pd.DataFrame({
            'service_date': [date(2024, 1, 1)],
            'service_category': ['All'],
            'client_count': [9430]
        })

        # 2. Data for Year View (By Category)
        self.mock_year_categories = pd.DataFrame({
            'service_date': [date(2024, 1, 1)] * 3,
            'service_category': ['Contracted Providers', 'Community Mental Health Centers', 'Hawaii State Hospital'],
            'client_count': [5201, 4506, 801]
        })

        # 3. Data for Month View (All Categories)
        month_dates_all = pd.to_datetime([f'2024-{m}-01' for m in range(1, 13)])
        month_counts_all = [5004] + [0]*10 + [5794] # Jan, ..., Dec
        self.mock_month_all = pd.DataFrame({
            'service_date': month_dates_all,
            'service_category': ['All'] * 12,
            'client_count': month_counts_all
        })

        # 4. Data for Month View (By Category)
        month_dates_cat = pd.to_datetime([f'2024-{m}-01' for m in range(1, 13)])
        month_counts_cat = [1862] + [0]*10 + [1817] # Jan, ..., Dec
        self.mock_month_categories = pd.DataFrame({
            'service_date': month_dates_cat,
            'service_category': ['Contracted Providers'] * 12,
            'client_count': month_counts_cat
        })

        # 5. Data for Day View (By Category)
        day_dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        day_counts = [0] * 366 # 2024 is a leap year
        day_counts[0] = 685    # Jan 1st
        day_counts[-1] = 679   # Dec 31st
        self.mock_day_categories = pd.DataFrame({
            'service_date': day_dates,
            'service_category': ['Contracted Providers'] * 366,
            'client_count': day_counts
        })
        
        # 6. Data for KPI card (no filters)
        self.mock_kpi_total_df = pd.DataFrame({'client_count': [20000]})
        self.mock_kpi_category_df = self.mock_year_categories.copy()


        # --- Configure Mocks ---
        def execute_side_effect(sql):
            if "year_all" in sql: return self.mock_year_all
            if "month_all" in sql: return self.mock_month_all
            if "day_all" in sql: return pd.DataFrame() # Not needed for these tests
            if "year_categories" in sql: return self.mock_year_categories
            if "month_categories" in sql: return self.mock_month_categories
            if "day_categories" in sql: return self.mock_day_categories
            if "kpi_total" in sql: return self.mock_kpi_total_df
            return pd.DataFrame()

        mock_execute_query.side_effect = execute_side_effect
        mock_load_sql_query.side_effect = lambda name: name

        # --- Import the dashboard module AFTER patching ---
        from amhd_dashboard import update_dashboard, reset_amhd_filters
        self.update_dashboard = update_dashboard
        self.reset_amhd_filters = reset_amhd_filters

    def test_year_view_2024_no_category(self):
        """- When year view is displayed, and the year 2024 is selected, the KPI card should have the number 9,430..."""
        kpi, bar_fig, table = self.update_dashboard(
            view='year',
            sel_years=[2024],
            sel_service_categories=None
        )

        # Assert KPI
        self.assertEqual(kpi, "9,430")

        # Assert Bar Chart
        self.assertEqual(len(bar_fig.data[0].y), 1, "Bar chart should have only one bar")
        self.assertEqual(bar_fig.data[0].y[0], '2024', "Bar should be for the year 2024")
        self.assertEqual(bar_fig.data[0].x[0], 9430, "Bar value should be 9430")

        # Assert Table
        table_data = parse_table_from_layout(table)
        self.assertEqual(len(table_data), 3, "Table should have 3 rows")
        self.assertEqual(table_data.get('Contracted Providers'), '5,201')
        self.assertEqual(table_data.get('Community Mental Health Centers'), '4,506')
        self.assertEqual(table_data.get('Hawaii State Hospital'), '801')

    def test_month_view_2024_no_category(self):
        """- When displayed in "Month View" with the year 2024 selected, the bar chart should show 12 bars..."""
        kpi, bar_fig, table = self.update_dashboard(
            view='month',
            sel_years=[2024],
            sel_service_categories=None
        )

        # Assert Bar Chart
        self.assertEqual(len(bar_fig.data[0].y), 12, "Bar chart should have 12 bars for the months")
        
        # Find and assert specific month values
        chart_df = pd.DataFrame({'period': bar_fig.data[0].y, 'value': bar_fig.data[0].x})
        jan_val = chart_df[chart_df['period'] == '2024, January']['value'].iloc[0]
        dec_val = chart_df[chart_df['period'] == '2024, December']['value'].iloc[0]
        
        self.assertEqual(jan_val, 5004)
        self.assertEqual(dec_val, 5793)

    def test_year_view_2024_with_category(self):
        """- When displayed in "Year View" with the year 2024 selected and category "Contracted Providers"..."""
        kpi, bar_fig, table = self.update_dashboard(
            view='year',
            sel_years=[2024],
            sel_service_categories=['Contracted Providers']
        )

        # Assert KPI
        self.assertEqual(kpi, "5,201")

        # Assert Bar Chart
        self.assertEqual(len(bar_fig.data[0].y), 1, "Bar chart should have only one bar")
        self.assertEqual(bar_fig.data[0].y[0], '2024', "Bar should be for the year 2024")
        self.assertEqual(bar_fig.data[0].x[0], 5201, "Bar value should be 5201")

        # Assert Table (should still show all categories for the year)
        table_data = parse_table_from_layout(table)
        self.assertEqual(len(table_data), 3, "Table should still have 3 rows for context")
        self.assertEqual(table_data.get('Contracted Providers'), '5,201')
        self.assertEqual(table_data.get('Community Mental Health Centers'), '4,506')
        self.assertEqual(table_data.get('Hawaii State Hospital'), '801')

    def test_month_view_2024_with_category(self):
        """- When displayed in "Month View" with year 2024 and category "Contracted Providers"..."""
        kpi, bar_fig, table = self.update_dashboard(
            view='month',
            sel_years=[2024],
            sel_service_categories=['Contracted Providers']
        )

        # Assert Bar Chart
        self.assertEqual(len(bar_fig.data[0].y), 12, "Bar chart should have 12 bars")
        
        chart_df = pd.DataFrame({'period': bar_fig.data[0].y, 'value': bar_fig.data[0].x})
        jan_val = chart_df[chart_df['period'] == '2024, January']['value'].iloc[0]
        dec_val = chart_df[chart_df['period'] == '2024, December']['value'].iloc[0]
        
        self.assertEqual(jan_val, 1862)
        self.assertEqual(dec_val, 1817)

    def test_day_view_2024_with_category(self):
        """- When displayed in "Day View" with year 2024 and category "Contracted Providers"..."""
        kpi, bar_fig, table = self.update_dashboard(
            view='day',
            sel_years=[2024],
            sel_service_categories=['Contracted Providers']
        )

        # Assert Bar Chart
        self.assertEqual(len(bar_fig.data[0].y), 366, "Bar chart should have 366 bars for the leap year 2024")
        
        chart_df = pd.DataFrame({'period': bar_fig.data[0].y, 'value': bar_fig.data[0].x})
        jan1_val = chart_df[chart_df['period'] == '2024-01-01']['value'].iloc[0]
        dec31_val = chart_df[chart_df['period'] == '2024-12-31']['value'].iloc[0]
        
        self.assertEqual(jan1_val, 685)
        self.assertEqual(dec31_val, 679)

    def test_kpi_and_table_consistency_across_views(self):
        """- The KPI card number and the values on the table should not change when we display by month or day view..."""
        # Run for Year View
        kpi_year, _, table_year_layout = self.update_dashboard(
            view='year',
            sel_years=[2024],
            sel_service_categories=['Contracted Providers']
        )
        table_year_data = parse_table_from_layout(table_year_layout)

        # Run for Month View
        kpi_month, _, table_month_layout = self.update_dashboard(
            view='month',
            sel_years=[2024],
            sel_service_categories=['Contracted Providers']
        )
        table_month_data = parse_table_from_layout(table_month_layout)

        # Run for Day View
        kpi_day, _, table_day_layout = self.update_dashboard(
            view='day',
            sel_years=[2024],
            sel_service_categories=['Contracted Providers']
        )
        table_day_data = parse_table_from_layout(table_day_layout)

        # Assert KPI consistency
        self.assertEqual(kpi_year, kpi_month, "KPI should be consistent between Year and Month view")
        self.assertEqual(kpi_year, kpi_day, "KPI should be consistent between Year and Day view")

        # Assert Table consistency
        self.assertDictEqual(table_year_data, table_month_data, "Table data should be consistent between Year and Month view")
        self.assertDictEqual(table_year_data, table_day_data, "Table data should be consistent between Year and Day view")

    def test_reset_filters_returns_correct_values(self):
        """Test that the reset button callback returns None for all filters."""
        # The _n_clicks argument is not used, so we can pass any value (e.g., 1)
        result = self.reset_amhd_filters(1)
        
        # The callback should return a tuple of two None values
        self.assertEqual(result, (None, None), "Reset callback should return (None, None)")

    def test_reset_filters_workflow(self):
        """Test that applying filters and then resetting returns to a larger, unfiltered state."""
        # 1. Apply a filter and confirm the state changes to the specific filtered value.
        kpi_filtered, _, _ = self.update_dashboard(
            view='year',
            sel_years=[2024],
            sel_service_categories=None
        )
        self.assertEqual(kpi_filtered, "9,430")
        
        # Convert to a number for comparison
        filtered_value = int(kpi_filtered.replace(',', ''))

        # 2. Get the reset values from the reset callback
        year_reset, category_reset = self.reset_amhd_filters(1)
        self.assertIsNone(year_reset)
        self.assertIsNone(category_reset)

        # 3. Apply the reset values to the main callback to get the unfiltered state
        kpi_after_reset, _, _ = self.update_dashboard(
            view='year',
            sel_years=year_reset,
            sel_service_categories=category_reset
        )
        
        # Convert to a number for comparison
        unfiltered_value = int(kpi_after_reset.replace(',', ''))

        # 4. Confirm the unfiltered state is larger than the filtered state
        self.assertGreater(unfiltered_value, filtered_value, "Unfiltered KPI should be greater than the filtered KPI")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
