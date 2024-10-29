from dash import (
    html, dcc, Output, Input, State, callback, 
    register_page
)
# from flask import session
import json
import dash_mantine_components as dmc


register_page(__name__, path="/coursePlan")


# Define your layout function
def layout():
    return html.Div([
        dmc.Center(id='course-plan-content', mt=50, pt=50),
    ])

# Define the callback to update the content based on login status
@callback(
    Output('course-plan-content', 'children'),
    Input('login-status', 'data'),
)
def update_course_plan(login_status: dict):

    if login_status and login_status.get('status') == 'login_success':

        registered_courses = [
            {"course": "15-112", "units": 12},
            {"course": "15-122", "units": 9},
            {"course": "15-150", "units": 9},
        ]

        return dmc.Paper(
            pt=20,
            shadow='sm',
            children=[
                dmc.Text("Here are your registered courses"),
                dmc.CodeHighlight(
                    language="json",
                    code=str(registered_courses),
                )
            ]
        )
    else:
        return dmc.Flex(
            align="center",
            children=[
                dmc.Text("This page requires login. Please", p=5),
                html.A('login', href='/login'),
                dmc.Text("to continue", p=5),
            ]
        )