import dash
import pandas as pd
import os
from dash import html, Input, Output, dcc
import plotly.express as px
import dash_bootstrap_components as dbc

# Load data - FIX the path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
# df = pd.read_csv(os.path.join(parent_dir, "pcos_dashboard.csv"))
df = pd.read_csv("/home/maher/Desktop/depi-final-project/dashboards/pcos_dashboard.csv")

numCols = df.select_dtypes("number").columns
catCols = df.select_dtypes(exclude=["number"]).columns

# default figures
PCOSPiePlot = px.pie(df, names="PCOS (Y/N)", title="PCOS")
piePlot = px.pie(df, names="Blood Group", title="Blood group")
histogramPlot = px.histogram(df, x=numCols[0], title=numCols[0])
scatterPlot = px.scatter(df, x=numCols[0], y=numCols[1], title=f"{numCols[0]} VS. {numCols[1]}")
barPlot = px.bar(df.groupby(catCols[0], as_index=False)[numCols[0]].mean(), x=catCols[0], y=numCols[0], title=f"{catCols[0]} VS. Average {numCols[0]}")

layout = dbc.Container(
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
                            id="pcos_bloodGroup",  # CHANGED
                            value=df["Blood Group"].unique(),
                            placeholder="Blood groups",
                        ),
                        dbc.Row(
                            [
                                dbc.Col([html.Label("PCOS")]),
                                dbc.Col(
                                    [
                                        dcc.Checklist(
                                            id="pcos_pcos",  # CHANGED
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
                                            id="pcos_pregnant",  # CHANGED
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
                                            id="pcos_weightGain",  # CHANGED
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
                                            id="pcos_hairGrowth",  # CHANGED
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
                                            id="pcos_skinDarkening",  # CHANGED
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
                                            id="pcos_hairLoss",  # CHANGED
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
                                            id="pcos_pimples",  # CHANGED
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
                                            id="pcos_fastFood",  # CHANGED
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
                                            id="pcos_regularExercise",  # CHANGED
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
                                            id="pcos_piePlot",  # CHANGED
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
                                            id="pcos_histPlot",  # CHANGED
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
                                            id="pcos_histPlotHue",  # CHANGED
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
                                            id="pcos_scatterPlotY",  # CHANGED
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
                                            id="pcos_scatterPlotX",  # CHANGED
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
                                            id="pcos_scatterPlotHue",  # CHANGED
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
                                            id="pcos_barPlotY",  # CHANGED
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
                                            id="pcos_barPlotX",  # CHANGED
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
                                            id="pcos_barPlotHue",  # CHANGED
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
                dcc.Graph(id="pcos_PCOSPiePlotGraph", figure=PCOSPiePlot)  # CHANGED
            ]),
            dbc.Col([
                dcc.Graph(id="pcos_piePlotGraph", figure=piePlot)  # CHANGED
            ])
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="pcos_histogramPlotGraph", figure=histogramPlot)  # CHANGED
            ])
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="pcos_scatterPlotGraph", figure=scatterPlot)  # CHANGED
            ])
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="pcos_barPlotGraph", figure=barPlot)  # CHANGED
            ])
        ]),
    ], className = 'pb-5'
)

# Update callback with new IDs
@dash.callback(
    [
        Output('pcos_PCOSPiePlotGraph', 'figure'),  # CHANGED
        Output('pcos_piePlotGraph', 'figure'),  # CHANGED
        Output('pcos_histogramPlotGraph', 'figure'),  # CHANGED
        Output('pcos_scatterPlotGraph', 'figure'),  # CHANGED
        Output('pcos_barPlotGraph', 'figure')  # CHANGED
    ],
    [
        Input('pcos_bloodGroup', 'value'),  # CHANGED
        Input('pcos_pcos', 'value'),  # CHANGED
        Input('pcos_pregnant', 'value'),  # CHANGED
        Input('pcos_weightGain', 'value'),  # CHANGED
        Input('pcos_hairGrowth', 'value'),  # CHANGED
        Input('pcos_skinDarkening', 'value'),  # CHANGED
        Input('pcos_hairLoss', 'value'),  # CHANGED
        Input('pcos_pimples', 'value'),  # CHANGED
        Input('pcos_fastFood', 'value'),  # CHANGED
        Input('pcos_regularExercise', 'value'),  # CHANGED

        Input('pcos_piePlot', 'value'),  # CHANGED

        Input('pcos_histPlot', 'value'),  # CHANGED
        Input('pcos_histPlotHue', 'value'),  # CHANGED

        Input('pcos_scatterPlotY', 'value'),  # CHANGED
        Input('pcos_scatterPlotX', 'value'),  # CHANGED
        Input('pcos_scatterPlotHue', 'value'),  # CHANGED

        Input('pcos_barPlotY', 'value'),  # CHANGED
        Input('pcos_barPlotX', 'value'),  # CHANGED
        Input('pcos_barPlotHue', 'value')  # CHANGED
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