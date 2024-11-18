import os
import grpc
import user_pb2
import user_pb2_grpc
import json
import math
import re
import time
import asyncio
import pandas as pd
from dataclasses import asdict
from dotenv import load_dotenv
import chainlit as cl
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents import initialize_agent, Tool, AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool
from langchain_community.vectorstores import FAISS
from langchain.tools.retriever import create_retriever_tool
from validators.models import DegreePlan, Course, SemesterPlan, Program
from validators.validator import DegreeValidator
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Import helper functions
from helper import process_data, initialize_vector_store

# Global variables
chat_history = []

# Load environment variables
load_dotenv()

# Get OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize components
# llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY)
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# Load course data and validator
COURSE_DATA_PATH = "data/all_courses_data.csv"
CORE_COURSES_PATH = "data/core_courses.json"
course_catalog_df = pd.read_csv(COURSE_DATA_PATH)

# Create a lookup dictionary using course code as the key
course_catalog_dict = course_catalog_df.set_index('course_code').to_dict('index')


# Set up course retriever tool
vector_store_path = "Courses_faiss"
vector_store = initialize_vector_store(vector_store_path, COURSE_DATA_PATH, embeddings, file_type="csv")
retriever = vector_store.as_retriever()
course_retriever_tool = create_retriever_tool(
    retriever,
    "course_search",
    "Search for information about courses. For any questions about CMU Africa courses, you must use this tool!",
)

# Set up student reviews retriever tool
vector_store_path = "student_reviews_faiss"
student_review_directory = "data/student_reviews/"
vector_store = initialize_vector_store(vector_store_path, student_review_directory, embeddings, file_type="pdf")
retriever = vector_store.as_retriever()
student_reviews_retriever_tool = create_retriever_tool(
    retriever,
    "student_reviews",
    "Search for information about student reviews of courses at CMU-Africa. For any information about student reviews, use this tool!",
)

# Set up handbook retriever tool
vector_store_path = "handbook_faiss"
handbook_directory = "data/handbook/"
vector_store = initialize_vector_store(vector_store_path, handbook_directory, embeddings, file_type="pdf")
retriever = vector_store.as_retriever()
handbook_retriever_tool = create_retriever_tool(
    retriever,
    "student_handbook",
    "Search for official information about degree programs, academic policies, and general requirements at CMU-Africa.",
)

# Wait for user login function
def get_user_info():
    try:
        logging.info("Attempting to get user info...")
        channel = grpc.insecure_channel('localhost:50051')
        stub = user_pb2_grpc.UserServiceStub(channel)
        response = stub.GetUser(user_pb2.UserRequest())

        user_info = {
            'first_name': response.first_name,
            'andrew_id': response.andrew_id,
            'profile': json.loads(response.profile_json) if response.profile_json else {}
        }

        if user_info['andrew_id']:  # Only return if we got actual user data
            logging.info(f"Successfully retrieved user info: {user_info}")
            return user_info

    except Exception as e:
        logging.debug(f"Error getting user info: {str(e)}")
        return None
    finally:
        try:
            channel.close()
        except:
            pass

async def wait_for_user_login():
    user_info = None
    while not user_info:
        user_info = get_user_info()
        await asyncio.sleep(1)  # Use asyncio.sleep instead of time.sleep
    return user_info

