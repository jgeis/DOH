# polysubstance_dashboard_db.py — pure layout + callbacks (desktop-safe, mobile-aware)

# - db_utils: to connect to database (SQLite or MSSQL based on config)
# - pandas / numpy: to clean and shape the data
# - dash + dash_bootstrap_components: to build the web page and styles
# - plotly: to draw the charts
from pathlib import Path

import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio


from theme import register_template
from db_utils import execute_query
from dashboard_utils import (
    make_kpi_card,
    make_left_sidebar,
    compute_last_updated_value,
    make_filters_card,
    dropdown_filter,
    sort_opts,
    statewide_first,
    apply_county_filter,
    county_output_should_include_statewide,
    append_statewide_aggregate_rows,
    format_count_display,
    format_display_list,
    apply_standard_bar_layout,
    apply_standard_line_layout,
    apply_standard_non_axis_layout,
    apply_standard_heatmap_layout,
    apply_standard_network_layout,
    apply_standard_sankey_layout,
)

# This applies our custom Plotly look (colors, fonts, etc.) everywhere in this app.
register_template()  # set your Plotly template globally

# Simple shortcuts so we can change these in one place if paths ever move
QUERIES_PATH = "queries.sql"
PREFERRED_QUERY = "load_polysubstance_data"
FALLBACK_QUERY  = "load_discharge_data_view_diag_su"


# ---------- SQL loader ----------
def load_sql_query(name: str, path: str = QUERIES_PATH) -> str:
    """
    Look inside queries.sql and pull out the SQL text that matches `name`.

    Why:
    - Keeps long SQL out of this Python file.
    - Makes it easier to update queries without touching code.
    """
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # queries.sql is broken up into blocks that start with "-- name:"
    blocks = text.split("-- name:")
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        lines = b.split("\n")
        block_name = lines[0].strip()
        sql = "\n".join(lines[1:]).strip()
        if block_name == name:
            return sql

    # If we get here, we didn't find a block with that name
    raise KeyError(f"Named query '{name}' not found in {path}.")


# ---------- DB → DataFrame ----------
def load_df():
    """
    Load the main dataset from the SQLite database.

    Steps:
      1. Try to use the polysubstance-only query.
      2. If it doesn't exist, fall back to the main data query.
      3. Read the result into a table (DataFrame).
      4. Clean up some columns so they behave nicely in filters and charts.
    """
    try:
        # First choice: use the specific polysubstance query
        sql = load_sql_query(PREFERRED_QUERY, QUERIES_PATH)
        print(f"[load_df] Using query: {PREFERRED_QUERY}")
    except KeyError:
        # If that fails, fall back to the more general query
        sql = load_sql_query(FALLBACK_QUERY, QUERIES_PATH)
        print(f"[load_df] Using query: {FALLBACK_QUERY}")

    # Execute query using db_utils (automatically uses correct database)
    df = execute_query(sql)

    # If nothing comes back, it’s better to crash early than show an empty dashboard.
    if df.empty:
        raise RuntimeError("Query returned 0 rows. Check DB and queries.sql.")

    # These columns are treated as category-like text fields.
    # Here we clean them up to avoid weird blanks or "nan" strings.
    want_obj = ["county", "city", "hawaii_residency", "age_group", "sex", "substance"]
    for c in want_obj:
        if c in df.columns:
            df[c] = (
                df[c].astype(str).str.strip()
                .replace({"nan": np.nan, "None": np.nan})
                .fillna("Unknown")
            )

    # Make sure the year column is a proper integer type so graphs order it correctly.
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

    # Print some quick info in the console for debugging.
    print(f"[load_df] rows={len(df):,}  cols={list(df.columns)}")
    print("Plotly default template:", pio.templates.default)
    return df




# ---------- Helper functions ----------
def build_cooccurrence_matrix(df):
    """
    Build a co-occurrence matrix showing how often substances appear together.
    
    Returns a DataFrame where rows and columns are substances, and values are
    the count of records where both substances appear together.
    """
    # Create a pivot table: rows=record_id, columns=substance, values=1 if present
    substance_matrix = df.pivot_table(
        index='record_id',
        columns='substance',
        aggfunc='size',
        fill_value=0
    ).clip(upper=1)  # Convert to binary (0 or 1)
    
    # Calculate co-occurrence: matrix multiplication
    cooccurrence = substance_matrix.T.dot(substance_matrix)
    
    return cooccurrence


def build_correlation_matrix(df):
    """
    Build a correlation matrix showing the correlation between substance occurrences.
    """
    substance_matrix = df.pivot_table(
        index='record_id',
        columns='substance',
        aggfunc='size',
        fill_value=0
    ).clip(upper=1)
    
    return substance_matrix.corr()


def build_cooccurrence_data(df, age=None, sex=None, county=None, year=None):
    """
    Build data for grouped bar chart showing co-occurrence percentages.

    For each substance, calculate what % of records also have other substances.
    """
    # Apply filters to match sunburst logic
    if "age_group" in df.columns:
        df = _apply_filter(df, "age_group", age)
    if "sex" in df.columns:
        df = _apply_filter(df, "sex", sex)
    if "county" in df.columns:
        df = apply_county_filter(df, county).copy()
    if "year" in df.columns:
        df = _apply_filter(df, "year", year)

    results = []

    for primary_substance in df['substance'].unique():
        # Get all records where the substance is present (not just primary)
        records = df[df['substance'] == primary_substance]['record_id'].unique()
        total = len(records)

        if total == 0:
            continue

        # For each other substance, count how many of these records also have it
        for other_substance in df['substance'].unique():
            if other_substance != primary_substance:
                count = df[
                    (df['record_id'].isin(records)) & 
                    (df['substance'] == other_substance)
                ]['record_id'].nunique()

                results.append({
                    'Primary': primary_substance,
                    'Also Found': other_substance,
                    'Percentage': (count / total) * 100,
                    'Count': count,
                    'Total': total
                })

    return pd.DataFrame(results)


def build_sunburst_cooccurrence_data(df):
    """Build Primary -> Also Found rows for sunburst co-occurrence visualization with record_id for aggregation."""
    results = []

    grouped = df.groupby("record_id")["substance"].unique()
    for record_id, substances in grouped.items():
        for i in range(len(substances)):
            for j in range(len(substances)):
                if i != j:
                    results.append({
                        "record_id": record_id,
                        "Primary": substances[i],
                        "Also Found": substances[j],
                    })

    return pd.DataFrame(results)




# Load the cleaned dataset once when the module is imported.
# All callbacks reuse this instead of hitting the DB over and over.
df_raw = load_df()
print("[debug] queries.sql path:", Path(QUERIES_PATH).resolve())

