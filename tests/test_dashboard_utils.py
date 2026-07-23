"""
Unit tests for dashboard_utils.py

Tests cover all utility functions including:
- Filter label handling and normalization
- Count suppression and formatting
- Percentage display and suppression  
- Data manipulation (statewide aggregation, county filtering)
- UI component generation
"""
import pytest
import pandas as pd
import numpy as np
from dashboard_utils import (
    get_standard_filter_label,
    _normalize_filter_label,
    format_count_display,
    build_suppressed_bar_count_columns,
    format_percentage_display,
    build_suppressed_percentage_columns,
    wrap_axis_label,
    compute_adaptive_horizontal_bar_height,
    opts_list,
    format_display_list,
    with_statewide_county,
    statewide_first,
    apply_county_filter,
    county_output_should_include_statewide,
    append_statewide_aggregate_rows,
    sort_opts,
    COUNT_SUPPRESSION_THRESHOLD,
    SUPPRESSED_COUNT_LABEL,
    STATEWIDE_COUNTY,
)


class TestFilterLabelHandling:
    """Test filter label standardization and normalization."""
    
    def test_get_standard_filter_label_known_label(self):
        """Test that known labels are standardized correctly."""
        assert get_standard_filter_label("Substance") == "Substance Type"
        assert get_standard_filter_label("sex") == "Sex at Birth"
        assert get_standard_filter_label("Year") == "Calendar Year"
    
    def test_get_standard_filter_label_unknown_label(self):
        """Test that unknown labels pass through unchanged."""
        assert get_standard_filter_label("Unknown Label") == "Unknown Label"
        assert get_standard_filter_label("Custom Field") == "Custom Field"
    
    def test_normalize_filter_label(self):
        """Test filter label normalization removes punctuation and standardizes case."""
        assert _normalize_filter_label("Sex at Birth") == "sex at birth"
        assert _normalize_filter_label("Race/Ethnicity") == "race ethnicity"
        assert _normalize_filter_label("Hawaii-Resident!") == "hawaii resident"
        assert _normalize_filter_label("  Multiple   Spaces  ") == "multiple spaces"


class TestCountSuppression:
    """Test count suppression and display formatting."""
    
    def test_format_count_display_above_threshold(self):
        """Test counts above threshold are formatted with commas."""
        assert format_count_display(100) == "100"
        assert format_count_display(1000) == "1,000"
        assert format_count_display(1234567) == "1,234,567"
    
    def test_format_count_display_below_threshold(self):
        """Test counts below threshold are suppressed."""
        assert format_count_display(5) == SUPPRESSED_COUNT_LABEL
        assert format_count_display(9) == SUPPRESSED_COUNT_LABEL
        assert format_count_display(0) == "0"
    
    def test_format_count_display_at_threshold(self):
        """Test count at threshold is shown."""
        assert format_count_display(COUNT_SUPPRESSION_THRESHOLD) == str(COUNT_SUPPRESSION_THRESHOLD)
    
    def test_format_count_display_none_or_nan(self):
        """Test None and NaN values are suppressed."""
        assert format_count_display(None) == SUPPRESSED_COUNT_LABEL
        assert format_count_display(np.nan) == SUPPRESSED_COUNT_LABEL
    
    def test_format_count_display_custom_threshold(self):
        """Test custom suppression threshold."""
        assert format_count_display(15, threshold=20) == "<10*"
        assert format_count_display(20, threshold=20) == "20"
    
    def test_format_count_display_custom_label(self):
        """Test custom suppression label."""
        assert format_count_display(5, suppressed_label="HIDDEN") == "HIDDEN"
    
    def test_build_suppressed_bar_count_columns_basic(self):
        """Test basic suppression for bar chart data."""
        values = [5, 15, 8, 100, 3]
        plot_vals, display_vals, mask = build_suppressed_bar_count_columns(values)
        
        # Values below threshold should be zeroed in plot
        assert plot_vals.tolist() == [0, 15, 0, 100, 0]
        # Display values should show suppression label
        assert display_vals.tolist() == [SUPPRESSED_COUNT_LABEL, "15", SUPPRESSED_COUNT_LABEL, "100", SUPPRESSED_COUNT_LABEL]
        # Mask should identify suppressed values
        assert mask.tolist() == [True, False, True, False, True]
    
    def test_build_suppressed_bar_count_columns_suppress_zero(self):
        """Test suppression behavior with suppress_zero flag."""
        values = [0, 5, 10, 15]
        plot_vals, display_vals, mask = build_suppressed_bar_count_columns(values, suppress_zero=True)
        
        # With suppress_zero=True, 0 should be suppressed
        assert plot_vals.tolist() == [0, 0, 10, 15]
        assert display_vals.tolist() == [SUPPRESSED_COUNT_LABEL, SUPPRESSED_COUNT_LABEL, "10", "15"]


