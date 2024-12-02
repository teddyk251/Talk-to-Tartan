from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from flasgger import Swagger, swag_from
from queue import Queue
import grpc
from concurrent import futures
import time
import json
import threading
import logging
import user_pb2
import user_pb2_grpc

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger("pymongo").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

# MongoDB setup
client = MongoClient('mongodb+srv://teddylnk1:Yd84SMrXpkolJbdy@cluster0.x10eb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['talk_to_tartan']
users_collection = db['users']

# Initialize queue
user_queue = Queue()

class UserService(user_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        logger.info("GetUser called - waiting for user info from queue")
        try:
            # while True:  # Keep trying to get user info
            #     try:
            #         user_info = user_queue.get(timeout=5)  # 5 second timeout
            #         logger.info(f"Retrieved user info from queue: {user_info}")
                    
            #         # Create the response
            #         response = user_pb2.UserInfo(
            #             first_name=user_info.get('first_name', ''),
            #             andrew_id=user_info.get('andrew_id', ''),
            #             profile_json=json.dumps(user_info.get('profile', {}))
            #         )
            #         logger.info(f"Sending response: {response}")
            #         return response
            #     except user_queue.empty:
            #         logger.debug("Queue empty, waiting for user info...")
            #         continue
            if not user_queue.empty():
                user_info = user_queue.get_nowait()  # Non-blocking retrieval
                logger.info(f"User info retrieved from queue: {user_info}")
                # Create and return the response
                logger.info(f"Retrieved user info from queue: {user_info}")
                    
                print(f"User INFO - {user_info}")    # Create the response
                response = user_pb2.UserInfo(
                    first_name=user_info.get('first_name', ''),
                    andrew_id=user_info.get('andrew_id', ''),
                    profile_json=json.dumps(user_info.get('profile', {}))
                )
                logger.info(f"Sending response: {response}")
                return response
            else:
                logger.warning("Queue is empty. No user info available.")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("No user info available in the queue.")
                return user_pb2.UserInfo()

        except Exception as e:
            logger.error(f"Error in GetUser: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return user_pb2.UserInfo()

def serve_grpc():
    try:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
        server.add_insecure_port('[::]:50051')
        logger.info("Starting gRPC server on port 50051")
        server.start()
        logger.info("gRPC server is running")
        server.wait_for_termination()
    except Exception as e:
        logger.error(f"Error starting gRPC server: {e}")

@app.route('/signup', methods=['POST'])
@swag_from({
    'tags': ['User'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'first_name': {'type': 'string'},
                    'andrew_ID': {'type': 'string'},
                    'password': {'type': 'string'},
                    'program': {'type': 'string'},
                    'interests': {'type': 'string'},
                    'previous_experience': {'type': 'string'},
                    'first_semester': {'type': 'boolean'},
                    'completed_semesters': {'type': 'integer'},
                    'starting_year': {'type': 'integer'},
                    'number_of_planned_semesters': {'type': 'integer'},
                    'courses': {
                        'type': 'object',
                        'properties': {
                            'semesters': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'semester': {'type': 'integer'},
                                        'courses': {
                                            'type': 'array',
                                            'items': {
                                                'type': 'object',
                                                'properties': {
                                                    'course_name': {'type': 'string'},
                                                    'course_code': {'type': 'string'}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'User registered successfully'
        },
        400: {
            'description': 'Username and password are required, or user already exists'
        },
        500: {
            'description': 'An error occurred during sign-up'
        }
    }
})
def sign_up():
    try:
        data = request.get_json()
        first_name = data.get('first_name')
        andrewID = data.get('andrew_ID')
        password = data.get('password')
        program = data.get('program')
        interests = data.get('interests')
        previous_experience = data.get('previous_experience')
        firstSemester = data.get('first_semester')
        completedCourses = data.get('courses')
        starting_year = data.get('starting_year')
        number_of_semesters = data.get('number_of_planned_semesters')

        if not andrewID or not password:
            return jsonify({'message': 'Username and password are required!'}), 400

        if users_collection.find_one({'andrewID': andrewID}):
            return jsonify({'message': 'Username already exists!'}), 400

        hashed_password = generate_password_hash(password)
        if not firstSemester:
            users_collection.insert_one({'andrewID': andrewID,
                                          'password': hashed_password,
                                          'first_name': first_name,
                                          'profile': {
                                            'program': program,
                                            'starting_year': starting_year,
                                            'number_of_semesters': number_of_semesters,
                                            'interests': interests,
                                            'previous_experience': previous_experience,
                                            'courses': completedCourses}})
        else:
            users_collection.insert_one({'andrewID': andrewID,
                                          'password': hashed_password,
                                          'first_name': first_name,
                                          'profile': {
                                            'program': program,
                                            'starting_year': starting_year,
                                            'number_of_semesters': number_of_semesters,
                                            'interests': interests,
                                            'previous_experience': previous_experience,
                                            'courses': {'semesters': []}}})

        return jsonify({'message': 'User registered successfully!'}), 201
    except Exception as e:
        return jsonify({'message': 'An error occurred during sign-up', 'error': str(e)}), 500

@app.route('/signin', methods=['POST'])
@swag_from({
    'tags': ['User'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'andrew_ID': {'type': 'string'},
                    'password': {'type': 'string'},
                    'profile': {'type': 'object'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Login successful'
        },
        401: {
            'description': 'Invalid credentials'
        },
        500: {
            'description': 'An error occurred during sign-in'
        }
    }
})
def sign_in():
    try:
        logging.info("Received signin request")
        data = request.get_json()
        logging.debug(f"Sign-in data received: {data}")
        
        andrewID = data.get('andrew_ID')
        password = data.get('password')

        if not andrewID or not password:
            return jsonify({'message': 'Username and password are required!'}), 400

        user = users_collection.find_one({'andrewID': andrewID})
        logging.debug(f"Found user in database: {user}")
        
        if user and check_password_hash(user['password'], password):
            # Prepare user info for the queue
            user_info = {
                'first_name': user.get('first_name', ''),
                'andrew_id': user.get('andrewID', ''),
                'profile': user.get('profile', {})
            }
            
            logging.info(f"User authenticated successfully. Putting user info in queue: {user_info}")
            
            # Clear the queue before putting new user info
            # while not user_queue.empty():
            #     user_queue.get()
            
            user_queue.put(user_info)
            logging.info(f"Queue size after put: {user_queue.qsize()}")
            
            return jsonify({
                'message': 'Login successful!', 
                'user': user['andrewID'],
                'profile': user['profile']
            }), 200

        return jsonify({'message': 'Invalid credentials!'}), 401
        
    except Exception as e:
        logging.error(f"Error in sign_in: {str(e)}")
        return jsonify({'message': 'An error occurred during sign-in', 'error': str(e)}), 500

@app.route('/profile/<andrew_ID>', methods=['GET'])
@swag_from({
    'tags': ['User'],
    'parameters': [
        {
            'name': 'andrew_ID',
            'in': 'path',
            'required': True,
            'type': 'string'
        }
    ],
    'responses': {
        200: {
            'description': 'User profile retrieved successfully'
        },
        404: {
            'description': 'User not found'
        },
        500: {
            'description': 'An error occurred while retrieving profile'
        }
    }
})
def get_profile(andrew_ID):
    try:
        user = users_collection.find_one({'andrewID': andrew_ID})
        if not user:
            return jsonify({'message': 'User not found!'}), 404
        del user["password"]
        del user["_id"]
        return jsonify(user), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred while retrieving profile', 'error': str(e)}), 500
    
@app.route('/add_feedback', methods=['POST'])
def add_feedback():
    """
    Endpoint to handle feedback data sent by the Chainlit app and store it in MongoDB.
    """
    try:
        feedback_data = request.get_json()
        # print(f"Feedback data received: {feedback_data}")
        if not feedback_data:
            return jsonify({"error": "Invalid data format, expected JSON"}), 400

        # Validate required fields
        required_fields = ['id', 'feedback', 'value', 'query', 'response']
        if not all(field in feedback_data for field in required_fields):
            return jsonify({"error": f"Missing required fields. Required: {required_fields}"}), 400

        # Insert feedback data into MongoDB
        feedback_collection = db['feedback']
        feedback_collection.insert_one(feedback_data)

        logging.info(f"Feedback successfully stored in MongoDB: {feedback_data}")
        return jsonify({"message": "Feedback stored successfully!"}), 201
    except Exception as e:
        logging.error(f"Error storing feedback: {e}")
        return jsonify({"error": "An error occurred while storing feedback", "details": str(e)}), 500

@app.route('/get_feedback', methods=['GET'])
def get_feedback():
    """
    Endpoint to retrieve all feedback stored in MongoDB.
    """
    try:
        # Connect to the feedback collection
        feedback_collection = db['feedback']
        
        # Retrieve all feedbacks from the collection
        feedbacks = list(feedback_collection.find({}, {'_id': 0}))  # Exclude MongoDB's '_id' field for cleaner output
        
        if not feedbacks:
            return jsonify({"message": "No feedbacks found"}), 404

        logging.info(f"Feedbacks successfully retrieved from MongoDB:  {feedbacks}")
        return jsonify({"feedbacks": feedbacks}), 200
    except Exception as e:
        logging.error(f"Error retrieving feedback: {e}")
        return jsonify({"error": "An error occurred while retrieving feedback", "details": str(e)}), 500
    
@app.route('/update_profile/<andrew_ID>', methods=['PUT'])
def update_profile(andrew_ID):
    try:
        user = users_collection.find_one({'andrewID': andrew_ID})
        if not user:
            return jsonify({'message': 'User not found!'}), 404

        data = request.get_json()
        users_collection.update_one({'andrewID': andrew_ID}, {'$set': {'profile': data}})
        return jsonify({'message': 'User profile updated successfully!'}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred while updating profile', 'error': str(e)}), 500


if __name__ == '__main__':
    # Start gRPC server in a separate thread
    grpc_thread = threading.Thread(target=serve_grpc, daemon=True)
    grpc_thread.start()
    logger.info("gRPC thread started")
    
    # Give gRPC server time to start
    time.sleep(2)
    
    # Start Flask server
    logger.info("Starting Flask application")
    app.run(port=5001, debug=True, use_reloader=False)  # Disable reloader to avoid duplicate gRPC servers