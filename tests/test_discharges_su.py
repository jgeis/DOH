"""
test_discharges_su.py - Tests for discharges_su_dashboard.py and /discharges-su page.

Tests cover:
- Page loading and initialization
- Filter functionality with real data
- Data validation across all visuals
- Specific test case: Alcohol, 2024, Honolulu, 18-44, Male showing 1,473 discharges

These tests use REAL DATA from the database to verify:
- Queries are working correctly
- Visuals load as expected
- Filters work correctly with actual data
"""
import pytest
import pandas as pd
import plotly.graph_objects as go
import discharges_su_dashboard


class TestDischargesSUPageStructure:
    """Test basic page structure and initialization."""
    
    def test_discharges_su_page_registered(self):
        """Test that discharges-su page is registered."""
        from dash import page_registry
        import multi_dashboard  # Ensures pages are registered
        
        paths = [page['path'] for page in page_registry.values()]
        assert '/discharges-su' in paths, "discharges-su page should be registered"
    
    def test_discharges_su_page_has_layout(self):
        """Test that discharges-su page has a layout."""
        from pages import discharges_su
        
        assert hasattr(discharges_su, 'layout'), "Page should have layout attribute"
        assert discharges_su.layout is not None, "Layout should not be None"
    
    def test_discharges_su_imports_correctly(self):
        """Test that discharges_su_dashboard module can be imported."""
        assert hasattr(discharges_su_dashboard, 'layout'), "Module should have layout"
        assert hasattr(discharges_su_dashboard, 'update_dashboard'), "Module should have update_dashboard callback"


class TestDischargesSUDataLoading:
    """Test data loading and initialization with real data."""
    
    def test_load_discharge_dataframe_from_db(self):
        """Test that data loading function works correctly with real data."""
        df = discharges_su_dashboard.df_raw
        
        assert not df.empty, "Real data should not be empty"
        assert 'substance' in df.columns, "Should have substance column"
        assert 'county' in df.columns, "Should have county column"
        assert 'year' in df.columns, "Should have year column"
        assert 'age_group' in df.columns, "Should have age_group column"
        assert 'sex' in df.columns, "Should have sex column"
        assert 'record_id' in df.columns, "Should have record_id column"
        assert len(df) > 0, "Should have at least some rows of data"
    
    def test_year_column_is_numeric(self):
        """Test that year column is numeric in real data."""
        df = discharges_su_dashboard.df_raw
        
        assert pd.api.types.is_numeric_dtype(df['year']), "Year column should be numeric"
    
    def test_county_column_has_no_trailing_whitespace(self):
        """Test that county column values are trimmed (regression test for county filter bug)."""
        df = discharges_su_dashboard.df_raw
        if 'county' in df.columns:
            county_values = df['county'].unique()
            for county in county_values:
                county_str = str(county)
                assert county_str == county_str.strip(), f"County '{county}' should not have trailing whitespace"

    def test_city_column_has_no_trailing_whitespace(self):
        """Test that city column values are trimmed (regression test for city filter bug)."""
        df = discharges_su_dashboard.df_raw
        
        if 'city' in df.columns:
            city_values = df['city'].unique()
            for city in city_values:
                city_str = str(city)
                assert city_str == city_str.strip(), f"City '{city}' should not have trailing whitespace"

    def test_age_column_has_no_trailing_whitespace(self):
        """Test that age column values are trimmed (regression test for age filter bug)."""
        df = discharges_su_dashboard.df_raw
        
        if 'age_group' in df.columns:
            age_values = df['age_group'].unique()
            for age in age_values:
                age_str = str(age)
                assert age_str == age_str.strip(), f"Age '{age}' should not have trailing whitespace"


    def test_sex_column_has_no_trailing_whitespace(self):
        """Test that sex column values are trimmed (regression test for sex filter bug)."""
        df = discharges_su_dashboard.df_raw
        
        if 'sex' in df.columns:
            sex_values = df['sex'].unique()
            for sex in sex_values:
                sex_str = str(sex)
                assert sex_str == sex_str.strip(), f"Sex '{sex}' should not have trailing whitespace"

    def test_substance_column_has_no_trailing_whitespace(self):
        """Test that substance column values are trimmed (regression test for substance filter bug)."""
        df = discharges_su_dashboard.df_raw
        
        if 'substance' in df.columns:
            substance_values = df['substance'].unique()
            for substance in substance_values:
                substance_str = str(substance)
                assert substance_str == substance_str.strip(), f"Substance '{substance}' should not have trailing whitespace"

    def test_race_ethnicity_column_has_no_trailing_whitespace(self):
        """Test that race/ethnicity column values are trimmed (regression test for race/ethnicity filter bug)."""
        df = discharges_su_dashboard.df_raw
        
        if 'race_ethnicity' in df.columns:
            race_ethnicity_values = df['race_ethnicity'].unique()
            for race_ethnicity in race_ethnicity_values:
                race_ethnicity_str = str(race_ethnicity)
                assert race_ethnicity_str == race_ethnicity_str.strip(), f"Race/Ethnicity '{race_ethnicity}' should not have trailing whitespace"

    def test_hawaii_residency_column_has_no_trailing_whitespace(self):
        """Test that Hawaii residency column values are trimmed (regression test for Hawaii residency filter bug)."""
        df = discharges_su_dashboard.df_raw
        
        if 'hawaii_residency' in df.columns:
            hawaii_residency_values = df['hawaii_residency'].unique()
            for residency in hawaii_residency_values:
                residency_str = str(residency)
                assert residency_str == residency_str.strip(), f"Hawaii Residency '{residency}' should not have trailing whitespace"