class TestPercentageDisplay:
    """Test percentage display and suppression."""
    
    def test_format_percentage_display_normal(self):
        """Test normal percentage formatting."""
        assert format_percentage_display(25.5, count_value=100) == "25.5%"
        assert format_percentage_display(10.123, count_value=50, decimals=2) == "10.12%"
        assert format_percentage_display(0, count_value=100) == "0.0%"
    
    def test_format_percentage_display_suppressed_count(self):
        """Test percentage is hidden when count is suppressed."""
        result = format_percentage_display(25.5, count_display=SUPPRESSED_COUNT_LABEL)
        assert result == ""
        
        result = format_percentage_display(25.5, count_value=5)  # Below threshold
        assert result == ""
    
    def test_format_percentage_display_custom_decimals(self):
        """Test custom decimal precision."""
        assert format_percentage_display(33.333, count_value=100, decimals=0) == "33%"
        assert format_percentage_display(33.333, count_value=100, decimals=2) == "33.33%"
    
    def test_format_percentage_display_invalid_values(self):
        """Test handling of invalid percentage values."""
        assert format_percentage_display(np.nan, count_value=100) == ""
        assert format_percentage_display(np.inf, count_value=100) == ""
        assert format_percentage_display(None, count_value=100) == ""
    
    def test_build_suppressed_percentage_columns(self):
        """Test building suppressed percentage columns for charts."""
        percentages = [25.5, 15.0, 8.5, 50.0]
        counts = [100, 50, 5, 200]  # Third count is suppressed
        
        plot_vals, display_vals, mask = build_suppressed_percentage_columns(
            percentages, count_values=counts
        )
        
        # Third value should be zeroed
        assert plot_vals.tolist() == [25.5, 15.0, 0.0, 50.0]
        # Third display should be empty
        assert display_vals.tolist() == ["25.5%", "15.0%", "", "50.0%"]
        # Mask should identify suppressed value
        assert mask.tolist() == [False, False, True, False]


class TestAxisFormatting:
    """Test axis label formatting."""
    
    def test_wrap_axis_label_short(self):
        """Test short labels remain unwrapped."""
        assert wrap_axis_label("Short Label") == "Short Label"
        assert wrap_axis_label("Age Group") == "Age Group"
    
    def test_wrap_axis_label_long(self):
        """Test long labels are wrapped with HTML breaks."""
        long_label = "This is a very long axis label that should be wrapped into multiple lines"
        result = wrap_axis_label(long_label, max_len=30)
        assert "<br>" in result
        # Check it's split into multiple parts
        assert len(result.split("<br>")) > 1
    
    def test_wrap_axis_label_custom_length(self):
        """Test custom wrap length."""
        label = "Medium length label for testing custom wrap"
        result = wrap_axis_label(label, max_len=20)
        assert "<br>" in result
    
    def test_wrap_axis_label_none(self):
        """Test None input returns empty string."""
        assert wrap_axis_label(None) == ""


class TestChartDimensions:
    """Test chart dimension calculations."""
    
    def test_compute_adaptive_horizontal_bar_height_basic(self):
        """Test basic height calculation."""
        height = compute_adaptive_horizontal_bar_height(10)
        assert height == 80 + (10 * 30)  # base_padding + (count * pixels_per_bar)
        assert height == 380
    
    def test_compute_adaptive_horizontal_bar_height_min(self):
        """Test minimum height constraint."""
        height = compute_adaptive_horizontal_bar_height(2, min_height=400)
        assert height == 400
    
    def test_compute_adaptive_horizontal_bar_height_max(self):
        """Test maximum height constraint."""
        height = compute_adaptive_horizontal_bar_height(100, max_height=800)
        assert height == 800
    
    def test_compute_adaptive_horizontal_bar_height_custom_params(self):
        """Test custom parameters."""
        height = compute_adaptive_horizontal_bar_height(
            10, pixels_per_bar=50, base_padding=100
        )
        assert height == 100 + (10 * 50)
        assert height == 600


class TestDataManipulation:
    """Test data manipulation utilities."""
    
    def test_opts_list(self):
        """Test conversion of values to Dash dropdown format."""
        values = ["Option A", "Option B", "Option C"]
        result = opts_list(values)
        expected = [
            {"label": "Option A", "value": "Option A"},
            {"label": "Option B", "value": "Option B"},
            {"label": "Option C", "value": "Option C"},
        ]
        assert result == expected
    
    def test_format_display_list_single(self):
        """Test single-item list formatting."""
        assert format_display_list(["Item"]) == "Item"
    
    def test_format_display_list_two(self):
        """Test two-item list formatting."""
        assert format_display_list(["Item A", "Item B"]) == "Item A and Item B"
    
    def test_format_display_list_multiple(self):
        """Test multiple-item list formatting with Oxford comma."""
        result = format_display_list(["A", "B", "C"])
        assert result == "A, B, and C"
        
        result = format_display_list(["A", "B", "C", "D"])
        assert result == "A, B, C, and D"
    
    def test_format_display_list_empty(self):
        """Test empty list returns empty string."""
        assert format_display_list([]) == ""
        assert format_display_list(["", "  "]) == ""


