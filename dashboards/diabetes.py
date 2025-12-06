import dash
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import os

df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "diabetes_prediction_dataset.csv"))
# إنشاء التطبيق
# dash.register_page(__name__, path="/diabetes")

# تحديد مدى العمر من البيانات نفسها
min_age = int(df['age'].min())
max_age = int(df['age'].max())

# تصميم الواجهة (Layout)
layout = html.Div([
    html.H1("📊 Diabetes Dashboard with Age Filter", style={'textAlign': 'center', 'marginBottom': 30}),

    # 🔹 Slider لاختيار مدى العمر
    html.Div([
        html.Label("Select Age Range:", style={'fontWeight': 'bold'}),
        dcc.RangeSlider(
            id='age-slider',
            min=min_age,
            max=max_age,
            step=1,
            marks={i: str(i) for i in range(min_age, max_age+1, 10)},
            value=[min_age, max_age],
            tooltip={"placement": "bottom", "always_visible": True}
        )
    ], style={'margin': '40px'}),

    # 🔹 اختيار المتغير للـ Box Plot
    html.Div([
        html.Label("Select variable for Box Plot:", style={'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='variable-dropdown',
            options=[
                {'label': 'BMI', 'value': 'bmi'},
                {'label': 'HbA1c Level', 'value': 'HbA1c_level'},
                {'label': 'Blood Glucose Level', 'value': 'blood_glucose_level'}
            ],
            value='bmi',
            clearable=False,
            style={'width': '50%', 'margin': 'auto'}
        ),
    ], style={'textAlign': 'center', 'marginBottom': 40}),

    # Box Plot
    dcc.Graph(id='box-plot', style={'height': '500px'}),

    html.Hr(),

    # 🔹 اختيار حالة التدخين للـ Histogram
    html.Div([
        html.Label("Select Smoking History:", style={'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='smoke',
            options=[{'label': s, 'value': s} for s in df['smoking_history'].unique()],
            value=df['smoking_history'].unique()[0],
            clearable=False,
            style={'width': '50%', 'margin': 'auto'}
        ),
    ], style={'textAlign': 'center', 'marginBottom': 40}),

    # Histogram
    dcc.Graph(id='bar-chart', style={'height': '500px'})
])

# 🔹 Callback 1 → Box Plot
@dash.callback(
    Output('box-plot', 'figure'),
    [Input('variable-dropdown', 'value'),
     Input('age-slider', 'value')]
)
def update_box_plot(selected_var, age_range):
    filtered_df = df[(df['age'] >= age_range[0]) & (df['age'] <= age_range[1])]
    fig = px.box(
        filtered_df,
        x='diabetes',
        y=selected_var,
        color='diabetes',
        title=f"Distribution of {selected_var.capitalize()} by Diabetes Status (Age {age_range[0]}–{age_range[1]})",
        labels={'diabetes': 'Diabetes', selected_var: selected_var.capitalize()},
        template='plotly_white'
    )
    fig.update_layout(title_x=0.5)
    return fig


# 🔹 Callback 2 → Histogram
@dash.callback(
    Output('bar-chart', 'figure'),
    [Input('smoke', 'value'),
     Input('age-slider', 'value')]
)
def update_chart(smoke_value, age_range):
    filtered = df[(df['smoking_history'] == smoke_value) &
                  (df['age'] >= age_range[0]) &
                  (df['age'] <= age_range[1])]

    fig = px.histogram(
        filtered,
        x='age',
        color='diabetes',
        barmode='group',
        title=f"Diabetes by Age ({smoke_value}) - Age {age_range[0]}–{age_range[1]}",
        labels={'age': 'Age', 'diabetes': 'Diabetes Status'},
        template='plotly_white'
    )
    fig.update_layout(title_x=0.5)
    return fig