@pytest.mark.integration
class TestDischargesSUFiltering:
    """Test filter functionality with real data."""
    
    def test_filter_by_substance_alcohol(self):
        """Test filtering by Alcohol substance with real data."""
        result = discharges_su_dashboard.update_dashboard(
            substance=['Alcohol'],
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
        result = discharges_su_dashboard.update_dashboard(
            substance=None,
            county=['Honolulu'],
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        kpi, bar_fig, substance_line, county_line, age_line, sex_stacked, table_year, table_county, table_age, table_sex, table_race, table_residency = result
        # Bar chart should have data
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        # County table should show 7,001 for county Honolulu
        assert table_county is not None, "County table should not be None"
        table_county_str = str(table_county)
        assert '7,001' in table_county_str or '7001' in table_county_str, f"County table should contain 7,001, got: {table_county_str}"
        assert 'Honolulu' in table_county_str, f"County table should contain Honolulu, got: {table_county_str}"
    
    def test_filter_by_year_2024(self):
        """Test filtering by year 2024 with real data."""
        result = discharges_su_dashboard.update_dashboard(
            substance=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        kpi, bar_fig, substance_line, county_line, age_line, sex_stacked, *tables = result
        print(f"kpi: {kpi}")
        print(f"bar_fig: {bar_fig}")
        print(f"substance_line: {substance_line}")
        print(f"county_line: {county_line}")
        print(f"age_line: {age_line}")
        print(f"sex_stacked: {sex_stacked}")
        #assert false, "failure"

        # Line charts should only show 2024 data
        if len(substance_line.data) > 0:
            for trace in substance_line.data:
                if len(trace.x) > 0:
                    assert all(x == 2024 for x in trace.x), f"All years should be 2024, got {trace.x}"

    def test_filter_by_city_honolulu(self):
        """Test filtering by Honolulu city with real data."""
        result = discharges_su_dashboard.update_dashboard(
            substance=None,
            county=None,
            city=['Honolulu'],
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        kpi, bar_fig, substance_line, county_line, age_line, sex_stacked, table_year, table_county, table_age, table_sex, table_race, table_residency = result
        # Bar chart should have data
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        # KPI card should show 4,875 
        assert '4,875' in kpi or '4875' in kpi, f"KPI should contain '4,875', got: {kpi}"
        # County table should show 4,875 for city Honolulu
        assert table_county is not None, "County table should not be None"
        table_county_str = str(table_county)
        assert '4,875' in table_county_str or '4875' in table_county_str, f"County table should contain 4,875, got: {table_county_str}"
        assert 'Honolulu' in table_county_str, f"County table should contain Honolulu, got: {table_county_str}"

    def test_filter_by_age_group_18_44(self):
        """Test filtering by age group 18-44 with real data."""
        result = discharges_su_dashboard.update_dashboard(
            substance=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=['18-44'],
            sex=None,
            race_ethnicity=None
        )
        kpi, bar_fig, substance_line, county_line, age_line, sex_stacked, table_year, table_county, table_age, table_sex, table_race, table_residency = result
        # Bar chart should have data
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        # KPI card should show 5,097 
        assert '5,097' in kpi or '5097' in kpi, f"KPI should contain '5,097', got: {kpi}"
        # Age table should show 5,097 for age group 18-44
        assert table_age is not None, "Age table should not be None"
        table_age_str = str(table_age)
        assert '5,097' in table_age_str or '5097' in table_age_str, f"Age table should contain 5,097, got: {table_age_str}"
        assert '18-44' in table_age_str, f"Age table should contain 18-44, got: {table_age_str}"

    def test_filter_by_sex_male(self):
        """Test filtering by sex Male with real data."""
        result = discharges_su_dashboard.update_dashboard(
            substance=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=['Male'],
            race_ethnicity=None
        )
        kpi, bar_fig, substance_line, county_line, age_line, sex_stacked, table_year, table_county, table_age, table_sex, table_race, table_residency = result
        # Bar chart should have data
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        # KPI card should show 7,057 
        assert '7,057' in kpi or '7057' in kpi, f"KPI should contain '7,057', got: {kpi}"
        # Sex table should show 7,057 for Male
        assert table_sex is not None, "Sex table should not be None"
        table_sex_str = str(table_sex)
        assert '7,057' in table_sex_str or '7057' in table_sex_str, f"Sex table should contain 7,057, got: {table_sex_str}"
        assert 'Male' in table_sex_str, f"Sex table should contain Male, got: {table_sex_str}"

    def test_filter_by_race_ethnicity_white(self):
        """Test filtering by race/ethnicity White/Caucasian with real data."""
        result = discharges_su_dashboard.update_dashboard(
            substance=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=['White/Caucasian']
        )
        kpi, bar_fig, substance_line, county_line, age_line, sex_stacked, table_year, table_county, table_age, table_sex, table_race, table_residency = result
        # Bar chart should have data
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        # KPI card should show 5,289 
        assert '5,289' in kpi or '5289' in kpi, f"KPI should contain '5,289', got: {kpi}"
        # Race/Ethnicity table should show 5,289 for White/Caucasian
        assert table_race is not None, "Race/Ethnicity table should not be None"
        table_race_str = str(table_race)
        assert '5,289' in table_race_str or '5289' in table_race_str, f"Race/Ethnicity table should contain 5,289, got: {table_race_str}"
        assert 'White/Caucasian' in table_race_str, f"Race/Ethnicity table should contain White/Caucasian, got: {table_race_str}"

    def test_filter_by_hawaii_residency_resident(self):
        """Test filtering by Hawaii residency with real data."""
        result = discharges_su_dashboard.update_dashboard(
            substance=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=['Resident'],
            age=None,
            sex=None,
            race_ethnicity=None
        )
        kpi, bar_fig, substance_line, county_line, age_line, sex_stacked, table_year, table_county, table_age, table_sex, table_race, table_residency = result
        # Bar chart should have data
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        # KPI card should show 9,854 
        assert '9,854' in kpi or '9854' in kpi, f"KPI should contain '9,854', got: {kpi}"
        # Residency table should show 9,854 for Resident
        assert table_residency is not None, "Residency table should not be None"
        table_residency_str = str(table_residency)
        assert '9,854' in table_residency_str or '9854' in table_residency_str, f"Residency table should contain 9,854, got: {table_residency_str}"
        assert 'Resident' in table_residency_str, f"Residency table should contain Resident, got: {table_residency_str}"


@pytest.mark.regression
class TestDischargesSURegressionScenarios:
    """Regression tests for known scenarios using real data."""
    
    def test_specific_scenario_alcohol_2024_honolulu_18_44_male_1473_discharges(self):
        """
        REGRESSION TEST: Specific test case with REAL DATA.
        
        When filtering for:
        - Substance Type: Alcohol
        - Calendar Year: 2024
        - County: Honolulu
        - Age Group: 18-44
        - Sex at Birth: Male
        
        Expected results (verified from real data):
        - All visuals should show 1,473 discharges
        - This verifies:
          * Query is working correctly
          * Visuals load as expected
          * Filters work correctly
          * All aggregations are consistent
        """
        # Apply the specific filters to real data
        result = discharges_su_dashboard.update_dashboard(
            substance=['Alcohol'],
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
         substance_line_fig, 
         county_line_fig, 
         age_line_fig, 
         sex_stacked_fig,
         table_year,
         table_county,
         table_age,
         table_sex,
         table_race,
         table_residency) = result
        
        # TEST 1: KPI card should show 1,473
        assert '1,473' in kpi_text or '1473' in kpi_text, f"KPI should contain '1,473', got: {kpi_text}"
        
        # TEST 2: Bar chart (Discharges by Substance) should show 1,473 for Alcohol
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        
        bar_data = bar_fig.data[0]
        # Since we filtered for Alcohol only, should have one bar
        assert len(bar_data.y) == 1, f"Should have 1 substance bar (Alcohol), got {len(bar_data.y)}"
        assert bar_data.x[0] == 1473, f"Bar chart should show 1473 discharges, got {bar_data.x[0]}"
        
        # TEST 3: Substance line chart should show 1,473 for 2024
        assert substance_line_fig is not None, "Substance line chart should not be None"
        assert len(substance_line_fig.data) > 0, "Substance line chart should have data"
        
        # Should have one trace for Alcohol
        alcohol_trace = substance_line_fig.data[0]
        assert len(alcohol_trace.x) == 1, f"Should have 1 point (2024), got {len(alcohol_trace.x)}"
        assert alcohol_trace.x[0] == 2024, f"Year should be 2024, got {alcohol_trace.x[0]}"
        assert alcohol_trace.y[0] == 1473, f"Substance line should show 1473, got {alcohol_trace.y[0]}"
        
        # TEST 4: County line chart should show 1,473 for Honolulu in 2024
        assert county_line_fig is not None, "County line chart should not be None"
        assert len(county_line_fig.data) > 0, "County line chart should have data"
        
        # Should have one trace for Honolulu
        honolulu_trace = county_line_fig.data[0]
        assert len(honolulu_trace.x) == 1, f"Should have 1 point (2024), got {len(honolulu_trace.x)}"
        assert honolulu_trace.x[0] == 2024, f"Year should be 2024, got {honolulu_trace.x[0]}"
        assert honolulu_trace.y[0] == 1473, f"County line should show 1473, got {honolulu_trace.y[0]}"
        
        # TEST 5: Age line chart should show 1,473 for 18-44 in 2024
        assert age_line_fig is not None, "Age line chart should not be None"
        assert len(age_line_fig.data) > 0, "Age line chart should have data"
        
        # Should have one trace for 18-44
        age_trace = age_line_fig.data[0]
        assert len(age_trace.x) == 1, f"Should have 1 point (2024), got {len(age_trace.x)}"
        assert age_trace.x[0] == 2024, f"Year should be 2024, got {age_trace.x[0]}"
        assert age_trace.y[0] == 1473, f"Age line should show 1473, got {age_trace.y[0]}"
        
        # TEST 6: Sex stacked bar chart should show 1,473 for Male in 2024
        assert sex_stacked_fig is not None, "Sex stacked bar should not be None"
        assert len(sex_stacked_fig.data) > 0, "Sex stacked bar should have data"
        
        # Should have one trace for Male
        male_trace = sex_stacked_fig.data[0]
        assert len(male_trace.x) == 1, f"Should have 1 bar (2024), got {len(male_trace.x)}"
        assert male_trace.x[0] == 2024, f"Year should be 2024, got {male_trace.x[0]}"
        assert male_trace.y[0] == 1473, f"Sex stacked bar should show 1473, got {male_trace.y[0]}"
        
        # TEST 7: Year table should show 1,473 for 2024
        assert table_year is not None, "Year table should not be None"
        # Convert table to string to search for value
        table_year_str = str(table_year)
        assert '1,473' in table_year_str or '1473' in table_year_str, f"Year table should contain 1,473"
        assert '2024' in table_year_str, "Year table should contain 2024"
        
        # TEST 8: County table should show 1,473 for Honolulu
        assert table_county is not None, "County table should not be None"
        table_county_str = str(table_county)
        assert '1,473' in table_county_str or '1473' in table_county_str, f"County table should contain 1,473"
        assert 'Honolulu' in table_county_str, "County table should contain Honolulu"
        
        # TEST 9: Age table should show 1,473 for 18-44
        assert table_age is not None, "Age table should not be None"
        table_age_str = str(table_age)
        assert '1,473' in table_age_str or '1473' in table_age_str, f"Age table should contain 1,473"
        assert '18-44' in table_age_str, "Age table should contain 18-44"
        
        # TEST 10: Sex table should show 1,473 for Male
        assert table_sex is not None, "Sex table should not be None"
        table_sex_str = str(table_sex)
        assert '1,473' in table_sex_str or '1473' in table_sex_str, f"Sex table should contain 1,473"
        assert 'Male' in table_sex_str, "Sex table should contain Male"
    
    def test_empty_filters_shows_all_data(self):
        """Regression: Empty filters should show all data from real database."""
        result = discharges_su_dashboard.update_dashboard(
            substance=None,
            county=None,
            city=None,
            year=None,
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        
        kpi, bar_fig, substance_line, county_line, age_line, sex_stacked, *tables = result
        
        # Should have data for multiple substances
        assert bar_fig is not None, "Bar chart should not be None"
        assert len(bar_fig.data) > 0, "Bar chart should have data"
        
        bar_data = bar_fig.data[0]
        assert len(bar_data.y) > 1, f"Should show multiple substances, got {len(bar_data.y)}"
    
    def test_multiple_years_selected(self):
        """Regression: Multiple year selection should work with real data."""
        result = discharges_su_dashboard.update_dashboard(
            substance=['Alcohol'],
            county=['Honolulu'],
            city=None,
            year=[2023, 2024],
            hawaii_residency=None,
            age=['18-44'],
            sex=['Male'],
            race_ethnicity=None
        )
        
        kpi, bar_fig, substance_line, county_line, age_line, sex_stacked, *tables = result
        
        # Line charts should show both years
        if len(substance_line.data) > 0:
            alcohol_trace = substance_line.data[0]
            years_shown = set(alcohol_trace.x)
            assert 2023 in years_shown or 2024 in years_shown, "Should show at least one of the selected years"
    
    def test_yearly_sex_stacked_bar_xaxis_single_year_filter(self):
        """
        REGRESSION TEST: Verify x-axis behavior when filtering to single year.
        
        When filtering to a single year (e.g., 2024) and single sex (e.g., Male),
        the "Yearly Discharges by Gender" stacked bar chart should:
        1. Show only the filtered year on the x-axis (not interpolated values)
        2. Have dtick=1 set to force integer-only tick marks
        3. Not show spurious intermediate ticks like "2,2023.6", "2,2023.8", etc.
        
        This prevents Plotly from treating the numeric year axis as continuous
        and auto-generating intermediate tick marks.
        """
        result = discharges_su_dashboard.update_dashboard(
            substance=None,
            county=None,
            city=None,
            year=[2024],  # Single year filter
            hawaii_residency=None,
            age=None,
            sex=['Male'],  # Single sex filter
            race_ethnicity=None
        )
        
        kpi, bar_fig, substance_line, county_line, age_line, sex_stacked, *tables = result
        
        # Verify sex_stacked bar chart exists and has data
        assert sex_stacked is not None, "Sex stacked bar chart should not be None"
        assert len(sex_stacked.data) > 0, "Sex stacked bar chart should have data"
        
        # Verify x-axis data shows only 2024
        male_trace = sex_stacked.data[0]
        assert len(male_trace.x) == 1, f"Should have exactly 1 year point, got {len(male_trace.x)}"
        assert male_trace.x[0] == 2024, f"X-axis should show 2024, got {male_trace.x[0]}"
        
        # Verify x-axis configuration has dtick=1 to force integer ticks
        xaxis_config = sex_stacked.layout.xaxis
        assert hasattr(xaxis_config, 'dtick'), "X-axis should have dtick configured"
        assert xaxis_config.dtick == 1, f"X-axis dtick should be 1 (integer ticks only), got {xaxis_config.dtick}"
        
    def test_yearly_sex_stacked_bar_xaxis_multiple_years(self):
        """
        REGRESSION TEST: Verify x-axis with multiple years displays correctly.
        
        When filtering to multiple years (e.g., 2023, 2024), the chart should:
        1. Display all selected years that have data
        2. Still use dtick=1 for integer-only tick marks
        3. Maintain proper spacing between bars
        """
        result = discharges_su_dashboard.update_dashboard(
            substance=None,
            county=None,
            city=None,
            year=[2023, 2024],  # Multiple years
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        
        kpi, bar_fig, substance_line, county_line, age_line, sex_stacked, *tables = result
        
        # Verify sex_stacked bar chart exists and has data
        assert sex_stacked is not None, "Sex stacked bar chart should not be None"
        assert len(sex_stacked.data) > 0, "Sex stacked bar chart should have data"
        
        # Collect all years across all traces (Male, Female, etc.)
        all_years = set()
        for trace in sex_stacked.data:
            if hasattr(trace, 'x') and len(trace.x) > 0:
                all_years.update(trace.x)
        
        # Should have both years (or at least one if data doesn't exist for one year)
        assert len(all_years) > 0, "Should have at least one year displayed"
        assert all(year in [2023, 2024] for year in all_years), f"All years should be from selected [2023, 2024], got {all_years}"
        
        # Verify x-axis configuration still has dtick=1
        xaxis_config = sex_stacked.layout.xaxis
        assert hasattr(xaxis_config, 'dtick'), "X-axis should have dtick configured"
        assert xaxis_config.dtick == 1, f"X-axis dtick should be 1 (integer ticks only), got {xaxis_config.dtick}"


@pytest.mark.integration
class TestDischargesSUCharts:
    """Test chart generation and data validation with real data."""
    
    def test_bar_chart_structure(self):
        """Test that bar chart has correct structure with real data."""
        result = discharges_su_dashboard.update_dashboard(
            substance=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        
        kpi, bar_fig, *rest = result
        
        # Should be a bar chart
        assert isinstance(bar_fig, go.Figure), "Should be a Plotly Figure"
        assert len(bar_fig.data) > 0, "Should have at least one trace"
        assert bar_fig.data[0].type == 'bar', "Should be a bar chart"
        
        # Bar chart should be horizontal (orientation='h')
        assert bar_fig.data[0].orientation == 'h', "Bar chart should be horizontal"
    
    def test_line_chart_structure(self):
        """Test that line charts have correct structure with real data."""
        result = discharges_su_dashboard.update_dashboard(
            substance=['Alcohol'],
            county=None,
            city=None,
            year=None,
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        
        kpi, bar_fig, substance_line, county_line, age_line, sex_stacked, *tables = result
        
        # Substance line should be a line chart
        assert isinstance(substance_line, go.Figure), "Should be a Plotly Figure"
        if len(substance_line.data) > 0:
            for trace in substance_line.data:
                assert trace.type == 'scatter', "Should be scatter type"
    
    def test_stacked_bar_structure(self):
        """Test that stacked bar chart has correct structure with real data."""
        result = discharges_su_dashboard.update_dashboard(
            substance=['Alcohol'],
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        
        kpi, bar_fig, substance_line, county_line, age_line, sex_stacked, *tables = result
        
        # Should be a stacked bar chart
        assert isinstance(sex_stacked, go.Figure), "Should be a Plotly Figure"
        assert len(sex_stacked.data) > 0, "Should have at least one trace"


class TestDischargesSUTables:
    """Test table generation with real data."""
    
    def test_tables_are_not_none(self):
        """Test that all tables are generated."""
        result = discharges_su_dashboard.update_dashboard(
            substance=['Alcohol'],
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        
        (kpi, bar_fig, substance_line, county_line, age_line, sex_stacked,
         table_year, table_county, table_age, table_sex, table_race, table_residency) = result
        
        assert table_year is not None, "Year table should not be None"
        assert table_county is not None, "County table should not be None"
        assert table_age is not None, "Age table should not be None"
        assert table_sex is not None, "Sex table should not be None"
        assert table_race is not None, "Race table should not be None"
        assert table_residency is not None, "Residency table should not be None"


class TestDischargesSUResetFilters:
    """Test filter reset functionality."""
    
    def test_reset_filters_callback_exists(self):
        """Test that reset filters callback is defined."""
        assert hasattr(discharges_su_dashboard, 'reset_discharges_filters'), "Should have reset_discharges_filters function"
        assert callable(discharges_su_dashboard.reset_discharges_filters), "reset_discharges_filters should be callable"
    
    def test_reset_filters_returns_none_values(self):
        """Test that reset filters returns None for all filter values."""
        result = discharges_su_dashboard.reset_discharges_filters(1)
        
        # Should return 8 None values (one for each filter)
        assert len(result) == 8, f"Should return 8 values, got {len(result)}"
        assert all(v is None for v in result), "All filter values should be None after reset"


@pytest.mark.integration
class TestDischargesSUDataConsistency:
    """Test data consistency across different visuals."""
    
    def test_kpi_matches_filtered_data_count(self):
        """Test that KPI value matches the actual filtered data count."""
        # Get raw data and apply same filters
        df = discharges_su_dashboard.df_raw.copy()
        
        # Apply filters manually
        df_filtered = df[
            (df['substance'] == 'Alcohol') &
            (df['county'] == 'Honolulu') &
            (df['year'] == 2024) &
            (df['age_group'] == '18-44') &
            (df['sex'] == 'Male')
        ]
        
        expected_count = df_filtered['record_id'].nunique()
        
        # Now call the dashboard callback
        result = discharges_su_dashboard.update_dashboard(
            substance=['Alcohol'],
            county=['Honolulu'],
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=['18-44'],
            sex=['Male'],
            race_ethnicity=None
        )
        
        kpi_text = result[0]
        
        # Extract number from KPI text
        import re
        numbers = re.findall(r'[\d,]+', kpi_text)
        if numbers:
            kpi_value = int(numbers[0].replace(',', ''))
            assert kpi_value == expected_count, f"KPI should show {expected_count}, got {kpi_value}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
