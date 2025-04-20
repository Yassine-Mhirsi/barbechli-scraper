import dash
from dash import callback, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from utils.functions import create_card
from utils.data import data_import
import pandas as pd
import plotly.express as px
import json
from dateutil.parser import parse  # Using dateutil for more flexible date parsing

# Initialize the Dash page
dash.register_page(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    path="/store_overview",
)

# =============================================
# Load and prepare data
# =============================================

df=data_import()

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
    store_engagement = store_engagement.sort_values('click_count', ascending=False)
    top_stores = store_engagement.head(5)['store_label'].tolist()
    
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
    
    # Clean deal type names for better display
    deal_data['deal_type'] = deal_data['deal_type'].replace({
        'price_deal': 'Regular Deal',
        'price_hot_deal': 'Hot Deal',
        'price_top_deal': 'Top Deal'
    })
    
    # Parse priceTable data safely
    price_records = []
    for idx, row in df.iterrows():
        try:
            # Try to parse the price table data
            if isinstance(row['priceTable'], str):
                try:
                    price_table = json.loads(row['priceTable'])
                except json.JSONDecodeError:
                    # Try with single quote replacement
                    price_table = json.loads(row['priceTable'].replace("'", '"'))
            else:
                price_table = row['priceTable']
                
            # Process each price record
            if isinstance(price_table, list):
                for entry in price_table:
                    try:
                        dt = parse(entry['date_price'])
                        price_records.append({
                            'store_label': row['store_label'],
                            'product_name': row['title'],
                            'product_id': row['uniqueID'],
                            'date_price': dt.strftime('%Y-%m-%d'),
                            'price': float(entry['price'])
                        })
                    except (ValueError, KeyError, TypeError):
                        continue
        except (json.JSONDecodeError, TypeError, AttributeError):
            continue
    
    price_data = pd.DataFrame(price_records)
    if not price_data.empty:
        price_data['date_price'] = pd.to_datetime(price_data['date_price'])
        price_data = price_data.sort_values('date_price')
    
    # Get top 5 most expensive products per store
    top_products = df.sort_values(['store_label', 'price'], ascending=[True, False]) \
                   .groupby('store_label').head(5)
    
    # Get top 3 brands per store (for top 5 stores)
    top_brands = df[df['store_label'].isin(top_stores)] \
               .groupby(['store_label', 'brand'])['clicks'].sum().reset_index() \
               .sort_values(['store_label', 'clicks'], ascending=[True, False]) \
               .groupby('store_label').head(3)
    
    # Average price per store
    avg_price_by_store = df.groupby('store_label')['price'].mean().reset_index()
    avg_price_by_store = avg_price_by_store.sort_values('price', ascending=False)
    
    # Store product count
    product_count_by_store = df.groupby('store_label')['uniqueID'].count().reset_index()
    product_count_by_store.columns = ['store_label', 'product_count']
    
    # Calculate summary stats
    stats = {
        'total_stores': df['store_label'].nunique(),
        'avg_price': df['price'].mean(),
        'total_deals': df[['price_deal', 'price_hot_deal', 'price_top_deal']].sum().sum(),
        'total_products': len(df)
    }
    
    # Create store options for dropdown
    store_options = [{'label': 'All Stores', 'value': 'ALL'}]
    store_options += [{'label': store, 'value': store} 
                    for store in df['store_label'].unique() if pd.notna(store)]
    
    return {
        'engagement_data': engagement_data,
        'store_engagement': store_engagement,
        'deal_data': deal_data,
        'price_data': price_data,
        'top_products': top_products,
        'top_brands': top_brands,
        'top_stores': top_stores,
        'avg_price_by_store': avg_price_by_store,
        'product_count_by_store': product_count_by_store,
        'store_options': store_options,
        **stats
    }

store_data = prepare_store_data(df)

