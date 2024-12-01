import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load dataset
data = pd.read_csv('credit_risk_dataset.csv')

# Determine meaningful income range
valid_income_range = data['person_income'][data['person_income'] <= 300000]
income_min = valid_income_range.min()
income_max = valid_income_range.max()

# Create the Dash app
app = dash.Dash(__name__)
app.title = "Professional Loan Interest Rate Dashboard"

# App Layout
app.layout = html.Div([  
    # Header Section
    html.Div([
        html.H1("Loan Interest Rate Analysis Dashboard",
                style={'text-align': 'center', 'font-weight': 'bold', 'color': '#ffffff'}),
        html.P("Explore the impact of borrower demographics on loan interest rates. Utilize interactive filters and visualizations to uncover trends.",
               style={'text-align': 'center', 'font-size': '18px', 'color': '#aaaaaa'})
    ], style={'padding': '20px', 'background-color': '#222'}),  

    # Filters Section
    html.Div([
        html.Div([
            html.Label("Homeownership Status:", style={'font-weight': 'bold', 'color': '#ffffff'}),
            dcc.Dropdown(
                id='homeownership-dropdown',
                options=[{'label': home, 'value': home} for home in data['person_home_ownership'].unique()],
                value=data['person_home_ownership'].unique()[0],
                placeholder="Select Homeownership Status"
            ),
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label("Loan Intent:", style={'font-weight': 'bold', 'color': '#ffffff'}),
            dcc.Dropdown(
                id='loan-intent-dropdown',
                options=[{'label': intent, 'value': intent} for intent in data['loan_intent'].unique()],
                value=data['loan_intent'].unique()[0],
                placeholder="Select Loan Intent"
            ),
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label("Income Range ($):", style={'font-weight': 'bold', 'color': '#ffffff'}),
            dcc.RangeSlider(
                id='income-slider',
                min=income_min,
                max=income_max,
                step=5000,
                marks={i: {'label': f'${i // 1000}K', 'style': {'color': '#ffffff', 'font-size': '12px'}}
                       for i in range(int(income_min), int(income_max) + 1, 50000)},
                value=[income_min, income_max],
                tooltip={"placement": "bottom", "always_visible": True}
            ),
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),
    ], style={'background-color': '#333', 'padding': '10px'}),  

    # Visualization Section
    html.Div([
        dcc.Tabs([
            dcc.Tab(label="Age vs Loan Interest Rate", children=[
                dcc.Graph(id='age-vs-interest-plot')
            ]),
            dcc.Tab(label="Income vs Loan Interest Rate", children=[
                dcc.Graph(id='income-vs-interest-plot')
            ]),
            dcc.Tab(label="Credit History vs Loan Interest Rate", children=[
                dcc.Graph(id='credit-history-vs-interest-plot')
            ]),
            dcc.Tab(label="Loan Amount vs Income Heatmap", children=[  # Updated Tab
                dcc.Graph(id='loan-amount-vs-income-heatmap')
            ]),
            dcc.Tab(label="Loan Status Distribution", children=[
                dcc.Graph(id='loan-status-pie-chart')
            ]),
        ], style={'background-color': '#444', 'color': '#000'})
    ], style={'background-color': '#222'})
], style={'font-family': 'Arial, sans-serif', 'background-color': '#111'})

# Helper function to generate figures
def generate_fig(figure_type, data, x, y, color, title, labels, hover_data=None):
    """
    Helper function to generate different types of plots (scatter, histogram, pie, etc.)
    """
    if figure_type == 'scatter':
        fig = px.scatter(
            data,
            x=x,
            y=y,
            color=color,
            title=title,
            labels=labels,
            hover_data=hover_data
        )
    elif figure_type == 'histogram':
        fig = px.histogram(
            data,
            x=x,
            nbins=20,
            title=title,
            labels=labels,
            color=color,
            marginal='box'
        )
    elif figure_type == 'pie':
        fig = px.pie(
            data,
            names=x,
            title=title,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
    elif figure_type == 'heatmap':  # Added heatmap functionality
        fig = px.density_heatmap(
            data,
            x=x,
            y=y,
            title=title,
            labels=labels,
            color_continuous_scale="Viridis"
        )

    fig.update_layout(template='plotly_dark')
    return fig

# Callback to update plots
@app.callback(
    [Output('age-vs-interest-plot', 'figure'),
     Output('income-vs-interest-plot', 'figure'),
     Output('credit-history-vs-interest-plot', 'figure'),
     Output('loan-amount-vs-income-heatmap', 'figure'),  # Updated Output
     Output('loan-status-pie-chart', 'figure')],
    [Input('homeownership-dropdown', 'value'),
     Input('loan-intent-dropdown', 'value'),
     Input('income-slider', 'value')]
)
def update_plots(homeownership, loan_intent, income_range):
    # Filter dataset
    filtered_data = data[(data['person_home_ownership'] == homeownership) &
                         (data['loan_intent'] == loan_intent) &
                         (data['person_income'] >= income_range[0]) &
                         (data['person_income'] <= income_range[1])]

    # Generate figures using the helper function
    fig_age = generate_fig('scatter', filtered_data, 'person_age', 'loan_int_rate', 'loan_grade',
                           'Loan Interest Rate by Age', {'person_age': 'Age', 'loan_int_rate': 'Interest Rate (%)'},
                           hover_data=['loan_status', 'loan_amnt'])

    fig_income = generate_fig('scatter', filtered_data, 'person_income', 'loan_int_rate', 'loan_grade',
                              'Loan Interest Rate by Income', {'person_income': 'Income ($)', 'loan_int_rate': 'Interest Rate (%)'},
                              hover_data=['loan_status', 'loan_amnt'])

    fig_credit = generate_fig('scatter', filtered_data, 'cb_person_cred_hist_length', 'loan_int_rate', 'loan_status',
                              'Interest Rate vs Credit History Length', {'cb_person_cred_hist_length': 'Credit History Length (years)',
                                                                         'loan_int_rate': 'Interest Rate (%)'})

    fig_heatmap = generate_fig('heatmap', filtered_data, 'person_income', 'loan_amnt', None,
                               'Loan Amount vs Income Heatmap', {'person_income': 'Income ($)', 'loan_amnt': 'Loan Amount ($)'})

    fig_pie = generate_fig('pie', filtered_data, 'loan_status', None, None, 'Loan Status Distribution', None)

    return fig_age, fig_income, fig_credit, fig_heatmap, fig_pie

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
