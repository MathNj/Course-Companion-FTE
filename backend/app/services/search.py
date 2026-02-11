"""
Search Service

Implements grounded Q&A by searching through chapter content and returning relevant sections.
This ensures ChatGPT can answer questions using only course material (zero-hallucination).
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from app.services.content import get_chapter_with_cache

logger = logging.getLogger(__name__)


async def search_chapters(
    query: str,
    accessible_chapter_ids: List[str],
    limit: int = 20,
    chapter_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search through chapter content and return relevant sections.

    This is the core of the Grounded Q&A feature - it allows ChatGPT to find
    relevant course material to answer student questions without hallucinating.

    Args:
        query: Search query string
        accessible_chapter_ids: List of chapter IDs the user has access to
        limit: Maximum number of results to return
        chapter_id: Optional - limit search to specific chapter

    Returns:
        List of search results with chapter_id, section_id, snippet, relevance_score
    """
    # Determine which chapters to search
    chapters_to_search = [chapter_id] if chapter_id else accessible_chapter_ids

    # Normalize query for matching
    query_normalized = query.lower().strip()
    query_terms = _extract_search_terms(query_normalized)

    if not query_terms:
        logger.warning(f"No valid search terms in query: {query}")
        return []

    # Search all accessible chapters
    all_results = []
    for cid in chapters_to_search:
        if cid not in accessible_chapter_ids:
            # Skip chapters user doesn't have access to
            continue

        chapter_content = await get_chapter_with_cache(cid)
        if not chapter_content:
            logger.warning(f"Chapter {cid} not found during search")
            continue

        # Search through chapter sections
        chapter_results = _search_chapter_sections(
            chapter_content=chapter_content,
            query_terms=query_terms,
            query_original=query
        )
        all_results.extend(chapter_results)

    # Sort by relevance score (descending)
    all_results.sort(key=lambda x: x["relevance_score"], reverse=True)

    # Limit results
    return all_results[:limit]


def _extract_search_terms(query: str) -> List[str]:
    """
    Extract meaningful search terms from query.

    Removes common stopwords and very short terms.

    Args:
        query: Normalized query string

    Returns:
        List of search terms
    """
    # Common English stopwords to filter out
    stopwords = {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
        "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
        "to", "was", "will", "with", "what", "how", "does", "do", "can",
        "why", "when", "where", "who", "which", "this", "these", "those",
        "i", "you", "me", "my", "your"
    }

    # Split on whitespace and punctuation
    words = re.findall(r'\b\w+\b', query)

    # Filter stopwords and very short words (< 3 chars)
    terms = [
        word for word in words
        if len(word) >= 3 and word not in stopwords
    ]

    return terms


def _search_chapter_sections(
    chapter_content: Dict[str, Any],
    query_terms: List[str],
    query_original: str
) -> List[Dict[str, Any]]:
    """
    Search through all sections of a chapter.

    Handles both structured chapters (with sections) and raw markdown content (from R2).

    Args:
        chapter_content: Chapter JSON with sections OR raw markdown content
        query_terms: Normalized search terms
        query_original: Original query for snippet highlighting

    Returns:
        List of search results from this chapter
    """
    results = []
    # Content service returns "chapter_id" not "id"
    chapter_id = chapter_content.get("id") or chapter_content.get("chapter_id", "unknown")
    chapter_title = chapter_content.get("title", "Unknown Chapter")

    # Check if chapter has structured sections
    if "sections" in chapter_content and chapter_content["sections"]:
        sections = chapter_content.get("sections", [])

        for section in sections:
            section_id = section.get("id")
            section_title = section.get("title", "")
            section_content = section.get("content", "")

            # Search in section content
            matches = _find_matches_in_text(
                text=section_content,
                query_terms=query_terms
            )

            if matches:
                # Calculate relevance score
                relevance_score = _calculate_relevance_score(
                    matches=matches,
                    query_terms=query_terms,
                    text=section_content
                )

                # Extract snippet with highlighted match
                snippet = _extract_snippet(
                    text=section_content,
                    matches=matches,
                    query_original=query_original,
                    max_length=300
                )

                results.append({
                    "chapter_id": chapter_id,
                    "chapter_title": chapter_title,
                    "section_id": section_id,
                    "section_title": section_title,
                    "snippet": snippet,
                    "relevance_score": relevance_score,
                    "match_count": len(matches)
                })

    # Check if chapter has raw markdown content (from R2)
    elif "content" in chapter_content and chapter_content["content"]:
        raw_content = chapter_content.get("content", "")

        # Search in raw markdown content
        matches = _find_matches_in_text(
            text=raw_content,
            query_terms=query_terms
        )

        if matches:
            # Calculate relevance score
            relevance_score = _calculate_relevance_score(
                matches=matches,
                query_terms=query_terms,
                text=raw_content
            )

            # Extract snippet with highlighted match
            snippet = _extract_snippet(
                text=raw_content,
                matches=matches,
                query_original=query_original,
                max_length=300
            )

            results.append({
                "chapter_id": chapter_id,
                "chapter_title": chapter_title,
                "section_id": "main-content",
                "section_title": chapter_title,
                "snippet": snippet,
                "relevance_score": relevance_score,
                "match_count": len(matches)
            })

    return results


