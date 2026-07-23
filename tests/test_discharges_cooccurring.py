"""
Tests for discharges_cooccurring_dashboard.py and /discharges-cooccurring-su and /discharges-cooccurring-mh page.

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
import discharges_cooccurring_dashboard
from tests.test_utils import assert_returned_tables_sort_order


class TestPageStructure:
    """Test basic page structure and initialization."""
    
    def test_discharges_cooccurring_pages_registered(self):
        """Test that discharges-cooccurring-su and discharges-cooccurring-mg pages are registered."""
        from dash import page_registry
        import multi_dashboard  # Ensures pages are registered
        
        paths = [page['path'] for page in page_registry.values()]
        assert '/discharges-cooccurring-su' in paths, "discharges-cooccurring-su page should be registered"
        assert '/discharges-cooccurring-mh' in paths, "discharges-cooccurring-mh page should be registered"
    
    def test_discharges_cooccurring_pages_have_layouts(self):
        """Test that discharges-cooccurring-su(mh) page has a layout."""
        from pages import discharges_cooccurring_su
        from pages import discharges_cooccurring_mh
 
        assert hasattr(discharges_cooccurring_su, 'layout'), "Page should have layout attribute"
        assert discharges_cooccurring_su.layout is not None, "Layout should not be None"
        assert hasattr(discharges_cooccurring_mh, 'layout'), "Page should have layout attribute"
        assert discharges_cooccurring_mh.layout is not None, "Layout should not be None"
    
    def test_discharges_cooccurring_dashboard_imports_correctly(self):
        """Test that discharges_cooccurring_dashboard module can be imported."""
        assert hasattr(discharges_cooccurring_dashboard, 'layout'), "Module should have layout"
        assert hasattr(discharges_cooccurring_dashboard, 'update_dashboard'), "Module should have update_dashboard callback"

    def test_callback_returns_tables_in_canonical_order(self):
        """Verify the update_dashboard callback returns tables sorted by dashboard_utils."""
        assert_returned_tables_sort_order(discharges_cooccurring_dashboard)

class TestDataLoading:
    """Test data loading and initialization with real data."""
    
    def test_load_discharge_dataframe_from_db(self):
        """Test that data loading function works correctly with real data."""
        df = discharges_cooccurring_dashboard.df_raw
        
        assert not df.empty, "Real data should not be empty"
        assert 'diagnosis' in df.columns, "Should have diagnosis column"
        assert 'diagnosis_type' in df.columns, "Should have diagnosis_type column"
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
        df = discharges_cooccurring_dashboard.df_raw
        
        assert pd.api.types.is_numeric_dtype(df['year']), "Year column should be numeric"
    
    def test_county_column_has_no_trailing_whitespace(self):
        """Test that county column values are trimmed (regression test for county filter bug)."""
        df = discharges_cooccurring_dashboard.df_raw
        if 'county' in df.columns:
            county_values = df['county'].unique()
            for county in county_values:
                county_str = str(county)
                assert county_str == county_str.strip(), f"County '{county}' should not have trailing whitespace"

    def test_city_column_has_no_trailing_whitespace(self):
        """Test that city column values are trimmed (regression test for city filter bug)."""
        df = discharges_cooccurring_dashboard.df_raw
        
        if 'city' in df.columns:
            city_values = df['city'].unique()
            for city in city_values:
                city_str = str(city)
                assert city_str == city_str.strip(), f"City '{city}' should not have trailing whitespace"

    def test_age_column_has_no_trailing_whitespace(self):
        """Test that age column values are trimmed (regression test for age filter bug)."""
        df = discharges_cooccurring_dashboard.df_raw
        
        if 'age_group' in df.columns:
            age_values = df['age_group'].unique()
            for age in age_values:
                age_str = str(age)
                assert age_str == age_str.strip(), f"Age '{age}' should not have trailing whitespace"

    def test_sex_column_has_no_trailing_whitespace(self):
        """Test that sex column values are trimmed (regression test for sex filter bug)."""
        df = discharges_cooccurring_dashboard.df_raw
        
        if 'sex' in df.columns:
            sex_values = df['sex'].unique()
            for sex in sex_values:
                sex_str = str(sex)
                assert sex_str == sex_str.strip(), f"Sex '{sex}' should not have trailing whitespace"

    def test_substance_column_has_no_trailing_whitespace(self):
        """Test that substance column values are trimmed (regression test for substance filter bug)."""
        df = discharges_cooccurring_dashboard.df_raw
        
        if 'substance' in df.columns:
            substance_values = df['substance'].unique()
            for substance in substance_values:
                substance_str = str(substance)
                assert substance_str == substance_str.strip(), f"Substance '{substance}' should not have trailing whitespace"

    def test_race_ethnicity_column_has_no_trailing_whitespace(self):
        """Test that race/ethnicity column values are trimmed (regression test for race/ethnicity filter bug)."""
        df = discharges_cooccurring_dashboard.df_raw
        
        if 'race_ethnicity' in df.columns:
            race_ethnicity_values = df['race_ethnicity'].unique()
            for race_ethnicity in race_ethnicity_values:
                race_ethnicity_str = str(race_ethnicity)
                assert race_ethnicity_str == race_ethnicity_str.strip(), f"Race/Ethnicity '{race_ethnicity}' should not have trailing whitespace"

    def test_hawaii_residency_column_has_no_trailing_whitespace(self):
        """Test that Hawaii residency column values are trimmed (regression test for Hawaii residency filter bug)."""
        df = discharges_cooccurring_dashboard.df_raw
        
        if 'hawaii_residency' in df.columns:
            hawaii_residency_values = df['hawaii_residency'].unique()
            for residency in hawaii_residency_values:
                residency_str = str(residency)
                assert residency_str == residency_str.strip(), f"Hawaii Residency '{residency}' should not have trailing whitespace"



@pytest.mark.integration
class TestFiltering:
    """Test filter functionality with real data."""
    
    def test_filter_by_year_2024(self):
        """Test filtering by year 2024 with real data."""
        result = discharges_cooccurring_dashboard.update_dashboard(
            su=None,
            mh=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        kpi, sub_bar, mh_bar, sub_line, mh_line, table_year, table_county, table_age, table_sex, table_race, table_hawaii = result
        # Line charts should only show 2024 data
        if len(sub_line.data) > 0:
            for trace in sub_line.data:
                if len(trace.x) > 0:
                    assert all(x == 2024 for x in trace.x), f"All years should be 2024, got {trace.x}"
        # KPI card should show 1,960 
        assert '1,960' in kpi or '1,960' in kpi, f"KPI should contain '1,960', got: {kpi}"

    def test_filter_by_substance_alcohol(self):
        """Test filtering by Alcohol substance with real data."""
        result = discharges_cooccurring_dashboard.update_dashboard(
            su=['Alcohol'],
            mh=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        
        # Result should be a tuple with 11 elements
        assert len(result) == 11, f"Should return 11 elements, got {len(result)}"
        
        # KPI should show some value
        kpi = result[0]
        assert kpi is not None, "KPI should not be None"
        assert any(c.isdigit() for c in str(kpi)), "KPI should show numeric value"
        # KPI card should show 834 
        assert '834' in kpi or '834' in kpi, f"KPI should contain '834', got: {kpi}"

    def test_filter_by_county_honolulu(self):
        """Test filtering by Honolulu county with real data."""
        result = discharges_cooccurring_dashboard.update_dashboard(
            su=None,
            mh=None,
            county=['Honolulu'],
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        print(result)
        kpi, sub_bar, mh_bar, sub_line, mh_line, table_year, table_county, table_age, table_sex, table_race, table_hawaii = result
        print(f"kpi: {kpi}")
        print(f"sub_bar: {sub_bar}")
        print(f"mh_bar: {mh_bar}")
        print(f"sub_line: {sub_line}")
        print(f"table_county: {table_county}")
        print(f"table_age: {table_age}")
        print(f"table_sex: {table_sex}")

        # Bar chart should have data
        assert sub_bar is not None, "Bar chart should not be None"
        assert len(sub_bar.data) > 0, "Bar chart should have data"
        assert mh_bar is not None, "Bar chart should not be None"
        assert len(mh_bar.data) > 0, "Bar chart should have data"
        # County table should show 1,346 for county Honolulu
        assert table_county is not None, "County table should not be None"
        table_county_str = str(table_county)
        assert '1,346' in table_county_str or '1,346' in table_county_str, f"County table should contain 1,346, got: {table_county_str}"
        assert 'Honolulu' in table_county_str, f"County table should contain Honolulu, got: {table_county_str}"
    

    def test_filter_by_city_honolulu(self):
        """Test filtering by Honolulu city with real data."""
        result = discharges_cooccurring_dashboard.update_dashboard(
            su=None,
            mh=None,
            county=None,
            city=['Honolulu'],
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        kpi, sub_bar, mh_bar, sub_line, mh_line, table_year, table_county, table_age, table_sex, table_race, table_hawaii = result
        # Bar chart should have data
        assert sub_bar is not None, "Bar chart should not be None"
        assert len(sub_bar.data) > 0, "Bar chart should have data"
        assert mh_bar is not None, "Bar chart should not be None"
        assert len(mh_bar.data) > 0, "Bar chart should have data"
        # KPI card should show 1,045 
        assert '1,045' in kpi or '1,045' in kpi, f"KPI should contain '1,045', got: {kpi}"
        # County table should show 1,045 for city Honolulu
        assert table_county is not None, "County table should not be None"
        table_county_str = str(table_county)
        print(f"table_county_str: {table_county_str}")
        assert '1,045' in table_county_str or '1,045' in table_county_str, f"County table should contain 1,045, got: {table_county_str}"
        assert 'Statewide' in table_county_str, f"County table should contain Statewide, got: {table_county_str}"

    def test_filter_by_age_group_18_44(self):
        """Test filtering by age group 18-44 with real data."""
        result = discharges_cooccurring_dashboard.update_dashboard(
            su=None,
            mh=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=['18-44'],
            sex=None,
            race_ethnicity=None
        )
        kpi, sub_bar, mh_bar, sub_line, mh_line, table_year, table_county, table_age, table_sex, table_race, table_hawaii = result
        # Bar chart should have data
        assert sub_bar is not None, "Bar chart should not be None"
        assert len(sub_bar.data) > 0, "Bar chart should have data"
        assert mh_bar is not None, "Bar chart should not be None"
        assert len(mh_bar.data) > 0, "Bar chart should have data"
        # KPI card should show 1,180
        assert '1,180' in kpi or '1,180' in kpi, f"KPI should contain '1,180', got: {kpi}"
        # Age table should show 1,180 for age group 18-44
        assert table_age is not None, "Age table should not be None"
        table_age_str = str(table_age)
        print(f"table_age_str: {table_age_str}")
        assert '1,180' in table_age_str or '1,180' in table_age_str, f"Age table should contain 1,180, got: {table_age_str}"
        assert '18-44' in table_age_str, f"Age table should contain 18-44, got: {table_age_str}"

    def test_filter_by_sex_male(self):
        """Test filtering by sex Male with real data."""
        result = discharges_cooccurring_dashboard.update_dashboard(
            su=None,
            mh=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=['Male'],
            race_ethnicity=None
        )
        kpi, sub_bar, mh_bar, sub_line, mh_line, table_year, table_county, table_age, table_sex, table_race, table_hawaii = result
        # Bar chart should have data
        assert sub_bar is not None, "Bar chart should not be None"
        assert len(sub_bar.data) > 0, "Bar chart should have data"
        assert mh_bar is not None, "Bar chart should not be None"
        assert len(mh_bar.data) > 0, "Bar chart should have data"
        # KPI card should show 1,168 
        assert '1,168' in kpi or '1,168' in kpi, f"KPI should contain '1,168', got: {kpi}"
        # Sex table should show 1,168 for Male
        assert table_sex is not None, "Sex table should not be None"
        table_sex_str = str(table_sex)
        print(f"table_sex_str: {table_sex_str}")
        assert '1,168' in table_sex_str or '1,168' in table_sex_str, f"Sex table should contain 1,168, got: {table_sex_str}"
        assert 'Male' in table_sex_str, f"Sex table should contain Male, got: {table_sex_str}"

    def test_filter_by_race_ethnicity_white(self):
        """Test filtering by race/ethnicity White/Caucasian with real data."""
        result = discharges_cooccurring_dashboard.update_dashboard(
            su=None,
            mh=None,            
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=['White/Caucasian']
        )
        kpi, sub_bar, mh_bar, sub_line, mh_line, table_year, table_county, table_age, table_sex, table_race, table_hawaii = result
        # Bar chart should have data
        assert sub_bar is not None, "Bar chart should not be None"
        assert len(sub_bar.data) > 0, "Bar chart should have data"
        assert mh_bar is not None, "Bar chart should not be None"
        assert len(mh_bar.data) > 0, "Bar chart should have data"
        # KPI card should show 916 
        assert '916' in kpi or '916' in kpi, f"KPI should contain '916', got: {kpi}"
        # # Race/Ethnicity table should show 916 for White/Caucasian
        assert table_race is not None, "Race/Ethnicity table should not be None"
        table_race_str = str(table_race)
        assert '916' in table_race_str or '916' in table_race_str, f"Race/Ethnicity table should contain 916, got: {table_race_str}"
        assert 'White/Caucasian' in table_race_str, f"Race/Ethnicity table should contain White/Caucasian, got: {table_race_str}"

    def test_filter_by_hawaii_residency_resident(self):
        """Test filtering by Hawaii residency with real data."""
        result = discharges_cooccurring_dashboard.update_dashboard(
            su=None,
            mh=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=['Resident'],
            age=None,
            sex=None,
            race_ethnicity=None
        )
        kpi, sub_bar, mh_bar, sub_line, mh_line, table_year, table_county, table_age, table_sex, table_race, table_hawaii = result
        # Bar chart should have data
        assert sub_bar is not None, "Bar chart should not be None"
        assert len(sub_bar.data) > 0, "Bar chart should have data"
        assert mh_bar is not None, "Bar chart should not be None"
        assert len(mh_bar.data) > 0, "Bar chart should have data"
        # KPI card should show 1,840 
        assert '1,840' in kpi or '1,840' in kpi, f"KPI should contain '1,840', got: {kpi}"
        # # Residency table should show 1,840 for Resident
        # assert table_residency is not None, "Residency table should not be None"
        # table_residency_str = str(table_residency)
        # assert '1,840' in table_residency_str or '1,840' in table_residency_str, f"Residency table should contain 1,840, got: {table_residency_str}"
        # assert 'Resident' in table_residency_str, f"Residency table should contain Resident, got: {table_residency_str}"


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
        - All visuals should show 169 discharges
        - This verifies:
          * Query is working correctly
          * Visuals load as expected
          * Filters work correctly
          * All aggregations are consistent
        """
        # Apply the specific filters to real data
        result = discharges_cooccurring_dashboard.update_dashboard(
            su=['Alcohol'],
            mh=None,
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
         sub_bar_fig, 
         mh_bar_fig, 
         sub_line_fig, 
         mh_line_fig,
         table_year,
         table_county,
         table_age,
         table_sex,
         table_race,
         table_residency) = result
        
        # TEST 1: KPI card should show 169
        assert '169' in kpi_text or '169' in kpi_text, f"KPI should contain '169', got: {kpi_text}"
        
        # TEST 2: Bar chart (Discharges by Substance) should show 169 for Alcohol
        assert sub_bar_fig is not None, "Bar chart should not be None"
        assert len(sub_bar_fig.data) > 0, "Bar chart should have data"
        
        bar_data = sub_bar_fig.data[0]
        assert len(bar_data.y) == 8, f"Should have 8 bars, got {len(bar_data.y)}"
        alcohol_index = 7
        assert bar_data.x[alcohol_index] == 169, f"Bar chart should show 169 discharges, got {bar_data.x[alcohol_index]}"
        assert bar_data.y[alcohol_index] == 'Alcohol', f"Bar chart should show Alcohol discharges, got {bar_data.y[alcohol_index]}"

        # TEST 3: Substance line chart should show 169 for 2024
        assert sub_line_fig is not None, "Substance line chart should not be None"
        assert len(sub_line_fig.data) == 8, f"Substance line chart should have 8 points (2024), got {len(sub_line_fig.data)}"
        
        # TEST 4: Should have one trace for Alcohol
        alcohol_trace = sub_line_fig.data[0]
        assert len(alcohol_trace.x) == 1, f"Should have 1 points (2024), got {len(alcohol_trace.x)}"
        assert alcohol_trace.x[0] == 2024, f"Year should be 2024, got {alcohol_trace.x[0]}"
        assert alcohol_trace.y[0] == 169, f"Substance line should show 169, got {alcohol_trace.y[0]}"
        
        # TEST 5: Year table should show 169 for 2024
        assert table_year is not None, "Year table should not be None"
        # Convert table to string to search for value
        table_year_str = str(table_year)
        assert '169' in table_year_str, f"Year table should contain 169"
        assert '2024' in table_year_str, "Year table should contain 2024"
        
        # TEST 6: County table should show 169 for Honolulu
        assert table_county is not None, "County table should not be None"
        table_county_str = str(table_county)
        assert '169' in table_county_str, f"County table should contain 169"
        assert 'Honolulu' in table_county_str, "County table should contain Honolulu"
        
        # TEST 7: Age table should show 169 for 18-44
        assert table_age is not None, "Age table should not be None"
        table_age_str = str(table_age)
        assert '169' in table_age_str, f"Age table should contain 169"
        assert '18-44' in table_age_str, "Age table should contain 18-44"
        
        # TEST 8: Sex table should show 169 for Male
        assert table_sex is not None, "Sex table should not be None"
        table_sex_str = str(table_sex)
        assert '169' in table_sex_str, f"Sex table should contain 169"
        assert 'Male' in table_sex_str, "Sex table should contain Male"
    
    def test_empty_filters_shows_all_data(self):
        """Regression: Empty filters should show all data from real database."""
        result = discharges_cooccurring_dashboard.update_dashboard(
            su=None,
            mh=None,
            county=None,
            city=None,
            year=None,
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        
        kpi, sub_bar, mh_bar, sub_line, mh_line, table_year, table_county, table_age, table_sex, table_race, table_hawaii = result
        
        # Should have data for multiple substances
        assert sub_bar is not None, "Bar chart should not be None"
        assert len(sub_bar.data) > 0, "Bar chart should have data"
        
        bar_data = sub_bar.data[0]
        assert len(bar_data.y) > 1, f"Should show multiple substances, got {len(bar_data.y)}"
    
    def test_multiple_years_selected(self):
        """Regression: Multiple year selection should work with real data."""
        result = discharges_cooccurring_dashboard.update_dashboard(
            su=['Alcohol'],
            mh=None,
            county=['Honolulu'],
            city=None,
            year=[2023, 2024],
            hawaii_residency=None,
            age=['18-44'],
            sex=['Male'],
            race_ethnicity=None
        )
        
        kpi, sub_bar, mh_bar, sub_line, mh_line, table_year, table_county, table_age, table_sex, table_race, table_hawaii = result
        
        # Line charts should show both years
        if len(sub_line.data) > 0:
            alcohol_trace = sub_line.data[0]
            years_shown = set(alcohol_trace.x)
            assert 2023 in years_shown and 2024 in years_shown, "Should show both of the selected years"

@pytest.mark.integration
class TestDischargesSUCharts:
    """Test chart generation and data validation with real data."""
    
    def test_bar_chart_structure(self):
        """Test that bar chart has correct structure with real data."""
        result = discharges_cooccurring_dashboard.update_dashboard(
            su=None,
            mh=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        
        kpi, sub_bar, mh_bar, sub_line, mh_line, table_year, table_county, table_age, table_sex, table_race, table_hawaii = result
        
        # Should be a bar chart
        assert isinstance(sub_bar, go.Figure), "Should be a Plotly Figure"
        assert len(sub_bar.data) > 0, "Should have at least one trace"
        assert sub_bar.data[0].type == 'bar', "Should be a bar chart"
        
        # Bar chart should be horizontal (orientation='h')
        assert sub_bar.data[0].orientation == 'h', "Bar chart should be horizontal"
    
    def test_line_chart_structure(self):
        """Test that line charts have correct structure with real data."""
        result = discharges_cooccurring_dashboard.update_dashboard(
            su=['Alcohol'],
            mh=None,
            county=None,
            city=None,
            year=None,
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        
        kpi, sub_bar, mh_bar, sub_line, mh_line, table_year, table_county, table_age, table_sex, table_race, table_hawaii = result
        
        # Substance line should be a line chart
        assert isinstance(sub_line, go.Figure), "Should be a Plotly Figure"
        if len(sub_line.data) > 0:
            for trace in sub_line.data:
                assert trace.type == 'scatter', "Should be scatter type"
    
    # def test_stacked_bar_structure(self):
    #     """Test that stacked bar chart has correct structure with real data."""
    #     result = discharges_cooccurring_dashboard.update_dashboard(
    #         su=['Alcohol'],
    #         mh=None,
    #         county=None,
    #         city=None,
    #         year=[2024],
    #         hawaii_residency=None,
    #         age=None,
    #         sex=None,
    #         race_ethnicity=None
    #     )
        
    #     kpi, sub_bar, mh_bar, sub_line, mh_line, table_year, table_county, table_age, table_sex, table_race, table_hawaii = result
        
    #     # Should be a stacked bar chart
    #     assert isinstance(table_sex, go.Figure), "Should be a Plotly Figure"
    #     assert len(table_sex.data) > 0, "Should have at least one trace"


class TestDischargesSUTables:
    """Test table generation with real data."""
    
    def test_tables_are_not_none(self):
        """Test that all tables are generated."""
        result = discharges_cooccurring_dashboard.update_dashboard(
            su=['Alcohol'],
            mh=None,
            county=None,
            city=None,
            year=[2024],
            hawaii_residency=None,
            age=None,
            sex=None,
            race_ethnicity=None
        )
        
        kpi, sub_bar, mh_bar, sub_line, mh_line, table_year, table_county, table_age, table_sex, table_race, table_hawaii = result
        
        assert table_county is not None, "County table should not be None"
        assert table_age is not None, "Age table should not be None"
        assert table_sex is not None, "Sex table should not be None"
        assert table_race is not None, "Race table should not be None"
        assert table_hawaii is not None, "Hawaii table should not be None"


class TestDischargesSUResetFilters:
    """Test filter reset functionality."""
    
    def test_reset_filters_callback_exists(self):
        """Test that reset filters callback is defined."""
        assert hasattr(discharges_cooccurring_dashboard, 'reset_discharges_filters'), "Should have reset_discharges_filters function"
        assert callable(discharges_cooccurring_dashboard.reset_discharges_filters), "reset_discharges_filters should be callable"
    
    def test_reset_filters_returns_none_values(self):
        """Test that reset filters returns None for all filter values."""
        result = discharges_cooccurring_dashboard.reset_discharges_filters(1)
        
        # Should return 9 None values (one for each filter)
        assert len(result) == 9, f"Should return 9 values, got {len(result)}"
        assert all(v is None for v in result), "All filter values should be None after reset"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
