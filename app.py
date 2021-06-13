import numpy as np
import dash
import json
import pandas as pd
import dash_table
from dash.dependencies import Output, Input, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import graph_viz
import graph_df

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# TODO: clean up styles it's a mess
# TODO: try to merge render functions a bit, too many of them
fontStyle = {"color": "#fff"}
mainBackground = "#2c2f33"
cardBackground = "#23272a"

card_title_font_style = {"color": "#8e9297", "textAlign": "end"}

column_names = {
    "country": [
        {"name": "Country", "id": "country"},
        {"name": "Reviews", "id": "no_reviews"},
        {"name": "Mean score", "id": "avg_points"},
        {"name": "Mean price", "id": "avg_price"},
    ],
    "variety": [
        {"name": "Wine variety", "id": "variety"},
        {"name": "Reviews", "id": "no_reviews"},
        {"name": "Mean points", "id": "avg_points"},
        {"name": "Mean price", "id": "avg_price"},
    ],
}

# TODO: add link to github
header = dbc.Card(
    [
        dbc.CardBody(
            [
                dcc.Link(
                    html.Img(
                        style={
                            "height": 40,
                            "size": 1,
                            "marginLeft": "1rem",
                        },
                        src=app.get_asset_url("github_logo.png"),
                    ),
                    refresh=True,
                    href="https://github.com/reachfall/dashboard-wine",
                    style={"alignSelf":"center"}
                ),
                html.Div(
                    [
                        html.Div(
                            style={"textAlign": "end"},
                            children=[
                                html.H1(
                                    style={**fontStyle, "marginBottom": 0},
                                    children="Wines around the world",
                                ),
                                html.H5(
                                    style={
                                        **fontStyle,
                                        "marginTop": 2,
                                    },
                                    children="by Wojciech Tomczak",
                                ),
                            ],
                        ),
                        html.Img(
                            style={"height": 100, "size": 1, "marginLeft": "2em"},
                            src=app.get_asset_url("logo.png"),
                        ),
                    ],
                    style={"display": "flex"},
                ),
            ],
            style={
                "backgroundColor": "rgba(0,0,0,0)",
                "display": "flex",
                "justifyContent": "space-between",
            },
        )
    ],
    style={
        "flex": 1,
        "borderColor": "#23272a",
        "borderRadius": 10,
        "backgroundColor": cardBackground,
        "marginBottom": "1.5vh",
    },
)


def render_card(children, header_text=None, height=None, header_id=None):
    return (
        dbc.Card(
            dbc.CardBody(
                [
                    html.H3(
                        header_text,
                        style={
                            "color": "#8e9297",
                            "textAlign": "end",
                            "marginBottom": 15,
                        },
                    ),
                    children,
                ]
            ),
            style={
                "backgroundColor": "#2c2f33",
                "height": height,
            },
        )
        if header_id is None
        else dbc.Card(
            dbc.CardBody(
                [
                    html.H3(
                        header_text,
                        id=header_id,
                        style={
                            "color": "#8e9297",
                            "textAlign": "end",
                            "marginBottom": 15,
                        },
                    ),
                    children,
                ]
            ),
            style={
                "backgroundColor": "#2c2f33",
                "height": height,
            },
        )
    )


def render_card_title(text):
    return html.H3(
        text,
        style={"color": "#8e9297", "textAlign": "end", "marginBottom": 15},
    )


def render_tab(tab_label, child):
    return dbc.Tab(
        label=tab_label,
        tab_style={"width": 200, "textAlign": "center"},
        label_style={"color": "#fff"},
        active_label_style={"color": "#23272a"},
        children=html.Div(
            style={"color": "#fff", "marginTop": 20},
            children=[child],
        ),
    )


def render_graph_on_callback(id, children=None):
    return dbc.Card(
        style={"backgroundColor": "#2c2f33"},
        children=[
            dbc.CardBody(children=[children, dcc.Loading(dcc.Graph(id=id))]),
        ],
    )


