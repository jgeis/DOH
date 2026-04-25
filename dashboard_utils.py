# dashboard_utils.py — Shared utilities for dashboards

import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dcc
from theme import register_template

# This applies our custom Plotly theme (colors, fonts, etc.)
register_template()


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


def sort_opts(series):
    """
    Turn a column into a sorted list of unique values.

    We also make sure "Unknown" always shows up at the end of the list
    so the drop-down menus look cleaner.
    """
    vals = pd.Series(series.unique()).astype(str)
    vals = sorted([v for v in vals if v != "Unknown"]) + (["Unknown"] if "Unknown" in vals.values else [])
    return vals


def opts_list(values):
    """
    Turn a simple list of values into the format Dash expects for
    drop-down choices (label + value).
    """
    return [{"label": v, "value": v} for v in values]


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


def make_kpi_card(label: str, count_id: str | None = None, count: int | None = None) -> dbc.Card:
    """
    Build the standard big green KPI card shown at the top-left of every page.

    Use `count_id` when the number is updated dynamically by a Dash callback
    (the callback should target that element ID). Use `count` for a pre-computed
    static total that never changes with filters.

    Args:
        label:    Descriptive text shown beneath the number (e.g. "Number of Discharges").
        count_id: HTML id for the <h2> element so a callback can update it at runtime.
        count:    Static integer to display directly in the card (formatted with commas).
    """
    if count_id is not None:
        value_el = html.H2(id=count_id, className="text-white")
    else:
        value_el = html.H2(f"{count:,}" if count is not None else "—", className="text-white")
    return dbc.Card(
        dbc.CardBody([
            value_el,
            html.Small(label, className="card-title text-white"),
        ]),
        className="bg-success text-center mb-4",
    )


def make_sidebar_helper_text(text: str | list[str] | tuple[str, ...]) -> html.Div:
    """
    Build the standardized helper text block shown under the filters card.

    Accepts either one string or multiple strings. Multiple strings are
    rendered as separate paragraphs with compact spacing.
    """
    lines = [text] if isinstance(text, str) else list(text)
    return html.Div(
        [
            html.P(line, className=("mb-0" if i == len(lines) - 1 else "mb-2"))
            for i, line in enumerate(lines)
        ],
        className="mt-3 text-muted small",
    )


def make_left_sidebar(
    kpi_card_component,
    reset_filters_button,
    filters_card,
    helper_text: str | list[str] | tuple[str, ...] | None = None,
    xs: int = 12,
    md: int = 3,
) -> dbc.Col:
    """
    Build the standardized left sidebar column used by dashboards.

    Order is always:
      1) KPI card
      2) Reset button
      3) Filters card
      4) Optional helper text block
    """
    children = [kpi_card_component, reset_filters_button, filters_card]
    if helper_text:
        if isinstance(helper_text, (str, list, tuple)):
            children.append(make_sidebar_helper_text(helper_text))
        else:
            children.append(helper_text)
    return dbc.Col(children, xs=xs, md=md)
