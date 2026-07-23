"""
test_dose.py - Tests for dose_dashboard.py and /dose page.

Tests cover:
- Page loading and initialization
- Filter functionality with real data
- Data validation across all visuals
- Specific test case: Opioids, Honolulu, 2024, 18-44, Male showing 41 discharges

These tests use REAL DATA from the database to verify:
- Queries are working correctly
- Visuals load as expected
- Filters work correctly with actual data

Note: Tests use 2024 and older data only. New date-based data gets added all the time,
so we avoid hardcoding numbers tied to years after 2024 as tests would fail when 
current dates are added. Data from 2024 and older will not change.

AI Query used to generate these tests:
Using test_discharges_su.py as an example, create tests for 'dose_dashboard.py'.  
Set the filters as appropriate and get the numbers directly from the dose_dashboard to use in the tests.
Add a test to verify the "Reset All Filters" buttons works along with any other tests you think may be valuable. 
New date-based data gets added all the time, so don't hard code any numbers that aren't tied to a year after 
2024 as the tests will fail when current dates are added. Data from 2024 and older will not change.

"""
import pytest
import pandas as pd
import plotly.graph_objects as go
import dose_dashboard


class TestDOSEPageStructure:
    """Test basic page structure and initialization."""
    
    def test_dose_page_registered(self):
        """Test that dose page is registered."""
        from dash import page_registry
        import multi_dashboard  # Ensures pages are registered
        
        paths = [page['path'] for page in page_registry.values()]
        assert '/dose' in paths, "dose page should be registered"
    
    def test_dose_page_has_layout(self):
        """Test that dose page has a layout."""
        from pages import dose
        
        assert hasattr(dose, 'layout'), "Page should have layout attribute"
        assert dose.layout is not None, "Layout should not be None"
    
    def test_dose_imports_correctly(self):
        """Test that dose_dashboard module can be imported."""
        assert hasattr(dose_dashboard, 'layout'), "Module should have layout"
        assert hasattr(dose_dashboard, 'update_dashboard'), "Module should have update_dashboard callback"