# Guard rails: limit years to our window and drop "unknown" ages
if "year" in df_raw.columns:
    # Make sure year is numeric
    df_raw["year"] = pd.to_numeric(df_raw["year"], errors="coerce").astype("Int64")
    valid_years = df_raw["year"].dropna()
    if not valid_years.empty:
        min_year = int(valid_years.min())
        max_year = int(valid_years.max())
        print(f"[polysubstance_dashboard] year range in data: {min_year}-{max_year}")
    mask_year = df_raw["year"].notna()
else:
    mask_year = True  # If we don't have a year, don't filter by year

def _is_unknown_age(val):
    """
    Decide if an age group value is basically "unknown".

    We treat blanks or common shortcuts (unknown, unk, n/a, etc.) as unknown.
    """
    s = (str(val) if val is not None else "").strip().lower()
    return s in {"", "unknown", "unk", "n/a", "na"}

# Remove rows with unknown age groups (only if that column exists)
mask_age = ~df_raw["age_group"].apply(_is_unknown_age) if "age_group" in df_raw.columns else True

# Keep only rows that pass both filters
df_raw = df_raw[mask_year & mask_age].copy()
last_updated_value = compute_last_updated_value(df_raw)


# ---------- filter options ----------
def opts(values):
    """
    Wrap a raw list of values into the format Dash expects for dropdown options:
    each one needs a label and value.
    """
    return [{"label": v, "value": v} for v in values]

# Build the dropdown choices for each filter, only if those columns exist.
substance_opts = sort_opts(df_raw["substance"]) if "substance" in df_raw.columns else []
county_opts    = sort_opts(df_raw["county"]) if "county" in df_raw.columns else []
age_opts       = sort_opts(df_raw["age_group"]) if "age_group" in df_raw.columns else []
sex_opts       = sort_opts(df_raw["sex"])       if "sex"       in df_raw.columns else []
year_opts      = sorted(df_raw["year"].dropna().unique().tolist()) if "year" in df_raw.columns else []

# Total number of unique records, used for the big KPI card.
kpi_total = df_raw["record_id"].nunique() if "record_id" in df_raw.columns else 0

from section_texts import SECTION_TEXTS
polysubstance_sidebar_text = SECTION_TEXTS.get("discharges_su_polysubstance", [])

# Filter display order is managed centrally in dashboard_utils.make_filters_card.
filters_card = make_filters_card(
    card_id="polysubstance-filters",
    title="Filter Data",
    filters=[
        dropdown_filter("Substance Type", "polysubstance-substance-filter", options=opts(substance_opts), multi=True, placeholder="All"),
        dropdown_filter("Age Group", "polysubstance-age-filter", options=opts(age_opts), multi=True, placeholder="All"),
        dropdown_filter("Sex", "polysubstance-sex-filter", options=opts(sex_opts), multi=True, placeholder="All"),
        dropdown_filter("County", "polysubstance-county-filter", options=opts(county_opts), multi=True, placeholder="All"),
        dropdown_filter("Calendar Year", "polysubstance-year-filter", options=opts(year_opts), multi=True, placeholder="All"),
    ],
)


# ---------- small helpers ----------
def _apply_filter(frame: pd.DataFrame, col: str, val) -> pd.DataFrame:
    """
    Helper to apply a filter to a column.

    - If val is empty or None, we leave the data alone.
    - If val is a list, we keep any rows that match any of those values.
    - If val is a single value, we match exactly that.

    Why: we use the same pattern for all filters, so this keeps the code
    short and consistent.
    """
    if val is None or (isinstance(val, (list, tuple)) and len(val) == 0):
        return frame.copy()
    if isinstance(val, (list, tuple)):
        return frame[frame[col].isin(val)].copy()
    return frame[frame[col] == val].copy()


def _wrap_label(label: str, max_len: int = 22):
    """
    Break long labels into two lines so they don't stretch the chart.

    We look for the last space before `max_len` and insert a line break there.
    """
    s = str(label)
    if len(s) <= max_len:
        return s
    cut = s.rfind(" ", 0, max_len)
    if cut == -1:
        return s
    return s[:cut] + "<br>" + s[cut+1:]


def _records_matching_all_selected_substances(frame: pd.DataFrame, selected_values) -> pd.DataFrame:
    """
    Return rows from records that contain ALL selected substances.

    This applies record-level AND logic:
    - No selections => return input frame unchanged.
    - One selection => records containing that substance.
    - Multiple selections => records containing every selected substance.
    """
    if not selected_values:
        return frame.copy()

    if not {"record_id", "substance"}.issubset(frame.columns):
        return frame.iloc[0:0].copy()

    selected = [str(v).strip() for v in selected_values if str(v).strip()]
    if not selected:
        return frame.copy()

    selected_set = set(selected)
    hits = (
        frame[frame["substance"].astype(str).isin(selected_set)][["record_id", "substance"]]
        .drop_duplicates()
    )
    required_count = len(selected_set)
    record_match_counts = hits.groupby("record_id")["substance"].nunique()
    matched_ids = record_match_counts[record_match_counts == required_count].index
    return frame[frame["record_id"].isin(matched_ids)].copy()


def graph_block(base_id: str, title_text: str, height: str):
    """
    Build a reusable chart "card" with a title and graph.

    Why: this keeps plot sections consistent across the page and helps
    avoid repeating the same layout code every time we add a graph.
    """
    return html.Div(
        [
            html.H5(title_text, id=f"{base_id}-title", className="mb-2"),

            # The graph itself; Plotly tools bar (modebar) is always ON.
            dcc.Graph(
                id=base_id,
                style={"height": height, "width": "100%"},
                config={"displayModeBar": True, "displaylogo": False},
            ),
        ],
        className="mb-4",
        # Let the tools bar hang outside the card if needed so it’s not cut off.
        style={"overflow": "visible"},
    )


