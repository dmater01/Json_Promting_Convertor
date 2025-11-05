# Monitoring and Alerting Guide

**Service:** Structured Prompt Service
**Version:** 0.1.0 MVP
**Last Updated:** October 20, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Monitoring Stack](#monitoring-stack)
3. [Accessing Dashboards](#accessing-dashboards)
4. [Key Metrics](#key-metrics)
5. [Alert Configuration](#alert-configuration)
6. [Runbooks](#runbooks)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Overview

The Structured Prompt Service uses a comprehensive monitoring stack to ensure high availability, performance, and reliability.

**Monitoring Architecture:**
```
┌─────────────┐
│   FastAPI   │──> Prometheus Client (metrics)
│     API     │──> JSON Logging (logs)
└─────────────┘
       │
       v
┌─────────────┐      ┌─────────────┐
│ Prometheus  │─────>│   Grafana   │──> Dashboards
│   (Metrics) │      │ (Visualize) │
└─────────────┘      └─────────────┘
       │
       v
┌─────────────┐      ┌─────────────┐
│ Alertmanager│─────>│  PagerDuty  │──> Pages/Emails
│   (Alerts)  │      │    Slack    │
└─────────────┘      └─────────────┘
```

---

## Monitoring Stack

### Components

| Component | Purpose | Port | URL |
|-----------|---------|------|-----|
| **Prometheus** | Metrics collection and storage | 9090 | http://localhost:9090 |
| **Grafana** | Metrics visualization | 3000 | http://localhost:3000 |
| **Alertmanager** | Alert routing and notifications | 9093 | http://localhost:9093 |
| **API /metrics** | Metrics exposition | 8000 | http://localhost:8000/v1/metrics |
| **API /health** | Health checks | 8000 | http://localhost:8000/v1/health |

### Data Flow

1. **Metrics Collection:**
   - FastAPI exports metrics via `/v1/metrics` endpoint
   - Prometheus scrapes metrics every 15 seconds
   - Metrics stored in time-series database

2. **Alerting:**
   - Prometheus evaluates alert rules every 15 seconds
   - Firing alerts sent to Alertmanager
   - Alertmanager routes to appropriate receivers (email, Slack, PagerDuty)

3. **Visualization:**
   - Grafana queries Prometheus for metrics
   - Dashboards auto-refresh every 10 seconds
   - Historical data available for analysis

---

## Accessing Dashboards

### Grafana

**URL:** http://localhost:3000
**Default Credentials:**
- Username: `admin`
- Password: `admin` (change on first login)

**Available Dashboards:**
1. **API Overview** - Main operational dashboard
   - Request rate, latency, success rate
   - Rate limit violations
   - Status code distribution

2. **System Metrics** (coming soon)
   - CPU, memory, disk usage
   - Database connections
   - Redis memory

### Prometheus

**URL:** http://localhost:9090

**Useful Pages:**
- **Graph:** http://localhost:9090/graph - Query and visualize metrics
- **Alerts:** http://localhost:9090/alerts - View active/pending alerts
- **Targets:** http://localhost:9090/targets - Check scrape health
- **Rules:** http://localhost:9090/rules - View alert and recording rules

### Alertmanager

**URL:** http://localhost:9093

**Features:**
- View active alerts
- Silence alerts temporarily
- View alert history
- Test notification routing

---

## Key Metrics

### API Performance Metrics

| Metric | Type | Description | PromQL Query |
|--------|------|-------------|--------------|
| **Request Rate** | Counter | Requests per second | `sum(rate(http_requests_total[5m]))` |
| **Error Rate** | Counter | 5xx errors as % of total | `sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))` |
| **P50 Latency** | Histogram | 50th percentile latency | `histogram_quantile(0.50, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))` |
| **P95 Latency** | Histogram | 95th percentile latency | `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))` |
| **P99 Latency** | Histogram | 99th percentile latency | `histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))` |

### Cache Metrics

| Metric | Type | Description | PromQL Query |
|--------|------|-------------|--------------|
| **Cache Hit Rate** | Counter | % of cache hits | `sum(rate(cache_hits_total[5m])) / (sum(rate(cache_hits_total[5m])) + sum(rate(cache_misses_total[5m])))` |
| **Cache Entries** | Gauge | Number of cached items | `cache_entries_total` |

### Rate Limiting Metrics

| Metric | Type | Description | PromQL Query |
|--------|------|-------------|--------------|
| **Rate Limit Violations** | Counter | 429 responses per second | `sum(rate(http_requests_total{status="429"}[5m]))` |

### System Metrics

| Metric | Type | Description | PromQL Query |
|--------|------|-------------|--------------|
| **CPU Usage** | Gauge | % CPU utilization | `100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)` |
| **Memory Usage** | Gauge | % memory used | `(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100` |
| **Disk Usage** | Gauge | % disk used | `(node_filesystem_size_bytes - node_filesystem_avail_bytes) / node_filesystem_size_bytes * 100` |

---

## Alert Configuration

### Alert Severity Levels

| Severity | Response Time | Examples | Action |
|----------|---------------|----------|--------|
| 🔴 **Critical** | Immediate (5-15 min) | APIDown, DatabaseDown, HighErrorRate | Page on-call engineer |
| 🟡 **Warning** | Within 1 hour | HighLatency, LowCacheHitRate | Email ops team |
| 🔵 **Info** | Next business day | TrafficSpike, LLMProviderSlowdown | Slack notification |

### Critical Alerts

#### APIDown
- **Condition:** API unhealthy for >1 minute
- **Impact:** Complete service outage
- **Runbook:** [docs/runbooks/APIDown.md](./runbooks/APIDown.md)

#### DatabaseDown
- **Condition:** PostgreSQL unreachable for >1 minute
- **Impact:** API cannot persist data
- **Runbook:** [docs/runbooks/DatabaseDown.md](./runbooks/DatabaseDown.md)

#### APIHighErrorRate
- **Condition:** >5% of requests return 5xx for >2 minutes
- **Impact:** Users experiencing failures
- **Runbook:** [docs/runbooks/HighErrorRate.md](./runbooks/HighErrorRate.md)

#### HighLatencyP95
- **Condition:** P95 latency >60s for >5 minutes
- **Impact:** Severe performance degradation
- **Runbook:** [docs/runbooks/HighLatency.md](./runbooks/HighLatency.md)

### Warning Alerts

#### HighLatencyP95 (Warning)
- **Condition:** P95 latency >30s for >10 minutes
- **Impact:** Performance degradation
- **Action:** Investigate, may escalate

#### LowCacheHitRate
- **Condition:** Cache hit rate <5% for >15 minutes
- **Impact:** Increased LLM costs, higher latency
- **Action:** Check cache configuration

#### HighRateLimitViolations
- **Condition:** >10 rate limit violations/sec for >10 minutes
- **Impact:** Users hitting limits frequently
- **Action:** Review rate limit settings

### Info Alerts

#### LLMProviderSlowdown
- **Condition:** LLM provider P95 >45s for >15 minutes
- **Impact:** Slower responses (cached requests unaffected)
- **Action:** Monitor provider status

#### NoRecentRequests
- **Condition:** Zero analyze requests for >30 minutes
- **Impact:** Potential availability issue
- **Action:** Verify service is accessible

---

## Alert Notification Routing

### Routing Configuration

```yaml
Critical Alerts (severity=critical):
  → PagerDuty (page oncall)
  → Email (oncall@company.com)
  → Slack (#incidents)

Warning Alerts (severity=warning):
  → Email (ops-team@company.com)
  → Slack (#alerts)

Info Alerts (severity=info):
  → Slack (#alerts)

Security Alerts (component=security):
  → Email (security@company.com)
  → Slack (#security-alerts)
  → (Also routed by severity)
```

### Configuring Notifications

**Edit:** `monitoring/alertmanager/alertmanager.yml`

**Email Configuration:**
```yaml
receivers:
  - name: 'email'
    email_configs:
      - to: 'ops-team@yourcompany.com'
        from: 'alerts@yourcompany.com'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'alerts@yourcompany.com'
        auth_password: 'your-app-password'
```

**Slack Configuration:**
```yaml
receivers:
  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#alerts'
```

**PagerDuty Configuration:**
```yaml
receivers:
  - name: 'pager'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_SERVICE_KEY'
```

---

## Runbooks

All operational runbooks are located in `docs/runbooks/`

### Available Runbooks

1. **[Runbook Index](./runbooks/RUNBOOK_INDEX.md)** - Overview and quick reference
2. **[APIDown](./runbooks/APIDown.md)** - API service unavailable
3. **[HighErrorRate](./runbooks/HighErrorRate.md)** - Elevated 5xx error rate
4. **[DatabaseDown](./runbooks/DatabaseDown.md)** - PostgreSQL unavailable (TODO)
5. **[RedisDown](./runbooks/RedisDown.md)** - Redis cache unavailable (TODO)
6. **[HighLatency](./runbooks/HighLatency.md)** - Slow response times (TODO)

### Runbook Structure

Each runbook follows this format:
1. **Overview** - What the alert means
2. **Impact** - User/business impact
3. **Diagnosis** - How to investigate
4. **Common Causes & Resolutions** - Step-by-step fixes
5. **Escalation** - When/who to escalate
6. **Prevention** - How to avoid in future

---

## Troubleshooting

### Alert Not Firing When Expected

**Check Prometheus:**
```bash
# View alert status
curl http://localhost:9090/api/v1/alerts | jq

# Check specific alert rule
curl http://localhost:9090/api/v1/rules | jq '.data.groups[].rules[] | select(.name == "APIDown")'

# Test query manually
curl 'http://localhost:9090/api/v1/query?query=up{job="api"}' | jq
```

**Check Alertmanager:**
```bash
# View active alerts
curl http://localhost:9093/api/v2/alerts | jq

# Check configuration
docker logs alertmanager
```

### Alert Firing But No Notification

**Check Alertmanager Logs:**
```bash
docker logs alertmanager --tail 100

# Look for:
# - "Notify attempt failed"
# - SMTP errors
# - Webhook errors
```

**Test Notification Manually:**
```bash
# Send test alert
curl -X POST http://localhost:9093/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d '[{
    "labels": {"alertname": "Test", "severity": "info"},
    "annotations": {"summary": "Test alert"}
  }]'
```

### Metrics Not Showing in Grafana

**Check Prometheus Scrape:**
```bash
# View targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.job == "structured-prompt-api")'

# Check last scrape time
```

**Test Metrics Endpoint:**
```bash
curl http://localhost:8000/v1/metrics | head -20

# Should see Prometheus-formatted metrics
```

### High Cardinality Metrics

**Problem:** Too many unique label combinations

**Diagnosis:**
```promql
# Count unique time series
count({__name__=~".+"})

# Find high-cardinality metrics
topk(10, count by (__name__)({__name__=~".+"}))
```

**Solution:**
- Reduce label cardinality (e.g., use "error" instead of specific error messages)
- Increase Prometheus retention period
- Use recording rules for expensive queries

---

## Health Checks

### Enhanced Health Endpoint

**URL:** http://localhost:8000/v1/health

**Response Example:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development",
  "uptime_seconds": 3600,
  "timestamp": 1729440000,
  "dependencies": {
    "postgres": {
      "status": "up",
      "latency_ms": 2.34
    },
    "redis": {
      "status": "up",
      "latency_ms": 0.87,
      "used_memory_mb": 12.5,
      "connected_clients": 5
    }
  },
  "system": {
    "cpu_percent": 15.2,
    "memory_percent": 45.7,
    "disk_percent": 62.3
  }
}
```

### Kubernetes Health Probes

**Liveness Probe:**
```yaml
livenessProbe:
  httpGet:
    path: /v1/live
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
```

**Readiness Probe:**
```yaml
readinessProbe:
  httpGet:
    path: /v1/ready
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
```

---

## Best Practices

### 1. Alert Hygiene

**Do:**
- ✅ Set appropriate thresholds (not too sensitive)
- ✅ Include runbook links in alert annotations
- ✅ Use inhibition rules to prevent alert storms
- ✅ Review and update alerts monthly

**Don't:**
- ❌ Alert on non-actionable conditions
- ❌ Set overly aggressive thresholds (alert fatigue)
- ❌ Ignore alerts (builds bad habits)

### 2. Metric Collection

**Do:**
- ✅ Use consistent naming conventions
- ✅ Add descriptive labels (but limit cardinality)
- ✅ Use appropriate metric types (Counter, Gauge, Histogram)
- ✅ Document custom metrics

**Don't:**
- ❌ Use high-cardinality labels (user IDs, request IDs)
- ❌ Create excessive unique time series
- ❌ Use inconsistent metric names

### 3. Dashboard Design

**Do:**
- ✅ Group related metrics together
- ✅ Use appropriate visualization types
- ✅ Set meaningful time ranges
- ✅ Add panel descriptions

**Don't:**
- ❌ Overcrowd dashboards with too many panels
- ❌ Use misleading y-axis scales
- ❌ Create dashboards without clear purpose

### 4. On-Call Response

**Do:**
- ✅ Acknowledge alerts promptly
- ✅ Follow runbooks systematically
- ✅ Document all actions taken
- ✅ Communicate in #incidents channel

**Don't:**
- ❌ Ignore alerts hoping they'll resolve
- ❌ Make changes without documentation
- ❌ Skip post-incident reviews

---

## Useful PromQL Queries

### Request Rate Trends

```promql
# Current request rate
sum(rate(http_requests_total[5m]))

# Request rate by endpoint
sum(rate(http_requests_total[5m])) by (handler)

# Request rate by status code
sum(rate(http_requests_total[5m])) by (status)
```

### Error Analysis

```promql
# Total 5xx errors per second
sum(rate(http_requests_total{status=~"5.."}[5m]))

# Error rate percentage
100 * sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))

# Most common error codes
topk(5, sum(rate(http_requests_total{status=~"5.."}[5m])) by (status))
```

### Latency Analysis

```promql
# P50, P95, P99 latencies
histogram_quantile(0.50, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# Average latency
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])
```

### Cache Performance

```promql
# Cache hit rate
sum(rate(cache_hits_total[5m])) / (sum(rate(cache_hits_total[5m])) + sum(rate(cache_misses_total[5m])))

# Cache entries over time
cache_entries_total
```

---

## Monitoring Checklist

### Daily

- [ ] Check Grafana dashboards for anomalies
- [ ] Review active alerts in Alertmanager
- [ ] Verify all services are "up" in Prometheus targets

### Weekly

- [ ] Review alert history and false positives
- [ ] Check disk space on monitoring servers
- [ ] Verify alert notifications are working

### Monthly

- [ ] Review and update alert thresholds
- [ ] Add new metrics for recent features
- [ ] Update runbooks with lessons learned
- [ ] Test disaster recovery procedures

---

## Additional Resources

- **Prometheus Documentation:** https://prometheus.io/docs/
- **Grafana Documentation:** https://grafana.com/docs/
- **PromQL Tutorial:** https://prometheus.io/docs/prometheus/latest/querying/basics/
- **Alert Runbooks:** [docs/runbooks/](./runbooks/)
- **Architecture Documentation:** [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Performance Test Results:** [PERFORMANCE_TEST_RESULTS.md](./PERFORMANCE_TEST_RESULTS.md)

---

## Support

For monitoring issues or questions:
- **Slack:** #monitoring or #incidents
- **Email:** ops-team@yourcompany.com
- **On-Call:** Check PagerDuty rotation
