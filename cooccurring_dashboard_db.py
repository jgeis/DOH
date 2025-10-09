# cooccurring_dashboard_db.py
# Co-occurring SUD (primary) + MH (secondary) dashboard
# - Uses queries.sql block: -- name: load_sud_primary_mh_secondary_v2
# - If no MH table/column is present, it patches mh_union to 'Unknown' and LEFT JOINs it.

import re
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
import plotly.express as px

from theme import register_template
register_template()

DB_PATH = "discharges.db"
QUERIES_PATH = "queries.sql"
QUERY_NAME = "load_sud_primary_mh_secondary_v2"  # <-- your block name

# Try to auto-detect a mental-health column/table if present
CANDIDATE_MH_COLS = [
    "mh_diagnosis", "mh_dx", "mental_health_diagnosis",
    "mental_health", "mh", "mh_condition", "mh_diag"
]
CANDIDATE_MH_TABLES = ["mh_diagnoses", "demographics", "diagnoses", "conditions", "mental_health", "dx_mh", "mh"]

# ---------- DB introspection ----------
def list_tables(con): 
    return [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]

def list_columns(con, table):
    try:
        return [r[1] for r in con.execute(f"PRAGMA table_info({table})")]
    except Exception:
        return []

def find_mh_source(con):
    """Return (table, col) if any MH column exists; else (None, None)."""
    tables = list_tables(con)
    ordered = [t for t in CANDIDATE_MH_TABLES if t in tables] + [t for t in tables if t not in CANDIDATE_MH_TABLES]
    for t in ordered:
        cols = list_columns(con, t)
        for c in CANDIDATE_MH_COLS:
            if c in cols:
                return t, c
    return None, None

# ---------- load named SQL ----------
def load_sql_query(name: str, path: str = QUERIES_PATH) -> str:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    for block in text.split("-- name:"):
        block = block.strip()
        if not block:
            continue
        first, *rest = block.split("\n")
        if first.strip() == name:
            return "\n".join(rest).strip()
    raise KeyError(f"Named query '{name}' not found in {path}.")

# ---------- replace the mh_union CTE cleanly ----------
# capture the full CTE including the trailing comma to avoid leftover text
MH_UNION_PATTERN_FULL = re.compile(
    r"(mh_union\s+AS\s*\(\s*)(.*?)(\s*\)\s*,)",  # prefix, body, '),'
    re.IGNORECASE | re.DOTALL
)

def _sub_mh_union_block(sql: str, new_body_sql: str) -> str:
    """Replace the entire `mh_union AS ( ... ),` block with new_body_sql."""
    m = MH_UNION_PATTERN_FULL.search(sql)
    if not m:
        # Some files may omit the trailing comma after the CTE; handle that variant too.
        alt = re.compile(r"(mh_union\s+AS\s*\(\s*)(.*?)(\s*\))", re.IGNORECASE | re.DOTALL)
        m = alt.search(sql)
        if not m:
            return sql  # can't find the block; better to leave original
        prefix, _, suffix = m.groups()
        return sql[:m.start()] + prefix + new_body_sql + suffix + sql[m.end():]

    prefix, _, suffix = m.groups()
    return sql[:m.start()] + prefix + new_body_sql + suffix + sql[m.end():]

def patch_mh_union_with_source(sql: str, table: str, col: str) -> str:
    """Point mh_union to the detected table/column."""
    new_body = f"""
      SELECT
        record_id,
        TRIM({col}) AS mh_dx,
        ''          AS mh_pos
      FROM {table}
      WHERE {col} IS NOT NULL AND TRIM({col}) <> ''
    """.strip()
    return _sub_mh_union_block(sql, new_body)

def patch_mh_union_to_unknown(sql: str) -> str:
    """Fallback: synthesize mh_union → 'Unknown' and switch JOIN to LEFT JOIN."""
    new_body = """
      SELECT
        record_id,
        'Unknown' AS mh_dx,
        ''        AS mh_pos
      FROM demographics
    """.strip()
    sql = _sub_mh_union_block(sql, new_body)
    sql = re.sub(r"\bJOIN\s+mh_union\b", "LEFT JOIN mh_union", sql, flags=re.IGNORECASE)
    return sql

