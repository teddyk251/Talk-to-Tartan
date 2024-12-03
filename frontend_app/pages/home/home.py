from dash import register_page
import dash_mantine_components as dmc
from utils.helpers import iconify
from dash import dcc


register_page(__name__, path="/")


__app__ = 'app.py'
__home__ = 'pages/home/home.py'
__coursePlan__ = 'pages/coursePlan.py'
__feedback__ = 'pages/feedback.py'

with open(__app__, 'r') as file:
    __app__ = file.read()
 
with open(__home__, 'r') as file:
    __home__ = file.read()

with open(__coursePlan__, 'r') as file:
    __coursePlan__ = file.read()

with open(__feedback__, 'r') as file:
    __feedback__ = file.read()


ButtonStyle =  {
    "background": "#ff004c",
    "padding": "5px 10px",  # Adjust padding to make the button smaller
    "border": "none",
    "borderRadius": "12px",  # Smaller border radius
    "color": "white",
    "fontSize": "18px",  # Reduce font size for a smaller look
    "textAlign": "center",
    "display": "flex",  # Use flexbox to position icon and label side by side
    "width": "auto",  # Allow the button to take the size based on its content
    "marginTop": "20px",
    "marginBottom": "20px",
}


layout = dmc.Box(
    m=30,
    children=[
        # Welcome Section
        dmc.Container(
            children=[
                dmc.Center(
                    dmc.Title("Welcome to Talk To Tartan!", order=1),
                    style={"paddingTop": "40px"}
                ),
                dmc.Center(
                    dmc.Text(
                        "Your personalized assistant for navigating course information and planning your academic journey.",
                        size="lg"
                    ),
                    style={"paddingTop": "10px"}
                ),
                dmc.Center(
                    dmc.NavLink(
                        label="Get Started",
                        href='/register',
                        leftSection=iconify(icon="vaadin:start-cog", width = 20),
                        style=ButtonStyle,
                        variant="filled"
                    ),
                    # dmc.Button("Get Started", size="lg", radius="xl", style=ButtonStyle),
                ),
            ],
            style={"marginBottom": "50px"}
        ),

        # About the App Section
        dmc.Container(
            children=[
                dmc.Title("What Does Talk To Tartan Do?", order=2),
                dmc.Text(
                    "Talk To Tartan is your one-stop solution for academic guidance. Whether you're "
                    "exploring new courses or organizing your course plans, our chatbot offers real-time "
                    "information and personalized advice to help you stay on track.",
                    size="md",
                    style={"marginTop": "10px", "textAlign": "center"}
                ),
                dmc.List(
                    children=[
                        dmc.ListItem("Stay Informed: Get up-to-date information about courses."),
                        dmc.ListItem("Personalized Course Plans: Organize and modify your course selections."),
                        dmc.ListItem("Academic Advising: Receive recommendations based on your academic goals."),
                        dmc.ListItem("Real-time Updates: Stay informed about important deadlines and changes."),
                    ],
                    spacing="sm",
                    size="sm",
                    style={"paddingTop": "20px"}
                ),
            ],
            style={"marginBottom": "50px", "padding": "0 50px"}
        ),

        # How It Works Section
        dmc.Container(
            children=[
                dmc.Title("How It Works", order=2),
                dmc.Text(
                    "Using Talk To Tartan is easy. Here's how:",
                    size="md",
                    style={"marginTop": "10px"}
                ),
                dmc.List(
                    children=[
                        dmc.ListItem("Step 1: Start a conversation by asking about a course or ask for help with course planning."),
                        dmc.ListItem("Step 2: Get detailed information about courses, including descriptions, schedules, and prerequisites."),
                        dmc.ListItem("Step 3: Organize and plan your courses based on your degree or personal preferences."),
                    ],
                    spacing="sm",
                    size="sm",
                    style={"paddingTop": "20px"}
                ),
            ],
            style={"marginBottom": "50px", "padding": "0 50px"}
        ),

        # Why Choose Talk To Tartan Section
        dmc.Container(
            children=[
                dmc.Title("Why Choose Talk To Tartan?", order=2),
                dmc.Text(
                    "Talk To Tartan is designed to simplify your academic planning. Get reliable, up-to-date "
                    "information, and easily plan your semester with personalized support.",
                    size="md",
                    style={"marginTop": "10px", "textAlign": "center"}
                ),
            ],
            style={"marginBottom": "50px", "padding": "0 50px"}
        ),

        # Call to Action Section
        dmc.Container(
            children=[
                dmc.Center(
                    children=[
                        dmc.Title("Ready to start planning your academic future?", order=3)
                    ],
                    style={"marginTop": "40px", "marginBottom": "5px"}
                ),
                dmc.Center(
                    children=[
                        dmc.NavLink(
                        label="Chat with Tartan Now!",
                        href='/coursePlan',
                        leftSection=iconify(icon="fluent-mdl2:chat-bot", width = 20),
                        style=ButtonStyle,
                        variant="filled"
                        ),
                        # dmc.Button("Chat with Tartan Now!", size="lg", radius="xl", style=ButtonStyle)
                    ],
                    style={"marginTop": "5px", "marginBottom": "60px"}
                )
            ]
        )
    ]
)