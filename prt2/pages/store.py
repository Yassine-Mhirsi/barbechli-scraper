import dash
from dash import callback, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from utils.functions import create_card
import pandas as pd
import plotly.express as px
import json
from dateutil.parser import parse  # Changed from datetime import

dash.register_page(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    path="/store_overview",
)

# Load data
df = pd.read_csv('products.csv')

# =============================================
# Data Preparation
# =============================================

def prepare_store_data(df):
    """Prepare all store-related data for visualizations"""
    # Store engagement data
    engagement_data = df.melt(
        id_vars=['store_label', 'title'],
        value_vars=['clicks', 'clicksExternal'],
        var_name='click_type',
        value_name='click_count'
    )

    # Calculate total engagement per store
    store_engagement = engagement_data.groupby('store_label')['click_count'].sum().reset_index()
    top_stores = store_engagement.nlargest(5, 'click_count')['store_label'].tolist()
    
    # Deal frequency data
    for col in ['price_deal', 'price_hot_deal', 'price_top_deal']:
        df[col] = df[col].apply(lambda x: 1 if str(x).lower() in ['yes', 'true'] else 0)
    
    deal_counts = df.groupby('store_label')[['price_deal', 'price_hot_deal', 'price_top_deal']].sum().reset_index()
    deal_data = deal_counts.melt(
        id_vars=['store_label'],
        value_vars=['price_deal', 'price_hot_deal', 'price_top_deal'],
        var_name='deal_type',
        value_name='count'
    )
    
    # Parse priceTable data and standardize to dd-mm-yy format
    price_records = []
    for idx, row in df.iterrows():
        try:
            price_table = json.loads(row['priceTable'].replace("'", '"')) if isinstance(row['priceTable'], str) else row['priceTable']
            for entry in price_table:
                try:
                    dt = parse(entry['date_price'])
                    price_records.append({
                        'store_label': row['store_label'],
                        'product_name': row['title'],
                        'date_price': dt.strftime('%d-%m-%y'),
                        'price': float(entry['price'])
                    })
                except (ValueError, KeyError):
                    continue
        except (json.JSONDecodeError, TypeError):
            continue
    
    price_data = pd.DataFrame(price_records)
    price_data['date_price'] = pd.to_datetime(price_data['date_price'], format='%d-%m-%y')
    
    # Get top 5 most expensive products per store
    top_products = df.sort_values(['store_label', 'price'], ascending=[True, False]) \
                   .groupby('store_label').head(5)
    
    # Get top 3 brands per store (for top 5 stores)
    top_brands = df[df['store_label'].isin(top_stores)] \
               .groupby(['store_label', 'brand'])['clicks'].sum().reset_index() \
               .sort_values(['store_label', 'clicks'], ascending=[True, False]) \
               .groupby('store_label').head(3)
    
    # Calculate summary stats
    stats = {
        'total_stores': df['store_label'].nunique(),
        'avg_price': df['price'].mean(),
        'total_deals': df[['price_deal', 'price_hot_deal', 'price_top_deal']].sum().sum(),
        'top_stores': top_stores,
        'store_engagement': store_engagement,
        'top_products': top_products,
        'top_brands': top_brands
    }
    # Get top 5 most expensive products per store (store this in stats)
    top_products = df.sort_values(['store_label', 'price'], ascending=[True, False]) \
                   .groupby('store_label').head(5)
    
    # Create store options for dropdown
    store_product_options = [{'label': store, 'value': store} 
                           for store in df['store_label'].unique()]
    
    
    return {
        'engagement_data': engagement_data,
        'deal_data': deal_data,
        'price_data': price_data,
        'top_products': top_products,
        'store_product_options': store_product_options,
        **stats
    }

store_data = prepare_store_data(df)

