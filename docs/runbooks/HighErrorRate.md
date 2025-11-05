# Runbook: High API Error Rate

**Alert Name:** `APIHighErrorRate`
**Severity:** 🔴 Critical
**MTTR Target:** 10 minutes
**Auto-Page:** Yes

---

## Overview

The API is returning 5xx errors at a rate exceeding 5% of total requests. Users are experiencing failures.

**Alert Condition:**
```promql
(
  sum(rate(http_requests_total{status=~"5.."}[5m]))
  /
  sum(rate(http_requests_total[5m]))
) > 0.05
for: 2m
```

---

## Impact

- **User Impact:** 5-100% of requests failing
- **Business Impact:** Degraded service, user complaints
- **Affected Endpoints:** Variable (check Grafana)
- **SLA Impact:** Potential SLA breach if >5% for >5 minutes

---

## Immediate Actions (First 2 Minutes)

### 1. Acknowledge & Assess

```bash
# Check current error rate in Grafana
# Open: http://localhost:3000
# Look at: "Success Rate" panel

# Check Prometheus for exact rate
curl -s 'http://localhost:9090/api/v1/query?query=sum(rate(http_requests_total{status=~"5.."}[5m]))' | jq '.data.result[0].value[1]'
```

### 2. Identify Error Patterns

```bash
# Check which status codes
docker logs api-server --tail 200 | grep -E "status_code: 5[0-9]{2}" | cut -d':' -f2 | sort | uniq -c

# Common codes:
# 500 - Internal Server Error (application bug)
# 502 - Bad Gateway (upstream service down)
# 503 - Service Unavailable (overloaded)
# 504 - Gateway Timeout (request timeout)
```

---

## Diagnosis

### Step 1: Check Recent Logs

```bash
# Get recent 500 errors with context
docker logs api-server --tail 500 | grep -B5 -A5 "ERROR"

# Look for:
# - Exception stack traces
# - Database errors
# - Redis errors
# - LLM provider errors
# - Timeout errors
```

### Step 2: Check Dependencies

```bash
# Check database
docker exec -it postgres psql -U structured_prompt -d structured_prompt_db -c "SELECT 1;"

# Check Redis
docker exec -it redis redis-cli PING

# Check if either is slow
time docker exec -it postgres psql -U structured_prompt -d structured_prompt_db -c "SELECT 1;"
# Should be <100ms

time docker exec -it redis redis-cli PING
# Should be <10ms
```

### Step 3: Check System Resources

```bash
# API server resources
docker stats api-server --no-stream

# Look for:
# - CPU >90% (overloaded)
# - Memory >90% (near OOM)
# - High I/O wait
```

### Step 4: Check Recent Changes

```bash
# Recent deployments?
git log --oneline -10

# Recent config changes?
ls -lt .env docker-compose.yml

# Recent database migrations?
docker exec -it postgres psql -U structured_prompt -d structured_prompt_db -c "SELECT * FROM alembic_version;"
```

---

## Common Causes & Resolutions

### Cause 1: Database Connection Pool Exhausted

**Symptoms:**
- Logs show: "ConnectionPool limit reached"
- Database queries timing out
- Error pattern: Intermittent 500s

**Diagnosis:**
```bash
# Check active connections
docker exec -it postgres psql -U structured_prompt -d structured_prompt_db -c "
SELECT count(*) as active_connections,
       max_connections
FROM pg_stat_activity, (SELECT setting::int as max_connections FROM pg_settings WHERE name='max_connections') m
GROUP BY max_connections;
"
```

**Resolution:**
```python
# Increase pool size in database.py
# SQLALCHEMY_POOL_SIZE = 20  # Increase from 10
# SQLALCHEMY_MAX_OVERFLOW = 40  # Increase from 20

# Restart API
docker-compose restart api
```

---

### Cause 2: LLM Provider Failures

**Symptoms:**
- Logs show: "LLM provider error" or "Gemini API error"
- Errors on `/v1/analyze/` endpoint specifically
- May show "429" or "503" from Gemini

**Diagnosis:**
```bash
# Check recent LLM errors
docker logs api-server --tail 200 | grep -i "gemini\|llm"

# Test Gemini API directly
curl -X POST https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -d '{"contents":[{"parts":[{"text":"test"}]}]}'
```

**Resolution:**
```bash
# If Gemini is rate limiting:
# - Enable caching more aggressively
# - Implement retry with backoff
# - Add timeout limits

# If Gemini is down:
# - Check Gemini status page
# - Implement fallback provider (Phase 3 feature)
# - Return graceful error to users

# Temporary mitigation - reduce request rate
# Update rate limits in database:
docker exec -it postgres psql -U structured_prompt -d structured_prompt_db -c "
UPDATE api_keys SET rate_limit_per_hour = 100 WHERE rate_limit_per_hour = 1000;
"
```

---

### Cause 3: Database Query Timeouts

**Symptoms:**
- Logs show: "Query timeout" or "statement timeout"
- Slow query logs
- Intermittent 500s

**Diagnosis:**
```bash
# Check for long-running queries
docker exec -it postgres psql -U structured_prompt -d structured_prompt_db -c "
SELECT pid, now() - query_start AS duration, state, query
FROM pg_stat_activity
WHERE state = 'active' AND now() - query_start > interval '1 second'
ORDER BY duration DESC;
"

# Check for table locks
docker exec -it postgres psql -U structured_prompt -d structured_prompt_db -c "
SELECT * FROM pg_locks WHERE NOT granted;
"
```

