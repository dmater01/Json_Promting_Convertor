# Load Testing Guide - Structured Prompt Service

This directory contains load testing scenarios for the Structured Prompt Service API using [Locust](https://locust.io/).

## Quick Start

### 1. Install Dependencies

```bash
pip install locust
# or
pip install -r requirements.txt
```

### 2. Run Baseline Test (Recommended)

```bash
locust -f load_tests/baseline_test.py \
  --host http://localhost:8000 \
  --headless \
  --users 10 \
  --spawn-rate 2 \
  --run-time 120s
```

### 3. View Results in Grafana

Open http://localhost:3000 and navigate to "API Overview - Structured Prompt Service" dashboard.

---

## Test Files

### `baseline_test.py` (Recommended)

Focused load test for main API functionality:

- **User Class:** `PromptAnalysisUser`
- **API Key:** High rate limit (1000 req/hour)
- **Tasks:**
  - `analyze_prompt` (weight: 10) - Random prompt analysis
  - `analyze_cached_prompt` (weight: 2) - Cache hit testing
  - `check_providers` (weight: 1) - Provider list endpoint
  - `check_cache_stats` (weight: 1) - Cache statistics endpoint

**When to use:** General performance testing, regression testing, production simulation

### `locustfile.py` (Comprehensive)

Full test suite including edge cases:

- **User Classes:**
  - `PromptAnalysisUser` - Main API functionality
  - `RateLimitTestUser` - Rate limiting stress test (low limit key)
  - `UnauthenticatedUser` - Authentication failure testing

**When to use:** Pre-deployment validation, security testing, edge case verification

---

## Running Tests

### Interactive Mode (Web UI)

```bash
# Start Locust web interface
locust -f load_tests/baseline_test.py --host http://localhost:8000

# Open browser to http://localhost:8089
# Configure users and spawn rate in UI
# Start test and monitor real-time
```

**Use cases:**
- Manual exploration
- Custom test scenarios
- Real-time monitoring
- Visual result analysis

### Headless Mode (CI/CD)

```bash
# Run specific configuration without UI
locust -f load_tests/baseline_test.py \
  --host http://localhost:8000 \
  --headless \
  --users 50 \
  --spawn-rate 5 \
  --run-time 300s \
  --csv results/test_$(date +%Y%m%d_%H%M%S)
```

**Use cases:**
- Automated testing
- CI/CD pipelines
- Scheduled benchmarks
- Regression detection

### Summary Mode (Quick Check)

```bash
# Show only summary statistics
locust -f load_tests/baseline_test.py \
  --host http://localhost:8000 \
  --headless \
  --users 10 \
  --spawn-rate 2 \
  --run-time 60s \
  --only-summary
```

**Use cases:**
- Quick validation
- Smoke tests
- Pre-deployment checks

---

## Test Scenarios

### Scenario 1: Baseline Performance (10 users)

**Purpose:** Establish performance baseline

```bash
locust -f load_tests/baseline_test.py \
  --host http://localhost:8000 \
  --headless \
  --users 10 \
  --spawn-rate 2 \
  --run-time 120s
```

**Expected Results:**
- 0% failure rate
- ~2-3 req/s throughput
- P50 latency < 10ms
- Cache hits observed

### Scenario 2: Stress Test (50 users)

**Purpose:** Test system under load

```bash
locust -f load_tests/baseline_test.py \
  --host http://localhost:8000 \
  --headless \
  --users 50 \
  --spawn-rate 5 \
  --run-time 120s
```

**Expected Results:**
- 0% failure rate (excluding rate limits)
- ~10-15 req/s throughput
- P50 latency < 10ms
- Rate limit violations observed

### Scenario 3: Spike Test (0 → 100 → 0)

**Purpose:** Test auto-scaling and recovery

```bash
# Spike to 100 users in 10 seconds
locust -f load_tests/baseline_test.py \
  --host http://localhost:8000 \
  --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 60s
```

**Monitor:**
- System recovery time
- Error rates during spike
- Cache effectiveness

### Scenario 4: Endurance Test (Long Duration)

**Purpose:** Detect memory leaks and resource exhaustion

```bash
# Run 30 users for 1 hour
locust -f load_tests/baseline_test.py \
  --host http://localhost:8000 \
  --headless \
  --users 30 \
  --spawn-rate 3 \
  --run-time 3600s
```

**Monitor:**
- Memory usage trends
- Database connection pool
- Redis memory usage
- Response time degradation

---

## Configuration

### Test API Keys

Update keys in test files before running:

**`baseline_test.py`:**
```python
API_KEY = "sp_e7f0e18bb662f3bee755f3bd6b7ee0f2f3326a6373025b4954808938da0deb2f"
```

**`locustfile.py`:**
```python
# High limit key (1000 req/hour)
API_KEY = "sp_e7f0..."

# Low limit key (3 req/hour) - for rate limit testing
RATE_LIMIT_KEY = "sp_e51..."
```

### Sample Prompts

Both test files include 10 sample prompts for variety:

```python
PROMPTS = [
    "Translate 'Hello World' to French",
    "Analyze the sentiment of: I love this product!",
    "Extract entities from: John Smith works at Acme Corp in New York",
    # ... 7 more prompts
]
```

**Customize:** Edit prompt list to match your use case.

---

## Monitoring

### Real-Time Monitoring

**Locust Web UI:**
- URL: http://localhost:8089 (when running in interactive mode)
- Metrics: RPS, response times, failure rates
- Charts: Real-time graphs

**Grafana Dashboard:**
- URL: http://localhost:3000
- Dashboard: "API Overview - Structured Prompt Service"
- Panels:
  - Requests per second
  - P95 latency
  - Success rate
  - Rate limit violations
  - Status code distribution

**Prometheus:**
- URL: http://localhost:9090
- Query metrics directly
- Set up custom alerts

### Key Metrics to Watch

| Metric | Baseline | Warning | Critical |
|--------|----------|---------|----------|
| **P50 Latency** | < 10ms | > 50ms | > 100ms |
| **P95 Latency** | < 5s | > 30s | > 60s |
| **Failure Rate** | 0% | > 1% | > 5% |
| **RPS** | 2-3 | - | - |
| **Cache Hit Rate** | 10-20% | < 5% | < 1% |

---

## Interpreting Results

### Success Criteria

✅ **Pass:**
- 0% failure rate (excluding expected 429s)
- P50 latency < 10ms for cached requests
- P95 latency < 10s for non-cached requests
- System remains stable throughout test

⚠️ **Warning:**
- 1-5% failure rate
- P95 latency 10-30s
- Increasing latency trends
- High rate limit violations

❌ **Fail:**
- >5% failure rate
- P95 latency >60s
- System crashes or hangs
- Database connection errors

### Common Patterns

**Cache Working Well:**
```
Cache hit! Latency: 0ms
Cache hit! Latency: 1ms
Cache hit! Latency: 0ms
```

**Rate Limiting Active:**
```
Rate limit hit (expected)
Rate limit hit (expected)
```

**Healthy Request Distribution:**
```
Type     Name                    # reqs  # fails  |  Avg    P50    P95
POST     /v1/analyze/              500      0     |  1500     8     4000
GET      /v1/health                 50      0     |  3600  4000    6000
```

---

## Troubleshooting

### Issue: All Requests Failing

**Check:**
1. API server is running: `curl http://localhost:8000/v1/health`
2. API key is valid
3. Database is accessible
4. Redis is running

### Issue: High Latency

**Possible Causes:**
1. LLM provider slowness (expected at P99)
2. Database connection pool exhaustion
3. Cache misses (check Redis)
4. CPU/Memory saturation

**Debug:**
```bash
# Check API logs
docker logs api-server

# Check resource usage
docker stats

# Check Redis
redis-cli info stats
```

### Issue: Rate Limit Violations

**Expected Behavior:**
- Default: 1000 requests/hour per key
- Stress tests will hit limits

**If Unexpected:**
- Verify API key rate limit setting
- Check if multiple tests running
- Review rate limiter Redis keys

### Issue: Cache Not Working

**Symptoms:**
- No "Cache hit!" messages
- All requests show high latency
- Cache stats show 0 hits

**Check:**
1. Redis is running: `redis-cli ping`
2. Cache TTL is set: Check `cache_ttl` parameter
3. Same prompts being used
4. Cache middleware enabled

---

## Best Practices

### 1. Start Small

Always run baseline test (10 users) before stress testing:

```bash
# Baseline first
locust -f load_tests/baseline_test.py --host http://localhost:8000 --headless --users 10 --run-time 60s

# Then stress test
locust -f load_tests/baseline_test.py --host http://localhost:8000 --headless --users 50 --run-time 120s
```

### 2. Monitor in Real-Time

Keep Grafana dashboard open during tests:

```bash
# Terminal 1: Run test
locust -f load_tests/baseline_test.py --host http://localhost:8000 --headless --users 30 --run-time 300s

# Terminal 2: Watch logs
docker logs -f api-server

# Browser: http://localhost:3000 (Grafana)
```

### 3. Save Results

Export results for comparison:

```bash
# Save to CSV files
locust -f load_tests/baseline_test.py \
  --host http://localhost:8000 \
  --headless \
  --users 50 \
  --run-time 300s \
  --csv results/baseline_$(date +%Y%m%d)

# Results saved to:
# - results/baseline_20251020_stats.csv
# - results/baseline_20251020_failures.csv
# - results/baseline_20251020_stats_history.csv
```

### 4. Test Incrementally

Gradually increase load to find breaking point:

```bash
# 10 users
locust ... --users 10 --run-time 60s

# 25 users
locust ... --users 25 --run-time 60s

# 50 users
locust ... --users 50 --run-time 60s

# 100 users
locust ... --users 100 --run-time 60s
```

### 5. Clean Up Between Tests

Reset cache and database state:

```bash
# Clear Redis cache
redis-cli FLUSHALL

# Reset rate limits
redis-cli KEYS "rate_limit:*" | xargs redis-cli DEL
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Load Test

on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  load-test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Start services
        run: docker-compose up -d

      - name: Install Locust
        run: pip install locust

      - name: Run baseline test
        run: |
          locust -f load_tests/baseline_test.py \
            --host http://localhost:8000 \
            --headless \
            --users 10 \
            --spawn-rate 2 \
            --run-time 120s \
            --csv results/baseline

      - name: Check failure rate
        run: |
          # Fail if >1% error rate
          python scripts/check_load_test_results.py results/baseline_stats.csv

      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: load-test-results
          path: results/
```

---

## Further Reading

- **Locust Documentation:** https://docs.locust.io/
- **Performance Test Results:** `docs/PERFORMANCE_TEST_RESULTS.md`
- **Grafana Dashboards:** `monitoring/grafana/provisioning/dashboards/`
- **API Documentation:** `docs/API.md`

---

## Support

For issues or questions:
1. Check `docs/PERFORMANCE_TEST_RESULTS.md` for baseline expectations
2. Review Grafana dashboards for anomalies
3. Check API logs: `docker logs api-server`
4. Verify Redis: `redis-cli info`
