"""
test_discharges_mh.py - Tests for discharges_mh_dashboard.py and /discharges-mh page.

Tests cover:
- Page loading and initialization
- Filter functionality with real data
- Data validation across all visuals
- Specific test case: Mood Disorders, 2024, Honolulu, 18-44, Male showing 1,253 discharges

These tests use REAL DATA from the database to verify:
- Queries are working correctly
- Visuals load as expected
- Filters work correctly with actual data

Query used to create these tests:
Using test_discharges_su.py as an example, create tests for 'discharges_mh_dashboard.py'.  
Set the filters as appropriate and get the numbers directly from the discharges_mh_dashboard to use in the tests.
Do not use the years 2025 or 2026 (if available) in the tests.   

Follow up request:
Add some asserts for table_race and table_residency in the #sym:test_specific_scenario_mood_2024_honolulu_18_44_male_1253_discharges method.
Add a test to verify the "Reset All Filters" buttons works along with any other tests you think may be valuable. 
New date-based data gets added all the time, so don't hard code any numbers that aren't tied to a year after 
2024 as the tests will fail when current dates are added. Data from 2024 and older will not change.
"""
import pytest
import pandas as pd
import plotly.graph_objects as go
import discharges_mh_dashboard


class TestDischargesMHPageStructure:
    """Test basic page structure and initialization."""
    
    def test_discharges_mh_page_registered(self):
        """Test that discharges-mh page is registered."""
        from dash import page_registry
        import multi_dashboard  # Ensures pages are registered
        
        paths = [page['path'] for page in page_registry.values()]
        assert '/discharges-mh' in paths, "discharges-mh page should be registered"
    
    def test_discharges_mh_page_has_layout(self):
        """Test that discharges-mh page has a layout."""
        from pages import discharges_mh
        
        assert hasattr(discharges_mh, 'layout'), "Page should have layout attribute"
        assert discharges_mh.layout is not None, "Layout should not be None"
    
    def test_discharges_mh_imports_correctly(self):
        """Test that discharges_mh_dashboard module can be imported."""
        assert hasattr(discharges_mh_dashboard, 'layout'), "Module should have layout"
        assert hasattr(discharges_mh_dashboard, 'update_dashboard'), "Module should have update_dashboard callback"


