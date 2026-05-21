# cares_statistics_dashboard.py — Hawai'i CARES 988 Statistics page

import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.express as px

from config import USE_MSSQL
from db_utils import execute_query
from dashboard_utils import (
    load_sql_query,
    make_last_updated_block,
    apply_standard_bar_layout,
    apply_standard_line_layout,
)
from theme import register_template

register_template()


def _query_name(base_name):
    """Return DB-specific named query key for MSSQL/SQLite compatibility."""
    return base_name if USE_MSSQL else f"{base_name}_sqlite"


def _compact_tick_label(value):
    """Format numeric ticks as compact labels like 6K, 1.5M."""
    v = float(value)
    if v >= 1_000_000:
        m = v / 1_000_000
        return f"{int(m)}M" if m.is_integer() else f"{m:.1f}M"
    if v >= 1_000:
        k = v / 1_000
        return f"{int(k)}K" if k.is_integer() else f"{k:.1f}K"
    return f"{int(v)}"


def _load_top_10_reasons_table():
    sql = load_sql_query(_query_name("load_cares_calls_by_nature_top_10"))
    df = execute_query(sql)

    # Column casing can differ by backend (e.g., Nature_of_Call vs nature_of_call).
    col_lookup = {c.lower(): c for c in df.columns}
    if "nature_of_call" in col_lookup and col_lookup["nature_of_call"] != "Nature_of_Call":
        df = df.rename(columns={col_lookup["nature_of_call"]: "Nature_of_Call"})
    if "percentage_of_total" in col_lookup and col_lookup["percentage_of_total"] != "percentage_of_total":
        df = df.rename(columns={col_lookup["percentage_of_total"]: "percentage_of_total"})

    # SQL output: Nature_of_Call, percentage_of_total
    if "Nature_of_Call" in df.columns:
        df = df.rename(columns={"Nature_of_Call": "Category"})
    if "percentage_of_total" in df.columns:
        df = df.rename(columns={"percentage_of_total": "Percent"})

    if "Percent" in df.columns:
        df["Percent"] = pd.to_numeric(df["Percent"], errors="coerce").fillna(0)
        df["Percent"] = df["Percent"].map(lambda v: f"{v:.2f}%")

    keep_cols = [col for col in ["Category", "Percent"] if col in df.columns]
    return df[keep_cols]


def _load_last_updated_value():
    sql = load_sql_query(_query_name("load_cares_calls_last_updated"))
    df = execute_query(sql)
    if df.empty or "last_updated" not in df.columns:
        return None

    parsed = pd.to_datetime(df.iloc[0]["last_updated"], errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.strftime("%Y-%m-%d")


def _load_calls_line_chart():
    sql = load_sql_query(_query_name("load_cares_calls_by_line_6_months"))
    df = execute_query(sql)

    # Column casing can differ by backend (e.g., Line vs line).
    col_lookup = {c.lower(): c for c in df.columns}
    if "line" in col_lookup and col_lookup["line"] != "Line":
        df = df.rename(columns={col_lookup["line"]: "Line"})
    if "date_month" in col_lookup and col_lookup["date_month"] != "Date_Month":
        df = df.rename(columns={col_lookup["date_month"]: "Date_Month"})
    if "num_calls" in col_lookup and col_lookup["num_calls"] != "num_calls":
        df = df.rename(columns={col_lookup["num_calls"]: "num_calls"})

    # SQL output: Line, Date_Month (yyyy-MM), num_calls
    df["Date_Month"] = pd.to_datetime(df["Date_Month"], format="%Y-%m", errors="coerce")
    df = df[df["Date_Month"].notna()].copy()
    df = df.sort_values("Date_Month")
    df["Month"] = df["Date_Month"].dt.strftime("%b")

    fig = px.line(
        df,
        x="Month",
        y="num_calls",
        color="Line",
        markers=True,
        labels={
            "Month": "Month",
            "num_calls": "# of calls/chats/texts",
            "Line": "Contact Type",
        },
    )
    apply_standard_line_layout(
        fig,
        yaxis=dict(title="# of calls/chats/texts"),
        xaxis=dict(title="Month"),
        height=420,
        hovermode="x",
        legend_title_text="",
    )
    max_calls = int(pd.to_numeric(df["num_calls"], errors="coerce").fillna(0).max()) if not df.empty else 0
    if max_calls > 0:
        if max_calls <= 10_000:
            step = 1_000
        elif max_calls <= 50_000:
            step = 5_000
        else:
            step = 10_000

        upper = ((max_calls + step - 1) // step) * step
        tickvals = list(range(0, upper + step, step))
        ticktext = [_compact_tick_label(v) for v in tickvals]
        fig.update_yaxes(tickmode="array", tickvals=tickvals, ticktext=ticktext)

    fig.update_traces(hovertemplate="%{fullData.name}<br>%{x}: %{y:,}<extra></extra>")
    return fig


def _load_cmo_bar_chart():
    sql = load_sql_query(_query_name("load_crisis_mobile_outreach_6_months"))
    df = execute_query(sql)

    # SQL output: Date (yyyy-MM), num_calls
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m", errors="coerce")
    df = df[df["Date"].notna()].copy()
    df = df.sort_values("Date")
    df["Month"] = df["Date"].dt.strftime("%b")

    fig = px.bar(
        df,
        x="Month",
        y="num_calls",
        labels={
            "Month": "Month",
            "num_calls": "# of CMOs",
        },
        text="num_calls",
    )
    apply_standard_bar_layout(
        fig,
        yaxis=dict(title="# of CMOs"),
        xaxis=dict(title="Month"),
        height=420,
    )
    fig.update_traces(
        marker_color="#22767C",
        texttemplate="%{text:,}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{x}: %{y:,}<extra></extra>",
    )
    return fig


def layout():
    try:
        top_10_df = _load_top_10_reasons_table()
        last_updated_value = _load_last_updated_value()
        calls_line_fig = _load_calls_line_chart()
        cmo_bar_fig = _load_cmo_bar_chart()
    except Exception as exc:
        return dbc.Container(
            dbc.Alert(
                f"Unable to load CARES statistics data in the current database mode. Details: {exc}",
                color="warning",
                className="mt-2",
            ),
            fluid=True,
        )

    table_component = dbc.Table.from_dataframe(
        top_10_df,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size="sm",
    )

    return dbc.Container(
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5("Top 10 reasons for contacting Hawai'i CARES 988", className="plot-card-header mb-2"),
                        html.Div(table_component, style={"overflowX": "auto"}),
                        html.Div(make_last_updated_block(last_updated_value), className="mt-2"),
                    ],
                    xs=12,
                    md=4,
                    className="mb-3",
                ),
                dbc.Col(
                    [
                        html.H5("Phone Call, Chat, & Text Volumes", className="plot-card-header mb-2"),
                        dcc.Graph(
                            id="cares-statistics-calls-line-chart",
                            figure=calls_line_fig,
                            config={"displayModeBar": True, "displaylogo": False},
                            style={"width": "100%", "height": "450px"},
                        ),
                    ],
                    xs=12,
                    md=4,
                    className="mb-3",
                ),
                dbc.Col(
                    [
                        html.H5("Crisis Mobile Outreach (CMO)", className="plot-card-header mb-2"),
                        dcc.Graph(
                            id="cares-statistics-cmo-bar-chart",
                            figure=cmo_bar_fig,
                            config={"displayModeBar": True, "displaylogo": False},
                            style={"width": "100%", "height": "450px"},
                        ),
                    ],
                    xs=12,
                    md=4,
                    className="mb-3",
                ),
            ],
            className="g-3",
        ),
        fluid=True,
    )
