"""
Performance Monitoring Middleware

Tracks latency, cache hit rates, and performance metrics for all API requests.
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track and log performance metrics.

    Tracks:
    - Request latency (p50, p95, p99)
    - Cache hit/miss rates
    - Error rates
    - Slow queries (>600ms)
    """

    def __init__(self, app, slow_query_threshold: float = 0.6):
        """
        Initialize performance monitoring.

        Args:
            app: FastAPI application
            slow_query_threshold: Threshold in seconds for slow queries (default: 600ms)
        """
        super().__init__(app)
        self.slow_query_threshold = slow_query_threshold

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and track performance metrics.
        """
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate latency
        latency = time.time() - start_time

        # Add performance headers
        response.headers["X-Response-Time"] = f"{latency*1000:.0f}ms"
        response.headers["X-Request-ID"] = self._generate_request_id()

        # Log performance
        self._log_performance(request, response, latency)

        return response

    def _generate_request_id(self) -> str:
        """Generate unique request ID for tracing."""
        import uuid
        return str(uuid.uuid4())[:8]

    def _log_performance(self, request: Request, response: Response, latency: float):
        """
        Log performance metrics.

        Args:
            request: FastAPI request
            response: FastAPI response
            latency: Request latency in seconds
        """
        # Check for slow queries
        if latency > self.slow_query_threshold:
            logger.warning(
                f"SLOW QUERY: {request.method} {request.url.path} "
                f"took {latency*1000:.0f}ms (threshold: {self.slow_query_threshold*1000:.0f}ms)"
            )

        # Check cache status
        cache_status = response.headers.get("X-Cache", "N/A")
        if cache_status == "HIT":
            logger.debug(f"CACHE HIT: {request.url.path} ({latency*1000:.0f}ms)")
        elif cache_status == "MISS":
            logger.debug(f"CACHE MISS: {request.url.path} ({latency*1000:.0f}ms)")

        # Log errors
        if response.status_code >= 400:
            logger.error(
                f"ERROR: {request.method} {request.url.path} "
                f"status={response.status_code} ({latency*1000:.0f}ms)"
            )
        else:
            logger.info(
                f"REQUEST: {request.method} {request.url.path} "
                f"status={response.status_code} ({latency*1000:.0f}ms)"
            )


# Performance metrics storage (for dashboard)
class PerformanceMetrics:
    """Store and aggregate performance metrics."""

    def __init__(self):
        self.request_times = []
        self.cache_hits = 0
        self.cache_misses = 0
        self.error_count = 0

    def record_request(self, latency: float, cache_hit: bool = False, is_error: bool = False):
        """
        Record a request metric.

        Args:
            latency: Request latency in seconds
            cache_hit: Whether this was a cache hit
            is_error: Whether this request resulted in an error
        """
        self.request_times.append(latency)

        if cache_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1

        if is_error:
            self.error_count += 1

        # Keep only last 1000 requests in memory
        if len(self.request_times) > 1000:
            self.request_times = self.request_times[-1000:]

    def get_statistics(self) -> dict:
        """
        Get aggregated performance statistics.

        Returns:
            Dictionary with p50, p95, p99 latencies, cache hit rate, error rate
        """
        if not self.request_times:
            return {
                "request_count": 0,
                "p50_latency_ms": 0,
                "p95_latency_ms": 0,
                "p99_latency_ms": 0,
                "cache_hit_rate": 0.0,
                "error_rate": 0.0
            }

        import numpy as np

        sorted_times = sorted(self.request_times)
        total_requests = len(self.request_times)

        return {
            "request_count": total_requests,
            "p50_latency_ms": np.percentile(sorted_times, 50) * 1000,
            "p95_latency_ms": np.percentile(sorted_times, 95) * 1000,
            "p99_latency_ms": np.percentile(sorted_times, 99) * 1000,
            "cache_hit_rate": self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0.0,
            "error_rate": self.error_count / total_requests if total_requests > 0 else 0.0
        }


# Global metrics instance
performance_metrics = PerformanceMetrics()
