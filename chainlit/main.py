import os
import grpc
import user_pb2
import user_pb2_grpc
import getpass
import json
import time
import asyncio
from math import sqrt
from dotenv import load_dotenv
import chainlit as cl
from langchain_openai import OpenAI, ChatOpenAI, OpenAIEmbeddings
from langchain.chains import LLMChain, APIChain
from langchain.memory.buffer import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents import initialize_agent, Tool, AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain.tools.retriever import create_retriever_tool
from langchain_community.document_loaders import PyPDFDirectoryLoader
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# import helper functions
from helper import process_data, initialize_vector_store

# Global variables
current_user = None
chain_setup_complete = False

# Load environment variables
load_dotenv()

# Initialize chat history
chat_history = []

# Get OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_user_info():
    global current_user
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
            current_user = user_info
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
    global current_user
    while not current_user:
        user_info = get_user_info()
        if user_info:
            break
        await asyncio.sleep(1)  # Use asyncio.sleep instead of time.sleep
    return current_user

def get_personalized_system_prompt():
    global current_user
    if not current_user:
        return """You are an AI assistant that helps students choose the right courses and understand academic programs at CMU-Africa..."""
    
    return f"""You are an AI assistant helping {current_user['first_name']}, a {current_user['profile']['program']} student at CMU-Africa. 
    You know that {current_user['first_name']} started in {current_user['profile']['starting_year']} and has interests in {current_user['profile']['interests']}.
    Their previous experience includes: {current_user['profile']['previous_experience']}.

    When answering questions, consider their program ({current_user['profile']['program']}) and interests ({current_user['profile']['interests']}) 
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
       - Clearly label student feedback as personal opinions from student.

    3. **student_handbook tool**:
       - Use this tool this tool to answer questions on degrees requirements, graduation policies, and other questions related to CMU-Africa.
    """

# Initialize components
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY)
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

###################################################################################################################################
######################################### COURSE TOOL #############################################################################
# Define file paths
vector_store_path = "Courses_faiss"
course_file_path = "data/all_courses_data.csv"

# Initialize vector store
vector_store = initialize_vector_store(vector_store_path, course_file_path, embeddings, file_type="csv")

# Set up retriever tool
retriever = vector_store.as_retriever()
course_retriever_tool = create_retriever_tool(
    retriever,
    "course_search",
    "Search for information about courses. For any questions about CMU Africa courses, you must use this tool!",
)

###################################################################################################################################	
######################################### COURSE REVIEWS TOOL ####################################################################
# Define file paths
vector_store_path = "student_reviews_faiss"
student_review_directory = "data/student_reviews/"

# Initialize vector store
vector_store = initialize_vector_store(vector_store_path, student_review_directory, embeddings, file_type="pdf")

# Set up retriever tool
retriever = vector_store.as_retriever()
student_reviews_retriever_tool = create_retriever_tool(
    retriever,
    "student_reviews",
    "Search for information about student about courses. For any information about student reviews on CMU Africa courses , you must use this tool!",
)

###################################################################################################################################
######################################### HANDBOOK TOOL ###########################################################################
# Define file paths
vector_store_path = "handbook_faiss"
handbook_directory = "data/handbook/"

# Initialize vector store
vector_store = initialize_vector_store(vector_store_path, handbook_directory, embeddings, file_type="pdf")

# Set up retriever tool
retriever = vector_store.as_retriever()
handbook_retriever_tool = create_retriever_tool(
    retriever,
    "student_handbook",
    "Search for information about official information on degree programs, academic policies, and general requirements at CMU-Africa , you must use this tool!",
)

@cl.on_chat_start
async def setup_chain():
    global current_user
        
    logging.info("Setting up chain and waiting for user login...")
    await cl.Message("Waiting for user login...").send()
    
    user_info = await wait_for_user_login()
    
    if user_info:
        logging.info(f"User info retrieved: {user_info}")
        welcome_message = f"Welcome {user_info['first_name']}! I see you're a {user_info['profile']['program']} student interested in {user_info['profile']['interests']}. How can I help you today?"
        await cl.Message(welcome_message).send()

        llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")
        tools = [course_retriever_tool, student_reviews_retriever_tool, handbook_retriever_tool]  # Added handbook tool
        llm_with_tools = llm.bind_tools(tools)

        prompt = ChatPromptTemplate.from_messages([
            ("system", get_personalized_system_prompt()),
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
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        # Store both user info and chain in session
        cl.user_session.set("user_info", user_info)
        cl.user_session.set("llm_chain", agent_executor)
    else:
        logging.warning("Failed to retrieve user info")
        await cl.Message("Failed to connect to login service. Please try again later.").send()

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
        result = await cl.make_async(llm_chain.invoke)(
            {
                "input": user_message, 
                "chat_history": chat_history
            }
        )

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
# Remove the chain_setup_complete flag as we'll use session management instead
# Remove the cleanup handler as Chainlit handles session cleanup automatically