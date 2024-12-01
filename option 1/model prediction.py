import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import joblib
import plotly.express as px
import plotly.graph_objects as go
from sklearn.inspection import permutation_importance

# Load Model and Data
decision_tree_model = joblib.load("decision_tree_model.joblib")
df = pd.read_csv("credit_risk_dataset.csv")
df['loan_grade'] = df['loan_grade'].map({'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6})
grade_map = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6:'G'}

# App Initialization
app = dash.Dash(__name__)
app.title = "Loan Default Predictor"

# Cool Blue-Green Theme Styling
theme = {
    "background": "#E0F7FA", 
    "text": "#01579B",  
    "card_background": "#FFFFFF",  
    "accent_color": "#00796B",  
    "font_family": "Arial, sans-serif",
    "hover_color": "#4DB6AC",
}

# App Layout
app.layout = html.Div(
    style={"backgroundColor": theme["background"], "fontFamily": theme["font_family"], "color": theme["text"], "padding": "20px"},
    children=[
        html.Div(
            children=html.H1("Loan Default Prediction Dashboard", style={"textAlign": "center", "color": theme["accent_color"], "fontWeight": "bold"}),
            style={"padding": "20px 0"}
        ),
        html.Div(
            style={"display": "flex", "justifyContent": "space-between", "gap": "20px"},
            children=[
                # Left Column: Prediction Section
                html.Div(
                    style={"width": "45%", "backgroundColor": theme["card_background"], "padding": "20px", "borderRadius": "10px", "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)"},
                    children=[
                        html.Label("Loan Grade:", style={"fontSize": "16px", "fontWeight": "bold"}),
                        dcc.Dropdown(id="loan_grade", options=[{'label': grade, 'value': value} for grade, value in zip(['A', 'B', 'C', 'D', 'E', 'F', 'G'], range(7))], value=1, style={"backgroundColor": theme["hover_color"], "color": theme["text"]}),
                        html.Label("Loan Interest Rate:", style={"fontSize": "16px", "marginTop": "10px", "fontWeight": "bold"}),
                        dcc.Input(id="loan_int_rate", type="number", placeholder="Enter loan interest rate", value=5.0, style={"width": "100%", "padding": "10px", "borderRadius": "5px", "border": "1px solid #ccc"}),
                        html.Label("Person's Income:", style={"fontSize": "16px", "marginTop": "10px", "fontWeight": "bold"}),
                        dcc.Input(id="person_income", type="number", placeholder="Enter income", value=57000, style={"width": "100%", "padding": "10px", "borderRadius": "5px", "border": "1px solid #ccc"}),
                        html.Button("Predict Loan Status", id="predict_btn", n_clicks=0, style={"marginTop": "20px", "backgroundColor": theme["accent_color"], "color": "#FFFFFF", "border": "none", "padding": "10px 20px", "cursor": "pointer", "borderRadius": "5px", "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)"}),
                        html.Div(id="prediction_output", style={"fontSize": "20px", "marginTop": "10px", "textAlign": "center", "fontWeight": "bold", "color": theme["accent_color"]}),
                    ]
                ),
                
                # Right Column: Insights Section
                html.Div(
                    style={"width": "45%"},
                    children=[
                        # Row 1: Key Insights
                        html.Div(
                            style={"marginBottom": "20px"},
                            children=[
                                html.H3("Key Insights from the Data", style={"textAlign": "center", "color": theme["accent_color"], "fontWeight": "bold"}),
                                dcc.Graph(id="data_insights", style={"height": "300px"}),
                            ]
                        ),
                        
                        # Row 2: Feature Importance
                        html.Div(
                            children=[
                                html.H3("Feature Importance", style={"textAlign": "center", "color": theme["accent_color"], "fontWeight": "bold"}),
                                dcc.Graph(id="feature_importance", style={"height": "300px"}),
                            ]
                        ),
                    ]
                ),
            ]
        ),
    ]
)

# Callbacks
@app.callback(
    Output("prediction_output", "children"),
    Input("predict_btn", "n_clicks"),
    State("loan_grade", "value"),
    State("loan_int_rate", "value"),
    State("person_income", "value")
)
def predict_loan_status(n_clicks, loan_grade, loan_int_rate, person_income):
    if n_clicks > 0:
        features = pd.DataFrame([[int(loan_grade), float(loan_int_rate), int(person_income)]], columns=["loan_grade", "loan_int_rate", "person_income"])
        prediction = decision_tree_model.predict(features)
        return "Prediction: Loan Default Risk 🚨" if prediction[0] == 1 else "Prediction: Low Default Risk ✅"
    return ""

@app.callback(
    Output("data_insights", "figure"),
    Input("predict_btn", "n_clicks")
)
def update_insights(n_clicks):
    # Convert the loan_grade back to letters for display
    df['loan_grade_'] = df['loan_grade'].map(grade_map)
    
    # Create the scatter plot with loan_grade as letters
    fig = px.scatter(df, x="person_income", y="loan_int_rate", color="loan_status", 
                     title="Loan Interest Rate vs Income", 
                     labels={"loan_int_rate": "Loan Interest Rate", "person_income": "Income"},
                     hover_data=["loan_grade_"])  
    
    fig.update_layout(paper_bgcolor=theme["background"], plot_bgcolor=theme["card_background"], font_color=theme["text"])
    return fig

@app.callback(
    Output("feature_importance", "figure"),
    Input("predict_btn", "n_clicks")
)
def update_feature_importance(n_clicks):
    perm_importance = permutation_importance(decision_tree_model, df[["loan_grade", "loan_int_rate", "person_income"]], df["loan_status"])
    importance_df = pd.DataFrame({"Feature": ["Loan Grade", "Loan Interest Rate", "Person's Income"], "Importance": perm_importance.importances_mean})
    fig = go.Figure(data=[go.Bar(x=importance_df["Feature"], y=importance_df["Importance"], marker_color=theme["accent_color"])])
    fig.update_layout(title="Feature Importance", template="plotly_white", paper_bgcolor=theme["background"], plot_bgcolor=theme["card_background"], font_color=theme["text"])
    return fig

# Run Server
if __name__ == "__main__":
    app.run_server(debug=True)
