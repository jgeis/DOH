# mobile_app.py (desktop unaffected; mobile isolated)

# 
# - Dash, html, dcc: to build the web app and layout
# - Input, Output: for callbacks (interactive parts)
# - dash_bootstrap_components: for nicer layout and Bootstrap styling
# - importlib, traceback: to safely import other files and show errors if needed
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import importlib, traceback


def _safe_import(name, attr=None):
    """
    Try to import another Python file (module) by name.

    - If it works, we return either the whole module or a specific
      attribute (like 'layout') from that module.
    - If it fails, we quietly return None.

    Why: this lets the app still run even if one of the page files
    is missing or broken, instead of crashing everything.
    """
    try:
        mod = importlib.import_module(name)
        return getattr(mod, attr) if attr else mod
    except Exception:
        return None


# Try to import the three page modules for the dashboards.
# These are separate files that hold each page's layout and logic.
ALT_MOD  = _safe_import("app_alt")
POLY_MOD = _safe_import("polysubstance_dashboard")
CO_MOD   = _safe_import("cooccurring_dashboard_db")

# Check if each module has a layout defined.
# We use these flags later to decide which tabs to show on desktop.
ALT_LAYOUT  = getattr(ALT_MOD,  "layout",  None) if ALT_MOD  else None
POLY_LAYOUT = getattr(POLY_MOD, "layout",  None) if POLY_MOD else None
CO_LAYOUT   = getattr(CO_MOD,   "layout",  None) if CO_MOD   else None


# Create the main Dash app.
# - external_stylesheets: load Bootstrap theme
# - suppress_callback_exceptions: let us define callbacks for components
#   that aren't always on the screen
# - meta_tags: set the viewport so it behaves better on phones
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    meta_tags=[{
        "name": "viewport",
        "content": "width=device-width, initial-scale=1, maximum-scale=1"
    }],
)

# Expose the Flask server for deployment
server = app.server

# Name that shows up in the browser tab
app.title = "Substance Use Dashboards (Responsive)"


def make_nav():
    """
    Build a simple top navigation bar.

    Right now it just shows the app title.
    We could add links or logos here later if we want.
    """
    return dbc.NavbarSimple(
        brand="Substance Use Dashboards",
        brand_href="#",
        color="light",
        expand="md",
        className="mb-2",
    )


# -------- DESKTOP TABS (default Dash look; no custom class) --------
def make_desktop_tabs():
    """
    Build the row of tabs for desktop users.

    - Each tab corresponds to one of the dashboard pages.
    - Tabs are only added if that page module actually exists.
    - We also pick a sensible default tab to show first.

    Important: we do NOT add any custom CSS class here,
    so the desktop view keeps the normal Dash tab look.
    """
    tabs = []
    default_value = None

    # Small helper to create a basic tab
    def _tab(label, value):
        return dcc.Tab(label=label, value=value)

    # Add a tab for each layout that is available
    if ALT_LAYOUT is not None:
        tabs.append(_tab("Discharges related to substance use", "alt"))
        default_value = default_value or "alt"
    if POLY_LAYOUT is not None:
        tabs.append(_tab("Related to polysubstance use", "poly"))
        default_value = default_value or "poly"
    if CO_LAYOUT is not None:
        tabs.append(_tab("Co-occurring (DB)", "co"))
        default_value = default_value or "co"

    # If nothing is available, show a single "No pages" tab
    if not tabs:
        tabs = [_tab("No pages available", "none")]
        default_value = "none"

    # Return the whole tab component
    return dcc.Tabs(tabs, id="tabs", value=default_value)


# -------- MOBILE SWITCH (segmented 2-button) --------
def make_mobile_tabs():
    """
    Build the page switcher for mobile users.

    Instead of regular tabs, we use a row of "pills" (buttons)
    styled through CSS to look like segmented controls.

    The actual behavior is the same: picking a value changes the page.
    """
    options = []
    default_value = None

    # Add an option for each available page
    if ALT_LAYOUT is not None:
        options.append({"label": "Discharges", "value": "alt"})
        default_value = default_value or "alt"
    if POLY_LAYOUT is not None:
        options.append({"label": "Polysubstance", "value": "poly"})
        default_value = default_value or "poly"
    if CO_LAYOUT is not None:
        options.append({"label": "Co-occurring", "value": "co"})
        default_value = default_value or "co"

    # Fallback when no pages are available
    if not options:
        options = [{"label": "No pages", "value": "none"}]
        default_value = "none"

    # The CSS in assets/mobile.css will style these classes
    # to look like segmented buttons ONLY on smaller screens.
    return dcc.RadioItems(
        id="tabs",
        options=options,
        value=default_value,
        className="seg-tabs",            # main container
        inputClassName="seg-tab",        # actual radio inputs (often hidden)
        labelClassName="seg-tab-label",  # clickable pill labels
    )


