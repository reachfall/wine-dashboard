import plotly.graph_objects as go
import plotly.express as px
import json
import os

import graph_df


token = os.environ.get('TOKEN', None)
if token is None:
    token = open("JSON/.mapbox_token").read()

px.set_mapbox_access_token(token)

mapbox = {
    "World": {
        "map": "mapbox://styles/etrashcan/ckpol4hcl022r17s1qjjlek6s",
        "cordinates": [35, 10],
        "zoom": 0.75,
    },
    "Europe": {
        "map": "mapbox://styles/etrashcan/ckpolipw402hp17si77i9312z",
        "cordinates": [57, 12],
        "zoom": 2.2,
    },
    "North America": {
        "map": "mapbox://styles/etrashcan/ckpoljfye02hy18pjgwejn1rs",
        "cordinates": [55, -105],
        "zoom": 1.55,
    },
    "South America": {
        "map": "mapbox://styles/etrashcan/ckpollyjb02ki17qh8umobfb5",
        "cordinates": [-27, -60],
        "zoom": 1.87,
    },
    "Asia": {
        "map": "mapbox://styles/etrashcan/ckpol3m49023g17pjpfp2y561",
        "cordinates": [27, 85],
        "zoom": 1.92,
    },
    "Africa": {
        "map": "mapbox://styles/etrashcan/ckpokz64501zb17pjwx7o92ht",
        "cordinates": [1, 15],
        "zoom": 1.92,
    },
    "Oceania": {
        "map": "mapbox://styles/etrashcan/ckpollgcw02jr18psekl06mmc",
        "cordinates": [-27, 140],
        "zoom": 2.5,
    },
}


for region in mapbox.keys():
    with open(f"JSON/{region}.json", "r") as f:
        mapbox[region]["JSON"] = json.loads(f.read())


def render_choropleth(region):
    data = (
        graph_df.df_choropleth
        if region == "World"
        else graph_df.df_choropleth.query(f"continent == '{region}'")
    )

    choropleth_map = px.choropleth_mapbox(
        data,
        geojson=mapbox[region]["JSON"],
        featureidkey="properties.iso_a2",
        locations="iso_a2",
        color="no_wines",
        color_continuous_scale="Burgyl",
        center={
            "lat": mapbox[region]["cordinates"][0],
            "lon": mapbox[region]["cordinates"][1],
        },
        zoom=mapbox[region]["zoom"],
        mapbox_style=mapbox[region]["map"],
        custom_data=["country", "continent", "no_wines"],
    )

    choropleth_map.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        plot_bgcolor="#191a1a",
        paper_bgcolor="#191a1a",
        height=515
    )

    choropleth_map.update_traces(
        marker_line_color="#191a1a",
        colorbar_ticks="",
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br><br>No. wines: %{customdata[2]}",
    )
    choropleth_map.update_layout(coloraxis_showscale=False)

    return choropleth_map


def render_sunburst_treemap(graph_type, treemap_value):
    if graph_type == "Sunburst":
        graph = px.sunburst(
            graph_df.df_sunburst,
            path=["continent_class", "country"],
            values="no_wines",
            color_discrete_sequence=px.colors.qualitative.Dark2,
        )
        graph.update_layout(
            uniformtext=dict(minsize=10, mode="hide"),
            plot_bgcolor="#191a1a",
            paper_bgcolor="#191a1a",
            font=dict(color="#fff"),
            margin={"r": 0, "t": 10, "l": 0, "b": 10},
            height=515
        )
    else:
        graph = px.treemap(
            graph_df.df_treemap,
            path=["world", "continent", "country"],
            values="no_wines",
            color=treemap_value,
            color_continuous_scale="Burgyl",
        )
        graph.update_layout(
            uniformtext=dict(minsize=10, mode="hide"),
            paper_bgcolor="#191a1a",
            plot_bgcolor="#191a1a",
            font=dict(color="#fff"),
            hoverlabel=dict(font=dict(color="#fff"), bordercolor="#fff"),
            margin={"r": 10, "t": 10, "l": 10, "b": 10},
            height=515
        )

    return graph


def render_barplot(df, value):
    bar = px.bar(df, x=value, y="no_reviews", height=220, log_y=True)

    bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#fff"),
        hoverlabel=dict(font=dict(color="#fff"), bordercolor="#fff"),
        showlegend=False,
        margin={"t": 10, "b": 0},
    )
    bar.update_xaxes(visible=False)
    bar.update_yaxes(title_font_color="rgba(0,0,0,0)")
    bar.update_traces(
        hovertemplate="<b>%{x}</b><br><br>No. reviews: %{y}",
        marker_color="#7289da",
        marker_line_color="#fff",
    )

    return bar


def render_indicator(value, name):
    indicator = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            title={"text": name},
            title_font_color="#8e9297",
            domain={"x": [0, 1], "y": [0, 1]},
            gauge_axis_showticklabels=False,
            gauge_axis_range=[0, 100],
            gauge_bgcolor="#23272a",
            gauge_bar_color="#7289da",
        )
    )
    indicator.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=300,
    )
    indicator.update_traces(number_font_color="#8e9297")
    return indicator
