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
    return html.Div(
        id='course-plan-content', 
        style={
            "paddingTop": "50px",
            "marginTop": "50px",
            "marginLeft": "100px",   # Adjust for left margin
            "marginRight": "100px",  # Adjust for right margin
        }
    )

# Define the callback to update the content based on login status
@callback(
    Output('course-plan-content', 'children'),
    Input('user-profile', 'data'),
    Input('login-status', 'data'),
)
def update_course_plan(user_profile:dict, login_status: dict):

    if login_status and login_status.get('status') == 'login_success':

        parsed_courses = parse_registered_courses(user_profile)

        semester_tables = []

        for semester, courses in parsed_courses.items():
            table = create_semester_table(semester, courses)
            semester_tables.append(table)

        return dmc.Paper(
            pt=20,
            shadow='sm',
            children=[
                dmc.Text("Here are your registered courses"),
                dmc.Paper(
                    children=semester_tables,
                    shadow="xs"
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


def parse_registered_courses(user_profile: dict):

    # get the courses from the user profile
    registered_courses = user_profile["courses"]["semesters"] # This returns a list of semesters

    # Create a dictionary to store the parsed courses
    parsed_courses = {} # semester_number: [course_code, course_name, units]

    if registered_courses == []:
        parsed_courses = None
    else:
        for semester in registered_courses:
            semester_number = semester["semester"]
            courses = [] # course_code, course_name, units
            for course in semester["courses"]:
                course_code = course["course_code"]
                course_name = course["course_name"]
                units = course["units"]
                courses.append([course_code, course_name, units])
            parsed_courses[semester_number] = courses

    return parsed_courses


def create_semester_table(semester_number: int, courses: list):

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
                            "caption": f"Semester {semester_number} Courses",
                            "head": ["Course Code", "Course Name", "Units"],
                            "body": courses,
                        }
                    )
                ],
                shadow="xs",
                style={"width": "100%"}
            )

    return table