# =============================================
# Visualizations (Green Theme)
# =============================================
def create_store_visualizations(store_data):
    """Create all store visualizations with green color scheme"""
    # 1. Store Engagement Treemap (Top 5 Stores)
    engagement_treemap = px.treemap(
        store_data['store_engagement'].nlargest(5, 'click_count'),
        path=['store_label'],
        values='click_count',
        title='Top 5 Stores by Engagement',
        color='click_count',
        color_continuous_scale='Greens',
        hover_data=['click_count']
    )
    engagement_treemap.update_traces(
        textinfo="label+value",
        hovertemplate="<b>%{label}</b><br>Engagement: %{value:,}"
    )
    
    # 2. Most Expensive Products (Horizontal Bar Chart)
    top_products_chart = px.bar(
        store_data['top_products'].sort_values('price', ascending=True),
        x='price',
        y='title',
        color='store_label',
        orientation='h',
        title='Top 5 Most Expensive Products per Store',
        color_discrete_sequence=px.colors.sequential.Greens[3:],
        height=800  # Increased height to accommodate all products
    )
    top_products_chart.update_layout(
        yaxis={'categoryorder':'total ascending'},
        showlegend=True
    )
    
    # 3. Top 3 Brands per Store (Grouped Bar Chart)
    top_brands_chart = px.bar(
        store_data['top_brands'],
        x='store_label',
        y='clicks',
        color='brand',
        barmode='group',
        title='Top 3 Brands for Top 5 Stores',
        color_discrete_sequence=px.colors.sequential.Greens[3:],
        labels={'clicks': 'Total Clicks', 'store_label': 'Store'}
    )
    # Store Engagement Comparison (unchanged)
    engagement_chart = px.bar(
        store_data['engagement_data'],
        x='store_label',
        y='click_count',
        color='click_type',
        barmode='group',
        title='Store Engagement Comparison',
        color_discrete_sequence=['#4CAF50', '#2E7D32'],
        labels={'click_count': 'Clicks', 'store_label': 'Store'}
    )
    engagement_chart.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Store Price Trends Over Time - Now with dropdown
    # First create figure with all stores (hidden by default)
    price_trends_chart = px.line(
        store_data['price_data'].sort_values('date_price'),
        x='date_price',
        y='price',
        color='store_label',
        title='Store Price Trends Over Time - Select Store',
        color_discrete_sequence=px.colors.sequential.Greens[3:],
        labels={'price': 'Price ($)', 'date_price': 'Date'}
    )
    
    # Create dropdown options
    store_options = [{'label': 'All Stores', 'value': 'ALL'}]
    store_options += [
        {'label': store, 'value': store} 
        for store in store_data['price_data']['store_label'].unique()
    ]
    
    # Store Deal Frequency (unchanged)
    deal_frequency_chart = px.bar(
        store_data['deal_data'],
        x='store_label',
        y='count',
        color='deal_type',
        barmode='stack',
        title='Store Deal Frequency',
        color_discrete_sequence=['#81C784', '#66BB6A', '#43A047'],
        labels={'count': 'Number of Deals', 'store_label': 'Store'}
    )
    deal_frequency_chart.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

     # Create base figure for top products (empty - will be updated by callback)
    top_products_chart = px.bar(
        title="Select a store to view its top 5 most expensive products"
    )
    top_products_chart.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Price ($)",
        yaxis_title="Product"
    )
    
    return {
        'engagement_treemap': engagement_treemap,
        'top_products_chart': top_products_chart,
        'top_brands_chart': top_brands_chart,
        'engagement_chart': engagement_chart,
        'price_trends_chart': price_trends_chart,
        'deal_frequency_chart': deal_frequency_chart,
        'store_options': store_options,
        'top_products_chart': top_products_chart,
        'store_product_options': store_data['store_product_options']
    }
figures = create_store_visualizations(store_data)
# =============================================
# Callback for Store Selection
# =============================================

@callback(
    Output('price-trends-chart', 'figure'),
    Input('store-selector', 'value')
)
@callback(
    Output('top-products-chart', 'figure'),
    Input('product-store-selector', 'value')
)
def update_price_trends(selected_store):
    # Filter data if a specific store is selected
    if selected_store != 'ALL':
        filtered_data = store_data['price_data'][store_data['price_data']['store_label'] == selected_store]
        fig = px.line(
            filtered_data.sort_values('date_price'),
            x='date_price',
            y='price',
            title=f'Price Trends for {selected_store}',
            color_discrete_sequence=['#2E7D32'],  # Single green color for single store
            hover_data=['product_name']  # Include product name in hover data
        )
    else:
        # Show all stores
        fig = px.line(
            store_data['price_data'].sort_values('date_price'),
            x='date_price',
            y='price',
            color='store_label',
            title='Store Price Trends - All Stores',
            color_discrete_sequence=px.colors.sequential.Greens[3:],
            hover_data=['product_name']  # Include product name in hover data
        )
    
    # Common formatting
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified',
        xaxis_title='Date',
        yaxis_title='Price ($)',
        showlegend=selected_store == 'ALL'  # Only show legend when showing all stores
    )
    
    # Format hover template based on selection
    if selected_store == 'ALL':
        fig.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>Product: %{customdata[0]}<br>Date: %{x|%d-%m-%y}<br>Price: $%{y:.2f}"
        )
    else:
        fig.update_traces(
            hovertemplate="<b>%{customdata[0]}</b><br>Date: %{x|%d-%m-%y}<br>Price: $%{y:.2f}"
        )
    
    return fig
def update_top_products(selected_store):
    if not selected_store:
        return px.bar(title="Select a store to view its top 5 most expensive products")
    
    filtered = store_data['top_products'][store_data['top_products']['store_label'] == selected_store] \
              .sort_values('price', ascending=True)
    
    fig = px.bar(
        filtered,
        x='price',
        y='title',
        orientation='h',
        title=f'Top 5 Most Expensive Products at {selected_store}',
        color_discrete_sequence=['#2E7D32'],
        labels={'price': 'Price ($)', 'title': 'Product'}
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        yaxis={'categoryorder':'total ascending'}
    )
    return fig
# =============================================
# Updated Dashboard Layout
# =============================================

