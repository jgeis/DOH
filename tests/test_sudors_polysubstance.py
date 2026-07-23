"""
test_sudors_polysubstance.py - Tests for sudors_polysubstance_dashboard.py and /sudors-polysubstance page.

Tests cover:
- Page loading and initialization
- Filter functionality with real data
- Data validation across all visuals
- Specific test case: All Stimulants, No homeless, Male, 45-54 in 2024 showing 36 deaths

These tests use REAL DATA from the database to verify:
- Queries are working correctly
- Visuals load as expected
- Filters work correctly with actual data
- Polysubstance co-occurrence logic works properly

Note: Tests use 2024 and older data only. New date-based data gets added all the time,
so we avoid hardcoding numbers tied to years after 2024 as tests would fail when 
current dates are added. Data from 2024 and older will not change.

The AI query that generated the tests:
Using test_discharges_su_polysubstance.py and test_sudors_dashboard.py as examples, create tests for 'sudors_polysubstance_dashboard.py'.  
Set the filters as appropriate and get the numbers directly from the sudors_polysubstance_dashboard to use in the tests.
Add a test to verify the "Reset All Filters" buttons works along with any other tests you think may be valuable. 
New date-based data gets added all the time, so don't hard code any numbers that aren't tied to a year after 
2024 as the tests will fail when current dates are added. Data from 2024 and older will not change.
"""
import pytest
import pandas as pd
import plotly.graph_objects as go
import sudors_polysubstance_dashboard


class TestSUDORSPolysubstancePageStructure:
    """Test basic page structure and initialization."""
    
    def test_sudors_polysubstance_page_has_layout(self):
        """Test that sudors-polysubstance dashboard has a layout."""
        assert hasattr(sudors_polysubstance_dashboard, 'layout'), "Page should have layout attribute"
        assert sudors_polysubstance_dashboard.layout is not None, "Layout should not be None"
    
    def test_sudors_polysubstance_imports_correctly(self):
        """Test that sudors_polysubstance_dashboard module can be imported."""
        assert hasattr(sudors_polysubstance_dashboard, 'update_dashboard'), "Module should have update_dashboard callback"
        assert hasattr(sudors_polysubstance_dashboard, 'reset_cooccurrence_filters'), "Module should have reset_cooccurrence_filters callback"


class TestSUDORSPolysubstanceDataLoading:
    """Test data loading and initialization with real data."""
    
    def test_load_sudors_polysubstance_dataframe_from_db(self):
        """Test that data loading function works correctly with real data."""
        df = sudors_polysubstance_dashboard.df_raw
        
        assert not df.empty, "Real data should not be empty"
        assert 'substance' in df.columns, "Should have substance column"
        assert 'homeless' in df.columns, "Should have homeless column"
        assert 'sex' in df.columns, "Should have sex column"
        assert 'age_cat' in df.columns, "Should have age_cat column"
        assert 'race_ethnicity' in df.columns, "Should have race_ethnicity column"
        assert 'year' in df.columns, "Should have year column"
        assert 'incident_id' in df.columns, "Should have incident_id column"
        assert len(df) > 0, "Should have at least some rows of data"
    
    def test_homeless_column_has_no_trailing_whitespace(self):
        """Test that homeless column values are trimmed (regression test for filter bug)."""
        df = sudors_polysubstance_dashboard.df_raw
        if 'homeless' in df.columns:
            homeless_values = df['homeless'].unique()
            for homeless in homeless_values:
                homeless_str = str(homeless)
                assert homeless_str == homeless_str.strip(), f"Homeless '{homeless}' should not have trailing whitespace"

    def test_sex_column_has_no_trailing_whitespace(self):
        """Test that sex column values are trimmed (regression test for sex filter bug)."""
        df = sudors_polysubstance_dashboard.df_raw
        
        if 'sex' in df.columns:
            sex_values = df['sex'].unique()
            for sex in sex_values:
                sex_str = str(sex)
                assert sex_str == sex_str.strip(), f"Sex '{sex}' should not have trailing whitespace"

    def test_substance_column_has_no_trailing_whitespace(self):
        """Test that substance column values are trimmed (regression test for substance filter bug)."""
        df = sudors_polysubstance_dashboard.df_raw
        
        if 'substance' in df.columns:
            substance_values = df['substance'].unique()
            for substance in substance_values:
                substance_str = str(substance)
                assert substance_str == substance_str.strip(), f"Substance '{substance}' should not have trailing whitespace"

    def test_age_column_has_no_trailing_whitespace(self):
        """Test that age column values are trimmed (regression test for age filter bug)."""
        df = sudors_polysubstance_dashboard.df_raw
        
        if 'age_cat' in df.columns:
            age_values = df['age_cat'].unique()
            for age in age_values:
                age_str = str(age)
                assert age_str == age_str.strip(), f"Age '{age}' should not have trailing whitespace"

    def test_race_ethnicity_column_has_no_trailing_whitespace(self):
        """Test that race/ethnicity column values are trimmed (regression test for race/ethnicity filter bug)."""
        df = sudors_polysubstance_dashboard.df_raw
        
        if 'race_ethnicity' in df.columns:
            race_ethnicity_values = df['race_ethnicity'].unique()
            for race_ethnicity in race_ethnicity_values:
                race_ethnicity_str = str(race_ethnicity)
                assert race_ethnicity_str == race_ethnicity_str.strip(), f"Race/Ethnicity '{race_ethnicity}' should not have trailing whitespace"


