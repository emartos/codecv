import logging
import os
import time
from typing import Optional, Any

import openai
from src.llm.cache_manager import CacheManager

from .model_interface import ModelInterface


class Openai(ModelInterface):
    """
    Provides functionality to generate text using the OpenAI API
    and a caching system.
    """

    def __init__(self, max_tokens: int = 4000):
        """
        Initializes the OpenAI API client and sets up necessary configurations.
        """
        super().__init__(max_tokens=max_tokens)
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI()
        self.cache_manager = CacheManager()
        self.model = os.getenv("OPENAI_TEXT_MODEL", "gpt-5.4-mini")
        self.role = os.getenv("OPENAI_TEXT_ROLE", "assistant")

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
            "max_completion_tokens": max_tokens,
        }
        if response_format:
            request_params["response_format"] = response_format

        max_retries = 10
        initial_delay = 5.0
        retry_count = 0

        while retry_count < max_retries:
            try:
                tokens = self.estimate_tokens(prompt)
                logging.debug(f"DEBUG - OpenAI Prompt: {prompt}")
                logging.info(f"📊 Prompt size for '{self.get_name()}': ~{tokens} tokens.")
            
                response_object = self.client.chat.completions.create(**request_params)
                logging.debug(f"DEBUG - OpenAI Response Object: {response_object}")
                
                response = response_object.choices[0].message.content
                finish_reason = response_object.choices[0].finish_reason

                if response is None or response.strip() == "":
                    # Log detail before failing
                    error_msg = f"❌ OpenAI returned empty content. Finish reason: '{finish_reason}'. Full response: {response_object}"
                    logging.error(error_msg)
                    
                    # Log the prompt that caused the empty response for easier debugging
                    logging.error(f"❌ Problematic Prompt: {prompt}")

                    # For debugging as requested, we fail immediately to stop wasting tokens
                    raise Exception(error_msg)

                if cache:
                    self.cache_manager.set(prompt, response)
                return response
            except openai.RateLimitError:
                retry_count += 1
                message = f"Rate limit exceeded. Retry {retry_count}/{max_retries}"
                logging.warning(f"{message} after {initial_delay:.1f} seconds.")
                self._sleep_with_progress(initial_delay, message)
                initial_delay *= 1.5
            except Exception as e:
                # Only raise if it's not an empty content error we're already handling
                if "empty content" not in str(e):
                    raise Exception(f"An unexpected error occurred: {str(e)}")
                raise

        raise Exception(f"Failed after {max_retries} retries due to rate limits or empty responses.")
