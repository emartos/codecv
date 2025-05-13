import logging
import os
import time
from typing import Optional, Any

import google.generativeai as genai
from google.api_core import exceptions
from src.llm.cache_manager import CacheManager

from .model_interface import ModelInterface


class Googlegenai(ModelInterface):
    """
    Provides functionality to generate text using the Google Gemini API
    and a caching system.
    """

    def __init__(self):
        """
        Initializes the Google Gemini API client and sets up necessary configurations.
        """
        self.cache_manager = CacheManager()
        self.model = os.getenv("GOOGLE_TEXT_MODEL", "gemini-1.5-flash")
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        self.client = genai.GenerativeModel(
            model_name=self.model,
            # API key is automatically picked up from GOOGLE_API_KEY env var
            # or can be passed explicitly via client_options if needed
        )
        self.role = os.getenv("GOOGLE_TEXT_ROLE", "user")  # Gemini uses 'user' for prompts

    def get_name(self) -> str:
        """
        Retrieves the identifier name of the Google Gemini API handler.

        Returns:
            str: The string "googlegenai", which serves as the identifier for this handler.
        """
        return "googlegenai"

    def generate(
        self,
        prompt: str,
        response_format: Optional[Any] = None,
        cache: bool = True,
        temperature: float = 0.3,
        max_tokens: int = 1500,
    ) -> str:
        """
        Generates text using the Google Gemini API based on the provided prompt and settings.

        If caching is enabled and a cached response exists for the given prompt, it is
        returned directly. Otherwise, a request is made to Google's Gemini API, and the
        response is optionally cached.

        Args:
            prompt (str): The input text prompt for generating a response.
            response_format (Optional[Any]): Custom response formatting (defaults to None).
            cache (bool, optional): Whether to use caching for responses. Defaults to True.
            temperature (float, optional): Controls output randomness (0.0 to 2.0). Defaults to 0.3.
            max_tokens (int, optional): The maximum number of tokens in the response. Defaults to 1500.

        Returns:
            str: The generated text response from the API.

        Raises:
            google.api_core.exceptions.ResourceExhausted: If the API rate limit is exceeded, with retries up to the maximum limit.
            Exception: For any unexpected exceptions during the API request.

        Raises on failure after retries:
            Exception: If rate limits persist after exhausting retries.
        """
        cached_response = self.cache_manager.get(prompt)
        if cache and cached_response is not None:
            return cached_response

        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        if response_format:
            generation_config["response_mime_type"] = (
                "application/json" if response_format == "json" else "text/plain"
            )

        max_retries = 15
        initial_delay = 5.0
        retry_count = 0

        while retry_count < max_retries:
            try:
                response = self.client.generate_content(
                    contents=[{"role": self.role, "parts": [{"text": prompt}]}],
                    generation_config=generation_config
                )
                response_text = response.text
                if cache:
                    self.cache_manager.set(prompt, response_text)
                return response_text
            except exceptions.ResourceExhausted:
                retry_count += 1
                logging.warning(
                    f"Rate limit exceeded. Retry {retry_count}/{max_retries} after {initial_delay} seconds."
                )
                time.sleep(initial_delay)
                initial_delay *= 0.5
            except Exception as e:
                raise Exception(f"An unexpected error occurred: {str(e)}")

        raise Exception(f"Failed after {max_retries} retries due to rate limits.")