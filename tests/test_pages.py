"""
Tests for individual dashboard pages.

Tests page registration, layout generation, and basic rendering
for all pages in the multi-page dashboard application.
"""
import pytest
from dash import page_registry
import importlib
import os

# Check if Selenium is available for browser-based tests
try:
    import selenium
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


# List of all page modules to test
PAGE_MODULES = [
    "pages.home",
    "pages.discharges_su",
    "pages.discharges_su_polysubstance",
    "pages.discharges_su_co_sud_mh",
    "pages.discharges_su_co_mh_sud",
    "pages.discharges_mh",
    "pages.discharges_mh_co_sud_mh",
    "pages.discharges_mh_co_mh_sud",
    "pages.sudors",
    "pages.sudors_polysubstance",
    "pages.dose",
    "pages.wonder_overview",
    "pages.wonder_breakdown",
    "pages.cares_call_volume",
    "pages.cares_statistics",
    "pages.crisis_mobile_outreach",
    "pages.adad",
    "pages.adad_cooccurring",
    "pages.camhd",
    "pages.camhd_cooccurring",
    "pages.amhd",
    "pages.amhd_cooccurring",
    "pages.lcrs",
    "pages.sicm",
]


class TestPageRegistration:
    """Test that all pages are properly registered."""
    
    def test_all_pages_can_import(self):
        """Test that all page modules can be imported without errors."""
        failed_imports = []
        
        for module_name in PAGE_MODULES:
            try:
                importlib.import_module(module_name)
            except Exception as e:
                failed_imports.append((module_name, str(e)))
        
        assert len(failed_imports) == 0, f"Failed imports: {failed_imports}"
    
    def test_home_page_registered(self):
        """Test that the home page is registered at root path."""
        # Import multi_dashboard to ensure pages are registered
        import multi_dashboard
        
        # Check if root path is in registry
        root_page = None
        for page in page_registry.values():
            if page.get('path') == '/':
                root_page = page
                break
        
        assert root_page is not None, "Home page not found in registry"
    
    def test_all_pages_registered(self):
        """Test that all pages are in the page registry."""
        import multi_dashboard
        
        expected_paths = [
            "/",
            "/discharges-su",
            "/discharges-mh",
            "/sudors",
            "/dose",
            "/adad",
            "/amhd",
            "/camhd",
        ]
        
        registered_paths = [page['path'] for page in page_registry.values()]
        
        for path in expected_paths:
            assert path in registered_paths, f"Path {path} not registered"
    
    def test_pages_have_titles(self):
        """Test that all registered pages have titles."""
        import multi_dashboard
        
        for page_info in page_registry.values():
            assert 'title' in page_info
            assert page_info['title'] is not None
            assert len(page_info['title']) > 0


class TestPageLayouts:
    """Test page layout generation."""
    
    def test_home_page_has_layout(self):
        """Test that home page has a valid layout."""
        from pages import home
        
        assert hasattr(home, 'layout')
        assert home.layout is not None
    
    def test_home_page_layout_content(self):
        """Test that home page contains navigation links."""
        from pages import home
        
        layout_str = str(home.layout)
        # Should contain links to other pages
        assert "href" in layout_str, "Home page should contain navigation links"
    
    def test_dashboard_pages_have_layouts(self):
        """Test that all dashboard pages have layouts."""
        dashboard_pages = [
            "pages.discharges_su",
            "pages.discharges_mh",
            "pages.sudors",
            "pages.adad",
        ]
        
        for module_name in dashboard_pages:
            module = importlib.import_module(module_name)
            assert hasattr(module, 'layout'), f"{module_name} missing layout"
            assert module.layout is not None, f"{module_name} layout is None"
    
    def test_page_layouts_are_callable_or_objects(self):
        """Test that all registered page modules have valid layouts."""
        import multi_dashboard
        
        for page_info in page_registry.values():
            module_name = page_info.get('module')
            if module_name and module_name != "pages.home":
                # Import the actual module object from the module name string
                module = importlib.import_module(module_name)
                # Layout can be a function or a component
                assert hasattr(module, 'layout'), f"Module {module_name} missing layout"
                assert module.layout is not None, f"Module {module_name} layout is None"