# =============================================
# Visualizations
# =============================================
def create_store_visualizations(store_data):
    """Create all store visualization figures"""
    
    # 1. Store Engagement Treemap (Top 5 Stores)
    engagement_treemap = px.treemap(
        store_data['store_engagement'].head(5),
        path=['store_label'],
        values='click_count',
        title='Top 5 Stores by Total Engagement',
        color='click_count',
        color_continuous_scale='Greens',
        hover_data=['click_count']
    )
    engagement_treemap.update_traces(
        textinfo="label+value",
        hovertemplate="<b>%{label}</b><br>Engagement: %{value:,}"
    )
    
    # 2. Store Engagement Comparison
    engagement_chart = px.bar(
        store_data['engagement_data'].groupby(['store_label', 'click_type'])['click_count'].sum().reset_index(),
        x='store_label',
        y='click_count',
        color='click_type',
        barmode='group',
        title='Store Engagement Comparison',
        color_discrete_sequence=['#4CAF50', '#2E7D32'],
        labels={'click_count': 'Clicks', 'store_label': 'Store'}
    )
    engagement_chart.update_layout(
        xaxis_tickangle=-45,
        xaxis_title="Store",
        yaxis_title="Number of Clicks"
    )
    
    # 3. Top Brands per Store (Grouped Bar Chart)
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
    top_brands_chart.update_layout(
        xaxis_tickangle=-45,
        xaxis_title="Store",
        yaxis_title="Total Clicks"
    )
    
    # 4. Average Price by Store
    avg_price_chart = px.bar(
        store_data['avg_price_by_store'].head(10),
        x='store_label',
        y='price',
        title='Average Price by Top 10 Stores',
        color='price',
        color_continuous_scale='Greens',
        labels={'price': 'Average Price ($)', 'store_label': 'Store'}
    )
    avg_price_chart.update_layout(
        xaxis_tickangle=-45,
        xaxis_title="Store",
        yaxis_title="Average Price ($)"
    )
    
    # 5. Store Deal Frequency
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
        xaxis_tickangle=-45,
        xaxis_title="Store",
        yaxis_title="Number of Deals"
    )
    
    # 6. Price Trends Chart (base figure - will be updated by callback)
    price_trends_chart = px.line(
        title="Store Price Trends Over Time - Select a Store"
    )
    
    # 7. Product Count by Store
    product_count_chart = px.bar(
        store_data['product_count_by_store'].sort_values('product_count', ascending=False).head(10),
        x='store_label',
        y='product_count',
        title='Product Count by Top 10 Stores',
        color='product_count',
        color_continuous_scale='Greens',
        labels={'product_count': 'Number of Products', 'store_label': 'Store'}
    )
    product_count_chart.update_layout(
        xaxis_tickangle=-45,
        xaxis_title="Store",
        yaxis_title="Number of Products"
    )
    
    return {
        'engagement_treemap': engagement_treemap,
        'engagement_chart': engagement_chart,
        'top_brands_chart': top_brands_chart,
        'avg_price_chart': avg_price_chart,
        'deal_frequency_chart': deal_frequency_chart,
        'price_trends_chart': price_trends_chart,
        'product_count_chart': product_count_chart
    }

figures = create_store_visualizations(store_data)

# =============================================
# Callbacks for Interactive Features
# =============================================

