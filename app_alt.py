# app_alt.py  — pure layout + callbacks (no Dash() here)

import sqlite3
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
import plotly.express as px
from theme import register_template

# Use global theme from theme.py
register_template()

# ----------------------------
# Helper: load a named SQL block
# ----------------------------
def load_sql_query(name, path="queries.sql"):
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
    blocks = sql.split("-- name:")
    m = {}
    for b in blocks:
        if not b.strip():
            continue
        lines = b.strip().split("\n")
        m[lines[0].strip()] = "\n".join(lines[1:]).strip()
    if name not in m:
        raise KeyError(f"Named query '{name}' not found in {path}.")
    return m[name]

# ----------------------------
# Load data from SQLite via your named query
# ----------------------------
def load_main_dataframe_from_db(db_path="discharges.db"):
    sql = load_sql_query("load_main_data")
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(sql, conn)
    finally:
        conn.close()

    if df.empty:
        raise RuntimeError("Query returned 0 rows. Check -- name: load_main_data in queries.sql")

    if "calendar_year" in df.columns:
        df["calendar_year"] = pd.to_numeric(df["calendar_year"], errors="ignore")

    for col in ["county", "region", "residency", "age_group", "sex", "substance"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")
    return df

# ----------------------------
# Data + filter options
# ----------------------------
df_raw = load_main_dataframe_from_db("discharges.db")
total_unique = df_raw["record_id"].nunique()

def sort_opts(series):
    vals = pd.Series(series.unique()).astype(str)
    vals = sorted([v for v in vals if v != "Unknown"]) + (["Unknown"] if "Unknown" in vals.values else [])
    return vals

county_opts    = sort_opts(df_raw["county"])    if "county"    in df_raw.columns else []
region_opts    = sort_opts(df_raw["region"])    if "region"    in df_raw.columns else []
residency_opts = sort_opts(df_raw["residency"]) if "residency" in df_raw.columns else []
age_opts       = sort_opts(df_raw["age_group"]) if "age_group" in df_raw.columns else []
sex_opts       = sort_opts(df_raw["sex"])       if "sex"       in df_raw.columns else []

# ----------------------------
# Layout (exported symbol)
# ----------------------------
layout = dbc.Container([
    html.H2(
        "Substance Use Emergency Discharges — Alt Views (2018–2024)",
        className="text-white bg-dark p-3 text-center mb-4"
    ),

    dbc.Row([
        # Left: KPI + Filters
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Total Discharges", className="card-title text-white"),
                    html.H2(f"{total_unique:,}", className="text-white"),
                    html.Small("Count of unique records from 2018 to 2024", className="text-white-50")
                ])
            ], className="bg-success text-center mb-4"),

            html.H5("Filter Data"),
            dcc.Dropdown(county_opts,    id="county-filter",    placeholder="County",    className="mb-2"),
            dcc.Dropdown(region_opts,    id="region-filter",    placeholder="Region",    className="mb-2"),
            dcc.Dropdown(residency_opts, id="residency-filter", placeholder="Residency", className="mb-2"),
            dcc.Dropdown(age_opts,       id="age-filter",       placeholder="Age Group", className="mb-2"),
            dcc.Dropdown(sex_opts,       id="sex-filter",       placeholder="Sex",       className="mb-4"),
        ], width=3),

        # Middle: charts
        dbc.Col([
            dcc.Graph(id="county-year-lines", className="mb-4", style={"height": "400px"}),
            dcc.Graph(id="sex-year-stacked", style={"height": "360px"})
        ], width=6),

        # Right: tables + pie
        dbc.Col([
            html.H5("By County"),
            html.Div(id="table-county", className="mb-3"),
            html.H5("By Age Group"),
            html.Div(id="table-age", className="mb-3"),
            html.H5("Gender Share"),
            dcc.Graph(id="sex-pie", style={"height": "260px"}),
        ], width=3),
    ])
], fluid=True)

