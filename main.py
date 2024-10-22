import os
import getpass
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

# import helper functions
from helper import process_data, initialize_vector_store

# Load environment variables
load_dotenv()

# Initialize chat history
chat_history = []

# Get OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize components
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY)
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

###################################################################################################################################
######################################### COURSE TOOL #############################################################################
# Define file paths
vector_store_path = "Courses_faiss"
course_file_path = "data/all_courses_data.csv"


# Initialize vector store
vector_store = initialize_vector_store(vector_store_path, course_file_path, embeddings,file_type="csv")

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
vector_store = initialize_vector_store(vector_store_path, student_review_directory, embeddings,file_type="pdf")

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
vector_store = initialize_vector_store(vector_store_path, handbook_directory, embeddings,file_type="pdf")

# Set up retriever tool
retriever = vector_store.as_retriever()
handbook_retriever_tool = create_retriever_tool(
    retriever,
    "student_handbook",
    "Search for information about official information on degree programs, academic policies, and general requirements at CMU-Africa , you must use this tool!",
)



prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are an AI assistant that helps students choose the right courses and understand academic programs at CMU-Africa. When answering questions about courses, you must **always retrieve information from both the course_search and student_reviews tools** and combine them in your response. Follow these detailed guidelines:

1. **course_search tool**:
   - Use this tool to gather official course details such as content, prerequisites, schedules, and any other factual information.
   - This is your primary source for accurate, official course information, and must always be included.
   - Ensure to pass all courses returned from this tool to the student_review tool.


2. **student_reviews tool**:
   - After gathering the list of courses from **course_search**, use the **exact names or codes of each course** to search for student reviews..
   - Make sure to pass **all course names** to the **student_reviews** tool, one by one, and gather feedback for each.
   - If no reviews are available for certain courses, mention that no reviews are found for those courses.
   - Clearly label student feedback as personal opinions from student.


3. **student_handbook tool**:
   - Use this tool this tool to answer questions on degrees requirements,  graduation policies, and other questions related to CMU-Africa.



            
            """
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)


@cl.on_chat_start
def setup_chain():
    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")
    tools = [course_retriever_tool, student_reviews_retriever_tool]
    llm_with_tools = llm.bind_tools(tools)

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

    cl.user_session.set("llm_chain", agent_executor)


@cl.on_message
async def handle_message(message: cl.Message):
    user_message = message.content.lower()
    llm_chain = cl.user_session.get("llm_chain")

    result = llm_chain.invoke(
        {"input": user_message, "chat_history": chat_history})
    chat_history.extend(
        [
            HumanMessage(content=user_message),
            AIMessage(content=result["output"]),
        ]
    )

    await cl.Message(result['output']).send()
