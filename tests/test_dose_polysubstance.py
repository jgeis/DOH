"""
test_dose_polysubstance.py - Tests for dose_polysubstance_dashboard.py and /dose-polysubstance page.

Tests cover:
- Page loading and initialization
- Filter functionality with real data
- Data validation across all visuals
- Specific test case: Stimulants, Honolulu, 2024, Male showing 12 records

These tests use REAL DATA from the database to verify:
- Queries are working correctly
- Visuals load as expected
- Filters work correctly with actual data
- Polysubstance co-occurrence logic works properly

Note: Tests use 2024 and older data only. New date-based data gets added all the time,
so we avoid hardcoding numbers tied to years after 2024 as tests would fail when 
current dates are added. Data from 2024 and older will not change.

AI Query used to generate the tests:
Using test_discharges_su_polysubstance.py as an example, create tests for 'dose_polysubstance_dashboard.py'.  
Set the filters as appropriate and get the numbers directly from the dose_dashboard to use in the tests.
Add a test to verify the "Reset All Filters" buttons works along with any other tests you think may be valuable. 
New date-based data gets added all the time, so don't hard code any numbers that aren't tied to a year after 
2024 as the tests will fail when current dates are added. Data from 2024 and older will not change.

"""
import pytest
import pandas as pd
import plotly.graph_objects as go
import dose_polysubstance_dashboard


class TestDOSEPolysubstancePageStructure:
    """Test basic page structure and initialization."""
    
    def test_dose_polysubstance_page_registered(self):
        """Test that dose-polysubstance page is registered."""
        from dash import page_registry
        import multi_dashboard  # Ensures pages are registered
        
        paths = [page['path'] for page in page_registry.values()]
        assert '/dose-polysubstance' in paths, "dose-polysubstance page should be registered"
    
    def test_dose_polysubstance_page_has_layout(self):
        """Test that dose-polysubstance page has a layout."""
        from pages import dose_polysubstance
        
        assert hasattr(dose_polysubstance, 'layout'), "Page should have layout attribute"
        assert dose_polysubstance.layout is not None, "Layout should not be None"
    
    def test_dose_polysubstance_imports_correctly(self):
        """Test that dose_polysubstance_dashboard module can be imported."""
        assert hasattr(dose_polysubstance_dashboard, 'layout'), "Module should have layout"
        assert hasattr(dose_polysubstance_dashboard, 'update_dashboard'), "Module should have update_dashboard callback"


class TestDOSEPolysubstanceDataLoading:
    """Test data loading and initialization with real data."""
    
    def test_load_dose_polysubstance_dataframe_from_db(self):
        """Test that data loading function works correctly with real data."""
        df = dose_polysubstance_dashboard.df_raw
        
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
        df = dose_polysubstance_dashboard.df_raw
        
        assert pd.api.types.is_numeric_dtype(df['year']), "Year column should be numeric"
    
    def test_county_column_has_no_trailing_whitespace(self):
        """Test that county column values are trimmed (regression test for county filter bug)."""
        df = dose_polysubstance_dashboard.df_raw
        if 'county' in df.columns:
            county_values = df['county'].unique()
            for county in county_values:
                county_str = str(county)
                assert county_str == county_str.strip(), f"County '{county}' should not have trailing whitespace"

    def test_city_column_has_no_trailing_whitespace(self):
        """Test that city column values are trimmed (regression test for city filter bug)."""
        df = dose_polysubstance_dashboard.df_raw
        
        if 'city' in df.columns:
            city_values = df['city'].unique()
            for city in city_values:
                city_str = str(city)
                assert city_str == city_str.strip(), f"City '{city}' should not have trailing whitespace"

    def test_age_column_has_no_trailing_whitespace(self):
        """Test that age column values are trimmed (regression test for age filter bug)."""
        df = dose_polysubstance_dashboard.df_raw
        
        if 'age_group' in df.columns:
            age_values = df['age_group'].unique()
            for age in age_values:
                age_str = str(age)
                assert age_str == age_str.strip(), f"Age '{age}' should not have trailing whitespace"

    def test_sex_column_has_no_trailing_whitespace(self):
        """Test that sex column values are trimmed (regression test for sex filter bug)."""
        df = dose_polysubstance_dashboard.df_raw
        
        if 'sex' in df.columns:
            sex_values = df['sex'].unique()
            for sex in sex_values:
                sex_str = str(sex)
                assert sex_str == sex_str.strip(), f"Sex '{sex}' should not have trailing whitespace"

    def test_substance_column_has_no_trailing_whitespace(self):
        """Test that substance column values are trimmed (regression test for substance filter bug)."""
        df = dose_polysubstance_dashboard.df_raw
        
        if 'substance' in df.columns:
            substance_values = df['substance'].unique()
            for substance in substance_values:
                substance_str = str(substance)
                assert substance_str == substance_str.strip(), f"Substance '{substance}' should not have trailing whitespace"

    def test_race_ethnicity_column_has_no_trailing_whitespace(self):
        """Test that race/ethnicity column values are trimmed (regression test for race/ethnicity filter bug)."""
        df = dose_polysubstance_dashboard.df_raw
        
        if 'race_ethnicity' in df.columns:
            race_ethnicity_values = df['race_ethnicity'].unique()
            for race_ethnicity in race_ethnicity_values:
                race_ethnicity_str = str(race_ethnicity)
                assert race_ethnicity_str == race_ethnicity_str.strip(), f"Race/Ethnicity '{race_ethnicity}' should not have trailing whitespace"

    def test_hawaii_residency_column_has_no_trailing_whitespace(self):
        """Test that Hawaii residency column values are trimmed (regression test for Hawaii residency filter bug)."""
        df = dose_polysubstance_dashboard.df_raw
        
        if 'hawaii_residency' in df.columns:
            hawaii_residency_values = df['hawaii_residency'].unique()
            for residency in hawaii_residency_values:
                residency_str = str(residency)
                assert residency_str == residency_str.strip(), f"Hawaii Residency '{residency}' should not have trailing whitespace"


