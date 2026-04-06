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

    def __init__(self, max_tokens: int = 4000):
        """
        Initializes the Google Gemini API client and sets up necessary configurations.
        """
        super().__init__(max_tokens=max_tokens)
        self.cache_manager = CacheManager()
        self.model = os.getenv("GOOGLE_TEXT_MODEL", "gemini-3.1-flash-lite-preview")
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        
        # Configure the Google AI Studio API key
        genai.configure(api_key=self.api_key)

        self.client = genai.GenerativeModel(
            model_name=self.model,
        )
        self.role = os.getenv("GOOGLE_TEXT_ROLE", "user")  # Gemini uses 'user' for prompts

    def get_name(self) -> str:
        """
        Retrieves the identifier name of the Google Gemini API handler.

        Returns:
            str: The string "googlegenai", which serves as the identifier for this handler.
        """
        return "googlegenai"

    def estimate_tokens(self, prompt: str) -> int:
        """
        Estimates the number of tokens using Google's API.

        Args:
            prompt (str): The text input to be tokenized.

        Returns:
            int: The estimated count of tokens.
        """
        try:
            return self.client.count_tokens(prompt).total_tokens
        except Exception:
            # Fallback to the default tiktoken estimation if API call fails
            return super().estimate_tokens(prompt)

    def generate(
        self,
        prompt: str,
        response_format: Optional[Any] = None,
        cache: bool = True,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
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
            max_tokens (int, optional): The maximum number of tokens in the response. Defaults to self.max_tokens.

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

        if max_tokens is None:
            max_tokens = self.max_tokens

        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        if response_format:
            generation_config["response_mime_type"] = (
                "application/json" if response_format == "json" else "text/plain"
            )

        max_retries = 5
        initial_delay = 10.0
        retry_count = 0

        while retry_count < max_retries:
            try:
                tokens = self.estimate_tokens(prompt)
                logging.info(f"📊 Prompt size for '{self.get_name()}': ~{tokens} tokens.")
            
                response = self.client.generate_content(
                    contents=[{"role": self.role, "parts": [{"text": prompt}]}],
                    generation_config=generation_config
                )
                if not response or not hasattr(response, "text") or not response.text:
                     raise exceptions.InternalServerError("Google Gemini returned empty or invalid response")

                response_text = response.text
                if cache:
                    self.cache_manager.set(prompt, response_text)
                return response_text
            except exceptions.ResourceExhausted:
                retry_count += 1
                delay = initial_delay * (1.5 ** (retry_count - 1))  # Less aggressive exponential backoff
                message = f"Rate limit exceeded. Retry {retry_count}/{max_retries}"
                logging.warning(f"{message} after {delay:.1f} seconds.")
                self._sleep_with_progress(delay, message)
            except exceptions.NotFound as e:
                raise Exception(f"Model not found: {self.model}. Check if the model name is correct for the v1beta API: {str(e)}")
            except Exception as e:
                raise Exception(f"An unexpected error occurred: {str(e)}")

        raise Exception(f"Failed after {max_retries} retries due to rate limits.")