# ---------- layout factory (mobile-aware) ----------
def layout_for(is_mobile: bool = False):
    """
    Build the full page layout.

    We accept a flag `is_mobile` so we can adjust chart heights
    for smaller screens.

    The page is split into three columns:
      LEFT:  KPI + filters
      CENTER: main bar/stacked charts
      RIGHT: treemap + small summary tables
    """
    # Make charts taller on phones so they are easier to read.
    h_bar = "60vh" if is_mobile else "400px"
    h_stack = "55vh" if is_mobile else "360px"
    h_full_row = "55vh" if is_mobile else "420px"
    h_tree = "46vh" if is_mobile else "280px"

    # LEFT: KPI + filters
    left = make_left_sidebar(
        make_kpi_card(
            label="Number of Discharges Related to Polysubstance Use",
            count_id="polysubstance-kpi-total",
        ),
        dbc.Button(
            "Reset All Filters", id="polysubstance-reset-filters-btn",
            color="secondary",
            outline=True,
            className="w-100 mb-3",
            n_clicks=0,
        ),
        filters_card,
        helper_text=polysubstance_sidebar_text,
        last_updated_value=last_updated_value,
        xs=12,
        md=3,
    )

    # CENTER: main charts focused on substance over time
    center = dbc.Col([
        graph_block("bar-top-substances", "Substance Type", h_bar),
        # Hidden description for screen readers.
        html.P("Horizontal bar chart showing the top substances among polysubstance records.", className="visually-hidden"),

        graph_block("line-year-substance", "Yearly Discharges by Polysubstance", h_stack),
        html.P("Line chart showing yearly discharges by substance.", className="visually-hidden"),
    ], xs=12, md=6)

    # RIGHT: county share chart + two small summary tables (no headers per site-wide standard)
    right = dbc.Col([
        html.Div(id="tbl-county-share", className="sidebar-table mb-4"),

        html.Div(id="tbl-year", className="sidebar-table mb-4"),

        # Two summary tables (Age + Sex at Birth) — NO HEADERS
        dbc.Row([
            dbc.Col([
                html.Div(id="tbl-age", className="sidebar-table"),
            ], xs=12, md=12),
            dbc.Col([
                html.Div(id="tbl-sex", className="sidebar-table"),
            ], xs=12, md=12),
        ], className="g-3"),
    ], xs=12, md=3)

    # Wrap everything up in one fluid container.
    return dbc.Container([
        # Accessibility: a "skip" link so keyboard users can jump right to filters.
        html.A(
            "Skip to filters", href="#polysubstance-filters",
            className="visually-hidden-focusable", tabIndex=0
        ),

        # Store mobile state for callbacks
        dcc.Store(id="polysubstance-cooccurrence-is-mobile", data=is_mobile),

        dbc.Row([left, center, right], className="g-3"),

        # Full-width row under filters/blurbs: county trend (left) + sunburst co-occurrence (right)
        dbc.Row([
            dbc.Col([
                graph_block("stack-year-county", "Yearly Discharges by County", h_full_row),
                html.P("Line chart showing discharges by year and county.", className="visually-hidden"),
            ], xs=12, md=6),
            dbc.Col([
                graph_block("sunburst-cooccurrence", "Substance Co-occurrence Sunburst", h_full_row),
                html.P("Sunburst chart showing co-occurring substances in the selected cohort.", className="visually-hidden"),
            ], xs=12, md=6),
        ], className="g-3"),

        
        # Visualization 1: Heatmap
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Co-occurrence Heatmap", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.P([
                            "Heatmap showing how often substances appear together in the same polysubstance record. ",
                            "Darker cells indicate stronger co-occurrence.  When you select one or more substances to filter on, ",
                            "the heatmap updates to show how often each pair of substances co-occur among all records ", 
                            "that include all of your selected substance(s). This helps you see which other substances are ", 
                            "most likely to appear together with your selection.",
                            html.Br() if is_mobile else "",
                            html.Small("(Scroll horizontally to see full chart)", className="text-muted") if is_mobile else ""
                        ], className="text-muted mb-3"),
                        dcc.Loading(
                            html.Div(
                                dcc.Graph(
                                    id="polysubstance-cooccurrence-heatmap",
                                    config={"displayModeBar": True, "displaylogo": False},
                                    style={
                                        # Fixed height for both mobile and desktop
                                        "height": "600px",
                                        "minWidth": "1500px"
                                    }
                                ),
                                style={
                                    # handles horizontal scrolling on smaller screen sizes (mobile)
                                    "overflowX": "auto",
                                },
                                className="graph-inner" if is_mobile else ""
                            ),
                            className="heatmap-scroll" if is_mobile else ""
                        ),
                        html.P(
                            "Heatmap showing how often substances appear together in the same polysubstance record.",
                            className="visually-hidden",
                        )
                    ])
                ])
            ], md=12, className="mb-4")
        ]),
        
        # Visualization 2: Grouped Bar Chart
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Co-occurrence by Selected Substance", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.P([
                            "Grouped bar chart showing what percentage of cases with a given substance also contain each other substance. ",
                            "Use the Substance Type filter above to focus on one or more substances.",
                            html.Br() if is_mobile else "",
                            html.Small("(Scroll horizontally to see all substances)", className="text-muted") if is_mobile else ""
                        ], className="text-muted mb-3"),
                        html.Div(
                            id="polysubstance-cooccurrence-bar-caption",
                            className="plot-card-header text-center mb-2",
                            style={
                                "minHeight": "2.2rem",
                                "lineHeight": "1.25",
                                "overflow": "visible",
                                "whiteSpace": "normal",
                                "paddingTop": "0.25rem",
                                "paddingBottom": "0.25rem",
                            },
                        ),
                        dcc.Loading(
                            html.Div(
                                html.Div(
                                    dcc.Graph(
                                        id="polysubstance-cooccurrence-bar-chart",
                                        config={"displayModeBar": True, "displaylogo": False},
                                        style={"height": "650px" if is_mobile else "500px"}
                                    ),
                                    className="graph-inner" if is_mobile else ""
                                ),
                                className="hscroll-graph" if is_mobile else ""
                            )
                        ),
                        html.P(
                            "Grouped bar chart showing the percentage of cases where each substance co-occurs with other substances.",
                            className="visually-hidden",
                        )
                    ])
                ])
            ], md=12, className="mb-4")
        ]),
        
        # Visualization 3: Network Graph
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Substance Co-occurrence Network", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.P([
                            "Network graph showing substances as connected nodes. ",
                            "Thicker lines indicate more frequent co-occurrence. ",
                            "Only connections with 50 or more cases are shown."
                        ], className="text-muted mb-3"),
                        dcc.Loading(
                            dcc.Graph(
                                id="polysubstance-cooccurrence-network",
                                config={"displayModeBar": True, "displaylogo": False},
                                style={"minHeight": "650px"}
                            )
                        ),
                        html.P(
                            "Network graph showing substances as connected nodes, with thicker lines indicating more frequent co-occurrence.",
                            className="visually-hidden",
                        )
                    ])
                ])
            ], md=12, className="mb-4")
        ]),
        
        # Visualization 4: Sankey Diagram
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Substance Flow Diagram (Sankey)", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.P([
                            "Sankey diagram showing flows between the most frequent co-occurring substances in polysubstance cases. ",
                            "Flow width represents the number of co-occurrences. ",
                            "Only the top 8 substances by frequency are shown."
                        ], className="text-muted mb-3"),
                        dcc.Loading(
                            dcc.Graph(
                                id="polysubstance-cooccurrence-sankey",
                                config={"displayModeBar": True, "displaylogo": False},
                                style={"minHeight": "760px"}
                            )
                        ),
                        html.P(
                            "Sankey diagram showing flows between the most frequent co-occurring substances in polysubstance cases.",
                            className="visually-hidden",
                        )
                    ])
                ])
            ], md=12, className="mb-4")
        ]),

    ], fluid=True)




