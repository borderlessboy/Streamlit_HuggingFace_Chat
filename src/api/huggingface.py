"""HuggingFace API client."""

import json
import hashlib
import threading
import time
from typing import Generator, Optional, Dict, Tuple

import redis
import requests
import streamlit as st
from requests.exceptions import RequestException

from utils.logger import setup_logger
from config.settings import CACHE_TTL, MAX_CACHE_SIZE, REDIS_CONFIG, MAX_CONTEXT_LENGTH

logger = setup_logger(__name__)


class SimpleCache:
    """A simple in-memory cache implementation with size limit and expiration."""

    def __init__(self, max_size: int = MAX_CACHE_SIZE, ttl: int = CACHE_TTL) -> None:
        """Initialize the cache with size limit and TTL."""
        self.cache: Dict[str, Tuple[str, float]] = {}
        self.max_size = max_size
        self.ttl = ttl
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[str]:
        """Retrieve value from cache if not expired."""
        with self._lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    logger.info("Cache hit for key: %s", key)
                    return value
                logger.info("Cache expired for key: %s", key)
                del self.cache[key]
            logger.info("Cache miss for key: %s", key)
            return None

    def setex(self, key: str, expire_time: int, value: str) -> None:
        """Set value in cache with expiration."""
        with self._lock:
            if len(self.cache) >= self.max_size:
                oldest = min(self.cache.items(), key=lambda x: x[1][1])[0]
                del self.cache[oldest]
                logger.info("Cache full. Removed oldest key: %s", oldest)
            self.cache[key] = (value, time.time())
            logger.info("Cache set for key: %s with expiration: %s", key, expire_time)

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self.cache.clear()
            logger.info("Cache cleared")


def initialize_redis() -> Optional[redis.Redis]:
    """Initialize Redis connection with error handling."""
    try:
        client = redis.Redis(**REDIS_CONFIG)
        client.ping()
        logger.info("Redis connection established successfully")
        return client
    except Exception as e:
        logger.warning(
            "Redis connection failed: %s. Falling back to in-memory cache.", e
        )
        return None


