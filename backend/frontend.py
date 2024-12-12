import dash
from dash import dcc, html, Input, Output
import requests

app = dash.Dash(__name__)

app.layout = html.Div([
    # User authentication section (sign-up/sign-in)
    html.Div([
        dcc.Input(id='username', type='text', placeholder='Username'),
        dcc.Input(id='password', type='password', placeholder='Password'),
        html.Button('Sign Up', id='sign-up-button'),
        html.Button('Sign In', id='sign-in-button'),
        html.Div(id='auth-response')
    ]),

    # Section for interacting with the LLM using Chainlit
    html.Hr(),
    html.H3("LLM Interaction"),
    html.Iframe(src="http://localhost:8000",  # Assuming Chainlit runs on port 8000
                style={"width": "100%", "height": "500px"}),

    # Section for other tools implemented using Langchain
    html.Div(id='tools-section')
])

@app.callback(
    Output('auth-response', 'children'),
    Input('sign-up-button', 'n_clicks'),
    Input('sign-in-button', 'n_clicks'),
    [Input('username', 'value'), Input('password', 'value')]
)
def authenticate_user(sign_up_clicks, sign_in_clicks, username, password):
    if sign_up_clicks:
        response = requests.post('http://127.0.0.1:5000/signup', json={
            'username': username,
            'password': password
        })
        return response.text
    elif sign_in_clicks:
        response = requests.post('http://127.0.0.1:5000/signin', json={
            'username': username,
            'password': password
        })
        return response.text

if __name__ == '__main__':
    app.run_server(debug=True)