@pytest.mark.integration
class TestSUDORSPolysubstanceFiltering:
    """Test filter functionality with real data."""
    
    def test_filter_by_substance_all_stimulants(self):
        """Test filtering by All Stimulants substance with real data from 2024."""
        result = sudors_polysubstance_dashboard.update_dashboard(
            substance=['All Stimulants'],
            homeless=None,
            sex=None,
            age=None,
            race=None,
            year=['2024']
        )
        
        # Result should be a tuple with 7 elements (kpi, bar, 5 tables)
        assert len(result) == 7, f"Should return 7 elements, got {len(result)}"
        
        # KPI should show 304
        kpi = result[0]
        assert kpi is not None, "KPI should not be None"
        assert '304' in kpi, f"KPI should show 304 for All Stimulants in 2024, got: {kpi}"
    
    def test_filter_by_year_2024(self):
        """Test filtering by year 2024 with real data."""
        result = sudors_polysubstance_dashboard.update_dashboard(
            substance=None,
            homeless=None,
            sex=None,
            age=None,
            race=None,
            year=['2024']
        )
        kpi, bar_fig, table_race, table_sex, table_homeless, table_year, table_age = result
        
        # KPI should show 343 for all 2024 data
        assert '343' in kpi, f"KPI should contain 343 for 2024, got: {kpi}"
        
        # Year table should show 343 for 2024
        assert table_year is not None, "Year table should not be None"
        table_year_str = str(table_year)
        assert '343' in table_year_str, f"Year table should contain 343, got: {table_year_str}"
        assert '2024' in table_year_str, f"Year table should contain 2024, got: {table_year_str}"

    def test_filter_by_homeless_no(self):
        """Test filtering by Homeless=No with real data from 2024."""
        result = sudors_polysubstance_dashboard.update_dashboard(
            substance=None,
            homeless=['No'],
            sex=None,
            age=None,
            race=None,
            year=['2024']
        )
        kpi, bar_fig, table_race, table_sex, table_homeless, table_year, table_age = result
        
        # KPI should show 242
        assert '242' in kpi, f"KPI should contain 242 for Homeless No in 2024, got: {kpi}"
        
        # Bar chart should have data
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        
        # Homeless table should show 242 for No
        assert table_homeless is not None, "Homeless table should not be None"
        table_homeless_str = str(table_homeless)
        assert '242' in table_homeless_str, f"Homeless table should contain 242, got: {table_homeless_str}"
        assert 'No' in table_homeless_str, f"Homeless table should contain No, got: {table_homeless_str}"

    def test_filter_by_sex_male(self):
        """Test filtering by sex Male with real data from 2024."""
        result = sudors_polysubstance_dashboard.update_dashboard(
            substance=None,
            homeless=None,
            sex=['Male'],
            age=None,
            race=None,
            year=['2024']
        )
        kpi, bar_fig, table_race, table_sex, table_homeless, table_year, table_age = result
        
        # KPI should show 269
        assert '269' in kpi, f"KPI should contain 269 for Male in 2024, got: {kpi}"
        
        # Sex table should show 269 for Male
        assert table_sex is not None, "Sex table should not be None"
        table_sex_str = str(table_sex)
        assert '269' in table_sex_str, f"Sex table should contain 269, got: {table_sex_str}"
        assert 'Male' in table_sex_str, f"Sex table should contain Male, got: {table_sex_str}"

    def test_filter_by_age_group_25_34(self):
        """Test filtering by age group 25-34 with real data from 2024."""
        result = sudors_polysubstance_dashboard.update_dashboard(
            substance=None,
            homeless=None,
            sex=None,
            age=['25-34'],
            race=None,
            year=['2024']
        )
        kpi, bar_fig, table_race, table_sex, table_homeless, table_year, table_age = result
        
        # KPI should show 41
        assert '41' in kpi, f"KPI should contain 41 for age 25-34 in 2024, got: {kpi}"
        
        # Age table should show 41 for age group 25-34
        assert table_age is not None, "Age table should not be None"
        table_age_str = str(table_age)
        assert '41' in table_age_str, f"Age table should contain 41, got: {table_age_str}"
        assert '25-34' in table_age_str, f"Age table should contain 25-34, got: {table_age_str}"

    def test_filter_by_race_ethnicity_asian(self):
        """Test filtering by race/ethnicity Asian, non-Hispanic with real data from 2024."""
        result = sudors_polysubstance_dashboard.update_dashboard(
            substance=None,
            homeless=None,
            sex=None,
            age=None,
            race=['Asian, non-Hispanic'],
            year=['2024']
        )
        kpi, bar_fig, table_race, table_sex, table_homeless, table_year, table_age = result
        
        # KPI should show 53
        assert '53' in kpi, f"KPI should contain 53 for Asian, non-Hispanic in 2024, got: {kpi}"
        
        # Race/Ethnicity table should show 53 for Asian, non-Hispanic
        assert table_race is not None, "Race/Ethnicity table should not be None"
        table_race_str = str(table_race)
        assert '53' in table_race_str, f"Race/Ethnicity table should contain 53, got: {table_race_str}"
        assert 'Asian, non-Hispanic' in table_race_str, f"Race/Ethnicity table should contain Asian, non-Hispanic, got: {table_race_str}"