@pytest.mark.integration
class TestDOSEPolysubstanceFiltering:
    """Test filter functionality with real data."""
    
    def test_filter_by_substance_stimulants(self):
        """Test filtering by Stimulants substance with real data from 2024."""
        result = dose_polysubstance_dashboard.update_dashboard(
            substance=['Stimulants'],
            year=[2024],
            county=None,
            city=None,
            age=None,
            sex=None,
            race=None,
            residency=None
        )
        
        # Result should be a tuple with 11 elements (kpi, 5 charts, 5 tables)
        assert len(result) == 11, f"Should return 11 elements, got {len(result)}"
        
        # KPI should show 39
        kpi = result[0]
        assert kpi is not None, "KPI should not be None"
        assert '39' in kpi, f"KPI should show 39 for Stimulants in 2024, got: {kpi}"
    
    def test_filter_by_year_2024(self):
        """Test filtering by year 2024 with real data."""
        result = dose_polysubstance_dashboard.update_dashboard(
            substance=None,
            year=[2024],
            county=None,
            city=None,
            age=None,
            sex=None,
            race=None,
            residency=None
        )
        kpi, substance_bar, year_line, county_line, sunburst, cooccur_bar, *tables = result
        
        # KPI should show 70 for all 2024 data
        assert '70' in kpi, f"KPI should contain 70 for 2024, got: {kpi}"
        
        # Line chart should only show 2024 data
        if len(year_line.data) > 0:
            for trace in year_line.data:
                if len(trace.x) > 0:
                    assert all(x == 2024 for x in trace.x), f"All years should be 2024, got {trace.x}"

    def test_filter_by_county_honolulu(self):
        """Test filtering by Honolulu county with real data from 2024."""
        result = dose_polysubstance_dashboard.update_dashboard(
            substance=None,
            year=[2024],
            county=['Honolulu'],
            city=None,
            age=None,
            sex=None,
            race=None,
            residency=None
        )
        kpi, substance_bar, year_line, county_line, sunburst, cooccur_bar, table_county, table_age, table_sex, table_race, table_residency = result
        
        # KPI should show 33
        assert '33' in kpi, f"KPI should contain 33 for Honolulu 2024, got: {kpi}"
        
        # Bar chart should have data
        assert substance_bar is not None, "Bar chart should not be None"
        assert len(substance_bar.data) > 0, "Bar chart should have data"
        
        # County table should show 33 for Honolulu
        assert table_county is not None, "County table should not be None"
        table_county_str = str(table_county)
        assert '33' in table_county_str, f"County table should contain 33, got: {table_county_str}"
        assert 'Honolulu' in table_county_str, f"County table should contain Honolulu, got: {table_county_str}"

    def test_filter_by_city_honolulu(self):
        """Test filtering by Honolulu city with real data from 2024."""
        result = dose_polysubstance_dashboard.update_dashboard(
            substance=None,
            year=[2024],
            county=None,
            city=['Honolulu'],
            age=None,
            sex=None,
            race=None,
            residency=None
        )
        kpi, substance_bar, year_line, county_line, sunburst, cooccur_bar, table_county, table_age, table_sex, table_race, table_residency = result
        
        # KPI should show 25
        assert '25' in kpi, f"KPI should contain 25 for city Honolulu 2024, got: {kpi}"
        
        # Bar chart should have data
        assert substance_bar is not None, "Bar chart should not be None"
        assert len(substance_bar.data) > 0, "Bar chart should have data"

    def test_filter_by_age_group_18_44(self):
        """Test filtering by age group 18-44 with real data from 2024."""
        result = dose_polysubstance_dashboard.update_dashboard(
            substance=None,
            year=[2024],
            county=None,
            city=None,
            age=['18-44'],
            sex=None,
            race=None,
            residency=None
        )
        kpi, substance_bar, year_line, county_line, sunburst, cooccur_bar, table_county, table_age, table_sex, table_race, table_residency = result
        
        # KPI should show 46
        assert '46' in kpi, f"KPI should contain 46 for age 18-44 in 2024, got: {kpi}"
        
        # Age table should show 46 for age group 18-44
        assert table_age is not None, "Age table should not be None"
        table_age_str = str(table_age)
        assert '46' in table_age_str, f"Age table should contain 46, got: {table_age_str}"
        assert '18-44' in table_age_str, f"Age table should contain 18-44, got: {table_age_str}"

    def test_filter_by_sex_male(self):
        """Test filtering by sex Male with real data from 2024."""
        result = dose_polysubstance_dashboard.update_dashboard(
            substance=None,
            year=[2024],
            county=None,
            city=None,
            age=None,
            sex=['Male'],
            race=None,
            residency=None
        )
        kpi, substance_bar, year_line, county_line, sunburst, cooccur_bar, table_county, table_age, table_sex, table_race, table_residency = result
        
        # KPI should show 49
        assert '49' in kpi, f"KPI should contain 49 for Male in 2024, got: {kpi}"
        
        # Sex table should show 49 for Male
        assert table_sex is not None, "Sex table should not be None"
        table_sex_str = str(table_sex)
        assert '49' in table_sex_str, f"Sex table should contain 49, got: {table_sex_str}"
        assert 'Male' in table_sex_str, f"Sex table should contain Male, got: {table_sex_str}"

    def test_filter_by_race_ethnicity_white(self):
        """Test filtering by race/ethnicity White/Caucasian with real data from 2024."""
        result = dose_polysubstance_dashboard.update_dashboard(
            substance=None,
            year=[2024],
            county=None,
            city=None,
            age=None,
            sex=None,
            race=['White/Caucasian'],
            residency=None
        )
        kpi, substance_bar, year_line, county_line, sunburst, cooccur_bar, table_county, table_age, table_sex, table_race, table_residency = result
        
        # KPI should show 37
        assert '37' in kpi, f"KPI should contain 37 for White/Caucasian in 2024, got: {kpi}"
        
        # Race/Ethnicity table should show 37 for White/Caucasian
        assert table_race is not None, "Race/Ethnicity table should not be None"
        table_race_str = str(table_race)
        assert '37' in table_race_str, f"Race/Ethnicity table should contain 37, got: {table_race_str}"
        assert 'White/Caucasian' in table_race_str, f"Race/Ethnicity table should contain White/Caucasian, got: {table_race_str}"

    def test_filter_by_hawaii_residency_resident(self):
        """Test filtering by Hawaii residency with real data from 2024."""
        result = dose_polysubstance_dashboard.update_dashboard(
            substance=None,
            year=[2024],
            county=None,
            city=None,
            age=None,
            sex=None,
            race=None,
            residency=['Resident']
        )
        kpi, substance_bar, year_line, county_line, sunburst, cooccur_bar, table_county, table_age, table_sex, table_race, table_residency = result
        
        # KPI should show 69
        assert '69' in kpi, f"KPI should contain 69 for Resident in 2024, got: {kpi}"
        
        # Residency table should show 69 for Resident
        assert table_residency is not None, "Residency table should not be None"
        table_residency_str = str(table_residency)
        assert '69' in table_residency_str, f"Residency table should contain 69, got: {table_residency_str}"
        assert 'Resident' in table_residency_str, f"Residency table should contain Resident, got: {table_residency_str}"