# Keep desktop default layout for older code that imports `layout` directly.
layout = layout_for(is_mobile=False)


# ---------- callbacks (figures + tables) ----------
@callback(
    Output("polysubstance-kpi-total", "children"),
    Output("bar-top-substances-title", "children"),
    Output("line-year-substance-title", "children"),
    Output("stack-year-county-title", "children"),
    Output("bar-top-substances", "figure"),
    Output("line-year-substance", "figure"),
    Output("stack-year-county", "figure"),
    Output("tbl-county-share", "children"),
    Output("tbl-year", "children"),
    Output("tbl-age", "children"),
    Output("tbl-sex", "children"),
    Input("polysubstance-substance-filter", "value"),
    Input("polysubstance-age-filter", "value"),
    Input("polysubstance-sex-filter", "value"),
    Input("polysubstance-county-filter", "value"),
    Input("polysubstance-year-filter", "value"),
)
def update(substance, age, sex, county, year):
    # Base frame for co-occurrence-aware charts: apply non-substance filters only.
    dff_base = df_raw.copy()
    if "age_group" in dff_base.columns:
        dff_base = _apply_filter(dff_base, "age_group", age)
    if "sex" in dff_base.columns:
        dff_base = _apply_filter(dff_base, "sex", sex)
    if "county" in dff_base.columns:
        dff_base = apply_county_filter(dff_base, county).copy()
    if "year" in dff_base.columns:
        dff_base = _apply_filter(dff_base, "year", year)

    # Main frame for existing visuals: includes substance filter.
    dff = dff_base.copy()
    if "substance" in dff.columns:
        dff = _apply_filter(dff, "substance", substance)

    include_statewide_on_line = county_output_should_include_statewide(county)

    # ---------- Bar: Top substances ----------
    selected_substances = (
        [v for v in substance if v]
        if isinstance(substance, (list, tuple, set))
        else ([substance] if substance else [])
    )

    # KPI uses the same record-level AND cohort logic used by co-occurrence visuals.
    kpi_source = dff_base
    if selected_substances and {"substance", "record_id"}.issubset(dff_base.columns):
        kpi_source = _records_matching_all_selected_substances(dff_base, selected_substances)
    kpi_value = (
        format_count_display(kpi_source["record_id"].nunique())
        if "record_id" in kpi_source.columns and not kpi_source.empty
        else "0"
    )

    if not selected_substances:
        bar_title = "Substance Type"
    elif len(selected_substances) == 1:
        bar_title = f"Substances found along with {selected_substances[0]}"
    else:
        bar_title = f"Substances found along with {format_display_list(selected_substances)}"

    # Dynamic top titles for line charts (replace in-figure titles).
    if not selected_substances:
        line_title = "Yearly Discharges by Polysubstance"
        county_title = "Yearly Discharges by County"
    elif len(selected_substances) == 1:
        line_title = f"Yearly Discharges by Polysubstance (found along with {selected_substances[0]})"
        county_title = f"Yearly Discharges by County (where {selected_substances[0]} is present)"
    else:
        selected_text = format_display_list(selected_substances)
        line_title = f"Yearly Discharges by Polysubstance (found along with {selected_text})"
        county_title = f"Yearly Discharges by County (where {selected_text} are present)"

    bar_source = dff
    if selected_substances and {"substance", "record_id"}.issubset(dff_base.columns):
        bar_source = _records_matching_all_selected_substances(dff_base, selected_substances)

    if {"substance", "record_id"}.issubset(bar_source.columns) and not bar_source.empty:
        sub_counts = (
            bar_source.groupby("substance")["record_id"]
            .nunique().reset_index(name="discharges")
            .sort_values("discharges", ascending=True)
        )

        # When filtering by substance, show only co-substances (exclude selected values).
        if selected_substances:
            selected_set = {str(v) for v in selected_substances}
            sub_counts = sub_counts[~sub_counts["substance"].astype(str).isin(selected_set)]

        # Keep current default behavior (top 10) only when no substance is selected.
        if not selected_substances:
            sub_counts = sub_counts.tail(10)

        if sub_counts.empty:
            fig_sub = px.bar()
            fig_sub.add_annotation(text="No co-substances found for selected filter.", showarrow=False)
            apply_standard_bar_layout(fig_sub)
        else:
            sub_counts["substance_wrapped"] = sub_counts["substance"].apply(_wrap_label)

            sub_counts["display_count"] = sub_counts["discharges"].apply(format_count_display)

            fig_sub = px.bar(
                sub_counts,
                x="discharges",
                y="substance_wrapped",
                orientation="h",
                labels={
                    "discharges": "Number of Discharges",
                    "substance_wrapped": "Substance Type",
                },
                text="display_count",
            )
            fig_sub.update_traces(
                marker_color="#22767C",
                textposition="auto",
                cliponaxis=True
            )
            apply_standard_bar_layout(
                fig_sub,
                xaxis=dict(rangemode="tozero"),
            )
    else:
        fig_sub = px.bar()


    # ---------- Line: Yearly Discharges by Substance ----------
    line_source = dff
    if selected_substances and {"substance", "record_id"}.issubset(dff_base.columns):
        line_source = _records_matching_all_selected_substances(dff_base, selected_substances)
        if not line_source.empty:
            selected_set = {str(v) for v in selected_substances}
            line_source = line_source[~line_source["substance"].astype(str).isin(selected_set)]

    if {"year", "substance", "record_id"}.issubset(line_source.columns) and not line_source.empty:
        top_substances = (
            line_source.groupby("substance")["record_id"]
               .nunique()
               .sort_values(ascending=False)
               .head(10)
               .index.tolist()
        )

        by_year_substance = (
            line_source[line_source["substance"].isin(top_substances)]
               .drop_duplicates(subset=["record_id", "year", "substance"])
               .groupby(["year", "substance"])["record_id"]
               .nunique()
               .reset_index(name="discharges")
               .sort_values(["year", "substance"])
        )
        by_year_substance["display_count"] = by_year_substance["discharges"].apply(format_count_display)

        substance_order = sort_opts(by_year_substance["substance"])
        by_year_substance["substance"] = pd.Categorical(
            by_year_substance["substance"],
            categories=substance_order,
            ordered=True,
        )

        fig_year_substance = px.line(
            by_year_substance,
            x="year",
            y="discharges",
            color="substance",
            markers=True,
            custom_data=["display_count"],
            category_orders={"substance": substance_order},
            labels={"year": "Year", "discharges": "Discharges", "substance": "Substance"}
        )
        fig_year_substance.update_traces(
            hovertemplate="Year %{x}<br>Substance: %{fullData.name}<br>Discharges: %{customdata[0]}<br>Only records containing all selected substances are included.<extra></extra>"
        )
        apply_standard_line_layout(
            fig_year_substance,
            xaxis=dict(dtick=1),
            yaxis=dict(rangemode="tozero"),
            title=None,
            legend=dict(
                title_text="Substance",
                orientation="h",
                yanchor="top",
                y=-0.2,
                xanchor="left",
                x=0,
            ),
        )
    else:
        fig_year_substance = px.line()

    demographic_source = dff
    if selected_substances and {"substance", "record_id"}.issubset(dff_base.columns):
        demographic_source = _records_matching_all_selected_substances(dff_base, selected_substances)

    # ---------- Line: Year × County ----------
    if {"year", "county", "record_id"}.issubset(demographic_source.columns) and not demographic_source.empty:
        yearly_counts = (
            demographic_source.drop_duplicates(subset=["record_id"])
               .groupby(["year", "county"])["record_id"]
               .nunique().reset_index(name="discharges")
        )

        if include_statewide_on_line:
            yearly_counts = append_statewide_aggregate_rows(
                yearly_counts,
                value_col="discharges",
                county_col="county",
            )

        county_order = statewide_first(sort_opts(yearly_counts["county"]))
        yearly_counts["county"] = pd.Categorical(
            yearly_counts["county"],
            categories=county_order,
            ordered=True,
        )
        yearly_counts = yearly_counts.sort_values(["year", "county"])
        yearly_counts["display_count"] = yearly_counts["discharges"].apply(format_count_display)

        fig_year_county = px.line(
            yearly_counts,
            x="year", y="discharges",
            color="county",
            markers=True,
            custom_data=["display_count"],
            category_orders={"county": county_order},
            labels={"year": "Year", "discharges": "Discharges"}
        )
        fig_year_county.update_traces(
            hovertemplate="Year %{x}<br>County: %{fullData.name}<br>Discharges: %{customdata[0]}<br>Only records containing all selected substances are included.<extra></extra>"
        )

        apply_standard_line_layout(
            fig_year_county,
            xaxis=dict(dtick=1),
            yaxis=dict(rangemode="tozero"),
            title=None,
        )
    else:
        fig_year_county = px.line()

    # ---------- Table: county share ----------
    uniq = demographic_source.drop_duplicates(subset=["record_id"])
    if {"county", "record_id"}.issubset(uniq.columns) and not uniq.empty:
        county_counts = uniq.groupby("county")["record_id"].nunique().reset_index(name="discharges")

        county_order = statewide_first(sort_opts(county_counts["county"]))
        county_counts["county"] = pd.Categorical(
            county_counts["county"],
            categories=county_order,
            ordered=True,
        )
        county_counts = county_counts.sort_values("county")
        county_counts["discharges"] = county_counts["discharges"].map(format_count_display)
        header_labels = {"county": "County", "discharges": "Discharges"}
        county_counts = county_counts.rename(columns=header_labels)
        # Manual table builder for compatibility
        tbl_county = dbc.Table([
            html.Thead(html.Tr([html.Th(col) for col in county_counts.columns])),
            html.Tbody([
                html.Tr([html.Td(val) for val in row]) for row in county_counts.values
            ])
        ], striped=True, bordered=True, hover=True, size="sm")
    else:
        tbl_county = dbc.Alert("No county data available.", color="warning", className="mb-0")

    # ---------- Small tables ----------
    def simple_table(df, col, ordered=None):
        if col not in df.columns or df.empty:
            return dbc.Alert(f"No data for '{col}'.", color="warning", className="mb-0")

        g = df.groupby(col)["record_id"].nunique().reset_index(name="discharges")

        if ordered:
            g[col] = pd.Categorical(g[col], categories=ordered, ordered=True)
            g = g.sort_values(col)

        g["discharges"] = g["discharges"].map(format_count_display)

        header_labels = {
            "year": "Year",
            "age_group": "Age Group",
            "sex": "Sex at Birth",
            "discharges": "Discharges",
        }
        g = g.rename(columns=header_labels)

        # Manual table builder for compatibility
        return dbc.Table([
            html.Thead(html.Tr([html.Th(col) for col in g.columns])),
            html.Tbody([
                html.Tr([html.Td(val) for val in row]) for row in g.values
            ])
        ], striped=True, bordered=True, hover=True, size="sm")

    # Extract year groups dynamically in descending order (newest first).
    year_groups = None
    if "year" in uniq.columns and not uniq.empty:
        year_vals = (
            uniq["year"]
            .dropna()
            .astype(str)
            .drop_duplicates()
            .tolist()
        )
        year_groups = sorted(
            year_vals,
            key=lambda v: int(v) if str(v).isdigit() else str(v),
            reverse=True,
        )
    age_groups = sort_opts(uniq["age_group"]) if "age_group" in uniq.columns and not uniq.empty else None

    year_source = uniq.copy()
    if "year" in year_source.columns and not year_source.empty:
        year_source["year"] = year_source["year"].astype(str)

    tbl_year = simple_table(year_source, "year", year_groups)
    tbl_age = simple_table(uniq, "age_group", age_groups)
    tbl_sex = simple_table(uniq, "sex")

    return kpi_value, bar_title, line_title, county_title, fig_sub, fig_year_substance, fig_year_county, tbl_county, tbl_year, tbl_age, tbl_sex



