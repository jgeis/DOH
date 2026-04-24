from db_utils import execute_query
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
import plotly.express as px
from theme import register_template
from dashboard_utils import make_kpi_card
import json
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

def load_sudors_dataframe_from_db():
    """
    This helper:
      1. Loads the main SQL query by name.
      2. Connects to the database and runs the query.
      3. Cleans up some columns so the rest of the app is easier to write.

    Why: having this in one place avoids repeating the same database
    logic in multiple callbacks.
    
    Note: Uses either SQLite or MSSQL automatically based on config.
    """
    
    sql = load_sql_query("load_sudors_data_view_diag_su$")
    
    # Execute query using db_utils (automatically uses correct database)
    df = execute_query(sql)
    print(f"load_sudors_data_view_diag_su$ returned {len(df):,} rows")

    # If there is no data, we stop early instead of showing a broken page
    if df.empty:
        raise RuntimeError("Query returned 0 rows.")

    # Make the year column numeric when possible so graphs treat it as numbers
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")

    # For these columns, replace missing values with "Unknown"
    # so we don't get blank labels in filters and tables.
    for col in ["substance", "homeless", "sex", "age_cat", "race_ethnicity", "year"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")
    return df

# Load the full dataset once at startup.
# The callbacks will reuse this instead of hitting the database every time.
df_raw = load_sudors_dataframe_from_db()

# Count how many unique records we have to show on the KPI card.
total_unique = df_raw["incident_id"].nunique()

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
substance_opts  = sort_opts(df_raw["substance"])                     if "substance"  in df_raw.columns else []
homeless_opts   = sort_opts(df_raw["homeless"])                      if "homeless"   in df_raw.columns else []
sex_opts        = sort_opts(df_raw["sex"])                           if "sex"        in df_raw.columns else []
age_opts        = sort_opts(df_raw["age_cat"])                       if "age_cat"    in df_raw.columns else []
race_opts       = sort_opts(df_raw["race_ethnicity"])                if "race_ethnicity"       in df_raw.columns else []
year_opts       = sorted(df_raw["year"].dropna().unique().tolist())  if "year"       in df_raw.columns else []

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
    href="#sudors-filters",
    className="visually-hidden-focusable",
    tabIndex=0
)

# Big green card that shows the total number of discharges.
# Why: gives users a quick "at a glance" number when they open the page.
kpi_card = make_kpi_card(
    label="Number of Unintentional or Undetermined Overdose Deaths",
    count_id="kpi-total-deaths",
)