def _page_for(value, is_mobile=False):
    """
    Given the selected tab value (alt, poly, co) and whether we're
    on mobile or not, return the right page layout.

    - If the page module has a layout_for() function, we call it with
      is_mobile so the page can adjust its own layout.
    - Otherwise, we fall back to the simple layout attribute.

    If anything goes wrong, we return a friendly message instead of crashing.
    """
    try:
        if value == "alt" and ALT_MOD:
            return ALT_MOD.layout_for(is_mobile) if hasattr(ALT_MOD, "layout_for") else ALT_MOD.layout
        if value == "poly" and POLY_MOD:
            return POLY_MOD.layout_for(is_mobile) if hasattr(POLY_MOD, "layout_for") else POLY_MOD.layout
        if value == "co" and CO_MOD:
            return CO_MOD.layout_for(is_mobile) if hasattr(CO_MOD, "layout_for") else CO_MOD.layout
    except Exception:
        pass
    return html.Div("No pages available.", className="p-3 text-muted")


# -------- Shells --------
def desktop_shell():
    """
    This is the outer frame for the desktop version of the app.

    It includes:
      - the top navigation bar,
      - the row of tabs,
      - an empty 'page-body' where we will place the current page.

    Why: separating the shell makes it easy to swap between
    desktop and mobile versions without touching the inner pages.
    """
    return dbc.Container(
        fluid=True,
        children=[
            make_nav(),
            make_desktop_tabs(),                    # desktop tabs
            html.Div(id="page-body", className="mt-3"),
        ],
        className="p-2"
    )


def mobile_shell():
    """
    This is the outer frame for the mobile version of the app.

    Differences from desktop:
      - uses a wrapper class 'mobile-root' so CSS can target mobile only
      - uses the mobile-style segmented buttons instead of normal tabs
      - slightly different spacing around the content
    """
    return html.Div(
        className="mobile-root",  # helps us target mobile styles in CSS
        children=[
            dbc.Container(
                fluid=True,
                children=[
                    make_nav(),
                    make_mobile_tabs(),                 # segmented buttons
                    html.Div(id="page-body", className="mt-2"),
                ],
                className="px-2"
            )
        ]
    )


# -------- Layout + width detection --------
# Top-level layout for the entire app.
# We:
#  - store whether the screen is "mobile" or not,
#  - use an Interval to measure the window size once,
#  - and load the desktop shell by default.
app.layout = html.Div([
    # Keeps a simple True/False flag for "is this mobile?"
    dcc.Store(id="is-mobile", storage_type="memory"),

    # Small timer that runs once on page load and triggers a JS check
    dcc.Interval(id="init-width", n_intervals=0, interval=100, max_intervals=1),

    # This is where we place either the desktop or mobile shell
    html.Div(id="app-shell", children=desktop_shell()),
])


# This is a small piece of JavaScript (client-side callback).
# It runs in the browser and checks the window width.
# If the width is less than 768px (Bootstrap's "md" breakpoint),
# we treat it as a mobile screen.
app.clientside_callback(
    """
    function(n){
      try{
        return (typeof window!=='undefined') && window.innerWidth < 768; // Bootstrap md breakpoint
      }catch(e){ return false; }
    }
    """,
    Output("is-mobile", "data"),
    Input("init-width", "n_intervals"),
)


@app.callback(Output("app-shell", "children"), Input("is-mobile", "data"))
def _swap_shell(is_mobile):
    """
    This callback swaps the whole outer layout depending on screen size.

    - If is_mobile is True, we show the mobile shell.
    - If is_mobile is False, we show the desktop shell.

    If something goes wrong, we show an error message instead of a blank page.
    """
    try:
        return mobile_shell() if is_mobile else desktop_shell()
    except Exception:
        return html.Div([
            html.H4("Layout error", className="text-danger"),
            html.Pre(traceback.format_exc(), style={"whiteSpace": "pre-wrap"})
        ], className="p-3")


@app.callback(
    Output("page-body", "children"),
    Input("tabs", "value"),
    Input("is-mobile", "data"),
)
def _render_page(tab_value, is_mobile):
    """
    This callback updates the main content area whenever:
      - the user changes tabs (or segmented buttons), or
      - the app switches between mobile and desktop.

    It picks the right page layout using _page_for() and drops it
    into the 'page-body' area.

    If something fails, we again show a readable error box.
    """
    try:
        return _page_for(tab_value, bool(is_mobile))
    except Exception:
        return html.Div([
            html.H4("Page render error", className="text-danger"),
            html.Pre(traceback.format_exc(), style={"whiteSpace": "pre-wrap"})
        ], className="p-3")


# This lets you run the app directly with: python mobile_app.py
# debug=True gives you live reload and nicer error messages during development.
if __name__ == "__main__":
    app.run(debug=True)
