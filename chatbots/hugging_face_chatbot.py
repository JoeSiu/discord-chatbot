from chatbots.chatbot import ChatBot
import asyncio
import json
import requests


class HuggingFaceChatBot(ChatBot):
    """
    A class that represents a chatbot that uses a Hugging Face model for generating responses.
    """

    def __init__(self, token, model):
        """
        Initializes a new ChatBot instance.

        Args:
            model (str): The name of the Hugging Face model to use.
            token (str): The API token to use for accessing the Hugging Face API.

        Raises:
            ValueError: If `model` or `token` are empty strings.
        """
        if not token:
            raise ValueError("token cannot be an empty string")
        if not model:
            raise ValueError("model cannot be an empty string")

        self.model = model
        self.api_base_url = "https://api-inference.huggingface.co/models"
        self.api_url = f"{self.api_base_url}/{model}"
        self.headers = {"Authorization": f"Bearer {token}"}
        self.past_user_inputs = []
        self.generated_responses = []

    async def query(self, input: str, debug=False):
        """
        Queries the Hugging Face model with the given input text and returns the generated response.

        Args:
            input (str): The user's input text.
            debug (bool): Whether to include debugging information in the response.

        Returns:
            A tuple of two values:
            - success (bool): Whether the query was successful.
            - generated_text (str): The generated response text.
              If `success` is False, this will contain an error message instead.

        Raises:
            ValueError: If `input` is an empty string.
        """
        if not input:
            raise ValueError("input cannot be an empty string")

        data = {
            "inputs": {
                "past_user_inputs": self.past_user_inputs,
                "generated_responses": self.generated_responses,
                "text": input.strip(),
            },
            "options": {
                "wait_for_model": True
            }
        }

        data = json.loads(json.dumps(data))

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, lambda: requests.post(self.api_url, headers=self.headers, json=data))

        response_json = json.loads(response.text)

        success = False
        generated_text = None
        if 'generated_text' in response_json:
            success = True
            generated_text = response_json['generated_text'].strip()
            self.past_user_inputs.append(input)
            self.generated_responses.append(generated_text)
        else:
            error = response_json.get('error')
            if error:
                generated_text = error
            else:
                generated_text = f"No generated text found in response\n`{response_json}`"

        if debug:
            generated_text += f"\n```json\n{json.dumps(response_json, indent=2)}\n```"

        return success, generated_text

    def change_model(self, new_model):
        """
        Changes the Hugging Face model used by the chatbot.

        Args:
            new_model (str): The name of the new Hugging Face model to use.

        Returns:
            True if the model was changed successfully, False if not.
        """
        response = requests.get(f"{self.api_base_url}/{new_model}")
        if response.status_code == 200:
            self.model = new_model
            self.api_url = f"{self.api_base_url}/{new_model}"
            return True
        else:
            return False

    def change_token(self, new_token):
        """
        Changes the API token used by the chatbot.

        Args:
            new_token (str): The new API token to use.
            
        Returns:
            True if the API was changed successfully.
        """
        self.headers = {"Authorization": f"Bearer {new_token}"}
        return True

    def clear_context(self):
        """
        Clears the chatbot's context (i.e. past user inputs and generated responses).
        """
        self.past_user_inputs = []
        self.generated_responses = []

    def get_model(self):
        """
        Returns the name of the Hugging Face model used by the chatbot.
        """
        return self.model
