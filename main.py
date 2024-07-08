import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

# Sample data
data = {
    'SKU': ['Item1', 'Item2', 'Item3', 'Item4', 'Item5'],
    'PSL': [100, 150, 200, 130, 170],
    'ROP': [50, 70, 90, 60, 80],
    'Stock': [80, 120, 180, 100, 150],
    'On Order': [20, 30, 40, 25, 35],
    'Desc': ['Description1', 'Description2', 'Description3', 'Description4', 'Description5']
}

df = pd.DataFrame(data)

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Color variables
AVAILABLE_COLOR = 'rgba(173, 216, 230, 1)'  # solid light blue
ON_ORDER_COLOR = 'rgba(144, 238, 144, 0.5)'  # light green semi-transparent
PSL_COLOR = 'rgba(173, 216, 230, 0.5)'  # light blue semi-transparent
ROP_COLOR = 'red'  # red color for ROP line

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Label("Options:"),
            dcc.Checklist(
                id='legend-checklist',
                options=[
                    {'label': 'Preferred Stock Level (PSL)', 'value': 'PSL'},
                    {'label': 'On Order Quantity', 'value': 'On Order'},
                    {'label': 'Reorder Point (ROP)', 'value': 'ROP'}
                ],
                value=['PSL', 'On Order', 'ROP'],
                inline=True
            )
        ], width=4),
        dbc.Col([
            html.Label("Sort By:"),
            dcc.RadioItems(
                id='sort-radio',
                options=[
                    {'label': 'Item Name (ASC)', 'value': 'item_asc'},
                    {'label': 'PSL (DESC)', 'value': 'psl_desc'}
                ],
                value='item_asc',
                inline=True
            )
        ], width=4),
        dbc.Col([
            html.Label("Filter Items:"),
            dcc.Dropdown(
                id='filter-input',
                options=[{'label': sku, 'value': sku} for sku in df['SKU']],
                multi=True,
                placeholder='Filter items...'
            )
        ], width=4)
    ], style={'margin-bottom': '20px', 'margin-left': '20px', 'margin-right': '20px'}),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='inventory-graph')
        ])
    ])
], fluid=True)


# Callback to update the graph
@app.callback(
    Output('inventory-graph', 'figure'),
    Input('legend-checklist', 'value'),
    Input('sort-radio', 'value'),
    Input('filter-input', 'value')
)
def update_graph(selected_legends, sort_option, filter_value):
    # Filter and sort the dataframe
    if filter_value:
        filtered_df = df[df['SKU'].isin(filter_value)]
    else:
        filtered_df = df

    if sort_option == 'item_asc':
        filtered_df = filtered_df.sort_values('SKU')
    elif sort_option == 'psl_desc':
        filtered_df = filtered_df.sort_values('PSL', ascending=False)

    # Create the figure
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=filtered_df['SKU'],
        y=filtered_df['Stock'],
        name='Available Stock Level',
        marker_color=AVAILABLE_COLOR,  # solid light blue
        hovertemplate='<b>Item Name:</b> %{x}<br><b>Desc:</b> %{customdata[0]}<br><b>Available:</b> %{y}<br><b>On Order:</b> %{customdata[1]}<br><b>PSL:</b> %{customdata[2]}<br><b>ROP:</b> %{customdata[3]}'
    ))

    if 'On Order' in selected_legends:
        fig.add_trace(go.Bar(
            x=filtered_df['SKU'],
            y=filtered_df['On Order'],
            name='On Order Quantity',
            marker_color=ON_ORDER_COLOR,  # light green semi-transparent
            base=filtered_df['Stock'],
            hovertemplate='<b>Item Name:</b> %{x}<br><b>Desc:</b> %{customdata[0]}<br><b>Available:</b> %{customdata[1]}<br><b>On Order:</b> %{y}<br><b>PSL:</b> %{customdata[2]}<br><b>ROP:</b> %{customdata[3]}'
        ))

    if 'PSL' in selected_legends:
        fig.add_trace(go.Scatter(
            x=filtered_df['SKU'],
            y=filtered_df['PSL'],
            mode='markers+lines',
            name='Preferred Stock Level (PSL)',
            line=dict(color=PSL_COLOR),  # light blue semi-transparent
            hovertemplate='<b>Item Name:</b> %{x}<br><b>Desc:</b> %{customdata[0]}<br><b>Available:</b> %{customdata[1]}<br><b>On Order:</b> %{customdata[2]}<br><b>PSL:</b> %{y}<br><b>ROP:</b> %{customdata[3]}'
        ))

    if 'ROP' in selected_legends:
        fig.add_trace(go.Scatter(
            x=filtered_df['SKU'],
            y=filtered_df['ROP'],
            mode='lines+markers',
            name='Reorder Point (ROP)',
            line=dict(dash='dash', color=ROP_COLOR),  # red color for ROP line
            hovertemplate='<b>Item Name:</b> %{x}<br><b>Desc:</b> %{customdata[0]}<br><b>Available:</b> %{customdata[1]}<br><b>On Order:</b> %{customdata[2]}<br><b>PSL:</b> %{customdata[3]}<br><b>ROP:</b> %{y}'
        ))

    fig.update_layout(
        barmode='stack',
        xaxis=dict(
            tickangle=-45,
            title_text='Item Name'
        ),
        yaxis=dict(
            title_text='Quantity'
        ),
        title='Inventory Management'
    )

    fig.update_traces(
        customdata=filtered_df[['Desc', 'Stock', 'On Order', 'PSL', 'ROP']].values
    )

    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
