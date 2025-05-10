import hashlib
import os
from typing import Optional

import redis


class CacheManager:
    """
    Manages the caching of responses for prompts using a Redis backend.
    """

    def __init__(self):
        """
        Initializes the CacheManager by loading environment variables
        and creating a Redis connection.
        """
        self.REDIS_HOST = os.getenv("REDIS_HOST")
        self.REDIS_PORT = os.getenv("REDIS_PORT")
        self.REDIS_DB = os.getenv("REDIS_DB")
        self.TTL = os.getenv("CACHE_TTL")
        try:
            self.redis = redis.Redis(
                host=self.REDIS_HOST, port=self.REDIS_PORT, db=self.REDIS_DB
            )
            self.redis.ping()
        except redis.ConnectionError:
            self.redis = None

    def _get_cache_key(self, prompt: str) -> str:
        """
        Creates a unique cache key by hashing the prompt content using
        SHA256, then prefixes it with 'llm:prompt:'.
        """
        hashed_prompt = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        return f"llm:prompt:{hashed_prompt}"

    def get(self, prompt: str) -> Optional[str]:
        """
        Retrieves a cached response for the given prompt. If the response
        exists in Redis, it is decoded and returned; otherwise, returns None.
        """
        if self.redis is None:
            return None

        cache_key = self._get_cache_key(prompt)
        try:
            cached_response = self.redis.get(cache_key)
            if cached_response:
                return cached_response.decode("utf-8")
        except redis.ConnectionError:
            pass

        return None

    def set(self, prompt: str, response: str) -> None:
        """
        Saves the given response to Redis under the cache key derived from
        the prompt, with an optional TTL if provided in the environment variables.
        """
        if self.redis is None:
            return

        cache_key = self._get_cache_key(prompt)

        try:
            self.redis.set(cache_key, response, self.TTL)
        except redis.ConnectionError:
            pass