reset_filters_button = dbc.Button(
    "Reset All Filters",
    id="sudors-reset-filters-btn",
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

        html.Label("Substance", htmlFor="sudors-substance-filter", tabIndex=2, className="form-label"),
        dcc.Dropdown(
            id="sudors-substance-filter", options=opts_list(substance_opts), multi=True,
            placeholder="Substance", className="mb-2",
            persistence=True, persistence_type="session"
        ),
        html.Label("Homeless", htmlFor="sudors-homeless-filter", tabIndex=2, className="form-label"),
        dcc.Dropdown(
            id="sudors-homeless-filter", options=opts_list(homeless_opts), multi=True,
            placeholder="Homeless", className="mb-2",
            persistence=True, persistence_type="session"
        ),
        html.Label("Race/Ethnicity", htmlFor="sudors-race-filter", tabIndex=5, className="form-label"),
        dcc.Dropdown(
            id="sudors-race-filter", options=opts_list(race_opts), multi=True,
            placeholder="Race/Ethnicity", className="mb-2",
            persistence=True, persistence_type="session"
        ),
        html.Label("Sex", htmlFor="sudors-sex-filter", tabIndex=6, className="form-label"),
        dcc.Dropdown(
            id="sudors-sex-filter", options=opts_list(sex_opts), multi=True,
            placeholder="Sex", className="mb-0",
            persistence=True, persistence_type="session"
        ),
        html.Label("Age Group", htmlFor="sudors-age-filter", tabIndex=5, className="form-label"),
        dcc.Dropdown(
            id="sudors-age-filter", options=opts_list(age_opts), multi=True,
            placeholder="Age Group", className="mb-2",
            persistence=True, persistence_type="session"
        ),
        html.Label("Calendar Year", htmlFor="sudors-year-filter", tabIndex=3, className="form-label"),
        dcc.Dropdown(
            id="sudors-year-filter", options=opts_list(year_opts), multi=True,
            placeholder="Calendar Year", className="mb-2",
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
    id="sudors-filters",
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
                graph_block("bar-deaths", "Deaths by Substance", bar_h),
                html.P("Bar chart showing deaths by substance.", className="visually-hidden"),
            ]),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            graph_block("sex-sudors-pie", "Deaths by Gender", pie_h),
                            html.P("Pie chart showing deaths by gender.", className="visually-hidden"),
                        ],
                        xs=12,
                        md=6,
                    ),
                    dbc.Col(
                        [
                            graph_block("homeless-sudors-pie", "Homeless Deaths", pie_h),
                            html.P("Pie chart showing deaths by homeless status.", className="visually-hidden"),
                        ],
                        xs=12,
                        md=6,
                    ),
                ],
                className="g-2",
            ),
            dbc.Row([
                graph_block("substance-year-line", "Deaths by Substance Over Time", bar_h),
                html.P("Line chart showing deaths by substance over time.", className="visually-hidden"),
            ]),
        ],
        xs=12, md=6
    )

    # Right column:
    # summary tables (by county and by age group)
    #
    # On phones, the two small tables sit side-by-side.
    # On bigger screens, they stack vertically.
    right_col = dbc.Col(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H6("By Race/Ethnicity", className="mb-2"),
                            html.Div(
                                id="table-race",
                                className="mobile-side-table",
                                style={"overflowX": "auto"}
                            ),
                        ],
                        xs=6, md=12, className="pe-1 mb-3",
                    ),
                    dbc.Col(
                        [
                            html.H6("Calendar Year", className="mb-2"),
                            html.Div(
                                id="table-calendar",
                                className="mobile-side-table",
                                style={"overflowX": "auto"}
                            ),
                        ],
                        xs=6, md=12, className="ps-1 mb-3",
                    ),
                    dbc.Col(
                        [
                            html.H6("By Age", className="mb-2"),
                            html.Div(
                                id="table-sudors-age",
                                className="mobile-side-table",
                                style={"overflowX": "auto"}
                            ),
                        ],
                        xs=6, md=12, className="ps-1 mb-3",
                    ),
                ],
                className="g-2"
            ),

        ],
        xs=12, md=3
    )


    # Wrap everything in a fluid container so it stretches with the screen.
    return dbc.Container([
        skip_link,
        html.Div(
            dbc.Row([left_col, center_col, right_col], className="g-3"),
            id="sudors-section",
            style={} if show_deaths else {"display": "none"}
        ),

        html.Hr(
            className="my-5",
            style={} if (show_deaths) else {"display": "none"}
        ),

        html.P(
            "This section highlights the number of unintentional and undetermined drug overdose deaths in Hawaii broken down by substances that caused death (not mutually exclusive), age, race/ethnicity, sex at birth, and housing status. Specific substances tracked include: Fentanyl, Methamphetamine, Heroin, Prescription Opioids, Cocaine, and Benzodiazepines. Data is sourced from the State Unintentional Drug Overdose Reporting System (SUDORS) which collects information from death certificates, medical examiner or coroner reports, and postmortem toxicology reports to provide comprehensive information on the circumstances surrounding overdose deaths.",
            className="small text-muted mt-2 mb-3",
        ),

    ], fluid=True, className="p-2")


# This is the default layout used when the app imports this file.
# We pass False here since desktop is the standard case.
layout = layout_for(is_mobile=False)

# ----------------------------
# Figures + tables (no plotly titles)
# ----------------------------

