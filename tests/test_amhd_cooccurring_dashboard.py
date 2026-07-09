import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import plotly.graph_objects as go
from datetime import date

# Helper function to parse the dbc.Table component for easier testing
def parse_table_from_layout(table_layout):
    """Parses a dbc.Table from a Dash layout to extract its data."""
    if not table_layout or not hasattr(table_layout, 'children'):
        return {}
    
    table = table_layout.children[0]
    body = table.children[1].children
    
    data = {}
    for row in body:
        row_data = [cell.children for cell in row.children]
        category = row_data[0]
        value = row_data[1]
        data[category] = value
        
    return data


class TestAMHDCooccurringDashboard(unittest.TestCase):

    @patch('amhd_cooccurring_dashboard._run_named_amhd_cooccurring_query')
    def setUp(self, mock_run_query):
        """Set up mock dataframes to simulate database queries."""

        # --- Fixture Data ---
        # This data is configured to be returned by the mocked query runner
        # based on the query name and filter context.

        # Data for Year View (All Categories)
        self.mock_year_total = pd.DataFrame({'total_consumers': [2168]})
        self.mock_year_view_all_cats = pd.DataFrame({'year': [2024], 'consumer_count': [2168]})
        self.mock_year_table_data = pd.DataFrame({
            'service_category': ['Contracted Providers', 'Community Mental Health Centers', 'Hawaii State Hospital'],
            'consumer_count': [1119, 1071, 685]
        })

        # Data for Month View (All Categories)
        month_dates_all = pd.to_datetime([f'2024-{m}-01' for m in range(1, 13)])
        month_counts_all = [1624] + [1000]*10 + [1656] # Jan, ..., Dec
        self.mock_month_view_all_cats = pd.DataFrame({
            'period_date': month_dates_all,
            'consumer_count': month_counts_all
        })

        # Data for Year View (Filtered by Category)
        self.mock_year_total_filtered = pd.DataFrame({'total_consumers': [1119]})
        self.mock_year_view_filtered = pd.DataFrame({'year': [2024], 'consumer_count': [1119]})

        # Data for Month View (Filtered by Category)
        month_dates_cat = pd.to_datetime([f'2024-{m}-01' for m in range(1, 13)])
        month_counts_cat = [633] + [500]*10 + [630] # Jan, ..., Dec
        self.mock_month_view_filtered = pd.DataFrame({
            'period_date': month_dates_cat,
            'consumer_count': month_counts_cat
        })

        # Data for Day View (Filtered by Category)
        day_dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        day_counts = [100] * 366 # 2024 is a leap year
        day_counts[0] = 353    # Jan 1st
        day_counts[-1] = 341   # Dec 31st
        self.mock_day_view_filtered = pd.DataFrame({
            'service_date': day_dates,
            'consumer_count': day_counts
        })

        # --- Configure Mock ---
        def query_side_effect(query_name, context):
            is_filtered_by_cat = 'Contracted Providers' in context.get('service_categories_key', ())
            
            if query_name == "load_amhd_cooccurring_consumers_total":
                return self.mock_year_total_filtered if is_filtered_by_cat else self.mock_year_total
            
            if query_name == "load_amhd_cooccurring_consumers_by_year":
                return self.mock_year_view_filtered if is_filtered_by_cat else self.mock_year_view_all_cats
            
            if query_name == "load_amhd_cooccurring_consumers_by_month":
                return self.mock_month_view_filtered if is_filtered_by_cat else self.mock_month_view_all_cats
                
            if query_name == "load_amhd_cooccurring_consumers_by_date":
                return self.mock_day_view_filtered # Only tested with category filter
            
            if query_name == "load_amhd_cooccurring_consumers_by_service_category":
                return self.mock_year_table_data # Table data is consistent

            return pd.DataFrame()

        mock_run_query.side_effect = query_side_effect

        # --- Import the dashboard module AFTER patching ---
        from amhd_cooccurring_dashboard import update_amhd_kpi, update_amhd_figures, update_amhd_tables, reset_amhd_filters
        self.update_amhd_kpi = update_amhd_kpi
        self.update_amhd_figures = update_amhd_figures
        self.update_amhd_tables = update_amhd_tables
        self.reset_amhd_filters = reset_amhd_filters

    def test_year_view_2024_no_category(self):
        """- When year view is displayed, and the year 2024 is selected, the KPI card should have the number 2,168..."""
        kpi = self.update_amhd_kpi(sel_years=[2024], sel_service_categories=None, start_date=None, end_date=None)
        bar_fig = self.update_amhd_figures(view='year', sel_years=[2024], sel_service_categories=None, start_date=None, end_date=None)
        table = self.update_amhd_tables(sel_years=[2024], sel_service_categories=None, start_date=None, end_date=None)

        # Assert KPI
        self.assertEqual(kpi, "2,168")

        # Assert Bar Chart
        self.assertEqual(len(bar_fig.data[0].y), 1, "Bar chart should have only one bar")
        self.assertEqual(bar_fig.data[0].y[0], '2024', "Bar should be for the year 2024")
        self.assertEqual(bar_fig.data[0].x[0], 2168, "Bar value should be 2168")

        # Assert Table
        table_data = parse_table_from_layout(table)
        self.assertEqual(len(table_data), 3, "Table should have 3 rows")
        self.assertEqual(table_data.get('Contracted Providers'), '1,119')
        self.assertEqual(table_data.get('Community Mental Health Centers'), '1,071')
        self.assertEqual(table_data.get('Hawaii State Hospital'), '685')

    def test_month_view_2024_no_category(self):
        """- When displayed in "Month View" with the year 2024 selected, the bar chart should show 12 bars..."""
        bar_fig = self.update_amhd_figures(view='month', sel_years=[2024], sel_service_categories=None, start_date=None, end_date=None)

        # Assert Bar Chart
        self.assertEqual(len(bar_fig.data[0].y), 12, "Bar chart should have 12 bars for the months")
        
        chart_df = pd.DataFrame({'period': bar_fig.data[0].y, 'value': bar_fig.data[0].x})
        jan_val = chart_df[chart_df['period'] == '2024, January']['value'].iloc[0]
        dec_val = chart_df[chart_df['period'] == '2024, December']['value'].iloc[0]
        
        self.assertEqual(jan_val, 1624)
        self.assertEqual(dec_val, 1656)

    def test_year_view_2024_with_category(self):
        """- When displayed in "Year View" with the year 2024 selected and category "Contracted Providers"..."""
        kpi = self.update_amhd_kpi(sel_years=[2024], sel_service_categories=['Contracted Providers'], start_date=None, end_date=None)
        bar_fig = self.update_amhd_figures(view='year', sel_years=[2024], sel_service_categories=['Contracted Providers'], start_date=None, end_date=None)
        table = self.update_amhd_tables(sel_years=[2024], sel_service_categories=['Contracted Providers'], start_date=None, end_date=None)

        # Assert KPI
        self.assertEqual(kpi, "1,119")

        # Assert Bar Chart
        self.assertEqual(len(bar_fig.data[0].y), 1, "Bar chart should have only one bar")
        self.assertEqual(bar_fig.data[0].y[0], '2024', "Bar should be for the year 2024")
        self.assertEqual(bar_fig.data[0].x[0], 1119, "Bar value should be 1119")

        # Assert Table
        table_data = parse_table_from_layout(table)
        self.assertEqual(len(table_data), 3, "Table should still have 3 rows for context")
        self.assertEqual(table_data.get('Contracted Providers'), '1,119')
        self.assertEqual(table_data.get('Community Mental Health Centers'), '1,071')
        self.assertEqual(table_data.get('Hawaii State Hospital'), '685')

    def test_month_view_2024_with_category(self):
        """- When displayed in "Month View" with year 2024 and category "Contracted Providers"..."""
        bar_fig = self.update_amhd_figures(view='month', sel_years=[2024], sel_service_categories=['Contracted Providers'], start_date=None, end_date=None)

        # Assert Bar Chart
        self.assertEqual(len(bar_fig.data[0].y), 12, "Bar chart should have 12 bars")
        
        chart_df = pd.DataFrame({'period': bar_fig.data[0].y, 'value': bar_fig.data[0].x})
        jan_val = chart_df[chart_df['period'] == '2024, January']['value'].iloc[0]
        dec_val = chart_df[chart_df['period'] == '2024, December']['value'].iloc[0]
        
        self.assertEqual(jan_val, 633)
        self.assertEqual(dec_val, 630)

    def test_day_view_2024_with_category(self):
        """- When displayed in "Day View" with year 2024 and category "Contracted Providers"..."""
        bar_fig = self.update_amhd_figures(view='day', sel_years=[2024], sel_service_categories=['Contracted Providers'], start_date=None, end_date=None)

        # Assert Bar Chart
        self.assertEqual(len(bar_fig.data[0].y), 366, "Bar chart should have 366 bars for the leap year 2024")
        
        chart_df = pd.DataFrame({'period': bar_fig.data[0].y, 'value': bar_fig.data[0].x})
        jan1_val = chart_df[chart_df['period'] == '2024-01-01']['value'].iloc[0]
        dec31_val = chart_df[chart_df['period'] == '2024-12-31']['value'].iloc[0]
        
        self.assertEqual(jan1_val, 353)
        self.assertEqual(dec31_val, 341)

    def test_kpi_and_table_consistency_across_views(self):
        """- The KPI card number and the values on the table should not change when we display by month or day view..."""
        # Run for Year View
        kpi_year = self.update_amhd_kpi(sel_years=[2024], sel_service_categories=['Contracted Providers'], start_date=None, end_date=None)
        table_year_layout = self.update_amhd_tables(sel_years=[2024], sel_service_categories=['Contracted Providers'], start_date=None, end_date=None)
        table_year_data = parse_table_from_layout(table_year_layout)

        # Run for Month View
        kpi_month = self.update_amhd_kpi(sel_years=[2024], sel_service_categories=['Contracted Providers'], start_date=None, end_date=None)
        table_month_layout = self.update_amhd_tables(sel_years=[2024], sel_service_categories=['Contracted Providers'], start_date=None, end_date=None)
        table_month_data = parse_table_from_layout(table_month_layout)

        # Run for Day View
        kpi_day = self.update_amhd_kpi(sel_years=[2024], sel_service_categories=['Contracted Providers'], start_date=None, end_date=None)
        table_day_layout = self.update_amhd_tables(sel_years=[2024], sel_service_categories=['Contracted Providers'], start_date=None, end_date=None)
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
        self.assertEqual(kpi_filtered, "2,168")
                
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