def render_dropdown(id, labels, values, default_value):
    return dcc.Dropdown(
        style={
            "color": "#8e9297",
            "marginBottom": 25,
        },
        id=id,
        options=[{"label": labels[i], "value": values[i]} for i in range(len(labels))],
        value=default_value,
        clearable=False,
    )


sunburst_treemap_header = html.Div(
    [
        html.H3(
            style={"color": "#8e9297", "textAlign": "end", "marginBottom": 15},
            children="Wine distribution around the world",
        ),
        dbc.Row(
            [
                dbc.Col(
                    render_dropdown(
                        "sunburst-treemap-dropdown",
                        ["Sunburst", "Treemap"],
                        ["Sunburst", "Treemap"],
                        "Sunburst",
                    ),
                    width=6,
                ),
                dbc.Col(
                    id="treemap-render-dropdown",
                    style={"display": "block"},
                    children=[
                        render_dropdown(
                            "treemap-dropdown",
                            ["Price", "Score"],
                            ["price", "points"],
                            "price",
                        )
                    ],
                    width=6,
                ),
            ]
        ),
    ]
)

choropleth_header = html.Div(
    [
        html.H3(
            style={"color": "#8e9297", "textAlign": "end", "marginBottom": 15},
            children="Wine around the world",
        ),
        render_dropdown(
            "choropleth-dropdown",
            [
                "World",
                "North America",
                "Europe",
                "Asia",
                "South America",
                "Africa",
                "Oceania",
            ],
            [
                "World",
                "North America",
                "Europe",
                "Asia",
                "South America",
                "Africa",
                "Oceania",
            ],
            "World",
        ),
    ]
)

master_taster_table1 = dash_table.DataTable(
    id="tasters-datatable",
    style_header={
        "backgroundColor": "#191a1a",
        "textAlign": "center",
    },
    style_cell={
        "backgroundColor": "#2c2f33",
    },
    style_table={"overflow": "auto"},
    page_size=16,
    columns=[
        {"name": "Taster name", "id": "taster_name"},
        {"name": "Twitter", "id": "taster_twitter_handle"},
        {"name": "Reviews", "id": "no_reviews"},
    ],
    data=graph_df.df_tasters_stats.iloc[:, :3]
    .sort_values(by=["no_reviews"], ascending=False)
    .to_dict("records"),
)

master_taster_table2 = dcc.Loading(
    dash_table.DataTable(
        id="tasters-datatable-details",
        style_header={
            "backgroundColor": "#191a1a",
            "textAlign": "center",
        },
        style_cell={
            "backgroundColor": "#2c2f33",
        },
        sort_action="native",
        style_table={"overflow": "auto"},
        page_size=10,
    )
)

master_taster_table3 = html.Div(
    [
        dash_table.DataTable(
            id="q-and-a",
            style_header={
                "backgroundColor": "#191a1a",
                "textAlign": "center",
            },
            style_cell={
                "backgroundColor": "#2c2f33",
            },
            style_table={"overflow": "auto"},
            style_data_conditional=(
                [
                    {"if": {"column_id": "Question"}, "textAlign": "left"},
                ]
                + [
                    {
                        "if": {"row_index": i, "column_id": "Answer"},
                        "textAlign": "center",
                    }
                    for i in [6, 7, 8, 9]
                ]
            ),
            columns=[
                {"name": "Question", "id": "Question"},
                {"name": "Answer", "id": "Answer"},
            ],
        ),
        dcc.Loading(
            dcc.Graph(
                id="q-and-a-barplot", style={"marginTop": 10, "overflowX": "auto"}
            )
        ),
    ],
)

world_of_wines_tab = dbc.Row(
    [
        dbc.Col(render_graph_on_callback("sunburst-treemap", sunburst_treemap_header)),
        dbc.Col(render_graph_on_callback("choropleth", choropleth_header)),
    ],
    style={"alignItems": "stretch"},
)

