import ollama
import os
import logging
from typing import Optional, Any
from src.llm.cache_manager import CacheManager
from .model_interface import ModelInterface
from requests.exceptions import RequestException


class Ollama(ModelInterface):
    """
    Class that integrates the Ollama library for Llama models.
    """

    def __init__(self, max_tokens: int = 4000):
        """
        Initializes Ollama for Llama integration with cache management.
        """
        super().__init__(max_tokens=max_tokens)
        self.cache_manager = CacheManager()
        self.model = os.getenv("LLAMA_TEXT_MODEL", "llama3.1")

        base_url = os.getenv("LLAMA_BASE_URL", "http://localhost:11434")
        ollama.base_url = base_url

    def get_name(self) -> str:
        """
        Returns the name of the model ('ollama' in this case).
        """
        return "ollama"

    def generate(
        self,
        prompt: str,
        response_format: Optional[Any] = None,
        cache: bool = True,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
    ):
        """
        Generates text using the Ollama client for Llama based on the provided prompt and settings.

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

        options = {
            "temperature": temperature,
            "num_predict": max_tokens,
        }

        request_params = {
            "model": self.model,
            "prompt": prompt,
            "options": options,
        }

        max_retries = 10
        initial_delay = 5.0
        retry_count = 0

        while retry_count < max_retries:
            try:
                response = ollama.generate(**request_params)
                response_text = response.get("response", "")
                if cache:
                    self.cache_manager.set(prompt, response_text)
                return response_text
            except (ollama.ResponseError, RequestException) as e:
                retry_count += 1
                message = f"Rate limit exceeded. Retry {retry_count}/{max_retries}"
                logging.warning(f"{message} after {initial_delay:.1f} seconds.")
                self._sleep_with_progress(initial_delay, message)
                initial_delay *= 1.5
            except Exception as e:
                raise Exception(f"An unexpected error occurred: {str(e)}")

        raise Exception(f"Failed after {max_retries} retries due to rate limits.")