# ---------- run → df ----------
REQUIRED_COLS = {
    "record_id", "substance", "mh_diagnosis",
    "county", "region", "zip", "residency",
    "age_group", "sex", "calendar_year"
}

def load_df() -> pd.DataFrame:
    base_sql = load_sql_query(QUERY_NAME, QUERIES_PATH)
    with sqlite3.connect(DB_PATH) as con:
        mh_table, mh_col = find_mh_source(con)
        if mh_table and mh_col:
            sql = patch_mh_union_with_source(base_sql, mh_table, mh_col)
            mh_source = f"{mh_table}.{mh_col}"
        else:
            sql = patch_mh_union_to_unknown(base_sql)
            mh_source = "NONE (fallback: 'Unknown')"
        df = pd.read_sql_query(sql, con)

    if df.empty:
        raise RuntimeError(f"Query '{QUERY_NAME}' returned 0 rows. MH source: {mh_source}")

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise RuntimeError("Missing columns from SQL result: " + ", ".join(missing))

    # Clean + guardrails (to mirror PB)
    for c in ["substance", "mh_diagnosis", "county", "region", "zip", "residency", "age_group", "sex"]:
        df[c] = df[c].astype(str).str.strip().replace({"nan": np.nan, "None": np.nan}).fillna("Unknown")
    df["calendar_year"] = pd.to_numeric(df["calendar_year"], errors="coerce").astype("Int64")
    df = df[df["calendar_year"].between(2018, 2024, inclusive="both")]
    df = df[df["age_group"].str.strip().str.lower().ne("unknown")]

    print(f"[cooccurring] rows={len(df):,} cols={list(df.columns)}")
    print("[cooccurring] DB:", Path(DB_PATH).resolve())
    print("[cooccurring] SQL block:", QUERY_NAME, "from", Path(QUERIES_PATH).resolve())
    print(f"[cooccurring] MH source: {mh_source}")
    return df

df_raw = load_df()

# ---------- filter options ----------
def sort_opts(s: pd.Series):
    vals = pd.Series(s.unique()).astype(str)
    core = sorted([v for v in vals if v not in ("Unknown", "")])
    return core + (["Unknown"] if "Unknown" in vals.values else [])

year_opts      = sorted(df_raw["calendar_year"].dropna().unique().tolist())
substance_opts = sort_opts(df_raw["substance"])
mh_opts        = sort_opts(df_raw["mh_diagnosis"])
county_opts    = sort_opts(df_raw["county"])
age_opts       = sort_opts(df_raw["age_group"])
sex_opts       = sort_opts(df_raw["sex"])
kpi_total      = df_raw["record_id"].nunique()

# ---------- layout (module style for multi-dashboard) ----------
layout = dbc.Container([
    html.H2("Co-occurring: Substance Use × Mental Health (2018–2024)",
            className="text-white bg-dark p-3 text-center mb-4"),
    dbc.Row([
        dbc.Col([
            dbc.Card(dbc.CardBody([
                html.Div("Unique discharges with SUD + MH", className="text-white-50"),
                html.H1(f"{kpi_total:,}", className="m-0"),
            ]), className="bg-success text-center mb-3"),

            dbc.Button("Reset Filters", id="btn-reset-co", className="mb-3", color="secondary"),

            html.Div("Substance", className="fw-bold mb-1"),
            dcc.Dropdown(substance_opts, id="co-f-substance", placeholder="All", className="mb-2"),

            html.Div("Mental Health Dx", className="fw-bold mb-1"),
            dcc.Dropdown(mh_opts, id="co-f-mh", placeholder="All", className="mb-2"),

            html.Div("Age Group", className="fw-bold mb-1"),
            dcc.Dropdown(age_opts, id="co-f-age", placeholder="All", className="mb-2"),

            html.Div("Sex", className="fw-bold mb-1"),
            dcc.Dropdown(sex_opts, id="co-f-sex", placeholder="All", className="mb-2"),

            html.Div("County", className="fw-bold mb-1"),
            dcc.Dropdown(county_opts, id="co-f-county", placeholder="All", className="mb-2"),

            html.Div("Year", className="fw-bold mb-1"),
            dcc.Dropdown(year_opts, id="co-f-year", placeholder="All"),
        ], width=3),

        dbc.Col([
            dcc.Graph(id="co-heat-sud-mh", className="mb-4", style={"height": "400px"}),
            dcc.Graph(id="co-year-county", style={"height": "360px"}),
        ], width=6),

        dbc.Col([
            html.H5("Top Mental Health Dx", className="mb-2"),
            html.Div(id="co-tbl-mh", className="mb-3"),
            html.H5("Top Substances", className="mb-2"),
            html.Div(id="co-tbl-sud"),
        ], width=3),
    ])
], fluid=True)

