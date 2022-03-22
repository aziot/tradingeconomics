import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, callback, dcc, html, no_update
from plotly.subplots import make_subplots

import tradingeconomics as te

# Constants
COUNTRIES = [
    "Brazil",
    "China",
    "France",
    "Germany",
    "Greece",
    "India",
    "Nigeria",
    "South Africa",
    "South Korea",
    "Switzerland",
    "United Kingdom",
    "United States",
]

# Initialization
te.login()

app = Dash(
    __name__,
    title="Credit rating vs. GDP",
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    serve_locally=False,
)


# Utility functions
def get_gdp_data(country="United States"):
    """TODO(aziot)"""
    if not country:
        return None
    df = te.getHistoricalData(country=country, indicator="gdp", output_type="df")
    df["DateTime"] = df["DateTime"].astype("datetime64")
    df["Year"] = df["DateTime"].transform([lambda dt: dt.year])
    df = df.rename(columns={"Value": "GDP"})
    return df.sort_values(by=["Year"], ascending=[False])[["Year", "GDP"]]


def get_rating_data(country="United States"):
    """TODO(aziot)"""
    if not country:
        return None
    df = te.getHistoricalRatings(country=country, output_type="df")
    df["Date"] = df["Date"].astype("datetime64")
    df["Year"] = df["Date"].transform([lambda dt: dt.year])
    return df.sort_values(by=["Year"], ascending=[False])[
        ["Year", "Agency", "Rating", "Outlook"]
    ]


app.layout = html.Div(
    [
        html.H2("Study the effect of a country's credit rating to its GDP."),
        html.Br(),
        html.Div(
            [
                dcc.Dropdown(
                    COUNTRIES,
                    id="country-dropdown",
                    style={"min-width": "15%", "margin-right": "3%"},
                    value="United States",
                ),
                dbc.RadioItems(
                    id="radios",
                    # className="btn-group",
                    # inputClassName="btn-check",
                    # labelClassName="btn btn-outline-primary",
                    # labelCheckedClassName="active",
                    options=[
                        {"label": "Tabular", "value": 1},
                        {"label": "Graphical", "value": 2},
                    ],
                    value=1,
                ),
            ],
            id="input-div",
            style={"display": "flex", "flex-direction": "row"},
        ),
        html.Br(),
        html.Div(
            [
                dbc.Table.from_dataframe(
                    get_gdp_data(),
                    striped=True,
                    bordered=True,
                    hover=True,
                ),
                dbc.Table.from_dataframe(
                    get_rating_data(),
                    striped=True,
                    bordered=True,
                    hover=True,
                ),
            ],
            id="output-div",
        ),
    ],
    id="master",
)


@app.callback(
    Output(component_id="output-div", component_property="children"),
    [Input("country-dropdown", "value"), Input("radios", "value")],
)
def update_output_div(country, radio_choice):
    gdp = get_gdp_data(country)
    ratings = get_rating_data(country)

    if radio_choice == 1:
        return [
            dbc.Table.from_dataframe(gdp, striped=True, bordered=True, hover=True),
            dbc.Table.from_dataframe(ratings, striped=True, bordered=True, hover=True),
        ]
    else:
        agencies = set(ratings["Agency"].tolist())

        fig = make_subplots(
            rows=len(agencies),
            cols=1,
            specs=[[{"secondary_y": True}] for _ in agencies],
        )

        # Add traces
        for index, agency in enumerate(agencies):
            fig.add_trace(
                go.Scatter(x=gdp["Year"].tolist(), y=gdp["GDP"].tolist(), name="GDP"),
                row=index + 1,
                col=1,
                secondary_y=False,
            )

            fig.add_trace(
                go.Scatter(
                    x=(ratings[ratings["Agency"] == agency])["Year"].tolist(),
                    y=(ratings[ratings["Agency"] == agency])["Rating"].tolist(),
                    name="{} rating".format(agency),
                ),
                row=index + 1,
                col=1,
                secondary_y=True,
            )

        # Add figure title
        fig.update_layout(title_text="GDP vs Credit Rating")

        # Set x-axis title
        fig.update_xaxes(title_text="Year")

        # Set y-axes titles
        fig.update_yaxes(title_text="<b>GDP</b>", secondary_y=False)
        fig.update_yaxes(title_text="<b>Rating</b>", secondary_y=True)

        return [dcc.Graph(id="gdp-vs-rating-graph", figure=fig)]


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
