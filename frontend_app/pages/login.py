import dash
import dash_mantine_components as dmc 

from dash import html, dcc
from utils.helpers import iconify
from dash_iconify import DashIconify

from dash import Output, Input, State, callback
from dash import callback_context as ctx


from backend_client import sign_in_user

dash.register_page(__name__)


loginButtonStyle =   {
    "background": "#ff004c",
    "padding": "5px 20px" ,
    "border": "none",
    "borderRadius": "20px",
    "color": "white",
    "fontSize":"16px",
    "width":"100%"
    
  }

layout = dmc.Center(
    [dmc.Paper(
        shadow='sm',
        p = "30px",
        mt = 60,
        children = [
            dmc.Box(
                style = {"width":'300px'},
                # method='POST',
                children = [
                    dmc.Text("Sign in ",  size='xl', fw=700),
                    dmc.Text("Please log in to continue", c='gray', size='xs', mb = 10),
                    dmc.TextInput(
                        label="Andrew ID",
                        name='id',
                        placeholder="Enter your Andrew ID",
                        required = True,
                        id='id-input',
                        leftSection=iconify(icon="streamline:interface-id-thumb-mark-identification-password-touch-id-secure-fingerprint-finger-security", width=20),
                    ),
                    dmc.PasswordInput(
                        mb=20,
                        label="Password",
                        placeholder="Enter your password",
                        id='password-input',
                        leftSection=iconify(icon="bi:shield-lock", width=20),
                        name='password',
                        required = True
                    ),
                    dmc.Button("Sign in", id="login-button", n_clicks=0, style=loginButtonStyle),
                    dmc.Divider(label="Don't have and Account?", mb = 10, mt = 10),
                    dmc.Flex(
                        mt = 10,
                        align = 'center',
                        children = [
                            html.A('Sign up', href='/register', style = {'fontSize':'12px'})
                        ]
                    )
                ]
            )
        ]
    ),
    dmc.NotificationProvider(),
    html.Div(id="sign-in-notifications-container", children=[])]
)


@callback(
    [Output(component_id="login-status", component_property="data", allow_duplicate=True),
     Output(component_id="sign-in-notifications-container", component_property="children"),
     Output(component_id="user-profile", component_property="data")],
    Input('login-button', 'n_clicks'),
    State('id-input', 'value'),
    State('password-input', 'value'),
    prevent_initial_call=True
)
def handle_login(login_click: int, id: str, password: str):

    # Check if the login button is clicked
    if login_click > 0:

        notification = None
        login_status = None

        payload = {
            "andrew_ID": id,
            "password": password
        }

        if id and password:  # If both email and password are provided

            response = sign_in_user(payload)
            response_json = response.json()

            if response.status_code == 200:

                login_status = {'status': 'login_success'}

                notification = dmc.Notification(
                    title="Login Successful",
                    id="simple-notify",
                    action="show",
                    color="green",
                    message=response_json["message"],
                    icon=DashIconify(icon="ic:round-check"),
                )

                profile = get_dummy_profile()


            else:
                notification = dmc.Notification(
                    title="Login Unsuccessful",
                    id="simple-notify",
                    action="show",
                    color="red",
                    message=response_json["message"],
                    icon=DashIconify(icon="ic:round-error"),
                )

                profile = None

        else:  # If fields are missing # TODO: Make sure to verify and edit this else block
            notification = dmc.Notification(
                title="Login Unsuccessful",
                id="simple-notify",
                action="show",
                color="red",
                message="Please fill in all fields",
                icon=DashIconify(icon="ic:round-error"),
            )

            profile = None

        return login_status, notification, profile
    
    return dash.no_update, dash.no_update, dash.no_update


import random
def get_dummy_profile():

    sign_up = {
        "first_name": "John Doe",
        "andrew_ID": "johndoe",
        "password": "password",
        "program": "MSIT",
        "interests": "I am interested in AI and ML",
        "previous_experience": "I have a BSc in Computer Science",
        "first_semester": False,
        "completed_semesters": 2,
        "starting_year": 2021,
        "number_of_planned_semesters": 4,
        "courses": {
            "semesters": [
                {
                    "semester": i + 1,
                    "courses": [
                        {
                            "course_name": f"Course {j + 1}",
                            "course_code": f"{random.choice(['10', '15', '18', '11'])}-{random.randint(100, 999)}",
                            "units": random.choice([6, 12])
                        }
                        for j in range(4)  # 4 courses per semester
                    ]
                }
                for i in range(4)  # 4 semesters
            ]
        }
    }

    return sign_up