@callback(
    Output('price-trends-chart', 'figure'),
    Input('store-selector', 'value')
)
def update_price_trends(selected_store):
    """Update price trends chart based on selected store"""
    # Check if price data is available
    if store_data['price_data'].empty:
        fig = px.line(title="No price history data available")
        fig.update_layout(
            annotations=[{
                'text': 'No price history data available for this selection',
                'showarrow': False,
                'font': {'size': 16}
            }]
        )
        return fig
    
    # Filter data if a specific store is selected
    if selected_store != 'ALL':
        filtered_data = store_data['price_data'][store_data['price_data']['store_label'] == selected_store]
        
        # Check if filtered data is empty
        if filtered_data.empty:
            fig = px.line(title=f"No price history data available for {selected_store}")
            fig.update_layout(
                annotations=[{
                    'text': f'No price history data available for {selected_store}',
                    'showarrow': False,
                    'font': {'size': 16}
                }]
            )
            return fig
        
        fig = px.line(
            filtered_data.sort_values('date_price'),
            x='date_price',
            y='price',
            title=f'Price Trends for {selected_store}',
            color_discrete_sequence=['#2E7D32'],
            hover_data=['product_name']
        )
    else:
        # Show all stores with data
        fig = px.line(
            store_data['price_data'].sort_values('date_price'),
            x='date_price',
            y='price',
            color='store_label',
            title='Store Price Trends - All Stores',
            color_discrete_sequence=px.colors.sequential.Greens[3:],
            hover_data=['product_name']
        )
    
    # Common formatting
    fig.update_layout(
        hovermode='x unified',
        xaxis_title='Date',
        yaxis_title='Price ($)',
        showlegend=selected_store == 'ALL'
    )
    
    # Format hover template based on selection
    if selected_store == 'ALL':
        fig.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>Product: %{customdata[0]}<br>Date: %{x|%Y-%m-%d}<br>Price: $%{y:.2f}"
        )
    else:
        fig.update_traces(
            hovertemplate="<b>%{customdata[0]}</b><br>Date: %{x|%Y-%m-%d}<br>Price: $%{y:.2f}"
        )
    
    return fig

# =============================================
# Dashboard Layout
# =============================================

layout = dbc.Container(
    [
        # Header Section
        html.Div(
            [
                html.H1("Store Performance Dashboard", className="page-header"),
                html.P("Analyze store engagement, pricing trends, and product performance", 
                      className="page-subtitle"),
            ],
            className="header-section"
        ),
        
        # Summary Cards
        dbc.Row(
            [
                dbc.Col(create_card("Total Stores", f"{store_data['total_stores']:,}", "fa-store"), width=4),
                dbc.Col(create_card("Avg Price", f"${store_data['avg_price']:.2f}", "fa-tag"), width=4),
                dbc.Col(create_card("Total Products", f"{store_data['total_products']:,}", "fa-box"), width=4),
            ],
            className="summary-cards-row",
        ),
        
        # Pricing Trends with Dropdown
        html.H2("Pricing Trends", className="section-header"),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='store-selector',
                    options=store_data['store_options'],
                    value='ALL',
                    clearable=False,
                    className="store-selector"
                ),
                dcc.Graph(
                    id='price-trends-chart',
                    figure=figures['price_trends_chart'],
                    className="chart-card",
                    style={"height": "500px"}
                )
            ], width=12)
        ], className="chart-row"),
        
        # Store Engagement Section
        html.H2("Store Engagement", className="section-header"),
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
                    figure=figures['engagement_chart'],
                    className="chart-card",
                    style={"height": "500px"}
                ),
                width=6
            ),
        ], className="chart-row"),
        
        # Store Products and Brands Section
        html.H2("Products and Brands", className="section-header"),
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    figure=figures['product_count_chart'],
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
        
        # Store Pricing Section
        html.H2("Store Pricing Analysis", className="section-header"),
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    figure=figures['avg_price_chart'],
                    className="chart-card",
                    style={"height": "500px"}
                ),
                width=6
            ),
            dbc.Col(
                dcc.Graph(
                    figure=figures['deal_frequency_chart'],
                    className="chart-card",
                    style={"height": "500px"}
                ),
                width=6
            ),
        ], className="chart-row"),
        
        # Explanation Section
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        html.H3("Understanding Store Metrics", className="mt-4"),
                        html.P([
                            html.Strong("Engagement: "), 
                            "Total clicks and external clicks received by products from each store."
                        ]),
                        html.P([
                            html.Strong("Pricing Trends: "), 
                            "Historical price data showing how product prices have changed over time."
                        ]),
                        html.P([
                            html.Strong("Deal Frequency: "), 
                            "Distribution of regular deals, hot deals, and top deals across stores."
                        ]),
                    ],
                    className="info-section"
                ),
                width=12
            ),
            className="mt-4"
        )
    ],
    fluid=True,
    className="dashboard-container"
)