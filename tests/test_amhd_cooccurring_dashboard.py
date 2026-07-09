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
    
    body = table_layout.children[1].children
    
    data = {}
    for row in body:
        row_data = [cell.children for cell in row.children]
        category = row_data[0]
        value = row_data[1]
        data[category] = value
        
    return data


class TestAMHDCooccurringDashboard(unittest.TestCase):

    @patch('amhd_cooccurring_dashboard.load_sql_query')
    @patch('amhd_cooccurring_dashboard.execute_query')
    def setUp(self, mock_execute_query, mock_load_sql_query):
        """Set up mock dataframes to simulate loading pre-aggregated data."""

        # --- Fixture Data ---
        self.mock_unfiltered_total = pd.DataFrame({'consumer_count': [15000]})
        self.mock_year_total = pd.DataFrame({'total_consumers': [2168]})
        self.mock_year_view_all_cats = pd.DataFrame({'service_date': [date(2024, 1, 1)], 'service_category': ['All'], 'consumer_count': [2168]})
        self.mock_year_categories = pd.DataFrame({
            'service_date': [date(2024, 1, 1)] * 3,
            'service_category': ['Contracted Providers', 'Community Mental Health Centers', 'Hawaii State Hospital'],
            'consumer_count': [1119, 1071, 685]
        })
        month_dates_all = pd.to_datetime([f'2024-{m}-01' for m in range(1, 13)])
        month_counts_all = [1624] + [1000]*10 + [1656]
        self.mock_month_all = pd.DataFrame({'service_date': month_dates_all, 'service_category': ['All'] * 12, 'consumer_count': month_counts_all})
        self.mock_year_total_filtered = pd.DataFrame({'total_consumers': [1119]})
        self.mock_year_view_filtered = pd.DataFrame({'service_date': [date(2024, 1, 1)], 'service_category': ['Contracted Providers'], 'consumer_count': [1119]})
        month_dates_cat = pd.to_datetime([f'2024-{m}-01' for m in range(1, 13)])
        month_counts_cat = [633] + [500]*10 + [630]
        self.mock_month_categories = pd.DataFrame({'service_date': month_dates_cat, 'service_category': ['Contracted Providers'] * 12, 'consumer_count': month_counts_cat})
        day_dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        day_counts = [100] * 366
        day_counts[0] = 353
        day_counts[-1] = 341
        self.mock_day_categories = pd.DataFrame({'service_date': day_dates, 'service_category': ['Contracted Providers'] * 366, 'consumer_count': day_counts})
        self.mock_kpi_total_df = pd.DataFrame({'consumer_count': [20000]})
        self.mock_kpi_category_df = self.mock_year_categories.copy()

        # --- Configure Mocks ---
        def execute_side_effect(sql):
            if "year_all" in sql: return self.mock_year_all.copy()
            if "month_all" in sql: return self.mock_month_all.copy()
            if "day_all" in sql: return pd.DataFrame()
            if "year_categories" in sql: return self.mock_year_categories.copy()
            if "month_categories" in sql: return self.mock_month_categories.copy()
            if "day_categories" in sql: return self.mock_day_categories.copy()
            if "kpi_total" in sql: return self.mock_kpi_total_df.copy()
            return pd.DataFrame()

        mock_execute_query.side_effect = execute_side_effect
        mock_load_sql_query.side_effect = lambda name: name

        # --- Import the dashboard module AFTER patching ---
        # Import the simple reset function first
        from amhd_cooccurring_dashboard import reset_amhd_cooccurring_filters
        self.reset_amhd_cooccurring_filters = reset_amhd_cooccurring_filters

        # Then, patch the KPI total and import the main update function
        with patch('amhd_cooccurring_dashboard.amhd_cooccurring_kpi_total', 20000):
            from amhd_cooccurring_dashboard import update_dashboard
            self.update_dashboard = update_dashboard

    def test_year_view_2024_no_category(self):
        kpi, bar_fig, table = self.update_dashboard(view='year', sel_years=[2024], sel_service_categories=None)
        self.assertEqual(kpi, "2,168")
        self.assertEqual(len(bar_fig.data[0].y), 1)
        table_data = parse_table_from_layout(table)
        self.assertEqual(len(table_data), 3)
        self.assertEqual(table_data.get('Contracted Providers'), '1,119')

    def test_month_view_2024_no_category(self):
        kpi, bar_fig, table = self.update_dashboard(view='month', sel_years=[2024], sel_service_categories=None)
        self.assertEqual(len(bar_fig.data[0].y), 12)
        chart_df = pd.DataFrame({'period': bar_fig.data[0].y, 'value': bar_fig.data[0].x})
        self.assertEqual(chart_df[chart_df['period'] == '2024, January']['value'].iloc[0], 1624)

    def test_year_view_2024_with_category(self):
        kpi, bar_fig, table = self.update_dashboard(view='year', sel_years=[2024], sel_service_categories=['Contracted Providers'])
        self.assertEqual(kpi, "1,119")
        self.assertEqual(len(bar_fig.data[0].y), 1)
        table_data = parse_table_from_layout(table)
        self.assertEqual(table_data.get('Contracted Providers'), '1,119')

    def test_month_view_2024_with_category(self):
        kpi, bar_fig, table = self.update_dashboard(view='month', sel_years=[2024], sel_service_categories=['Contracted Providers'])
        self.assertEqual(len(bar_fig.data[0].y), 12)
        chart_df = pd.DataFrame({'period': bar_fig.data[0].y, 'value': bar_fig.data[0].x})
        self.assertEqual(chart_df[chart_df['period'] == '2024, January']['value'].iloc[0], 633)

    def test_day_view_2024_with_category(self):
        kpi, bar_fig, table = self.update_dashboard(view='day', sel_years=[2024], sel_service_categories=['Contracted Providers'])
        self.assertEqual(len(bar_fig.data[0].y), 366)
        chart_df = pd.DataFrame({'period': bar_fig.data[0].y, 'value': bar_fig.data[0].x})
        self.assertEqual(chart_df[chart_df['period'] == '2024-01-01']['value'].iloc[0], 353)

    def test_kpi_and_table_consistency_across_views(self):
        kpi_year, _, table_year_layout = self.update_dashboard(view='year', sel_years=[2024], sel_service_categories=['Contracted Providers'])
        table_year_data = parse_table_from_layout(table_year_layout)
        kpi_month, _, table_month_layout = self.update_dashboard(view='month', sel_years=[2024], sel_service_categories=['Contracted Providers'])
        table_month_data = parse_table_from_layout(table_month_layout)
        self.assertEqual(kpi_year, kpi_month)
        self.assertDictEqual(table_year_data, table_month_data)

    def test_reset_filters_returns_correct_values(self):
        """Test that the reset button callback returns None for all filters."""
        result = self.reset_amhd_cooccurring_filters(1)
        self.assertEqual(result, (None, None), "Reset callback should return (None, None)")

    def test_reset_filters_workflow(self):
        """Test that applying filters and then resetting returns to a larger, unfiltered state."""
        # 1. Arrange: Apply a filter and confirm the state changes.
        kpi_filtered, _, _ = self.update_dashboard(view='year', sel_years=[2024], sel_service_categories=None)
        self.assertEqual(kpi_filtered, "2,168")
        filtered_value = int(kpi_filtered.replace(',', ''))

        # 2. Act: Simulate the reset button click.
        year_reset, category_reset = self.reset_amhd_cooccurring_filters(1)
        
        # 3. Assert: Check that the reset values are correct.
        self.assertIsNone(year_reset)
        self.assertIsNone(category_reset)

        # 4. Act: Apply the reset values to the main callback to get the unfiltered state.
        kpi_after_reset, _, _ = self.update_dashboard(view='year', sel_years=year_reset, sel_service_categories=category_reset)
        
        # 5. Assert: Confirm the state has returned to a larger, unfiltered value.
        unfiltered_value = int(kpi_after_reset.replace(',', ''))
        self.assertGreater(unfiltered_value, filtered_value, "Unfiltered KPI should be greater than the filtered KPI")


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
