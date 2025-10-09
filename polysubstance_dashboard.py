# polysubstance_dashboard_db.py  — pure layout + callbacks
import sqlite3
from pathlib import Path

import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.io as pio

from theme import register_template
register_template()  # sets your Plotly template globally

DB_PATH = "discharges.db"
QUERIES_PATH = "queries.sql"
PREFERRED_QUERY = "load_polysubstance_data"   # polysubstance-only block
FALLBACK_QUERY  = "load_main_data"            # fallback

# ---------- SQL loader ----------
def load_sql_query(name: str, path: str = QUERIES_PATH) -> str:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
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
    raise KeyError(f"Named query '{name}' not found in {path}.")

# ---------- DB → DataFrame ----------
def load_df():
    try:
        sql = load_sql_query(PREFERRED_QUERY, QUERIES_PATH)
        print(f"[load_df] Using query: {PREFERRED_QUERY}")
    except KeyError:
        sql = load_sql_query(FALLBACK_QUERY, QUERIES_PATH)
        print(f"[load_df] Using query: {FALLBACK_QUERY}")

    with sqlite3.connect(DB_PATH) as con:
        df = pd.read_sql_query(sql, con)

    if df.empty:
        raise RuntimeError("Query returned 0 rows. Check DB and queries.sql.")

    want_obj = ["county", "region", "residency", "age_group", "sex", "substance"]
    for c in want_obj:
        if c in df.columns:
            df[c] = (
                df[c].astype(str).str.strip()
                .replace({"nan": np.nan, "None": np.nan})
                .fillna("Unknown")
            )

    if "calendar_year" in df.columns:
        df["calendar_year"] = pd.to_numeric(df["calendar_year"], errors="coerce").astype("Int64")

    print(f"[load_df] rows={len(df):,}  cols={list(df.columns)}")
    print("Plotly default template:", pio.templates.default)
    return df

df_raw = load_df()
print("[debug] queries.sql path:", Path(QUERIES_PATH).resolve())

# Guard rails: years + no unknown age
if "calendar_year" in df_raw.columns:
    df_raw["calendar_year"] = pd.to_numeric(df_raw["calendar_year"], errors="coerce").astype("Int64")
    mask_year = df_raw["calendar_year"].between(2018, 2024, inclusive="both")
else:
    mask_year = True

def _is_unknown_age(val):
    s = (str(val) if val is not None else "").strip().lower()
    return s in {"", "unknown", "unk", "n/a", "na"}

mask_age = ~df_raw["age_group"].apply(_is_unknown_age) if "age_group" in df_raw.columns else True
df_raw = df_raw[mask_year & mask_age].copy()

# ---------- filter options ----------
def sort_opts(series):
    vals = pd.Series(series.unique()).astype(str)
    return sorted([v for v in vals if v != "Unknown"]) + (["Unknown"] if "Unknown" in vals.values else [])

substance_opts = sort_opts(df_raw["substance"]) if "substance" in df_raw.columns else []
county_opts    = sort_opts(df_raw["county"])    if "county"    in df_raw.columns else []
age_opts       = sort_opts(df_raw["age_group"]) if "age_group" in df_raw.columns else []
sex_opts       = sort_opts(df_raw["sex"])       if "sex"       in df_raw.columns else []
year_opts      = sorted(df_raw["calendar_year"].dropna().unique().tolist()) if "calendar_year" in df_raw.columns else []

kpi_total = df_raw["record_id"].nunique() if "record_id" in df_raw.columns else 0

# ---------- exported layout ----------
layout = dbc.Container([
    html.H2("Polysubstance Discharges — Exploratory View (2018–2024)",
            className="text-white bg-dark p-3 text-center mb-4"),

    dbc.Row([
        # LEFT: KPI + filters
        dbc.Col([
            dbc.Card(dbc.CardBody([
                html.H1(f"{kpi_total:,}", className="m-0"),
                html.Div("2018–2024: Number of Discharges Related to Polysubstance Use",
                         className="text-white-50"),
            ]), className="bg-success text-center mb-3"),

            dbc.Button("Reset All Filters", id="reset-btn", className="mb-3", color="secondary"),

            html.Div("Substance Type", className="fw-bold mb-1"),
            dcc.Dropdown(substance_opts, id="f-substance", placeholder="All", className="mb-3"),

            html.Div("Age Group", className="fw-bold mb-1"),
            dcc.Dropdown(age_opts, id="f-age", placeholder="All", className="mb-3"),

            html.Div("Sex", className="fw-bold mb-1"),
            dcc.Dropdown(sex_opts, id="f-sex", placeholder="All", className="mb-3"),

            html.Div("County", className="fw-bold mb-1"),
            dcc.Dropdown(county_opts, id="f-county", placeholder="All", className="mb-3"),

            html.Div("Calendar Year", className="fw-bold mb-1"),
            dcc.Dropdown(year_opts, id="f-year", placeholder="All", className="mb-3"),
        ], width=3),

        # MIDDLE: main visuals
        dbc.Col([
            dcc.Graph(id="bar-top-substances", className="mb-4", style={"height": "400px"}),
            dcc.Graph(id="stack-year-county", style={"height": "360px"}),
        ], width=6),

        # RIGHT: county treemap + small tables
        dbc.Col([
            dcc.Graph(id="treemap-county", className="mb-3", style={"height": "280px"}),
            html.H5("Age Group", className="mb-2"),
            html.Div(id="tbl-age", className="mb-3"),
            html.H5("Sex", className="mb-2"),
            html.Div(id="tbl-sex"),
        ], width=3),
    ])
], fluid=True)