master_taster_tab = dbc.Row(
    children=[
        dbc.Col(
            render_card(master_taster_table1, "Pick one, any one...", "68vh"),
        ),
        dbc.Col(
            [
                render_card(
                    render_dropdown(
                        "tasters-datatable-details-dropdown",
                        ["Regions", "Variety"],
                        ["country", "variety"],
                        "country",
                    ),
                    "...now pick grouping method...",
                ),
                html.Div(
                    render_card(
                        master_taster_table2,
                        header_id="custom-datatable-header",
                        height="50vh",
                    ),
                    style={"marginTop": 20},
                ),
            ],
        ),
        dbc.Col(
            [
                render_card(master_taster_table3, "...yet more results", "68vh"),
            ],
        ),
    ],
)

winery_championship_tab = html.Div(
    [
        html.Div(
            [
                html.Img(
                    style={"height": 200, "size": 1, "marginRight": "1em"},
                    src=app.get_asset_url("work_in_progress.svg"),
                ),
                html.H2("Construction underway", style={"marginTop": 40}),
                html.H3("Winery championships will commence soon"),
            ],
            style={"marginTop": 150},
        )
    ],
    style={
        "color": "#fff",
        "display": "flex",
        "justifyContent": "center",
        "alignItems": "center",
        "textAlign": "center",
        "flexDirection": "column",
    },
)

question_style = {"font": "italic"}

about_tab = dbc.Row(
    [
        dbc.Col(
            [
                html.H5("Why wine reviews?"),
                html.P(
                    "It was between this, football across ages and Netflix movie and shows database. So I asked 8 ball to choose for me and that's what I winded up with. In a hindsight not a bad decision."
                ),
                html.H5("What the data is about?"),
                html.P(
                    [
                        "It's wine review data scraped from ",
                        dcc.Link(
                            "WineEnthusiast",
                            refresh=True,
                            href="https://www.winemag.com/?s=&drink_type=wine",
                        ),
                        ", by ",
                        dcc.Link(
                            "some man",
                            refresh=True,
                            href="https://www.kaggle.com/zynicide",
                        ),
                        " who got inspired after watching a documentary on master sommeliers. And for his deed I like many others who've used this dataset before me, am thankful.",
                    ]
                ),
                html.H5("What the purpose of this dataset?"),
                html.P(
                    [
                        "Dashboard created with help of this data goes against its creator. It was made with predictive models in mind, so this project is a far cry from its destiny. But it looks good on a map. For more info see: ",
                        dcc.Link(
                            "Kagle wine review dataset",
                            refresh=True,
                            href="https://www.kaggle.com/zynicide/wine-reviews",
                        ),
                    ]
                ),
                html.H5("Future of dashboard"),
                html.P(
                    "There is stil much to do. Due to time constraints not all functionality was implemented. 'Winery championship' is still work in the progress, layout is as responsive as 100 year old man with dementia and code is one big mess held together by duck tape. But I tell myself it's not that bad, everything will be for forgetten, just look at that picture of a small cute cat."
                ),
            ]
        ),
        dbc.Col(
            html.Div(
                html.Img(
                    style={"size": 3},
                    src=app.get_asset_url("cute_small_cat.jpg"),
                ),
                style={
                    "display": "flex",
                    "justifyContent": "center",
                    "alignContent": "center",
                },
            )
        ),
    ]
)

tabMenu = dbc.Card(
    style={
        "borderColor": "#23272a",
        "borderRadius": 10,
        "backgroundColor": cardBackground,
        "height": "80vh",
    },
    children=[
        dbc.CardBody(
            children=[
                dbc.Tabs(
                    style={"justifyContent": "end"},
                    children=[
                        render_tab("World of wines", world_of_wines_tab),
                        render_tab("Master taster", master_taster_tab),
                        render_tab("Winery championship", winery_championship_tab),
                        render_tab("About", about_tab),
                    ],
                )
            ]
        )
    ],
)

