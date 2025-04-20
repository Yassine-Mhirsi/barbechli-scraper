import dash
from dash import callback, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from utils.functions import create_card
import pandas as pd
import plotly.express as px

dash.register_page(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    path="/engagement_overview",
)

df=pd.read_csv('products.csv')

# Clicks vs. Clicks External	Bar Chart	clicks, clicksExternal
# Melt the DataFrame to long format for clicks and clicksExternal
df_long31 = df.melt(
    id_vars=['brand','title'],               # Keep uniqueID as identifier (or another column like 'title')
    value_vars=['clicks', 'clicksExternal'], # Columns to compare
    var_name='click_type',              # Name of the new category column
    value_name='click_count'            # Name of the new value column
)

# Create the Bar Chart
fig31 = px.bar(
    df_long31, 
    x='brand',                       # X-axis: one bar per product
    y='click_count',                    # Y-axis: number of clicks
    color='click_type',                 # Different colors for clicks vs clicksExternal
    barmode='group',                    # Group bars side-by-side
    title='Clicks vs. Clicks External',
    hover_name='title',               # Show product name on hover

)
# fig31 = px.bar(df, x="clicks,clicks_external", title="Bar Chart Example")

# Engagement by Availability	Grouped Bar	availability, clicks, clicksExternal
# fig32 = px.bar(df, x="category", y="value", color="subcategory", 
#              title="Grouped Bar Example", barmode="group")


# # Top Products by Engagement	Horizontal Bar	title, clicks, clicksExternal
# fig33 = px.bar(df, x="value", y="category", orientation="h", 
            #  title="Horizontal Bar Example")


layout = html.Div([
    html.H1("Analysis Dashboard"),  # Main title
    html.H2("4. Engagement Insights"),
    dcc.Graph(figure=fig31),
])
# # layout
# layout = dbc.Container(
#     [
#         html.Div(
#             [
#                 html.H2(
#                     "Purchase overview",  # title
#                     className="title",
#                 ),
#                 html.Br(),
#                 dbc.Row(
#                     [
#                         dbc.Col(
#                             [
#                                 html.H3(
#                                     "Select Year",
#                                     className="subtitle-small",
#                                 ),
#                                 dcc.Dropdown(
#                                     id="year-dropdown",
#                                     options=[
#                                         {"label": "All (2018-2022)", "value": "All"}
#                                     ],
#                                     # + [
#                                     #     {"label": col, "value": col}
#                                     #     for col in sorted(
#                                     #         df["Order Date Year"].unique()
#                                     #     )
#                                     # ],
#                                     value="All",
#                                     clearable=True,
#                                     multi=False,
#                                     placeholder="Select here",
#                                     className="custom-dropdown",
#                                 ),
#                             ],
#                             width=4,
#                         ),
#                     ]
#                 ),
#                 html.Br(),
#                 dbc.Row(
#                     [
#                         dbc.Col(
#                             create_card("Purchases", "purchases-card", "fa-list"),
#                             width=4,
#                         ),
#                         dbc.Col(
#                             create_card("Total Spend", "spend-card", "fa-coins"),
#                             width=4,
#                         ),
#                         dbc.Col(
#                             create_card("Top Category", "category-card", "fa-tags"),
#                             width=4,
#                         ),
#                     ],
#                 ),
#                 html.Br(),
#                 dbc.Row(
#                     [
#                         dbc.Col(
#                             dcc.Loading(
#                                 dcc.Graph(
#                                     id="sales-chart",
#                                     config={"displayModeBar": False},
#                                     className="chart-card",
#                                     style={"height": "400px"},
#                                 ),
#                                 type="circle",
#                                 color="#f79500",
#                             ),
#                             width=6,
#                         ),
#                         dbc.Col(
#                             dcc.Loading(
#                                 dcc.Graph(
#                                     id="category-chart",
#                                     config={"displayModeBar": False},
#                                     className="chart-card",
#                                     style={"height": "400px"},
#                                 ),
#                                 type="circle",
#                                 color="#f79500",
#                             ),
#                             width=6,
#                         ),
#                     ],
#                 ),
#             ],
#             className="page-content",
#         )
#     ],
#     fluid=True,
# )


