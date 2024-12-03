import requests

# BASE_URL = "http://172.29.104.127:5001"  # Flask backend API URL
BASE_URL = "http://localhost:5001"  # Flask backend API URL

# Function for sign-up request
def sign_up_user(payload: dict) -> dict:
    """
    Sends a POST request to the sign-up endpoint to create a new user.
    
    Args:
        payload (dict): A dictionary containing user registration details.
    
    Returns:
        dict: The JSON response from the Flask backend after sign-up.
    """
    endpoint = "signup"  # Placeholder for your sign-up endpoint

    response = requests.post(url=f"{BASE_URL}/{endpoint}", json=payload)

    return response


# Function for sign-in request
def sign_in_user(payload: dict) -> dict:
    """
    Sends a POST request to the sign-in endpoint to authenticate a user.
    
    Args:
        andrew_id (str): The Andrew ID for login.
        password (str): The user's password.
    
    Returns:
        dict: The JSON response from the Flask backend after sign-in.
    """
    endpoint = "signin"  # Placeholder for your login endpoint

    response = requests.post(url=f"{BASE_URL}/{endpoint}", json=payload)

    return response


# Function for fetching feedack data
def get_feedback_data() -> dict:
    """
    Sends a GET request to the feedback endpoint to retrieve feedback data.
    
    Returns:
        dict: The JSON response from the Flask backend with feedback data.
    """
    endpoint = "get_feedback"  # Placeholder for your feedback endpoint

    response = requests.get(url=f"{BASE_URL}/{endpoint}")

    return response


# # Example sign-up payload
# sign_up_payload = {
#     "first_name": "John Doe",
#     "andrew_ID": "johndoe",
#     "password": "password",
#     "program": "MSIT",
#     "interests": "I am interested in AI and ML",
#     "previous_experience": "I have a BSc in Computer Science",
#     "first_semester": False,
#     "completed_semesters": 2,
#     "starting_year": 2021,
#     "number_of_planned_semesters": 4,
#     "courses": {
#         "semesters": [
#             {
#                 "semester": 1,
#                 "courses": [
#                     {
#                         "course_name": "Deep Learning",
#                         "course_code": "CS601"
#                     }
#                 ]
#             },
#             {
#                 "semester": 2,
#                 "courses": [
#                     {
#                         "course_name": "Data Mining",
#                         "course_code": "CS605"
#                     }
#                 ]
#             }
#         ]
#     }
# }

# # Example usage
# if __name__ == "__main__":
#     # Call the sign-up function
#     sign_up_response = sign_up_user(sign_up_payload)
#     print("Sign-Up Response:", sign_up_response)

#     # Call the sign-in function
#     login_response = sign_in_user(andrew_id="johndoe", password="password")
#     print("Login Response:", login_response)
