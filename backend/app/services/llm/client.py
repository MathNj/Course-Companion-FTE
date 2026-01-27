"""
OpenAI GPT-4o-mini Client Wrapper

Handles API communication with retry logic, timeout handling, and error management.
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from openai import AsyncOpenAI
from openai import APIError, APITimeoutError

from app.config.llm_settings import LLMSettings

logger = logging.getLogger(__name__)


class OpenAIClient:
    """
    Wrapper for OpenAI API with retry logic and error handling.
    """

    def __init__(self):
        """Initialize OpenAI client with configuration."""
        self.settings = LLMSettings()
        self.client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
        self.model = self.settings.OPENAI_MODEL
        self.timeout = self.settings.OPENAI_TIMEOUT
        self.max_retries = self.settings.OPENAI_MAX_RETRIES

    async def create_message(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 2000,
        temperature: float = 0.3,
        response_format: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a chat completion with GPT-4o-mini with retry logic.

        Args:
            system_prompt: System prompt for the conversation
            user_message: User message content
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0-1.0)
            response_format: Optional JSON mode specification {"type": "json_object"}

        Returns:
            Dictionary containing:
                - content: Response text
                - input_tokens: Input token count
                - output_tokens: Output token count
                - total_tokens: Total token count
                - model: Model used
                - latency_ms: Request duration

        Raises:
            APIError: If API call fails after retries
        """
        start_time = datetime.now()

        for attempt in range(self.max_retries):
            try:
                # Build messages
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]

                # API call with optional JSON mode
                completion = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    response_format=response_format
                )

                # Calculate latency
                latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)

                # Extract response data
                content = completion.choices[0].message.content
                input_tokens = completion.usage.prompt_tokens
                output_tokens = completion.usage.completion_tokens
                total_tokens = completion.usage.total_tokens

                logger.info(
                    f"OpenAI API call successful: model={self.model}, "
                    f"tokens={total_tokens}, latency={latency_ms}ms"
                )

                return {
                    "content": content,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "model": completion.model,
                    "latency_ms": latency_ms,
                    "finish_reason": completion.choices[0].finish_reason
                }

            except APITimeoutError as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Timeout on attempt {attempt + 1}, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"API timeout after {self.max_retries} attempts")
                    raise

            except APIError as e:
                if attempt < self.max_retries - 1 and e.status_code >= 500:
                    # Retry on server errors
                    wait_time = 2 ** attempt
                    logger.warning(f"API error {e.status_code} on attempt {attempt + 1}, retrying...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"API error after {self.max_retries} attempts: {str(e)}")
                    raise

            except Exception as e:
                logger.error(f"Unexpected error in OpenAI API call: {str(e)}")
                raise

        # Should not reach here
        raise APIError("Max retries exceeded")

    async def is_available(self) -> bool:
        """Check if OpenAI API is accessible (simple health check)."""
        try:
            # Quick test with minimal tokens
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI API health check failed: {str(e)}")
            return False


# Global client instance (singleton pattern)
_openai_client: Optional[OpenAIClient] = None


def get_openai_client() -> OpenAIClient:
    """Get or create global OpenAI client instance."""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient()
    return _openai_client


# Backwards compatibility alias
get_anthropic_client = get_openai_client
