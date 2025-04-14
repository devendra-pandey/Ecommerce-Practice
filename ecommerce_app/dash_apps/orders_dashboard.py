import pandas as pd
import plotly.express as px
from dash import html, dcc
from django_plotly_dash import DjangoDash
from ecommerce_app.models import Order, PaymentMethod

app = DjangoDash('OrdersDashboard')

# Extract data from DB
orders = Order.objects.all().values('payment_method__method', 'placed_at')
df = pd.DataFrame(orders)

# Aggregated count by payment type
payment_count = df['payment_method__method'].value_counts().reset_index()
payment_count.columns = ['Payment Type', 'Orders']

app.layout = html.Div([
    html.H4("Orders by Payment Method"),
    dcc.Graph(figure=px.pie(payment_count, names='Payment Type', values='Orders'))
])