wine_details_modal = dbc.Modal(
    [
        dbc.ModalHeader(
            html.H3(id="wine-details-header", style={**card_title_font_style}),
            style={"backgroundColor": "#2c2f33"},
        ),
        dbc.ModalBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dcc.Loading(
                                    id="wine-details-modal-points-gauge-graph",
                                    style={"margin": 0},
                                ),
                                dcc.Loading(
                                    id="wine-details-modal-price-gauge-graph",
                                    style={"margin": 0},
                                ),
                            ]
                        ),
                        dbc.Col(
                            dash_table.DataTable(
                                id="wine-details-body-datatable",
                                style_header={
                                    "backgroundColor": "#2c2f33",
                                    "color": "#2c2f33",
                                    "border": "none",
                                },
                                style_cell={
                                    "backgroundColor": "#2c2f33",
                                    "color": "#fff",
                                    "border": "none",
                                },
                                style_table={
                                    "overflow": "auto",
                                    "margin": 10,
                                },
                                style_data_conditional=[
                                    {
                                        "if": {"column_id": "col1"},
                                        "textAlign": "left",
                                    },
                                ],
                                columns=[
                                    {"name": "col1", "id": "col1"},
                                    {"name": "col2", "id": "col2"},
                                ],
                            ),
                        ),
                    ]
                )
            ],
            style={"backgroundColor": "#2c2f33"},
        ),
    ],
    id="wine-details-modal",
    centered=True,
)

app.layout = html.Div(
    style={
        "position": "fixed",
        "backgroundColor": mainBackground,
        "top": 0,
        "left": 0,
        "bottom": 0,
        "right": 0,
        "paddingTop": "1.5vh",
        "paddingBottom": "1.5vh",
        "paddingLeft": "1vw",
        "paddingRight": "1vw",
        "overflow": "auto",
    },
    children=[header, tabMenu, wine_details_modal],
)


@app.callback(
    Output("choropleth", "figure"),
    Input("choropleth-dropdown", "value"),
)
def update_choropleth(value):
    return graph_viz.render_choropleth(value)


@app.callback(
    [
        Output("sunburst-treemap", "figure"),
        Output("treemap-render-dropdown", "style"),
    ],
    [
        Input("sunburst-treemap-dropdown", "value"),
        Input("treemap-dropdown", "value"),
    ],
)
def render_sunburst_treemap(graph_type, treemap_value):
    treemap_dropdown_visibility = (
        {"display": "none"} if graph_type == "Sunburst" else {"display": "block"}
    )
    return [
        graph_viz.render_sunburst_treemap(graph_type, treemap_value),
        treemap_dropdown_visibility,
    ]