# # callback cards and graphs
# @callback(
#     [
#         Output("purchases-card", "children"),
#         Output("spend-card", "children"),
#         Output("category-card", "children"),
#         Output("sales-chart", "figure"),
#         Output("category-chart", "figure"),
#     ],
#     [
#         Input("year-dropdown", "value"),
#     ],
# )
# def update_values(select_year):
#     # Brand Insights	

#     # Top Brands by Clicks	Bar Chart	brand, clicks
#     fig01 = px.bar(df, x="brand", y="clicks", title="Top Brands by Clicks")

#     # Brand Price Distribution	Box Plot	brand, price
#     fig02 = px.box(df, x="brand", y="price", title="Brand Price Distribution")


#     # Brand Availability Breakdown	Pie Chart	brand, availability
#     # Group by 'brand' and 'availability' and count occurrences
#     availability_counts = df.groupby(['brand', 'availability']).size().reset_index(name='count')

#     # Create the Pie Chart
#     fig03 = px.pie(
#         availability_counts, 
#         names='brand',              # Categories for the pie slices
#         values='count',             # Numeric values for slice sizes
#         title='Brand Availability Breakdown',
#         hover_data=['availability'] # Show availability status on hover
#     )

#     # filtered_df = df.copy()

#     # # filter
#     # if select_year and select_year != "All":
#     #     filtered_df = filtered_df[filtered_df["Order Date Year"] == select_year]

#     # # cards
#     # purchases_card = f"{filtered_df['Quantity'].count():,.0f}"
#     # spend_card = f"$ {round(filtered_df['Purchase Total'].sum(), -2):,.0f}"
#     # category_card = (
#     #     filtered_df.groupby("Category")["Survey ResponseID"].nunique().idxmax()
#     # )

#     # # sales
#     # sales_chart = px.bar(
#     #     filtered_df.groupby("Order Date Month", observed=True)["Purchase Total"]
#     #     .sum()
#     #     .reset_index(),
#     #     x="Order Date Month",
#     #     y="Purchase Total",
#     #     text_auto=".2s",
#     #     title="Total Monthly Spend",
#     # )

#     # sales_chart.update_traces(
#     #     textposition="outside",
#     #     marker_color="#f79500",
#     #     hoverlabel=dict(bgcolor="rgba(255, 255, 255, 0.1)", font_size=12),
#     #     hovertemplate="<b>%{x}</b><br>Value: %{y:,}<extra></extra>",
#     # )

#     # sales_chart.update_layout(
#     #     xaxis_title=None,
#     #     yaxis_title=None,
#     #     plot_bgcolor="rgba(0, 0, 0, 0)",
#     #     yaxis=dict(showticklabels=False),
#     #     margin=dict(l=35, r=35, t=60, b=40),
#     # )

#     # # category
#     # category_chart = px.treemap(
#     #     filtered_df.groupby("Category", as_index=False, observed=True)["Quantity"]
#     #     .count()
#     #     .nlargest(5, columns="Quantity"),
#     #     path=["Category"],
#     #     values="Quantity",
#     #     title="Top 5 Purchase Categories",
#     #     color="Category",
#     #     color_discrete_sequence=["#cb7721", "#b05611", "#ffb803", "#F79500", "#803f0c"],
#     # )

#     # category_chart.data[0].textinfo = "label+value"

#     # category_chart.update_traces(textfont=dict(size=13))

#     # category_chart.update_layout(margin=dict(l=35, r=35, t=60, b=35), hovermode=False)

#     return fig01, fig02, fig03 #purchases_card, spend_card, category_card, sales_chart, category_chart