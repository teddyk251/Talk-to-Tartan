from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
# Allow cross-origin requests (necessary for Dash and Flask interaction)
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow requests from Dash to Flask

# MongoDB setup
client = MongoClient(
    'mongodb+srv://teddylnk1:Yd84SMrXpkolJbdy@cluster0.x10eb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['talk_to_tartan']
users_collection = db['users']

# User sign-up route (initial registration)


@app.route('/signup', methods=['POST'])
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
                                            'courses': {'semesters': []
                                                        }
                                                        }})

        return jsonify({'message': 'User registered successfully!'}), 201
    except Exception as e:
        return jsonify({'message': 'An error occurred during sign-up', 'error': str(e)}), 500

# User sign-in route


@app.route('/signin', methods=['POST'])
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
def get_profile(andrew_ID):
    try:
        user = users_collection.find_one({'andrewID': andrew_ID })
        del user["password"]
        del user["andrewID"]
        del user["_id"]
        if not user:

            return jsonify({'message': 'User not found!'}), 404
        return jsonify(user), 200
    except Exception as e:
        print(f"Exception: {e}")
        return jsonify({'message': 'An error occurred while retrieving profile', 'error': str(e)}), 500


# Add a semester and courses for a user
# @app.route('/profile/add-semester', methods=['POST'])
# def add_semester():
#     try:
#         data = request.get_json()
#         username = data.get('username')
#         semester_data = data.get('semester')

#         if not username:
#             return jsonify({'message': 'Username is required!'}), 400

#         if not semester_data:
#             return jsonify({'message': 'Semester data is required!'}), 400

#         user = users_collection.find_one({'username': username})
#         if not user:
#             return jsonify({'message': 'User not found!'}), 404

#         # Add semester to profile
#         users_collection.update_one(
#             {'username': username},
#             {'$push': {'profile.courses.semesters': semester_data}}
#         )
#         return jsonify({'message': 'Semester added successfully!'}), 200
#     except Exception as e:
#         return jsonify({'message': 'An error occurred while adding semester', 'error': str(e)}), 500


# @app.route('/profile/update', methods=['POST'])
# def update_profile():
#     try:
#         data = request.get_json()
#         username = data.get('username')
#         update_data = data.get('update', {})

#         if not username:
#             return jsonify({'message': 'Username is required!'}), 400

#         if not update_data:
#             return jsonify({'message': 'Update data is required!'}), 400

#         user = users_collection.find_one({'username': username})
#         if not user:
#             return jsonify({'message': 'User not found!'}), 404
        
#         # Update profile data
#         users_collection.update_one({'username': username}, {
#                                     '$set': {'profile': update_data}})
#         return jsonify({'message': 'Profile updated successfully!'}), 200
#     except Exception as e:
#         return jsonify({'message': 'An error occurred while updating profile', 'error': str(e)}), 500



if __name__ == '__main__':
    app.run(port=5000, debug=True)
