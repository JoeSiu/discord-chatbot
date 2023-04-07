import abc


class ChatBot(abc.ABC):
    """
    An abstract base class for chatbot implementations.
    """

    @abc.abstractmethod
    def __init__(self, token, model):
        """
        Initializes a new ChatBot instance.

        Args:
            token (str): The API token to use for accessing the model API.
            model (str): The name of the model to use.
        """
        pass

    @abc.abstractmethod
    async def query(self, input: str, debug=False):
        """
        Queries the model with the given input text and returns the generated response.

        Args:
            input (str): The user's input text.
            debug (bool): Whether to include debugging information in the response.

        Returns:
            A tuple of two values:
            - success (bool): Whether the query was successful.
            - generated_text (str): The generated response text.
              If `success` is False, this will contain an error message instead.
        """
        pass

    @abc.abstractmethod
    def change_model(self, new_model):
        """
        Changes the model used by the chatbot.

        Args:
            new_model (str): The name of the new model to use.

        Returns:
            True if the model was changed successfully, False if not.
        """
        pass

    @abc.abstractmethod
    def change_token(self, new_token):
        """
        Changes the API token used by the chatbot.

        Args:
            new_token (str): The new API token to use.

        Returns:
            True if the API was changed successfully.
        """
        pass

    @abc.abstractmethod
    def clear_context(self):
        """
        Clears the chatbot's context (i.e. past user inputs and generated responses).
        """
        pass

    @abc.abstractmethod
    def get_model(self):
        """
        Returns the name of the model used by the chatbot.
        """
        pass