# ---------- Reset filters ----------
@callback(
    Output("polysubstance-substance-filter", "value"),
    Output("polysubstance-age-filter", "value"),
    Output("polysubstance-sex-filter", "value"),
    Output("polysubstance-county-filter", "value"),
    Output("polysubstance-year-filter", "value"),
    Input("polysubstance-reset-filters-btn", "n_clicks"),
    prevent_initial_call=True
)
def _reset_filters(n):
    """
    When the user clicks the Reset button, clear every filter.

    We return empty lists so Dash treats them as "no selection".
    """
    return [], [], [], [], []



# ---------- Callbacks ----------


@callback(
    Output("polysubstance-cooccurrence-heatmap", "figure"),
    Input("polysubstance-substance-filter", "value"),
    Input("polysubstance-cooccurrence-is-mobile", "data"),
)
def update_heatmap(selected_substances, is_mobile):
    """Create a heatmap showing correlation between substances, filtered by selected substance(s)."""
    if df_raw.empty or 'substance' not in df_raw.columns:
        return go.Figure().add_annotation(text="No data available", showarrow=False)

    # Filter the dataframe by selected substances if any are selected
    dff = df_raw.copy()
    selected_values = (
        [v for v in selected_substances if v]
        if isinstance(selected_substances, (list, tuple, set))
        else ([selected_substances] if selected_substances else [])
    )
    if selected_values:
        # Keep records that contain all selected substances.
        dff = _records_matching_all_selected_substances(dff, selected_values)
        if dff.empty:
            return go.Figure().add_annotation(text="No data for selected substance(s)", showarrow=False)

    # Build correlation matrix on filtered data
    corr_matrix = build_correlation_matrix(dff)
    if corr_matrix.empty:
        return go.Figure().add_annotation(text="No co-occurrence data available", showarrow=False)

    # Adjust parameters based on mobile state
    if is_mobile:
        text_size = 9
        height = 700  # Taller to accommodate all rows
        width = 800   # Wide enough to not compress
        margin_left = 120
        margin_right = 80  # Space for colorbar
        margin_top = 80
        margin_bottom = 120
        title_text = "Substance Correlations"
        title_size = 14
    else:
        text_size = 10
        height = 600
        width = None  # Auto width for desktop
        margin_left = 150
        margin_right = 50
        margin_top = 80
        margin_bottom = 150
        title_text = "Substance Co-occurrence Correlation Matrix"
        title_size = 16

    # Create heatmap
    subtitle = ""
    if selected_values and len(selected_values) > 1:
        subtitle = f" (records containing all of: {format_display_list(selected_values)})"

    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.index,
        colorscale='RdYlGn',
        zmid=0,
        text=corr_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": text_size},
        colorbar=dict(title="Correlation")
    ))

    fig.update_layout(
        title=dict(text=title_text + subtitle, font=dict(size=title_size)),
        xaxis=dict(side='bottom', tickangle=45, tickfont=dict(size=text_size)),
        yaxis=dict(autorange='reversed', tickfont=dict(size=text_size)),
        height=height,
        width=width,
        autosize=False if is_mobile else True
    )

    apply_standard_heatmap_layout(fig)

    return fig


