"""
Query to generate the tests:
cares_statistics_dashboard.py is different than all the other dashboards.  There are no filters, no kpi card, etc.  
It's formatted completely differently and the values displayed in it are going to change over time.  
Given all this, generate tests to verify the format.  For example, verify there are two sections "Past Month" and "Past 6 Months".
Verify the "Past Month" section shows 3 rows with 4 columns each, and so on and so forth.
"""
import pytest
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.graph_objects as go
import cares_statistics_dashboard

@pytest.mark.integration
class TestCaresStatisticsDashboard:
    """
    Integration tests for cares_statistics_dashboard.py.
    Because this dashboard has no interactive filters, these tests verify 
    the data loader functions and the static structural formatting of the page layout.
    """

    def test_page_and_module_structure(self):
        """Test that the page is registered and the module has the necessary components."""
        from dash import page_registry
        import multi_dashboard  # Ensures pages are registered
        
        paths = [page['path'] for page in page_registry.values()]
        assert '/cares-statistics' in paths, "/cares-statistics page should be registered"
        
        from pages import cares_statistics
        assert hasattr(cares_statistics, 'layout'), "Page module should have a layout"
        assert hasattr(cares_statistics_dashboard, 'layout'), "Dashboard module should have a layout"
        # Notice we do NOT check for update_dashboard here, as this page uses static loading

    def test_data_loaders(self):
        """Test that all individual data loading functions execute successfully."""
        from cares_statistics_dashboard import (
            _load_top_box_data, 
            _load_top_10_reasons_table, 
            _load_calls_line_chart, 
            _load_cmo_bar_chart
        )
        
        # 1. Test KPI Top Box Data
        top_box_data = _load_top_box_data()
        assert isinstance(top_box_data, dict), "Top box data should return a dictionary"
        
        # 2. Test Top 10 Table Data
        top_10_df = _load_top_10_reasons_table()
        assert not top_10_df.empty, "Top 10 reasons table should not be empty"
        assert 'Category' in top_10_df.columns, "Table should have a 'Category' column"
        assert 'Percent' in top_10_df.columns, "Table should have a 'Percent' column"
        
        # 3. Test Line Chart Generation
        line_fig = _load_calls_line_chart()
        assert isinstance(line_fig, go.Figure), "Should return a Plotly figure"
        assert len(line_fig.data) > 0, "Line chart should have data traces"
        
        # 4. Test Bar Chart Generation
        bar_fig = _load_cmo_bar_chart()
        assert isinstance(bar_fig, go.Figure), "Should return a Plotly figure"
        assert len(bar_fig.data) > 0, "Bar chart should have data traces"

    def test_layout_structure_and_formatting(self):
        """
        Traverse the generated Dash layout to verify structural requirements 
        (e.g., banners, 3x4 KPI grid, chart placement).
        """
        layout = cares_statistics_dashboard.layout()
        
        # 1. Verify the layout successfully generated and didn't hit the Exception Alert fallback
        assert isinstance(layout, dbc.Container)
        assert not isinstance(layout.children, dbc.Alert), "Layout failed to load data and returned an error alert."
        
        # The main container should have exactly 3 children: Row 1, Hr (divider), Row 2
        assert len(layout.children) == 3, "Dashboard should be split into a top row, divider, and bottom row"
        row1, hr, row2 = layout.children
        
        # ---------------------------------------------------------
        # VERIFY SECTION 1: "Past Month" (KPI Grid)
        # ---------------------------------------------------------
        assert "Past Month" in str(row1), "The 'Past Month' banner text is missing"
        
        # Row 1 has two columns: the Banner (children[0]) and the KPI Grid (children[1])
        kpi_grid_container = row1.children[1]
        kpi_grid = kpi_grid_container.children # The inner dbc.Row holding the cards
        
        # Verify 12 cards exist (4 calls, 4 chats, 4 texts)
        assert len(kpi_grid.children) == 12, "Expected exactly 12 KPI cards"
        
        # Verify it generates a 3 Row x 4 Column grid
        # Bootstrap creates a 4-column layout when elements are set to md=3 (12 total span / 3 = 4 cols)
        for col in kpi_grid.children:
            assert col.md == 3, "KPI columns must have md=3 to form 4 columns per row"
            assert isinstance(col.children, dbc.Card), "Each grid item must be a dbc.Card"

        # ---------------------------------------------------------
        # VERIFY SECTION 2: "Past 6 Months" (Charts & Tables)
        # ---------------------------------------------------------
        assert "Past 6 Months" in str(row2), "The 'Past 6 Months' banner text is missing"
        
        # Row 2 has two columns: the Banner (children[0]) and Content (children[1])
        content_container = row2.children[1]
        content_row = content_container.children # The inner dbc.Row holding the 3 content blocks
        
        assert len(content_row.children) == 3, "Expected 3 horizontal layout columns in the bottom section"
        table_col, line_col, bar_col = content_row.children
        
        # Verify Table Column
        assert "Top 10 reasons" in str(table_col), "Missing Top 10 reasons table header"
        
        # Verify Line Chart Column
        assert "Phone Call, Chat, & Text Volumes" in str(line_col), "Missing Volumes line chart header"
        line_graph = line_col.children[1]
        assert isinstance(line_graph, dcc.Graph), "Line chart component is missing"
        assert line_graph.id == "cares-statistics-calls-line-chart"
        
        # Verify Bar Chart Column
        assert "Crisis Mobile Outreach (CMO)" in str(bar_col), "Missing CMO bar chart header"
        bar_graph = bar_col.children[1]
        assert isinstance(bar_graph, dcc.Graph), "Bar chart component is missing"
        assert bar_graph.id == "cares-statistics-cmo-bar-chart"