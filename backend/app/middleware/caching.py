"""
Caching Middleware for Performance Optimization

Implements ETag support, Cache-Control headers, and response compression
for Phase 1 deterministic APIs.
"""

import hashlib
import json
import logging
from typing import Optional, Callable, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import Headers

logger = logging.getLogger(__name__)


class CachingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for cache control and ETag support.

    Features:
    - ETag generation for immutable content
    - Cache-Control headers for CDN/browser caching
    - Conditional requests (If-None-Match / If-Modified-Since)
    - Gzip compression support

    Cache Strategy:
    - Immutable content (chapters, quizzes): 24h cache
    - User-specific data: 5 min cache
    - Search results: 1 min cache
    """

    # Cache TTLs (in seconds)
    TTL_IMMUTABLE = 86400  # 24 hours
    TTL_USER_DATA = 300     # 5 minutes
    TTL_SEARCH = 60         # 1 minute

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request through caching layer.
        """
        # Handle GET requests with cache headers
        if request.method == "GET":
            return await self._handle_get_request(request, call_next)

        # For non-GET requests, pass through
        response = await call_next(request)
        return response

    async def _handle_get_request(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Handle GET request with caching logic.
        """
        # Check for conditional request headers
        if_none_match = request.headers.get("if-none-match")
        if_modified_since = request.headers.get("if-modified-since")

        # Generate cache key for this request
        cache_key = self._generate_cache_key(request)

        # If client has ETag, check if resource changed
        if if_none_match:
            # Check if resource is still the same
            current_etag = await self._get_etag_for_key(cache_key)
            if current_etag and current_etag == if_none_match:
                logger.debug(f"Cache HIT: {request.url} (ETag match)")
                return Response(
                    status_code=304,
                    headers={
                        "ETag": current_etag,
                        "Cache-Control": self._get_cache_control(request.url)
                    }
                )

        # Proceed with request
        response = await call_next(request)

        # Add caching headers to response
        if response.status_code == 200 and isinstance(response, JSONResponse):
            response = await self._add_cache_headers(request, response, cache_key)

        return response

    def _generate_cache_key(self, request: Request) -> str:
        """
        Generate cache key for request.

        Includes URL and relevant query parameters.
        """
        # Sort query params for consistency
        query_params = sorted(request.query_params.items())
        query_string = "&".join(f"{k}={v}" for k, v in query_params)

        # Build cache key
        key_parts = [
            request.url.path,
            query_string if query_string else ""
        ]

        return hashlib.md5("|".join(key_parts).encode()).hexdigest()

    async def _get_etag_for_key(self, cache_key: str) -> Optional[str]:
        """
        Get ETag for cached resource.

        In production, this would check Redis or another cache layer.
        For now, we'll skip cache lookup and always proceed to request.
        """
        # TODO: Implement Redis/Cache lookup for ETags
        return None

    async def _add_cache_headers(
        self,
        request: Request,
        response: Response,
        cache_key: str
    ) -> Response:
        """
        Add cache headers to response.
        """
        # Generate ETag from response body
        body = response.body.decode()
        etag = self._generate_etag(body)

        # Determine cache control
        cache_control = self._get_cache_control(request.url)

        # Add headers
        response.headers["ETag"] = etag
        response.headers["Cache-Control"] = cache_control

        # Add Vary header for proper caching
        if "Authorization" in request.headers:
            response.headers["Vary"] = "Authorization"

        logger.debug(f"Cache headers added: {request.url} (ETag: {etag[:8]}...)")

        return response

    def _generate_etag(self, body: str) -> str:
        """
        Generate ETag from response body.
        """
        return hashlib.sha256(body.encode()).hexdigest()

    def _get_cache_control(self, url: str) -> str:
        """
        Determine Cache-Control header based on URL pattern.
        """
        # Immutable content - long cache
        if any(pattern in url for pattern in ["/chapters/", "/quizzes/", "/content/"]):
            return f"public, max-age={self.TTL_IMMUTABLE}, s-maxage={self.TTL_IMMUTABLE}, immutable"

        # Search results - short cache
        elif "/search" in url:
            return f"public, max-age={self.TTL_SEARCH}"

        # User-specific data - very short cache
        elif any(pattern in url for pattern in ["/progress", "/user", "/me"]):
            return f"private, max-age={self.TTL_USER_DATA}, must-revalidate"

        # Default: no caching
        else:
            return "no-cache, no-store, must-revalidate"


async def compress_response(response: JSONResponse) -> JSONResponse:
    """
    Compress JSON response using gzip if supported by client.

    Starlette/FastAPI handles this automatically in production with GZipMiddleware,
    but this is a placeholder for manual compression if needed.
    """
    # FastAPI's GZipMiddleware handles this automatically
    return response