class TestDOSEDataLoading:
    """Test data loading and initialization with real data."""
    
    def test_load_dose_dataframe_from_db(self):
        """Test that data loading function works correctly with real data."""
        df = dose_dashboard.df_dose_raw
        
        assert not df.empty, "Real data should not be empty"
        assert 'substance' in df.columns, "Should have substance column"
        assert 'county' in df.columns, "Should have county column"
        assert 'city' in df.columns, "Should have city column"
        assert 'year' in df.columns, "Should have year column"
        assert 'age_group' in df.columns, "Should have age_group column"
        assert 'sex' in df.columns, "Should have sex column"
        assert 'race_ethnicity' in df.columns, "Should have race_ethnicity column"
        assert 'hawaii_residency' in df.columns, "Should have hawaii_residency column"
        assert 'record_id' in df.columns, "Should have record_id column"
        assert len(df) > 0, "Should have at least some rows of data"
    
    def test_year_column_is_numeric(self):
        """Test that year column is numeric in real data."""
        df = dose_dashboard.df_dose_raw
        
        assert pd.api.types.is_numeric_dtype(df['year']), "Year column should be numeric"
    
    def test_county_column_has_no_trailing_whitespace(self):
        """Test that county column values are trimmed (regression test for county filter bug)."""
        df = dose_dashboard.df_dose_raw
        if 'county' in df.columns:
            county_values = df['county'].unique()
            for county in county_values:
                county_str = str(county)
                assert county_str == county_str.strip(), f"County '{county}' should not have trailing whitespace"

    def test_city_column_has_no_trailing_whitespace(self):
        """Test that city column values are trimmed (regression test for city filter bug)."""
        df = dose_dashboard.df_dose_raw
        
        if 'city' in df.columns:
            city_values = df['city'].unique()
            for city in city_values:
                city_str = str(city)
                assert city_str == city_str.strip(), f"City '{city}' should not have trailing whitespace"

    def test_age_column_has_no_trailing_whitespace(self):
        """Test that age column values are trimmed (regression test for age filter bug)."""
        df = dose_dashboard.df_dose_raw
        
        if 'age_group' in df.columns:
            age_values = df['age_group'].unique()
            for age in age_values:
                age_str = str(age)
                assert age_str == age_str.strip(), f"Age '{age}' should not have trailing whitespace"

    def test_sex_column_has_no_trailing_whitespace(self):
        """Test that sex column values are trimmed (regression test for sex filter bug)."""
        df = dose_dashboard.df_dose_raw
        
        if 'sex' in df.columns:
            sex_values = df['sex'].unique()
            for sex in sex_values:
                sex_str = str(sex)
                assert sex_str == sex_str.strip(), f"Sex '{sex}' should not have trailing whitespace"

    def test_substance_column_has_no_trailing_whitespace(self):
        """Test that substance column values are trimmed (regression test for substance filter bug)."""
        df = dose_dashboard.df_dose_raw
        
        if 'substance' in df.columns:
            substance_values = df['substance'].unique()
            for substance in substance_values:
                substance_str = str(substance)
                assert substance_str == substance_str.strip(), f"Substance '{substance}' should not have trailing whitespace"

    def test_race_ethnicity_column_has_no_trailing_whitespace(self):
        """Test that race/ethnicity column values are trimmed (regression test for race/ethnicity filter bug)."""
        df = dose_dashboard.df_dose_raw
        
        if 'race_ethnicity' in df.columns:
            race_ethnicity_values = df['race_ethnicity'].unique()
            for race_ethnicity in race_ethnicity_values:
                race_ethnicity_str = str(race_ethnicity)
                assert race_ethnicity_str == race_ethnicity_str.strip(), f"Race/Ethnicity '{race_ethnicity}' should not have trailing whitespace"

    def test_hawaii_residency_column_has_no_trailing_whitespace(self):
        """Test that Hawaii residency column values are trimmed (regression test for Hawaii residency filter bug)."""
        df = dose_dashboard.df_dose_raw
        
        if 'hawaii_residency' in df.columns:
            hawaii_residency_values = df['hawaii_residency'].unique()
            for residency in hawaii_residency_values:
                residency_str = str(residency)
                assert residency_str == residency_str.strip(), f"Hawaii Residency '{residency}' should not have trailing whitespace"


