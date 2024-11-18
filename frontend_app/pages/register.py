import dash
from dash import html, dcc, Input, Output, State, callback, ALL
from utils.helpers import iconify
import dash_mantine_components as dmc 

from backend_client import sign_up_user

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
                    leftSection=iconify(icon="icon-park-outline:edit-name", width=20),
                ),
                dmc.TextInput(
                    label="Andrew ID",
                    name='id',
                    id='andrew-id-input',
                    placeholder="Enter your Andrew ID",
                    required = True,
                    leftSection=iconify(
                        icon="streamline:interface-id-thumb-mark-identification-password-touch-id-secure-fingerprint-finger-security", 
                        width=20
                    ),
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
                    value="EAI",
                    label="Select your program",
                    size="sm",
                    mb=10,
                ),
                dmc.Textarea(
                    label="Academic or Research Interests",
                    placeholder="What are your research and academic interests?",
                    w=500,
                    autosize=True,
                    id="interest-textarea",
                    minRows=2,
                    maxRows=4,
                ),
                dmc.Textarea(
                    label="Previous experience",
                    placeholder="What academic, research or professional experience do you have?",
                    w=500,
                    autosize=True,
                    id="prev-exp-textarea",
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
                    w=270,
                ),
                dmc.NumberInput(
                    label="Starting Year",
                    id="starting-year-input",
                    description="What year did you start at CMU?",
                    value=2024,
                    min=2024,
                    w=270,
                ),
                dmc.NumberInput(
                    label="Number of Semesters Planned",
                    id="planned-semesters-input",
                    description="How many semesters do you plan to take?",
                    value=0,
                    min=3,
                    max=4,
                    w=270,
                ),
                html.Div(id='course-inputs-container'),
                dmc.Button("Sign up", id="sign-up-button", n_clicks=0, style=loginButtonStyle),
                dmc.Divider(mb = 10, mt = 10),
                dmc.Flex(
                    mt = 10,
                    align = 'center',
                    children = [
                        dmc.Text(f"Already have an Account?", c='gray', size = 'xs'),
                        html.A('Sign in', href='/login', style = {'fontSize':'12px'})
                    ]
                ),
                dmc.NotificationProvider(),
                html.Div(
                    id='sign-up-notifications-container',
                    children=[],
                    style={'marginTop': '20px'}
                )  
            ]
        )
    ]
)


@callback(
    Output('course-inputs-container', 'children'),
    Input('first-semester-radio', 'value'),
    Input('completed-semesters-input', 'value'),
    prevent_initial_call=True
)
def update_semester_input(first_semester: str, completed_semesters: int):

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
                                id={'type': 'course-code', 'semester': i, 'course': j},  # Unique ID for course code
                                label='Course Code',
                                placeholder='Enter course code',
                            ),
                            span=6  # Span 6 out of 12 columns for course code
                        ),
                        dmc.GridCol(
                            dmc.TextInput(
                                id={'type': 'course-title', 'semester': i, 'course': j},  # Unique ID for course title
                                label='Course Title',
                                placeholder='Enter course title',
                            ),
                            span=6  # Span 6 out of 12 columns for course title
                        )
                    ], gutter='xs')  # Small gutter between the columns
                )

            # Create an Accordion for each semester with the course inputs
            semester_section = dmc.Accordion(
                    dmc.AccordionItem(
                        children=[
                            dmc.AccordionControl(f"Semester-{i + 1}"),
                            dmc.AccordionPanel(
                                children=courses, # List of course rows
                                id=f"semester-{i + 1}"  # Unique ID for each AccordionPanel
                            ), 
                        ],
                        value=f"semester-{i + 1}"  # Unique value for each AccordionItem
                    )
            )
            semester_sections.append(semester_section)

        return semester_sections
    else:
        return []
    

# Helper function to create a semester entry
def create_semester(semester_number, course_codes, course_titles):
    if course_codes and course_titles:  # Check if both lists are not empty
        if len(course_codes) == len(course_titles):  # Ensure they have the same length
            courses = [
                {"course_name": title, "course_code": code}
                for title, code in zip(course_titles, course_codes)
            ]
            return {"semester": semester_number, "courses": courses}
        else:
            raise ValueError(f"Mismatch in number of course codes and titles for semester {semester_number}.")
    return None  # Return None if no courses exist
    

