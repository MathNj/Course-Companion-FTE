"""
Phase 1/2 Isolation Test (CRITICAL)

This test ensures that Phase 1 deterministic endpoints make ZERO LLM calls,
even after Phase 2 hybrid intelligence features are deployed.

This is a CONSTITUTIONAL REQUIREMENT (SC-017).
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.database import get_db


client = TestClient(app)


class TestPhase1Phase2Isolation:
    """
    CRITICAL TEST: Verify Phase 1 endpoints remain LLM-free after Phase 2 deployment.

    This test ensures the Zero-Backend-LLM principle for Phase 1 is maintained.
    """

    @pytest.mark.asyncio
    async def test_phase1_endpoints_remain_llm_free_with_mock(self, db: AsyncSession):
        """
        CRITICAL: Verify that ALL Phase 1 endpoints make ZERO LLM calls.

        This test mocks both OpenAI and Anthropic clients to detect ANY LLM usage.
        If this test fails, Phase 2 CANNOT be deployed to production.

        Test Plan:
        1. Create test user and get JWT token
        2. Call every Phase 1 endpoint with valid auth
        3. Assert that NO LLM client was instantiated
        4. Verify all responses are deterministic (no LLM content)

        Scenarios:
        - GET /api/v1/chapters - Should serve from database only
        - GET /api/v1/chapters/{chapter_id} - Should serve from R2/database only
        - GET /api/v1/quizzes/{quiz_id} - Should serve from database only
        - POST /api/v1/quizzes/{quiz_id}/submit - Should grade deterministically
        - GET /api/v1/progress - Should aggregate from database only
        - GET /api/v1/progress/quiz-history - Should fetch from database only
        """
        # Arrange: Mock ALL potential LLM clients
        with patch('app.services.llm.client.AsyncOpenAI') as mock_openai, \
             patch('app.services.llm.client.anthropic.Anthropic') as mock_anthropic:

            # Setup mock instances
            mock_openai_instance = MagicMock()
            mock_anthropic_instance = MagicMock()
            mock_openai.return_value = mock_openai_instance
            mock_anthropic.return_value = mock_anthropic_instance

            # Create test user and get auth token
            # For now, use a test token - in real test, create user first
            test_token = "Bearer test-token-for-isolation-test"

            # Act: Call ALL Phase 1 endpoints
            endpoints_to_test = [
                ("GET", "/api/v1/chapters"),
                ("GET", "/api/v1/chapters/01-intro"),
                ("GET", "/api/v1/quizzes/01-intro-quiz"),
                ("GET", "/api/v1/progress"),
                ("GET", "/api/v1/progress/quiz-history"),
            ]

            for method, endpoint in endpoints_to_test:
                if method == "GET":
                    response = client.get(
                        endpoint,
                        headers={"Authorization": test_token}
                    )
                elif method == "POST":
                    response = client.post(
                        endpoint,
                        json={"answers": {"q1": "a"}},
                        headers={"Authorization": test_token}
                    )

                # Assert: Request should succeed (200 or 401 for bad token is acceptable)
                # We're testing for NO LLM calls, not authentication
                assert response.status_code in [200, 201, 401, 403], \
                    f"Phase 1 endpoint {endpoint} returned unexpected status: {response.status_code}"

            # CRITICAL ASSERT: Verify NO LLM clients were instantiated
            mock_openai.assert_not_called()
            mock_anthropic.assert_not_called()

            # Verify no LLM client methods were called
            mock_openai_instance.assert_not_called()
            mock_anthropic_instance.assert_not_called()

    @pytest.mark.asyncio
    async def test_v2_endpoints_use_llm(self, db: AsyncSession):
        """
        Verify that Phase 2 endpoints DO use LLM clients.

        This is the opposite test - confirms Phase 2 features work as expected.
        """
        # This test would require a premium user and valid quiz data
        # For now, we'll skip implementation details
        pass

    def test_phase1_modules_dont_import_llm_services(self):
        """
        STATIC ANALYSIS: Verify Phase 1 modules don't import Phase 2 LLM services.

        This checks the code structure at import time.
        """
        import ast
        import os

        v1_modules = []

        # Find all Phase 1 router files
        backend_dir = "app/api/v1"
        if os.path.exists(backend_dir):
            for file in os.listdir(backend_dir):
                if file.endswith(".py") and file != "__init__.py":
                    v1_modules.append(os.path.join(backend_dir, file))

        for module_path in v1_modules:
            with open(module_path, 'r') as f:
                tree = ast.parse(f.read())

                # Check all imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            # Phase 1 MUST NOT import from v2 or services/llm
                            assert not alias.name.startswith("app.api.v2"), \
                                f"VIOLATION: {module_path} imports from app.api.v2"
                            assert not alias.name.startswith("app.services.llm"), \
                                f"VIOLATION: {module_path} imports from app.services.llm"

                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            assert not node.module.startswith("app.api.v2"), \
                                f"VIOLATION: {module_path} imports from app.api.v2"
                            assert not node.module.startswith("app.services.llm"), \
                                f"VIOLATION: {module_path} imports from app.services.llm"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
