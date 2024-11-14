from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from flasgger import Swagger
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
            while True:  # Keep trying to get user info
                try:
                    user_info = user_queue.get(timeout=5)  # 5 second timeout
                    logger.info(f"Retrieved user info from queue: {user_info}")
                    
                    # Create the response
                    response = user_pb2.UserInfo(
                        first_name=user_info.get('first_name', ''),
                        andrew_id=user_info.get('andrew_id', ''),
                        profile_json=json.dumps(user_info.get('profile', {}))
                    )
                    logger.info(f"Sending response: {response}")
                    return response
                except user_queue.empty:
                    logger.debug("Queue empty, waiting for user info...")
                    continue
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

@app.route('/signin', methods=['POST'])
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
            while not user_queue.empty():
                user_queue.get()
            
            user_queue.put(user_info)
            logging.info(f"Queue size after put: {user_queue.qsize()}")
            
            return jsonify({
                'message': 'Login successful!', 
                'user': user['andrewID'],
                'profile':data
            }), 200

        return jsonify({'message': 'Invalid credentials!'}), 401
        
    except Exception as e:
        logging.error(f"Error in sign_in: {str(e)}")
        return jsonify({'message': 'An error occurred during sign-in', 'error': str(e)}), 500

@app.route('/profile/<andrew_ID>', methods=['GET'])
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

if __name__ == '__main__':
    # Start gRPC server in a separate thread
    grpc_thread = threading.Thread(target=serve_grpc, daemon=True)
    grpc_thread.start()
    logger.info("gRPC thread started")
    
    # Give gRPC server time to start
    time.sleep(2)
    
    # Start Flask server
    logger.info("Starting Flask application")
    app.run(port=5000, debug=True, use_reloader=False)  # Disable reloader to avoid duplicate gRPC servers