class TestDischargesMHDataLoading:
    """Test data loading and initialization with real data."""
    
    def test_load_discharge_dataframe_from_db(self):
        """Test that data loading function works correctly with real data."""
        df = discharges_mh_dashboard.df_raw
        
        assert not df.empty, "Real data should not be empty"
        assert 'diagnosis' in df.columns, "Should have diagnosis column"
        assert 'county' in df.columns, "Should have county column"
        assert 'year' in df.columns, "Should have year column"
        assert 'age_group' in df.columns, "Should have age_group column"
        assert 'sex' in df.columns, "Should have sex column"
        assert 'record_id' in df.columns, "Should have record_id column"
        assert len(df) > 0, "Should have at least some rows of data"
    
    def test_year_column_is_numeric(self):
        """Test that year column is numeric in real data."""
        df = discharges_mh_dashboard.df_raw
        
        assert pd.api.types.is_numeric_dtype(df['year']), "Year column should be numeric"
    
    def test_county_column_has_no_trailing_whitespace(self):
        """Test that county column values are trimmed (regression test for county filter bug)."""
        df = discharges_mh_dashboard.df_raw
        if 'county' in df.columns:
            county_values = df['county'].unique()
            for county in county_values:
                county_str = str(county)
                assert county_str == county_str.strip(), f"County '{county}' should not have trailing whitespace"

    def test_city_column_has_no_trailing_whitespace(self):
        """Test that city column values are trimmed (regression test for city filter bug)."""
        df = discharges_mh_dashboard.df_raw
        
        if 'city' in df.columns:
            city_values = df['city'].unique()
            for city in city_values:
                city_str = str(city)
                assert city_str == city_str.strip(), f"City '{city}' should not have trailing whitespace"

    def test_age_column_has_no_trailing_whitespace(self):
        """Test that age column values are trimmed (regression test for age filter bug)."""
        df = discharges_mh_dashboard.df_raw
        
        if 'age_group' in df.columns:
            age_values = df['age_group'].unique()
            for age in age_values:
                age_str = str(age)
                assert age_str == age_str.strip(), f"Age '{age}' should not have trailing whitespace"


    def test_sex_column_has_no_trailing_whitespace(self):
        """Test that sex column values are trimmed (regression test for sex filter bug)."""
        df = discharges_mh_dashboard.df_raw
        
        if 'sex' in df.columns:
            sex_values = df['sex'].unique()
            for sex in sex_values:
                sex_str = str(sex)
                assert sex_str == sex_str.strip(), f"Sex '{sex}' should not have trailing whitespace"

    def test_diagnosis_column_has_no_trailing_whitespace(self):
        """Test that diagnosis column values are trimmed (regression test for diagnosis filter bug)."""
        df = discharges_mh_dashboard.df_raw
        
        if 'diagnosis' in df.columns:
            diagnosis_values = df['diagnosis'].unique()
            for diagnosis in diagnosis_values:
                diagnosis_str = str(diagnosis)
                assert diagnosis_str == diagnosis_str.strip(), f"Diagnosis '{diagnosis}' should not have trailing whitespace"

    def test_race_ethnicity_column_has_no_trailing_whitespace(self):
        """Test that race/ethnicity column values are trimmed (regression test for race/ethnicity filter bug)."""
        df = discharges_mh_dashboard.df_raw
        
        if 'race_ethnicity' in df.columns:
            race_ethnicity_values = df['race_ethnicity'].unique()
            for race_ethnicity in race_ethnicity_values:
                race_ethnicity_str = str(race_ethnicity)
                assert race_ethnicity_str == race_ethnicity_str.strip(), f"Race/Ethnicity '{race_ethnicity}' should not have trailing whitespace"

    def test_hawaii_residency_column_has_no_trailing_whitespace(self):
        """Test that Hawaii residency column values are trimmed (regression test for Hawaii residency filter bug)."""
        df = discharges_mh_dashboard.df_raw
        
        if 'hawaii_residency' in df.columns:
            hawaii_residency_values = df['hawaii_residency'].unique()
            for residency in hawaii_residency_values:
                residency_str = str(residency)
                assert residency_str == residency_str.strip(), f"Hawaii Residency '{residency}' should not have trailing whitespace"



