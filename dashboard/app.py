import os
import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html

app = Dash(
    __name__,
    use_pages=True,
    title="Barbechli Scraper Dashboard",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)
server = app.server

# sidebar
sidebar = html.Div(
    [
        dbc.Row(
            [html.Img(src="assets/logos/barbechli-logo.svg", style={"height": "35px"})],
            className="sidebar-logo",
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink(
                    "Brand Insights", href="/brands_overview", active="exact"
                ),
                dbc.NavLink(
                    "Store Insights",href="/store_overview",active="exact",
                ),
                dbc.NavLink(
                    "Price Evolution Insights", href="/price_overview", active="exact"
                ),
                dbc.NavLink(
                    "Engagement insights", href="/engagement_overview", active="exact"
                ),
            ],
            vertical=True,
            pills=True,
        ),
        html.Div(
            [
                html.Span("Created by "),
                html.A(
                    "Yassine Mhirsi",
                    href="https://github.com/Yassine-Mhirsi",
                    target="_blank",
                ),
                html.Span(" & "),
                html.A(
                    "Nour Smiai",
                    href="https://github.com/S01Nour",
                    target="_blank",
                ),
                html.Br(),
                html.Span("Code Source "),
                html.A(
                    "Barbechli Scraper",
                    href="https://github.com/Yassine-Mhirsi/barbechli-scraper",
                    target="_blank",
                ),
            ],
            className="subtitle-sidebar",
            style={"position": "absolute", "bottom": "10px", "width": "100%"},
        ),
    ],
    className="sidebar",
)


content = html.Div(
    className="page-content",
)

# defining font-awesome (icons) and fonts
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        {%css%}
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <link rel="icon" href="/assets/logos/favicon.svg" type="image/x-icon">
    </head>
    <body>
        {%app_entry%}
        {%config%}
        {%scripts%}
        {%renderer%}
    </body>
</html>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap');
</style>
"""

# layout
app.layout = html.Div(
    [
        dcc.Location(id="url", pathname="/brands_overview"),
        sidebar,
        content,
        dash.page_container,
    ]
)
if __name__ == "__main__":
    # Get port from environment variable or default to 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)