from dash import (
    html, Output, Input, State, callback, 
    register_page
)
import dash_mantine_components as dmc
from backend_client import get_feedback_data

register_page(__name__, path="/feedback")


ButtonStyle = {
    "background": "#ff004c",
    "padding": "5px 20px",
    "border": "none",
    "borderRadius": "20px",
    "color": "white",
    "fontSize": "16px",
    "width": "200px",  # Restrict button width to 200px
    "textAlign": "center",  # Ensure text is centered
    "cursor": "pointer",  # Change cursor to pointer for better UX
}

# Define your layout function
def layout():
    return html.Div(
        id='feedback-content',
        style={
            "paddingTop": "50px",
            "marginTop": "50px",
            "marginLeft": "100px",   # Adjust for left margin
            "marginRight": "100px",  # Adjust for right margin
        },
        children=[
            html.Div(id="feedback-page")
        ]
    )

# Define the callback to update the content based on login status
@callback(
    Output('feedback-page', 'children'),
    State('user-profile', 'data'),
    Input('login-status', 'data')
)
def display_feedback_page(user_profile: dict, login_status: dict):

    if login_status and login_status.get('status') == 'login_success':

        # if user_profile["role"] == "admin":
        return dmc.Paper(
            pt=20,
            shadow='sm',
            children=[
                dmc.Paper(
                    children=[
                        dmc.Button(
                            "Update Feedback",
                            id="update-feedback-btn",
                            n_clicks=0,
                            style=ButtonStyle,
                        ),
                        html.Div(id="feedback-display"),
                    ],
                    shadow="xs"
                )
            ]
        )
        # else:
        #     return dmc.Flex(
        #         align="center",
        #         children=[
        #             dmc.Text("You do not have access to this page", p=5),
        #         ]
        #     )
    else:
        return dmc.Flex(
            align="center",
            children=[
                dmc.Text("This page requires login. Please", p=5),
                html.A('login', href='/login'),
                dmc.Text("to continue", p=5),
            ]
        )
    

@callback(
    Output('feedback-display', 'children'),
    Input('update-feedback-btn', 'n_clicks'),
    suppress_callback_exceptions=True
)
def update_feedback_page(n_clicks):

    parsed_feedback = []
            
    if n_clicks:
        response = get_feedback_data()
        feedback_data = response.json()
        parsed_feedback = parse_feedback(feedback_data)

    feedback_table = create_feedback_table(parsed_feedback)

    return dmc.Paper(
        pt=20,
        shadow='sm',
        children=[
            dmc.Paper(
                children=feedback_table,
                shadow="xs"
            )
        ]
    )


def parse_feedback(feedback_data: dict):

    parsed_feedback = []

    for feedback in feedback_data["feedbacks"]:

        field1 = feedback["id"]
        field2 = feedback["feedback"]
        field3 = feedback["value"]

        parsed_feedback.append([field1, field2, field3])

    return parsed_feedback


def create_feedback_table(feedback: list):

    # Create a table for the semester
    table = dmc.Paper(
                pt=30,
                children=[
                    dmc.Table(
                        striped=True,
                        highlightOnHover=True,
                        withTableBorder=True,
                        withColumnBorders=True,
                        horizontalSpacing=10,
                        data={
                            "caption": f"User Feedback",
                            "head": ["ID", "Feedback", "Value"],
                            "body": feedback,
                        }
                    )
                ],
                shadow="xs",
                style={"width": "100%"}
            )

    return table