@callback(
    Output("polysubstance-cooccurrence-bar-chart", "figure"),
    Output("polysubstance-cooccurrence-bar-caption", "children"),
    Input("polysubstance-substance-filter", "value"),
    Input("polysubstance-cooccurrence-is-mobile", "data"),
)
def update_bar_chart(selected_substances, is_mobile):
    """Create grouped bar chart showing co-occurrence percentages."""
    
    if df_raw.empty or 'substance' not in df_raw.columns:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    # Build co-occurrence data
    co_data = build_cooccurrence_data(df_raw)
    
    if co_data.empty:
        return go.Figure().add_annotation(text="No co-occurrence data available", showarrow=False)
    
    # Mobile-specific adjustments
    if is_mobile:
        text_size = 8
        height = 650
        width = 900  # Fixed width for scrolling
        title_size = 13
        margin_left = 140
        margin_right = 40
        margin_top = 70
        margin_bottom = 100
    else:
        text_size = 10
        height = 500
        width = None  # Auto width
        title_size = 16
        margin_left = 150
        margin_right = 50  # Can reduce now that legend is on top
        margin_top = 120  # More room for horizontal legend
        margin_bottom = 120  # More room for x-axis labels
    
    selected_values = (
        [v for v in selected_substances if v]
        if isinstance(selected_substances, (list, tuple, set))
        else ([selected_substances] if selected_substances else [])
    )
    bar_caption = ""

    # Filter by selected substances from main Substance Type filter.
    if selected_values:
        matched = _records_matching_all_selected_substances(df_raw, selected_values)
        if matched.empty:
            return go.Figure().add_annotation(
                text=f"No co-occurrence data for selected substance(s): {', '.join(str(v) for v in selected_values)}",
                showarrow=False
            )

        total_records = matched["record_id"].nunique()
        selected_set = {str(v) for v in selected_values}
        co_data = (
            matched.groupby("substance")["record_id"]
            .nunique()
            .reset_index(name="Count")
        )
        co_data = co_data[~co_data["substance"].astype(str).isin(selected_set)]
        if co_data.empty:
            return go.Figure().add_annotation(
                text="No additional co-substances found with all selected substances.",
                showarrow=False
            )

        co_data = co_data.rename(columns={"substance": "Also Found"})
        co_data["Total"] = total_records
        co_data["Percentage"] = (co_data["Count"] / total_records) * 100
        
        # Sort by percentage descending (highest to lowest) for both mobile and desktop
        co_data = co_data.sort_values('Percentage', ascending=False)
        
        # Create custom text with percentage and count
        co_data['label'] = co_data.apply(
            lambda row: f"{row['Percentage']:.1f}% (n={int(row['Count']):,})", 
            axis=1
        )
        
        # Create formatted hover text
        co_data['Count_formatted'] = co_data['Count'].apply(format_count_display)
        co_data['Total_formatted'] = co_data['Total'].apply(format_count_display)
        
        # Mobile: vertical bars (x=substance, y=percentage), Desktop: horizontal bars (x=percentage, y=substance)
        if len(selected_values) == 1:
            selected_label = str(selected_values[0])
            title_text = f"When {selected_label} is present, % with other substances"
        else:
            title_text = (
                f"When all of: {format_display_list(selected_values)} are present, % with other substances"
            )
        bar_caption = title_text

        if is_mobile:
            fig = px.bar(
                co_data,
                x='Also Found',
                y='Percentage',
                orientation='v',
                labels={'Percentage': 'Co-occurrence %', 'Also Found': 'Other Substance'},
                text='label',
                hover_data={
                    'Count': False, 
                    'Total': False, 
                    'label': False,
                    'Count_formatted': ':.0f',
                    'Total_formatted': ':.0f'
                },
                custom_data=['Count_formatted', 'Total_formatted']
            )
            
            fig.update_traces(
                marker_color="#22767C",
                textposition='outside',
                textangle=0,
                hovertemplate='<b>%{x}</b><br>' +
                             'Co-occurrence: %{y:.1f}%<br>' +
                             'Count: %{customdata[0]}<br>' +
                             'Total: %{customdata[1]}<extra></extra>',
                textfont=dict(size=text_size),
                cliponaxis=False
            )
            max_pct = float(co_data['Percentage'].max()) if not co_data.empty else 0.0
            fig.update_yaxes(range=[0, max_pct * 1.15 if max_pct else 1])
            # Keep visual order explicitly descending left-to-right.
            fig.update_xaxes(
                categoryorder='array',
                categoryarray=co_data['Also Found'].tolist()
            )
        else:
            fig = px.bar(
                co_data,
                x='Percentage',
                y='Also Found',
                orientation='h',
                labels={'Percentage': 'Co-occurrence %', 'Also Found': 'Other Substance'},
                text='label',
                hover_data={
                    'Count': False, 
                    'Total': False, 
                    'label': False,
                    'Count_formatted': ':.0f',
                    'Total_formatted': ':.0f'
                },
                custom_data=['Count_formatted', 'Total_formatted', 'Also Found']
            )
            
            fig.update_traces(
                marker_color="#22767C",
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>' +
                             'Co-occurrence: %{x:.1f}%<br>' +
                             'Count: %{customdata[0]}<br>' +
                             'Total: %{customdata[1]}<extra></extra>',
                textfont=dict(size=text_size),
                cliponaxis=False
            )
            max_pct = float(co_data['Percentage'].max()) if not co_data.empty else 0.0
            fig.update_xaxes(range=[0, max_pct * 1.15 if max_pct else 1])
            # Horizontal bars render categories bottom-to-top; reverse for descending top-to-bottom.
            fig.update_yaxes(
                categoryorder='array',
                categoryarray=co_data['Also Found'].tolist()[::-1]
            )
        
    else:
        # Show all primary substances
        # Add custom text label with percentage and count
        co_data['label'] = co_data.apply(
            lambda row: f"{row['Percentage']:.1f}% (n={int(row['Count']):,})" if not is_mobile else f"{row['Percentage']:.0f}%", 
            axis=1
        )
        
        # Create formatted hover text
        co_data['Count_formatted'] = co_data['Count'].apply(format_count_display)
        co_data['Total_formatted'] = co_data['Total'].apply(format_count_display)
        
        fig = px.bar(
            co_data,
            x='Primary',
            y='Percentage',
            color='Also Found',
            barmode='group',
            labels={'Percentage': 'Co-occurrence %', 'Primary': 'Primary Substance'},
            hover_data={
                'Count': False, 
                'Total': False, 
                'label': False,
                'Count_formatted': ':.0f',
                'Total_formatted': ':.0f'
            },
            custom_data=['Count_formatted', 'Total_formatted', 'Also Found']
        )
        
        fig.update_traces(
            # Grouped view has many traces; outside labels can clip and leave artifacts.
            textposition='none',
            text=None,
            textangle=0,
            hovertemplate='<b>%{customdata[2]}</b><br>' +
                         'Primary: %{x}<br>' +
                         'Co-occurrence: %{y:.1f}%<br>' +
                         'Count: %{customdata[0]}<br>' +
                         'Total: %{customdata[1]}<extra></extra>',
            textfont=dict(size=text_size),
            cliponaxis=False
        )
    
    # Apply mobile-responsive layout
    # X-axis angle: 45° for grouped view (substance names), 45° for mobile filtered (substance names), 0° for desktop filtered (percentages)
    x_angle = 45 if not selected_values else (45 if is_mobile else 0)

    fig.update_layout(
        height=height,
        width=width,
        xaxis=dict(
            tickangle=x_angle,
            tickfont=dict(size=text_size)
        ),
        yaxis=dict(tickfont=dict(size=text_size)),
        legend=dict(
            font=dict(size=text_size),
            orientation="h",  # Horizontal legend
            yanchor="bottom",
            y=1.02,  # Position above plot area
            xanchor="center",
            x=0.5  # Center horizontally
        ) if not selected_values else dict(font=dict(size=text_size)),
        autosize=False if is_mobile else True
    )

    apply_standard_bar_layout(fig, margin={"t": 30, "b": 50})
    
    return fig, bar_caption