# Get personalized system prompt function
def get_personalized_system_prompt(user_info):
    return f"""You are an AI assistant helping {user_info['first_name']}, a {user_info['profile']['program']} student at CMU-Africa. 
    You know that {user_info['first_name']} started in {user_info['profile']['starting_year']} and has interests in {user_info['profile']['interests']}.
    Their previous experience includes: {user_info['profile']['previous_experience']}.

    When answering questions, consider their program ({user_info['profile']['program']}) and interests ({user_info['profile']['interests']}) 
    to provide more relevant recommendations.

    When answering questions about courses, you must **always retrieve information from both the course_search and student_reviews tools** 
    and combine them in your response. Follow these detailed guidelines:

    1. **course_search tool**:
       - Use this tool to gather official course details such as content, prerequisites, schedules, and any other factual information.
       - This is your primary source for accurate, official course information, and must always be included.
       - Ensure to pass all courses returned from this tool to the student_review tool.

    2. **student_reviews tool**:
       - After gathering the list of courses from **course_search**, use the **exact names or codes of each course** to search for student reviews.
       - Make sure to pass **all course names** to the **student_reviews** tool, one by one, and gather feedback for each.
       - If no reviews are available for certain courses, mention that no reviews are found for those courses.
       - Clearly label student feedback as personal opinions from students.

    3. **student_handbook tool**:
       - Use this tool to answer questions on degree requirements, graduation policies, and other questions related to CMU-Africa.

    4. **validate_course_addition tool**:
       - If the user asks to add a course to their degree plan, validate whether this course can be added to the specified semester.
       - The input should be formatted as '<course_code> semester <semester_id>' 

    5. **validate_full_degree_plan tool**:
       - Use this tool when the user wants to check if their full degree plan meets all graduation requirements.
       - It provides a detailed report indicating whether the plan is valid or if there are any unmet requirements.

    6. **export_degree_plan tool**:
       - Use this tool if the user requests to export their degree plan.
       - Export the degree plan in an Excel format that contains all the relevant course information, including semester, year, units, and course titles.
    """

# Define the tools
def filter_prerequisites(prerequisites):
    course_code_pattern = r'\b\d{2}-\d{3}\b'
    filtered_prerequisites = []
    for prereq in prerequisites:
        # Find all course codes in the prerequisite string
        valid_codes = re.findall(course_code_pattern, prereq)
        # Add to list if valid course codes are found, otherwise skip (empty list)
        if valid_codes:
            filtered_prerequisites.extend(valid_codes)
    return filtered_prerequisites

