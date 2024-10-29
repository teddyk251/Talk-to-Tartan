import dash
from dash import html, dcc
# from flask import session

dash.register_page(__name__)


def layout(**kwargs):
        
    return html.Div(
        [
            html.Div(html.H2("You have been logged out")),
            
        ]
    )