@callback(
    Output("sunburst-cooccurrence", "figure"),
    Input("polysubstance-substance-filter", "value"),
    Input("polysubstance-age-filter", "value"),
    Input("polysubstance-sex-filter", "value"),
    Input("polysubstance-county-filter", "value"),
    Input("polysubstance-year-filter", "value"),
)
def update_sunburst(selected_substances, age, sex, county, year):
    """Create a sunburst chart showing Primary -> Also Found co-occurrences."""
    if df_raw.empty or not {"record_id", "substance"}.issubset(df_raw.columns):
        return go.Figure().add_annotation(text="No data available", showarrow=False)

    dff = df_raw.copy()
    if "age_group" in dff.columns:
        dff = _apply_filter(dff, "age_group", age)
    if "sex" in dff.columns:
        dff = _apply_filter(dff, "sex", sex)
    if "county" in dff.columns:
        dff = apply_county_filter(dff, county).copy()
    if "year" in dff.columns:
        dff = _apply_filter(dff, "year", year)
    if "substance" in dff.columns:
        dff = _apply_filter(dff, "substance", selected_substances)

    if dff.empty:
        return go.Figure().add_annotation(text="No data matching filters", showarrow=False)

    sunburst_data = build_sunburst_cooccurrence_data(dff)
    if sunburst_data.empty:
        return go.Figure().add_annotation(
            text="No co-occurrence data available",
            showarrow=False,
        )

    # Count unique records per (Primary, Also Found) pair
    pair_counts = sunburst_data.groupby(["Primary", "Also Found"])["record_id"].nunique().reset_index(name="Count")
    
    # Also get the total unique records per Primary substance
    primary_totals = dff.groupby("substance")["record_id"].nunique().reset_index(name="Count")
    
    # Build arrays for go.Sunburst with explicit unique ids.
    # We normalize child wedge sizes per parent so the outer ring fully covers each parent arc.
    ids = []
    labels = []
    parents = []
    values = []
    customdata = []

    primary_total_map = dict(zip(primary_totals["substance"], primary_totals["Count"]))

    # Inner ring: one node per substance.
    for _, row in primary_totals.iterrows():
        substance = row["substance"]
        total = float(row["Count"])
        ids.append(f"sub::{substance}")
        labels.append(substance)
        parents.append("")
        values.append(total)
        # [raw_count, primary_substance]
        customdata.append([int(total), substance])

    # Outer ring: co-occurrence children under each primary substance.
    # Raw counts overlap by design, so we scale child arc lengths to fill each parent exactly.
    for primary, sub_df in pair_counts.groupby("Primary"):
        parent_total = float(primary_total_map.get(primary, 0))
        raw_sum = float(sub_df["Count"].sum())
        if parent_total <= 0 or raw_sum <= 0:
            continue

        for _, row in sub_df.iterrows():
            also_found = row["Also Found"]
            raw_count = float(row["Count"])
            scaled_value = parent_total * (raw_count / raw_sum)
            ids.append(f"pair::{primary}::{also_found}")
            labels.append(also_found)
            parents.append(f"sub::{primary}")
            values.append(scaled_value)
            customdata.append([int(raw_count), primary])

    fig = go.Figure(go.Sunburst(
        ids=ids,
        labels=labels,
        parents=parents,
        values=values,
        customdata=customdata,
        branchvalues="total",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Raw Count: %{customdata[0]:,}<br>"
            "Primary: %{customdata[1]}<extra></extra>"
        ),
    ))
    apply_standard_non_axis_layout(fig, title="Substance Co-occurrence Sunburst")
    return fig