@tool
def validate_course_addition(input: str) -> str:
    """Validates if a course can be added to the specified semester in the degree plan."""
    
    try:
        # Extract course code and semester from input
        parts = input.split("semester")
        course_code = parts[0].strip()
        semester = int(parts[1].strip())
        #print(f'Starting validation for course {course_code} in semester {semester}')
        print(f"Course code: {course_code}, Semester: {semester}")
        print(f"Course code type: {type(course_code)}, Semester type: {type(semester)}")
        
        
        
        degree_plan = cl.user_session.get("degree_plan")
        if not degree_plan:
            return "No degree plan found in the session. Please create or load a degree plan first."

        validator = cl.user_session.get("validator")
        
        

        # Extract course information from validator dataset
        print('HERE 1')
        course_data = next(course for course in validator.courses_df.to_dict('records') if course['course_code'] == course_code)
        print('HERE 2')
        prereq = course_data.get('Prerequisites', [""])
        print('HERE 3')
        course = Course(
            course_code=course_data['course_code'],
            course_name=course_data['course_name'],
            units=int(course_data['course_units']),
            semester_availability=course_data['course_semester'],
            prerequisites=filter_prerequisites(prereq),
            program=course_data['Course discipline']
        )
        print('HERE 4')
        print("Course data extracted")

        prerequisites = course.prerequisites
        # if prerequisites :
        if prerequisites is None or (isinstance(prerequisites, float) and math.isnan(prerequisites)):
            pass
        else:
            completed_courses = degree_plan.get_completed_courses(semester)
            print(prerequisites, completed_courses)
            for prereq in prerequisites:
                print(prereq)
                if prereq not in completed_courses:
                    return f"Cannot add course {course_code}: Prerequisite {prereq} is not met. Please ensure the course is taken in an earlier semester."
        print("Passed prerequisites check")
        # Check if the course is already added to the degree plan
        for sem in degree_plan.semesters:
            #print(f"split {semester.split(' ')}")
            #semester = semester.split(" ")[1]
            #print(f"Semester {sem.semester} - {int(semester)}")
            if sem.semester == semester:
                if course_code in [c.course_code for c in sem.courses]:
                    return f"Course {course_code} is already added to {semester}."
        print("Passed course already added check")
        
        # Check if the course is available in the specified semester
        # Add logic to convert odd and even semesters to Fall and Spring
        # If semester 1 -> Fall, semester 2 -> Spring , semester 3 -> Fall, etc.
        #print(f"Semester --> {semester}")
        # if "sem" in semester.lower():
        #     semester = semester.split(" ")[1]
        # else:
        semester_number = semester
        semester_type = "Fall" if semester_number % 2 == 1 else "Spring"
        if semester_type not in course.semester_availability:
            return f"The course {course_code} is not available in {semester}. It is offered in {', '.join(course.semester_availability)}."
        
        print("Passed course availability check")


        # Check if the course exceeds the maximum units allowed per semester
        print("Checking max units")
        print(f"Degree plan {degree_plan}")
        print(f"Semesters {degree_plan.semesters}")
        print(f"current Semester {semester}")
        print(type(degree_plan.semesters[0].total_units))
        max_units_per_semester = 54
        for sem in degree_plan.semesters:
            print(f"Semester {sem.semester} - ")
            if sem.semester.lower() == semester.lower():
                print("Semester found")
                total_units = sem.total_units
                print(f"Total units in semester {semester}: {total_units}")
                print(f"Total units type {type(total_units)}")
                if total_units + course.units > max_units_per_semester:
                    return f"Cannot add course {course_code} to {semester}: Exceeds the maximum units allowed per semester ({max_units_per_semester} units)."

        print("Passed max units check")

        # Check if the course has been done in the past semesters
        completed_courses = degree_plan.get_completed_courses( semester)
        print(f" Completed courses - {list(completed_courses)}")
        if course_code in completed_courses:
            return f"Course {course_code} has already been completed in a previous semester."

        print("Passed completed courses check")

        return f"The course {course_code} can be added to {semester}."

    except Exception as e:
        return f"Error validating course addition: {str(e)}"

@tool
def add_course_to_plan(course_code: str, semester: str) -> str:
    """Adds a validated course to the specified semester in the degree plan."""
    try:
        # Retrieve the degree plan from the session
        degree_plan = cl.user_session.get("degree_plan")

        # Locate the course from the course catalog
        validator = cl.user_session.get("validator")
        course_data = next(course for course in validator.courses_df.to_dict('records') if course['course_code'] == course_code)
        # print(f" Course data {course_data}")
        course = Course(
            course_code=course_data['course_code'],
            course_name=course_data['course_name'],
            units=course_data['course_units'],
            semester_availability=course_data['course_semester'],
            prerequisites=course_data.get('Prerequisites', ""),
            program=course_data['Course discipline']
        )

        # Locate the appropriate semester in the degree plan
        semester_found = False
        for sem in degree_plan.semesters:
            if sem.semester.lower() == semester.lower():
                sem.courses.append(course)
                semester_found = True
                break

        if not semester_found:
            # If semester not found, create a new SemesterPlan and add the course
            new_semester = SemesterPlan( semester=semester, courses=[course])
            degree_plan.semesters.append(new_semester)

        # Save updated degree plan in the session
        cl.user_session.set("degree_plan", degree_plan)

        return f"Course {course_code} ({course.course_name}) has been successfully added to {semester}."

    except Exception as e:
        return f"Error adding course {course_code}: {str(e)}"