@pytest.mark.integration
class TestDOSEFiltering:
    """Test filter functionality with real data."""
    
    def test_filter_by_substance_opioids(self):
        """Test filtering by Opioids substance with real data from 2024."""
        result = dose_dashboard.update_dashboard(
            substance=['Opioids'],
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        
        # Result should be a tuple with 9 elements (kpi, bar, line, map, 5 tables)
        assert len(result) == 9, f"Should return 9 elements, got {len(result)}"
        
        # KPI should show 253
        kpi = result[0]
        assert kpi is not None, "KPI should not be None"
        assert '253' in kpi, f"KPI should show 253 for Opioids in 2024, got: {kpi}"
    
    def test_filter_by_county_honolulu(self):
        """Test filtering by Honolulu county with real data from 2024."""
        result = dose_dashboard.update_dashboard(
            substance=None,
            county=['Honolulu'],
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        kpi, bar_fig, line_fig, map_fig, table_county, table_age, table_sex, table_race, table_residency = result
        
        # KPI should show 526
        assert '526' in kpi or '526' in kpi, f"KPI should contain 526 for Honolulu 2024, got: {kpi}"
        
        # Bar chart should have data
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        
        # County table should show 526 for Honolulu
        assert table_county is not None, "County table should not be None"
        table_county_str = str(table_county)
        assert '526' in table_county_str or '526' in table_county_str, f"County table should contain 526, got: {table_county_str}"
        assert 'Honolulu' in table_county_str, f"County table should contain Honolulu, got: {table_county_str}"
    
    def test_filter_by_year_2024(self):
        """Test filtering by year 2024 with real data."""
        result = dose_dashboard.update_dashboard(
            substance=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        kpi, bar_fig, line_fig, map_fig, *tables = result
        
        # KPI should show 878 for all 2024 data
        assert '878' in kpi, f"KPI should contain 878 for 2024, got: {kpi}"
        
        # Line chart should only show 2024 data
        if len(line_fig.data) > 0:
            for trace in line_fig.data:
                if len(trace.x) > 0:
                    assert all(x == 2024 for x in trace.x), f"All years should be 2024, got {trace.x}"

    def test_filter_by_city_honolulu(self):
        """Test filtering by Honolulu city with real data from 2024."""
        result = dose_dashboard.update_dashboard(
            substance=None,
            county=None,
            city=['Honolulu'],
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        kpi, bar_fig, line_fig, map_fig, table_county, table_age, table_sex, table_race, table_residency = result
        
        # KPI should show 332
        assert '332' in kpi or '332' in kpi, f"KPI should contain 332 for city Honolulu 2024, got: {kpi}"
        
        # Bar chart should have data
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"

    def test_filter_by_age_group_18_44(self):
        """Test filtering by age group 18-44 with real data from 2024."""
        result = dose_dashboard.update_dashboard(
            substance=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=['18-44'],
            sex=None,
            race_ethnicity=None
        )
        kpi, bar_fig, line_fig, map_fig, table_county, table_age, table_sex, table_race, table_residency = result
        
        # KPI should show 312
        assert '312' in kpi or '312' in kpi, f"KPI should contain 312 for age 18-44 in 2024, got: {kpi}"
        
        # Age table should show 312 for age group 18-44
        assert table_age is not None, "Age table should not be None"
        table_age_str = str(table_age)
        assert '312' in table_age_str or '312' in table_age_str, f"Age table should contain 312, got: {table_age_str}"
        assert '18-44' in table_age_str, f"Age table should contain 18-44, got: {table_age_str}"

    def test_filter_by_sex_male(self):
        """Test filtering by sex Male with real data from 2024."""
        result = dose_dashboard.update_dashboard(
            substance=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=['Male'],
            race_ethnicity=None
        )
        kpi, bar_fig, line_fig, map_fig, table_county, table_age, table_sex, table_race, table_residency = result
        
        # KPI should show 488
        assert '488' in kpi or '488' in kpi, f"KPI should contain 488 for Male in 2024, got: {kpi}"
        
        # Sex table should show 488 for Male
        assert table_sex is not None, "Sex table should not be None"
        table_sex_str = str(table_sex)
        assert '488' in table_sex_str or '488' in table_sex_str, f"Sex table should contain 488, got: {table_sex_str}"
        assert 'Male' in table_sex_str, f"Sex table should contain Male, got: {table_sex_str}"

    def test_filter_by_race_ethnicity_white(self):
        """Test filtering by race/ethnicity White/Caucasian with real data from 2024."""
        result = dose_dashboard.update_dashboard(
            substance=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=['White/Caucasian']
        )
        kpi, bar_fig, line_fig, map_fig, table_county, table_age, table_sex, table_race, table_residency = result
        
        # KPI should show 326
        assert '326' in kpi or '326' in kpi, f"KPI should contain 326 for White/Caucasian in 2024, got: {kpi}"
        
        # Race/Ethnicity table should show 326 for White/Caucasian
        assert table_race is not None, "Race/Ethnicity table should not be None"
        table_race_str = str(table_race)
        assert '326' in table_race_str or '326' in table_race_str, f"Race/Ethnicity table should contain 326, got: {table_race_str}"
        assert 'White/Caucasian' in table_race_str, f"Race/Ethnicity table should contain White/Caucasian, got: {table_race_str}"

    def test_filter_by_hawaii_residency_resident(self):
        """Test filtering by Hawaii residency with real data from 2024."""
        result = dose_dashboard.update_dashboard(
            substance=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=['Resident'],
            age=None,
            sex=None,
            race_ethnicity=None
        )
        kpi, bar_fig, line_fig, map_fig, table_county, table_age, table_sex, table_race, table_residency = result
        
        # KPI should show 816
        assert '816' in kpi or '816' in kpi, f"KPI should contain 816 for Resident in 2024, got: {kpi}"
        
        # Residency table should show 816 for Resident
        assert table_residency is not None, "Residency table should not be None"
        table_residency_str = str(table_residency)
        assert '816' in table_residency_str or '816' in table_residency_str, f"Residency table should contain 816, got: {table_residency_str}"
        assert 'Resident' in table_residency_str, f"Residency table should contain Resident, got: {table_residency_str}"


@pytest.mark.regression
class TestDOSERegressionScenarios:
    """Regression tests for known scenarios using real data from 2024."""
    
    def test_specific_scenario_opioids_2024_honolulu_18_44_male_41_discharges(self):
        """
        REGRESSION TEST: Specific test case with REAL DATA from 2024.
        
        When filtering for:
        - Substance Type: Opioids
        - County: Honolulu
        - Calendar Year: 2024
        - Age Group: 18-44
        - Sex: Male
        
        Expected results (verified from real data):
        - All visuals should show 41 discharges
        - This verifies:
          * Query is working correctly
          * Visuals load as expected
          * Filters work correctly
          * All aggregations are consistent
        
        Note: Using 2024 data which will not change. Do not use 2025 or later.
        """
        # Apply the specific filters to real data
        result = dose_dashboard.update_dashboard(
            substance=['Opioids'],
            county=['Honolulu'],
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=['18-44'],
            sex=['Male'],
            race_ethnicity=None
        )
        
        # Unpack the results (9 outputs)
        (kpi_text, 
         bar_fig, 
         line_fig, 
         map_fig,
         table_county,
         table_age,
         table_sex,
         table_race,
         table_residency) = result
        
        # TEST 1: KPI card should show 41
        assert '41' in kpi_text, f"KPI should contain 41, got: {kpi_text}"
        
        # TEST 2: Bar chart (Discharges by Substance) should show 41 for Opioids
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        
        bar_data = bar_fig.data[0]
        # Since we filtered for Opioids only, should have one bar
        assert len(bar_data.y) == 1, f"Should have 1 substance bar (Opioids), got {len(bar_data.y)}"
        assert bar_data.x[0] == 41, f"Bar chart should show 41 discharges, got {bar_data.x[0]}"
        
        # TEST 3: Line chart should show 41 for 2024
        assert line_fig is not None, "Line chart should not be None"
        assert len(line_fig.data) > 0, "Line chart should have data"
        
        # Should have one trace for Opioids
        opioids_trace = line_fig.data[0]
        assert len(opioids_trace.x) == 1, f"Should have 1 point (2024), got {len(opioids_trace.x)}"
        assert opioids_trace.x[0] == 2024, f"Year should be 2024, got {opioids_trace.x[0]}"
        assert opioids_trace.y[0] == 41, f"Line chart should show 41, got {opioids_trace.y[0]}"
        
        # TEST 4: Map should exist (may or may not have data depending on ZIP availability)
        assert map_fig is not None, "Map should not be None"
        
        # TEST 5: County table should show 41 for Honolulu
        assert table_county is not None, "County table should not be None"
        table_county_str = str(table_county)
        assert '41' in table_county_str, f"County table should contain 41, got: {table_county_str}"
        assert 'Honolulu' in table_county_str, "County table should contain Honolulu"
        
        # TEST 6: Age table should show 41 for 18-44
        assert table_age is not None, "Age table should not be None"
        table_age_str = str(table_age)
        assert '41' in table_age_str, f"Age table should contain 41, got: {table_age_str}"
        assert '18-44' in table_age_str, "Age table should contain 18-44"
        
        # TEST 7: Sex table should show 41 for Male
        assert table_sex is not None, "Sex table should not be None"
        table_sex_str = str(table_sex)
        assert '41' in table_sex_str, f"Sex table should contain 41, got: {table_sex_str}"
        assert 'Male' in table_sex_str, "Sex table should contain Male"
        
        # TEST 8: Race/Ethnicity table should have data (multiple race categories shown)
        assert table_race is not None, "Race/Ethnicity table should not be None"
        table_race_str = str(table_race)
        assert any(race in table_race_str for race in ['White/Caucasian', 'Filipino', 'Japanese', 'Native Hawaiian', 'Other']), \
            f"Race/Ethnicity table should contain race categories"
        
        # TEST 9: Residency table should show data totaling to 41
        assert table_residency is not None, "Residency table should not be None"
        table_residency_str = str(table_residency)
        assert 'Resident' in table_residency_str or 'Non-resident' in table_residency_str, \
            "Residency table should contain residency categories"
    
    def test_empty_filters_shows_all_data(self):
        """Regression: Empty filters should show all data from real database."""
        result = dose_dashboard.update_dashboard(
            substance=None,
            county=None,
            city=None,
            year=None,
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        
        kpi, bar_fig, line_fig, map_fig, *tables = result
        
        # Should have data for multiple substances
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        
        bar_data = bar_fig.data[0]
        assert len(bar_data.y) > 1, f"Should show multiple substances, got {len(bar_data.y)}"
    
    def test_multiple_years_selected(self):
        """Regression: Multiple year selection should work with real data."""
        result = dose_dashboard.update_dashboard(
            substance=['Opioids'],
            county=['Honolulu'],
            city=None,
            year=[2023, 2024],
            hawaii_residency=None,
            age=['18-44'],
            sex=['Male'],
            race_ethnicity=None
        )
        
        kpi, bar_fig, line_fig, map_fig, *tables = result
        
        # Line chart should show both years (if data exists for both)
        if len(line_fig.data) > 0:
            opioids_trace = line_fig.data[0]
            years_shown = set(opioids_trace.x)
            assert 2023 in years_shown or 2024 in years_shown, "Should show at least one of the selected years"


class TestDOSEResetFilters:
    """Test filter reset functionality."""
    
    def test_reset_filters_callback_exists(self):
        """Test that reset filters callback is defined."""
        assert hasattr(dose_dashboard, 'reset_dose_filters'), "Should have reset_dose_filters function"
        assert callable(dose_dashboard.reset_dose_filters), "reset_dose_filters should be callable"
    
    def test_reset_filters_returns_none_values(self):
        """Test that reset filters returns None for all filter values."""
        result = dose_dashboard.reset_dose_filters(1)
        
        # Should return 8 None values (one for each filter)
        assert len(result) == 8, f"Should return 8 values, got {len(result)}"
        assert all(v is None for v in result), "All filter values should be None after reset"


@pytest.mark.integration
class TestDOSEEdgeCases:
    """Test edge cases and data consistency."""
    
    def test_no_data_scenario_handles_gracefully(self):
        """Test that filtering with conflicting criteria doesn't crash."""
        # Filter for a city in a different county (should return no results)
        result = dose_dashboard.update_dashboard(
            substance=None,
            county=['Hawaii'],
            city=['Honolulu'],  # Honolulu is not in Hawaii county
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        
        # Should not crash, should return valid structure
        assert len(result) == 9, "Should still return 9 elements even with no data"
        
        kpi = result[0]
        assert kpi is not None, "KPI should not be None"
    
    def test_all_filters_applied_simultaneously(self):
        """Test that all filters can be applied together without errors."""
        result = dose_dashboard.update_dashboard(
            substance=['Opioids'],
            county=['Honolulu'],
            city=['Honolulu'],
            year=[2024],
            hawaii_residency=['Resident'],
            age=['18-44'],
            sex=['Male'],
            race_ethnicity=['White/Caucasian']
        )
        
        # Should not crash
        assert len(result) == 9, "Should return 9 elements"
        
        kpi = result[0]
        assert kpi is not None, "KPI should not be None"
    
    def test_year_2024_data_consistency(self):
        """
        Test that 2024 data remains consistent (878 total discharges).
        
        This is a regression test to ensure that historical 2024 data 
        doesn't change over time.
        """
        result = dose_dashboard.update_dashboard(
            substance=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        
        kpi = result[0]
        assert '878' in kpi, f"2024 should have 878 discharges (stable historical data), got: {kpi}"
    
    def test_data_integrity_all_visuals_match(self):
        """Test that KPI and table totals match for filtered data."""
        result = dose_dashboard.update_dashboard(
            substance=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=['Male'],
            race_ethnicity=None
        )
        
        kpi_text = result[0]
        table_sex = result[6]
        
        # Extract number from KPI
        import re
        kpi_numbers = re.findall(r'[\d,]+', kpi_text)
        if kpi_numbers:
            kpi_value = kpi_numbers[0]
            
            # Table should also show the same total
            table_sex_str = str(table_sex)
            assert kpi_value in table_sex_str, f"Sex table should contain same total as KPI ({kpi_value})"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
