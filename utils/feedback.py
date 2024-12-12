import chainlit.data as cl_data
import requests
import logging
from chainlit.types import Feedback

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class CustomDataLayer(cl_data.BaseDataLayer):
    """
    Custom Data Layer to manage feedback, threads, and steps.
    """

    async def upsert_feedback(self, feedback: Feedback) -> str:
        """
        Save user feedback along with the query and response.
        """
        # Prepare feedback payload
        print(f"Type of feedback: {type(feedback)}")
        print(f"Type of id: {type(feedback.forId)}")
        print(f"Type of comment: {type(feedback.comment)}")
        print(f"Type of value: {type(feedback.value)}")
        feedback_payload = {
            "id": feedback.forId,
            "feedback": feedback.comment,
            "value": int(feedback.value),
            # "query": last_query,
            # "response": last_response,
        }

        # Save feedback to a backend or database (mocked here as a log)
        try:
            # Replace this with your database or API call
            logging.info(f"Feedback saved: {feedback_payload}")

            # Optionally send feedback to a Flask API
            response = requests.post("http://localhost:5001/add_feedback", json=feedback_payload, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            logging.info("Feedback successfully sent to the backend.")
            return "Feedback stored successfully!"
        except Exception as e:
            logging.error(f"Error saving feedback: {e}")
            return "Failed to store feedback."


    # Abstract methods that must be implemented (placeholders for now)
    async def build_debug_url(self, *args, **kwargs):
        return ""

    async def create_element(self, element, *args, **kwargs):
        pass

    async def create_step(self, step_dict, *args, **kwargs):
        pass

    async def create_user(self, user, *args, **kwargs):
        return None

    async def delete_element(self, element_id, thread_id=None):
        pass

    async def delete_feedback(self, feedback_id, *args, **kwargs):
        return True

    async def delete_step(self, step_id, *args, **kwargs):
        pass

    async def delete_thread(self, thread_id, *args, **kwargs):
        pass

    async def get_element(self, thread_id, element_id):
        return None

    async def get_thread(self, thread_id, *args, **kwargs):
        return None

    async def get_thread_author(self, thread_id, *args, **kwargs):
        return "admin"

    async def get_user(self, identifier: str):
        return None

    async def list_threads(self, pagination, filters, *args, **kwargs):
        return None

    async def update_step(self, step_dict, *args, **kwargs):
        pass

    async def update_thread(
        self,
        thread_id: str,
        name=None,
        user_id=None,
        metadata=None,
        tags=None,
    ):
        pass
