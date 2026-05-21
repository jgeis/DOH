from db_utils import execute_query
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
import plotly.express as px
from theme import register_template
from dashboard_utils import (
    make_kpi_card,
    make_left_sidebar,
    compute_last_updated_value,
    make_filters_card,
    radio_filter,
    STATEWIDE_COUNTY,
    format_count_display,
    apply_standard_bar_layout,
)
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

last_updated_value = max(
    (
        value
        for value in [
            compute_last_updated_value(df_raw_substance),
            compute_last_updated_value(df_raw_race),
            compute_last_updated_value(df_raw_age_group),
            compute_last_updated_value(df_raw_gender),
        ]
        if value
    ),
    default=None,
)

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
kpi_card = make_kpi_card(
    label="Number of Unintentional or Undetermined Overdose Deaths",
    count_id="wonder-breakdown-kpi-deaths",
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
# Filter display order is managed centrally in dashboard_utils.make_filters_card.
filters_card = make_filters_card(
    card_id="wonder-breakdown-filters",
    title="Filter Data",
    filters=[
        radio_filter(
            "County",
            "wonder-breakdown-county-filter",
            options=opts_list(wonder_county_opts),
            value=DEFAULT_COUNTY,
            labelStyle={"display": "block", "marginBottom": "0.25rem"},
            inputStyle={"marginRight": "0.4rem"},
            persistence="wonder-breakdown-county-filter",
            persistence_type="session",
        ),
        radio_filter(
            "Calendar Year",
            "wonder-breakdown-year-filter",
            options=opts_list(wonder_year_opts),
            value=DEFAULT_YEAR,
            labelStyle={"display": "block", "marginBottom": "0.25rem"},
            inputStyle={"marginRight": "0.4rem"},
            persistence="wonder-breakdown-year-filter",
            persistence_type="session",
        ),
    ],
)

from section_texts import SECTION_TEXTS
wonder_breakdown_sidebar_text = SECTION_TEXTS.get("wonder_breakdown", [])

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
    left_col = make_left_sidebar(
        kpi_card,
        reset_filters_button,
        filters_card,
        helper_text=wonder_breakdown_sidebar_text,
        last_updated_value=last_updated_value,
        xs=12,
        md=3,
    )

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
            id="wonder-breakdown-section",
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

    def filter_df(df):
        if "year" in df.columns:
            df = apply_filter(df, "year", year)

        if "county" in df.columns and county is not None:
            county_text = str(county).strip().lower()
            statewide_text = STATEWIDE_COUNTY.lower()
            statewide_rows = df[
                df["county"].astype(str).str.strip().str.lower() == statewide_text
            ]
            non_statewide_rows = df[
                df["county"].astype(str).str.strip().str.lower() != statewide_text
            ]

            if county_text == statewide_text:
                # Statewide: prefer aggregating real county rows so years that
                # lack a literal "Statewide" row still show data.
                df = non_statewide_rows if not non_statewide_rows.empty else statewide_rows
            else:
                # Specific county: use that county's rows; fall back to the
                # Statewide rows when the source only provides statewide-level
                # data for this year (e.g. gender/race in 2023).
                county_rows = apply_filter(non_statewide_rows, "county", county)
                df = county_rows if not county_rows.empty else statewide_rows

        return df

    # KPI: use age_group (has county-level data for all years including 2023).
    # For the KPI we never fall back to Statewide when a specific county is
    # selected — that would show the wrong total.
    def kpi_filter_df(df):
        if "year" in df.columns:
            df = apply_filter(df, "year", year)
        if "county" in df.columns and county is not None:
            county_text = str(county).strip().lower()
            statewide_text = STATEWIDE_COUNTY.lower()
            if county_text == statewide_text:
                non_statewide = df[
                    df["county"].astype(str).str.strip().str.lower() != statewide_text
                ]
                df = non_statewide if not non_statewide.empty else df[
                    df["county"].astype(str).str.strip().str.lower() == statewide_text
                ]
            else:
                df = apply_filter(df, "county", county)
        return df

    filter_total = kpi_filter_df(df_raw_age_group.copy())["deaths"].sum()

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
        by_sub["display_count"] = by_sub["deaths"].apply(format_count_display)

        sub_bar = px.bar(
            by_sub,
            x="deaths",
            y="substance",
            barmode="stack",
            text="display_count",
            labels={"deaths": "Number of Deaths", "substance": "Substance"},
        )

        sub_bar.update_traces(
            marker_color="#22767C",
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}: %{text}<extra></extra>",
        )

        max_deaths = by_sub["deaths"].max() if not by_sub.empty else 0
        x_max = max(10, int(max_deaths * 1.15))

        apply_standard_bar_layout(
            sub_bar,
            margin=dict(l=140, r=50),
            xaxis=dict(range=[0, x_max]),
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
        by_race["display_count"] = by_race["deaths"].apply(format_count_display)

        race_bar = px.bar(
            by_race,
            x="deaths",
            y="race",
            barmode="stack",
            text="display_count",
            labels={"deaths": "Number of Deaths", "race": "Race"},
        )

        race_bar.update_traces(
            marker_color="#22767C",
            textposition="outside",
            hovertemplate="%{y}: %{text}<extra></extra>",
        )

        apply_standard_bar_layout(race_bar, yaxis=dict(autorange="reversed"))

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
        by_age_group["display_count"] = by_age_group["deaths"].apply(format_count_display)

        age_group_bar = px.bar(
            by_age_group,
            x="deaths",
            y="age_group",
            barmode="stack",
            text="display_count",
            labels={"deaths": "Number of Deaths", "age_group": "Age Group"},
        )

        age_group_bar.update_traces(
            marker_color="#22767C",
            textposition="outside",
            hovertemplate="%{y}: %{text}<extra></extra>",
        )

        apply_standard_bar_layout(age_group_bar, yaxis=dict(autorange="reversed"))

    else:
        age_group_bar = px.bar()

    # ---------- Pie chart: Deaths by Gender ----------
    if "gender" in dff_gender.columns:
        by_gender = (
            dff_gender.groupby("gender", as_index=False)["deaths"]
            .sum()
            .sort_values("gender")
        )
        by_gender["display_count"] = by_gender["deaths"].apply(format_count_display)
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
        format_count_display(filter_total),
        sub_bar,
        race_bar,
        age_group_bar,
        gender_pie,
    )