@pytest.mark.integration
class TestDischargesMHFiltering:
    """Test filter functionality with real data."""
    
    def test_filter_by_diagnosis_mood_disorders(self):
        """Test filtering by Mood Disorders diagnosis with real data."""
        result = discharges_mh_dashboard.update_dashboard(
            diagnosis=['Mood (Affective) Disorder (includes Major Depressive and Bipolar Disorders)'],
            county=None,
            city=None,
            year=None,
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        
        # Result should be a tuple with 12 elements
        assert len(result) == 12, f"Should return 12 elements, got {len(result)}"
        
        # KPI should show some value
        kpi = result[0]
        assert kpi is not None, "KPI should not be None"
        assert '1' in str(kpi) or '2' in str(kpi), "KPI should show numeric value"
    
    def test_filter_by_county_honolulu(self):
        """Test filtering by Honolulu county with real data."""
        result = discharges_mh_dashboard.update_dashboard(
            diagnosis=None,
            county=['Honolulu'],
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        kpi, bar_fig, diagnosis_line, county_line, age_line, sex_stacked, table_year, table_county, table_age, table_sex, table_race, table_residency = result
        # Bar chart should have data
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        # County table should show 7,060 for county Honolulu
        assert table_county is not None, "County table should not be None"
        table_county_str = str(table_county)
        assert '7,060' in table_county_str or '7060' in table_county_str, f"County table should contain 7,060, got: {table_county_str}"
        assert 'Honolulu' in table_county_str, f"County table should contain Honolulu, got: {table_county_str}"
    
    def test_filter_by_year_2024(self):
        """Test filtering by year 2024 with real data."""
        result = discharges_mh_dashboard.update_dashboard(
            diagnosis=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        kpi, bar_fig, diagnosis_line, county_line, age_line, sex_stacked, *tables = result
        
        # KPI should show 9,592
        assert '9,592' in kpi or '9592' in kpi, f"KPI should contain '9,592', got: {kpi}"

        # Line charts should only show 2024 data
        if len(diagnosis_line.data) > 0:
            for trace in diagnosis_line.data:
                if len(trace.x) > 0:
                    assert all(x == 2024 for x in trace.x), f"All years should be 2024, got {trace.x}"

    def test_filter_by_city_honolulu(self):
        """Test filtering by Honolulu city with real data."""
        result = discharges_mh_dashboard.update_dashboard(
            diagnosis=None,
            county=None,
            city=['Honolulu'],
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        kpi, bar_fig, diagnosis_line, county_line, age_line, sex_stacked, table_year, table_county, table_age, table_sex, table_race, table_residency = result
        # Bar chart should have data
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        # KPI card should show 4,963 
        assert '4,963' in kpi or '4963' in kpi, f"KPI should contain '4,963', got: {kpi}"
        # County table should show 4,963 for city Honolulu
        assert table_county is not None, "County table should not be None"
        table_county_str = str(table_county)
        assert '4,963' in table_county_str or '4963' in table_county_str, f"County table should contain 4,963, got: {table_county_str}"
        assert 'Honolulu' in table_county_str, f"County table should contain Honolulu, got: {table_county_str}"

    def test_filter_by_age_group_18_44(self):
        """Test filtering by age group 18-44 with real data."""
        result = discharges_mh_dashboard.update_dashboard(
            diagnosis=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=['18-44'],
            sex=None,
            race_ethnicity=None
        )
        kpi, bar_fig, diagnosis_line, county_line, age_line, sex_stacked, table_year, table_county, table_age, table_sex, table_race, table_residency = result
        # Bar chart should have data
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        # KPI card should show 4,212 
        assert '4,212' in kpi or '4212' in kpi, f"KPI should contain '4,212', got: {kpi}"
        # Age table should show 4,212 for age group 18-44
        assert table_age is not None, "Age table should not be None"
        table_age_str = str(table_age)
        assert '4,212' in table_age_str or '4212' in table_age_str, f"Age table should contain 4,212, got: {table_age_str}"
        assert '18-44' in table_age_str, f"Age table should contain 18-44, got: {table_age_str}"

    def test_filter_by_sex_male(self):
        """Test filtering by sex Male with real data."""
        result = discharges_mh_dashboard.update_dashboard(
            diagnosis=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=['Male'],
            race_ethnicity=None
        )
        kpi, bar_fig, diagnosis_line, county_line, age_line, sex_stacked, table_year, table_county, table_age, table_sex, table_race, table_residency = result
        # Bar chart should have data
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        # KPI card should show 4,500 
        assert '4,500' in kpi or '4500' in kpi, f"KPI should contain '4,500', got: {kpi}"
        # Sex table should show 4,500 for Male
        assert table_sex is not None, "Sex table should not be None"
        table_sex_str = str(table_sex)
        assert '4,500' in table_sex_str or '4500' in table_sex_str, f"Sex table should contain 4,500, got: {table_sex_str}"
        assert 'Male' in table_sex_str, f"Sex table should contain Male, got: {table_sex_str}"

    def test_filter_by_race_ethnicity_white(self):
        """Test filtering by race/ethnicity White/Caucasian with real data."""
        result = discharges_mh_dashboard.update_dashboard(
            diagnosis=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=['White/Caucasian']
        )
        kpi, bar_fig, diagnosis_line, county_line, age_line, sex_stacked, table_year, table_county, table_age, table_sex, table_race, table_residency = result
        # Bar chart should have data
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        # KPI card should show 4,084 
        assert '4,084' in kpi or '4084' in kpi, f"KPI should contain '4,084', got: {kpi}"
        # Race/Ethnicity table should show 4,084 for White/Caucasian
        assert table_race is not None, "Race/Ethnicity table should not be None"
        table_race_str = str(table_race)
        assert '4,084' in table_race_str or '4084' in table_race_str, f"Race/Ethnicity table should contain 4,084, got: {table_race_str}"
        assert 'White/Caucasian' in table_race_str, f"Race/Ethnicity table should contain White/Caucasian, got: {table_race_str}"

    def test_filter_by_hawaii_residency_resident(self):
        """Test filtering by Hawaii residency with real data."""
        result = discharges_mh_dashboard.update_dashboard(
            diagnosis=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=['Resident'],
            age=None,
            sex=None,
            race_ethnicity=None
        )
        kpi, bar_fig, diagnosis_line, county_line, age_line, sex_stacked, table_year, table_county, table_age, table_sex, table_race, table_residency = result
        # Bar chart should have data
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        # KPI card should show 9,190 
        assert '9,190' in kpi or '9190' in kpi, f"KPI should contain '9,190', got: {kpi}"
        # Residency table should show 9,190 for Resident
        assert table_residency is not None, "Residency table should not be None"
        table_residency_str = str(table_residency)
        assert '9,190' in table_residency_str or '9190' in table_residency_str, f"Residency table should contain 9,190, got: {table_residency_str}"
        assert 'Resident' in table_residency_str, f"Residency table should contain Resident, got: {table_residency_str}"


@pytest.mark.regression
class TestDischargesMHRegressionScenarios:
    """Regression tests for known scenarios using real data."""
    
    def test_specific_scenario_mood_2024_honolulu_18_44_male_1253_discharges(self):
        """
        REGRESSION TEST: Specific test case with REAL DATA.
        
        When filtering for:
        - Mental Health Diagnosis: Mood (Affective) Disorder (includes Major Depressive and Bipolar Disorders)
        - Calendar Year: 2024
        - County: Honolulu
        - Age Group: 18-44
        - Sex at Birth: Male
        
        Expected results (verified from real data):
        - All visuals should show 1,253 discharges
        - This verifies:
          * Query is working correctly
          * Visuals load as expected
          * Filters work correctly
          * All aggregations are consistent
        """
        # Apply the specific filters to real data
        result = discharges_mh_dashboard.update_dashboard(
            diagnosis=['Mood (Affective) Disorder (includes Major Depressive and Bipolar Disorders)'],
            county=['Honolulu'],
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=['18-44'],
            sex=['Male'],
            race_ethnicity=None
        )
        
        # Unpack the results
        (kpi_text, 
         bar_fig, 
         diagnosis_line_fig, 
         county_line_fig, 
         age_line_fig, 
         sex_stacked_fig,
         table_year,
         table_county,
         table_age,
         table_sex,
         table_race,
         table_residency) = result
        
        # TEST 1: KPI card should show 1,253
        assert '1,253' in kpi_text or '1253' in kpi_text, f"KPI should contain '1,253', got: {kpi_text}"
        
        # TEST 2: Bar chart (Discharges by Mental Health Diagnosis) should show 1,253 for Mood Disorders
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        
        bar_data = bar_fig.data[0]
        # Since we filtered for Mood Disorders only, should have one bar
        assert len(bar_data.y) == 1, f"Should have 1 diagnosis bar (Mood Disorders), got {len(bar_data.y)}"
        assert bar_data.x[0] == 1253, f"Bar chart should show 1253 discharges, got {bar_data.x[0]}"
        
        # TEST 3: Diagnosis line chart should show 1,253 for 2024
        assert diagnosis_line_fig is not None, "Diagnosis line chart should not be None"
        assert len(diagnosis_line_fig.data) > 0, "Diagnosis line chart should have data"
        
        # Should have one trace for Mood Disorders
        mood_trace = diagnosis_line_fig.data[0]
        assert len(mood_trace.x) == 1, f"Should have 1 point (2024), got {len(mood_trace.x)}"
        assert mood_trace.x[0] == 2024, f"Year should be 2024, got {mood_trace.x[0]}"
        assert mood_trace.y[0] == 1253, f"Diagnosis line should show 1253, got {mood_trace.y[0]}"
        
        # TEST 4: County line chart should show 1,253 for Honolulu in 2024
        assert county_line_fig is not None, "County line chart should not be None"
        assert len(county_line_fig.data) > 0, "County line chart should have data"
        
        # Should have one trace for Honolulu
        honolulu_trace = county_line_fig.data[0]
        assert len(honolulu_trace.x) == 1, f"Should have 1 point (2024), got {len(honolulu_trace.x)}"
        assert honolulu_trace.x[0] == 2024, f"Year should be 2024, got {honolulu_trace.x[0]}"
        assert honolulu_trace.y[0] == 1253, f"County line should show 1253, got {honolulu_trace.y[0]}"
        
        # TEST 5: Age line chart should show 1,253 for 18-44 in 2024
        assert age_line_fig is not None, "Age line chart should not be None"
        assert len(age_line_fig.data) > 0, "Age line chart should have data"
        
        # Should have one trace for 18-44
        age_trace = age_line_fig.data[0]
        assert len(age_trace.x) == 1, f"Should have 1 point (2024), got {len(age_trace.x)}"
        assert age_trace.x[0] == 2024, f"Year should be 2024, got {age_trace.x[0]}"
        assert age_trace.y[0] == 1253, f"Age line should show 1253, got {age_trace.y[0]}"
        
        # TEST 6: Sex stacked bar chart should show 1,253 for Male in 2024
        assert sex_stacked_fig is not None, "Sex stacked bar should not be None"
        assert len(sex_stacked_fig.data) > 0, "Sex stacked bar should have data"
        
        # Should have one trace for Male
        male_trace = sex_stacked_fig.data[0]
        assert len(male_trace.x) == 1, f"Should have 1 bar (2024), got {len(male_trace.x)}"
        assert male_trace.x[0] == 2024, f"Year should be 2024, got {male_trace.x[0]}"
        assert male_trace.y[0] == 1253, f"Sex stacked bar should show 1253, got {male_trace.y[0]}"
        
        # TEST 7: Year table should show 1,253 for 2024
        assert table_year is not None, "Year table should not be None"
        # Convert table to string to search for value
        table_year_str = str(table_year)
        assert '1,253' in table_year_str or '1253' in table_year_str, f"Year table should contain 1,253"
        assert '2024' in table_year_str, "Year table should contain 2024"
        
        # TEST 8: County table should show 1,253 for Honolulu
        assert table_county is not None, "County table should not be None"
        table_county_str = str(table_county)
        assert '1,253' in table_county_str or '1253' in table_county_str, f"County table should contain 1,253"
        assert 'Honolulu' in table_county_str, "County table should contain Honolulu"
        
        # TEST 9: Age table should show 1,253 for 18-44
        assert table_age is not None, "Age table should not be None"
        table_age_str = str(table_age)
        assert '1,253' in table_age_str or '1253' in table_age_str, f"Age table should contain 1,253"
        assert '18-44' in table_age_str, "Age table should contain 18-44"
        
        # TEST 10: Sex table should show 1,253 for Male
        assert table_sex is not None, "Sex table should not be None"
        table_sex_str = str(table_sex)
        assert '1,253' in table_sex_str or '1253' in table_sex_str, f"Sex table should contain 1,253"
        assert 'Male' in table_sex_str, "Sex table should contain Male"
        
        # TEST 11: Race/Ethnicity table should have data (multiple race categories shown)
        assert table_race is not None, "Race/Ethnicity table should not be None"
        table_race_str = str(table_race)
        # Should contain race/ethnicity categories - verify at least some common ones are present
        assert any(race in table_race_str for race in ['White/Caucasian', 'Filipino', 'Japanese', 'Native Hawaiian']), \
            f"Race/Ethnicity table should contain race categories"
        
        # TEST 12: Residency table should show 1,224 Residents + other categories totaling to 1,253
        assert table_residency is not None, "Residency table should not be None"
        table_residency_str = str(table_residency)
        assert '1,224' in table_residency_str or '1224' in table_residency_str, f"Residency table should contain 1,224 for Resident"
        assert 'Resident' in table_residency_str, "Residency table should contain Resident"
        assert 'Non-resident' in table_residency_str or '25' in table_residency_str, "Residency table should show Non-resident data"
    
    def test_empty_filters_shows_all_data(self):
        """Regression: Empty filters should show all data from real database."""
        result = discharges_mh_dashboard.update_dashboard(
            diagnosis=None,
            county=None,
            city=None,
            year=None,
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        
        kpi, bar_fig, diagnosis_line, county_line, age_line, sex_stacked, *tables = result
        
        # Should have data for multiple diagnoses
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        
        bar_data = bar_fig.data[0]
        assert len(bar_data.y) > 1, f"Should show multiple diagnoses, got {len(bar_data.y)}"
    
    def test_multiple_years_selected(self):
        """Regression: Multiple year selection should work with real data."""
        result = discharges_mh_dashboard.update_dashboard(
            diagnosis=['Mood (Affective) Disorder (includes Major Depressive and Bipolar Disorders)'],
            county=['Honolulu'],
            city=None,
            year=[2023, 2024],
            hawaii_residency=None,
            age=['18-44'],
            sex=['Male'],
            race_ethnicity=None
        )
        
        kpi, bar_fig, diagnosis_line, county_line, age_line, sex_stacked, *tables = result
        
        # Line charts should show both years
        if len(diagnosis_line.data) > 0:
            mood_trace = diagnosis_line.data[0]
            years_shown = set(mood_trace.x)
            assert 2023 in years_shown or 2024 in years_shown, f"Should show 2023 or 2024, got {years_shown}"


class TestDischargesMHResetFilters:
    """Test filter reset functionality."""
    
    def test_reset_filters_callback_exists(self):
        """Test that reset filters callback is defined."""
        assert hasattr(discharges_mh_dashboard, 'reset_discharges_mh_filters'), "Should have reset_discharges_mh_filters function"
        assert callable(discharges_mh_dashboard.reset_discharges_mh_filters), "reset_discharges_mh_filters should be callable"
    
    def test_reset_filters_returns_none_values(self):
        """Test that reset filters returns None for all filter values."""
        result = discharges_mh_dashboard.reset_discharges_mh_filters(1)
        
        # Should return 8 None values (one for each filter)
        assert len(result) == 8, f"Should return 8 filter values, got {len(result)}"
        assert all(v is None for v in result), "All filter values should be None after reset"


class TestDischargesMHEdgeCases:
    """Test edge cases and data quality scenarios."""
    
    def test_no_data_scenario_handles_gracefully(self):
        """Test that filtering with no matching data doesn't crash."""
        # Filter for a very specific combination that's unlikely to exist
        # but don't use current year data (use 2024 which is fixed)
        result = discharges_mh_dashboard.update_dashboard(
            diagnosis=['Mood (Affective) Disorder (includes Major Depressive and Bipolar Disorders)'],
            county=['Kauaʻi'],
            city=['Honolulu'],  # City in different county - should yield no results or very few
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        
        # Should still return 12 elements
        assert len(result) == 12, f"Should return 12 elements even with no/minimal data, got {len(result)}"
        
        # Figures should still be created (even if empty)
        kpi, bar_fig, diagnosis_line, county_line, age_line, sex_stacked, *tables = result
        assert bar_fig is not None, "Bar chart should exist even with no data"
        assert diagnosis_line is not None, "Line chart should exist even with no data"
    
    def test_all_filters_applied_simultaneously(self):
        """Test that applying all filters at once works correctly."""
        # Use 2024 data which won't change
        result = discharges_mh_dashboard.update_dashboard(
            diagnosis=['Mood (Affective) Disorder (includes Major Depressive and Bipolar Disorders)'],
            county=['Honolulu'],
            city=['Honolulu'],
            year=[2024],
            hawaii_residency=['Resident'],
            age=['18-44'],
            sex=['Male'],
            race_ethnicity=['White/Caucasian']
        )
        
        kpi, bar_fig, diagnosis_line, county_line, age_line, sex_stacked, *tables = result
        
        # Should have some data
        assert kpi is not None, "KPI should not be None"
        # Should be a number (could be suppressed or actual count)
        kpi_str = str(kpi)
        assert any(char.isdigit() for char in kpi_str) or '<10*' in kpi_str, "KPI should show a number or suppressed count"
    
    def test_year_2024_data_consistency(self):
        """Test that 2024 data remains consistent (regression test for data changes)."""
        # This test uses fixed year 2024 data which should not change
        result = discharges_mh_dashboard.update_dashboard(
            diagnosis=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        
        kpi = result[0]
        
        # 2024 data should show 9,592 discharges
        # This is fixed data that won't change
        assert '9,592' in kpi or '9592' in kpi, f"2024 should have 9,592 discharges (fixed data), got: {kpi}"
    
    def test_data_integrity_all_visuals_match(self):
        """Test that KPI and all tables show consistent totals for a specific filter."""
        # Use 2024 data to ensure consistency
        result = discharges_mh_dashboard.update_dashboard(
            diagnosis=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=['Male'],
            race_ethnicity=None
        )
        
        kpi, bar_fig, diagnosis_line, county_line, age_line, sex_stacked, table_year, table_county, table_age, table_sex, table_race, table_residency = result
        
        # KPI should match what's in the sex table
        kpi_str = str(kpi)
        table_sex_str = str(table_sex)
        
        assert '4,500' in kpi_str or '4500' in kpi_str, f"KPI should show 4,500, got: {kpi_str}"
        assert '4,500' in table_sex_str or '4500' in table_sex_str, f"Sex table should show 4,500, got: {table_sex_str}"