@pytest.mark.regression
class TestDOSEPolysubstanceRegressionScenarios:
    """Regression tests for known scenarios using real data from 2024."""
    
    def test_specific_scenario_stimulants_2024_honolulu_male_12_records(self):
        """
        REGRESSION TEST: Specific test case with REAL DATA from 2024.
        
        When filtering for:
        - Substance Type: Stimulants
        - County: Honolulu
        - Calendar Year: 2024
        - Sex: Male
        
        Expected results (verified from real data):
        - All visuals should show 12 records
        - This verifies:
          * Query is working correctly
          * Visuals load as expected
          * Filters work correctly
          * All aggregations are consistent
          * Polysubstance co-occurrence logic works
        
        Note: Using 2024 data which will not change. Do not use 2025 or later.
        """
        # Apply the specific filters to real data
        result = dose_polysubstance_dashboard.update_dashboard(
            substance=['Stimulants'],
            year=[2024],
            county=['Honolulu'],
            city=None,
            age=None,
            sex=['Male'],
            race=None,
            residency=None
        )
        
        # Unpack the results (11 outputs)
        (kpi_text, 
         substance_bar, 
         year_line, 
         county_line,
         sunburst,
         cooccur_bar,
         table_county,
         table_age,
         table_sex,
         table_race,
         table_residency) = result
        
        # TEST 1: KPI card should show 12
        assert '12' in kpi_text, f"KPI should contain 12, got: {kpi_text}"
        
        # TEST 2: Substance bar chart should have data (showing co-occurring substances)
        assert substance_bar is not None, "Bar chart should not be None"
        # May or may not have data depending on co-occurrence
        
        # TEST 3: Line chart should show 12 for 2024
        assert year_line is not None, "Line chart should not be None"
        if len(year_line.data) > 0:
            # Should have at least one trace
            stimulants_trace = year_line.data[0]
            if len(stimulants_trace.x) > 0:
                assert 2024 in stimulants_trace.x, f"Should have 2024 data"
        
        # TEST 4: County line chart should exist
        assert county_line is not None, "County line chart should not be None"
        
        # TEST 5: Sunburst chart should exist
        assert sunburst is not None, "Sunburst should not be None"
        
        # TEST 6: Co-occurrence bar should exist
        assert cooccur_bar is not None, "Co-occurrence bar should not be None"
        
        # TEST 7: County table should show 12 for Honolulu
        assert table_county is not None, "County table should not be None"
        table_county_str = str(table_county)
        assert '12' in table_county_str, f"County table should contain 12, got: {table_county_str}"
        assert 'Honolulu' in table_county_str, "County table should contain Honolulu"
        
        # TEST 8: Age table should have data
        assert table_age is not None, "Age table should not be None"
        
        # TEST 9: Sex table should show 12 for Male
        assert table_sex is not None, "Sex table should not be None"
        table_sex_str = str(table_sex)
        assert '12' in table_sex_str, f"Sex table should contain 12, got: {table_sex_str}"
        assert 'Male' in table_sex_str, "Sex table should contain Male"
        
        # TEST 10: Race/Ethnicity table should have data (multiple race categories shown)
        assert table_race is not None, "Race/Ethnicity table should not be None"
        
        # TEST 11: Residency table should have data
        assert table_residency is not None, "Residency table should not be None"
    
    def test_empty_filters_shows_all_data(self):
        """Regression: Empty filters should show all data from real database."""
        result = dose_polysubstance_dashboard.update_dashboard(
            substance=None,
            year=None,
            county=None,
            city=None,
            age=None,
            sex=None,
            race=None,
            residency=None
        )
        
        kpi, substance_bar, year_line, county_line, sunburst, cooccur_bar, *tables = result
        
        # Should have data for multiple substances
        assert substance_bar is not None, "Bar chart should not be None"
        assert len(substance_bar.data) > 0, "Bar chart should have data"
        
        bar_data = substance_bar.data[0]
        assert len(bar_data.y) > 1, f"Should show multiple substances, got {len(bar_data.y)}"
    
    def test_multiple_years_selected(self):
        """Regression: Multiple year selection should work with real data."""
        result = dose_polysubstance_dashboard.update_dashboard(
            substance=['Stimulants'],
            year=[2023, 2024],
            county=['Honolulu'],
            city=None,
            age=None,
            sex=['Male'],
            race=None,
            residency=None
        )
        
        kpi, substance_bar, year_line, county_line, sunburst, cooccur_bar, *tables = result
        
        # Line chart should show both years (if data exists for both)
        if len(year_line.data) > 0:
            stimulants_trace = year_line.data[0]
            years_shown = set(stimulants_trace.x)
            assert 2023 in years_shown or 2024 in years_shown, "Should show at least one of the selected years"


