import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
import dash
import dash_bootstrap_components as dbc



df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "kidney.csv"))
if df.duplicated().sum() > 0: df.drop_duplicates(inplace=True)
for col in df.columns:
    if df[col].dtype != 'object': df[col] = df[col].fillna(df[col].median())
X = df.drop('Class', axis=1)
y = df['Class']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
rf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
rf.fit(X_train, y_train)
acc = accuracy_score(y_test, rf.predict(X_test))
# حساب أهمية الميزات للرسم
importances = rf.feature_importances_
feat_df = pd.DataFrame({'Feature': X.columns, 'Importance': importances}).sort_values(by='Importance', ascending=False)


# ==========================================
# 3. تصميم الداش بورد (Layout)
# ==========================================
# (Cyberpunk Style)

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

colors = {
    'background': '#0f0f0f',
    'text': '#00ffcc',
    'panel': '#1a1a1a'
}

layout = html.Div(style={'backgroundColor': colors['background'], 'color': 'white', 'padding': '20px', 'minHeight': '100vh'}, children=[

    # العنوان
    html.H1(" Kidney Disease AI Dashboard", style={'textAlign': 'center', 'color': colors['text'], 'fontWeight': 'bold'}),
    html.Div(f"Model Accuracy: {acc*100:.2f}%", style={'textAlign': 'center', 'fontSize': '20px', 'color': '#ffcc00', 'marginBottom': '30px'}),


    html.Div([
        # Feature Importance
        html.Div([
            html.H4("Top Risk Factors", style={'textAlign': 'center'}),
            dcc.Graph(
                figure=px.bar(feat_df.head(7), x='Importance', y='Feature', orientation='h',
                              template='plotly_dark', color='Importance', color_continuous_scale='Viridis')
                              .update_layout(paper_bgcolor=colors['panel'], plot_bgcolor=colors['panel'])
            )
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        # Scatter Plot
        html.Div([
            html.H4("Interactive Analysis ", style={'textAlign': 'center', 'color': '#00ffcc'}),


            html.Div([
                html.Label("Select X Axis:"),
                dcc.Dropdown(
                    id='xaxis-column',
                    options=[{'label': i, 'value': i} for i in df.columns if i != 'Class'],
                    value=feat_df.iloc[0]['Feature'],
                    style={'color': 'black'}
                ),
            ], style={'width': '48%', 'display': 'inline-block'}),

            html.Div([
                html.Label("Select Y Axis:"),
                dcc.Dropdown(
                    id='yaxis-column',
                    options=[{'label': i, 'value': i} for i in df.columns if i != 'Class'],
                    value=feat_df.iloc[1]['Feature'], # Default: 2nd Most important
                    style={'color': 'black'}
                ),
            ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'}),


            dcc.Graph(id='indicator-graphic')

        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right', 'backgroundColor': colors['panel'], 'padding': '10px', 'borderRadius': '10px'})

    ], style={'marginBottom': '20px'}),


    html.Div([
        html.H4("Distribution Analysis", style={'textAlign': 'center'}),
        dcc.Graph(id='dist-graphic')
    ], style={'width': '100%', 'backgroundColor': colors['panel'], 'padding': '10px', 'borderRadius': '10px'})

])

# ==========================================
# 4. التفاعل (Callbacks) - مخ التطبيق
# ==========================================
@dash.callback(
    [Output('indicator-graphic', 'figure'),
     Output('dist-graphic', 'figure')],
    [Input('xaxis-column', 'value'),
     Input('yaxis-column', 'value')]
)
def update_graph(xaxis_name, yaxis_name):
    # 1. Scatter Plot
    fig1 = px.scatter(df, x=xaxis_name, y=yaxis_name, color='Class',
                     color_discrete_map={0: '#00ccff', 1: '#ff3333'},
                     template='plotly_dark', title=f'{xaxis_name} vs {yaxis_name}')
    fig1.update_layout(transition_duration=500, paper_bgcolor=colors['panel'], plot_bgcolor=colors['panel'])

    # 2. Box Plot
    fig2 = px.box(df, x='Class', y=xaxis_name, color='Class',
                  color_discrete_map={0: '#00ccff', 1: '#ff3333'},
                  template='plotly_dark', title=f'Distribution of {xaxis_name} by Class')
    fig2.update_layout(paper_bgcolor=colors['panel'], plot_bgcolor=colors['panel'])

    return fig1, fig2
