from db_utils import execute_query
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
import plotly.express as px
from theme import register_template
import re

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


sql_substance = load_sql_query("load_wonder_substance")
df_raw_substance = execute_query(sql_substance)

sql_race = load_sql_query("load_wonder_race")
df_raw_race = execute_query(sql_race)

sql_age_group = load_sql_query("load_wonder_age_group")
df_raw_age_group = execute_query(sql_age_group)

sql_gender = load_sql_query("load_wonder_gender")
df_raw_gender = execute_query(sql_gender)

# Count number of deaths in wonder_gender.csv "deaths" column
total_unique = df_raw_gender["deaths"].count()

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
wonder_county_opts  = sort_opts(df_raw_gender["county"])                           if "county"  in df_raw_gender.columns else []
wonder_year_opts    = sorted(df_raw_gender["year"].dropna().unique().tolist())     if "year"    in df_raw_gender.columns else []

DEFAULT_COUNTY = "Statewide" if "Statewide" in wonder_county_opts else (wonder_county_opts[0] if wonder_county_opts else None)
DEFAULT_YEAR = wonder_year_opts[-1] if wonder_year_opts else None

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
    href="#wonder-breakdown-filters",
    className="visually-hidden-focusable",
    tabIndex=0
)

# Big green card that shows the total number of discharges.
# Why: gives users a quick "at a glance" number when they open the page.
kpi_card = dbc.Card(
    dbc.CardBody([
        html.H2(id="wonder-breakdown-kpi-deaths", className="text-white"),
        html.Small("Number of Unintentional/Undetermined Overdose Deaths", className="card-title text-white"),
    ]),
    className="bg-success text-center mb-4"
)

reset_filters_button = dbc.Button(
    "Reset All Filters",
    id="wonder-breakdown-reset-filters-btn",
    color="secondary",
    outline=True,
    className="w-100 mb-3",
    n_clicks=0,
)

