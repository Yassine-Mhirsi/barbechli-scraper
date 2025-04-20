import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from utils.functions import create_card
import pandas as pd
import plotly.express as px
import numpy as np

# Initialize the Dash page
dash.register_page(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    path="/engagement_overview",
)

# Load and prepare data
df = pd.read_csv('products.csv')

# =============================================
# Data Preparation
# =============================================

def prepare_chart_data(df):
    """Prepare all data needed for visualizations"""
    # Create data for clicks comparison
    clicks_comparison = df.melt(
        id_vars=['brand', 'title', 'uniqueID'],
        value_vars=['clicks', 'clicksExternal'],
        var_name='click_type',
        value_name='click_count'
    )
    
    # Calculate click statistics by brand
    brand_engagement = df.groupby('brand').agg({
        'clicks': 'sum',
        'clicksExternal': 'sum'
    }).reset_index()
    brand_engagement['click_ratio'] = brand_engagement['clicksExternal'] / brand_engagement['clicks']
    brand_engagement = brand_engagement.sort_values('clicks', ascending=False).head(10)
    
    # Calculate engagement by availability
    availability_engagement = df.groupby('availability').agg({
        'clicks': 'sum',
        'clicksExternal': 'sum',
        'uniqueID': 'count'
    }).reset_index()
    availability_engagement['clicks_per_product'] = availability_engagement['clicks'] / availability_engagement['uniqueID']
    availability_engagement['external_clicks_per_product'] = availability_engagement['clicksExternal'] / availability_engagement['uniqueID']
    
    # Top products by engagement
    df['total_engagement'] = df['clicks'] + df['clicksExternal']
    top_products = df.sort_values('total_engagement', ascending=False).head(15)
    
    # Create engagement metrics for store comparison
    store_engagement = df.groupby('store_label').agg({
        'clicks': 'sum',
        'clicksExternal': 'sum',
        'uniqueID': 'count'
    }).reset_index()
    store_engagement['conversion_rate'] = (store_engagement['clicksExternal'] / store_engagement['clicks'] * 100).round(2)
    store_engagement = store_engagement.sort_values('clicks', ascending=False).head(10)
    brand_engagement_notna=brand_engagement[brand_engagement['brand']!='na']
    return {
        'clicks_comparison': clicks_comparison,
        'brand_engagement': brand_engagement,
        'brand_engagement_notna': brand_engagement_notna,
        'availability_engagement': availability_engagement,
        'top_products': top_products,
        'store_engagement': store_engagement,
        'total_clicks': df['clicks'].sum(),
        'total_external_clicks': df['clicksExternal'].sum(),
        'conversion_rate': (df['clicksExternal'].sum() / df['clicks'].sum() * 100) if df['clicks'].sum() > 0 else 0
    }

chart_data = prepare_chart_data(df)

# =============================================
# Visualizations
# =============================================

def create_visualizations(df, chart_data):
    """Create all visualization figures"""
    # Clicks vs. External Clicks by Brand
    fig01 = px.bar(
        chart_data['brand_engagement_notna'],
        x="brand",
        y=["clicks", "clicksExternal"],
        title="Clicks vs. External Clicks by Top 10 Brands",
        barmode="group",
        color_discrete_sequence=["#1F77B4", "#FF7F0E"]
    )
    fig01.update_layout(
        xaxis_title="Brand",
        yaxis_title="Number of Clicks",
        legend_title="Click Type"
    )
    
    # Engagement by Availability Status
    availability_data = chart_data['availability_engagement'].melt(
        id_vars=['availability', 'uniqueID'],
        value_vars=['clicks_per_product', 'external_clicks_per_product'],
        var_name='metric',
        value_name='value'
    )
    
    fig02 = px.bar(
        availability_data,
        x="availability",
        y="value",
        color="metric",
        title="Engagement Metrics by Product Availability",
        barmode="group",
        color_discrete_sequence=["#2CA02C", "#D62728"]
    )
    fig02.update_layout(
        xaxis_title="Availability Status",
        yaxis_title="Average Clicks per Product",
        legend_title="Metric"
    )
    
    # Top Products by Engagement
    fig03 = px.bar(
        chart_data['top_products'],
        x="total_engagement",
        y="title",
        orientation="h",
        title="Top 15 Products by Total Engagement",
        color="total_engagement",
        color_continuous_scale="viridis",
        hover_data=["clicks", "clicksExternal"]
    )
    fig03.update_layout(
        xaxis_title="Total Engagement (Clicks)",
        yaxis_title="Product",
        yaxis=dict(autorange="reversed")
    )
    
    # Conversion Rate by Store (External Clicks / Total Clicks)
    fig04 = px.bar(
        chart_data['store_engagement'],
        x="store_label",
        y="conversion_rate",
        title="Conversion Rate by Top 10 Stores (External Clicks / Total Clicks)",
        color="conversion_rate",
        color_continuous_scale="RdYlGn",
        hover_data=["clicks", "clicksExternal", "uniqueID"]
    )
    fig04.update_layout(
        xaxis_title="Store",
        yaxis_title="Conversion Rate (%)",
        xaxis_tickangle=-45
    )
    
    return {
        'clicks_by_brand': fig01,
        'engagement_by_availability': fig02,
        'top_products': fig03,
        'conversion_by_store': fig04
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
                html.H1("Engagement Analysis Dashboard", className="page-header"),
                html.P("This dashboard provides insights into user engagement metrics, focusing on the relationship between clicks and external clicks.", 
                      className="page-subtitle"),
            ],
            className="header-section"
        ),
        
        # Summary Cards
        dbc.Row(
            [
              dbc.Col(
                  create_card(
                      "Total Clicks",
                      f"{chart_data['total_clicks']:,}",
                      "fa-mouse-pointer"
                  ),
                  width=4,
              ),
              dbc.Col(
                  create_card(
                      "External Clicks",
                      f"{chart_data['total_external_clicks']:,}",
                      "fa-external-link-alt"
                  ),
                  width=4,
              ),
              dbc.Col(
                  create_card(
                      "Conversion Rate",
                      f"{chart_data['conversion_rate']:.2f}%",
                      "fa-chart-line"
                  ),
                  width=4,
              ),
          ],className="summary-cards-row",
      ),
        
        # Main Visualizations
        html.H2("Engagement Performance Metrics", className="section-header"),
        
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        figure=figures['clicks_by_brand'],
                        config={"displayModeBar": False},
                        className="chart-card",
                        style={"height": "500px"}
                    ),
                    width=6
                ),
                dbc.Col(
                    dcc.Graph(
                        figure=figures['engagement_by_availability'],
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
                        figure=figures['top_products'],
                        config={"displayModeBar": False},
                        className="chart-card",
                        style={"height": "500px"}
                    ),
                    width=6
                ),
                dbc.Col(
                    dcc.Graph(
                        figure=figures['conversion_by_store'],
                        config={"displayModeBar": False},
                        className="chart-card",
                        style={"height": "500px"}
                    ),
                    width=6
                ),
            ],
            className="chart-row"
        ),
        
        # Explanation Section
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        html.H3("Understanding Clicks vs. External Clicks", className="mt-4"),
                        html.P([
                            html.Strong("Clicks: "), 
                            "Total number of times users interacted with the product listing on the platform."
                        ]),
                        html.P([
                            html.Strong("External Clicks: "), 
                            "Number of times users clicked through to the external retailer's website to potentially make a purchase."
                        ]),
                        html.P([
                            html.Strong("Conversion Rate: "), 
                            "The percentage of total clicks that resulted in external clicks, indicating potential purchase intent."
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