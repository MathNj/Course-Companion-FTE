"""
Unit Tests for Search Service (Grounded Q&A)

Tests the search functionality that enables ChatGPT to answer questions
using only course material.
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.services.search import (
    search_chapters,
    _extract_search_terms,
    _find_matches_in_text,
    _calculate_relevance_score,
    _extract_snippet,
    _clean_snippet_boundaries
)


# Mock chapter content for testing
MOCK_CHAPTER_1 = {
    "id": "chapter-1",
    "title": "Introduction to Generative AI",
    "sections": [
        {
            "id": "section-1-1",
            "title": "What is Generative AI?",
            "content": "Generative AI refers to artificial intelligence systems that can create new content - including text, images, audio, and code. Unlike traditional AI that classifies or predicts, generative AI produces original outputs based on patterns learned from training data."
        },
        {
            "id": "section-1-2",
            "title": "Types of Generative Models",
            "content": "There are several types of generative models including Large Language Models (LLMs) like GPT, image generation models like DALL-E and Stable Diffusion, and audio generation models. Each model type is specialized for creating different kinds of content."
        }
    ]
}

MOCK_CHAPTER_2 = {
    "id": "chapter-2",
    "title": "Large Language Models",
    "sections": [
        {
            "id": "section-2-1",
            "title": "What are LLMs?",
            "content": "Large Language Models are neural networks trained on massive amounts of text data. They learn patterns, context, and relationships between words to generate human-like text."
        }
    ]
}


class TestExtractSearchTerms:
    """Test search term extraction and stopword filtering."""

    def test_basic_term_extraction(self):
        """Should extract meaningful terms and filter stopwords."""
        query = "what is generative AI and how does it work"
        terms = _extract_search_terms(query.lower())

        # Should include meaningful terms
        assert "generative" in terms
        assert "work" in terms

        # Should exclude stopwords
        assert "what" not in terms
        assert "is" not in terms
        assert "and" not in terms
        assert "how" not in terms
        assert "does" not in terms
        assert "it" not in terms

    def test_filters_short_words(self):
        """Should filter out words shorter than 3 characters."""
        query = "ai ml do it"
        terms = _extract_search_terms(query.lower())

        # All words are < 3 chars or stopwords, should be empty
        assert len(terms) == 0

    def test_handles_punctuation(self):
        """Should split on punctuation correctly."""
        query = "what's generative AI? explain it!"
        terms = _extract_search_terms(query.lower())

        assert "generative" in terms
        assert "explain" in terms

    def test_empty_query(self):
        """Should return empty list for empty query."""
        terms = _extract_search_terms("")
        assert terms == []


class TestFindMatchesInText:
    """Test finding matches of search terms in text."""

    def test_finds_single_term(self):
        """Should find single occurrence of term."""
        text = "Generative AI is powerful"
        matches = _find_matches_in_text(text, ["generative"])

        assert len(matches) == 1
        assert matches[0][1] == "generative"

    def test_finds_multiple_occurrences(self):
        """Should find all occurrences of a term."""
        text = "AI is great. AI is powerful. AI is the future."
        matches = _find_matches_in_text(text, ["ai"])

        # Should find 3 occurrences of "ai"
        assert len(matches) == 3

    def test_finds_multiple_terms(self):
        """Should find all occurrences of multiple terms."""
        text = "Generative AI and traditional AI"
        matches = _find_matches_in_text(text, ["generative", "traditional"])

        assert len(matches) == 2
        terms_found = [term for _, term in matches]
        assert "generative" in terms_found
        assert "traditional" in terms_found

    def test_case_insensitive(self):
        """Should find matches regardless of case."""
        text = "Generative AI and GENERATIVE models"
        matches = _find_matches_in_text(text, ["generative"])

        assert len(matches) == 2

    def test_no_matches(self):
        """Should return empty list when no matches found."""
        text = "Some random text"
        matches = _find_matches_in_text(text, ["nonexistent"])

        assert len(matches) == 0


class TestCalculateRelevanceScore:
    """Test relevance score calculation."""

    def test_more_matches_higher_score(self):
        """More matches should result in higher score."""
        text = "AI " * 100  # 100 occurrences

        matches_many = [(i, "ai") for i in range(100)]
        matches_few = [(i, "ai") for i in range(10)]

        score_many = _calculate_relevance_score(matches_many, ["ai"], text)
        score_few = _calculate_relevance_score(matches_few, ["ai"], text)

        assert score_many > score_few

    def test_term_coverage_affects_score(self):
        """Matching more unique query terms should increase score."""
        text = "generative AI traditional models"

        # Match all terms
        matches_all = [(0, "generative"), (11, "ai"), (14, "traditional")]
        score_all = _calculate_relevance_score(matches_all, ["generative", "ai", "traditional"], text)

        # Match only one term
        matches_one = [(0, "generative")]
        score_one = _calculate_relevance_score(matches_one, ["generative", "ai", "traditional"], text)

        assert score_all > score_one

    def test_no_matches_zero_score(self):
        """No matches should result in zero score."""
        text = "Some text"
        matches = []
        score = _calculate_relevance_score(matches, ["term"], text)

        assert score == 0.0


class TestExtractSnippet:
    """Test snippet extraction with context."""

    def test_extracts_snippet_with_match(self):
        """Should extract snippet centered around match."""
        text = "This is some introductory text. Generative AI is amazing. More text here."
        matches = [(text.lower().find("generative"), "generative")]

        snippet = _extract_snippet(text, matches, "generative AI", max_length=50)

        assert "Generative AI" in snippet
        assert len(snippet) <= 53  # 50 + "..." (3 chars)

    def test_adds_ellipsis_when_truncated(self):
        """Should add ellipsis when text is truncated."""
        text = "A" * 500
        matches = [(250, "term")]

        snippet = _extract_snippet(text, matches, "term", max_length=100)

        # Should have ellipsis on both sides since match is in middle
        assert snippet.startswith("...")
        assert snippet.endswith("...")

    def test_no_ellipsis_for_short_text(self):
        """Should not add ellipsis if entire text fits."""
        text = "Short text"
        matches = [(0, "short")]

        snippet = _extract_snippet(text, matches, "short", max_length=100)

        assert not snippet.startswith("...")
        assert not snippet.endswith("...")

    def test_returns_beginning_when_no_matches(self):
        """Should return beginning of text when no matches."""
        text = "This is some text without matches"
        matches = []

        snippet = _extract_snippet(text, matches, "query", max_length=20)

        assert snippet.startswith("This is some text")


class TestCleanSnippetBoundaries:
    """Test snippet boundary cleaning."""

    def test_cleans_start_at_sentence(self):
        """Should clean start at sentence boundary."""
        snippet = "ncluding text. This is a sentence. Another one."
        cleaned = _clean_snippet_boundaries(snippet, truncated_start=True, truncated_end=False)

        # Should start at "This is a sentence"
        assert cleaned.startswith("This is a sentence")

    def test_cleans_end_at_sentence(self):
        """Should clean end at sentence boundary."""
        snippet = "This is a sentence. Another sent"
        cleaned = _clean_snippet_boundaries(snippet, truncated_start=False, truncated_end=True)

        # Should end at first sentence
        assert cleaned == "This is a sentence."

    def test_no_cleaning_when_not_truncated(self):
        """Should not clean boundaries if not truncated."""
        snippet = "Complete text here"
        cleaned = _clean_snippet_boundaries(snippet, truncated_start=False, truncated_end=False)

        assert cleaned == snippet


@pytest.mark.asyncio
class TestSearchChapters:
    """Test the main search_chapters function."""

    @patch('app.services.search.get_chapter_with_cache')
    async def test_searches_accessible_chapters(self, mock_get_chapter):
        """Should search only chapters user has access to."""
        mock_get_chapter.side_effect = lambda cid: MOCK_CHAPTER_1 if cid == "chapter-1" else MOCK_CHAPTER_2

        results = await search_chapters(
            query="generative AI",
            accessible_chapter_ids=["chapter-1", "chapter-2"],
            limit=10
        )

        # Should find results in both chapters
        assert len(results) > 0
        chapter_ids = [r["chapter_id"] for r in results]
        assert "chapter-1" in chapter_ids

    @patch('app.services.search.get_chapter_with_cache')
    async def test_respects_chapter_filter(self, mock_get_chapter):
        """Should search only specified chapter when chapter_id provided."""
        mock_get_chapter.return_value = MOCK_CHAPTER_1

        results = await search_chapters(
            query="generative AI",
            accessible_chapter_ids=["chapter-1", "chapter-2"],
            limit=10,
            chapter_id="chapter-1"
        )

        # Should only search chapter-1
        mock_get_chapter.assert_called_once_with("chapter-1")

        # All results should be from chapter-1
        for result in results:
            assert result["chapter_id"] == "chapter-1"

    @patch('app.services.search.get_chapter_with_cache')
    async def test_returns_sorted_by_relevance(self, mock_get_chapter):
        """Should return results sorted by relevance score (descending)."""
        mock_get_chapter.return_value = MOCK_CHAPTER_1

        results = await search_chapters(
            query="generative AI models",
            accessible_chapter_ids=["chapter-1"],
            limit=10
        )

        # Check that results are sorted by relevance (descending)
        scores = [r["relevance_score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    @patch('app.services.search.get_chapter_with_cache')
    async def test_respects_limit(self, mock_get_chapter):
        """Should limit number of results returned."""
        mock_get_chapter.return_value = MOCK_CHAPTER_1

        results = await search_chapters(
            query="AI",
            accessible_chapter_ids=["chapter-1"],
            limit=1
        )

        assert len(results) <= 1

    @patch('app.services.search.get_chapter_with_cache')
    async def test_skips_inaccessible_chapters(self, mock_get_chapter):
        """Should not search chapters user doesn't have access to."""
        mock_get_chapter.return_value = MOCK_CHAPTER_1

        results = await search_chapters(
            query="generative AI",
            accessible_chapter_ids=["chapter-1"],  # Only chapter-1 accessible
            limit=10,
            chapter_id="chapter-2"  # Request chapter-2
        )

        # Should not call get_chapter for chapter-2 since user doesn't have access
        mock_get_chapter.assert_not_called()
        assert len(results) == 0

    @patch('app.services.search.get_chapter_with_cache')
    async def test_handles_missing_chapter(self, mock_get_chapter):
        """Should handle gracefully when chapter not found in storage."""
        mock_get_chapter.return_value = None

        results = await search_chapters(
            query="generative AI",
            accessible_chapter_ids=["chapter-1"],
            limit=10
        )

        # Should return empty results without error
        assert results == []

    @patch('app.services.search.get_chapter_with_cache')
    async def test_returns_all_result_fields(self, mock_get_chapter):
        """Should return all required fields in results."""
        mock_get_chapter.return_value = MOCK_CHAPTER_1

        results = await search_chapters(
            query="generative AI",
            accessible_chapter_ids=["chapter-1"],
            limit=10
        )

        assert len(results) > 0

        # Check first result has all required fields
        result = results[0]
        assert "chapter_id" in result
        assert "chapter_title" in result
        assert "section_id" in result
        assert "section_title" in result
        assert "snippet" in result
        assert "relevance_score" in result
        assert "match_count" in result

    @patch('app.services.search.get_chapter_with_cache')
    async def test_empty_query_returns_empty(self, mock_get_chapter):
        """Should return empty results for query with no valid terms."""
        mock_get_chapter.return_value = MOCK_CHAPTER_1

        results = await search_chapters(
            query="a an the",  # All stopwords
            accessible_chapter_ids=["chapter-1"],
            limit=10
        )

        assert results == []
