import logging
import os
import threading
from typing import List, Optional, Any

from src.llm.model_provider import ModelProvider
from .model_interface import ModelInterface


class Smart(ModelInterface):
    """
    A smart model provider that can switch between multiple LLM providers
    when one is exhausted or hits rate limits.
    """

    def __init__(self, max_tokens: int = 4000):
        """
        Initializes the smart provider by loading the available providers
        from environment variables and setting up thread-safe rotation.
        """
        super().__init__(max_tokens=max_tokens)
        self.model_provider = ModelProvider()
        
        # Get providers from environment.
        # Check LLM_PROVIDERS first, then LLM_PROVIDER as a list.
        providers_env = os.getenv("LLM_PROVIDERS") or os.getenv("LLM_PROVIDER") or "openai"
        self.provider_names = [p.strip() for p in providers_env.split(",") if p.strip()]
        
        self.providers: List[ModelInterface] = []
        self._load_providers()
        
        self._current_provider_index = 0
        self._lock = threading.Lock()
        
        if not self.providers:
            raise ValueError("No valid LLM providers configured for Smart provider")

    def _load_providers(self):
        """Loads instances of the configured providers."""
        for name in self.provider_names:
            try:
                if name == "smart":
                    continue  # Avoid infinite recursion
                provider = self.model_provider.get(name, max_tokens=self.max_tokens)
                self.providers.append(provider)
            except Exception as e:
                logging.warning(f"Failed to load LLM provider '{name}': {e}")

    def get_name(self) -> str:
        """Returns the identifier name of the smart provider."""
        return "smart"

    def _get_current_provider(self) -> ModelInterface:
        """Returns the current active provider in a thread-safe manner."""
        with self._lock:
            return self.providers[self._current_provider_index % len(self.providers)]

    def _switch_to_next_provider(self):
        """Switches to the next available provider in the list."""
        with self._lock:
            old_provider_name = self.providers[self._current_provider_index % len(self.providers)].get_name()
            self._current_provider_index = (self._current_provider_index + 1) % len(self.providers)
            new_provider = self.providers[self._current_provider_index]
            logging.info(f"🔄 Switching to LLM provider: {new_provider.get_name()} (was {old_provider_name})")

    def estimate_tokens(self, prompt: str) -> int:
        """Estimates tokens using the current active provider."""
        return self._get_current_provider().estimate_tokens(prompt)

    def generate(
        self,
        prompt: str,
        response_format: Optional[Any] = None,
        cache: bool = True,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generates text, attempting to use the current provider and falling back
        to others if a failure (like rate limiting) occurs.
        """
        if max_tokens is None:
            max_tokens = self.max_tokens

        # Track failed providers for this specific request
        failed_providers_in_request = set()
        
        # Max attempts to find ANY working provider
        max_total_attempts = len(self.providers) * 2
        attempts = 0
        
        while attempts < max_total_attempts:
            # 1. Determine which provider to use for this attempt
            with self._lock:
                # If the current provider has already failed for this request, 
                # keep switching until we find one that hasn't.
                checked_in_lock = 0
                while self.providers[self._current_provider_index].get_name() in failed_providers_in_request and checked_in_lock < len(self.providers):
                    self._current_provider_index = (self._current_provider_index + 1) % len(self.providers)
                    checked_in_lock += 1
                
                provider = self.providers[self._current_provider_index]
            
            provider_name = provider.get_name()

            try:
                return provider.generate(
                    prompt=prompt,
                    response_format=response_format,
                    cache=cache,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            except Exception as e:
                attempts += 1
                error_msg = str(e).lower()
                
                # Add this provider to the failed set for this specific request
                failed_providers_in_request.add(provider_name)
                
                # If it's a rate limit or exhaustion error, switch global provider
                if any(x in error_msg for x in ["rate limit", "exhausted", "too many requests", "429"]):
                    logging.warning(f"⚠️ Provider '{provider_name}' rate limited: {e}")
                    self._switch_to_next_provider()
                elif any(x in error_msg for x in ["model not found", "invalid argument", "400", "401", "403"]):
                    # Persistent client error
                    logging.error(f"❌ Provider '{provider_name}' permanent failure: {e}")
                    self._switch_to_next_provider()
                else:
                    # For other types of errors, still try another provider
                    logging.error(f"❌ Provider '{provider_name}' unexpected failure: {e}")
                    self._switch_to_next_provider()

                # If all providers have failed for this request, wait and reset
                if len(failed_providers_in_request) >= len(self.providers):
                    logging.warning("⚠️ All providers failed for this request. Waiting 10s before retrying...")
                    self._sleep_with_progress(10, "All providers exhausted, cooling down")
                    failed_providers_in_request.clear()
                    
                if attempts >= max_total_attempts:
                    raise Exception(f"All configured LLM providers failed after {attempts} attempts. Last error: {e}")
                    
        raise Exception("All configured LLM providers failed after multiple attempts.")