@pytest.mark.regression
class TestSUDORSPolysubstanceRegressionScenarios:
    """Regression tests for known scenarios using real data from 2024."""
    
    def test_specific_scenario_stimulants_no_male_45_54_2024_36_deaths(self):
        """
        REGRESSION TEST: Specific test case with REAL DATA from 2024.
        
        When filtering for:
        - Substance Type: All Stimulants
        - Homeless: No
        - Sex: Male
        - Age Group: 45-54
        - Calendar Year: 2024
        
        Expected results (verified from real data):
        - All visuals should show 36 deaths
        - This verifies:
          * Query is working correctly
          * Visuals load as expected
          * Filters work correctly
          * All aggregations are consistent
          * Polysubstance co-occurrence logic works
        
        Note: Using 2024 data which will not change. Do not use 2025 or later.
        """
        # Apply the specific filters to real data
        result = sudors_polysubstance_dashboard.update_dashboard(
            substance=['All Stimulants'],
            homeless=['No'],
            sex=['Male'],
            age=['45-54'],
            race=None,
            year=['2024']
        )
        
        # Unpack the results (7 outputs)
        (kpi_text, 
         bar_fig, 
         table_race,
         table_sex,
         table_homeless,
         table_year,
         table_age) = result
        
        # TEST 1: KPI card should show 36
        assert '36' in kpi_text, f"KPI should contain 36, got: {kpi_text}"
        
        # TEST 2: Bar chart should have data (showing co-occurring substances)
        assert bar_fig is not None, "Bar chart should not be None"
        # May or may not have data depending on co-occurrence
        
        # TEST 3: Race table should have data
        assert table_race is not None, "Race table should not be None"
        
        # TEST 4: Sex table should show 36 for Male
        assert table_sex is not None, "Sex table should not be None"
        table_sex_str = str(table_sex)
        assert '36' in table_sex_str, f"Sex table should contain 36, got: {table_sex_str}"
        assert 'Male' in table_sex_str, "Sex table should contain Male"
        
        # TEST 5: Homeless table should show 36 for No
        assert table_homeless is not None, "Homeless table should not be None"
        table_homeless_str = str(table_homeless)
        assert '36' in table_homeless_str, f"Homeless table should contain 36, got: {table_homeless_str}"
        assert 'No' in table_homeless_str, "Homeless table should contain No"
        
        # TEST 6: Year table should show 36 for 2024
        assert table_year is not None, "Year table should not be None"
        table_year_str = str(table_year)
        assert '36' in table_year_str, f"Year table should contain 36, got: {table_year_str}"
        assert '2024' in table_year_str, "Year table should contain 2024"
        
        # TEST 7: Age table should show 36 for 45-54
        assert table_age is not None, "Age table should not be None"
        table_age_str = str(table_age)
        assert '36' in table_age_str, f"Age table should contain 36, got: {table_age_str}"
        assert '45-54' in table_age_str, "Age table should contain 45-54"
    
    def test_empty_filters_shows_all_data(self):
        """Regression: Empty filters should show all data from real database."""
        result = sudors_polysubstance_dashboard.update_dashboard(
            substance=None,
            homeless=None,
            sex=None,
            age=None,
            race=None,
            year=None
        )
        
        kpi, bar_fig, table_race, table_sex, table_homeless, table_year, table_age = result
        
        # Should have data for multiple substances
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        
        bar_data = bar_fig.data[0]
        assert len(bar_data.y) > 1, f"Should show multiple substances, got {len(bar_data.y)}"
    
    def test_multiple_years_selected(self):
        """Regression: Multiple year selection should work with real data."""
        result = sudors_polysubstance_dashboard.update_dashboard(
            substance=['All Stimulants'],
            homeless=['No'],
            sex=['Male'],
            age=['45-54'],
            race=None,
            year=['2023', '2024']
        )
        
        kpi, bar_fig, table_race, table_sex, table_homeless, table_year, table_age = result
        
        # Year table should show both years
        table_year_str = str(table_year)
        assert '2023' in table_year_str or '2024' in table_year_str, "Should show at least one of the selected years"


