import pandas as pd
from dash import Dash, html, Input, Output, dcc
import plotly.express as px
import dash_bootstrap_components as dbc

df = pd.read_csv("./pcos_ready.csv")
numCols = df.select_dtypes("number").columns
catCols = df.select_dtypes(exclude=["number"]).columns

# default figures
PCOSPiePlot = px.pie(df, names="PCOS (Y/N)", title="PCOS")
piePlot = px.pie(df, names="Blood Group", title="Blood group")
histogramPlot = px.histogram(df, x=numCols[0], title=numCols[0])
scatterPlot = px.scatter(df, x=numCols[0], y=numCols[1], title=f"{numCols[0]} VS. {numCols[1]}")
barPlot = px.bar(df.groupby(catCols[0], as_index=False)[numCols[0]].mean(), x=catCols[0], y=numCols[0], title=f"{catCols[0]} VS. Average {numCols[0]}")

app = Dash(__name__, external_stylesheets=[dbc.themes.VAPOR])

app.layout = dbc.Container(
    [
        html.H1("PCOS Dashboard"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3("Show data for:"),
                        dcc.Dropdown(
                            multi=True,
                            options=[
                                {"label": x, "value": x}
                                for x in df["Blood Group"].unique()
                            ],
                            id="bloodGroup",
                            value=df["Blood Group"].unique(),
                            placeholder="Blood groups",
                        ),
                        dbc.Row(
                            [
                                dbc.Col([html.Label("PCOS")]),
                                dbc.Col(
                                    [
                                        dcc.Checklist(
                                            id="pcos",
                                            options=[
                                                {"label": "yes", "value": "yes"},
                                                {"label": "no", "value": "no"},
                                            ],
                                            inline=True,
                                            labelStyle={
                                                "display": "inline-block",
                                                "margin-right": "15px",
                                            },
                                            value=['yes', 'no']
                                        )
                                    ]
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col([html.Label("Pregnant")]),
                                dbc.Col(
                                    [
                                        dcc.Checklist(
                                            id="pregnant",
                                            options=[
                                                {"label": "yes", "value": "yes"},
                                                {"label": "no", "value": "no"},
                                            ],
                                            inline=True,
                                            labelStyle={
                                                "display": "inline-block",
                                                "margin-right": "15px",
                                            },
                                            value=['yes', 'no']
                                        )
                                    ]
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col([html.Label("Weight gain")]),
                                dbc.Col(
                                    [
                                        dcc.Checklist(
                                            id="weightGain",
                                            options=[
                                                {"label": "yes", "value": "yes"},
                                                {"label": "no", "value": "no"},
                                            ],
                                            inline=True,
                                            labelStyle={
                                                "display": "inline-block",
                                                "margin-right": "15px",
                                            },
                                            value=['yes', 'no']
                                        )
                                    ]
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col([html.Label("Hair growth")]),
                                dbc.Col(
                                    [
                                        dcc.Checklist(
                                            id="hairGrowth",
                                            options=[
                                                {"label": "yes", "value": "yes"},
                                                {"label": "no", "value": "no"},
                                            ],
                                            inline=True,
                                            labelStyle={
                                                "display": "inline-block",
                                                "margin-right": "15px",
                                            },
                                            value=['yes', 'no']
                                        )
                                    ]
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col([html.Label("Skin darkening")]),
                                dbc.Col(
                                    [
                                        dcc.Checklist(
                                            id="skinDarkening",
                                            options=[
                                                {"label": "yes", "value": "yes"},
                                                {"label": "no", "value": "no"},
                                            ],
                                            inline=True,
                                            labelStyle={
                                                "display": "inline-block",
                                                "margin-right": "15px",
                                            },
                                            value=['yes', 'no']
                                        )
                                    ]
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col([html.Label("Hair loss")]),
                                dbc.Col(
                                    [
                                        dcc.Checklist(
                                            id="hairLoss",
                                            options=[
                                                {"label": "yes", "value": "yes"},
                                                {"label": "no", "value": "no"},
                                            ],
                                            inline=True,
                                            labelStyle={
                                                "display": "inline-block",
                                                "margin-right": "15px",
                                            },
                                            value=['yes', 'no']
                                        )
                                    ]
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col([html.Label("Pimples")]),
                                dbc.Col(
                                    [
                                        dcc.Checklist(
                                            id="pimples",
                                            options=[
                                                {"label": "yes", "value": "yes"},
                                                {"label": "no", "value": "no"},
                                            ],
                                            inline=True,
                                            labelStyle={
                                                "display": "inline-block",
                                                "margin-right": "15px",
                                            },
                                            value=['yes', 'no']
                                        )
                                    ]
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col([html.Label("Fast food")]),
                                dbc.Col(
                                    [
                                        dcc.Checklist(
                                            id="fastFood",
                                            options=[
                                                {"label": "yes", "value": "yes"},
                                                {"label": "no", "value": "no"},
                                            ],
                                            inline=True,
                                            labelStyle={
                                                "display": "inline-block",
                                                "margin-right": "15px",
                                            },
                                            value=['yes', 'no']
                                        )
                                    ]
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col([html.Label("Regular exercise")]),
                                dbc.Col(
                                    [
                                        dcc.Checklist(
                                            id="regularExercise",
                                            options=[
                                                {"label": "yes", "value": "yes"},
                                                {"label": "no", "value": "no"},
                                            ],
                                            inline=True,
                                            labelStyle={
                                                "display": "inline-block",
                                                "margin-right": "15px",
                                            },
                                            value=['yes', 'no']
                                        )
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=4,
                ),
                dbc.Col(
                    [
                        html.H3("Plots"),
                        dbc.Row(
                            [
                                dbc.Col([html.Label("Pie")], width=2),
                                dbc.Col(
                                    [
                                        dcc.Dropdown(
                                            id="piePlot",
                                            options=[
                                                {"label": x, "value": x}
                                                for x in catCols
                                                if x != 'PCOS (Y/N)'
                                            ],
                                            multi=False,
                                            placeholder="Select column",
                                            value='Blood Group',
                                            clearable=False,
                                        )
                                    ]
                                ),
                            ],
                            className="mb-2",
                        ),
                        dbc.Row(
                            [
                                dbc.Col([html.Label("Histogram")], width=2),
                                dbc.Col(
                                    [
                                        dcc.Dropdown(
                                            id="histPlot",
                                            options=[
                                                {"label": x, "value": x}
                                                for x in numCols
                                            ],
                                            multi=False,
                                            placeholder="Select column",
                                            clearable=False,
                                            value=numCols[0],
                                        ),
                                    ]
                                ),
                                dbc.Col(
                                    [
                                        dcc.Dropdown(
                                            id="histPlotHue",
                                            options=[
                                                {"label": x, "value": x}
                                                for x in catCols
                                            ],
                                            multi=False,
                                            placeholder="Select hue",
                                        ),
                                    ]
                                ),
                            ],
                            className="mb-2",
                        ),
                        dbc.Row(
                            [
                                dbc.Col([html.Label("Scatter")], width=2),
                                dbc.Col(
                                    [
                                        dcc.Dropdown(
                                            id="scatterPlotY",
                                            options=[
                                                {"label": x, "value": x}
                                                for x in numCols
                                            ],
                                            multi=False,
                                            placeholder="Select Y-axis",
                                            value=numCols[0],
                                            clearable=False,
                                        )
                                    ]
                                ),
                                dbc.Col(
                                    [
                                        dcc.Dropdown(
                                            id="scatterPlotX",
                                            options=[
                                                {"label": x, "value": x}
                                                for x in numCols
                                            ],
                                            multi=False,
                                            placeholder="Select X-axis",
                                            value=numCols[1],
                                            clearable=False,
                                        )
                                    ]
                                ),
                                dbc.Col(
                                    [
                                        dcc.Dropdown(
                                            id="scatterPlotHue",
                                            options=[
                                                {"label": x, "value": x}
                                                for x in catCols
                                            ],
                                            multi=False,
                                            placeholder="Select hue",
                                        )
                                    ]
                                ),
                            ],
                            className="mb-2",
                        ),
                        dbc.Row(
                            [
                                dbc.Col([html.Label("Bar")], width=2),
                                dbc.Col(
                                    [
                                        dcc.Dropdown(
                                            id="barPlotY",
                                            options=[
                                                {"label": x, "value": x}
                                                for x in numCols
                                            ],
                                            multi=False,
                                            placeholder="Select Y-axis",
                                            value=numCols[0],
                                            clearable=False,
                                        )
                                    ]
                                ),
                                dbc.Col(
                                    [
                                        dcc.Dropdown(
                                            id="barPlotX",
                                            options=[
                                                {"label": x, "value": x}
                                                for x in catCols
                                            ],
                                            multi=False,
                                            placeholder="Select X-axis",
                                            value=catCols[0],
                                            clearable=False,
                                        )
                                    ]
                                ),
                                dbc.Col(
                                    [
                                        dcc.Dropdown(
                                            id="barPlotHue",
                                            options=[
                                                {"label": x, "value": x}
                                                for x in catCols
                                            ],
                                            multi=False,
                                            placeholder="Select hue",
                                        )
                                    ]
                                ),
                            ],
                            className="mb-2",
                        ),
                    ]
                ),
            ]
        ),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="PCOSPiePlotGraph", figure=PCOSPiePlot)
            ]),
            dbc.Col([
                dcc.Graph(id="piePlotGraph", figure=piePlot)
            ])
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="histogramPlotGraph", figure=histogramPlot)
            ])
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="scatterPlotGraph", figure=scatterPlot)
            ])
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="barPlotGraph", figure=barPlot)
            ])
        ]),
    ], className = 'pb-5'
)

