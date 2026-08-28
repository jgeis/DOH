# polysubstance_dashboard_db.py — pure layout + callbacks (desktop-safe, mobile-aware)

# - db_utils: to connect to database (SQLite or MSSQL based on config)
# - pandas / numpy: to clean and shape the data
# - dash + dash_bootstrap_components: to build the web page and styles
# - plotly: to draw the charts
from pathlib import Path

import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio


from theme import register_template
from db_utils import execute_query
from dashboard_utils import (
    apply_year_filter,
    make_kpi_card,
    make_left_sidebar,
    make_right_summary_tables_col,
    compute_last_updated_value,
    compute_adaptive_horizontal_bar_height,
    make_filters_card,
    dropdown_filter,
    sort_opts,
    statewide_first,
    apply_county_filter,
    county_output_should_include_statewide,
    append_statewide_aggregate_rows,
    format_count_display,
    build_suppressed_percentage_columns,
    format_display_list,
    wrap_axis_label,
    apply_standard_single_series_bar_trace,
    apply_standard_bar_layout,
    add_stacked_bar_total_labels,
    apply_standard_line_layout,
    apply_standard_non_axis_layout,
    apply_standard_heatmap_layout,
    _get_active_filters_from_ctx,
    build_summary_count_table,
    load_sql_query,
)

# This applies our custom Plotly look (colors, fonts, etc.) everywhere in this app.
register_template()  # set your Plotly template globally

# ---------- DB → DataFrame ----------
def load_df():
    """
    Load the main dataset from the SQLite database.

    Steps:
      1. Load the polysubstance data query.
      2. Read the result into a table (DataFrame).
      3. Clean up some columns so they behave nicely in filters and charts.
    """

    sql = load_sql_query("load_polysubstance_data")

    # Execute query using db_utils (automatically uses correct database)
    df = execute_query(sql)

    # If nothing comes back, it’s better to crash early than show an empty dashboard.
    if df.empty:
        raise RuntimeError("Query returned 0 rows. Check DB and queries.sql.")

    # These columns are treated as category-like text fields.
    # Here we clean them up to avoid weird blanks or "nan" strings.
    want_obj = ["county", "city", "hawaii_residency", "age_group", "sex", "substance", "race_ethnicity"]
    for c in want_obj:
        if c in df.columns:
            # Catch actual nulls first, then convert to string and strip whitespace
            df[c] = df[c].fillna("Unknown").astype(str).str.strip()
            # Explicitly catch empty strings and pandas <NA> string artifacts
            df[c] = df[c].replace({
                "": "Unknown", 
                "nan": "Unknown", 
                "NaN": "Unknown", 
                "None": "Unknown", 
                "<NA>": "Unknown"
            })

    # Make sure the year column is a proper integer type so graphs order it correctly.
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

    # Print some quick info in the console for debugging.
    print(f"[load_df] rows={len(df):,}  cols={list(df.columns)}")
    print("Plotly default template:", pio.templates.default)
    return df




# ---------- Helper functions ----------
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


def build_cooccurrence_data(df, age=None, sex=None, county=None, year=None, race_ethnicity=None, hawaii_residency=None):
    """
    Build data for grouped bar chart showing co-occurrence percentages.

    For each substance, calculate what % of records also have other substances.
    """
    # Apply filters to match sunburst logic
    if "age_group" in df.columns:
        df = apply_filter(df, "age_group", age)
    if "sex" in df.columns:
        df = apply_filter(df, "sex", sex)
    if "county" in df.columns:
        df = apply_county_filter(df, county).copy()
    if "year" in df.columns:
        df = apply_year_filter(df, "year", year)
    if "race_ethnicity" in df.columns:
        df = apply_filter(df, "race_ethnicity", race_ethnicity)
    if "hawaii_residency" in df.columns:
        df = apply_filter(df, "hawaii_residency", hawaii_residency)

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
last_updated_value = compute_last_updated_value(df_raw)


# ---------- filter options ----------
def opts(values):
    """
    Wrap a raw list of values into the format Dash expects for dropdown options:
    each one needs a label and value.
    """
    return [{"label": v, "value": v} for v in values]

# Build the dropdown choices for each filter, only if those columns exist.
substance_opts        = sort_opts(df_raw["substance"])        if "substance"        in df_raw.columns else []
county_opts           = sort_opts(df_raw["county"])           if "county"           in df_raw.columns else []
age_opts              = sort_opts(df_raw["age_group"])        if "age_group"        in df_raw.columns else []
sex_opts              = sort_opts(df_raw["sex"])              if "sex"              in df_raw.columns else []
year_opts             = sort_opts(df_raw["year"])             if "year"             in df_raw.columns else []
race_ethnicity_opts   = sort_opts(df_raw["race_ethnicity"])   if "race_ethnicity"   in df_raw.columns else []
hawaii_residency_opts = sort_opts(df_raw["hawaii_residency"]) if "hawaii_residency" in df_raw.columns else []