@app.callback(
    [
        Output("tasters-datatable-details", "columns"),
        Output("tasters-datatable-details", "data"),
        Output("custom-datatable-header", "children"),
        Output("q-and-a", "data"),
        Output("q-and-a-barplot", "figure"),
    ],
    [
        Input("tasters-datatable", "active_cell"),
        Input("tasters-datatable-details-dropdown", "value"),
    ],
    State("tasters-datatable", "data"),
)
def render_details_datatable(active_cell, value, table_data):
    if active_cell:
        _ = json.dumps(active_cell, indent=2)
        row = active_cell["row"]
        row_dict = table_data[row]
    else:
        row_dict = table_data[0]

    twitter_handle = (
        np.nan
        if row_dict["taster_twitter_handle"] is None
        else row_dict["taster_twitter_handle"]
    )

    name = row_dict["taster_name"]
    result = graph_df.get_taster_details(name, twitter_handle, value)
    result.sort_values(by=["no_reviews"], inplace=True, ascending=False)

    if value == "country":
        add_result = graph_df.get_taster_details(
            name, twitter_handle, "variety"
        ).sort_values(by="no_reviews", ascending=False)
        wine_variety = [
            add_result["no_reviews"].values[0],
            add_result["variety"].values[0],
        ]
        wine_country = [result["no_reviews"].values[0], result["country"].values[0]]
    else:
        add_result = graph_df.get_taster_details(
            name, twitter_handle, "country"
        ).sort_values(by="no_reviews", ascending=False)
        wine_variety = [result["no_reviews"].values[0], result["variety"].values[0]]
        wine_country = [
            add_result["no_reviews"].values[0],
            add_result["country"].values[0],
        ]

    q_and_a = pd.DataFrame(
        {
            "Question": [
                "Your name?",
                "Your twitter?",
                "Most reviewed wine by variety?",
                "What variety?",
                "Most reviewed wine by origin country?",
                "What country?",
                "What's the best wine you reviewed?",
                "Which one was the crappiest?",
                "What about the cheapest wine?",
                "And the most expensive one?",
            ],
            "Answer": [
                name,
                twitter_handle,
                *wine_variety,
                *wine_country,
                "Click for details",
                "Click for details",
                "Click for details",
                "Click for details",
            ],
        }
    )

    return [
        column_names[value],
        result.to_dict("records"),
        f"Here are results for {row_dict['taster_name']}",
        q_and_a.to_dict("records"),
        graph_viz.render_barplot(result, value),
    ]


@app.callback(
    [
        Output("wine-details-modal", "is_open"),
        Output("wine-details-header", "children"),
        Output("wine-details-body-datatable", "data"),
        Output("wine-details-modal-points-gauge-graph", "children"),
        Output("wine-details-modal-price-gauge-graph", "children"),
    ],
    Input("q-and-a", "active_cell"),
    State("q-and-a", "data"),
)
def render_wine_modal(active_cell, table_data):
    if active_cell:
        _ = json.dumps(active_cell, indent=2)
        # we are intrested in rows 6,7,8,9
        row = active_cell["row"]

        if row not in [6, 7, 8, 9]:
            return [False, None, None]

        # name and twitter handle are stored in 0th and 1st row
        name = table_data[0]["Answer"]
        twitter_handle = (
            np.nan if table_data[1]["Answer"] is None else table_data[1]["Answer"]
        )

        map_question_to_param = {
            6: "points_max",
            7: "points_min",
            8: "price_min",
            9: "price_max",
        }

        taster_stats = graph_df.get_taster_stats(name, twitter_handle)
        wine_review = graph_df.find_wine_review(
            name, twitter_handle, taster_stats, map_question_to_param[row]
        )

        title = (f"{wine_review['title'].values[0]}",)

        wine_info = pd.DataFrame(
            {
                "col1": [
                    "Variety",
                    "Designation",
                    "Continent",
                    "Origin country",
                    "Province",
                    "Primary region",
                    "Secondary region",
                    "Winerey",
                    "Reviewer's name",
                    "Reviewer's twitter",
                ],
                "col2": [
                    wine_review[col].values[0]
                    for col in [
                        "variety",
                        "designation",
                        "continent",
                        "country",
                        "province",
                        "region_1",
                        "region_2",
                        "winery",
                        "taster_name",
                        "taster_twitter_handle",
                    ]
                ],
            }
        )

        points_gauge_graph = (
            None
            if wine_review["points"].values[0] is None
            else dcc.Graph(
                figure=graph_viz.render_indicator(
                    wine_review["points"].values[0], "Points"
                )
            )
        )
        price_gauge_graph = (
            None
            if wine_review["price"].values[0] is None
            else dcc.Graph(
                figure=graph_viz.render_indicator(
                    wine_review["price"].values[0], "Price"
                )
            )
        )

        return [
            True,
            title,
            wine_info.to_dict("records"),
            points_gauge_graph,
            price_gauge_graph,
        ]
    else:
        return [False, None, None, None, None]


if __name__ == "__main__":
    app.run_server(debug=False)
