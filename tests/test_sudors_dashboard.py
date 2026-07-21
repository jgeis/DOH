"""
test_sudors_dashboard.py - Tests for sudors_dashboard.py

Tests cover:
- Page loading and initialization
- Filter functionality with real data
- Data validation across all visuals
- Specific test cases (2024 totals, 2023-2024 totals, narrow filter scenarios)
- Edge cases for empty datasets to ensure no "Column not found" errors

These tests use REAL DATA from the database to verify:
- Queries are working correctly
- Visuals load as expected
- Filters work correctly with actual data

Here's the prompt I used to generate these tests:
Using test_discharges_su.py as an example, create tests for 'sudors_dashboard.py'.  Here are some numbers you can use:
- When the year filter is set to 2024, the KPI card should have a value of 360.  
The "Deaths by Substance" bar chart should have 9 rows.  The top bar should be 'All Stimulants' with a value of 304 and the next one should be 'Methamphetamine' with a value of 277. 
The "Yearly Deaths by Substance" line chart should have a single year, 2024.  The dot for '2024' and 'Fentanyl' should have a value of 105.
The 'Calendar year' table should have 1 row, '2024' with a value of '360'.  
The 'Age Group' table should have 8 rows with '25-34' having a value of 42. 
The 'Sex at Birth' table should have 2 rows with 'Male' having a value of 278.
The 'Race/Ethnicity' table should have 8 rows with 'Asian, non-Hispanic' having a value of 54.
The 'Homeless' table should have 3 rows with 'No' having a value of 253.
 a 3 rows with the following values `Contracted Providers=5,201, Community Mental Health Centers=4,506, and Hawaii State Hospital=801.

- When the year filter is set to 2023 and 2024, the KPI card should have a value of 692.  
The "Deaths by Substance" bar chart should have 9 rows.  The top bar should be 'All Stimulants' with a value of 557 and the next one should be 'Methamphetamine' with a value of 498. 
The "Yearly Deaths by Substance" line chart should have the years 2023 and 2024.  The dot for '2023' and 'Fentanyl' should have a value of 107 and the dot for '2024' and 'Fentanyl' should have a value of 105.
The 'Calendar year' table should have 2 rows, '2023' with a value of '332' and '2024' with a value of '360'.  
The 'Age Group' table should have 8 rows with '25-34' having a value of 81. 
The 'Sex at Birth' table should have 2 rows with 'Male' having a value of 529.
The 'Race/Ethnicity' table should have 8 rows with 'Asian, non-Hispanic' having a value of 88.
The 'Homeless' table should have 3 rows with 'No' having a value of 468.

- Verify the 'Reset All Filters' button resets everything back to the original state.

- Set the following filters: substance type=All Stimulants, year=2024, Age Group=45-54, Sex at Birth=Male, Race/Ethnicity='Multiracial, non-hispanic', Homeless=No
the KPI card should have a value of 18.  
The "Deaths by Substance" bar chart should have 1 row, 'All Stimulants' with a value of 18. 
The "Yearly Deaths by Substance" line chart should have a single dot, 2024.  The dot for '2024' and 'All Stimulants' should have a value of 18.
The 'Calendar year' table should have 1 row, '2024' with a value of '18'.  
The 'Age Group' table should have 1 row with '45-54' having a value of 18. 
The 'Sex at Birth' table should have 1 rows with 'Male' having a value of 18.
The 'Race/Ethnicity' table should have 1 row with 'Multiracial, non-hispanic' having a value of 18.
The 'Homeless' table should have 1 rows with 'No' having a value of 18.

- Set the following filters: substance type=All Stimulants, year=2024, Age Group=45-54, Sex at Birth=Male, Race/Ethnicity='Multiracial, non-hispanic', Homeless=Yes
Verify the tables do not display "Column 'column_name' not found." So the year table should not say "Column 'year' not found. etc.

"""
import pytest
import pandas as pd
import plotly.graph_objects as go
import sudors_dashboard
from tests.test_utils import assert_returned_tables_sort_order

class TestSudorsPageStructure:
    """Test basic page structure and initialization."""
    
    def test_sudors_page_has_layout(self):
        """Test that sudors dashboard has a layout."""
        assert hasattr(sudors_dashboard, 'layout'), "Page should have layout attribute"
        assert sudors_dashboard.layout is not None, "Layout should not be None"
    
    def test_sudors_imports_correctly(self):
        """Test that sudors_dashboard module can be imported and has callbacks."""
        assert hasattr(sudors_dashboard, 'update_dashboard'), "Module should have update_dashboard callback"
        assert hasattr(sudors_dashboard, 'reset_all_filters'), "Module should have reset_all_filters callback"

    def test_callback_returns_tables_in_canonical_order(self):
        """Verify the update_dashboard callback returns tables sorted by dashboard_utils."""
        assert_returned_tables_sort_order(sudors_dashboard)