@tool
def show_degree_plan() -> str:
    """Displays the current degree plan, listing all courses added so far by semester."""
    try:
        # Retrieve the degree plan from the session
        degree_plan = cl.user_session.get("degree_plan")
        
        if not degree_plan or not degree_plan.semesters:
            return "No courses have been added to the degree plan yet."

        # Prepare the output
        response = f"Degree Plan for {degree_plan.student_id} ({degree_plan.program.value}):\n\n"

        # Iterate over each semester in the degree plan
        for sem in sorted(degree_plan.semesters, key=lambda x: (x.semester)):
            response += f"{sem.semester}:\n"
            if sem.courses:
                for course in sem.courses:
                    response += f"  - {course.course_code}: {course.course_name} ({course.units} units)\n"
            else:
                response += "  No courses added for this semester.\n"
            response += "\n"

        return response.strip()

    except Exception as e:
        return f"Error displaying degree plan: {str(e)}"

@tool
def validate_full_degree_plan() -> str:
    """Validates the complete degree plan against program requirements. Returns a detailed validation report."""
    try:
        validator = cl.user_session.get("validator")
        plan = cl.user_session.get("degree_plan")

        if not plan:
            return "No degree plan found in the session. Please create or load a degree plan first."

        report = validator.validate_full_plan(plan)

        if report["is_valid"]:
            response = f"""DEGREE PLAN VALIDATION SUCCESSFUL ✓
- Program: {plan.program}
- Total Units: {report['total_units']}
- Core Units: {report['core_units']}
- Elective Units: {report['elective_units']}

All requirements have been met for graduation."""
        else:
            response = f"""DEGREE PLAN VALIDATION FAILED ✗
- Program: {plan.program}
- Total Units: {report['total_units']}
- Core Units: {report['core_units']}
- Elective Units: {report['elective_units']}

Issues Found:
"""
            for issue in report["issues"]:
                response += f"- {issue}\n"
                
            if report["warnings"]:
                response += "\nWarnings:\n"
                for warning in report["warnings"]:
                    response += f"- {warning}\n"
        
        return response

    except Exception as e:
        return f"ERROR validating degree plan: {str(e)}"

@tool
def export_degree_plan() -> str:
    """Exports the degree plan to an Excel file."""
    try:
        plan = cl.user_session.get("degree_plan")
        
        if not plan:
            return "No degree plan found in the session. Please create or load a degree plan first."

        # Convert DegreePlan dataclass to dictionary suitable for DataFrame conversion
        semester_data = []

        for sem in plan.semesters:
            for course in sem.courses:
                semester_data.append({
                    "Student ID": plan.student_id,
                    "Program": plan.program.value,
                    # "Year": sem.year,
                    "Semester": sem.semester,
                    "Course Code": course.course_code,
                    "Course Name": course.course_name,
                    "Units": course.units
                })

        df = pd.DataFrame(semester_data)
        export_path = f"./data/{plan.student_id}_degree_plan.xlsx"
        df.to_excel(export_path, index=False)

        return f"Degree plan exported successfully to {export_path}."

    except Exception as e:
        return f"ERROR exporting degree plan: {str(e)}"


# Chat start event
@cl.on_chat_start
async def setup_chain():
    logging.info("Setting up chain and waiting for user login...")
    await cl.Message("Waiting for user login...").send()

    # Wait for user to login and retrieve user info
    user_info = await wait_for_user_login()

    if user_info:
        logging.info(f"User info retrieved: {user_info}")
        welcome_message = f"Welcome {user_info['first_name']}! I see you're a {user_info['profile']['program']} student interested in {user_info['profile']['interests']}. How can I help you today?"
        await cl.Message(welcome_message).send()

        # Initialize LLM and tools
        llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-4o", temperature=0)
        
        tools = [
            course_retriever_tool,
            student_reviews_retriever_tool,
            handbook_retriever_tool,
            validate_course_addition,
            add_course_to_plan,
            show_degree_plan,
            validate_full_degree_plan,
            export_degree_plan
        ]

        llm_with_tools = llm.bind_tools(tools)

        prompt = ChatPromptTemplate.from_messages([
            ("system", get_personalized_system_prompt(user_info)),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                    x["intermediate_steps"]
                ),
                "chat_history": lambda x: x["chat_history"]
            }
            | prompt
            | llm_with_tools
            | OpenAIToolsAgentOutputParser()
        )
        
        # Initialize agent executor
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        # Store user info and LLM chain in session
        cl.user_session.set("user_info", user_info)
        cl.user_session.set("llm_chain", agent_executor)
        degreePlan = convert_user_info_to_degree_plan(user_info)
        cl.user_session.set("degree_plan", degreePlan)
        cl.user_session.set("validator", DegreeValidator(COURSE_DATA_PATH))
    else:
        logging.warning("Failed to retrieve user info")
        await cl.Message("Failed to connect to login service. Please try again later.").send()

