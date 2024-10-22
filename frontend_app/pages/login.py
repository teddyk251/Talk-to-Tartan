import dash
import dash_mantine_components as dmc 

from dash import html, dcc
from utils.helpers import iconify
from dash_iconify import DashIconify

from dash import Output, Input, State, callback


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
    html.Div(id="notifications-container", children=[])]
)


@callback(
    [Output(component_id="url", component_property="pathname"),
     Output(component_id="notifications-container", component_property="children")],
    Input('login-button', 'n_clicks'),
    State('id-input', 'value'),
    State('password-input', 'value'),
    prevent_initial_call=True
)
def handle_login(n_clicks, id, password):
    url = "/login"
    notification = None

    # Check if the login button is clicked
    if n_clicks > 0:
        if id and password:  # If both email and password are provided
            url = "/talkToTartan"
            notification = dmc.Notification(
                title="Login Successful",
                id="simple-notify",
                action="show",
                color="green",
                message="Redirecting...",
                icon=DashIconify(icon="ic:round-check"),
            )
        else:  # If fields are missing
            notification = dmc.Notification(
                title="Login Unsuccessful",
                id="simple-notify",
                action="show",
                color="red",
                message="Please fill in all fields",
                icon=DashIconify(icon="ic:round-error"),
            )

    return url, notification