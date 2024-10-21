# Backend (Flask) Code

from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS  # Allow cross-origin requests (necessary for Dash and Flask interaction)

app = Flask(__name__)
CORS(app)  # Allow requests from Dash to Flask

# MongoDB setup
client = MongoClient('mongodb+srv://teddylnk1:QediKATX9h71opAb@cluster0.1gznc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['my_project_db']
users_collection = db['users']

# User sign-up route
@app.route('/signup', methods=['POST'])
def sign_up():
    data = request.get_json()
    username = data['username']
    password = generate_password_hash(data['password'])

    if users_collection.find_one({'username': username}):
        return jsonify({'message': 'Username already exists!'}), 400

    users_collection.insert_one({'username': username, 'password': password})
    return jsonify({'message': 'User registered successfully!'})

# User sign-in route
@app.route('/signin', methods=['POST'])
def sign_in():
    print("Called sign in")
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = users_collection.find_one({'username': username})
    if user and check_password_hash(user['password'], password):
        return jsonify({'message': 'Login successful!'})
    return jsonify({'message': 'Invalid credentials!'}), 401

if __name__ == '__main__':
    app.run(port=5000, debug=True)