# Total number of unique records, used for the big KPI card.
kpi_total = df_raw["record_id"].nunique() if "record_id" in df_raw.columns else 0

from section_texts import SECTION_TEXTS
polysubstance_sidebar_text = SECTION_TEXTS.get("discharges-su-polysubstance", [])

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
        dropdown_filter("Race/Ethnicity", "polysubstance-race-ethnicity-filter", options=opts(race_ethnicity_opts), multi=True, placeholder="All"),
        dropdown_filter("Hawaii Resident", "polysubstance-hawaii-residency-filter", options=opts(hawaii_residency_opts), multi=True, placeholder="All"),
    ],
)


# ---------- small helpers ----------
def apply_filter(frame: pd.DataFrame, col: str, val) -> pd.DataFrame:
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


def wrap_label(label: str, max_len: int = 22):
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


def records_matching_all_selected_substances(frame: pd.DataFrame, selected_values) -> pd.DataFrame:
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

# ---------- layout factory (mobile-aware) ----------
def layout_for(is_mobile: bool = False):
    """
    Build the full page layout.

    We accept a flag `is_mobile` so we can adjust chart heights
    for smaller screens.

    The page is split into three columns:
      LEFT:  KPI + filters
      CENTER: main bar/stacked charts
      RIGHT: summary tables
    """
    # Make charts taller on phones so they are easier to read.
    h_bar = (
        "60vh"
        if is_mobile
        else f"{compute_adaptive_horizontal_bar_height(len(substance_opts))}px"
    )
    h_stack = "55vh" if is_mobile else "360px"
    h_full_row = "55vh" if is_mobile else "420px"
    sunburst_height = "70vh" if is_mobile else "760px"

    def panel(content, sr_text=None, class_name="mb-4 p-2 bg-white rounded-2"):
        children = [content]
        if sr_text:
            children.append(html.P(sr_text, className="visually-hidden"))
        return html.Div(children, className=class_name)

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
        md=4,
    )

    # CENTER: top charts in the middle column
    center = dbc.Col([
        panel(
            dcc.Graph(
                id="sunburst-cooccurrence",
                style={"height": sunburst_height, "width": "100%"},
                config={"displayModeBar": True, "displaylogo": False},
            ),
            "Sunburst chart showing co-occurring substances in the selected cohort.",
        ),
        panel(
            dcc.Graph(
                id="bar-top-substances",
                style={"width": "100%"},
                config={"displayModeBar": True, "displaylogo": False},
            ),
            "Horizontal bar chart showing the top substances among polysubstance records.",
        ),
    ], xs=12, md=8)

    # Trend charts should span the combined left + middle width.
    trend_charts = dbc.Col([
        panel(
            dcc.Graph(
                id="line-year-substance",
                style={"height": h_stack, "width": "100%"},
                config={"displayModeBar": True, "displaylogo": False},
            ),
            "Line chart showing yearly discharges by substance.",
        ),
        panel(
            dcc.Graph(
                id="polysubstance-age-year-lines",
                style={"height": h_stack, "width": "100%"},
                config={"displayModeBar": True, "displaylogo": False},
            ),
            "Line chart showing yearly discharges by age group.",
        ),
        panel(
            dcc.Graph(
                id="polysubstance-sex-year-stacked",
                style={"height": h_bar, "width": "100%"},
                config={"displayModeBar": True, "displaylogo": False},
            ),
            "Stacked bar chart showing yearly discharges by gender.",
        ),
    ], xs=12, md=12)

    # RIGHT: summary tables (ordered by shared site-wide utility)
    right = make_right_summary_tables_col(
        [
            ("Calendar Year", "tbl-year"),
            ("County", "tbl-county-share"),
            ("Age Group", "tbl-age"),
            ("Sex", "tbl-sex"),
            ("Race/Ethnicity", "tbl-race-ethnicity"),
            ("Hawaii Resident", "tbl-hawaii-residency"),
        ],
        xs=12,
        md=3,
    )

    # Wrap everything up in one fluid container.
    return dbc.Container([
        # Accessibility: a "skip" link so keyboard users can jump right to filters.
        html.A(
            "Skip to filters", href="#polysubstance-filters",
            className="visually-hidden-focusable", tabIndex=0
        ),

        # Store mobile state for callbacks
        dcc.Store(id="polysubstance-cooccurrence-is-mobile", data=is_mobile),

        # Hidden placeholders keep existing callback outputs stable after removing visible title boxes.
        html.Div(id="bar-top-substances-title", style={"display": "none"}),
        html.Div(id="line-year-substance-title", style={"display": "none"}),
        html.Div(id="stack-year-county-title", style={"display": "none"}),
        html.Div(id="polysubstance-cooccurrence-bar-caption", style={"display": "none"}),

        dbc.Row([
            dbc.Col([
                dbc.Row([left, center], className="g-3"),
                dbc.Row([trend_charts], className="g-3 mt-0"),
            ], xs=12, md=9),
            right,
        ], className="g-3"),

        # Full-width row under filters/blurbs: county trend
        dbc.Row([
            dbc.Col([
                panel(
                    dcc.Graph(
                        id="stack-year-county",
                        style={"height": h_full_row, "width": "100%"},
                        config={"displayModeBar": True, "displaylogo": False},
                    ),
                    "Line chart showing discharges by year and county.",
                ),
            ], xs=12, md=12),
        ], className="g-3"),

        
        # Visualization 1: Heatmap
        dbc.Row([
            dbc.Col([
                panel(
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
                    "Heatmap showing how often substances appear together in the same polysubstance record.",
                )
            ], md=12, className="mb-4")
        ]),
        
        # Visualization 2: Grouped Bar Chart
        dbc.Row([
            dbc.Col([
                panel(
                    dcc.Loading(
                        html.Div(
                            html.Div(
                                dcc.Graph(
                                    id="polysubstance-cooccurrence-bar-chart",
                                    config={"displayModeBar": True, "displaylogo": False},
                                    style={"width": "100%"}
                                ),
                                className="graph-inner" if is_mobile else ""
                            ),
                            className="hscroll-graph" if is_mobile else ""
                        )
                    ),
                    "Grouped bar chart showing the percentage of cases where each substance co-occurs with other substances.",
                )
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
    Output("polysubstance-age-year-lines", "figure"),
    Output("polysubstance-sex-year-stacked", "figure"),
    Output("stack-year-county", "figure"),
    Output("tbl-year", "children"),
    Output("tbl-county-share", "children"),
    Output("tbl-age", "children"),
    Output("tbl-sex", "children"),
    Output("tbl-race-ethnicity", "children"),
    Output("tbl-hawaii-residency", "children"),
    Input("polysubstance-substance-filter", "value"),
    Input("polysubstance-age-filter", "value"),
    Input("polysubstance-sex-filter", "value"),
    Input("polysubstance-county-filter", "value"),
    Input("polysubstance-year-filter", "value"),
    Input("polysubstance-race-ethnicity-filter", "value"),
    Input("polysubstance-hawaii-residency-filter", "value"),
)
def update(substance, age, sex, county, year, race_ethnicity, hawaii_residency):
    # Base frame for co-occurrence-aware charts: apply non-substance filters only.
    dff_base = df_raw.copy()
    if "age_group" in dff_base.columns:
        dff_base = apply_filter(dff_base, "age_group", age)
    if "sex" in dff_base.columns:
        dff_base = apply_filter(dff_base, "sex", sex)
    if "county" in dff_base.columns:
        dff_base = apply_county_filter(dff_base, county).copy()
    if "year" in dff_base.columns:
        dff_base = apply_year_filter(dff_base, "year", year)
    if "race_ethnicity" in dff_base.columns:
        dff_base = apply_filter(dff_base, "race_ethnicity", race_ethnicity)
    if "hawaii_residency" in dff_base.columns:
        dff_base = apply_filter(dff_base, "hawaii_residency", hawaii_residency)

    # Main frame for existing visuals: includes substance filter.
    dff = dff_base.copy()
    if "substance" in dff.columns:
        dff = apply_filter(dff, "substance", substance)

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
        kpi_source = records_matching_all_selected_substances(dff_base, selected_substances)
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
        bar_source = records_matching_all_selected_substances(dff_base, selected_substances)

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
            apply_standard_bar_layout(fig_sub, title=bar_title)
        else:
            sub_counts["substance_wrapped"] = sub_counts["substance"].apply(wrap_label)

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
            apply_standard_single_series_bar_trace(fig_sub)
            apply_standard_bar_layout(
                fig_sub,
                xaxis=dict(rangemode="tozero"),
                title=bar_title,
            )
    else:
        fig_sub = px.bar()
        apply_standard_bar_layout(fig_sub, title=bar_title)


    # ---------- Line: Yearly Discharges by Substance ----------
    line_source = dff
    if selected_substances and {"substance", "record_id"}.issubset(dff_base.columns):
        line_source = records_matching_all_selected_substances(dff_base, selected_substances)
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
            title=line_title,
        )

    else:
        fig_year_substance = px.line()
        apply_standard_line_layout(fig_year_substance, title=line_title)

    demographic_source = dff
    if selected_substances and {"substance", "record_id"}.issubset(dff_base.columns):
        demographic_source = records_matching_all_selected_substances(dff_base, selected_substances)

    # ---------- Line: Yearly Discharges by Age Group ----------
    if {"year", "age_group", "record_id"}.issubset(demographic_source.columns) and not demographic_source.empty:
        by_ya = (
            demographic_source.drop_duplicates(subset=["record_id"])
            .groupby(["year", "age_group"])["record_id"].nunique()
            .reset_index(name="discharges")
        )
        by_ya["display_count"] = by_ya["discharges"].apply(format_count_display)

        age_line_fig = px.line(
            by_ya,
            x="year",
            y="discharges",
            color="age_group",
            markers=True,
            custom_data=["display_count"],
            labels={"year": "Year", "discharges": "Discharges", "age_group": "Age Group"},
            category_orders={"age_group": age_opts} if age_opts else None,
        )
        age_line_fig.update_traces(
            hovertemplate="Year %{x}<br>Age Group: %{fullData.name}<br>Discharges: %{customdata[0]}<extra></extra>"
        )
        apply_standard_line_layout(age_line_fig, title="Yearly Discharges by Age Group")
    else:
        age_line_fig = px.line()
        apply_standard_line_layout(age_line_fig, title="Yearly Discharges by Age Group")

    # ---------- Stacked bar: Yearly Discharges by Gender (Sex) ----------
    if {"year", "sex", "record_id"}.issubset(demographic_source.columns) and not demographic_source.empty:
        by_ys = (
            demographic_source.drop_duplicates(subset=["record_id"])
            .groupby(["year", "sex"])["record_id"].nunique()
            .reset_index(name="discharges")
            .sort_values(["year", "sex"])
        )
        by_ys["display_count"] = by_ys["discharges"].apply(format_count_display)

        sex_bar = px.bar(
            by_ys,
            x="year",
            y="discharges",
            color="sex",
            barmode="stack",
            labels={"year": "Year", "discharges": "Discharges", "sex": "Sex at Birth"},
            text="display_count"
        )
        sex_bar.update_traces(
            textposition="inside",
            insidetextanchor="middle",
            cliponaxis=False
        )

        totals = by_ys.groupby("year")["discharges"].sum().reset_index()
        add_stacked_bar_total_labels(sex_bar, totals, x_col="year", y_col="discharges")

        max_y = int(totals["discharges"].max()) if not totals.empty else 0
        apply_standard_bar_layout(
            sex_bar,
            margin=dict(t=80),
            xaxis=dict(dtick=1),
            yaxis=dict(range=[0, max_y * 1.25 if max_y else 1]),
            title="Yearly Discharges by Gender",
        )
        sex_bar.update_traces(
            textposition="inside",
            insidetextanchor="middle",
            selector={"type": "bar"},
        )
    else:
        sex_bar = px.bar()
        apply_standard_bar_layout(
            sex_bar,
            margin=dict(t=80),
            title="Yearly Discharges by Gender",
        )

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
            title=county_title,
        )
    else:
        fig_year_county = px.line()
        apply_standard_line_layout(fig_year_county, title=county_title)

    def summary_table(df, col, ordered=None, filter_selection=None):
        # Use shared build_summary_count_table for summary tables, letting it handle header labels
        if col not in df.columns or df.empty:
            return dbc.Alert(f"No data for '{col}'.", color="warning", className="mb-0")
        return build_summary_count_table(
            df,
            group_col=col,
            id_col="record_id",
            categories=ordered,
            filter_selection=filter_selection,
            include_statewide_county=(col == "county" and include_statewide_on_line),
        )

    # ---------- Small tables ----------
    uniq = demographic_source.drop_duplicates(subset=["record_id"])
    
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

    year_source = uniq.copy()
    if "year" in year_source.columns and not year_source.empty:
        year_source["year"] = year_source["year"].astype(str)

    county_opts_ordered = statewide_first(sort_opts(uniq["county"])) if "county" in uniq.columns and not uniq.empty else None
    tbl_county = summary_table(uniq, "county", county_opts_ordered, filter_selection=county)
    tbl_year = summary_table(year_source, "year", year_groups, filter_selection=year)
    tbl_age = summary_table(uniq, "age_group", age_opts, filter_selection=age)
    tbl_sex = summary_table(uniq, "sex", sex_opts, filter_selection=sex)
    tbl_race = summary_table(uniq, "race_ethnicity", race_ethnicity_opts, filter_selection=race_ethnicity)
    tbl_hawaii = summary_table(uniq, "hawaii_residency", hawaii_residency_opts, filter_selection=hawaii_residency)

    return (
        kpi_value, 
        bar_title, 
        line_title, 
        county_title, 
        fig_sub, 
        fig_year_substance, 
        age_line_fig, 
        sex_bar, 
        fig_year_county, 
        tbl_year, 
        tbl_county, 
        tbl_age, 
        tbl_sex, 
        tbl_race, 
        tbl_hawaii
    )


# ---------- Reset filters ----------
@callback(
    Output("polysubstance-substance-filter", "value"),
    Output("polysubstance-age-filter", "value"),
    Output("polysubstance-sex-filter", "value"),
    Output("polysubstance-county-filter", "value"),
    Output("polysubstance-year-filter", "value"),
    Output("polysubstance-race-ethnicity-filter", "value"),
    Output("polysubstance-hawaii-residency-filter", "value"),
    Input("polysubstance-reset-filters-btn", "n_clicks"),
    prevent_initial_call=True
)
def reset_filters(n):
    """
    When the user clicks the Reset button, clear every filter.

    We return empty lists so Dash treats them as "no selection".
    """
    return [], [], [], [], [], [], []



# ---------- Callbacks ----------


@callback(
    Output("polysubstance-cooccurrence-heatmap", "figure"),
    Output("polysubstance-cooccurrence-bar-chart", "figure"),
    Output("polysubstance-cooccurrence-bar-caption", "children"),
    Output("sunburst-cooccurrence", "figure"),
    Input("polysubstance-substance-filter", "value"),
    Input("polysubstance-cooccurrence-is-mobile", "data"),
    Input("polysubstance-age-filter", "value"),
    Input("polysubstance-sex-filter", "value"),
    Input("polysubstance-county-filter", "value"),
    Input("polysubstance-year-filter", "value"),
    Input("polysubstance-race-ethnicity-filter", "value"),
    Input("polysubstance-hawaii-residency-filter", "value"),
)
def update_dashboard(selected_substances, is_mobile, age, sex, county, year, race_ethnicity, hawaii_residency):
    """
    Unified callback that updates the heatmap, grouped bar chart, and sunburst
    simultaneously.
    """
    empty_fig = go.Figure().add_annotation(text="No data available", showarrow=False)
    bar_caption = ""
    heatmap_note = (
        "Heatmap shows how often substances appear together; darker cells indicate stronger co-occurrence."
    )

    def title_top_margin(title_text: str, base: int = 70, per_line: int = 18, min_margin: int = 90, max_margin: int = 170) -> int:
        """Compute consistent top spacing for multi-line in-figure title blocks."""
        line_count = max(1, str(title_text).count("<br>") + 1)
        computed = base + ((line_count - 1) * per_line)
        return max(min_margin, min(max_margin, computed))
    
    # If the raw data is completely missing, return empty states for everything
    if df_raw.empty or 'substance' not in df_raw.columns:
        return empty_fig, empty_fig, bar_caption, empty_fig

    # Parse selected substances once
    selected_values = (
        [v for v in selected_substances if v]
        if isinstance(selected_substances, (list, tuple, set))
        else ([selected_substances] if selected_substances else [])
    )

    # ---------------------------------------------------------
    # 1. Heatmap Generation
    # ---------------------------------------------------------
    dff_heat = df_raw.copy()
    if "age_group" in dff_heat.columns: dff_heat = apply_filter(dff_heat, "age_group", age)
    if "sex" in dff_heat.columns:       dff_heat = apply_filter(dff_heat, "sex", sex)
    if "county" in dff_heat.columns:    dff_heat = apply_county_filter(dff_heat, county).copy()
    if "year" in dff_heat.columns:      dff_heat = apply_year_filter(dff_heat, "year", year)
    if "race_ethnicity" in dff_heat.columns: dff_heat = apply_filter(dff_heat, "race_ethnicity", race_ethnicity)
    if "hawaii_residency" in dff_heat.columns: dff_heat = apply_filter(dff_heat, "hawaii_residency", hawaii_residency)

    if selected_values:
        dff_heat = records_matching_all_selected_substances(dff_heat, selected_values)
        
    heatmap_subtitle = (
        f" (records containing all of: {format_display_list(selected_values)})"
        if (selected_values and len(selected_values) > 1)
        else ""
    )

    if dff_heat.empty:
        heatmap_fig = go.Figure().add_annotation(text="No data for selected substance(s)", showarrow=False)
    else:
        corr_matrix = build_correlation_matrix(dff_heat)
        if corr_matrix.empty:
            heatmap_fig = go.Figure().add_annotation(text="No co-occurrence data available", showarrow=False)
        else:
            if is_mobile:
                text_size, height, width = 9, 700, 800
                title_text, title_size = "Substance Correlations", 14
            else:
                text_size, height, width = 10, 600, None
                title_text, title_size = "Substance Co-occurrence Correlation Matrix", 16

            heatmap_fig = go.Figure(data=go.Heatmap(
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

            heatmap_fig.update_layout(
                title=dict(text=title_text + heatmap_subtitle, font=dict(size=title_size)),
                xaxis=dict(side='bottom', tickangle=45, tickfont=dict(size=text_size)),
                yaxis=dict(autorange='reversed', tickfont=dict(size=text_size)),
                height=height,
                width=width,
                autosize=False if is_mobile else True
            )
            apply_standard_heatmap_layout(heatmap_fig)

    apply_standard_heatmap_layout(heatmap_fig)
    heatmap_title = "Substance Co-occurrence Correlation Matrix" + heatmap_subtitle
    filter_context = _get_active_filters_from_ctx()
    heatmap_title_text = (
        f"{heatmap_title}{filter_context}"
        f"<br><span style='font-size:{12 if is_mobile else 13}px;color:#5f6b76'>{heatmap_note}</span>"
    )
    heatmap_fig.update_layout(
        title=dict(
            text=heatmap_title_text,
            font=dict(size=18, color="#1f2d3d"),
            x=0.5,
            xanchor="center",
        ),
        margin=dict(t=title_top_margin(heatmap_title_text)),
    )


    # ---------------------------------------------------------
    # 2. Grouped Bar Chart Generation
    # ---------------------------------------------------------
    co_data = build_cooccurrence_data(df_raw, age=age, sex=sex, county=county, year=year, race_ethnicity=race_ethnicity, hawaii_residency=hawaii_residency)
    
    if co_data.empty:
        bar_fig = go.Figure().add_annotation(text="No co-occurrence data available", showarrow=False)
    else:
        plot_width = 900 if is_mobile else None
        
        if selected_values:
            dff_base_matched = df_raw.copy()
            if "age_group" in dff_base_matched.columns: dff_base_matched = apply_filter(dff_base_matched, "age_group", age)
            if "sex" in dff_base_matched.columns:       dff_base_matched = apply_filter(dff_base_matched, "sex", sex)
            if "county" in dff_base_matched.columns:    dff_base_matched = apply_county_filter(dff_base_matched, county).copy()
            if "year" in dff_base_matched.columns:      dff_base_matched = apply_year_filter(dff_base_matched, "year", year)
            if "race_ethnicity" in dff_base_matched.columns: dff_base_matched = apply_filter(dff_base_matched, "race_ethnicity", race_ethnicity)
            if "hawaii_residency" in dff_base_matched.columns: dff_base_matched = apply_filter(dff_base_matched, "hawaii_residency", hawaii_residency)

            matched = records_matching_all_selected_substances(dff_base_matched, selected_values)
            if matched.empty:
                bar_fig = go.Figure().add_annotation(
                    text=f"No co-occurrence data for selected substance(s): {', '.join(str(v) for v in selected_values)}",
                    showarrow=False
                )
            else:
                total_records = matched["record_id"].nunique()
                selected_set = {str(v) for v in selected_values}
                co_data = matched.groupby("substance")["record_id"].nunique().reset_index(name="Count")
                co_data = co_data[~co_data["substance"].astype(str).isin(selected_set)]
                
                if co_data.empty:
                    bar_fig = go.Figure().add_annotation(text="No additional co-substances found with all selected substances.", showarrow=False)
                else:
                    co_data = co_data.rename(columns={"substance": "Also Found"})
                    co_data["Total"] = total_records
                    co_data["Percentage"] = (co_data["Count"] / total_records) * 100
                    co_data = co_data.sort_values('Percentage', ascending=False)
                    
                    co_data['Count_formatted'] = co_data['Count'].apply(format_count_display)
                    co_data['Total_formatted'] = co_data['Total'].apply(format_count_display)
                    co_data['Plot_Percentage'], co_data['Percentage_display'], _ = build_suppressed_percentage_columns(
                        co_data['Percentage'], count_display_values=co_data['Count_formatted'], decimals=1
                    )
                    co_data['Cooccurrence_line'] = co_data['Percentage_display'].apply(
                        lambda pct: f"Co-occurrence: {pct}" if pd.notna(pct) and str(pct).strip() else "Co-occurrence: Suppressed"
                    )
                    co_data['label'] = co_data.apply(
                        lambda row: f"{row['Percentage_display']} (n={row['Count_formatted']})" if pd.notna(row['Percentage_display']) and str(row['Percentage_display']).strip() else row['Count_formatted'],
                        axis=1
                    )
                    
                    if len(selected_values) == 1:
                        bar_caption = f"When {selected_values[0]} is present, % with other substances"
                    else:
                        bar_caption = f"When all of: {format_display_list(selected_values)} are present, % with other substances"

                    if is_mobile:
                        bar_fig = px.bar(
                            co_data, x='Also Found', y='Plot_Percentage', orientation='v',
                            labels={'Plot_Percentage': 'Percentage', 'Also Found': 'Other Substance'},
                            text='label', hover_data={'Count': False, 'Total': False, 'label': False},
                            custom_data=['Count_formatted', 'Total_formatted', 'Cooccurrence_line']
                        )
                        apply_standard_single_series_bar_trace(
                            bar_fig, textangle=0,
                            hovertemplate='<b>%{x}</b><br>%{customdata[2]}<br>Count: %{customdata[0]}<br>Total: %{customdata[1]}<extra></extra>',
                        )
                        max_pct = float(co_data['Plot_Percentage'].max()) if not co_data.empty else 0.0
                        bar_fig.update_yaxes(range=[0, max_pct * 1.15 if max_pct else 1])
                        bar_fig.update_xaxes(categoryorder='array', categoryarray=co_data['Also Found'].tolist())
                    else:
                        bar_fig = px.bar(
                            co_data, x='Plot_Percentage', y='Also Found', orientation='h',
                            labels={'Plot_Percentage': 'Percentage', 'Also Found': 'Other Substance'},
                            text='label', hover_data={'Count': False, 'Total': False, 'label': False},
                            custom_data=['Count_formatted', 'Total_formatted', 'Cooccurrence_line', 'Also Found']
                        )
                        apply_standard_single_series_bar_trace(
                            bar_fig,
                            hovertemplate='<b>%{y}</b><br>%{customdata[2]}<br>Count: %{customdata[0]}<br>Total: %{customdata[1]}<extra></extra>',
                        )
                        max_pct = float(co_data['Plot_Percentage'].max()) if not co_data.empty else 0.0
                        bar_fig.update_xaxes(range=[0, max_pct * 1.15 if max_pct else 1])
                        bar_fig.update_yaxes(categoryorder='array', categoryarray=co_data['Also Found'].tolist()[::-1])
        else:
            co_data['Count_formatted'] = co_data['Count'].apply(format_count_display)
            co_data['Total_formatted'] = co_data['Total'].apply(format_count_display)
            co_data['Plot_Percentage'], co_data['Percentage_display'], _ = build_suppressed_percentage_columns(
                co_data['Percentage'], count_display_values=co_data['Count_formatted'], decimals=1
            )
            co_data['Cooccurrence_line'] = co_data['Percentage_display'].apply(
                lambda pct: f"Co-occurrence: {pct}" if pd.notna(pct) and str(pct).strip() else "Co-occurrence: Suppressed"
            )
            co_data['label'] = co_data.apply(
                lambda row: f"{row['Percentage_display']} (n={row['Count_formatted']})" if pd.notna(row['Percentage_display']) and str(row['Percentage_display']).strip() else row['Count_formatted'] if not is_mobile else (row['Percentage_display'] if pd.notna(row['Percentage_display']) and str(row['Percentage_display']).strip() else ""),
                axis=1
            )
            
            bar_fig = px.bar(
                co_data, x='Primary', y='Plot_Percentage', color='Also Found', barmode='group',
                labels={'Plot_Percentage': 'Co-occurrence percentage', 'Primary': 'Primary Substance'},
                hover_data={'Count': False, 'Total': False, 'label': False},
                custom_data=['Count_formatted', 'Total_formatted', 'Cooccurrence_line', 'Also Found']
            )
            bar_fig.update_traces(
                textposition='none', text=None, textangle=0,
                hovertemplate='<b>%{customdata[3]}</b><br>Primary: %{x}<br>%{customdata[2]}<br>Count: %{customdata[0]}<br>Total: %{customdata[1]}<extra></extra>',
                cliponaxis=False
            )
        
        x_angle = 45 if not selected_values else (45 if is_mobile else 0)
        bar_fig.update_layout(width=plot_width, autosize=False if is_mobile else True)
        bar_fig.update_xaxes(tickangle=x_angle)

        if not selected_values:
            # Keep legend on top, but below the title/subtitle block.
            bar_fig.update_layout(legend=dict(orientation="h", yanchor="top", y=1.0, xanchor="center", x=0.5))

        chart_height = compute_adaptive_horizontal_bar_height(len(co_data), min_height=260, max_height=500)
        apply_standard_bar_layout(
            bar_fig,
            height=chart_height,
            title="Co-occurrence by Selected Substance",
        )

    if not bar_caption:
        bar_caption = "Grouped bar chart showing co-occurrence percentages between substances in the selected cohort."
    filter_context = _get_active_filters_from_ctx()
    bar_title_text = (
        "Co-occurrence by Selected Substance"
        + f"{filter_context}"
        + f"<br><span style='font-size:{12 if is_mobile else 13}px;color:#5f6b76'>{bar_caption}</span>"
    )

    bar_fig.update_layout(
        title=dict(
            text=bar_title_text,
            font=dict(size=18, color="#1f2d3d"),
            x=0.5,
            xanchor="center",
        ),
        margin=dict(t=title_top_margin(bar_title_text)),
    )


    # ---------------------------------------------------------
    # 3. Sunburst Generation
    # ---------------------------------------------------------
    if not {"record_id", "substance"}.issubset(df_raw.columns):
        sunburst_fig = go.Figure().add_annotation(text="No data available", showarrow=False)
    else:
        dff_sun = df_raw.copy()
        if "age_group" in dff_sun.columns: dff_sun = apply_filter(dff_sun, "age_group", age)
        if "sex" in dff_sun.columns:       dff_sun = apply_filter(dff_sun, "sex", sex)
        if "county" in dff_sun.columns:    dff_sun = apply_county_filter(dff_sun, county).copy()
        if "year" in dff_sun.columns:      dff_sun = apply_year_filter(dff_sun, "year", year)
        if "race_ethnicity" in dff_sun.columns: dff_sun = apply_filter(dff_sun, "race_ethnicity", race_ethnicity)
        if "hawaii_residency" in dff_sun.columns: dff_sun = apply_filter(dff_sun, "hawaii_residency", hawaii_residency)

        if selected_values:
            dff_sun = records_matching_all_selected_substances(dff_sun, selected_values)

        if dff_sun.empty:
            sunburst_fig = go.Figure().add_annotation(text="No data matching filters", showarrow=False)
        else:
            if selected_values:
                selected_label = selected_values[0] if len(selected_values) == 1 else format_display_list(selected_values)
                selected_label_wrapped = wrap_axis_label(selected_label, max_len=28)
                selected_set = {str(v) for v in selected_values}

                cohort_records = dff_sun.drop_duplicates(subset=["record_id", "substance"])
                outer_counts = cohort_records.groupby("substance")["record_id"].nunique().sort_values(ascending=False)
                outer_counts = outer_counts[~outer_counts.index.astype(str).isin(selected_set)]

                root_value = float(outer_counts.sum())
                if outer_counts.empty or root_value <= 0:
                    sunburst_fig = go.Figure().add_annotation(text="No co-occurrence data available", showarrow=False)
                else:
                    ids, labels, parents, values = ["root"], [selected_label_wrapped], [""], [root_value]
                    customdata = [[int(dff_sun["record_id"].nunique()), selected_label, selected_label]]

                    def compact_label(value: str, max_chars: int = 12) -> str:
                        text = str(value).strip()
                        return text if len(text) <= max_chars else text[: max_chars - 3].rstrip() + "..."

                    for substance_key, raw_count in outer_counts.items():
                        scaled_value = float(raw_count)
                        ids.append(f"sub::{substance_key}")
                        show_label = (scaled_value / root_value) >= 0.04 if root_value else False
                        label_text = substance_key if show_label else compact_label(substance_key)
                        labels.append(wrap_axis_label(label_text, max_len=20))
                        parents.append("root")
                        values.append(scaled_value)
                        customdata.append([int(raw_count), selected_label, str(substance_key)])

                    sunburst_fig = go.Figure(go.Sunburst(
                        ids=ids, labels=labels, parents=parents, values=values, customdata=customdata,
                        branchvalues="total", insidetextorientation="horizontal",
                        hovertemplate="<b>%{customdata[2]}</b><br>Raw Count: %{customdata[0]:,}<br>Cohort: %{customdata[1]}<extra></extra>",
                    ))
                    apply_standard_non_axis_layout(sunburst_fig, title="Substance Co-occurrence Sunburst")
                    sunburst_fig.update_layout(uniformtext_minsize=8, uniformtext_mode="show")
            else:
                sunburst_data = build_sunburst_cooccurrence_data(dff_sun)
                if sunburst_data.empty:
                    sunburst_fig = go.Figure().add_annotation(text="No co-occurrence data available", showarrow=False)
                else:
                    pair_counts = sunburst_data.groupby(["Primary", "Also Found"])["record_id"].nunique().reset_index(name="Count")
                    primary_totals = dff_sun.groupby("substance")["record_id"].nunique().reset_index(name="Count")
                    
                    ids, labels, parents, values, customdata = [], [], [], [], []
                    primary_total_map = dict(zip(primary_totals["substance"], primary_totals["Count"]))

                    for _, row in primary_totals.iterrows():
                        substance_key, total = row["substance"], float(row["Count"])
                        ids.append(f"sub::{substance_key}")
                        labels.append(substance_key)
                        parents.append("")
                        values.append(total)
                        customdata.append([int(total), substance_key])

                    for primary_key, sub_df in pair_counts.groupby("Primary"):
                        parent_total = float(primary_total_map.get(primary_key, 0))
                        raw_sum = float(sub_df["Count"].sum())
                        if parent_total > 0 and raw_sum > 0:
                            for _, row in sub_df.iterrows():
                                also_found, raw_count = row["Also Found"], float(row["Count"])
                                ids.append(f"pair::{primary_key}::{also_found}")
                                labels.append(also_found)
                                parents.append(f"sub::{primary_key}")
                                values.append(parent_total * (raw_count / raw_sum))
                                customdata.append([int(raw_count), primary_key])

                    sunburst_fig = go.Figure(go.Sunburst(
                        ids=ids, labels=labels, parents=parents, values=values, customdata=customdata,
                        branchvalues="total",
                        hovertemplate="<b>%{label}</b><br>Raw Count: %{customdata[0]:,}<br>Primary: %{customdata[1]}<extra></extra>",
                    ))
                    apply_standard_non_axis_layout(sunburst_fig, title="Substance Co-occurrence Sunburst")
                    sunburst_fig.update_layout(uniformtext_minsize=8, uniformtext_mode="show")


    return heatmap_fig, bar_fig, bar_caption, sunburst_fig