import logging
import os
import time

import openai
from src.llm.cache_manager import CacheManager

from .model_interface import ModelInterface


class Openai(ModelInterface):
    """
    Provides functionality to generate text using the OpenAI API
    and a caching system.
    """

    def __init__(self):
        """
        Initializes the OpenAI API client and sets up necessary configurations.
        """
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI()
        self.cache_manager = CacheManager()
        self.model = os.getenv("OPENAI_TEXT_MODEL", "gpt-4")
        self.role = os.getenv("OPENAI_TEXT_ROLE", "assistant")
        self.priority = 1

    def get_name(self) -> str:
        """
        Retrieves the identifier name of the OpenAI API handler.

        Returns:
            str: The string `"openai"`, which serves as the identifier for this handler.
        """
        return "openai"

    def generate(
        self,
        prompt: str,
        response_format=None,
        cache: bool = True,
        temperature: float = 0.3,
        max_tokens: int = 1500,
    ):
        """
        Generates text using the OpenAI API based on the provided prompt and settings.

        If caching is enabled and a cached response exists for the given prompt, it is
        returned directly. Otherwise, a request is made to OpenAI's API, and the
        response is optionally cached.

        Args:
            prompt (str): The input text prompt for generating a response.
            response_format (Optional[Any]): Custom response formatting (defaults to None).
            cache (bool, optional): Whether to use caching for responses. Defaults to True.
            temperature (float, optional): Controls output randomness (0.0 to 1.0). Defaults to 0.3.
            max_tokens (int, optional): The maximum number of tokens in the response. Defaults to 1500.

        Returns:
            str: The generated text response from the API.

        Raises:
            openai.RateLimitError: If the API rate limit is exceeded, with retries up to the maximum limit.
            Exception: For any unexpected exceptions during the API request.

        Raises on failure after retries:
            Exception: If rate limits persist after exhausting retries.
        """
        cached_response = self.cache_manager.get(prompt)
        if cache and cached_response is not None:
            return cached_response

        request_params = {
            "model": self.model,
            "messages": [{"role": self.role, "content": f"{prompt}"}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            request_params["response_format"] = response_format

        max_retries = 15
        initial_delay = 5.0
        retry_count = 0

        while retry_count < max_retries:
            try:
                response_object = self.client.chat.completions.create(**request_params)
                response = response_object.choices[0].message.content
                if cache:
                    self.cache_manager.set(prompt, response)
                return response
            except openai.RateLimitError:
                retry_count += 1
                logging.warning(
                    f"Rate limit exceeded. Retry {retry_count}/{max_retries} after {initial_delay} seconds."
                )
                time.sleep(initial_delay)
                initial_delay *= 0.5
            except Exception as e:
                raise Exception(f"An unexpected error occurred: {str(e)}")

        raise Exception(f"Failed after {max_retries} retries due to rate limits.")