@callback(
    [Output(component_id="registration-status", component_property="data", allow_duplicate=True),
     Output(component_id="sign-up-notifications-container", component_property="children")],

    Input(component_id='sign-up-button', component_property='n_clicks'),

    State(component_id="first-name-input", component_property="value"),
    State(component_id="andrew-id-input", component_property="value"),
    State(component_id="password-input", component_property="value"),
    State(component_id="program-radio-group", component_property="value"),
    State(component_id="interest-textarea", component_property="value"),
    State(component_id="prev-exp-textarea", component_property="value"),
    State(component_id="first-semester-radio", component_property="value"),
    State(component_id="completed-semesters-input", component_property="value"),
    State(component_id="starting-year-input", component_property="value"),
    State(component_id="planned-semesters-input", component_property="value"),

    State({'type': 'course-code', 'semester': 0, 'course': ALL}, 'value'),
    State({'type': 'course-title', 'semester': 0, 'course': ALL}, 'value'),
    State({'type': 'course-code', 'semester': 1, 'course': ALL}, 'value'),
    State({'type': 'course-title', 'semester': 1, 'course': ALL}, 'value'),
    State({'type': 'course-code', 'semester': 2, 'course': ALL}, 'value'),
    State({'type': 'course-title', 'semester': 2, 'course': ALL}, 'value'),
    prevent_initial_call=True
)
def handle_registration(

    n_clicks: int,
    first_name: str,
    andrew_id: str,
    password: str,
    program: str,
    interests: str,
    prev_exp: str,
    first_semester: str,
    completed_semesters: int,
    starting_year: int,
    planned_semesters: int,

    course_codes_sem1: list,
    course_titles_sem1: list,
    course_codes_sem2: list,
    course_titles_sem2: list,
    course_codes_sem3: list,
    course_titles_sem3: list
):
    
    status = None
    notification = None

    empty_string_fields = all(v != "" for v in [
        first_name, andrew_id, program, interests, prev_exp
    ])
    password_field = password != None

    non_empty_flag = empty_string_fields and password_field

    # Check if the sign up button is clicked
    if n_clicks > 0:

        # Create the courses for each semester
        semesters = []

         # Create semesters and filter out empty ones
        for semester_number, course_codes, course_titles in [
            (1, course_codes_sem1, course_titles_sem1),
            (2, course_codes_sem2, course_titles_sem2),
            (3, course_codes_sem3, course_titles_sem3),
        ]:
            semester_data = create_semester(semester_number, course_codes, course_titles)
            if semester_data:  # Only add if the semester_data is not None
                semesters.append(semester_data)

        # Create the payload
        payload = {
            "first_name": first_name,
            "andrew_ID": andrew_id,
            "password": password,
            "program": program,
            "interests": interests,
            "previous_experience": prev_exp,
            "first_semester": True if first_semester.lower() == 'yes' else False,
            "completed_semesters": completed_semesters,
            "starting_year": starting_year,
            "number_of_planned_semesters": planned_semesters,
            "courses": {
                "semesters": semesters
            }
        }

        if non_empty_flag:

            print(f"PAYLOAD: {payload}")
            
            response = sign_up_user(payload)
            response_json = response.json()

            # response_json = {
            #     "message": "Registration successful",
            #     "status": 201
            # }

            if response.status_code == 201:

                status = {'status': 'registration_success'}

                notification = dmc.Notification(
                    title="Registration Successful",
                    id="simple-notify",
                    action="show",
                    color="green",
                    message=response_json["message"],
                    icon=iconify(icon="ic:round-check"),
                )
            else:
                notification = dmc.Notification(
                    title="Registration Unsuccessful",
                    id="simple-notify",
                    action="show",
                    color="red",
                    message=response_json["message"],
                    icon=iconify(icon="ic:round-error"),
                )
        else:
            notification = dmc.Notification(
                title="Registration Unsuccessful",
                id="simple-notify",
                action="show",
                color="red",
                message="Please fill in all fields",
                icon=iconify(icon="ic:round-error"),
            )

    return status, notification