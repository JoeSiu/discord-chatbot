from chatbots.chatbot import ChatBot
import poe
import utils


class PoeChatBot(ChatBot):
    """
    A class that represents a chatbot that uses poe.com for generating responses.
    """

    def __init__(self, token, model, proxy=None):
        """
        Initializes a new ChatBot instance.

        Args:
            model (str): The name of the poe model to use.
            token (str): The token (cookie) to use for accessing poe.com.
            proxy (str): The proxy to use for connecting to poe.com.

        Raises:
            ValueError: If `model` or `token` are empty strings.
        """
        if not token:
            raise ValueError("token cannot be an empty string")
        if not model:
            raise ValueError("model cannot be an empty string")

        self.token = token
        self.proxy = proxy if proxy and len(proxy.strip()) > 0 else None
        self.client = poe.Client(token=self.token, proxy=self.proxy)
        self.model = self.__get_model_key(model)

    async def query(self, input: str, debug=False):
        """
        Queries the Poe with the given input text and returns the generated response.

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

        success = True
        generated_text = ""

        try:
            # As client.send_message is a synconous iterator, we need to wrap it in async
            # iterator to prevent errors like discord.gateway: shard id none heartbeat blocked for more than x seconds
            ait = utils.async_wrap_iter(
                self.client.send_message(self.model, input, False))
            
            # Combine the response chunks into a single string
            async for chunk in ait:
                generated_text += chunk["text_new"]
                
        except Exception as e:
            success = False
            error_message = str(e)
            
            # If response timeouted while generating (e.g. response is too long)
            if len(generated_text) > 0:
                generated_text = f"{generated_text}... (`{error_message}`)"
            
            # If no response received       
            else:
                generated_text = f"{error_message}"

        return success, generated_text

    def change_model(self, new_model):
        """
        Changes the Hugging Face model used by the chatbot.

        Args:
            new_model (str): The name of the new bot to use.

        Returns:
            True if the model was changed successfully, False if not.
        """
        key = self.__get_model_key(new_model)
        if key is not None:
            self.model = key
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
        self.token = new_token
        self.__update_client()
        return True

    def change_proxy(self, new_proxy):
        """
        Changes the proxy used by the chatbot.

        Args:
            proxy (str): The new proxy to use.

        Returns:
            True if the proxy was changed successfully.
        """
        self.proxy = new_proxy
        self.__update_client()
        return True

    def clear_context(self):
        """
        Clears the chatbot's context
        """
        self.client.send_chat_break(self.model)

    def get_model(self):
        """
        Returns the name of the model used by the chatbot.
        """
        return self.__get_model_value(self.model)

    def get_available_models(self):
        return self.client.bot_names.items()

    def __update_client(self, token=None, proxy=None):
        """
        Updates the Poe client with the provided token and proxy, or the default ones if None.

        Args:
            token (str): The new token to use for the client. Defaults to None.
            proxy (str): The new proxy to use for the client. Defaults to None.

        Returns:
            None

        """
        # Set token to default if None
        if token is None:
            token = self.token
        # Otherwise, update the token attribute
        else:
            self.token = token

        # Set proxy to default if None
        if proxy is None:
            proxy = self.proxy
        # Otherwise, update the proxy attribute
        else:
            self.proxy = proxy

        # Create a new Poe client with the updated token and proxy
        self.client = poe.Client(token=token, proxy=proxy)

    def __get_model_key(self, model_name):
        """
        Returns the key of the model used by the chatbot based on the given model name.

        Args:
            model_name (str): The name of the model to check.

        Returns:
            str or None: The key of the model if it exists, or None if it doesn't.

        """
        # Loop through the items in bot_names
        for key, value in self.get_available_models():
            # If the value matches the given model_name, return the corresponding key
            if utils.normalize_text(value) == utils.normalize_text(model_name):
                return key
        # If no key matches the given model_name, return None
        return None

    def __get_model_value(self, model_name):
        """
        Returns the value of the model used by the chatbot based on the given model name.

        Args:
            model_name (str): The name of the model to check.

        Returns:
            str or None: The key of the model if it exists, or None if it doesn't.

        """
        # Loop through the items in bot_names
        for key, value in self.get_available_models():
            # If the value matches the given model_name, return the corresponding key
            if utils.normalize_text(key) == utils.normalize_text(model_name):
                return value
        # If no key matches the given model_name, return None
        return None
