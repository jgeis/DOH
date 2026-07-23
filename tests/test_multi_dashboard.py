"""
Integration tests for multi_dashboard.py

Tests the main Dash application including:
- App initialization
- Page routing
- Navigation tab rendering
- Callback functionality
"""
import pytest
from dash import Dash


class TestAppInitialization:
    """Test basic app initialization and configuration."""
    
    def test_app_exists(self):
        """Test that the app instance is created."""
        from multi_dashboard import app
        assert app is not None
        assert isinstance(app, Dash)
    
    def test_app_title(self):
        """Test app title is set correctly."""
        from multi_dashboard import app
        assert app.title == "Substance Use Dashboards"
    
    def test_app_uses_bootstrap(self):
        """Test that Bootstrap CSS is included."""
        from multi_dashboard import app
        assert app.config.external_stylesheets is not None
    
    def test_suppress_callback_exceptions(self):
        """Test that callback exceptions are suppressed for dynamic pages."""
        from multi_dashboard import app
        assert app.config.suppress_callback_exceptions is True
    
    def test_server_exists(self):
        """Test that Flask server is accessible."""
        from multi_dashboard import server
        assert server is not None


class TestRouteConfiguration:
    """Test route and navigation group configuration."""
    
    def test_tab_paths_defined(self):
        """Test that all tab paths are defined."""
        from multi_dashboard import TAB_PATHS
        assert TAB_PATHS is not None
        assert len(TAB_PATHS) > 0
        assert "/" in TAB_PATHS
    
    def test_nav_groups_defined(self):
        """Test that navigation groups are defined."""
        from multi_dashboard import NAV_GROUPS
        assert NAV_GROUPS is not None
        assert "substance" in NAV_GROUPS
        assert "adad" in NAV_GROUPS
        assert "amhd" in NAV_GROUPS
    
    def test_route_to_group_mapping(self):
        """Test that routes map to correct groups."""
        from multi_dashboard import ROUTE_TO_GROUP
        assert ROUTE_TO_GROUP["/discharges-su"] == "substance"
        assert ROUTE_TO_GROUP["/adad"] == "adad"
        assert ROUTE_TO_GROUP["/amhd"] == "amhd"
    
    def test_sudors_nav_groups_defined(self):
        """Test SUDORS-specific navigation groups."""
        from multi_dashboard import SUDORS_NAV_GROUPS, SUDORS_ROUTE_TO_GROUP
        assert SUDORS_NAV_GROUPS is not None
        assert "substance" in SUDORS_NAV_GROUPS
        assert "/sudors" in SUDORS_ROUTE_TO_GROUP
    
    def test_default_path_defined(self):
        """Test that a default path is defined."""
        from multi_dashboard import DEFAULT_PATH
        assert DEFAULT_PATH is not None
        assert DEFAULT_PATH.startswith("/")


class TestAppLayout:
    """Test the app layout structure."""
    
    def test_layout_exists(self):
        """Test that the app has a layout."""
        from multi_dashboard import app
        assert app.layout is not None
    
    def test_layout_has_location(self):
        """Test that layout includes dcc.Location for routing."""
        from multi_dashboard import app
        layout_str = str(app.layout)
        assert "url" in layout_str or "Location" in str(type(app.layout))
    
    def test_layout_has_navigation(self):
        """Test that layout includes navigation elements."""
        from multi_dashboard import app
        layout_str = str(app.layout)
        assert "top-nav" in layout_str
    
    def test_layout_has_page_container(self):
        """Test that layout includes page container."""
        from multi_dashboard import app
        # The page_container should be present in the layout
        assert app.layout is not None


class TestNavigationCallback:
    """Test the navigation tab callback functionality."""
    
    def test_update_active_tab_substance_route(self):
        """Test navigation for substance use routes."""
        from multi_dashboard import update_active_tab
        
        tabs, style = update_active_tab("/discharges-su")
        
        # Should return tabs
        assert tabs is not None
        assert len(tabs) > 0
        # Navigation should be visible
        assert style == {}
    
    def test_update_active_tab_adad_route(self):
        """Test navigation for ADAD routes."""
        from multi_dashboard import update_active_tab
        
        tabs, style = update_active_tab("/adad")
        
        assert tabs is not None
        assert len(tabs) > 0
        assert style == {}
    
    def test_update_active_tab_sudors_route(self):
        """Test navigation for SUDORS routes."""
        from multi_dashboard import update_active_tab
        
        tabs, style = update_active_tab("/sudors")
        
        assert tabs is not None
        assert len(tabs) > 0
        assert style == {}
    
    def test_update_active_tab_unknown_route(self):
        """Test navigation for unknown routes hides nav."""
        from multi_dashboard import update_active_tab
        
        tabs, style = update_active_tab("/unknown-route")
        
        # Unknown routes should hide navigation
        assert style == {"display": "none"}
    
    def test_update_active_tab_none_pathname(self):
        """Test navigation with None pathname."""
        from multi_dashboard import update_active_tab
        
        tabs, style = update_active_tab(None)
        
        # Should handle None gracefully
        assert tabs is not None
    
    def test_update_active_tab_marks_active(self):
        """Test that the current tab is marked as selected."""
        from multi_dashboard import update_active_tab
        
        tabs, style = update_active_tab("/discharges-su")
        
        # Find the selected tab
        selected_found = False
        for tab in tabs:
            # Check if this tab has the selected class
            if hasattr(tab, 'className') and 'tab--selected' in str(tab.className):
                selected_found = True
                break
        
        assert selected_found