# Handles user message input
@cl.on_message
async def handle_message(message: cl.Message):
    llm_chain = cl.user_session.get("llm_chain")

    if not llm_chain:
        await cl.Message("Session not initialized properly. Please refresh the page.").send()
        return

    user_message = message.content.lower()

    try:
        # Show thinking message
        thinking_msg = cl.Message(content="Thinking...")
        await thinking_msg.send()

        # Run the chain with async handling
        result = await cl.make_async(llm_chain.invoke)({
            "input": user_message,
            "chat_history": chat_history
        })

        # Remove thinking message
        await thinking_msg.remove()

        # Update chat history
        chat_history.extend([
            HumanMessage(content=user_message),
            AIMessage(content=result["output"]),
        ])

        # Send the actual response
        await cl.Message(content=result["output"]).send()

    except Exception as e:
        logging.error(f"Error processing message: {str(e)}")
        await cl.Message("An error occurred while processing your message. Please try again.").send()


# Wait for user login function
def get_user_info():
    try:
        logging.info("Attempting to get user info...")
        channel = grpc.insecure_channel('localhost:50051')
        stub = user_pb2_grpc.UserServiceStub(channel)
        response = stub.GetUser(user_pb2.UserRequest())

        user_info = {
            'first_name': response.first_name,
            'andrew_id': response.andrew_id,
            'profile': json.loads(response.profile_json) if response.profile_json else {}
        }

        if user_info['andrew_id']:  # Only return if we got actual user data
            logging.info(f"Successfully retrieved user info: {user_info}")
            return user_info

    except Exception as e:
        logging.debug(f"Error getting user info: {str(e)}")
        return None
    finally:
        try:
            channel.close()
        except:
            pass

async def wait_for_user_login():
    user_info = None
    while not user_info:
        user_info = get_user_info()
        await asyncio.sleep(1)  # Use asyncio.sleep instead of time.sleep
    return user_info

def convert_user_info_to_degree_plan(user_info) -> DegreePlan:
    semesters = []

    for semester_data in user_info['profile']['courses']['semesters']:
        # Extract courses from the current semester
        courses = []
        for course in semester_data['courses']:
            if course['course_name'] and course['course_code']:  # Filter out empty or None values
                course_code = course['course_code']

                # Retrieve course details from course catalog using course code
                course_data = course_catalog_dict.get(course_code, {})

                # Create Course object with the retrieved details
                course_obj = Course(
                    course_code=course_code,
                    course_name=course_data.get('course_name', course['course_name']),
                    units=int(course_data.get('course_units', 0)),  # Default to 0 if not found
                    semester_availability=course_data.get('semester_availability', []),
                    prerequisites=course_data.get('prerequisites', []),
                    program=course_data.get('program', user_info['profile']['program'])
                )
                courses.append(course_obj)

        # Create a SemesterPlan object
        # print(f"Semester data: {semester_data}")
        semester = SemesterPlan(
            semester=int(semester_data['semester']),
            courses=courses
        )
        semesters.append(semester)

    # Create the DegreePlan object
    degree_plan = DegreePlan(
        student_id=user_info['andrew_id'],
        program=Program(user_info['profile']['program']),
        semesters=semesters
    )

    return degree_plan