@callback(
    Output("sudors-substance-filter", "value"),
    Output("sudors-homeless-filter", "value"),
    Output("sudors-race-filter", "value"),
    Output("sudors-sex-filter", "value"),
    Output("sudors-age-filter", "value"),
    Output("sudors-year-filter", "value"),
    Input("sudors-reset-filters-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_all_filters(_n_clicks):
    # Reset all multi-select dropdowns to their default empty state.
    return None, None, None, None, None, None

@callback(
    Output("kpi-total-deaths", "children"),
    Output("bar-deaths", "figure"),
    Output("table-race", "children"),
    Output("table-calendar", "children"),
    Output("table-sudors-age", "children"),
    Output("sex-sudors-pie", "figure"),
    Output("homeless-sudors-pie", "figure"),
    Output("substance-year-line", "figure"),
    Input("sudors-substance-filter", "value"),
    Input("sudors-homeless-filter", "value"),
    Input("sudors-sex-filter", "value"),
    Input("sudors-age-filter", "value"),
    Input("sudors-race-filter", "value"),
    Input("sudors-year-filter", "value"),
)

def update_dashboard(substance, homeless, sex, age, race, year):
    """
    This function runs every time the user changes a filter.

    It:
      - Applies all the filters to the data,
      - Builds two graphs (line + stacked bar),
      - Builds two tables,
      - Builds the pie chart.
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
    if "substance" in dff.columns:      dff = apply_filter(dff, "substance", substance)
    if "homeless" in dff.columns:       dff = apply_filter(dff, "homeless", homeless)
    if "sex" in dff.columns:            dff = apply_filter(dff, "sex", sex)
    if "age" in dff.columns:            dff = apply_filter(dff, "age", age)
    if "race_ethnicity" in dff.columns: dff = apply_filter(dff, "race_ethnicity", race)
    if "year" in dff.columns:           dff = apply_filter(dff, "year", year)

    # Count unique discharges (each record_id represents one discharge).
    # Used to update the total on the KPI card when user selects the filter
    filter_total = dff["incident_id"].nunique()

    # ---------- Bar chart: Deaths by Substance ----------
    if {"substance"}.issubset(dff.columns):
        by_sub = (
            dff.groupby("substance")["incident_id"].nunique()
            .reset_index(name="count")
            .sort_values("count", ascending=True)
        )

        # Show all rows, but suppress low-count bars by plotting zero width.
        by_sub["plot_count"] = by_sub["count"].apply(lambda x: 0 if x < 10 else x)

        def ellipsize(text, max_len=25):
            if text is None:
                return text
            return text if len(text) <= max_len else text[:max_len] + "..."

        # Cuts off label length after 25 characters
        by_sub["substance_label"] = by_sub["substance"].apply(ellipsize)

        by_sub["display_count"] = by_sub["count"].apply(
            lambda x: "<10*" if x < 10 else f"{int(x):,}"
        )

        sud_bar = px.bar(
            by_sub,
            x="plot_count",
            y="substance_label",
            barmode="stack",
            text="display_count",
            labels={"plot_count": "Number of Deaths", "substance_label": "Cause of Death<br>(Not Mutually Exclusive)"},
        )

        sud_bar.update_traces(
            textposition="outside",
            cliponaxis=False,
            hovertemplate="Cause of Death: %{customdata}<br>Number of Deaths: %{text}<extra></extra>",
            customdata=by_sub["substance"],
        )

        sud_bar.update_layout(
            margin=dict(l=0, r=0, t=10, b=80),
            xaxis=dict(automargin=True, rangemode="tozero"),
        )

    else:
        sud_bar = px.bar()


    # ---------- Helper for the summary tables ----------
    def tbl(column, categories=None):
        """
        Build a small table that shows the count of unique discharges
        for each value in the chosen column.

        If we pass in a list of categories, we use that order in the table.
        """
        if column not in dff.columns:
            return dbc.Alert(
                f"Column '{column}' not found.",
                color="warning",
                className="mb-0"
            )

        # Count unique discharges per category
        g = dff.groupby(column)["incident_id"].nunique().reset_index(name="count")

        # Use the given category order if provided
        if categories:
            g[column] = pd.Categorical(g[column], categories=categories, ordered=True)
            g = g.sort_values(column)
        elif column == "race_ethnicity":
            g = g.sort_values("count", ascending=False)
        elif column == "homeless":
            g = g.sort_values("count", ascending=False)

        # Make the counts look nicer with commas
        g["count"] = g["count"].map(lambda x: "<10*" if x < 10 else f"{int(x):,}")

        # Use friendly display labels for table headers
        header_labels = {
            "race_ethnicity": "Race",
            "homeless": "Homeless",
            "year": "Year",
            "age_cat": "Age",
        }
        display_column = header_labels.get(column, column)
        g = g.rename(columns={column: display_column, "count": "Deaths"})

        # Build a styled table for the dashboard
        return dbc.Table.from_dataframe(g, striped=True, bordered=True, hover=True)

    # pin "under 15" at the top and "unknown" at the bottom, with the rest in numeric order in between
    def age_sort_key(label):
        text = str(label).strip()
        lower = text.lower()

        if lower == "under 15":
            return (0, -1, text)
        if lower == "unknown":
            return (2, float("inf"), text)

        match = re.search(r"\d+", text)
        if match:
            return (1, int(match.group()), text)

        return (1, float("inf"), text)

    age_table_order = []
    if "age_cat" in dff.columns:
        age_table_order = sorted(
            [v for v in dff["age_cat"].dropna().astype(str).unique()],
            key=age_sort_key,
        )


    # ---------- Pie chart: Deaths by Gender ----------
    if "sex" in dff.columns:
        pie_df = (
            dff.groupby("sex")["incident_id"].nunique()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )
        pie_df["display_count"] = pie_df["count"].apply(
            lambda x: "<10*" if x < 10 else f"{int(x):,}"
        )
        sex_pie = px.pie(
            pie_df,
            names="sex",
            values="count",
            hole=0.35,
            custom_data=["display_count"],
        )
        sex_pie.update_traces(
            textposition="inside",
            texttemplate="%{label}<br>%{percent:.1%} (%{customdata[0]})",
            hovertemplate="%{label}: %{customdata[0]} (%{percent:.1%})<extra></extra>"
        )
        sex_pie.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    else:
        sex_pie = px.pie()

    # ---------- Pie chart: Deaths by Homeless Status ----------
    if "homeless" in dff.columns:
        homeless_pie_df = (
            dff.groupby("homeless")["incident_id"].nunique()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )
        homeless_pie_df["display_count"] = homeless_pie_df["count"].apply(
            lambda x: "<10*" if x < 10 else f"{int(x):,}"
        )
        homeless_pie = px.pie(
            homeless_pie_df,
            names="homeless",
            values="count",
            hole=0.35,
            custom_data=["display_count"],
        )
        homeless_pie.update_traces(
            textposition="inside",
            texttemplate="%{label}<br>%{percent:.1%} (%{customdata[0]})",
            hovertemplate="%{label}: %{customdata[0]} (%{percent:.1%})<extra></extra>"
        )
        homeless_pie.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    else:
        homeless_pie = px.pie()

    # ---------- Line chart: Deaths by Substance Over Time ----------
    if {"year", "substance"}.issubset(dff.columns):
        by_year_substance = (
            dff.groupby(["year", "substance"])["incident_id"].nunique()
            .reset_index(name="count")
            .sort_values(["year", "substance"])
        )

        line_fig = px.line(
            by_year_substance,
            x="year",
            y="count",
            color="substance",
            markers=True,
            labels={"year": "Year", "count": "Number of Deaths", "substance": "Substance"},
        )
        line_fig.update_traces(
            hovertemplate="Year %{x}<br>Substance: %{fullData.name}<br>Deaths: %{y:,}<extra></extra>"
        )
        line_fig.update_layout(
            margin=dict(l=10, r=10, t=80, b=70),
            xaxis=dict(dtick=1, automargin=True, title_standoff=12),
            yaxis=dict(rangemode="tozero"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
                font=dict(size=10),
            ),
        )
    else:
        line_fig = px.line()


    # Return all the updated visuals and tables to Dash
    return (
        f"{filter_total:,}",
        sud_bar,
        tbl("race_ethnicity"),
        tbl("year"),
        tbl("age_cat", age_table_order),
        sex_pie,
        homeless_pie,
        line_fig,
    )
