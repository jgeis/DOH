# tests/test_app.py
from dash.testing.application_runners import import_app
import pytest

def test_app_loads(dash_duo):
    """
    GIVEN a Dash app
    WHEN the app is started
    THEN check that it loads without errors.
    """
    # The import_app function will find the `app` object in the specified module
    app = import_app("multi_dashboard")
    dash_duo.start_server(app)

    # Wait for the default page to load
    dash_duo.wait_for_page(url=f"http://localhost:{dash_duo.server.port}/")

    # Check that there are no severe browser errors
    assert dash_duo.get_logs() == [], "Browser console should contain no error"

    # You can also add assertions to check for specific components
    # For example, let's check if the main container is present
    dash_duo.wait_for_element(".container-fluid")
