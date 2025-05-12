import logging
from abc import ABC, abstractmethod

import tiktoken


class ModelInterface(ABC):
    """
    Defines an abstract interface for language models, providing a blueprint for
    implementations of text generation and token estimation.

    This class uses the Abstract Base Class (ABC) module to enforce the implementation
    of key methods in subclasses, such as `get_name` and `generate`.

    Attributes:
        model (Optional[Any]): The language model used for token estimation and text generation.
    """

    def __init__(self, model=None):
        """
        Initializes the `ModelInterface` with an optional model configuration.

        Args:
            model (Optional[Any]): The model configuration or identifier. Defaults to None.
        """
        self.model = model

    @abstractmethod
    def get_name(self) -> str:
        """
        Abstract method that must be implemented by subclasses to return
        the name of the language model being used.

        Returns:
            str: The name of the language model.
        """
        pass

    def estimate_tokens(self, prompt: str) -> int:
        """
        Estimates the number of tokens required to process a given text prompt.

        This is done using the Tiktoken library, which provides encoding utilities
        for OpenAI-compatible language models. The method falls back to a default
        encoding (`cl100k_base`) if the given model does not have a specific mapping.

        Args:
            prompt (str): The text input to be tokenized and processed.

        Returns:
            int: The estimated count of tokens present in the given prompt.

        Raises:
            KeyError: If the specified model is not recognized in Tiktoken.
            Warning: Logs a warning when the provided model does not have a specific encoding.
        """
        try:
            # Try to get the encoding for the model automatically
            encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            # Handle the case where the model is not mapped
            # Provide a default encoding here, e.g., use "cl100k_base" or other known encodings
            encoding = tiktoken.get_encoding("cl100k_base")
            # Log or print a warning for debugging purposes
            logging.warning(
                f"⚠️ Model '{self.model}' is not recognized. Using default encoding 'cl100k_base'."
            )

        # Estimate the token count for the prompt
        return len(encoding.encode(prompt))

    @abstractmethod
    def generate(
        self,
        prompt: str,
        response_format=None,
        cache: bool = True,
        temperature: float = 0.3,
        max_tokens: int = 1500,
    ):
        """
        Abstract method that must be implemented by subclasses to generate
        text responses based on a prompt and other optional parameters.

        Args:
            prompt (str): The input text for generating a response.
            response_format (Optional[Any]): Custom formatting for the response. Defaults to None.
            cache (bool, optional): Defines whether caching should be used. Defaults to True.
            temperature (float, optional): Controls randomness in the generated text (range: 0.0 to 1.0). Defaults to 0.3.
            max_tokens (int, optional): The maximum number of tokens allowed in the response. Defaults to 1500.

        Returns:
            Any: The generated text or structured response, depending on the subclass implementation.
        """
        pass