# ----------------------------
# Callbacks (app-agnostic)
# ----------------------------
@callback(
    Output("county-year-lines", "figure"),
    Output("sex-year-stacked", "figure"),
    Output("table-county", "children"),
    Output("table-age", "children"),
    Output("sex-pie", "figure"),
    Input("county-filter", "value"),
    Input("region-filter", "value"),
    Input("residency-filter", "value"),
    Input("age-filter", "value"),
    Input("sex-filter", "value"),
)
def update_dashboard(county, region, residency, age, sex):
    dff = df_raw.copy()
    if county:    dff = dff[dff["county"] == county]
    if region:    dff = dff[dff["region"] == region]
    if residency: dff = dff[dff["residency"] == residency]
    if age:       dff = dff[dff["age_group"] == age]
    if sex:       dff = dff[dff["sex"] == sex]

    dff_uniq = dff.drop_duplicates(subset="record_id")

    # Line chart: County × Year
    if {"county", "calendar_year"}.issubset(dff_uniq.columns):
        by_cy = (
            dff_uniq.groupby(["calendar_year", "county"])["record_id"]
            .nunique().reset_index(name="count")
        )
        counties = sort_opts(dff_uniq["county"]) if "county" in dff_uniq.columns else []
        if counties:
            by_cy["county"] = pd.Categorical(by_cy["county"], categories=counties, ordered=True)

        line_fig = px.line(
            by_cy, x="calendar_year", y="count", color="county",
            markers=True,
            labels={"calendar_year": "Year", "count": "Discharges", "county": "County"},
            title="Discharges by County and Year"
        )
        line_fig.update_traces(hovertemplate="Year %{x}<br>%{y:,} discharges<extra></extra>")
        line_fig.update_layout(margin=dict(l=0, r=20, t=40, b=0), xaxis=dict(dtick=1))
    else:
        line_fig = px.line(title="Discharges by County and Year (data missing)")

    # Stacked bar: Yearly Discharges by Gender
    if {"calendar_year", "sex"}.issubset(dff_uniq.columns):
        by_ys = (
            dff_uniq.groupby(["calendar_year", "sex"])["record_id"]
            .nunique().reset_index(name="count")
            .sort_values(["calendar_year", "sex"])
        )
        sex_bar = px.bar(
            by_ys, x="calendar_year", y="count", color="sex", barmode="stack",
            labels={"calendar_year": "Year", "count": "Discharges", "sex": "Gender"},
            title="Yearly Discharges by Gender",
            text=by_ys["count"].map(lambda x: f"{int(x):,}")
        )
        sex_bar.update_traces(textposition="inside", insidetextanchor="middle", cliponaxis=False)
        totals = by_ys.groupby("calendar_year")["count"].sum().reset_index()
        for _, row in totals.iterrows():
            sex_bar.add_annotation(
                x=row["calendar_year"], y=row["count"],
                text=f"{int(row['count']):,}", showarrow=False, yshift=10, font=dict(size=12)
            )
        max_y = int(totals["count"].max()) if not totals.empty else 0
        sex_bar.update_layout(margin=dict(l=0, r=0, t=40, b=0),
                              xaxis=dict(automargin=True),
                              yaxis=dict(range=[0, max_y * 1.15 if max_y else 1]))
    else:
        sex_bar = px.bar(title="Yearly Discharges by Gender (data missing)")

    # Tables
    def generate_table(column, categories=None):
        if column not in dff_uniq.columns:
            return dbc.Alert(f"Column '{column}' not found in data.", color="warning", className="mb-0")
        grouped = dff_uniq.groupby(column)["record_id"].nunique().reset_index()
        grouped.columns = [column, "count"]
        if categories:
            grouped[column] = pd.Categorical(grouped[column], categories=categories, ordered=True)
            grouped = grouped.sort_values(column)
        grouped["count"] = grouped["count"].map(lambda x: f"{int(x):,}")
        return dbc.Table.from_dataframe(grouped, striped=True, bordered=True, hover=True)

    # Pie: Gender share
    if "sex" in dff_uniq.columns:
        pie_df = (
            dff_uniq.groupby("sex")["record_id"]
            .nunique().reset_index(name="count")
            .sort_values("count", ascending=False)
        )
        sex_pie = px.pie(pie_df, names="sex", values="count", title="Discharges by Gender", hole=0.35)
        sex_pie.update_traces(
            textposition="inside",
            texttemplate="%{label}<br>%{percent:.1%} (%{value:,})",
            hovertemplate="%{label}: %{value:,} (%{percent:.1%})"
        )
        sex_pie.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    else:
        sex_pie = px.pie(title="Discharges by Gender (data missing)")

    return (
        line_fig,
        sex_bar,
        generate_table("county"),
        generate_table("age_group", ["<18", "18-44", "45-64", "65-74", "75+", "Unknown"]),
        sex_pie,
    )
