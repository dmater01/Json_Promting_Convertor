# Operations Runbooks - Structured Prompt Service

This directory contains runbooks for responding to common operational alerts and issues.

## Quick Reference

| Alert | Severity | Runbook | MTTR Target |
|-------|----------|---------|-------------|
| APIDown | 🔴 Critical | [APIDown](./APIDown.md) | 5 minutes |
| DatabaseDown | 🔴 Critical | [DatabaseDown](./DatabaseDown.md) | 5 minutes |
| RedisDown | 🔴 Critical | [RedisDown](./RedisDown.md) | 10 minutes |
| APIHighErrorRate | 🔴 Critical | [HighErrorRate](./HighErrorRate.md) | 10 minutes |
| HighLatencyP95 | 🔴 Critical | [HighLatency](./HighLatency.md) | 15 minutes |
| HighAuthFailures | 🟡 Warning | [HighAuthFailures](./HighAuthFailures.md) | 30 minutes |
| LowCacheHitRate | 🟡 Warning | [LowCacheHitRate](./LowCacheHitRate.md) | 1 hour |
| HighRateLimitViolations | 🟡 Warning | [HighRateLimitViolations](./HighRateLimitViolations.md) | 1 hour |
| LLMProviderSlowdown | 🔵 Info | [LLMProviderSlowdown](./LLMProviderSlowdown.md) | 2 hours |

## Runbook Structure

Each runbook follows this template:

1. **Overview** - What the alert means
2. **Impact** - User/business impact
3. **Diagnosis** - How to investigate
4. **Resolution** - Step-by-step fix
5. **Prevention** - How to avoid in future
6. **Escalation** - When/who to escalate to

## General Debugging Commands

### Check Service Health

```bash
# Check all services
docker-compose ps

# Check API health
curl http://localhost:8000/v1/health

# Check specific service logs
docker logs api-server --tail 100 --follow
docker logs postgres --tail 100
docker logs redis --tail 100
```

### Access Monitoring Tools

- **Grafana:** http://localhost:3000 (admin/admin)
- **Prometheus:** http://localhost:9090
- **Prometheus Alerts:** http://localhost:9090/alerts
- **Alertmanager:** http://localhost:9093

### Database Access

```bash
# Connect to PostgreSQL
docker exec -it postgres psql -U structured_prompt -d structured_prompt_db

# Check connections
SELECT count(*) FROM pg_stat_activity;

# Check long-running queries
SELECT pid, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC;
```

### Redis Access

```bash
# Connect to Redis
docker exec -it redis redis-cli

# Check memory usage
INFO memory

# Check key count
DBSIZE

# Check cache keys
KEYS cache:*

# Check rate limit keys
KEYS rate_limit:*
```

### Log Analysis

```bash
# Filter for errors
docker logs api-server 2>&1 | grep ERROR

# Filter for specific request ID
docker logs api-server 2>&1 | grep "request_id: abc-123"

# Count errors by type
docker logs api-server 2>&1 | grep ERROR | cut -d' ' -f5 | sort | uniq -c | sort -nr
```

## Escalation Path

### Level 1: On-Call Engineer
- **Contact:** Primary on-call rotation
- **Responsibility:** Initial response, diagnosis, basic fixes
- **Escalate after:** 30 minutes without resolution

### Level 2: Senior Engineer
- **Contact:** Secondary on-call
- **Responsibility:** Complex issues, infrastructure changes
- **Escalate after:** 1 hour without resolution

### Level 3: Engineering Lead
- **Contact:** Engineering manager
- **Responsibility:** Critical outages, architectural decisions
- **Escalate after:** Major incident declared

### Emergency Contacts

```
On-Call Hotline:  +1-XXX-XXX-XXXX
Slack Channel:    #incidents
Email:            oncall@yourcompany.com
PagerDuty:        https://yourcompany.pagerduty.com
```

## Incident Response Process

### 1. Acknowledge Alert
- Acknowledge in PagerDuty/Alertmanager
- Post in #incidents Slack channel
- Note start time

