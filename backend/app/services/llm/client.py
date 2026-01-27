"""
Anthropic Claude Sonnet 4.5 Client Wrapper

Handles API communication with retry logic, timeout handling, and error management.
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

import anthropic
from anthropic import Anthropic, APIError, APITimeoutError

from app.config.llm_settings import LLMSettings

logger = logging.getLogger(__name__)


class AnthropicClient:
    """
    Wrapper for Anthropic API with retry logic and error handling.
    """

    def __init__(self):
        """Initialize Anthropic client with configuration."""
        self.settings = LLMSettings()
        self.client = Anthropic(api_key=self.settings.ANTHROPIC_API_KEY)
        self.model = self.settings.ANTHROPIC_MODEL
        self.timeout = self.settings.ANTHROPIC_TIMEOUT
        self.max_retries = self.settings.ANTHROPIC_MAX_RETRIES

    async def create_message(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 2000,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Create a Claude message with retry logic.

        Args:
            system_prompt: System prompt for the conversation
            user_message: User message content
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0-1.0)

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
                # Synchronous API call (run in thread pool to avoid blocking)
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.messages.create(
                        model=self.model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        system=system_prompt,
                        messages=[
                            {"role": "user", "content": user_message}
                        ]
                    )
                )

                # Calculate latency
                latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)

                # Extract response data
                content = response.content[0].text
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
                total_tokens = response.usage.total_tokens

                logger.info(
                    f"Claude API call successful: model={self.model}, "
                    f"tokens={total_tokens}, latency={latency_ms}ms"
                )

                return {
                    "content": content,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "model": response.model,
                    "latency_ms": latency_ms,
                    "stop_reason": response.stop_reason
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
                logger.error(f"Unexpected error in Claude API call: {str(e)}")
                raise

        # Should not reach here
        raise APIError("Max retries exceeded")

    def is_available(self) -> bool:
        """Check if Anthropic API is accessible (simple health check)."""
        try:
            # Quick test with minimal tokens
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception as e:
            logger.error(f"Anthropic API health check failed: {str(e)}")
            return False


# Global client instance (singleton pattern)
_anthropic_client: Optional[AnthropicClient] = None


def get_anthropic_client() -> AnthropicClient:
    """Get or create global Anthropic client instance."""
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = AnthropicClient()
    return _anthropic_client