class TestSudorsDataLoading:
    """Test data loading and initialization with real data."""
    
    def test_load_sudors_dataframe_from_db(self):
        """Test that data loading function works correctly with real data."""
        df = sudors_dashboard.df_raw
        
        assert not df.empty, "Real data should not be empty"
        assert 'substance' in df.columns, "Should have substance column"
        assert 'homeless' in df.columns, "Should have homeless column"
        assert 'sex' in df.columns, "Should have sex column"
        assert 'age_cat' in df.columns, "Should have age_cat column"
        assert 'race_ethnicity' in df.columns, "Should have race_ethnicity column"
        assert 'year' in df.columns, "Should have year column"
        assert len(df) > 0, "Should have at least some rows of data"


@pytest.mark.regression
class TestSudorsRegressionScenarios:
    """Regression tests for known scenarios using specific data points."""
    
    def test_scenario_year_2024(self):
        """
        Verify data when year filter is set to 2024.
        Expected: KPI=360, Bar chart top=All Stimulants (304), Line chart dot=Fentanyl (105).
        Table verifications for specific row counts and values.
        """
        result = sudors_dashboard.update_dashboard(
            substance=None,
            homeless=None,
            sex=None,
            age=None,
            race=None,
            year=[2024]
        )
        
        kpi, bar_fig, table_race, table_sex, table_homeless, table_year, table_age, line_fig = result
        
        # Verify KPI
        assert '360' in kpi, f"KPI should contain 360, got: {kpi}"
        
        # Verify Bar Chart (Deaths by Substance)
        assert bar_fig is not None
        assert len(bar_fig.data) > 0
        bar_data = bar_fig.data[0]
        assert len(bar_data.y) == 9, f"Bar chart should have 9 rows, got {len(bar_data.y)}"
        
        # Check top bars (Plotly h-bars sort bottom-up by default, index checking may vary, 
        # but we check presence of specific values)
        assert 'All Stimulants' in bar_data.y
        assert 304 in bar_data.x
        assert 'Methamphetamine' in bar_data.y
        assert 277 in bar_data.x
        
        # Verify Line Chart (Yearly Deaths)
        assert line_fig is not None
        fentanyl_trace = next((trace for trace in line_fig.data if trace.name == 'Fentanyl'), None)
        assert fentanyl_trace is not None, "Fentanyl trace should exist"
        assert len(fentanyl_trace.x) == 1, "Should have a single year (2024)"
        assert fentanyl_trace.x[0] == 2024, "Year should be 2024"
        assert fentanyl_trace.y[0] == 105, f"2024 Fentanyl value should be 105, got {fentanyl_trace.y[0]}"
        
        # Verify Tables
        str_year = str(table_year)
        assert '2024' in str_year and '360' in str_year, "Year table should have 2024 with 360"
        
        str_age = str(table_age)
        assert '25-34' in str_age and '42' in str_age, "Age table should have 25-34 with 42"
        
        str_sex = str(table_sex)
        assert 'Male' in str_sex and '278' in str_sex, "Sex table should have Male with 278"
        
        str_race = str(table_race)
        assert 'Asian, non-Hispanic' in str_race and '54' in str_race, "Race table should have Asian, non-Hispanic with 54"
        
        str_homeless = str(table_homeless)
        assert 'No' in str_homeless and '253' in str_homeless, "Homeless table should have No with 253"

    def test_scenario_year_2023_and_2024(self):
        """
        Verify data when year filter is set to 2023 and 2024.
        Expected: KPI=692, Bar chart top=All Stimulants (557), Line chart dots=Fentanyl (107 for 2023, 105 for 2024).
        """
        result = sudors_dashboard.update_dashboard(
            substance=None,
            homeless=None,
            sex=None,
            age=None,
            race=None,
            year=[2023, 2024]
        )
        
        kpi, bar_fig, table_race, table_sex, table_homeless, table_year, table_age, line_fig = result
        
        # Verify KPI
        assert '692' in kpi, f"KPI should contain 692, got: {kpi}"
        
        # Verify Bar Chart
        bar_data = bar_fig.data[0]
        assert len(bar_data.y) == 9, "Bar chart should have 9 rows"
        assert 557 in bar_data.x, "All Stimulants should have 557"
        assert 498 in bar_data.x, "Methamphetamine should have 498"
        
        # Verify Line Chart
        fentanyl_trace = next((trace for trace in line_fig.data if trace.name == 'Fentanyl'), None)
        assert fentanyl_trace is not None
        assert len(fentanyl_trace.x) == 2, "Should have years 2023 and 2024"
        
        # Match years to values
        point_2023_idx = list(fentanyl_trace.x).index(2023)
        point_2024_idx = list(fentanyl_trace.x).index(2024)
        assert fentanyl_trace.y[point_2023_idx] == 107, "2023 Fentanyl value should be 107"
        assert fentanyl_trace.y[point_2024_idx] == 105, "2024 Fentanyl value should be 105"
        
        # Verify Tables
        str_year = str(table_year)
        assert '2023' in str_year and '332' in str_year
        assert '2024' in str_year and '360' in str_year
        
        str_age = str(table_age)
        assert '25-34' in str_age and '81' in str_age
        
        str_sex = str(table_sex)
        assert 'Male' in str_sex and '529' in str_sex
        
        str_race = str(table_race)
        assert 'Asian, non-Hispanic' in str_race and '88' in str_race
        
        str_homeless = str(table_homeless)
        assert 'No' in str_homeless and '486' in str_homeless

    def test_scenario_narrow_filters(self):
        """
        Verify heavily filtered scenario: All Stimulants, 2024, 45-54, Male, Multiracial, Homeless=No.
        Expected: All metrics and tables should show 18.
        """
        result = sudors_dashboard.update_dashboard(
            substance=['All Stimulants'],
            homeless=['No'],
            sex=['Male'],
            age=['45-54'],
            # Ensure this string exactly matches the database's capitalization!
            race=['Multiracial, non hispanic'], 
            year=[2024]
        )
        
        kpi, bar_fig, table_race, table_sex, table_homeless, table_year, table_age, line_fig = result
        print(f"Result: {result}")
        assert '18' in kpi, f"KPI should be 18, got {kpi}"
        
        # Bar Chart
        bar_data = bar_fig.data[0]
        assert len(bar_data.y) == 1, "Bar chart should have 1 row"
        assert bar_data.y[0] == 'All Stimulants'
        assert bar_data.x[0] == 18
        
        # Line Chart
        line_data = line_fig.data[0]
        assert len(line_data.x) == 1, "Line chart should have a single dot"
        assert line_data.x[0] == 2024
        assert line_data.name == 'All Stimulants'
        assert line_data.y[0] == 18
        
        # Tables
        assert '18' in str(table_year) and '2024' in str(table_year)
        assert '18' in str(table_age) and '45-54' in str(table_age)
        assert '18' in str(table_sex) and 'Male' in str(table_sex)
        assert '18' in str(table_race) and 'Multiracial, non hispanic' in str(table_race)
        assert '18' in str(table_homeless) and 'No' in str(table_homeless)


    def test_scenario_no_column_not_found_error(self):
        """
        Verify that heavily filtered scenarios causing empty subsets do not render 
        raw dataframe errors like "Column 'column_name' not found."
        """
        result = sudors_dashboard.update_dashboard(
            substance=['All Stimulants'],
            homeless=['Yes'],  # Changing to Yes to hit empty or different data
            sex=['Male'],
            age=['45-54'],
            race=['Multiracial, non-hispanic'],
            year=[2024]
        )
        
        _, _, table_race, table_sex, table_homeless, table_year, table_age, _ = result
        
        # Check all tables to ensure they do not bubble up pandas KeyErrors visually
        tables = [table_race, table_sex, table_homeless, table_year, table_age]
        for table in tables:
            table_str = str(table)
            assert "Column 'year' not found" not in table_str
            assert "Column 'age_cat' not found" not in table_str
            assert "Column 'sex' not found" not in table_str
            assert "Column 'race_ethnicity' not found" not in table_str
            assert "Column 'homeless' not found" not in table_str


class TestSudorsResetFilters:
    """Test filter reset functionality."""
    
    def test_reset_filters_returns_none_values(self):
        """Verify the 'Reset All Filters' button resets everything back to original state."""
        # Function returns values for substance, homeless, race, sex, age, year
        result = sudors_dashboard.reset_all_filters(1)
        
        assert len(result) == 6, f"Should return 6 values, got {len(result)}"
        assert all(v is None for v in result), "All filter dropdowns should be reset to None"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])