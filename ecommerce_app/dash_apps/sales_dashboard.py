import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output
from django_plotly_dash import DjangoDash

# Sample data — replace with your DB pull or CSV
data = {
    'order_date': pd.date_range(start='2023-01-01', periods=60),
    'sales': [x * 100 for x in range(60)],
    'category': ['Electronics', 'Clothing', 'Books'] * 20
}
df = pd.DataFrame(data)

# Initialize Dash app
app = DjangoDash('SalesDashboard')

# App layout
app.layout = html.Div([
    html.H4("Sales Over Time by Category"),
    dcc.Dropdown(
        id='category-filter',
        options=[{'label': cat, 'value': cat} for cat in df['category'].unique()],
        value='Electronics',
        clearable=False
    ),
    dcc.Graph(id='sales-graph')
])

# Callback to update graph based on dropdown
@app.callback(
    Output('sales-graph', 'figure'),
    [Input('category-filter', 'value')]
)
def update_graph(selected_category):
    filtered_df = df[df['category'] == selected_category]
    fig = px.line(filtered_df, x='order_date', y='sales', title=f"{selected_category} Sales Over Time")
    return fig
