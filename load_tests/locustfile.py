"""
Load testing scenarios for Structured Prompt Service.

Run with:
    locust -f load_tests/locustfile.py --host http://localhost:8000

Then open http://localhost:8089 to start tests.
"""

import json
import random
from locust import HttpUser, task, between, events
from locust.exception import RescheduleTask

# Test API key (create this before running tests)
API_KEY = "sp_e7f0e18bb662f3bee755f3bd6b7ee0f2f3326a6373025b4954808938da0deb2f"

# Sample prompts for testing
PROMPTS = [
    "Translate 'Hello World' to French",
    "Analyze the sentiment of: I love this product!",
    "Extract entities from: John Smith works at Acme Corp in New York",
    "Summarize: The quick brown fox jumps over the lazy dog",
    "Classify: This movie was absolutely terrible",
    "Convert to JSON: Name is Alice, age 30, city Paris",
    "Detect language of: Bonjour le monde",
    "Translate 'Good morning' to Spanish",
    "What is the intent of: Book a flight to London",
    "Parse: Product XYZ costs $99.99",
]


class PromptAnalysisUser(HttpUser):
    """
    Simulates users making requests to the analyze endpoint.

    This user class tests:
    - Authentication with API keys
    - Prompt analysis endpoint
    - Various prompt types
    - Cache behavior (repeated prompts)
    """

    # Wait between 1-3 seconds between requests
    wait_time = between(1, 3)

    def on_start(self):
        """Called when a user starts - verify API is accessible."""
        with self.client.get("/v1/health", catch_response=True) as response:
            if response.status_code != 200:
                print(f"Health check failed: {response.status_code}")
                response.failure("Health check failed")

    @task(10)
    def analyze_prompt(self):
        """
        Main task: Analyze a random prompt.

        Weight: 10 (most common operation)
        """
        prompt = random.choice(PROMPTS)

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        }

        payload = {
            "prompt": prompt,
            "llm_provider": "auto",
            "temperature": 0.1,
            "cache_ttl": 3600
        }

        with self.client.post(
            "/v1/analyze/",
            json=payload,
            headers=headers,
            catch_response=True,
            name="/v1/analyze/"
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "data" in data and "intent" in data["data"]:
                        response.success()
                    else:
                        response.failure("Invalid response structure")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            elif response.status_code == 429:
                # Rate limit hit - this is expected behavior
                response.success()
                print("Rate limit hit (expected)")
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(2)
    def analyze_cached_prompt(self):
        """
        Test cached responses.

        Weight: 2 (less common, tests cache hits)
        Uses the first prompt repeatedly to test caching.
        """
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        }

        payload = {
            "prompt": PROMPTS[0],  # Always use same prompt
            "llm_provider": "gemini",
            "temperature": 0.1,
            "cache_ttl": 3600
        }

        with self.client.post(
            "/v1/analyze/",
            json=payload,
            headers=headers,
            catch_response=True,
            name="/v1/analyze/ (cached)"
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Check if response was cached
                    if data.get("cached"):
                        print(f"Cache hit! Latency: {data.get('latency_ms')}ms")
                    response.success()
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            elif response.status_code == 429:
                response.success()
            else:
                response.failure(f"Status {response.status_code}")

    @task(1)
    def check_providers(self):
        """
        Check available LLM providers.

        Weight: 1 (occasional operation)
        """
        headers = {"X-API-Key": API_KEY}

        with self.client.get(
            "/v1/analyze/providers",
            headers=headers,
            catch_response=True,
            name="/v1/analyze/providers"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status {response.status_code}")

    @task(1)
    def check_cache_stats(self):
        """
        Check cache statistics.

        Weight: 1 (occasional monitoring)
        """
        headers = {"X-API-Key": API_KEY}

        with self.client.get(
            "/v1/analyze/cache/stats",
            headers=headers,
            catch_response=True,
            name="/v1/analyze/cache/stats"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status {response.status_code}")


class RateLimitTestUser(HttpUser):
    """
    Tests rate limiting behavior.

    Uses a separate API key with low rate limits.
    """

    wait_time = between(0.1, 0.5)  # Aggressive requests

    # This should be an API key with rate_limit_per_hour = 10 or similar
    RATE_LIMIT_KEY = "sp_e51bbc5a5904617f3da35f6ab66fafac1247d47a10da73bf1866715517a718e6"

    @task
    def trigger_rate_limit(self):
        """Rapidly make requests to trigger rate limiting."""
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.RATE_LIMIT_KEY
        }

        payload = {
            "prompt": "Quick test",
            "cache_ttl": 0  # Disable cache to ensure we hit rate limits
        }

        with self.client.post(
            "/v1/analyze/",
            json=payload,
            headers=headers,
            catch_response=True,
            name="/v1/analyze/ (rate limit test)"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:
                # Rate limit hit - exactly what we're testing
                response.success()
                try:
                    data = response.json()
                    details = data.get("error", {}).get("details", {})
                    print(f"Rate limited: {details.get('remaining')} remaining")
                except:
                    pass
            else:
                response.failure(f"Unexpected status: {response.status_code}")


class UnauthenticatedUser(HttpUser):
    """
    Tests behavior with invalid/missing authentication.
    """

    wait_time = between(1, 2)

    @task
    def try_without_auth(self):
        """Attempt request without API key."""
        payload = {"prompt": "Test"}

        with self.client.post(
            "/v1/analyze/",
            json=payload,
            catch_response=True,
            name="/v1/analyze/ (no auth)"
        ) as response:
            if response.status_code == 401:
                # Expected behavior
                response.success()
            else:
                response.failure(f"Expected 401, got {response.status_code}")

    @task
    def try_invalid_key(self):
        """Attempt request with invalid API key."""
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": "sp_invalid_key_12345"
        }

        payload = {"prompt": "Test"}

        with self.client.post(
            "/v1/analyze/",
            json=payload,
            headers=headers,
            catch_response=True,
            name="/v1/analyze/ (invalid key)"
        ) as response:
            if response.status_code == 401:
                response.success()
            else:
                response.failure(f"Expected 401, got {response.status_code}")


# Event hooks for reporting
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when the test starts."""
    print("\n" + "="*60)
    print("🚀 Starting Load Tests for Structured Prompt Service")
    print("="*60)
    print(f"Host: {environment.host}")
    print(f"Users: {environment.runner.user_count if hasattr(environment.runner, 'user_count') else 'N/A'}")
    print("="*60 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when the test stops."""
    print("\n" + "="*60)
    print("✅ Load Tests Completed")
    print("="*60)
    print("\nView results at: http://localhost:8089")
    print("View Grafana dashboards at: http://localhost:3000")
    print("="*60 + "\n")