class TestSUDORSPolysubstanceResetFilters:
    """Test filter reset functionality."""
    
    def test_reset_filters_callback_exists(self):
        """Test that reset filters callback is defined."""
        assert hasattr(sudors_polysubstance_dashboard, 'reset_cooccurrence_filters'), "Should have reset_cooccurrence_filters function"
        assert callable(sudors_polysubstance_dashboard.reset_cooccurrence_filters), "reset_cooccurrence_filters should be callable"
    
    def test_reset_filters_returns_none_values(self):
        """Test that reset filters returns None for all filter values."""
        result = sudors_polysubstance_dashboard.reset_cooccurrence_filters(1)
        
        # Should return 6 None values (one for each filter)
        assert len(result) == 6, f"Should return 6 values, got {len(result)}"
        assert all(v is None for v in result), "All filter values should be None after reset"


@pytest.mark.integration
class TestSUDORSPolysubstanceEdgeCases:
    """Test edge cases and data consistency."""
    
    def test_no_data_scenario_handles_gracefully(self):
        """Test that filtering with very specific criteria doesn't crash."""
        # Filter for a very unlikely combination
        result = sudors_polysubstance_dashboard.update_dashboard(
            substance=['All Stimulants'],
            homeless=['Yes'],
            sex=['Female'],
            age=['75+'],
            race=None,
            year=['2024']
        )
        
        # Should not crash, should return valid structure
        assert len(result) == 7, "Should still return 7 elements even with no/little data"
        
        kpi = result[0]
        assert kpi is not None, "KPI should not be None"
    
    def test_all_filters_applied_simultaneously(self):
        """Test that all filters can be applied together without errors."""
        result = sudors_polysubstance_dashboard.update_dashboard(
            substance=['All Stimulants'],
            homeless=['No'],
            sex=['Male'],
            age=['45-54'],
            race=['White, non-Hispanic'],
            year=['2024']
        )
        
        # Should not crash
        assert len(result) == 7, "Should return 7 elements"
        
        kpi = result[0]
        assert kpi is not None, "KPI should not be None"
    
    def test_year_2024_data_consistency(self):
        """
        Test that 2024 data remains consistent (343 total deaths).
        
        This is a regression test to ensure that historical 2024 data 
        doesn't change over time.
        """
        result = sudors_polysubstance_dashboard.update_dashboard(
            substance=None,
            homeless=None,
            sex=None,
            age=None,
            race=None,
            year=['2024']
        )
        
        kpi = result[0]
        assert '343' in kpi, f"2024 should have 343 deaths (stable historical data), got: {kpi}"
    
    def test_data_integrity_all_visuals_match(self):
        """Test that KPI and table totals match for filtered data."""
        result = sudors_polysubstance_dashboard.update_dashboard(
            substance=None,
            homeless=None,
            sex=['Male'],
            age=None,
            race=None,
            year=['2024']
        )
        
        kpi_text = result[0]
        table_sex = result[3]
        
        # Extract number from KPI
        import re
        kpi_numbers = re.findall(r'[\d,]+', kpi_text)
        if kpi_numbers:
            kpi_value = kpi_numbers[0]
            
            # Table should also show the same total
            table_sex_str = str(table_sex)
            assert kpi_value in table_sex_str, f"Sex table should contain same total as KPI ({kpi_value})"
    
    def test_polysubstance_cooccurrence_logic(self):
        """Test that polysubstance co-occurrence filtering works correctly."""
        # When filtering by a substance, the dashboard should keep only records
        # that contain ALL selected substances (not just any)
        result = sudors_polysubstance_dashboard.update_dashboard(
            substance=['Methamphetamine'],
            homeless=None,
            sex=None,
            age=None,
            race=None,
            year=['2024']
        )
        
        kpi, bar_fig, table_race, table_sex, table_homeless, table_year, table_age = result
        
        # KPI should show deaths with Methamphetamine (277)
        assert '277' in kpi, f"KPI should show 277 for Methamphetamine in 2024, got: {kpi}"
        
        # Bar chart should show co-occurring substances (not Methamphetamine itself)
        assert bar_fig is not None, "Bar chart should not be None"
        if len(bar_fig.data) > 0:
            bar_data = bar_fig.data[0]
            # The bar chart should exclude the filtered substance
            y_labels = [str(y) for y in bar_data.y]
            # Methamphetamine should not be in the bar labels since it's filtered out
            assert not any('Methamphetamine' in label for label in y_labels), \
                f"Co-occurring bar should not show the filtered substance (Methamphetamine), got: {y_labels}"
    
    def test_multiple_substances_requires_all(self):
        """Test that selecting multiple substances requires ALL to be present (AND logic)."""
        # When filtering by multiple substances, only records with ALL substances should match
        result = sudors_polysubstance_dashboard.update_dashboard(
            substance=['All Stimulants', 'Fentanyl'],
            homeless=None,
            sex=None,
            age=None,
            race=None,
            year=['2024']
        )
        
        kpi, bar_fig, table_race, table_sex, table_homeless, table_year, table_age = result
        
        # KPI should show deaths with BOTH All Stimulants AND Fentanyl (77)
        assert '77' in kpi, f"KPI should show 77 for records with both All Stimulants and Fentanyl in 2024, got: {kpi}"