@callback(
    Output("polysubstance-cooccurrence-network", "figure"),
    Input("polysubstance-substance-filter", "value"),  # Not used, but keeps callback structure
)
def update_network(_):
    """Create a network graph showing substance co-occurrences."""
    
    if df_raw.empty or 'substance' not in df_raw.columns:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    # Build co-occurrence matrix
    cooccurrence = build_cooccurrence_matrix(df_raw)
    
    # Create edge list (only show edges above a threshold)
    threshold = 50
    edges = []
    edge_weights = []
    
    substances = list(cooccurrence.index)
    
    for i, sub1 in enumerate(substances):
        for j, sub2 in enumerate(substances):
            if i < j:  # Only upper triangle to avoid duplicates
                weight = cooccurrence.loc[sub1, sub2]
                # Ensure weight is numeric for comparison
                try:
                    weight_num = float(weight)
                except Exception:
                    continue
                if weight_num > threshold:
                    edges.append((sub1, sub2))
                    edge_weights.append(weight_num)
    
    if not edges:
        return go.Figure().add_annotation(
            text=f"No co-occurrences above threshold ({threshold})",
            showarrow=False
        )
    
    # Simple circular layout
    n = len(substances)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    pos = {sub: (np.cos(angle), np.sin(angle)) for sub, angle in zip(substances, angles)}
    
    # Create edge traces with labels
    edge_traces = []
    edge_label_traces = []
    
    for (sub1, sub2), weight in zip(edges, edge_weights):
        x0, y0 = pos[sub1]
        x1, y1 = pos[sub2]
        
        # Normalize weight for line width (1-10 range)
        max_weight = max(edge_weights)
        line_width = 1 + (weight / max_weight) * 9
        
        # Add edge line
        edge_traces.append(go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(width=line_width, color='rgba(125,125,125,0.3)'),
            hoverinfo='skip',
            showlegend=False
        ))
        
        # Calculate position offset perpendicular to the line
        # This helps spread out labels to reduce overlap
        dx = x1 - x0
        dy = y1 - y0
        length = np.sqrt(dx**2 + dy**2)
        
        # Perpendicular offset (very small displacement to stay close to line)
        offset = 0.02
        perp_x = -dy / length * offset
        perp_y = dx / length * offset
        
        # Position label slightly offset from midpoint
        mid_x = (x0 + x1) / 2 + perp_x
        mid_y = (y0 + y1) / 2 + perp_y
        
        edge_label_traces.append(go.Scatter(
            x=[mid_x],
            y=[mid_y],
            mode='markers+text',
            text=[f"{int(weight):,}"],
            textfont=dict(size=10, color='#ffffff', family='Arial'),
            textposition='middle center',
            hovertext=f"{sub1} + {sub2}<br>Co-occurrences: {int(weight):,}",
            hoverinfo='text',
            showlegend=False,
            # Add background box to make text stand out
            marker=dict(
                size=20,
                color='#d32f2f',
                symbol='square',
                line=dict(width=0)
            )
        ))
    
    # Create node trace
    node_x = [pos[sub][0] for sub in substances]
    node_y = [pos[sub][1] for sub in substances]
    node_size = []
    for sub in substances:
        try:
            freq = float(cooccurrence.loc[sub, sub])
        except Exception:
            freq = 1.0
        node_size.append(freq / 50)
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=substances,
        textposition='top center',
        marker=dict(
            size=node_size,
            color='lightblue',
            line=dict(width=2, color='darkblue'),
            sizemode='area',
            sizeref=2.*max(node_size)/(40.**2) if node_size else 1,
            sizemin=4
        ),
        hovertext=[f"{sub}<br>Frequency: {cooccurrence.loc[sub, sub]:,.0f}" for sub in substances],
        hoverinfo='text',
        showlegend=False
    )
    
    # Combine traces: edges, edge labels, then nodes (so nodes appear on top)
    fig = go.Figure(data=edge_traces + edge_label_traces + [node_trace])
    apply_standard_network_layout(
        fig,
        node_count=len(substances),
        title=f"Substance Co-occurrence Network (threshold: {threshold}+ cases)",
        showlegend=False,
        hovermode='closest',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.2, 1.2], fixedrange=True),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.2, 1.2], fixedrange=True),
        plot_bgcolor='white',
    )
    
    return fig


@callback(
    Output("polysubstance-cooccurrence-sankey", "figure"),
    Input("polysubstance-substance-filter", "value"),  # Not used, but keeps callback structure
)
def update_sankey(_):
    """Create a Sankey diagram showing substance flow patterns."""
    
    if df_raw.empty or 'substance' not in df_raw.columns:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    # Get top substances to keep diagram readable
    top_substances = (
        df_raw.groupby('substance')['record_id']
        .nunique()
        .nlargest(8)
        .index.tolist()
    )
    
    # Filter to top substances
    df_filtered = df_raw[df_raw['substance'].isin(top_substances)].copy()
    
    # Build co-occurrence edges
    edges = []
    for substance in top_substances:
        records = df_filtered[df_filtered['substance'] == substance]['record_id'].unique()
        
        for other_sub in top_substances:
            if other_sub != substance:
                count = df_filtered[
                    (df_filtered['record_id'].isin(records)) & 
                    (df_filtered['substance'] == other_sub)
                ]['record_id'].nunique()

                if count > 20:  # Only show significant connections
                    edges.append({
                        'source': substance,
                        'target': other_sub,
                        'value': count
                    })
    
    if not edges:
        return go.Figure().add_annotation(text="Insufficient data for Sankey diagram", showarrow=False)
    
    edge_df = pd.DataFrame(edges)
    
    # Create node list and mappings
    all_nodes = list(set(edge_df['source'].tolist() + edge_df['target'].tolist()))
    node_dict = {node: idx for idx, node in enumerate(all_nodes)}

    # Scale figure height with node count so lower nodes/links are not clipped.
    node_count = len(all_nodes)
    
    # Map to indices
    source_indices = [node_dict[s] for s in edge_df['source']]
    target_indices = [node_dict[t] for t in edge_df['target']]
    
    # Create Sankey
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            color="lightblue"
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=edge_df['value'].tolist(),
            label=[f"{edge_df.iloc[i]['value']:,.0f}" for i in range(len(edge_df))]
        )
    )])
    
    apply_standard_sankey_layout(
        fig,
        node_count=node_count,
        title="Substance Co-occurrence Flow (Top 8 Substances)",
        font=dict(size=12),
    )
    
    return fig