class TestPagePaths:
    """Test page path configurations."""
    
    def test_all_paths_start_with_slash(self):
        """Test that all page paths start with /."""
        import multi_dashboard
        
        for page_info in page_registry.values():
            path = page_info.get('path')
            assert path is not None
            assert path.startswith('/'), f"Path {path} doesn't start with /"
    
    def test_no_duplicate_paths(self):
        """Test that there are no duplicate paths."""
        import multi_dashboard
        
        paths = [page['path'] for page in page_registry.values()]
        assert len(paths) == len(set(paths)), "Duplicate paths found"
    
    def test_paths_match_tab_paths(self):
        """Test that page paths match TAB_PATHS configuration."""
        import multi_dashboard
        try:
            from multi_dashboard import TAB_PATHS
        except ImportError:
            pytest.skip("TAB_PATHS not available")
        
        registered_paths = [page['path'] for page in page_registry.values()]
        
        # All TAB_PATHS should be registered
        for tab_path in TAB_PATHS.keys():
            assert tab_path in registered_paths, f"TAB_PATH {tab_path} not registered as page"


class TestPageMetadata:
    """Test page metadata and configuration."""
    
    def test_pages_have_names(self):
        """Test that all pages have names."""
        import multi_dashboard
        
        for page_info in page_registry.values():
            assert 'name' in page_info
            assert page_info['name'] is not None
    
    def test_page_names_are_descriptive(self):
        """Test that page names are descriptive (not empty)."""
        import multi_dashboard
        
        for page_info in page_registry.values():
            name = page_info.get('name', '')
            assert len(name) > 0, f"Page {page_info.get('path')} has empty name"
    
    def test_substance_use_pages_have_appropriate_titles(self):
        """Test that substance use pages have appropriate titles."""
        import multi_dashboard
        
        su_paths = ['/discharges-su', '/sudors', '/dose']
        
        for page_info in page_registry.values():
            if page_info['path'] in su_paths:
                title = page_info.get('title', '').lower()
                # Should reference substance or related terms
                assert any(term in title for term in [
                    'substance', 'discharge', 'overdose', 'sudors', 'dose', 'drug'
                ]), f"SU page {page_info['path']} has non-descriptive title: {page_info.get('title')}"


class TestDashboardPageStructure:
    """Test that dashboard pages follow expected structure."""
    
    def test_discharge_su_page_structure(self):
        """Test that discharge SU page has expected structure."""
        from pages import discharges_su
        
        assert hasattr(discharges_su, 'layout')
        assert discharges_su.layout is not None
    
    def test_dashboard_modules_exist(self):
        """Test that dashboard modules exist for page modules."""
        dashboard_modules = [
            "discharges_su_dashboard",
            "discharges_mh_dashboard",
            "sudors_dashboard",
            "dose_dashboard",
            "adad_dashboard",
            "amhd_dashboard",
        ]
        
        failed_imports = []
        for module_name in dashboard_modules:
            try:
                importlib.import_module(module_name)
            except Exception as e:
                failed_imports.append((module_name, str(e)))
        
        # At least some dashboard modules should exist
        # (Some may be optional or not yet implemented)
        if len(dashboard_modules) > 0:
            assert len(failed_imports) < len(dashboard_modules), f"All dashboard modules failed to import: {failed_imports}"