class TestCountyHandling:
    """Test county filtering and statewide aggregation."""
    
    def test_with_statewide_county(self):
        """Test adding Statewide option to county list."""
        counties = ["Honolulu", "Maui", "Hawaii"]
        result = with_statewide_county(counties)
        assert result[0] == STATEWIDE_COUNTY
        assert "Honolulu" in result
        assert "Maui" in result
        assert "Hawaii" in result
    
    def test_with_statewide_county_already_present(self):
        """Test handling when Statewide is already in list."""
        counties = ["Statewide", "Honolulu", "Maui"]
        result = with_statewide_county(counties)
        # Should still have Statewide first, but not duplicated
        assert result.count(STATEWIDE_COUNTY) == 1
        assert result[0] == STATEWIDE_COUNTY
    
    def test_statewide_first(self):
        """Test moving Statewide to front without adding it."""
        counties = ["Honolulu", "Statewide", "Maui"]
        result = statewide_first(counties)
        assert result[0] == STATEWIDE_COUNTY
        assert "Honolulu" in result
        assert "Maui" in result
    
    def test_statewide_first_not_present(self):
        """Test behavior when Statewide is not in list."""
        counties = ["Honolulu", "Maui", "Hawaii"]
        result = statewide_first(counties)
        assert STATEWIDE_COUNTY not in result
        assert result == counties
    
    def test_apply_county_filter_single(self, sample_dataframe):
        """Test filtering to a single county."""
        result = apply_county_filter(sample_dataframe, "Honolulu")
        assert len(result) == 1
        assert result["county"].iloc[0] == "Honolulu"
    
    def test_apply_county_filter_multiple(self, sample_dataframe):
        """Test filtering to multiple counties."""
        result = apply_county_filter(sample_dataframe, ["Honolulu", "Maui"])
        assert len(result) == 2
        assert set(result["county"]) == {"Honolulu", "Maui"}
    
    def test_apply_county_filter_statewide(self, sample_dataframe):
        """Test that Statewide selection returns all data."""
        result = apply_county_filter(sample_dataframe, [STATEWIDE_COUNTY, "Honolulu"])
        assert len(result) == len(sample_dataframe)
    
    def test_apply_county_filter_none(self, sample_dataframe):
        """Test that None returns all data."""
        result = apply_county_filter(sample_dataframe, None)
        assert len(result) == len(sample_dataframe)
    
    def test_apply_county_filter_empty(self, sample_dataframe):
        """Test that empty list returns all data."""
        result = apply_county_filter(sample_dataframe, [])
        assert len(result) == len(sample_dataframe)
    
    def test_county_output_should_include_statewide_none(self):
        """Test statewide should be included when no county selected."""
        assert county_output_should_include_statewide(None) is True
    
    def test_county_output_should_include_statewide_empty(self):
        """Test statewide should be included for empty selection."""
        assert county_output_should_include_statewide([]) is True
    
    def test_county_output_should_include_statewide_explicit(self):
        """Test statewide should be included when explicitly selected."""
        assert county_output_should_include_statewide([STATEWIDE_COUNTY]) is True
        assert county_output_should_include_statewide(["Honolulu", STATEWIDE_COUNTY]) is True
    
    def test_county_output_should_include_statewide_specific(self):
        """Test statewide should not be included for specific county."""
        assert county_output_should_include_statewide(["Honolulu"]) is False
    
    def test_append_statewide_aggregate_rows(self):
        """Test appending statewide aggregate rows."""
        df = pd.DataFrame({
            "county": ["Honolulu", "Maui", "Hawaii"],
            "year": [2020, 2020, 2020],
            "count": [100, 50, 75]
        })
        
        result = append_statewide_aggregate_rows(df, value_col="count")
        
        # Should have original rows plus one statewide row
        assert len(result) == 4
        statewide_row = result[result["county"] == STATEWIDE_COUNTY]
        assert len(statewide_row) == 1
        assert statewide_row["count"].iloc[0] == 225  # Sum of all counties
    
    def test_append_statewide_aggregate_rows_with_groups(self):
        """Test statewide aggregation with multiple grouping columns."""
        df = pd.DataFrame({
            "county": ["Honolulu", "Maui", "Honolulu", "Maui"],
            "year": [2020, 2020, 2021, 2021],
            "count": [100, 50, 120, 60]
        })
        
        result = append_statewide_aggregate_rows(df, value_col="count")
        
        # Should have original 4 rows plus 2 statewide rows (one per year)
        assert len(result) == 6
        statewide_rows = result[result["county"] == STATEWIDE_COUNTY]
        assert len(statewide_rows) == 2
        
        # Check aggregation by year
        statewide_2020 = statewide_rows[statewide_rows["year"] == 2020]
        assert statewide_2020["count"].iloc[0] == 150
        
        statewide_2021 = statewide_rows[statewide_rows["year"] == 2021]
        assert statewide_2021["count"].iloc[0] == 180