### 2. Assess Impact
- Check Grafana dashboards
- Verify user reports
- Determine severity level

### 3. Investigate
- Follow relevant runbook
- Gather diagnostic data
- Document findings

### 4. Resolve
- Apply fix from runbook
- Verify resolution in Grafana
- Monitor for 15 minutes

### 5. Document
- Update incident ticket
- Add timeline of events
- Note root cause
- Create follow-up tasks

### 6. Post-Mortem
- Schedule within 48 hours
- Document root cause
- Create prevention tasks
- Share learnings

## Common Fixes

### Restart API Service

```bash
docker-compose restart api
# Wait 30 seconds
curl http://localhost:8000/v1/health
```

### Restart All Services

```bash
docker-compose down
docker-compose up -d
# Wait 60 seconds
./scripts/health_check.sh
```

### Clear Redis Cache

```bash
docker exec -it redis redis-cli FLUSHDB
# Verify
docker exec -it redis redis-cli DBSIZE
```

### Database Connection Reset

```bash
# Restart PostgreSQL
docker-compose restart postgres
# Wait 30 seconds
# Restart API to reconnect
docker-compose restart api
```

### View Recent Metrics

```bash
# Request rate (last 5 minutes)
curl -s 'http://localhost:9090/api/v1/query?query=sum(rate(http_requests_total[5m]))' | jq '.data.result'

# Error rate (last 5 minutes)
curl -s 'http://localhost:9090/api/v1/query?query=sum(rate(http_requests_total{status=~"5.."}[5m]))' | jq '.data.result'

# P95 latency
curl -s 'http://localhost:9090/api/v1/query?query=histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))' | jq '.data.result'
```

## Maintenance Windows

### Scheduled Maintenance Process

1. **Announce** (24h before):
   - Post in #announcements
   - Email customers
   - Update status page

2. **Pre-Maintenance**:
   - Backup database
   - Verify rollback plan
   - Prepare monitoring

3. **During Maintenance**:
   - Follow maintenance runbook
   - Update status page every 15 min
   - Monitor #incidents channel

4. **Post-Maintenance**:
   - Verify all services healthy
   - Run smoke tests
   - Close status page incident
   - Send completion email

### Maintenance Runbooks

- [Database Migration](./maintenance/DatabaseMigration.md)
- [Zero-Downtime Deployment](./maintenance/ZeroDowntimeDeployment.md)
- [Scaling Up](./maintenance/ScalingUp.md)
- [Backup and Restore](./maintenance/BackupRestore.md)

## Performance Tuning

### Quick Wins

1. **Increase Cache TTL**:
   ```python
   # In .env
   CACHE_DEFAULT_TTL=7200  # 2 hours instead of 1
   ```

2. **Increase Rate Limits** (for VIP users):
   ```sql
   UPDATE api_keys
   SET rate_limit_per_hour = 10000
   WHERE name = 'vip-customer';
   ```

3. **Add Database Indexes**:
   ```bash
   docker exec -it postgres psql -U structured_prompt -d structured_prompt_db
   CREATE INDEX CONCURRENTLY idx_requests_api_key ON request_logs(api_key_id);
   ```

## Testing After Incident

```bash
# Run health checks
curl http://localhost:8000/v1/health

# Test analyze endpoint
curl -X POST http://localhost:8000/v1/analyze/ \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: YOUR_API_KEY' \
  -d '{"prompt": "Test after incident"}'

# Run load test (light)
locust -f load_tests/baseline_test.py \
  --host http://localhost:8000 \
  --headless \
  --users 5 \
  --spawn-rate 1 \
  --run-time 60s
```

## Additional Resources

- [Architecture Documentation](../ARCHITECTURE.md)
- [API Documentation](../API.md)
- [Performance Test Results](../PERFORMANCE_TEST_RESULTS.md)
- [Deployment Guide](../DEPLOYMENT.md)
- [Monitoring Guide](./MONITORING_GUIDE.md)
