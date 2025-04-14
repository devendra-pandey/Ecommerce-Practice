from django_plotly_dash import DjangoDash
from dash import dcc, html
import pandas as pd
import plotly.express as px
from ecommerce_app.models import Order, OrderItem, Product

app = DjangoDash('AdminDashboard')

# Get orders with payment info
orders = Order.objects.select_related('payment_method').all()

# ✅ Payment Type Chart (with safeguard for empty data)
payment_records = []
for o in orders:
    if o.payment_method:
        payment_records.append({'Payment': o.payment_method.get_method_display()})

if payment_records:
    payment_df = pd.DataFrame(payment_records)
    payment_fig = px.pie(payment_df, names='Payment', title="Orders by Payment Type")
else:
    payment_fig = px.pie(pd.DataFrame({'Empty': [1]}), names='Empty', title="No Payment Data Available")

# ✅ Top Products Chart
items = OrderItem.objects.select_related('product').all()
product_data = {}
for item in items:
    if item.product:
        product_data[item.product.name] = product_data.get(item.product.name, 0) + item.quantity

if product_data:
    top_df = pd.DataFrame(list(product_data.items()), columns=['Product', 'Quantity'])
    top_fig = px.bar(top_df.sort_values('Quantity', ascending=False), x='Product', y='Quantity', title="Top Selling Products")
else:
    top_fig = px.bar(pd.DataFrame({'Empty': [0]}), x='Empty', y='Empty', title="No Products Sold")

# ✅ Daily Sales Trend
sales_records = []
for o in orders:
    total = sum(item.quantity * item.price for item in o.order_items.all())
    sales_records.append({'Date': o.placed_at.date(), 'Total': total})

if sales_records:
    sales_df = pd.DataFrame(sales_records).groupby('Date').sum().reset_index()
    sales_fig = px.line(sales_df, x='Date', y='Total', title="Daily Sales")
else:
    sales_fig = px.line(pd.DataFrame({'Date': [], 'Total': []}), x='Date', y='Total', title="No Sales Data")

# ✅ Layout
app.layout = html.Div([
    html.H2("Admin Sales Dashboard"),
    dcc.Graph(figure=payment_fig),
    dcc.Graph(figure=top_fig),
    dcc.Graph(figure=sales_fig),
])