class TestSortOpts:
    """Test sorting options for dropdown menus."""
    
    def test_sort_opts_regular_strings(self):
        """Test sorting regular string values."""
        values = ["Zebra", "Apple", "Banana", "Unknown"]
        result = sort_opts(values)
        assert result == ["Apple", "Banana", "Zebra", "Unknown"]
    
    def test_sort_opts_age_ranges(self):
        """Test sorting age range values."""
        values = ["45+", "18-25", "0-17", "26-34", "35-44", "Unknown"]
        result = sort_opts(values)
        # Should be in age order, with Unknown last
        assert result == ["0-17", "18-25", "26-34", "35-44", "45+", "Unknown"]
    
    def test_sort_opts_years(self):
        """Test sorting year values in descending order."""
        values = ["2020", "2022", "2021", "2019", "Unknown"]
        result = sort_opts(values)
        # Years should be descending, Unknown last
        assert result == ["2022", "2021", "2020", "2019", "Unknown"]
    
    def test_sort_opts_under_age(self):
        """Test sorting with 'Under X' format."""
        values = ["18-25", "Under 18", "25-34", "Unknown"]
        result = sort_opts(values)
        assert result[0] == "Under 18"
        assert result[-1] == "Unknown"
    
    def test_sort_opts_less_than(self):
        """Test sorting with '<X' format."""
        values = ["18-25", "<18", "25-34", "35+"]
        result = sort_opts(values)
        assert result[0] == "<18"
    
    def test_sort_opts_plus_ranges(self):
        """Test sorting with '+' format."""
        values = ["18-25", "25-34", "65+", "35-44"]
        result = sort_opts(values)
        assert result[-1] == "65+"


class TestRegressionScenarios:
    """Regression tests for known edge cases and bugs."""
    
    def test_suppression_with_exactly_threshold_value(self):
        """Regression: Ensure threshold value itself is NOT suppressed."""
        value = COUNT_SUPPRESSION_THRESHOLD
        result = format_count_display(value)
        assert result != SUPPRESSED_COUNT_LABEL
        assert result == str(value)
    
    def test_zero_count_handling(self):
        """Regression: Ensure zeros are handled consistently."""
        # Zero should show as zero
        assert format_count_display(0) == '0'
    
    def test_mixed_type_county_filtering(self):
        """Regression: Handle mixed string/numeric types in filtering."""
        df = pd.DataFrame({
            "county": ["Honolulu", "Maui", "Hawaii"],
            "value": [1, 2, 3]
        })
        # Should not crash with case variations
        result = apply_county_filter(df, "honolulu")
        assert len(result) == 1
    
    def test_empty_dataframe_operations(self):
        """Regression: Ensure operations handle empty DataFrames gracefully."""
        empty_df = pd.DataFrame()
        
        # Should not crash
        result = apply_county_filter(empty_df, "Honolulu")
        assert result.empty
        
        result = append_statewide_aggregate_rows(empty_df, value_col="count")
        assert result.empty
    
    def test_unicode_and_special_characters(self):
        """Regression: Handle Hawaiian characters and special symbols."""
        label = "Hawaiʻi Resident"
        result = _normalize_filter_label(label)
        assert isinstance(result, str)
        
        # Should handle in display list
        result = format_display_list(["Hawaiʻi", "Maui", "O'ahu"])
        assert "Hawaiʻi" in result
    
    def test_very_large_counts(self):
        """Regression: Ensure large numbers are formatted correctly."""
        assert format_count_display(1000000) == "1,000,000"
        assert format_count_display(9999999) == "9,999,999"
    
    def test_percentage_edge_cases(self):
        """Regression: Handle percentage edge cases."""
        # 100%
        assert format_percentage_display(100.0, count_value=50) == "100.0%"
        # Very small percentage
        assert format_percentage_display(0.1, count_value=1000) == "0.1%"
        # Over 100% (shouldn't happen but handle gracefully)
        assert format_percentage_display(150.0, count_value=50) == "150.0%"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