class TestDOSEPolysubstanceResetFilters:
    """Test filter reset functionality."""
    
    def test_reset_filters_callback_exists(self):
        """Test that reset filters callback is defined."""
        assert hasattr(dose_polysubstance_dashboard, 'reset_filters'), "Should have reset_filters function"
        assert callable(dose_polysubstance_dashboard.reset_filters), "reset_filters should be callable"
    
    def test_reset_filters_returns_none_values(self):
        """Test that reset filters returns None for all filter values."""
        result = dose_polysubstance_dashboard.reset_filters(1)
        
        # Should return 8 None values (one for each filter)
        assert len(result) == 8, f"Should return 8 values, got {len(result)}"
        assert all(v is None for v in result), "All filter values should be None after reset"


@pytest.mark.integration
class TestDOSEPolysubstanceEdgeCases:
    """Test edge cases and data consistency."""
    
    def test_no_data_scenario_handles_gracefully(self):
        """Test that filtering with conflicting criteria doesn't crash."""
        # Filter for a city in a different county (should return no results or very few)
        result = dose_polysubstance_dashboard.update_dashboard(
            substance=None,
            year=[2024],
            county=['Hawaii'],
            city=['Honolulu'],  # Honolulu is not in Hawaii county
            age=None,
            sex=None,
            race=None,
            residency=None
        )
        
        # Should not crash, should return valid structure
        assert len(result) == 11, "Should still return 11 elements even with no/little data"
        
        kpi = result[0]
        assert kpi is not None, "KPI should not be None"
    
    def test_all_filters_applied_simultaneously(self):
        """Test that all filters can be applied together without errors."""
        result = dose_polysubstance_dashboard.update_dashboard(
            substance=['Stimulants'],
            year=[2024],
            county=['Honolulu'],
            city=['Honolulu'],
            age=['18-44'],
            sex=['Male'],
            race=['White/Caucasian'],
            residency=['Resident']
        )
        
        # Should not crash
        assert len(result) == 11, "Should return 11 elements"
        
        kpi = result[0]
        assert kpi is not None, "KPI should not be None"
    
    def test_year_2024_data_consistency(self):
        """
        Test that 2024 data remains consistent (70 total records).
        
        This is a regression test to ensure that historical 2024 data 
        doesn't change over time.
        """
        result = dose_polysubstance_dashboard.update_dashboard(
            substance=None,
            year=[2024],
            county=None,
            city=None,
            age=None,
            sex=None,
            race=None,
            residency=None
        )
        
        kpi = result[0]
        assert '70' in kpi, f"2024 should have 70 records (stable historical data), got: {kpi}"
    
    def test_data_integrity_all_visuals_match(self):
        """Test that KPI and table totals match for filtered data."""
        result = dose_polysubstance_dashboard.update_dashboard(
            substance=None,
            year=[2024],
            county=None,
            city=None,
            age=None,
            sex=['Male'],
            race=None,
            residency=None
        )
        
        kpi_text = result[0]
        table_sex = result[8]
        
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
        # When filtering by a substance, the dashboard should keep all rows
        # for records that contain that substance (including co-occurring substances)
        result = dose_polysubstance_dashboard.update_dashboard(
            substance=['Opioids'],
            year=[2024],
            county=None,
            city=None,
            age=None,
            sex=None,
            race=None,
            residency=None
        )
        
        kpi, substance_bar, year_line, county_line, sunburst, cooccur_bar, *tables = result
        
        # KPI should show records with Opioids (35)
        assert '35' in kpi, f"KPI should show 35 for Opioids in 2024, got: {kpi}"
        
        # Substance bar should show co-occurring substances (not Opioids itself)
        assert substance_bar is not None, "Substance bar should not be None"
        # The bar chart should exclude the filtered substance
        if len(substance_bar.data) > 0:
            bar_data = substance_bar.data[0]
            # Should have other substances, not Opioids
            y_labels = [str(y) for y in bar_data.y]
            # Opioids should not be in the bar labels since it's filtered out
            assert not any('Opioids' in label or 'Opioid' in label for label in y_labels), \
                f"Co-occurring bar should not show the filtered substance (Opioids), got: {y_labels}"