layout = dbc.Container(
    [
        # Header Section (unchanged)
        html.Div(
            [
                html.H1("Store Performance Dashboard", className="page-header"),
                html.P("Analyze store engagement, pricing trends, and deal frequency", 
                      className="page-subtitle"),
            ],
            className="header-section"
        ),
        
        # Summary Cards (unchanged)
        dbc.Row(
            [
                dbc.Col(create_card("Total Stores", f"{store_data['total_stores']:,}", "fa-store"), width=4),
                dbc.Col(create_card("Avg Price", f"${store_data['avg_price']:,.2f}", "fa-tag"), width=4),
                dbc.Col(create_card("Total Deals", f"{store_data['total_deals']:,}", "fa-percentage"), width=4),
            ],
            className="summary-cards-row",
        ),
        # Top Products Section with Dropdown
        html.H2("Product Pricing Analysis", className="section-header"),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='product-store-selector',
                    options=figures['store_product_options'],
                    placeholder="Select a store...",
                    className="store-selector"
                ),
                dcc.Graph(
                    id='top-products-chart',
                    figure=figures['top_products_chart'],
                    className="chart-card",
                    style={"height": "500px"}  # Fixed reasonable height
                )
            ], width=12)
        ], className="chart-row"),
        # New Visualizations Section
        html.H2("Store Performance Highlights", className="section-header"),
        
        # Top Stores Treemap and Top Brands
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    figure=figures['engagement_treemap'],
                    className="chart-card",
                    style={"height": "500px"}
                ),
                width=6
            ),
            dbc.Col(
                dcc.Graph(
                    figure=figures['top_brands_chart'],
                    className="chart-card",
                    style={"height": "500px"}
                ),
                width=6
            ),
        ], className="chart-row"),
        
        # Top Products Chart (full width)
        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    figure=figures['top_products_chart'],
                    className="chart-card",
                    style={"height": "800px"}  # Taller to show all products
                ),
                width=12
            ),
            className="chart-row"
        ),
        # Engagement Metrics (unchanged)
        html.H2("Engagement Metrics", className="section-header"),
        dbc.Row(dbc.Col(dcc.Graph(figure=figures['engagement_chart'], className="chart-card"), className="chart-row")),
        
        # Pricing Trends with Dropdown
        html.H2("Pricing Trends", className="section-header"),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='store-selector',
                    options=figures['store_options'],
                    value='ALL',
                    clearable=False,
                    className="store-selector"
                ),
                dcc.Graph(
                    id='price-trends-chart',
                    figure=figures['price_trends_chart'],
                    className="chart-card"
                )
            ], width=12)
        ], className="chart-row"),
        
        # Deal Performance (unchanged)
        html.H2("Deal Performance", className="section-header"),
        dbc.Row(dbc.Col(dcc.Graph(figure=figures['deal_frequency_chart'], className="chart-card"), className="chart-row")),
    ],
    fluid=True,
    className="dashboard-container"
)

# def create_store_visualizations(store_data):
#     """Create all store visualizations with green color scheme"""
#     # Store Engagement Comparison
#     engagement_chart = px.bar(
#         store_data['engagement_data'],
#         x='store_label',
#         y='click_count',
#         color='click_type',
#         barmode='group',
#         title='Store Engagement Comparison',
#         color_discrete_sequence=['#4CAF50', '#2E7D32'],
#         labels={'click_count': 'Clicks', 'store_label': 'Store'}
#     )
#     engagement_chart.update_layout(
#         plot_bgcolor='rgba(0,0,0,0)',
#         paper_bgcolor='rgba(0,0,0,0)'
#     )
    
#     # Store Price Trends Over Time
#     price_trends_chart = px.line(
#         store_data['price_data'].sort_values('date_price'),
#         x='date_price',
#         y='price',
#         color='store_label',
#         title='Store Price Trends Over Time',
#         color_discrete_sequence=px.colors.sequential.Greens[3:],
#         labels={'price': 'Price ($)', 'date_price': 'Date'}
#     )
#     price_trends_chart.update_layout(
#         plot_bgcolor='rgba(0,0,0,0)',
#         paper_bgcolor='rgba(0,0,0,0)',
#         hovermode='x unified'
#     )
    
#     # Store Deal Frequency
#     deal_frequency_chart = px.bar(
#         store_data['deal_data'],
#         x='store_label',
#         y='count',
#         color='deal_type',
#         barmode='stack',
#         title='Store Deal Frequency',
#         color_discrete_sequence=['#81C784', '#66BB6A', '#43A047'],
#         labels={'count': 'Number of Deals', 'store_label': 'Store'}
#     )
#     deal_frequency_chart.update_layout(
#         plot_bgcolor='rgba(0,0,0,0)',
#         paper_bgcolor='rgba(0,0,0,0)'
#     )
    
#     return {
#         'engagement_chart': engagement_chart,
#         'price_trends_chart': price_trends_chart,
#         'deal_frequency_chart': deal_frequency_chart
#     }