def _find_matches_in_text(text: str, query_terms: List[str]) -> List[Tuple[int, str]]:
    """
    Find all occurrences of query terms in text.

    Args:
        text: Text to search
        query_terms: List of normalized search terms

    Returns:
        List of (position, matched_term) tuples
    """
    text_normalized = text.lower()
    matches = []

    for term in query_terms:
        # Find all occurrences of this term
        start = 0
        while True:
            pos = text_normalized.find(term, start)
            if pos == -1:
                break
            matches.append((pos, term))
            start = pos + 1

    return matches


def _calculate_relevance_score(
    matches: List[Tuple[int, str]],
    query_terms: List[str],
    text: str
) -> float:
    """
    Calculate relevance score for a search result.

    Scoring factors:
    - Number of matches (more is better)
    - Unique terms matched (more is better)
    - Term density (matches closer together is better)
    - Total text length (shorter text with matches is more relevant)

    Args:
        matches: List of (position, term) tuples
        query_terms: Original query terms
        text: Full text being scored

    Returns:
        Relevance score (higher is better)
    """
    if not matches:
        return 0.0

    # Base score: number of matches
    match_count = len(matches)

    # Bonus for matching more unique terms
    unique_terms_matched = len(set(term for _, term in matches))
    unique_terms_total = len(query_terms)
    term_coverage = unique_terms_matched / unique_terms_total if unique_terms_total > 0 else 0

    # Bonus for higher term density (matches / text_length)
    text_length = len(text)
    density = match_count / text_length if text_length > 0 else 0

    # Calculate score (weighted combination)
    score = (
        match_count * 10 +           # Base score from match count
        term_coverage * 50 +         # Bonus for covering more query terms
        density * 1000               # Bonus for higher density
    )

    return round(score, 2)


def _extract_snippet(
    text: str,
    matches: List[Tuple[int, str]],
    query_original: str,
    max_length: int = 300
) -> str:
    """
    Extract a relevant snippet from text with highlighted matches.

    Finds the best segment of text that contains matches and returns
    it with context.

    Args:
        text: Full text
        matches: List of (position, term) tuples
        query_original: Original query for highlighting
        max_length: Maximum snippet length

    Returns:
        Text snippet with "..." before/after if truncated
    """
    if not matches:
        # No matches - return beginning of text
        snippet = text[:max_length]
        if len(text) > max_length:
            snippet += "..."
        return snippet.strip()

    # Find the first match position
    first_match_pos = min(pos for pos, _ in matches)

    # Calculate snippet bounds
    # Try to center the snippet around the first match
    snippet_start = max(0, first_match_pos - max_length // 2)
    snippet_end = min(len(text), snippet_start + max_length)

    # Adjust start if we hit the end
    if snippet_end == len(text) and len(text) > max_length:
        snippet_start = max(0, len(text) - max_length)

    # Extract snippet
    snippet = text[snippet_start:snippet_end]

    # Try to break at sentence boundaries for cleaner snippets
    snippet = _clean_snippet_boundaries(snippet, snippet_start > 0, snippet_end < len(text))

    # Add ellipsis if truncated
    if snippet_start > 0:
        snippet = "..." + snippet
    if snippet_end < len(text):
        snippet = snippet + "..."

    return snippet.strip()


def _clean_snippet_boundaries(snippet: str, truncated_start: bool, truncated_end: bool) -> str:
    """
    Clean snippet boundaries to break at sentence/word boundaries.

    Args:
        snippet: Raw snippet
        truncated_start: Whether snippet is truncated at start
        truncated_end: Whether snippet is truncated at end

    Returns:
        Cleaned snippet
    """
    # If truncated at start, try to start at a sentence or word boundary
    if truncated_start:
        # Look for first sentence boundary (. ! ?)
        sentence_match = re.search(r'[.!?]\s+', snippet)
        if sentence_match:
            snippet = snippet[sentence_match.end():]
        else:
            # No sentence boundary, try word boundary
            word_match = re.search(r'\s+', snippet)
            if word_match:
                snippet = snippet[word_match.end():]

    # If truncated at end, try to end at a sentence or word boundary
    if truncated_end:
        # Look for last sentence boundary
        last_sentence = re.findall(r'.*?[.!?]', snippet)
        if last_sentence:
            snippet = last_sentence[-1]
        else:
            # No sentence boundary, try last word boundary
            words = snippet.rsplit(None, 1)
            if len(words) > 1:
                snippet = words[0]

    return snippet
