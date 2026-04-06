import logging
import time
import random
from abc import ABC, abstractmethod
from typing import Optional, Any

import tiktoken
from tqdm import tqdm


class ModelInterface(ABC):
    """
    Defines an abstract interface for language models, providing a blueprint for
    implementations of text generation and token estimation.

    This class uses the Abstract Base Class (ABC) module to enforce the implementation
    of key methods in subclasses, such as `get_name` and `generate`.

    Attributes:
        model (Optional[Any]): The language model used for token estimation and text generation.
    """

    def __init__(self, model=None, max_tokens=4000):
        """
        Initializes the `ModelInterface` with an optional model configuration.

        Args:
            model (Optional[Any]): The model configuration or identifier. Defaults to None.
            max_tokens (int): The maximum number of tokens allowed in the response. Defaults to 4000.
        """
        self.model = model
        self.max_tokens = max_tokens

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

        The default implementation uses the Tiktoken library, which provides encoding
        utilities for OpenAI-compatible language models. Subclasses can override this
        method to provide model-specific estimation.

        Args:
            prompt (str): The text input to be tokenized and processed.

        Returns:
            int: The estimated count of tokens present in the given prompt.
        """
        try:
            # Try to get the encoding for the model automatically
            encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            # Handle the case where the model is not mapped
            # Provide a default encoding here, e.g., use "cl100k_base" or other known encodings
            encoding = tiktoken.get_encoding("cl100k_base")

        # Estimate the token count for the prompt
        return len(encoding.encode(prompt))

    @abstractmethod
    def generate(
        self,
        prompt: str,
        response_format=None,
        cache: bool = True,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
    ):
        """
        Abstract method that must be implemented by subclasses to generate
        text responses based on a prompt and other optional parameters.

        Args:
            prompt (str): The input text for generating a response.
            response_format (Optional[Any]): Custom formatting for the response. Defaults to None.
            cache (bool, optional): Defines whether caching should be used. Defaults to True.
            temperature (float, optional): Controls randomness in the generated text (range: 0.0 to 1.0). Defaults to 0.3.
            max_tokens (int, optional): The maximum number of tokens allowed in the response. Defaults to self.max_tokens.

        Returns:
            Any: The generated text or structured response, depending on the subclass implementation.
        """
        pass

    def _sleep_with_progress(self, seconds: float, message: str) -> None:
        """
        Sleeps for a specified number of seconds while showing a progress bar.

        Args:
            seconds (float): Number of seconds to sleep.
            message (str): Message to display with the progress bar.
        """
        # Use a small jitter to avoid synchronized retries
        jitter = random.uniform(0.1, 1.0)
        total_seconds = seconds + jitter
        
        # Round up to ensure at least some progress is shown if seconds > 0
        total_steps = max(1, int(total_seconds))
        
        # tqdm for progress bar
        with tqdm(total=total_steps, desc=message, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}s", leave=False) as pbar:
            for _ in range(total_steps):
                time.sleep(1)
                pbar.update(1)
            
            # Remaining fractional part
            remaining = total_seconds - total_steps
            if remaining > 0:
                time.sleep(remaining)
                # No need to update pbar for fractional part if we already reached total_steps