@app.callback(
    [
        Output('PCOSPiePlotGraph', 'figure'),
        Output('piePlotGraph', 'figure'),
        Output('histogramPlotGraph', 'figure'),
        Output('scatterPlotGraph', 'figure'),
        Output('barPlotGraph', 'figure')
    ],
    [
        Input('bloodGroup', 'value'),
        Input('pcos', 'value'),
        Input('pregnant', 'value'),
        Input('weightGain', 'value'),
        Input('hairGrowth', 'value'),
        Input('skinDarkening', 'value'),
        Input('hairLoss', 'value'),
        Input('pimples', 'value'),
        Input('fastFood', 'value'),
        Input('regularExercise', 'value'),

        Input('piePlot', 'value'),

        Input('histPlot', 'value'),
        Input('histPlotHue', 'value'),

        Input('scatterPlotY', 'value'),
        Input('scatterPlotX', 'value'),
        Input('scatterPlotHue', 'value'),

        Input('barPlotY', 'value'),
        Input('barPlotX', 'value'),
        Input('barPlotHue', 'value')
    ]
)
def filtersEffect(
    bloodGroup,
    pcos, 
    pregnant, 
    weightGain,
    hairGrowth,
    skinDarkening,
    hairLoss,
    pimples,
    fastFood,
    regularExercise,
    
    piePlot,

    histPlot,
    histPlotHue,

    scatterPlotY,
    scatterPlotX,
    scatterPlotHue,

    barPlotY,
    barPlotX,
    barPlotHue,
):

    dff = df[
        df['PCOS (Y/N)'].isin(pcos) &
        df['Blood Group'].isin(bloodGroup) &
        df['Pregnant(Y/N)'].isin(pregnant) &
        df['Weight gain(Y/N)'].isin(weightGain) &
        df['hair growth(Y/N)'].isin(hairGrowth) &
        df['Skin darkening (Y/N)'].isin(skinDarkening) &
        df['Hair loss(Y/N)'].isin(hairLoss) &
        df['Pimples(Y/N)'].isin(pimples) &
        df['Fast food (Y/N)'].isin(fastFood)&
        df['Reg.Exercise(Y/N)'].isin(regularExercise)
    ]

    return [
        px.pie(dff, names="PCOS (Y/N)", title="PCOS"),
        px.pie(dff, names=piePlot, title=piePlot),
        px.histogram(dff, x=histPlot, title=histPlot, color=histPlotHue),
        px.scatter(dff, x=scatterPlotX, y=scatterPlotY, title=f"{scatterPlotY} VS. {scatterPlotX}", color=scatterPlotHue),
        px.bar(dff.groupby(barPlotX, as_index=False)[barPlotY].mean(), x=barPlotX, y=barPlotY, title=f"{barPlotX} VS. Average {barPlotY}")
    ]

app.run()
