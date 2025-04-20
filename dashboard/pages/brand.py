import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from utils.functions import create_card
import pandas as pd
from utils.data import data_import
import plotly.express as px

# Initialize the Dash page
dash.register_page(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    path="/brands_overview",
)

# =============================================
# Load data
# =============================================

df=data_import()

# =============================================
# Data Preparation
# =============================================

def prepare_chart_data(df):
    """Prepare all data needed for visualizations"""
    # For availability pie chart
    availability_counts = df.groupby(['brand', 'availability']).size().reset_index(name='count')
    
    # Calculate median prices for each brand
    median_prices = df.groupby('brand')['price'].median().sort_values(ascending=False)
    
    # For top brands by product count (for treemap)
    brand_counts = df['brand'].value_counts().reset_index()
    brand_counts.columns = ['brand', 'count']
    brand_counts=brand_counts[brand_counts['brand'] != 'na']
    top_brands = brand_counts.nlargest(5, 'count')
   
    return {
        'availability_counts': availability_counts,
        'top_brands': top_brands,
        'median_prices': median_prices,
        'brands_count': df['brand'][df['brand'] != 'na'].nunique(),
        'total_products': len(df),
        'avg_price': df['price'].mean()
    }

chart_data = prepare_chart_data(df)

# =============================================
# Visualizations
# =============================================

def create_visualizations(df, chart_data):
    """Create all visualization figures"""
    # Top Brands by Clicks (Bar Chart)
    fig01 = px.bar(
        df.sort_values('clicks', ascending=False).head(20),
        x="brand", 
        y="clicks", 
        title="Top 20 Brands by Clicks",
        color="clicks",
        color_continuous_scale='oranges'
    )
    
    # Brand Price Distribution (Box Plot)
    fig02 = px.box(
        df,
        x="brand", 
        y="price", 
        title="Brand Price Distribution (Ordered by Median Price)",
        category_orders={"brand": chart_data['median_prices'].index.tolist()},
        color="brand"
    ).update_traces(boxpoints='outliers')
    
    # Brand Availability (Pie Chart)
    fig03 = px.pie(
        chart_data['availability_counts'],
        names='brand',
        values='count',
        title='Brand Availability Breakdown',
        hover_data=['availability'],
        hole=0.3
    )
    
    # Top Brands Treemap
    brands_treemap = px.treemap(
        chart_data['top_brands'],
        path=['brand'],
        values='count',
        title='Top 5 Brands by Product Count',
        color='count',
        color_continuous_scale='Reds'
    )
    
    return {
        'clicks_bar': fig01,
        'price_box': fig02,
        'availability_pie': fig03,
        'brands_treemap': brands_treemap
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
                html.H1("Brand Analysis Dashboard", className="page-header"),
                html.P("This dashboard provides insights into product performance across different brands.", 
                      className="page-subtitle"),
            ],
            className="header-section"
        ),
        
        # Summary Cards
        dbc.Row(
            [
              dbc.Col(
                  create_card(
                      "Number of Brands",
                      f"{chart_data['brands_count']:,}",
                      "fa-tags"
                  ),
                  width=4,
              ),
              dbc.Col(
                  create_card(
                      "Total Products",
                      f"{chart_data['total_products']:,}",
                      "fa-boxes"
                  ),
                  width=4,
              ),
              dbc.Col(
                  create_card(
                      "Avg Price",
                      f"{chart_data['avg_price']:.2f} DT",
                      "fa-tag"
                  ),
                  width=4,
              ),
          ],className="summary-cards-row",
      ),
        
        # Main Visualizations
        html.H2("Brand Performance Metrics", className="section-header"),
        
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        figure=figures['clicks_bar'],
                        config={"displayModeBar": False},
                        className="chart-card",
                        style={"height": "500px"}
                    ),
                    width=6
                ),
                dbc.Col(
                    dcc.Graph(
                        figure=figures['price_box'],
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
                        figure=figures['availability_pie'],
                        config={"displayModeBar": False},
                        className="chart-card",
                        style={"height": "500px"}
                    ),
                    width=6
                ),
                dbc.Col(
                    dcc.Graph(
                        figure=figures['brands_treemap'],
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
