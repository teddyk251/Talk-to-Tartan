import os
import json
import dash_mantine_components as dmc
import dash
import time

# Dash Imports
from dash import (
    Dash, html, dcc, callback, Input, Output, State, 
    clientside_callback, ClientsideFunction,
    _dash_renderer, page_container
)

# Internal Imports
from components.header import header
from components.sidebar import sidebar
from appconfig import stylesheets


_dash_renderer._set_react_version("18.2.0")

# external JavaScript files
# external_scripts = [
#     'http://172.29.104.127:8000/copilot/index.js'
# ]
external_scripts = [
    'http://localhost:8000/copilot/index.js'
]


app = Dash(
    __name__, use_pages=True,
    external_stylesheets=stylesheets,
    external_scripts=external_scripts
)

app.layout = dmc.MantineProvider(
    id="mantine-provider",
    children = [
        dmc.AppShell(
            id="app-shell",
            navbar={ "breakpoint": "md", "collapsed": {"mobile": True}},
            children = [
                dcc.Location(id="url"),
                dmc.AppShellHeader(header()),
                dmc.AppShellNavbar(sidebar, withBorder=True),
                dmc.AppShellMain(page_container),
                dcc.Store(id='login-status', data=None, storage_type='session'),  # For tracking login status
                dcc.Store(id='registration-status', data=None, storage_type='session'),  # For tracking registration status
                dcc.Store(id='user-profile', data=None, storage_type='session'),  # For tracking registered courses
            ]
        )
    ]   
)


@callback(
    [Output('login-status', 'data', allow_duplicate=True),
    Output('registration-status', 'data', allow_duplicate=True)],
    Input('logout-button', 'n_clicks'),
    prevent_initial_call=True
)
def logout_callback(logout_click: int):

    if logout_click > 0:
        return {'status': 'logged_out'}, {'status': 'logged_out'}
    else:
        return dash.no_update, dash.no_update


@callback(
    Output('url', 'pathname'),
    Input('login-status', 'data'),
    Input('registration-status', 'data'),
    prevent_initial_call=True
)
def update_url(login_status: dict, registration_status: dict):

    # Redirect to the login page if registration was successful
    if registration_status and registration_status['status'] == 'registration_success':
        if not login_status or login_status['status'] != 'login_success':
            time.sleep(2)
            return '/login'
    
    # Check if the login was successful
    if login_status and login_status['status'] == 'login_success':
        return '/coursePlan' # Redirect to the talkToTartan page
    elif login_status and login_status['status'] == 'logged_out':
        return '/logout'
    

@callback(
    Output('avatar-indicator', 'children'),
    Input("url", "pathname"),
)
def update_user_initials(url: str):
    user =''
    image=''
    size=0
    if  url =='/logout':
        user = ""
        size=0
    # elif 'email' in session:
    #     acount = session['email']
    #     user = f"{acount.get('given_name', '')[:1]}{acount.get('family_name', '')[:1]}"
    #     image = acount.get('picture', '')
    #     size=8

    status = dmc.Indicator(
            dmc.Avatar(
                style = {"cursor": "pointer" },
                size="md",
                radius="xl",
                src=image,
            ),
            offset=3,
            position="bottom-end",
            styles={
                "indicator": {"height": '20px', "padding": '2px', 'paddingInline':'0px'},
            },
            color='dark',
            size=size,
            label = user,
            withBorder=True,
            id = 'indicator'
        )
    return  status


clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='theme_switcher_callback'
    ),
    Output("mantine-provider", "theme"),
    Output("mantine-provider", "forceColorScheme"),
    Output("color-scheme-toggle", "rightSection"),
    Output("color-scheme-toggle", "label"),
    Input("color-scheme-toggle", "n_clicks")

)


clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='side_bar_toggle'
    ),
    Output("app-shell", "navbar"),
    Input("burger-button", "opened"),
    State("app-shell", "navbar"),
)


if __name__ == "__main__":
    app.run_server(debug=True, port= 8050)