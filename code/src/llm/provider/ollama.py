import ollama
import os
from src.llm.cache_manager import CacheManager
from .model_interface import ModelInterface
from requests.exceptions import RequestException


class Ollama(ModelInterface):
    """
    Class that integrates the Ollama library for Llama models.
    """

    def __init__(self):
        """
        Initializes Ollama for Llama integration with cache management.
        """
        self.cache_manager = CacheManager()
        self.model = os.getenv("LLAMA_TEXT_MODEL", "llama3.2")

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
        response_format=None,
        cache: bool = True,
        temperature: float = 0.3,
        max_tokens: int = 1500,
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
            "prompt": prompt,
        }

        max_retries = 15
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
                logging.warning(
                    f"Rate limit exceeded. Retry {retry_count}/{max_retries} after {initial_delay} seconds."
                )
                time.sleep(initial_delay)
                initial_delay *= 0.5
            except Exception as e:
                raise Exception(f"An unexpected error occurred: {str(e)}")

        raise Exception(f"Failed after {max_retries} retries due to rate limits.")