class HuggingFaceAPI:
    """Client for interacting with HuggingFace's inference API."""

    def __init__(self, model_name: str, api_token: str) -> None:
        """Initialize the API client."""
        self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        self.headers = {"Authorization": f"Bearer {api_token}"}
        self.redis_client = initialize_redis()
        self.simple_cache = SimpleCache()
        self.cache_ttl = CACHE_TTL
        logger.info("Initialized HuggingFace API client for model: %s", model_name)

    def get_from_cache(self, cache_key: str) -> Optional[str]:
        """Retrieve response from cache."""
        try:
            if self.redis_client:
                response = self.redis_client.get(cache_key)
                logger.debug(
                    "Redis cache lookup for key %s: %s",
                    cache_key,
                    "hit" if response else "miss",
                )
            else:
                response = self.simple_cache.get(cache_key)
                logger.debug(
                    "Simple cache lookup for key %s: %s",
                    cache_key,
                    "hit" if response else "miss",
                )

            if response:
                logger.info("Cache hit for key: %s", cache_key)
            else:
                logger.info("Cache miss for key: %s", cache_key)
            return response
        except Exception as e:
            logger.error("Error retrieving from cache: %s", e)
            return None

    def save_to_cache(
        self, cache_key: str, response: str, expire_time: int = CACHE_TTL
    ) -> None:
        """Save response to cache."""
        try:
            if self.redis_client:
                self.redis_client.setex(cache_key, expire_time, response)
                logger.debug(
                    "Saved to Redis cache - Key: %s, Size: %d chars",
                    cache_key,
                    len(response),
                )
            else:
                self.simple_cache.setex(cache_key, expire_time, response)
                logger.debug(
                    "Saved to simple cache - Key: %s, Size: %d chars",
                    cache_key,
                    len(response),
                )
            logger.info("Saved response to cache with key: %s", cache_key)
        except Exception as e:
            logger.error("Error saving to cache: %s", e)

    def clear_cache(self) -> None:
        """Clear all cached responses."""
        try:
            if self.redis_client:
                self.redis_client.flushall()
                logger.info("Redis cache cleared")
            else:
                self.simple_cache.clear()
                logger.info("Simple cache cleared")
        except Exception as e:
            logger.error("Error clearing cache: %s", e)

    def _get_cache_key(self, prompt: str, params: dict) -> str:
        """Generate cache key for the request."""
        # Include conversation context in cache key
        context = ""
        if "messages" in st.session_state and st.session_state.messages:
            # Get last 10 messages, excluding the current prompt
            last_messages = (
                st.session_state.messages[-10:-1]
                if len(st.session_state.messages) > 1
                else []
            )
            context = json.dumps(
                [
                    {
                        "role": msg["role"],
                        "content": msg["content"][
                            :100
                        ],  # Limit content length for cache key
                    }
                    for msg in last_messages
                ],
                sort_keys=True,
            )

        # Create unique key from prompt, context, and parameters
        key_content = f"v1:{prompt}:{context}:{json.dumps(params, sort_keys=True)}"
        return f"hf_cache:{hashlib.md5(key_content.encode()).hexdigest()}"

    def _get_params(self) -> dict:
        """Get model parameters from Streamlit session state."""
        return {
            "max_new_tokens": st.session_state.get("max_tokens", 1024),
            "temperature": st.session_state.get("temperature", 0.7),
            "top_p": st.session_state.get("top_p", 0.9),
            "repetition_penalty": st.session_state.get("rep_penalty", 1.1),
            "do_sample": True,
            "return_full_text": False,
        }

    def format_prompt(self, text: str) -> str:
        """Format the prompt with conversation context.

        Args:
            text: The user input text

        Returns:
            str: Formatted prompt string
        """
        system_prompt = (
            "You are a helpful AI coding assistant. "
            "You provide clear, concise, and accurate responses."
        )

        conversation_context = ""
        if "messages" in st.session_state and st.session_state.messages:
            # Get last 10 messages for context
            last_messages = (
                st.session_state.messages[-10:-1]
                if len(st.session_state.messages) > 1
                else []
            )
            for msg in last_messages:
                role = "user" if msg["role"] == "user" else "assistant"
                conversation_context += (
                    f"<|im_start|>{role}\n{msg['content']}\n<|im_end|>\n"
                )

        return f"""<|im_start|>system
{system_prompt}
<|im_end|>
{conversation_context}<|im_start|>user
{text}
<|im_end|>
<|im_start|>assistant
"""

    def generate_stream(self, prompt: str) -> Generator[str, None, None]:
        """Generate text from the model in a streaming fashion."""
        try:
            params = self._get_params()
            params["stream"] = True

            # Format prompt with context
            formatted_prompt = self.format_prompt(prompt)
            tokens_sent = len(formatted_prompt.split())

            # Check cache first
            cache_key = self._get_cache_key(prompt, params)
            cached_response = self.get_from_cache(cache_key)
            if cached_response:
                # Stream cached response
                for char in cached_response:
                    yield char
                    time.sleep(0.01)

                # Update counters after response is complete
                if "total_tokens_sent" not in st.session_state:
                    st.session_state.total_tokens_sent = 0
                if "total_tokens_received" not in st.session_state:
                    st.session_state.total_tokens_received = 0

                st.session_state.total_tokens_sent += tokens_sent
                st.session_state.total_tokens_received += len(cached_response.split())
                return

            # Continue with API request if no cache hit
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "inputs": formatted_prompt,
                    "parameters": params,
                },
                stream=True,
            )
            response.raise_for_status()

            full_response = ""
            tokens_received = 0

            for line in response.iter_lines():
                if not line or line == b"data: [DONE]":
                    continue

                try:
                    if line.startswith(b"data: "):
                        line = line[6:]
                    chunk = json.loads(line)

                    if isinstance(chunk, list) and chunk:
                        chunk = chunk[0]

                    if isinstance(chunk, dict):
                        if "generated_text" in chunk:
                            text = chunk["generated_text"]
                            full_response += text
                            tokens_received += len(text.split())
                            for char in text:
                                yield char
                                time.sleep(0.01)
                        elif "token" in chunk and isinstance(chunk["token"], dict):
                            text = chunk["token"].get("text", "")
                            full_response += text
                            tokens_received += 1
                            yield text

                except json.JSONDecodeError:
                    logger.debug("Skipping non-JSON line: %s", line)
                except (KeyError, TypeError, IndexError) as e:
                    logger.debug("Malformed response chunk: %s - %s", e, line)
                    continue

            # Update counters after response is complete
            if full_response:
                if "total_tokens_sent" not in st.session_state:
                    st.session_state.total_tokens_sent = 0
                if "total_tokens_received" not in st.session_state:
                    st.session_state.total_tokens_received = 0

                st.session_state.total_tokens_sent += tokens_sent
                st.session_state.total_tokens_received += tokens_received

                # Cache the complete response
                self.save_to_cache(cache_key, full_response)

        except RequestException as e:
            logger.error("API request failed: %s", e)
            yield f"Error: {str(e)}"

    def generate(self, prompt: str) -> Optional[str]:
        """Generate text from the model (non-streaming)."""
        try:
            params = self._get_params()
            cache_key = self._get_cache_key(prompt, params)

            # Check cache first
            cached_response = self.get_from_cache(cache_key)
            if cached_response:
                logger.info("Cache hit for: %s", cache_key)
                return cached_response

            # Format prompt with context
            formatted_prompt = self.format_prompt(prompt)

            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "inputs": formatted_prompt,  # Use formatted prompt
                    "parameters": params,
                },
            )
            response.raise_for_status()

            result = response.json()

            # Handle list response
            if isinstance(result, list) and result:
                result = result[0]  # Take first element

            # Handle dict response
            if isinstance(result, dict):
                generated_text = result.get("generated_text")
                if generated_text:
                    # Save to cache
                    self.save_to_cache(cache_key, generated_text)
                return generated_text

            return None

        except RequestException as e:
            logger.error("API request failed: %s", e)
            return None