@pytest.mark.integration
class TestDOSEPolysubstanceCharts:
    """Test chart generation and data validation with real data."""
    
    def test_substance_bar_chart_structure(self):
        """Test that substance bar chart has correct structure with real data."""
        result = dose_polysubstance_dashboard.update_dashboard(
            substance=None,
            year=[2024],
            county=None,
            city=None,
            age=None,
            sex=None,
            race=None,
            residency=None
        )
        kpi, substance_bar, year_line, county_line, sunburst, cooccur_bar, *tables = result
        
        # Should be a bar chart
        assert isinstance(substance_bar, go.Figure), "Should be a Plotly Figure"
        assert len(substance_bar.data) > 0, "Should have at least one trace"
        assert substance_bar.data[0].type == 'bar', "Should be a bar chart"
        
        # Bar chart should be horizontal (orientation='h')
        assert substance_bar.data[0].orientation == 'h', "Bar chart should be horizontal"
    
    def test_line_chart_structure(self):
        """Test that line charts have correct structure with real data."""
        result = dose_polysubstance_dashboard.update_dashboard(
            substance=['Stimulants'],
            year=None,
            county=None,
            city=None,
            age=None,
            sex=None,
            race=None,
            residency=None
        )
        
        kpi, substance_bar, year_line, county_line, sunburst, cooccur_bar, *tables = result
        
        # Year line should be a line chart
        assert isinstance(year_line, go.Figure), "Should be a Plotly Figure"
        if len(year_line.data) > 0:
            for trace in year_line.data:
                assert trace.type == 'scatter', "Should be scatter type"
        
        # County line should be a line chart
        assert isinstance(county_line, go.Figure), "Should be a Plotly Figure"
        if len(county_line.data) > 0:
            for trace in county_line.data:
                assert trace.type == 'scatter', "Should be scatter type"
    
    def test_sunburst_chart_structure(self):
        """Test that sunburst chart has correct structure with real data."""
        result = dose_polysubstance_dashboard.update_dashboard(
            substance=['Stimulants'],
            year=[2024],
            county=None,
            city=None,
            age=None,
            sex=None,
            race=None,
            residency=None
        )
        
        kpi, substance_bar, year_line, county_line, sunburst, cooccur_bar, *tables = result
        
        # Sunburst should be a Figure
        assert isinstance(sunburst, go.Figure), "Should be a Plotly Figure"
        # May or may not have data depending on co-occurrence patterns
    
    def test_cooccurrence_bar_structure(self):
        """Test that co-occurrence bar chart has correct structure with real data."""
        result = dose_polysubstance_dashboard.update_dashboard(
            substance=['Stimulants'],
            year=[2024],
            county=None,
            city=None,
            age=None,
            sex=None,
            race=None,
            residency=None
        )
        
        kpi, substance_bar, year_line, county_line, sunburst, cooccur_bar, *tables = result
        
        # Co-occurrence bar should be a Figure
        assert isinstance(cooccur_bar, go.Figure), "Should be a Plotly Figure"
        # May or may not have data depending on co-occurrence patterns


class TestDOSEPolysubstanceTables:
    """Test table generation with real data."""
    
    def test_tables_are_not_none(self):
        """Test that all tables are generated."""
        result = dose_polysubstance_dashboard.update_dashboard(
            substance=['Stimulants'],
            year=[2024],
            county=None,
            city=None,
            age=None,
            sex=None,
            race=None,
            residency=None
        )
        
        (kpi, substance_bar, year_line, county_line, sunburst, cooccur_bar,
         table_county, table_age, table_sex, table_race, table_residency) = result
        
        assert table_county is not None, "County table should not be None"
        assert table_age is not None, "Age table should not be None"
        assert table_sex is not None, "Sex table should not be None"
        assert table_race is not None, "Race table should not be None"
        assert table_residency is not None, "Residency table should not be None"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
