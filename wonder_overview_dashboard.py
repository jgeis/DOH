from db_utils import execute_query
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
import plotly.express as px
from theme import register_template
from dashboard_utils import (
    make_kpi_card,
    make_left_sidebar,
    make_filters_card,
    checklist_filter,
    statewide_first,
)
import json

register_template()

# ----------------------------
# Data helpers
# ----------------------------

def load_sql_query(name, path="queries.sql"):
    """
    This helper looks inside the queries.sql file and pulls out
    the specific SQL block we want by name.

    Why: this keeps all the SQL in one file instead of hard-coding
    long queries directly in the Python file.
    """
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
    # The SQL file is split into blocks marked with "-- name:"
    blocks = sql.split("-- name:")
    m = {}
    for b in blocks:
        # Skip any empty chunks
        if not b.strip():
            continue
        # First line after "-- name:" is the name, the rest is the SQL text
        lines = b.strip().split("\n")
        m[lines[0].strip()] = "\n".join(lines[1:]).strip()
    # If we typed the wrong query name, complain loudly
    if name not in m:
        raise KeyError(f"Named query '{name}' not found in {path}.")
    return m[name]

def load_wonder_overview_df_from_db():
    """
    This helper:
      1. Loads the main SQL query by name.
      2. Connects to the database and runs the query.
      3. Cleans up some columns so the rest of the app is easier to write.

    Why: having this in one place avoids repeating the same database
    logic in multiple callbacks.
    
    Note: Uses either SQLite or MSSQL automatically based on config.
    """
    
    sql = load_sql_query("load_wonder_overview")
    
    # Execute query using db_utils (automatically uses correct database)
    df = execute_query(sql)
    print(f"load_wonder_overview returned {len(df):,} rows")

    # If there is no data, we stop early instead of showing a broken page
    if df.empty:
        raise RuntimeError("Query returned 0 rows.")

    # Make the year column numeric when possible so graphs treat it as numbers
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")

    # For these columns, replace missing values with "Unknown"
    # so we don't get blank labels in filters and tables.
    for col in ["county", "year"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")
    return df

# Load the full dataset once at startup.
# The callbacks will reuse this instead of hitting the database every time.
df_raw = load_wonder_overview_df_from_db()

# Count number of deaths in wonder_overview.csv "deaths" column
total_unique = df_raw["deaths"].count()

def sort_opts(series):
    """
    Turn a column into a sorted list of unique values.

    We also make sure "Unknown" always shows up at the end of the list
    so the drop-down menus look cleaner.
    """
    vals = pd.Series(series.unique()).astype(str)
    vals = sorted([v for v in vals if v != "Unknown"]) + (["Unknown"] if "Unknown" in vals.values else [])
    return vals

# Build the lists of choices for each filter only if the column exists.
# Why: this makes the code more flexible if the data shape changes later.
wonder_county_opts  = sort_opts(df_raw["county"])                           if "county"  in df_raw.columns else []
wonder_year_opts    = sorted(df_raw["year"].dropna().unique().tolist())     if "year"    in df_raw.columns else []

def opts_list(values):
    """
    Turn a simple list of values into the format Dash expects for
    drop-down choices (label + value).
    """
    return [{"label": v, "value": v} for v in values]


# ----------------------------
# Reusable graph block (Tools toggle + title + graph)
# ----------------------------

def graph_block(base_id: str, title_text: str, height_px: str):
    """
    Make a standard "card" that holds:
      - a hidden store that remembers if the tools are on/off
      - a small Tools button that the user clicks
      - a title for the plot
      - the actual graph area

    Why: we use this pattern for several plots, so this function keeps
    the layout consistent and avoids repeating the same code over and over.
    """
    return html.Div(
        [
            # Header row with the plot title.
            html.H5(title_text, id=f"{base_id}-title", className="plot-card-header mb-2"),

            # The actual graph. Modebar (tools) is always on now.
            dcc.Graph(
                id=base_id,
                style={"height": height_px, "width": "100%"},
                config={"displayModeBar": True, "displaylogo": False},
            ),
        ],
        className="mb-4",
        # This makes sure the tools bar is never cut off visually.
        style={"overflow": "visible"}
    )

# ----------------------------
# UI
# ----------------------------

# This link helps keyboard and screen reader users jump straight to the filters.
skip_link = html.A(
    "Skip to filters",
    href="#wonder-overview-filters",
    className="visually-hidden-focusable",
    tabIndex=0
)

# Big green card that shows the total number of discharges.
# Why: gives users a quick "at a glance" number when they open the page.
kpi_card = make_kpi_card(
    label="Number of Unintentional or Undetermined Overdose Deaths",
    count_id="wonder-kpi-deaths",
)

reset_filters_button = dbc.Button(
    "Reset All Filters",
    id="wonder-reset-filters-btn",
    color="secondary",
    outline=True,
    className="w-100 mb-3",
    n_clicks=0,
)

# Card holding all the filter controls down the left side.
# Each filter uses the options we built from the data above.
# Filter display order is managed centrally in dashboard_utils.make_filters_card.
filters_card = make_filters_card(
    card_id="wonder-overview-filters",
    title="Filter Data",
    filters=[
        checklist_filter(
            "County",
            "wonder-county-filter",
            options=opts_list(wonder_county_opts),
            value=[],
            labelStyle={"display": "block", "marginBottom": "0.25rem"},
            inputStyle={"marginRight": "0.4rem"},
            persistence="wonder-overview-county-filter",
            persistence_type="session",
        ),
        checklist_filter(
            "Calendar Year",
            "wonder-year-filter",
            options=opts_list(wonder_year_opts),
            value=[],
            labelStyle={"display": "block", "marginBottom": "0.25rem"},
            inputStyle={"marginRight": "0.4rem"},
            persistence="wonder-overview-year-filter",
            persistence_type="session",
        ),
    ],
)

wonder_overview_sidebar_text = [
    "Overview trends summarize overdose deaths over time and by county.",
    "* Values less than 10 are suppressed for privacy reasons and are displayed as <10.",
    "† Unintentional and undetermined intent drug overdose death data sourced from the State Unintentional Drug Overdose Reporting System (SUDORS).",
    "‡ Overdose death data sourced from the CDC Wide-ranging ONline Data for Epidemiologic Research (WONDER).",
]

def layout_for(
    is_mobile: bool = False,
    show_deaths: bool = True,
):
    """
    Build the full page layout, with slightly different heights if we
    are on a phone vs a larger screen.

    Why: on small screens we want taller plots so they are easier to read,
    but on desktops shorter plots look better side-by-side.
    """
    # Adjust plot heights depending on screen size.
    line_h  = "55vh" if is_mobile else "360px"
    bar_h  = "55vh" if is_mobile else "360px"

    # Left column: KPI, reset button, and filters.
    left_col = make_left_sidebar(
        kpi_card,
        reset_filters_button,
        filters_card,
        helper_text=wonder_overview_sidebar_text,
        xs=12,
        md=3,
    )

    # Center column: the main line and bar charts.
    center_col = dbc.Col(
        [
            dbc.Row([
                graph_block("wonder-line-deaths", "Deaths by Calendar Year", line_h),
                html.P("Line chart showing deaths by calendar year.", className="visually-hidden"),
            ]),
            dbc.Row([
                graph_block("wonder-bar-deaths", "Deaths by County", bar_h),
                html.P("Bar chart showing deaths by county.", className="visually-hidden"),
            ]),
        ],
        xs=12, md=8
    )

    # Wrap everything in a fluid container so it stretches with the screen.
    return dbc.Container([
        skip_link,
        html.Div(
            dbc.Row([left_col, center_col], className="g-3"),
            id="wonder-overview-section",
            style={} if show_deaths else {"display": "none"}
        ),

        html.Hr(
            className="my-5",
            style={} if (show_deaths) else {"display": "none"}
        ),

    ], fluid=True, className="p-2")


# This is the default layout used when the app imports this file.
# We pass False here since desktop is the standard case.
layout = layout_for(is_mobile=False)

# ----------------------------
# Figures + tables (no plotly titles)
# ----------------------------

@callback(
    Output("wonder-county-filter", "value"),
    Output("wonder-year-filter", "value"),
    Input("wonder-reset-filters-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_all_filters(_n_clicks):
    # Reset both filters to default empty state.
    return [], []

@callback(
    Output("wonder-kpi-deaths", "children"),
    Output("wonder-line-deaths", "figure"),
    Output("wonder-bar-deaths", "figure"),
    Input("wonder-county-filter", "value"),
    Input("wonder-year-filter", "value"),
)

def update_dashboard(county, year):
    """
    This function runs every time the user changes a filter.

    It:
      - Applies all the filters to the data,
      - Builds two graphs (line + stacked bar)
    """

    def apply_filter(frame, col, val):
        """
        Small helper so we don't repeat the same filter logic.

        If the user did not pick anything, we leave the data alone.
        If they picked one or more values, we only keep matching rows.
        """
        if val is None or (isinstance(val, (list, tuple)) and len(val) == 0):
            return frame
        if isinstance(val, (list, tuple)):
            return frame[frame[col].isin(val)]
        return frame[frame[col] == val]

    # Start from the full dataset each time.
    dff = df_raw.copy()

    # Only apply filters for columns that actually exist.
    if "county" in dff.columns:    dff = apply_filter(dff, "county", county)
    if "year" in dff.columns:      dff = apply_filter(dff, "year", year)

    # KPI should reflect the statewide total only.
    # We still honor the selected year filter, but do not sum county + statewide together.
    kpi_df = df_raw.copy()
    if "year" in kpi_df.columns:
        kpi_df = apply_filter(kpi_df, "year", year)
    if "county" in kpi_df.columns:
        statewide_mask = kpi_df["county"].astype(str).str.strip().str.lower() == "statewide"
        if statewide_mask.any():
            kpi_df = kpi_df[statewide_mask]

    filter_total = kpi_df["deaths"].sum()

    # ---------- Line chart: Deaths by Calendar Year (by county) ----------
    if {"county", "year"}.issubset(dff.columns):
        by_year = (
            dff.groupby(["year", "county"], as_index=False)["deaths"]
            .sum()
            .sort_values(["year", "county"])
        )
        county_order = statewide_first(sort_opts(by_year["county"]))
        by_year["county"] = pd.Categorical(by_year["county"], categories=county_order, ordered=True)
        by_year = by_year.sort_values(["year", "county"])
        by_year["display_count"] = by_year["deaths"].apply(
            lambda x: "<10" if x < 10 else f"{int(x):,}"
        )

        year_line = px.line(
            by_year,
            x="year",
            y="deaths",
            color="county",
            markers=True,
            text="display_count",
            category_orders={"county": county_order},
            labels={"year": "Calendar Year", "deaths": "Number of Deaths", "county": "County"},
        )

        year_line.update_traces(
            textposition="top center",
            hovertemplate="Year %{x}<br>County: %{fullData.name}<br>Deaths: %{text}<extra></extra>",
        )

        year_line.update_layout(
            margin=dict(l=0, r=0, t=10, b=80),
            xaxis=dict(automargin=True, dtick=1),
        )

    else:
        year_line = px.line()

    # ---------- Bar chart: Deaths by Substance ----------
    if {"county", "year"}.issubset(dff.columns):
        by_county = (
            dff.groupby("county", as_index=False)["deaths"]
            .sum()
            .sort_values("deaths", ascending=False)
        )

        if "county" in by_county.columns:
            statewide_rows = by_county[by_county["county"].astype(str).str.strip().str.lower() == "statewide"]
            other_rows = by_county[by_county["county"].astype(str).str.strip().str.lower() != "statewide"]
            by_county = pd.concat([statewide_rows, other_rows], ignore_index=True)

        county_bar = px.bar(
            by_county,
            x="deaths",
            y="county",
            barmode="stack",
            text="deaths",
            labels={"deaths": "Number of Deaths", "county": "County of Death"},
        )

        county_bar.update_traces(
            textposition="outside",
        )

        county_bar.update_layout(
            margin=dict(l=0, r=0, t=10, b=80),
            xaxis=dict(automargin=True),
            yaxis=dict(autorange="reversed"),
        )

    else:
        county_bar = px.bar()

    # Return all the updated visuals and tables to Dash
    return (
        f"{filter_total:,}",
        year_line,
        county_bar
    )
