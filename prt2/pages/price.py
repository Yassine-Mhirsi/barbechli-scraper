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
    path="/price_overview",
)

df=pd.read_csv('products.csv')

# Price Evolution Insights	

# # Price Drop Impact on Engagement	Scatter Plot	price_drop, price_drop_percent, clicks
# fig21 = px.scatter(df, x="x_value", y="y_value", title="Scatter Plot Example")

# # Price History per Product	Line Graph	uniqueID, priceTable (parsed price, date_price)
# # fig22 = px.line(df, x="date", y="value", title="Line Graph Example")

# Weekly Price Drop Trends	Area Chart	price_week_drop, price_week_drop_percent, date_creation
fig23 = px.area(df, x="date_creation", y="price", title="Weekly Price Drop Trends")




layout = html.Div([
    html.H1("Analysis Dashboard"),  # Main title
    html.H2("3. Price Evolution Insights"),
    # dcc.Graph(figure=fig21),       
    # # dcc.Graph(figure=fig22),       
    dcc.Graph(figure=fig23),
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