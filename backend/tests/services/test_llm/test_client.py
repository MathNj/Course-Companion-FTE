"""
Unit Tests for OpenAI GPT-4o-mini Client

Tests for the LLM API wrapper including retry logic, timeout handling,
and JSON mode functionality.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import asyncio
from datetime import datetime

from app.services.llm.client import OpenAIClient, get_openai_client


class TestOpenAIClient:
    """Unit tests for OpenAI client wrapper."""

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test that OpenAI client initializes correctly."""
        client = OpenAIClient()
        assert client.model == "gpt-4o-mini"
        assert client.timeout == 30
        assert client.max_retries == 3

    @pytest.mark.asyncio
    async def test_singleton_pattern(self):
        """Test that get_openai_client returns same instance."""
        client1 = get_openai_client()
        client2 = get_openai_client()
        assert client1 is client2  # Same instance

    @pytest.mark.asyncio
    @patch('app.services.llm.client.AsyncOpenAI')
    async def test_create_message_success(self, mock_openai_class):
        """Test successful message creation."""
        # Setup mock
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = '{"test": "response"}'
        mock_completion.usage.prompt_tokens = 100
        mock_completion.usage.completion_tokens = 50
        mock_completion.usage.total_tokens = 150
        mock_completion.model = "gpt-4o-mini"
        mock_completion.choices[0].finish_reason = "stop"

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)

        mock_openai_class.return_value = mock_client

        # Import and use
        from app.services.llm.client import OpenAIClient
        client = OpenAIClient()
        client.client = mock_client

        # Execute
        response = await client.create_message(
            system_prompt="You are a helpful assistant.",
            user_message="Test message"
        )

        # Assert
        assert response["content"] == '{"test": "response"}'
        assert response["input_tokens"] == 100
        assert response["output_tokens"] == 50
        assert response["total_tokens"] == 150
        assert response["model"] == "gpt-4o-mini"
        assert "latency_ms" in response

    @pytest.mark.asyncio
    @patch('app.services.llm.client.AsyncOpenAI')
    async def test_create_message_with_json_mode(self, mock_openai_class):
        """Test message creation with JSON mode enabled."""
        # Setup mock
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = '{"key": "value"}'
        mock_completion.usage.prompt_tokens = 50
        mock_completion.usage.completion_tokens = 30
        mock_completion.usage.total_tokens = 80

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        mock_openai_class.return_value = mock_client

        from app.services.llm.client import OpenAIClient
        client = OpenAIClient()
        client.client = mock_client

        # Execute with JSON mode
        response = await client.create_message(
            system_prompt="Return JSON only.",
            user_message="What is 2+2?",
            response_format={"type": "json_object"}
        )

        # Assert JSON mode was passed
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args
        assert call_kwargs[1]['response_format'] == {"type": "json_object"}

    @pytest.mark.asyncio
    @patch('app.services.llm.client.AsyncOpenAI')
    async def test_retry_on_timeout(self, mock_openai_class):
        """Test that client retries on timeout errors."""
        from openai import APITimeoutError

        # Setup mock to fail twice, then succeed
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock()

        call_count = 0

        async def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise APITimeoutError("Request timed out")
            # Third attempt succeeds
            mock_completion = MagicMock()
            mock_completion.choices[0].message.content = "Success after retries"
            mock_completion.usage.prompt_tokens = 10
            mock_completion.usage.completion_tokens = 5
            mock_completion.usage.total_tokens = 15
            return mock_completion

        mock_client.chat.completions.create.side_effect = side_effect
        mock_openai_class.return_value = mock_client

        from app.services.llm.client import OpenAIClient
        client = OpenAIClient()
        client.client = mock_client

        # Execute
        response = await client.create_message(
            system_prompt="Test",
            user_message="Retry test"
        )

        # Assert
        assert call_count == 3  # Retried twice before success
        assert response["content"] == "Success after retries"

    @pytest.mark.asyncio
    @patch('app.services.llm.client.AsyncOpenAI')
    async def test_health_check_success(self, mock_openai_class):
        """Test health check returns True when API is available."""
        mock_client = AsyncMock()
        mock_completion = MagicMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)

        mock_openai_class.return_value = mock_client

        from app.services.llm.client import OpenAIClient
        client = OpenAIClient()
        client.client = mock_client

        # Execute
        is_available = await client.is_available()

        # Assert
        assert is_available is True

    @pytest.mark.asyncio
    @patch('app.services.llm.client.AsyncOpenAI')
    async def test_health_check_failure(self, mock_openai_class):
        """Test health check returns False when API is unavailable."""
        import openai

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=openai.APIError("API unavailable")
        )

        mock_openai_class.return_value = mock_client

        from app.services.llm.client import OpenAIClient
        client = OpenAIClient()
        client.client = mock_client

        # Execute
        is_available = await client.is_available()

        # Assert
        assert is_available is False