# ---------- callbacks (app-agnostic) ----------
@callback(
    Output("bar-top-substances", "figure"),
    Output("stack-year-county", "figure"),
    Output("treemap-county", "figure"),
    Output("tbl-age", "children"),
    Output("tbl-sex", "children"),
    Input("f-substance", "value"),
    Input("f-age", "value"),
    Input("f-sex", "value"),
    Input("f-county", "value"),
    Input("f-year", "value"),
    Input("reset-btn", "n_clicks"),
    prevent_initial_call=False
)
def update(substance, age, sex, county, year, _):
    dff = df_raw.copy()

    if substance: dff = dff[dff["substance"] == substance]
    if age:       dff = dff[dff["age_group"] == age]
    if sex:       dff = dff[dff["sex"] == sex]
    if county:    dff = dff[dff["county"] == county]
    if year:      dff = dff[dff["calendar_year"] == year]

    # Bar: Top substances
    if {"substance", "record_id"}.issubset(dff.columns) and not dff.empty:
        sub_counts = (
            dff.groupby("substance")["record_id"]
               .nunique().reset_index(name="discharges")
               .sort_values("discharges", ascending=True)
               .tail(10)
        )
        fig_sub = px.bar(
            sub_counts, x="discharges", y="substance", orientation="h",
            title="Top Substances (Polysubstance Records)",
            labels={"discharges": "Number of Discharges", "substance": "Substance Type"},
            text="discharges",
        )
        fig_sub.update_traces(texttemplate="%{text:,}", textposition="outside", cliponaxis=False)
        max_x = int(sub_counts["discharges"].max()) if not sub_counts.empty else 0
        fig_sub.update_layout(
            margin=dict(l=0, r=20, t=40, b=0),
            xaxis=dict(range=[0, max_x * 1.15 if max_x else 1], automargin=True),
            yaxis=dict(automargin=True),
        )
    else:
        fig_sub = px.bar(title="Top Substances (no data)")

    # Stacked Bar: Year × County
    if {"calendar_year", "county", "record_id"}.issubset(dff.columns) and not dff.empty:
        yearly_counts = (
            dff.drop_duplicates("record_id")
               .groupby(["calendar_year", "county"])["record_id"]
               .nunique().reset_index(name="discharges")
        )
        yearly_counts["label"] = yearly_counts["discharges"].map(lambda x: f"{int(x):,}")

        fig_year_county = px.bar(
            yearly_counts, x="calendar_year", y="discharges", color="county",
            barmode="stack",
            labels={"calendar_year": "Year", "discharges": "Discharges"},
            title="Discharges by Year and County",
            text="label",
        )
        fig_year_county.update_layout(
            margin=dict(l=0, r=20, t=40, b=0),
            xaxis=dict(dtick=1, automargin=True),
            uniformtext_minsize=12, uniformtext_mode="show",
        )
        fig_year_county.update_traces(textposition="inside", insidetextanchor="middle",
                                      cliponaxis=False, textfont_size=12)

        # Add centered labels for Kauai slice
        pivot = yearly_counts.pivot(index="calendar_year", columns="county", values="discharges").fillna(0)
        name_hawaii  = "Hawaii" if "Hawaii" in pivot.columns else None
        name_hon     = "Honolulu" if "Honolulu" in pivot.columns else None
        name_kauai   = "Kauai" if "Kauai" in pivot.columns else ("Kauaʻi" if "Kauaʻi" in pivot.columns else None)

        annotations = list(fig_year_county.layout.annotations) if fig_year_county.layout.annotations else []
        if name_kauai:
            for yr in pivot.index:
                haw = float(pivot.at[yr, name_hawaii]) if name_hawaii else 0.0
                hon = float(pivot.at[yr, name_hon]) if name_hon else 0.0
                kau = float(pivot.at[yr, name_kauai])
                if kau <= 0: 
                    continue
                y_mid = haw + hon + (kau / 2.0)
                annotations.append(dict(
                    x=yr, y=y_mid, text=f"{int(kau):,}",
                    showarrow=False, font=dict(size=13, color="black"),
                    xanchor="center", yanchor="middle"
                ))
        fig_year_county.update_layout(annotations=annotations)
    else:
        fig_year_county = px.bar(title="Discharges by Year and County (no data)")

    # Treemap: county share
    uniq = dff.drop_duplicates("record_id")
    if {"county", "record_id"}.issubset(uniq.columns) and not uniq.empty:
        county_counts = uniq.groupby("county")["record_id"].nunique().reset_index(name="discharges")
        fig_tree = px.treemap(county_counts, path=["county"], values="discharges",
                              title="County Share (Unique Discharges)")
        fig_tree.update_traces(
            texttemplate="%{label}<br>%{value:,}",
            hovertemplate="%{label}: %{value:,} (%{percentRoot:.1%})<extra></extra>"
        )
        fig_tree.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    else:
        fig_tree = px.treemap(title="County Share (no data)")

    # Tables
    def simple_table(df, col, ordered=None):
        if col not in df.columns or df.empty:
            return dbc.Alert(f"No data for '{col}'.", color="warning", className="mb-0")
        g = df.groupby(col)["record_id"].nunique().reset_index(name="discharges")
        if ordered:
            g[col] = pd.Categorical(g[col], categories=ordered, ordered=True)
            g = g.sort_values(col)
        g["discharges"] = g["discharges"].map(lambda x: f"{int(x):,}")
        return dbc.Table.from_dataframe(g, striped=True, bordered=True, hover=True, size="sm")

    tbl_age = simple_table(uniq, "age_group", ["<18", "18-44", "45-64", "65-74", "75+"])
    tbl_sex = simple_table(uniq, "sex")

    return fig_sub, fig_year_county, fig_tree, tbl_age, tbl_sex