# Card holding all the filter controls down the left side.
# Each filter uses the options we built from the data above.
filters_card = dbc.Card(
    dbc.CardBody([
        html.H5("Filter Data", tabIndex=1),

        html.Label("County", htmlFor="wonder-breakdown-county-filter", className="form-label"),
        dcc.RadioItems(
            id="wonder-breakdown-county-filter",
            options=opts_list(wonder_county_opts),
            value=DEFAULT_COUNTY,
            className="mb-2",
            labelStyle={"display": "block", "marginBottom": "0.25rem"},
            inputStyle={"marginRight": "0.4rem"},
        ),
        html.Label("Calendar Year", htmlFor="wonder-breakdown-year-filter", tabIndex=3, className="form-label"),
        dcc.RadioItems(
            id="wonder-breakdown-year-filter", options=opts_list(wonder_year_opts),
            value=DEFAULT_YEAR,
            className="mb-2",
            labelStyle={"display": "block", "marginBottom": "0.25rem"},
            inputStyle={"marginRight": "0.4rem"},
            persistence=True, persistence_type="session"
        ),
        html.Div(
            [
                html.P("* Values less than 10 are suppressed for privacy reasons and are displayed as <10.", className="small text-muted mb-1"),
                html.P("† Unintentional and undetermined intent drug overdose death data sourced from the State Unintentional Drug Overdose Reporting System (SUDORS).", className="small text-muted mb-1"),
                html.P("‡ Overdose death data sourced from the CDC Wide-ranging ONline Data for Epidemiologic Research (WONDER).", className="small text-muted mb-0"),
            ],
            className="mt-3",
        ),
    ]),
    id="wonder-breakdown-filters",
    className="mb-4"
)

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
    bar_h  = "55vh" if is_mobile else "360px"
    pie_h  = "46vh" if is_mobile else "260px"

    # Left column: KPI, reset button, and filters.
    left_col = dbc.Col([kpi_card, reset_filters_button, filters_card], xs=12, md=3)

    # Center column: the main line and bar charts.
    center_col = dbc.Col(
        [
            dbc.Row([
                graph_block("wonder-substance-deaths", "Deaths by Substance", bar_h),
                html.P("Bar chart showing deaths by substance.", className="visually-hidden"),
            ]),
            dbc.Row([
                graph_block("wonder-race-deaths", "Deaths by Race", bar_h),
                html.P("Bar chart showing deaths by race.", className="visually-hidden"),
            ]),
            dbc.Row([
                graph_block("wonder-age-group-deaths", "Deaths by Age Group", bar_h),
                html.P("Bar chart showing deaths by age group.", className="visually-hidden"),
            ]),
        ],
        xs=12, md=6
    )

    right_col = dbc.Col(
        [
            graph_block("wonder-gender-deaths", "Deaths by Gender", pie_h),
            html.P("Pie chart showing deaths by gender.", className="visually-hidden"),
        ],
        xs=12, md=3
    )

    # Wrap everything in a fluid container so it stretches with the screen.
    return dbc.Container([
        skip_link,
        html.Div(
            dbc.Row([left_col, center_col, right_col], className="g-3"),
            id="discharges-section",
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
    Output("wonder-breakdown-county-filter", "value"),
    Output("wonder-breakdown-year-filter", "value"),
    Input("wonder-breakdown-reset-filters-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_all_filters(_n_clicks):
    # Reset both filters to default values.
    return DEFAULT_COUNTY, DEFAULT_YEAR

@callback(
    Output("wonder-breakdown-kpi-deaths", "children"),
    Output("wonder-substance-deaths", "figure"),
    Output("wonder-race-deaths", "figure"),
    Output("wonder-age-group-deaths", "figure"),
    Output("wonder-gender-deaths", "figure"),
    Input("wonder-breakdown-county-filter", "value"),
    Input("wonder-breakdown-year-filter", "value"),
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
    dff = df_raw_gender.copy()

    # Only apply filters for columns that actually exist.
    if "county" in dff.columns:    dff = apply_filter(dff, "county", county)
    if "year" in dff.columns:      dff = apply_filter(dff, "year", year)

    # Count unique discharges (each record_id represents one discharge).
    # Used to update the total on the KPI card when user selects the filter
    filter_total = dff["deaths"].sum()

    def filter_df(df):
        if "county" in df.columns:
            df = apply_filter(df, "county", county)
        if "year" in df.columns:
            df = apply_filter(df, "year", year)
        return df

    dff_substance = filter_df(df_raw_substance.copy())
    dff_race = filter_df(df_raw_race.copy())
    dff_age_group = filter_df(df_raw_age_group.copy())
    dff_gender = filter_df(df_raw_gender.copy())

    # ---------- Bar chart: Deaths by Substance ----------
    if {"county", "year", "substance"}.issubset(dff_substance.columns):
        by_sub = (
            dff_substance.groupby("substance", as_index=False)["deaths"]
            .sum()
            .sort_values("deaths", ascending=False)
        )
        by_sub["display_count"] = by_sub["deaths"].apply(
            lambda x: "<10*" if x < 10 else f"{int(x):,}"
        )

        sub_bar = px.bar(
            by_sub,
            x="deaths",
            y="substance",
            barmode="stack",
            text="display_count",
            labels={"deaths": "Number of Deaths", "substance": "Substance"},
        )

        sub_bar.update_traces(
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}: %{text}<extra></extra>",
        )

        max_deaths = by_sub["deaths"].max() if not by_sub.empty else 0
        x_max = max(10, int(max_deaths * 1.15))

        sub_bar.update_layout(
            margin=dict(l=140, r=50, t=10, b=80),
            xaxis=dict(automargin=True, range=[0, x_max]),
            yaxis=dict(autorange="reversed"),
        )

    else:
        sub_bar = px.bar()


    # ---------- Bar chart: Deaths by Race ----------
    if {"county", "year", "race"}.issubset(dff_race.columns):
        by_race = (
            dff_race.groupby("race", as_index=False)["deaths"]
            .sum()
            .sort_values("deaths", ascending=False)
        )
        by_race["display_count"] = by_race["deaths"].apply(
            lambda x: "<10*" if x < 10 else f"{int(x):,}"
        )

        race_bar = px.bar(
            by_race,
            x="deaths",
            y="race",
            barmode="stack",
            text="display_count",
            labels={"deaths": "Number of Deaths", "race": "Race"},
        )

        race_bar.update_traces(
            textposition="outside",
            hovertemplate="%{y}: %{text}<extra></extra>",
        )

        race_bar.update_layout(
            margin=dict(l=0, r=0, t=10, b=80),
            xaxis=dict(automargin=True),
            yaxis=dict(autorange="reversed"),
        )

    else:
        race_bar = px.bar()

    # ---------- Bar chart: Deaths by Age Group ----------
    if {"county", "year", "age_group"}.issubset(dff_age_group.columns):
        by_age_group = (
            dff_age_group.groupby("age_group", as_index=False)["deaths"]
            .sum()
        )

        def age_group_sort_key(label):
            text = str(label).strip()
            lower = text.lower()

            normalized = lower.replace(" ", "")
            if normalized in {"<1", "under1"}:
                return -2

            if lower.startswith("under"):
                return -1
            if lower == "unknown":
                return 10**9

            m = re.search(r"\d+", text)
            return int(m.group()) if m else 10**8

        by_age_group["_age_sort"] = by_age_group["age_group"].apply(age_group_sort_key)
        by_age_group = by_age_group.sort_values("_age_sort").drop(columns=["_age_sort"])
        by_age_group["display_count"] = by_age_group["deaths"].apply(
            lambda x: "<10*" if x < 10 else f"{int(x):,}"
        )

        age_group_bar = px.bar(
            by_age_group,
            x="deaths",
            y="age_group",
            barmode="stack",
            text="display_count",
            labels={"deaths": "Number of Deaths", "age_group": "Age Group"},
        )

        age_group_bar.update_traces(
            textposition="outside",
            hovertemplate="%{y}: %{text}<extra></extra>",
        )

        age_group_bar.update_layout(
            margin=dict(l=0, r=0, t=10, b=80),
            xaxis=dict(automargin=True),
            yaxis=dict(autorange="reversed"),
        )

    else:
        age_group_bar = px.bar()

    # ---------- Pie chart: Deaths by Gender ----------
    if "gender" in dff_gender.columns:
        by_gender = (
            dff_gender.groupby("gender", as_index=False)["deaths"]
            .sum()
            .sort_values("gender")
        )
        by_gender["display_count"] = by_gender["deaths"].apply(
            lambda x: "<10*" if x < 10 else f"{int(x):,}"
        )
        gender_pie = px.pie(
            by_gender,
            names="gender",
            values="deaths",
            hole=0.35,
            custom_data=["display_count"],
        )
        gender_pie.update_traces(
            textposition="inside",
            texttemplate="%{label}<br>%{percent:.1%} (%{customdata[0]})",
            hovertemplate="%{label}: %{customdata[0]} (%{percent:.1%})<extra></extra>"
        )
        gender_pie.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    else:
        gender_pie = px.pie()

    # Return all the updated visuals and tables to Dash
    return (
        f"{filter_total:,}",
        sub_bar,
        race_bar,
        age_group_bar,
        gender_pie,
    )
