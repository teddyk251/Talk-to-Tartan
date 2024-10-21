import os
import json
import dash_mantine_components as dmc

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


app = Dash(
    __name__, use_pages=True,
    external_stylesheets=stylesheets,
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
            ]
        )
    ]   
)


@callback(
    Output('avatar-indicator', 'children'),
    Input("url", "pathname"),
)
def update_user_initials(url):
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