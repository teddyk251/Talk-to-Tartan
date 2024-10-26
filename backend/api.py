from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS  # Allow cross-origin requests (necessary for Dash and Flask interaction)
from flasgger import Swagger, swag_from

app = Flask(__name__)
CORS(app)  # Allow requests from Dash to Flask
swagger = Swagger(app)  # Initialize Swagger documentation

# MongoDB setup
client = MongoClient('mongodb+srv://teddylnk1:Yd84SMrXpkolJbdy@cluster0.x10eb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['talk_to_tartan']
users_collection = db['users']

# User sign-up route (initial registration)
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

# User sign-in route
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
                    'password': {'type': 'string'}
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
        data = request.get_json()
        andrewID = data.get('andrew_ID')
        password = data.get('password')

        if not andrewID or not password:
            return jsonify({'message': 'Username and password are required!'}), 400

        user = users_collection.find_one({'andrewID': andrewID})
        if user and check_password_hash(user['password'], password):
            return jsonify({'message': 'Login successful!', 'user': user['andrewID']}), 200

        return jsonify({'message': 'Invalid credentials!'}), 401
    except Exception as e:
        return jsonify({'message': 'An error occurred during sign-in', 'error': str(e)}), 500

# Get user profile
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
        user = users_collection.find_one({'andrewID': andrew_ID })
        if not user:
            return jsonify({'message': 'User not found!'}), 404
        del user["password"]
        del user["andrewID"]
        del user["_id"]
        return jsonify(user), 200
    except Exception as e:
        print(f"Exception: {e}")
        return jsonify({'message': 'An error occurred while retrieving profile', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
