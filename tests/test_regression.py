"""
Regression test suite for DOH Plotly Dashboard system.

This module contains tests that verify critical functionality continues to work
across code changes. These tests capture known behavior patterns and edge cases
to prevent regressions.

Tests are organized by functional area:
- Data integrity and consistency
- Count suppression logic
- Filter behavior
- Visualization rendering
- Database queries
- Critical user workflows
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, Mock
import plotly.graph_objects as go


@pytest.mark.regression
class TestCountSuppressionRegression:
    """
    Regression tests for count suppression logic.
    
    Critical behavior: Counts below threshold must be suppressed in all contexts
    to protect individual privacy while maintaining data utility.
    """
    
    def test_threshold_boundary_behavior(self):
        """
        Regression: Verify exact threshold behavior.
        
        Historical bug: Threshold value itself was sometimes suppressed.
        Expected: Values at threshold should NOT be suppressed.
        """
        from dashboard_utils import format_count_display, COUNT_SUPPRESSION_THRESHOLD
        
        # At threshold: should show
        assert format_count_display(COUNT_SUPPRESSION_THRESHOLD) == str(COUNT_SUPPRESSION_THRESHOLD)
        
        # Just below threshold: should suppress
        assert format_count_display(COUNT_SUPPRESSION_THRESHOLD - 1) != str(COUNT_SUPPRESSION_THRESHOLD - 1)
        
        # Just above threshold: should show
        result = format_count_display(COUNT_SUPPRESSION_THRESHOLD + 1)
        assert str(COUNT_SUPPRESSION_THRESHOLD + 1) in result
    
    def test_suppression_consistency_across_functions(self):
        """
        Regression: Ensure suppression logic is consistent across all display functions.
        
        Historical issue: Different functions had slightly different suppression logic.
        """
        from dashboard_utils import (
            format_count_display,
            build_suppressed_bar_count_columns,
            SUPPRESSED_COUNT_LABEL
        )
        
        test_value = 5  # Below threshold
        
        # Direct formatting
        direct_result = format_count_display(test_value)
        assert direct_result == SUPPRESSED_COUNT_LABEL
        
        # Bar column building
        plot_vals, display_vals, mask = build_suppressed_bar_count_columns([test_value])
        assert plot_vals[0] == 0
        assert display_vals[0] == SUPPRESSED_COUNT_LABEL
        assert mask[0] is True
    
    def test_zero_count_suppression(self):
        """
        Regression: Verify zero counts are suppressed.
        
        Historical behavior: Zeros should be suppressed to prevent
        revealing absence of cases in small populations.
        """
        from dashboard_utils import format_count_display, SUPPRESSED_COUNT_LABEL
        
        assert format_count_display(0) == SUPPRESSED_COUNT_LABEL
    
    def test_percentage_suppression_when_count_suppressed(self):
        """
        Regression: Percentages must be hidden when underlying count is suppressed.
        
        Critical privacy requirement: Showing percentages for suppressed counts
        can allow reverse calculation of suppressed values.
        """
        from dashboard_utils import format_percentage_display
        
        # High percentage but low count should suppress percentage
        result = format_percentage_display(90.0, count_value=5)
        assert result == ""
        
        # Same percentage with high count should show
        result = format_percentage_display(90.0, count_value=100)
        assert "90" in result


@pytest.mark.regression
class TestStatewideAggregationRegression:
    """
    Regression tests for statewide aggregation logic.
    
    Critical behavior: Statewide totals must correctly sum county-level data
    and handle special filtering rules.
    """
    
    def test_statewide_sum_accuracy(self):
        """
        Regression: Verify statewide aggregation sums correctly.
        
        Historical bug: Some groupings were double-counting or missing counties.
        """
        from dashboard_utils import append_statewide_aggregate_rows, STATEWIDE_COUNTY
        
        df = pd.DataFrame({
            'county': ['Honolulu', 'Maui', 'Hawaii', 'Kauai'],
            'count': [100, 50, 75, 25]
        })
        
        result = append_statewide_aggregate_rows(df, value_col='count')
        
        statewide_row = result[result['county'] == STATEWIDE_COUNTY]
        assert len(statewide_row) == 1
        assert statewide_row['count'].iloc[0] == 250  # Sum of all counties
    
    def test_statewide_filter_shows_all_data(self):
        """
        Regression: Selecting "Statewide" should show all county data.
        
        Historical issue: Statewide selection was sometimes treated as
        a specific county, returning no results.
        """
        from dashboard_utils import apply_county_filter, STATEWIDE_COUNTY
        
        df = pd.DataFrame({
            'county': ['Honolulu', 'Maui', 'Hawaii'],
            'value': [1, 2, 3]
        })
        
        result = apply_county_filter(df, STATEWIDE_COUNTY)
        assert len(result) == 3  # All counties
    
    def test_statewide_with_multiple_groupings(self):
        """
        Regression: Statewide aggregation with multiple grouping columns.
        
        Historical bug: Adding statewide rows broke when multiple grouping
        columns (e.g., year + substance) were present.
        """
        from dashboard_utils import append_statewide_aggregate_rows, STATEWIDE_COUNTY
        
        df = pd.DataFrame({
            'county': ['Honolulu', 'Maui', 'Honolulu', 'Maui'],
            'year': [2020, 2020, 2021, 2021],
            'count': [100, 50, 120, 60]
        })
        
        result = append_statewide_aggregate_rows(df, value_col='count')
        
        # Should have statewide row for each year
        statewide = result[result['county'] == STATEWIDE_COUNTY]
        assert len(statewide) == 2
        
        # Verify correct sums
        sw_2020 = statewide[statewide['year'] == 2020]['count'].iloc[0]
        sw_2021 = statewide[statewide['year'] == 2021]['count'].iloc[0]
        assert sw_2020 == 150
        assert sw_2021 == 180


@pytest.mark.regression
class TestSortingRegression:
    """
    Regression tests for sorting logic.
    
    Critical behavior: Age groups, years, and Unknown values must sort correctly
    in dropdowns and charts.
    """
    
    def test_age_group_sorting_order(self):
        """
        Regression: Age groups must sort numerically, not alphabetically.
        
        Historical bug: "18-25" would come after "35-44" alphabetically.
        """
        from dashboard_utils import sort_opts
        
        ages = ["45+", "18-25", "0-17", "65+", "26-34", "35-44", "Unknown"]
        result = sort_opts(ages)
        
        # Should be in numeric order
        assert result.index("0-17") < result.index("18-25")
        assert result.index("18-25") < result.index("26-34")
        assert result.index("26-34") < result.index("35-44")
        assert result.index("35-44") < result.index("45+")
        
        # Unknown should be last
        assert result[-1] == "Unknown"
    
    def test_year_sorting_descending(self):
        """
        Regression: Years should sort in descending order (newest first).
        
        Historical behavior: Users expect most recent year at top of dropdown.
        """
        from dashboard_utils import sort_opts
        
        years = ["2019", "2021", "2020", "2022", "Unknown"]
        result = sort_opts(years)
        
        # Should be descending
        assert result == ["2022", "2021", "2020", "2019", "Unknown"]
    
    def test_unknown_always_last(self):
        """
        Regression: "Unknown" values should always sort to the end.
        
        Historical bug: Unknown would sometimes sort alphabetically into the middle.
        """
        from dashboard_utils import sort_opts
        
        # Test with regular strings
        values = ["Apple", "Unknown", "Banana", "Cherry"]
        result = sort_opts(values)
        assert result[-1] == "Unknown"
        
        # Test with age ranges
        ages = ["Unknown", "18-25", "26-34"]
        result = sort_opts(ages)
        assert result[-1] == "Unknown"


@pytest.mark.regression
class TestFilterLabelConsistency:
    """
    Regression tests for filter label standardization.
    
    Critical behavior: Filter labels must be consistent across all dashboards
    to avoid user confusion.
    """
    
    def test_sex_label_standardization(self):
        """
        Regression: Sex/Gender labels must standardize to "Sex at Birth".
        
        Historical issue: Mixed use of "Sex", "Gender", "Sex at Birth" across pages.
        """
        from dashboard_utils import get_standard_filter_label
        
        assert get_standard_filter_label("sex") == "Sex at Birth"
        assert get_standard_filter_label("Sex") == "Sex at Birth"
        assert get_standard_filter_label("Gender") == "Sex at Birth"
        assert get_standard_filter_label("sex_at_birth") == "Sex at Birth"
    
    def test_year_label_standardization(self):
        """
        Regression: Year labels must standardize to "Calendar Year".
        """
        from dashboard_utils import get_standard_filter_label
        
        assert get_standard_filter_label("Year") == "Calendar Year"
        assert get_standard_filter_label("year") == "Calendar Year"
    
    def test_substance_label_standardization(self):
        """
        Regression: Substance labels should standardize consistently.
        """
        from dashboard_utils import get_standard_filter_label
        
        assert get_standard_filter_label("Substance") == "Substance Type"


@pytest.mark.regression
class TestDatabaseQueryRegression:
    """
    Regression tests for database query execution.
    
    Critical behavior: Database operations must handle errors gracefully
    and work with both SQLite and MSSQL.
    """
    
    @patch('db_utils.USE_MSSQL', False)
    @patch('db_utils.get_connection')
    def test_query_empty_result_handling(self, mock_get_connection):
        """
        Regression: Empty query results should return empty DataFrame, not error.
        
        Historical bug: Some queries would crash instead of returning empty results.
        """
        from db_utils import execute_query
        
        # Mock empty result
        mock_conn = Mock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_get_connection.return_value = mock_conn
        
        with patch('pandas.read_sql_query', return_value=pd.DataFrame()):
            result = execute_query("SELECT * FROM table WHERE 1=0")
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
    
    @patch('db_utils.USE_MSSQL', False)
    @patch('db_utils.SQLITE_DB_PATH', ':memory:')
    def test_sqlite_date_functions_work(self):
        """
        Regression: Custom SQLite date functions must be registered.
        
        Historical bug: YEAR(), MONTH(), DAY() functions would fail in SQLite.
        """
        from db_utils import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create test table
        cursor.execute("CREATE TABLE test (date_col TEXT)")
        cursor.execute("INSERT INTO test VALUES ('2020-06-15')")
        
        # These functions must work
        cursor.execute("SELECT YEAR(date_col) FROM test")
        assert cursor.fetchone()[0] == 2020
        
        conn.close()


@pytest.mark.regression
class TestVisualizationRegression:
    """
    Regression tests for chart and visualization generation.
    
    Critical behavior: Charts must render correctly with suppressed data
    and handle edge cases.
    """
    
    def test_horizontal_bar_suppression_zeroing(self):
        """
        Regression: Suppressed bars must have zero length to prevent visual leakage.
        
        Historical bug: Suppressed values would show as small bars, revealing counts.
        """
        from dashboard_utils import apply_suppressed_horizontal_bar_display
        
        # Create a simple bar chart
        fig = go.Figure(data=[
            go.Bar(x=[5, 15, 8, 100], y=['A', 'B', 'C', 'D'], orientation='h')
        ])
        
        result = apply_suppressed_horizontal_bar_display(fig)
        
        # Check that suppressed values (5, 8) are zeroed
        trace = result.data[0]
        x_values = list(trace.x)
        assert x_values[0] == 0  # 5 suppressed
        assert x_values[1] == 15  # 15 shown
        assert x_values[2] == 0  # 8 suppressed
        assert x_values[3] == 100  # 100 shown
    
    def test_percentage_plot_suppression(self):
        """
        Regression: Percentage charts must suppress values when counts are low.
        """
        from dashboard_utils import build_suppressed_percentage_columns
        
        percentages = [25.0, 50.0, 10.0]
        counts = [100, 5, 200]  # Middle count is suppressed
        
        plot_vals, display_vals, mask = build_suppressed_percentage_columns(
            percentages, count_values=counts
        )
        
        # Middle value should be suppressed
        assert plot_vals[1] == 0.0
        assert display_vals[1] == ""
        assert mask[1] is True


@pytest.mark.regression
class TestCriticalUserWorkflows:
    """
    Regression tests for complete user workflows.
    
    These tests verify end-to-end functionality that users depend on.
    """
    
    def test_county_filter_to_chart_workflow(self, sample_dataframe):
        """
        Regression: County filtering should flow through to chart data correctly.
        
        Critical workflow: User selects county → data filters → chart updates.
        """
        from dashboard_utils import apply_county_filter
        
        # User selects Honolulu
        filtered = apply_county_filter(sample_dataframe, "Honolulu")
        assert len(filtered) == 1
        assert all(filtered['county'] == 'Honolulu')
        
        # User selects multiple counties
        filtered = apply_county_filter(sample_dataframe, ["Honolulu", "Maui"])
        assert len(filtered) == 2
        assert set(filtered['county']) == {'Honolulu', 'Maui'}
    
    def test_data_to_suppressed_table_workflow(self, sample_dataframe_with_suppression):
        """
        Regression: Data should flow through suppression logic to tables correctly.
        
        Critical workflow: Raw data → suppression → formatted display.
        """
        from dashboard_utils import format_count_display
        
        df = sample_dataframe_with_suppression
        
        # Apply formatting
        df['count_display'] = df['count'].apply(format_count_display)
        
        # Check suppression applied correctly
        assert df[df['count'] == 8]['count_display'].iloc[0] == "<10*"
        assert df[df['count'] == 25]['count_display'].iloc[0] == "25"


@pytest.mark.regression
class TestEdgeCasesAndBoundaries:
    """
    Regression tests for known edge cases and boundary conditions.
    """
    
    def test_empty_dataframe_operations(self):
        """
        Regression: Operations on empty DataFrames should not crash.
        """
        from dashboard_utils import (
            apply_county_filter,
            append_statewide_aggregate_rows
        )
        
        empty_df = pd.DataFrame()
        
        # Should not crash
        result = apply_county_filter(empty_df, "Honolulu")
        assert result.empty
        
        result = append_statewide_aggregate_rows(empty_df, value_col='count')
        assert result.empty
    
    def test_single_row_operations(self):
        """
        Regression: Operations on single-row DataFrames.
        """
        from dashboard_utils import append_statewide_aggregate_rows
        
        single_row = pd.DataFrame({
            'county': ['Honolulu'],
            'count': [100]
        })
        
        result = append_statewide_aggregate_rows(single_row, value_col='count')
        assert len(result) == 2  # Original + statewide
    
    def test_all_values_suppressed(self):
        """
        Regression: Handle case where all values are below threshold.
        """
        from dashboard_utils import build_suppressed_bar_count_columns, SUPPRESSED_COUNT_LABEL
        
        values = [1, 2, 3, 4, 5]  # All below threshold
        
        plot_vals, display_vals, mask = build_suppressed_bar_count_columns(values)
        
        # All should be suppressed
        assert all(plot_vals == 0)
        assert all(display_vals == SUPPRESSED_COUNT_LABEL)
        assert all(mask)
    
    def test_unicode_handling_throughout(self):
        """
        Regression: Hawaiian unicode characters should work throughout system.
        """
        from dashboard_utils import (
            with_statewide_county,
            apply_county_filter,
            format_display_list
        )
        
        counties = ["Hawaiʻi", "O'ahu", "Maui"]
        
        # Should work in filter operations
        result = with_statewide_county(counties)
        assert "Hawaiʻi" in result
        
        # Should work in display
        result = format_display_list(counties)
        assert "Hawaiʻi" in result
    
    def test_very_large_numbers(self):
        """
        Regression: Very large counts should format correctly.
        """
        from dashboard_utils import format_count_display
        
        assert format_count_display(1000000) == "1,000,000"
        assert format_count_display(999999999) == "999,999,999"
    
    def test_null_and_none_handling(self):
        """
        Regression: NULL/None values should be handled gracefully.
        """
        from dashboard_utils import format_count_display, SUPPRESSED_COUNT_LABEL
        
        assert format_count_display(None) == SUPPRESSED_COUNT_LABEL
        assert format_count_display(np.nan) == SUPPRESSED_COUNT_LABEL
        
        # In DataFrames
        df = pd.DataFrame({'count': [None, np.nan, 100]})
        results = df['count'].apply(format_count_display)
        assert results.iloc[0] == SUPPRESSED_COUNT_LABEL
        assert results.iloc[1] == SUPPRESSED_COUNT_LABEL
        assert "100" in results.iloc[2]


@pytest.mark.regression
@pytest.mark.slow
class TestPerformanceRegression:
    """
    Regression tests to catch performance degradation.
    """
    
    def test_large_dataframe_filtering_performance(self):
        """
        Regression: County filtering should be fast even with large datasets.
        """
        from dashboard_utils import apply_county_filter
        import time
        
        # Create large DataFrame
        large_df = pd.DataFrame({
            'county': ['Honolulu'] * 10000 + ['Maui'] * 10000,
            'value': range(20000)
        })
        
        start = time.time()
        result = apply_county_filter(large_df, "Honolulu")
        elapsed = time.time() - start
        
        assert len(result) == 10000
        assert elapsed < 1.0  # Should take less than 1 second
    
    def test_suppression_performance(self):
        """
        Regression: Suppression operations should be fast on large datasets.
        """
        from dashboard_utils import build_suppressed_bar_count_columns
        import time
        
        # Create large dataset
        large_values = list(range(10000))
        
        start = time.time()
        plot_vals, display_vals, mask = build_suppressed_bar_count_columns(large_values)
        elapsed = time.time() - start
        
        assert len(plot_vals) == 10000
        assert elapsed < 1.0  # Should take less than 1 second


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "regression"])