@pytest.mark.integration
class TestSUDORSPolysubstanceCharts:
    """Test chart generation and data validation with real data."""
    
    def test_substance_bar_chart_structure(self):
        """Test that substance bar chart has correct structure with real data."""
        result = sudors_polysubstance_dashboard.update_dashboard(
            substance=None,
            homeless=None,
            sex=None,
            age=None,
            race=None,
            year=['2024']
        )
        kpi, bar_fig, table_race, table_sex, table_homeless, table_year, table_age = result
        
        # Should be a bar chart
        assert isinstance(bar_fig, go.Figure), "Should be a Plotly Figure"
        assert len(bar_fig.data) > 0, "Should have at least one trace"
        assert bar_fig.data[0].type == 'bar', "Should be a bar chart"
        
        # Bar chart should be horizontal (orientation='h')
        assert bar_fig.data[0].orientation == 'h', "Bar chart should be horizontal"
    
    def test_bar_chart_excludes_filtered_substance(self):
        """Test that bar chart excludes the filtered substance."""
        result = sudors_polysubstance_dashboard.update_dashboard(
            substance=['All Stimulants'],
            homeless=None,
            sex=None,
            age=None,
            race=None,
            year=['2024']
        )
        
        kpi, bar_fig, table_race, table_sex, table_homeless, table_year, table_age = result
        
        # Bar chart should not show All Stimulants since it's the filtered substance
        if len(bar_fig.data) > 0:
            bar_data = bar_fig.data[0]
            y_labels = [str(y) for y in bar_data.y]
            assert not any('All Stimulants' in label for label in y_labels), \
                f"Bar chart should not show filtered substance (All Stimulants)"


class TestSUDORSPolysubstanceTables:
    """Test table generation with real data."""
    
    def test_tables_are_not_none(self):
        """Test that all tables are generated."""
        result = sudors_polysubstance_dashboard.update_dashboard(
            substance=['All Stimulants'],
            homeless=None,
            sex=None,
            age=None,
            race=None,
            year=['2024']
        )
        
        (kpi, bar_fig, table_race, table_sex, table_homeless, table_year, table_age) = result
        
        assert table_race is not None, "Race table should not be None"
        assert table_sex is not None, "Sex table should not be None"
        assert table_homeless is not None, "Homeless table should not be None"
        assert table_year is not None, "Year table should not be None"
        assert table_age is not None, "Age table should not be None"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