@pytest.mark.integration
@pytest.mark.skipif(
    not SELENIUM_AVAILABLE,
    reason="Selenium is required for browser-based rendering tests. Install with: pip install selenium pytest-dash"
)
class TestPageRendering:
    """Integration tests for page rendering (requires Selenium)."""
    
    @pytest.mark.slow
    def test_home_page_renders(self, dash_duo):
        """Test that home page renders without errors."""
        from multi_dashboard import app
        
        dash_duo.start_server(app)
        dash_duo.wait_for_page(timeout=10)
        
        # Navigate to home
        dash_duo.driver.get(dash_duo.driver.current_url)
        
        # Should not have errors
        assert dash_duo.get_logs() == []
    
    @pytest.mark.slow
    @pytest.mark.parametrize("path", [
        "/",
        "/discharges-su",
        "/discharges-mh",
    ])
    def test_pages_load_without_errors(self, dash_duo, path):
        """Test that key pages load without errors."""
        from multi_dashboard import app
        
        dash_duo.start_server(app)
        dash_duo.wait_for_page(timeout=10)
        
        # Navigate to the page
        dash_duo.driver.get(dash_duo.server_url + path)
        
        # Wait for page to load
        dash_duo.wait_for_page(timeout=10)
        
        # Check for no errors
        logs = dash_duo.get_logs()
        # Filter out common warnings that aren't errors
        errors = [log for log in logs if 'error' in log.lower() and 'warning' not in log.lower()]
        assert len(errors) == 0, f"Errors found on {path}: {errors}"


class TestPageNavigation:
    """Test navigation between pages."""
    
    def test_home_page_has_links_to_dashboards(self):
        """Test that home page contains links to dashboard pages."""
        from pages import home
        
        layout_str = str(home.layout)
        
        # Should have links to major dashboards
        expected_links = [
            "/discharges-su",
            "/discharges-mh",
            "/sudors",
            "/adad",
        ]
        
        for link in expected_links:
            assert link in layout_str, f"Link to {link} not found on home page"
    
    def test_navigation_paths_are_consistent(self):
        """Test that navigation paths match registered pages."""
        from pages import home
        import multi_dashboard
        
        layout_str = str(home.layout)
        registered_paths = [page['path'] for page in page_registry.values()]
        
        # Extract hrefs from home page (simple check)
        import re
        hrefs = re.findall(r'href="([^"]+)"', layout_str)
        
        for href in hrefs:
            if href.startswith('/'):
                assert href in registered_paths, f"Home page links to unregistered path: {href}"


class TestRegressionScenarios:
    """Regression tests for page-related issues."""
    
    def test_all_page_files_exist(self):
        """Regression: Ensure all page files exist in filesystem."""
        pages_dir = "pages"
        
        for module_name in PAGE_MODULES:
            # Convert module name to file path
            file_name = module_name.replace("pages.", "") + ".py"
            file_path = os.path.join(pages_dir, file_name)
            
            assert os.path.exists(file_path), f"Page file not found: {file_path}"
    
    def test_no_circular_imports(self):
        """Regression: Ensure no circular imports in page modules."""
        # Try importing all pages in different orders
        import random
        modules_copy = PAGE_MODULES.copy()
        random.shuffle(modules_copy)
        
        failed = []
        for module_name in modules_copy:
            try:
                importlib.reload(importlib.import_module(module_name))
            except Exception as e:
                failed.append((module_name, str(e)))
        
        assert len(failed) == 0, f"Circular import issues: {failed}"
    
    def test_page_registry_not_empty(self):
        """Regression: Ensure page registry is populated."""
        import multi_dashboard
        
        assert len(page_registry) > 0, "Page registry is empty"
    
    def test_duplicate_page_names(self):
        """Regression: Check for duplicate page names."""
        import multi_dashboard
        
        # Some page names are intentionally duplicated across different paths
        allowed_duplicates = {
            "Related to co-occurring SUD (primary) and MH disorder (secondary)",
            "Related to co-occurring MH disorder (primary) and SUD (secondary)",
        }
        
        names = [page['name'] for page in page_registry.values()]
        duplicates = [name for name in names if names.count(name) > 1 and name not in allowed_duplicates]
        
        assert len(duplicates) == 0, f"Duplicate page names found: {set(duplicates)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
