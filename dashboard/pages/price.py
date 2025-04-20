import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from utils.functions import create_card
import pandas as pd
import plotly.express as px
import json
from datetime import datetime

# Initialize the Dash page
dash.register_page(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    path="/price_overview",
)

# Load and prepare data
df = pd.read_csv('products.csv')

# =============================================
# Data Preparation
# =============================================

def prepare_chart_data(df):
    """Prepare all data needed for visualizations"""
    # Parse the priceTable column to extract price history data
    df['priceTable'] = df['priceTable'].apply(
    lambda x: json.loads(x.replace("'", '"')) if isinstance(x, str) else x
)

    
    # Create price distribution data
    price_distribution = df['price'].value_counts().reset_index()
    price_distribution.columns = ['price_point', 'count']
    price_distribution = price_distribution.sort_values('price_point')
    
    # Calculate price statistics by brand
    price_by_brand = df.groupby('brand')['price'].agg(['mean', 'median', 'min', 'max']).reset_index()
    price_by_brand = price_by_brand.sort_values('median', ascending=False).head(10)
    
    # Price range distribution by store
    price_by_store = df.groupby('store_label')['price'].agg(['count', 'mean', 'median']).reset_index()
    price_by_store = price_by_store.sort_values('count', ascending=False).head(15)
    
    # Extract price history for time series
    price_history = []
    for idx, row in df.iterrows():
        if isinstance(row['priceTable'], list):
            for entry in row['priceTable']:
                if 'date_price' in entry and 'price' in entry:
                    try:
                        date = datetime.strptime(entry['date_price'].split('T')[0], '%Y-%m-%d')
                        price_history.append({
                            'date': date,
                            'price': entry['price'],
                            'product_id': row['uniqueID'],
                            'product_name': row['title']
                        })
                    except:
                        pass
    
    price_history_df = pd.DataFrame(price_history)
    if not price_history_df.empty:
        price_history_df = price_history_df.sort_values('date')
    
    return {
        'price_distribution': price_distribution,
        'price_by_brand': price_by_brand,
        'price_by_store': price_by_store,
        'price_history_df': price_history_df,
        'avg_price': df['price'].mean(),
        'median_price': df['price'].median(),
        'product_count': len(df)
    }

chart_data = prepare_chart_data(df)

# =============================================
# Visualizations
# =============================================

def create_visualizations(df, chart_data):
    """Create all visualization figures"""
    # Price Distribution Histogram
    fig01 = px.histogram(
        df,
        x="price",
        nbins=50,
        title="Price Distribution of Products",
        color_discrete_sequence=["#636EFA"],
    )
    
    # Price by Brand (Bar Chart)
    fig02 = px.bar(
        chart_data['price_by_brand'],
        x="brand",
        y="median",
        title="Median Price by Top 10 Brands",
        color="median",
        color_continuous_scale='blues',
        error_y="max",
        error_y_minus="min"
    )
    
    # Price by Store (Bar Chart) - Replacement for price drop visualization
    fig03 = px.bar(
        chart_data['price_by_store'],
        x="store_label",
        y="median",
        title="Median Price by Top 15 Stores",
        color="count",
        color_continuous_scale='purples',
        hover_data=["mean", "count"]
    )
    fig03.update_layout(xaxis_tickangle=-45)
    
    # Price Evolution Over Time (Line Chart)
    if not chart_data['price_history_df'].empty:
        # Group by date and calculate average price
        avg_price_over_time = chart_data['price_history_df'].groupby('date')['price'].mean().reset_index()
        
        # Create figure with improved hover information
        fig04 = px.line(
            avg_price_over_time,
            x="date",
            y="price",
            title="Average Price Evolution Over Time",
            line_shape="spline"
        )
        
        # Add a scatter trace for hover points with product information
        scatter_df = chart_data['price_history_df'].copy()
        fig04.add_trace(
            px.scatter(
                scatter_df,
                x="date",
                y="price",
                hover_data=["product_name", "product_id"],
                opacity=0.1
            ).data[0]
        )
        
        # Improve the hover template
        fig04.update_traces(
            hovertemplate="<b>Date:</b> %{x}<br><b>Price:</b> $%{y:.2f}<br><b>Product:</b> %{customdata[0]}<extra></extra>",
            selector=dict(type="scatter", mode="markers")
        )
    else:
        # Create empty figure if no data
        fig04 = px.line(title="Price Evolution Over Time (No data available)")
    
    return {
        'price_distribution': fig01,
        'price_by_brand': fig02,
        'price_by_store': fig03,
        'price_evolution': fig04
    }

figures = create_visualizations(df, chart_data)

# =============================================
# Dashboard Layout
# =============================================

layout = dbc.Container(
    [
        # Header Section
        html.Div(
            [
                html.H1("Price Analysis Dashboard", className="page-header"),
                html.P("This dashboard provides insights into product pricing trends and distribution.", 
                      className="page-subtitle"),
            ],
            className="header-section"
        ),
        
        # Summary Cards
        dbc.Row(
            [
              dbc.Col(
                  create_card(
                      "Average Price",
                      f"${chart_data['avg_price']:.2f}",
                      "fa-tag"
                  ),
                  width=4,
              ),
              dbc.Col(
                  create_card(
                      "Median Price",
                      f"${chart_data['median_price']:.2f}",
                      "fa-dollar-sign"
                  ),
                  width=4,
              ),
              dbc.Col(
                  create_card(
                      "Total Products",
                      f"{chart_data['product_count']:,}",
                      "fa-boxes"
                  ),
                  width=4,
              ),
          ],className="summary-cards-row",
      ),
        
        # Main Visualizations
        html.H2("Price Performance Metrics", className="section-header"),
        
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        figure=figures['price_distribution'],
                        config={"displayModeBar": False},
                        className="chart-card",
                        style={"height": "500px"}
                    ),
                    width=6
                ),
                dbc.Col(
                    dcc.Graph(
                        figure=figures['price_by_brand'],
                        config={"displayModeBar": False},
                        className="chart-card",
                        style={"height": "500px"}
                    ),
                    width=6
                ),
            ],
            className="chart-row"
        ),
        
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        figure=figures['price_by_store'],
                        config={"displayModeBar": False},
                        className="chart-card",
                        style={"height": "500px"}
                    ),
                    width=6
                ),
                dbc.Col(
                    dcc.Graph(
                        figure=figures['price_evolution'],
                        config={"displayModeBar": False},
                        className="chart-card",
                        style={"height": "500px"}
                    ),
                    width=6
                ),
            ],
            className="chart-row"
        ),
    ],
    fluid=True,
    className="dashboard-container"
)