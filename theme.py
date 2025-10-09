import plotly.io as pio

DEFAULTS = {
    # ---- Fonts & Text ----
    "font_family": "Inter, Segoe UI, Arial, sans-serif",
    "font_size": 13,
    "text_color": "#222222",    # axis labels & tick text
    "title_color": "#111111",   # chart titles

    # ---- Background Colors ----
    "paper_bg": "#F4F5F7",      # dashboard background (soft gray)
    "plot_bg":  "#FFFFFF",      # chart area background (white)

    # ---- Balanced, modern color palette ----
    # These complement Bootstrap greens/blues and look professional in both light and dark text.
    "colorway": [
        "#20639B",  # deep blue (primary)
        "#3CAEA3",  # teal
        "#F6D55C",  # gold / yellow accent
        "#ED553B",  # coral red
        "#173F5F",  # navy blue
        "#57A773",  # medium green
        "#4E89AE",  # steel blue
        "#FF9F1C",  # orange accent
        "#B8DE6F",  # lime green (highlight)
        "#9B59B6",  # purple accent
    ],
}

def build_template(cfg: dict | None = None) -> dict:
    """Return a Plotly template dict using DEFAULTS merged with cfg."""
    cfg = {**DEFAULTS, **(cfg or {})}
    return {
        "layout": {
            "font": {
                "family": cfg["font_family"],
                "size": cfg["font_size"],
                "color": cfg["text_color"]
            },
            "title": {
                "font": {"size": cfg["font_size"] + 5, "color": cfg["title_color"]},
                "x": 0.5, "xanchor": "center"
            },
            "paper_bgcolor": cfg["paper_bg"],
            "plot_bgcolor": cfg["plot_bg"],
            "colorway": cfg["colorway"],

            # ---- Axis Grid and Layout ----
            "xaxis": {
                "gridcolor": "#E0E0E0",
                "zerolinecolor": "#E0E0E0",
                "title": {"standoff": 8},
                "automargin": True
            },
            "yaxis": {
                "gridcolor": "#E0E0E0",
                "zerolinecolor": "#E0E0E0",
                "title": {"standoff": 8},
                "automargin": True
            },

            "margin": {"l": 40, "r": 20, "t": 50, "b": 40},

            # ---- Legend ----
            "legend": {
                "font": {"size": cfg["font_size"]},
                "orientation": "h",
                "yanchor": "bottom",
                "y": -0.25
            },
            "bargap": 0.25,
        }
    }

def register_template(name: str = "doh", cfg: dict | None = None, set_default: bool = True):
    """Register the theme with Plotly and optionally make it default."""
    pio.templates[name] = build_template(cfg)
    if set_default:
        pio.templates.default = name