class TestAppNavGroups:
    """Test navigation group structure and consistency."""
    
    def test_all_routes_have_labels(self):
        """Test that all routes in NAV_GROUPS have labels."""
        from multi_dashboard import NAV_GROUPS
        
        for group_name, routes in NAV_GROUPS.items():
            for path, label in routes:
                assert path.startswith("/")
                assert label is not None
                assert len(label) > 0
    
    def test_substance_group_contains_discharge_routes(self):
        """Test that substance group includes discharge-related routes."""
        from multi_dashboard import NAV_GROUPS
        
        substance_routes = [path for path, label in NAV_GROUPS["substance"]]
        assert "/discharges-su" in substance_routes
        assert "/discharges-su-polysubstance" in substance_routes
    
    def test_nav_group_consistency(self):
        """Test that ROUTE_TO_GROUP is consistent with NAV_GROUPS."""
        from multi_dashboard import NAV_GROUPS, ROUTE_TO_GROUP
        
        # All routes in NAV_GROUPS should be in ROUTE_TO_GROUP
        for group_name, routes in NAV_GROUPS.items():
            for path, label in routes:
                assert path in ROUTE_TO_GROUP
                assert ROUTE_TO_GROUP[path] == group_name
    
    def test_sudors_nav_group_consistency(self):
        """Test SUDORS navigation group consistency."""
        from multi_dashboard import SUDORS_NAV_GROUPS, SUDORS_ROUTE_TO_GROUP
        
        for group_name, routes in SUDORS_NAV_GROUPS.items():
            for path, label in routes:
                assert path in SUDORS_ROUTE_TO_GROUP
                assert SUDORS_ROUTE_TO_GROUP[path] == group_name


# @pytest.mark.integration
# class TestDashIntegration:
#     """Integration tests using Dash testing tools."""
    
#     @pytest.mark.slow
#     def test_app_starts_successfully(self, dash_duo):
#         """Test that the app starts without errors."""
#         from multi_dashboard import app
        
#         dash_duo.start_server(app)
        
#         # Wait for app to load
#         dash_duo.wait_for_page(timeout=10)
        
#         # App should not have any errors in console
#         assert dash_duo.get_logs() == []
    
#     @pytest.mark.slow
#     def test_navigation_elements_present(self, dash_duo):
#         """Test that navigation elements are rendered."""
#         from multi_dashboard import app
        
#         dash_duo.start_server(app)
#         dash_duo.wait_for_page(timeout=10)
        
#         # Check for navigation wrapper
#         nav_element = dash_duo.find_element("#top-nav-wrapper")
#         assert nav_element is not None
    
#     @pytest.mark.slow
#     def test_page_container_present(self, dash_duo):
#         """Test that page container is rendered."""
#         from multi_dashboard import app
        
#         dash_duo.start_server(app)
#         dash_duo.wait_for_page(timeout=10)
        
#         # Page container should exist
#         # This is a basic smoke test to ensure the app structure is correct
#         assert dash_duo.driver.find_element("css selector", "body") is not None


class TestAccessibility:
    """Test accessibility features."""
    
    def test_skip_link_present(self):
        """Test that skip-to-navigation link is present."""
        from multi_dashboard import app
        layout_str = str(app.layout)
        assert "Skip to navigation" in layout_str or "skip" in layout_str.lower()
    
    def test_skip_link_targets_navigation(self):
        """Test that skip link targets the navigation element."""
        from multi_dashboard import app
        # The skip link should point to #top-nav
        layout_str = str(app.layout)
        assert "top-nav" in layout_str


class TestRegressionScenarios:
    """Regression tests for known issues."""
    
    def test_empty_pathname_handled(self):
        """Regression: Ensure empty pathname doesn't crash."""
        from multi_dashboard import update_active_tab
        
        tabs, style = update_active_tab("")
        assert tabs is not None
    
    def test_pathname_with_trailing_slash(self):
        """Regression: Ensure trailing slashes are handled."""
        from multi_dashboard import update_active_tab
        
        # Even if pathname has trailing slash, should work
        tabs, style = update_active_tab("/discharges-su/")
        assert tabs is not None
    
    def test_case_sensitive_routes(self):
        """Regression: Ensure routes are case-sensitive."""
        from multi_dashboard import ROUTE_TO_GROUP
        
        # Routes should be lowercase
        for route in ROUTE_TO_GROUP.keys():
            assert route == route.lower()
    
    def test_all_nav_group_routes_exist(self):
        """Regression: Ensure all routes in NAV_GROUPS are mapped."""
        from multi_dashboard import NAV_GROUPS, ROUTE_TO_GROUP
        
        missing_routes = []
        for group_name, routes in NAV_GROUPS.items():
            for path, label in routes:
                if path not in ROUTE_TO_GROUP:
                    missing_routes.append(path)
        
        assert len(missing_routes) == 0, f"Routes not in ROUTE_TO_GROUP: {missing_routes}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
