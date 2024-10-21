import dash
from dash import html, dcc, Input, Output, callback
from utils.helpers import iconify
import dash_mantine_components as dmc 


dash.register_page(__name__)


loginButtonStyle =   {
    "background": "#ff004c",
    "padding": "5px 20px" ,
    "border": "none",
    "borderRadius": "20px",
    "color": "white",
    "fontSize":"16px",
    "width":"100%",
    "marginTop": "10px",
  }

layout = dmc.Paper(
    shadow='sm',
    p = "30px",
    mt = 60,
    children = [
        dmc.Box(
            style = {"width":'300px'},
            children = [
                dmc.Text("Sign up",  size='xl', fw=700),
                dmc.Text("Please Sign up to continue", c='gray', size='xs', mb = 10),
                dmc.TextInput(
                    label="First Name",
                    name='given_name',
                    id='first-name-input',
                    placeholder="Enter your first name",
                    required = True,
                ),
                dmc.TextInput(
                    label="Andrew ID",
                    name='id',
                    placeholder="Enter your Andrew ID",
                    required = True,
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
                dmc.RadioGroup(
                    children=dmc.Group(
                        [
                            dmc.Radio(label="EAI", value="EAI", color="red"),
                            dmc.Radio(label="ECE", value="ECE", color="green"),
                            dmc.Radio(label="IT", value="IT", color="blue"),
                        ], 
                        my=10
                    ),
                    id="program-radio-group",
                    value="MSEAI",
                    label="Select your program",
                    size="sm",
                    mb=10,
                ),
                dmc.Textarea(
                    label="Academic or Research Interests",
                    placeholder="What are your research and academic interests?",
                    w=500,
                    autosize=True,
                    id="interets-textarea",
                    minRows=2,
                    maxRows=4,
                ),
                dmc.RadioGroup(
                    children=dmc.Group(
                        [
                            dmc.Radio(label="Yes", value="Yes", color="red"),
                            dmc.Radio(label="No", value="No", color="red"),
                        ], 
                        my=10
                    ),
                    id="first-semester-radio",
                    value="Yes",
                    label="Is this your first semester at CMU?",
                    size="sm",
                    mb=10,
                    style={"marginTop": "10px"}
                ),
                dmc.NumberInput(
                    label="Completed Semesters",
                    id="completed-semesters-input",
                    description="How many semesters have you completed?",
                    value=0,
                    min=0,
                    max=3,
                    w=150,
                ),
                html.Div(id='course-inputs-container'),
                html.Button(
                    children="Sign up", 
                    n_clicks=0, 
                    type="submit", 
                    id="register-button", 
                    style =loginButtonStyle
                ),
                dmc.Divider(mb = 10, mt = 10),
                dmc.Flex(
                    mt = 10,
                    align = 'center',
                    children = [
                        dmc.Text(f"Already have an Account?", c='gray', size = 'xs'),
                        html.A('Sign in', href='/login', style = {'fontSize':'12px'})
                    ]
                )  
            ]
        )
    ]
)


@callback(
    Output('course-inputs-container', 'children'),
    Input('first-semester-radio', 'value'),
    Input('completed-semesters-input', 'value'),
)
def update_semester_input(first_semester, completed_semesters):

    if first_semester.lower() == 'no' and completed_semesters > 0:

        semester_sections = []

        for i in range(completed_semesters):
            # Create a section for each semester with 7 rows of course inputs
            courses = []

            for j in range(7):  # 7 possible courses per semester
                courses.append(
                    dmc.Grid([
                        dmc.GridCol(
                            dmc.TextInput(
                                id=f'course-{i}-{j}',  # Unique ID for course code
                                label='Course Code',
                                placeholder='Enter course code',
                            ),
                            span=6  # Span 6 out of 12 columns for course code
                        ),
                        dmc.GridCol(
                            dmc.TextInput(
                                id=f'course-title-{i}-{j}',  # Unique ID for course title
                                label='Course Title',
                                placeholder='Enter course title',
                            ),
                            span=6  # Span 6 out of 12 columns for course title
                        )
                    ], gutter='xs')  # Small gutter between the columns
                )
            # Create an Accordion for each semester with the course inputs
            semester_section = dmc.Accordion(
                children=[
                    dmc.AccordionItem(
                        children=courses,  # List of course rows
                        value=f"Semester-{i + 1}"  # Unique value for each AccordionItem
                    )
                ]
            )
            semester_sections.append(semester_section)

        return semester_sections
    else:
        return []