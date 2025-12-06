import dash
import pandas as pd
from dash import Dash, html, Input, Output, dcc
import plotly.express as px
import dash_bootstrap_components as dbc
import os

df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "heart_dashboard.csv"))
numCols = ['Age', 'RestingBP', 'Cholesterol', 'MaxHR', 'Oldpeak']
catCols = ['Sex', 'ChestPainType', 'FastingBS', 'RestingECG', 'ExerciseAngina', 'ST_Slope', 'HeartDisease']

# default figures
PCOSPiePlot = px.pie(df, names="HeartDisease", title="Heart Disease")
piePlot = px.pie(df, names="ChestPainType", title="Chest Pain Type")
histogramPlot = px.histogram(df, x=numCols[0], title=numCols[0])
scatterPlot = px.scatter(df, x=numCols[0], y=numCols[1], title=f"{numCols[0]} VS. {numCols[1]}")
barPlot = px.bar(df.groupby(catCols[0], as_index=False)[numCols[0]].mean(), x=catCols[0], y=numCols[0], title=f"{catCols[0]} VS. Average {numCols[0]}")

# dash.register_page(__name__, path="/heart", external_stylesheets=[dbc.themes.VAPOR])

layout = dbc.Container(
    [
        html.H1("Heart Failure Dashboard"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3("Show data for:"),
                        dcc.Dropdown(
                            multi=True,
                            options=[
                                {"label": x, "value": x}
                                for x in df["ChestPainType"].unique()
                            ],
                            id="ChestPainType",
                            value=df["ChestPainType"].unique(),
                            placeholder="Chest Pain Type",
                        ),
                        dcc.Dropdown(
                            multi=True,
                            options=[
                                {"label": x, "value": x}
                                for x in df["RestingECG"].unique()
                            ],
                            id="RestingECG",
                            value=df["RestingECG"].unique(),
                            placeholder="Resting ECG",
                        ),
                        dcc.Dropdown(
                            multi=True,
                            options=[
                                {"label": x, "value": x}
                                for x in df["ST_Slope"].unique()
                            ],
                            id="ST_Slope",
                            value=df["ST_Slope"].unique(),
                            placeholder="ST Slope",
                        ),
                        dbc.Row(
                            [
                                dbc.Col([html.Label("Heart Disease")]),
                                dbc.Col(
                                    [
                                        dcc.Checklist(
                                            id="HeartDisease",
                                            options=[
                                                {"label": "yes", "value": 1},
                                                {"label": "no", "value": 0},
                                            ],
                                            inline=True,
                                            labelStyle={
                                                "display": "inline-block",
                                                "margin-right": "15px",
                                            },
                                            value=[1, 0]
                                        )
                                    ]
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col([html.Label("Sex")]),
                                dbc.Col(
                                    [
                                        dcc.Checklist(
                                            id="Sex",
                                            options=[
                                                {"label": "male", "value": "M"},
                                                {"label": "female", "value": "F"},
                                            ],
                                            inline=True,
                                            labelStyle={
                                                "display": "inline-block",
                                                "margin-right": "15px",
                                            },
                                            value=['M', 'F']
                                        )
                                    ]
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col([html.Label("Fasting BS")]),
                                dbc.Col(
                                    [
                                        dcc.Checklist(
                                            id="FastingBS",
                                            options=[
                                                {"label": "yes", "value": 1},
                                                {"label": "no", "value": 0},
                                            ],
                                            inline=True,
                                            labelStyle={
                                                "display": "inline-block",
                                                "margin-right": "15px",
                                            },
                                            value=[1, 0]
                                        )
                                    ]
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col([html.Label("Exercise Angina")]),
                                dbc.Col(
                                    [
                                        dcc.Checklist(
                                            id="ExerciseAngina",
                                            options=[
                                                {"label": "yes", "value": "Y"},
                                                {"label": "no", "value": "N"},
                                            ],
                                            inline=True,
                                            labelStyle={
                                                "display": "inline-block",
                                                "margin-right": "15px",
                                            },
                                            value=['Y', 'N']
                                        )
                                    ]
                                ),
                            ]
                        )
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
                                            ],
                                            multi=False,
                                            placeholder="Select column",
                                            value='Age',
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

@dash.callback(
    [
        Output('PCOSPiePlotGraph', 'figure'),
        Output('piePlotGraph', 'figure'),
        Output('histogramPlotGraph', 'figure'),
        Output('scatterPlotGraph', 'figure'),
        Output('barPlotGraph', 'figure')
    ],
    [
        Input('ChestPainType', 'value'),
        Input('RestingECG', 'value'),
        Input('ST_Slope', 'value'),
        Input('HeartDisease', 'value'),
        Input('Sex', 'value'),
        Input('FastingBS', 'value'),
        Input('ExerciseAngina', 'value'),

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
    ChestPainType,
    RestingECG, 
    ST_Slope, 
    HeartDisease,
    Sex,
    FastingBS,
    ExerciseAngina,
    
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
        df['ChestPainType'].isin(ChestPainType) &
        df['RestingECG'].isin(RestingECG) &
        df['ST_Slope'].isin(ST_Slope) &
        df['HeartDisease'].isin(HeartDisease) &
        df['Sex'].isin(Sex) &
        df['FastingBS'].isin(FastingBS) &
        df['ExerciseAngina'].isin(ExerciseAngina)
    ]

    return [
        px.pie(dff, names="HeartDisease", title="Heart Disease"),
        px.pie(dff, names=piePlot, title=piePlot),
        px.histogram(dff, x=histPlot, title=histPlot, color=histPlotHue),
        px.scatter(dff, x=scatterPlotX, y=scatterPlotY, title=f"{scatterPlotY} VS. {scatterPlotX}", color=scatterPlotHue),
        px.bar(dff.groupby(barPlotX, as_index=False)[barPlotY].mean(), x=barPlotX, y=barPlotY, title=f"{barPlotX} VS. Average {barPlotY}")
    ]