**Resolution:**
```bash
# Kill long-running query (if identified)
docker exec -it postgres psql -U structured_prompt -d structured_prompt_db -c "
SELECT pg_terminate_backend(<PID>);
"

# Add missing indexes
docker exec -it postgres psql -U structured_prompt -d structured_prompt_db -c "
CREATE INDEX CONCURRENTLY idx_request_logs_created_at ON request_logs(created_at);
CREATE INDEX CONCURRENTLY idx_request_logs_api_key_id ON request_logs(api_key_id);
"

# Restart API to reset connections
docker-compose restart api
```

---

### Cause 4: Redis Connection Issues

**Symptoms:**
- Logs show: "Redis connection error" or "Connection refused"
- Cache operations failing
- All cache misses

**Diagnosis:**
```bash
# Check Redis status
docker exec -it redis redis-cli PING
# Expected: PONG

# Check Redis memory
docker exec -it redis redis-cli INFO memory | grep used_memory_human

# Check Redis connections
docker exec -it redis redis-cli INFO clients
```

**Resolution:**
```bash
# If Redis is down, restart it
docker-compose restart redis

# Wait for Redis to come back
sleep 10

# Restart API to reconnect
docker-compose restart api

# If Redis memory is full:
docker exec -it redis redis-cli FLUSHDB
# Warning: Clears all cached data
```

**See:** [RedisDown Runbook](./RedisDown.md)

---

### Cause 5: Application Bug (New Deployment)

**Symptoms:**
- Errors started after recent deployment
- Specific error pattern in logs
- Consistent reproduction

**Diagnosis:**
```bash
# Check recent commits
git log --oneline -5

# Check error traceback
docker logs api-server --tail 100 | grep -A20 "Traceback"
```

**Resolution:**
```bash
# Rollback to previous version
git log --oneline -5  # Note current commit
git checkout HEAD~1

# Rebuild and restart
docker-compose build api
docker-compose up -d api

# Monitor error rate
# Should drop immediately if this was the cause

# After confirmation, create hotfix branch
git checkout -b hotfix/error-rate-issue
# Fix the bug
# Deploy proper fix
```

---

### Cause 6: Overload / Traffic Spike

**Symptoms:**
- High CPU usage (>80%)
- Increased latency before errors
- All endpoints affected
- Correlates with traffic increase

**Diagnosis:**
```bash
# Check request rate
curl -s 'http://localhost:9090/api/v1/query?query=sum(rate(http_requests_total[5m]))' | jq

# Check CPU
docker stats api-server --no-stream | grep api

# Check connection count
docker exec -it postgres psql -U structured_prompt -d structured_prompt_db -c "
SELECT count(*) FROM pg_stat_activity;
"
```

**Resolution:**
```bash
# Immediate: Restart API to clear stuck processes
docker-compose restart api

# Short-term: Reduce rate limits
docker exec -it postgres psql -U structured_prompt -d structured_prompt_db -c "
UPDATE api_keys SET rate_limit_per_hour = rate_limit_per_hour / 2;
"

# Medium-term: Scale horizontally
# Add more API instances (see deployment guide)
docker-compose up -d --scale api=3
```

---

## Resolution Steps

### 1. Apply Fix
```bash
# Based on diagnosis, apply appropriate fix above
```

### 2. Verify Error Rate Decreased
```bash
# Check Grafana "Success Rate" panel
# Should return to >99%

# Check Prometheus
curl -s 'http://localhost:9090/api/v1/query?query=sum(rate(http_requests_total{status=~"5.."}[5m]))' | jq
# Should be near 0
```

### 3. Monitor for 15 Minutes
```bash
# Watch logs
docker logs api-server --follow | grep ERROR

# Watch metrics in Grafana
# Verify error rate stays low
```

---

## Escalation

### Escalate if:
- Error rate >50% for >5 minutes (critical outage)
- Unknown root cause after 10 minutes investigation
- Requires database schema change
- Requires infrastructure scaling

### Escalate to:
- **Level 2:** Senior Engineer
- **Level 3:** Engineering Lead (if >20% error rate or >30 min duration)

---

## Prevention

### Immediate:
1. Add request timeout limits
   ```python
   # In main.py
   LLM_REQUEST_TIMEOUT = 30  # seconds
   ```

2. Implement circuit breaker for LLM calls
   ```python
   # Add in llm_client.py
   from pybreaker import CircuitBreaker
   ```

3. Add database query timeout
   ```python
   # In database.py
   SQLALCHEMY_STATEMENT_TIMEOUT = 5000  # ms
   ```

### Short-term:
1. Implement retry logic with exponential backoff
2. Add more comprehensive error handling
3. Implement graceful degradation
4. Add canary deployments

### Long-term:
1. Multi-provider LLM support with fallback
2. Async job processing for long requests
3. Auto-scaling based on error rate
4. Better integration testing before deployment

---

## Post-Incident

### Update Incident Log
```markdown
**Incident:** High API Error Rate
**Duration:** [START] - [END]
**Peak Error Rate:** X%
**Root Cause:** [Description]
**Resolution:** [What fixed it]
**Affected Users:** ~X requests failed
```

### Create Follow-up Tasks
- [ ] Fix root cause permanently
- [ ] Add test to prevent regression
- [ ] Update monitoring to catch earlier
- [ ] Review similar code patterns

---

## Related Runbooks
- [APIDown](./APIDown.md)
- [DatabaseDown](./DatabaseDown.md)
- [HighLatency](./HighLatency.md)
- [LLMProviderSlowdown](./LLMProviderSlowdown.md)
