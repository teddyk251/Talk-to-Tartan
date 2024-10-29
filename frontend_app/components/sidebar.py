import dash_mantine_components as dmc
from dash import dcc
from utils.helpers import iconify


sidebar = dmc.Box(
    children = [
         dmc.NavLink(
            label="Home",
            leftSection=iconify(icon="solar:home-2-line-duotone", width = 20),
            href='/'
        ),
        dmc.NavLink(
            label="Current Plan",
            leftSection=iconify(icon="fluent-mdl2:plan-view", width = 20),
            href='/coursePlan'
        ),
        # dmc.NavLink(
        #     label="Talk to Tartan",
        #     leftSection=iconify(icon="tabler:message-chatbot", width = 20),
        #     href='/talkToTartan'
        # )
    ]
)