# ---------- callbacks ----------
@callback(
    Output("co-heat-sud-mh", "figure"),
    Output("co-year-county", "figure"),
    Output("co-tbl-mh", "children"),
    Output("co-tbl-sud", "children"),
    Input("co-f-substance", "value"),
    Input("co-f-mh", "value"),
    Input("co-f-age", "value"),
    Input("co-f-sex", "value"),
    Input("co-f-county", "value"),
    Input("co-f-year", "value"),
    Input("btn-reset-co", "n_clicks"),
    prevent_initial_call=False
)
def update(substance, mh_dx, age, sex, county, year, _):
    dff = df_raw.copy()
    if substance: dff = dff[dff["substance"] == substance]
    if mh_dx:     dff = dff[dff["mh_diagnosis"] == mh_dx]
    if age:       dff = dff[dff["age_group"] == age]
    if sex:       dff = dff[dff["sex"] == sex]
    if county:    dff = dff[dff["county"] == county]
    if year:      dff = dff[dff["calendar_year"] == year]

    uniq = dff.drop_duplicates("record_id")

    # Heatmap: Substance × MH (limit to top categories for readability)
    if {"substance", "mh_diagnosis"}.issubset(uniq.columns) and not uniq.empty:
        mat = uniq.groupby(["mh_diagnosis", "substance"])["record_id"].nunique().reset_index(name="discharges")
        top_mh  = uniq.groupby("mh_diagnosis")["record_id"].nunique().sort_values(ascending=False).head(12).index.tolist()
        top_sud = uniq.groupby("substance")["record_id"].nunique().sort_values(ascending=False).head(12).index.tolist()
        mat = mat[mat["mh_diagnosis"].isin(top_mh) & mat["substance"].isin(top_sud)]
        heat = px.density_heatmap(
            mat, x="substance", y="mh_diagnosis", z="discharges",
            histfunc="avg", color_continuous_scale="Viridis",
            title="Co-occurring: Substance × Mental Health (Top categories)"
        )
        heat.update_layout(margin=dict(l=0, r=10, t=50, b=0))
    else:
        heat = px.imshow([[0]], labels=dict(x="Substance", y="MH Dx", color="Discharges"),
                         title="Co-occurring: Substance × Mental Health (no data)")

    # Stacked bar: Year × County
    if {"calendar_year", "county"}.issubset(uniq.columns) and not uniq.empty:
        by_yr = uniq.groupby(["calendar_year", "county"])["record_id"].nunique().reset_index(name="discharges")
        fig_year_c = px.bar(
            by_yr, x="calendar_year", y="discharges", color="county",
            barmode="stack", title="Discharges by Year and County (co-occurring)",
            labels={"calendar_year": "Year", "discharges": "Discharges"},
            text=by_yr["discharges"].map(lambda x: f"{int(x):,}")
        )
        fig_year_c.update_traces(textposition="inside", insidetextanchor="middle", cliponaxis=False)
        fig_year_c.update_layout(margin=dict(l=0, r=0, t=50, b=0), xaxis=dict(dtick=1))
    else:
        fig_year_c = px.bar(title="Discharges by Year and County (no data)")

    # Small tables
    def small_table(frame, col):
        if col not in frame.columns or frame.empty:
            return dbc.Alert(f"No data for '{col}'.", color="warning", className="mb-0")
        g = frame.groupby(col)["record_id"].nunique().reset_index(name="discharges")
        g["discharges"] = g["discharges"].map(lambda x: f"{int(x):,}")
        return dbc.Table.from_dataframe(
            g.sort_values("discharges", ascending=False).head(12),
            striped=True, bordered=True, hover=True, size="sm"
        )

    return heat, fig_year_c, small_table(uniq, "mh_diagnosis"), small_table(uniq, "substance")
