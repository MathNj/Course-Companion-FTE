#!/usr/bin/env python3
"""
Performance Benchmarking Script

Tests API endpoints to measure actual performance and compare against targets.
"""

import asyncio
import time
import statistics
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from httpx import AsyncClient
import tabulate


class PerformanceBenchmark:
    """Benchmark API performance against targets."""

    # API base URL
    BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

    # Performance targets (in milliseconds)
    TARGETS = {
        "GET /chapters/{id}": {"p50": 150, "p95": 600},
        "GET /search": {"p50": 250, "p95": 600},
        "POST /quizzes/{id}/submit": {"p50": 200, "p95": 600},
        "PUT /progress/{user_id}": {"p50": 200, "p95": 600},
    }

    def __init__(self):
        self.client = None

    async def __aenter__(self):
        self.client = AsyncClient(base_url=self.BASE_URL)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.aclose()

    async def aclose(self):
        if self.client:
            await self.client.aclose()

    async def benchmark_endpoint(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> dict:
        """
        Benchmark a single endpoint with multiple requests.

        Returns:
            Dictionary with p50, p95, p99 latencies and request count
        """
        num_requests = kwargs.pop("num_requests", 50)

        print(f"\n{'='*60}")
        print(f"Benchmarking: {method} {url}")
        print(f"Requests: {num_requests}")
        print(f"{'='*60}\n")

        latencies = []
        errors = 0
        cache_hits = 0
        cache_misses = 0

        for i in range(num_requests):
            try:
                start = time.time()

                if method == "GET":
                    response = await self.client.get(url, **kwargs)
                elif method == "POST":
                    response = await self.client.post(url, **kwargs)
                elif method == "PUT":
                    response = await self.client.put(url, **kwargs)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                latency = (time.time() - start) * 1000  # Convert to ms

                if response.status_code == 200:
                    latencies.append(latency)

                    # Check cache headers
                    cache_status = response.headers.get("X-Cache", "MISS")
                    if cache_status == "HIT":
                        cache_hits += 1
                    else:
                        cache_misses += 1

                    # Check response time header if present
                    response_time_header = response.headers.get("X-Response-Time")
                    if response_time_header:
                        header_time = float(response_time_header.rstrip("ms"))
                        latency_diff = abs(latency - header_time)
                        if latency_diff > 50:  # Allow 50ms variance
                            print(f"  ⚠️ Header latency differs by {latency_diff:.0f}ms from measured")

                elif response.status_code == 304:
                    # Not Modified - cache hit
                    latencies.append((time.time() - start) * 1000)
                    cache_hits += 1
                else:
                    errors += 1
                    print(f"  ❌ Request {i+1}: HTTP {response.status_code}")

            except Exception as e:
                errors += 1
                print(f"  ❌ Request {i+1}: Exception: {e}")

        if not latencies:
            print("  ❌ All requests failed!")
            return {"error": "All requests failed"}

        # Calculate statistics
        latencies.sort()
        count = len(latencies)

        p50 = statistics.median(latencies)
        p95 = latencies[int(count * 0.95)] if count >= 20 else latencies[-1]
        p99 = latencies[int(count * 0.99)] if count >= 100 else latencies[-1]
        avg = statistics.mean(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)

        # Get target for this endpoint
        endpoint_key = f"{method} {url}"
        target = self._find_target(endpoint_key)

        # Calculate cache hit rate
        total_cache_operations = cache_hits + cache_misses
        cache_hit_rate = (cache_hits / total_cache_operations * 100) if total_cache_operations > 0 else 0

        # Display results
        print(f"\nResults:")
        print(f"  Requests: {count}")
        print(f"  Errors: {errors}")
        print(f"  Cache hits: {cache_hits}")
        print(f"  Cache misses: {cache_misses}")
        print(f"  Cache hit rate: {cache_hit_rate:.1f}%")
        print(f"\nLatency (ms):")
        print(f"  Min:    {min_latency:.0f}ms")
        print(f"  p50:    {p50:.0f}ms {'✓' if p50 <= target.get('p50', 999) else '❌'} (target: ≤{target.get('p50')}ms)")
        print(f"  p95:    {p95:.0f}ms {'✓' if p95 <= target.get('p95', 999) else '❌'} (target: ≤{target.get('p95')}ms)")
        print(f"  p99:    {p99:.0f}ms")
        print(f"  Average: {avg:.0f}ms")
        print(f"  Max:    {max_latency:.0f}ms")

        # Evaluate against targets
        p50_pass = p50 <= target.get('p50', 999)
        p95_pass = p95 <= target.get('p95', 999)

        if p50_pass and p95_pass:
            print(f"\n✅ PASSED: All latency targets met!")
        elif p50_pass and not p95_pass:
            print(f"\n⚠️  WARNING: p50 target met, but p95 exceeds target")
        else:
            print(f"\n❌ FAILED: p50 target not met!")

        return {
            "endpoint": endpoint_key,
            "num_requests": count,
            "errors": errors,
            "p50_ms": p50,
            "p95_ms": p95,
            "p99_ms": p99,
            "avg_ms": avg,
            "cache_hit_rate": cache_hit_rate,
            "target_p50": target.get("p50"),
            "target_p95": target.get("p95"),
            "p50_pass": p50_pass,
            "p95_pass": p95_pass,
        }

    def _find_target(self, endpoint: str) -> dict:
        """Find performance target for endpoint."""
        # Try exact match first
        if endpoint in self.TARGETS:
            return self.TARGETS[endpoint]

        # Try pattern matching
        for pattern, target in self.TARGETS.items():
            if pattern in endpoint or endpoint in pattern:
                return target

        # Default targets
        return {"p50": 600, "p95": 1000}

    async def run_all_benchmarks(self):
        """Run benchmarks for all key endpoints."""
        print(f"\n{'='*80}")
        print("Performance Benchmark Suite")
        print(f"API: {self.BASE_URL}")
        print(f"{'='*80}\n")

        results = []

        # Test endpoints
        endpoints_to_test = [
            ("GET", "/api/v1/chapters/chapter-1", {}, {}),
            ("GET", "/api/v1/chapters/chapter-2", {}, {}),
            ("GET", "/api/v1/search?q=transformer", {}, {}),
            ("GET", "/api/v1/search?q=llm", {}, {}),
            ("GET", "/api/v1/quizzes/quiz-1", {}, {}),
        ]

        for method, url, params, body in endpoints_to_test:
            try:
                if method == "GET":
                    result = await self.benchmark_endpoint(method, url, params=params)
                elif method == "POST":
                    result = await self.benchmark_endpoint(method, url, json=body)

                results.append(result)

            except Exception as e:
                print(f"\n❌ Error benchmarking {method} {url}: {e}")
                results.append({"error": str(e)})

        # Summary table
        self._print_summary_table(results)

    def _print_summary_table(self, results: list):
        """Print summary table of all benchmarks."""
        print(f"\n{'='*100}")
        print("SUMMARY")
        print(f"{'='*100}\n")

        headers = ["Endpoint", "Requests", "p50 (ms)", "p95 (ms)", "Target p50", "Target p95", "Status", "Cache Hit Rate"]

        rows = []
        for result in results:
            if "error" in result:
                rows.append([
                    result.get("endpoint", "Unknown"),
                    "-",
                    "-",
                    "-",
                    "-",
                    "-",
                    f"❌ Error",
                    "-"
                ])
            else:
                # Format endpoint name (truncate if too long)
                endpoint = result.get("endpoint", "")
                if len(endpoint) > 40:
                    endpoint = endpoint[:37] + "..."

                status = "✅ Pass" if result.get("p50_pass") and result.get("p95_pass") else "⚠️ Warning"

                rows.append([
                    endpoint,
                    result.get("num_requests", "-"),
                    f"{result.get('p50_ms', 0):.0f}",
                    f"{result.get('p95_ms', 0):.0f}",
                    f"{result.get('target_p50', '-'):>6}",
                    f"{result.get('target_p95', '-'):>6}",
                    status,
                    f"{result.get('cache_hit_rate', 0):.1f}%"
                ])

        # Print table
        print(tabulate.tabulate(rows, headers=headers, tablefmt="grid"))

        # Overall assessment
        passed = sum(1 for r in results if r.get("p50_pass") and r.get("p95_pass"))
        total = len([r for r in results if "error" not in r])

        print(f"\nOverall: {passed}/{total} endpoints passed")

        if passed == total:
            print("\n✅ ALL TESTS PASSED! Performance is excellent.")
        elif passed > 0:
            print(f"\n⚠️  {passed}/{total} endpoints passed. Some optimizations needed.")
        else:
            print(f"\n❌ NO TESTS PASSED. Performance optimization needed.")


async def main():
    """Run performance benchmarks."""
    print("Performance Benchmarking Tool")
    print("=" * 40)

    # Check if backend is running
    try:
        async with PerformanceBenchmark() as benchmark:
            await benchmark.run_all_benchmarks()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure the backend is running:")
        print("  cd backend")
        print("  uvicorn app.main:app --reload")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
