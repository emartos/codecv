import logging
import os
import time
from typing import Optional, Any

import openai
from src.llm.cache_manager import CacheManager

from .model_interface import ModelInterface


class Grok(ModelInterface):
    """
    Provides functionality to generate text using the Grok API
    and a caching system.
    """

    def __init__(self, max_tokens: int = 4000):
        """
        Initializes the OpenAI API client and sets up necessary configurations.
        """
        super().__init__(max_tokens=max_tokens)
        openai.base_url = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")
        openai.api_key = os.getenv("XAI_API_KEY")

        base_url = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")
        api_key = os.getenv("XAI_API_KEY")
        self.client = openai.OpenAI(base_url=base_url, api_key=api_key)

        self.cache_manager = CacheManager()
        self.model = os.getenv("XAI_TEXT_MODEL", "grok-2-latest")
        self.role = os.getenv("XAI_TEXT_ROLE", "assistant")

    def get_name(self) -> str:
        """
        Retrieves the identifier name of the OpenAI API handler.

        Returns:
            str: The string `"grok"`, which serves as the identifier for this handler.
        """
        return "grok"

    def generate(
        self,
        prompt: str,
        response_format: Optional[Any] = None,
        cache: bool = True,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
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
            max_tokens (int, optional): The maximum number of tokens in the response. Defaults to self.max_tokens.

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

        if max_tokens is None:
            max_tokens = self.max_tokens

        request_params = {
            "model": self.model,
            "messages": [{"role": self.role, "content": f"{prompt}"}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

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
                delay = initial_delay * (1.5 ** (retry_count - 1))
                message = f"Rate limit exceeded. Retry {retry_count}/{max_retries}"
                logging.warning(f"{message} after {delay:.1f} seconds.")
                self._sleep_with_progress(delay, message)
            except openai.BadRequestError as e:
                # Specific handling for model not found or other client errors
                error_msg = str(e).lower()
                if "model not found" in error_msg:
                    raise Exception(f"Model not found: {self.model}. Please check your XAI_TEXT_MODEL environment variable.")
                raise Exception(f"Invalid request to Grok API: {str(e)}")
            except Exception as e:
                raise Exception(f"An unexpected error occurred: {str(e)}")

        raise Exception(f"Failed after {max_retries} retries due to rate limits.")
