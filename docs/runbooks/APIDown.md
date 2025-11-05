# Runbook: API Down

**Alert Name:** `APIDown`
**Severity:** 🔴 Critical
**MTTR Target:** 5 minutes
**Auto-Page:** Yes

---

## Overview

The API service is not responding to health checks. This is a **complete outage** affecting all users.

**Alert Condition:**
```promql
up{job="api"} == 0
for: 1m
```

---

## Impact

- **User Impact:** 100% of API requests failing
- **Business Impact:** Complete service outage
- **Affected Endpoints:** All `/v1/*` endpoints
- **SLA Impact:** Critical SLA breach

---

## Immediate Actions (First 2 Minutes)

### 1. Acknowledge Alert
```bash
# In PagerDuty or Slack
"Acknowledged - investigating API Down alert"
```

### 2. Verify Outage
```bash
# Test health endpoint
curl -v http://localhost:8000/v1/health

# Expected: Connection refused or timeout
# If 200 OK: False alarm, check Prometheus config
```

### 3. Check Grafana Dashboard
- Open: http://localhost:3000
- Dashboard: "API Overview - Structured Prompt Service"
- Look for: Request rate drop to 0, spike in errors before outage

---

## Diagnosis

### Step 1: Check Service Status

```bash
# Check if container is running
docker ps | grep api

# Expected: Container should be in list
# If missing: Container crashed or was stopped
```

### Step 2: Check Recent Logs

```bash
# View last 100 lines
docker logs api-server --tail 100

# Look for:
# - Python exceptions/tracebacks
# - "Out of memory" errors
# - Database connection errors
# - Port binding errors
```

### Step 3: Check System Resources

```bash
# Check Docker container status
docker stats api-server --no-stream

# Look for:
# - High CPU (>90%)
# - High Memory (>90%)
# - Container restarts
```

### Step 4: Check Dependencies

```bash
# Database
curl http://localhost:8000/v1/health 2>&1 | grep postgres

# Redis
curl http://localhost:8000/v1/health 2>&1 | grep redis

# If either shows "down", see respective runbooks
```

---

## Common Causes & Resolutions

### Cause 1: Container Crashed

**Symptoms:**
- `docker ps` shows no api container
- Logs show exception before termination

**Resolution:**
```bash
# Restart the service
docker-compose restart api

# Wait 30 seconds
sleep 30

# Verify health
curl http://localhost:8000/v1/health

# Expected: {"status":"healthy",...}
```

**Verification:**
```bash
# Check Grafana dashboard
# Request rate should resume
# Error rate should return to 0%
```

---

### Cause 2: Out of Memory (OOM)

**Symptoms:**
- Logs show: "MemoryError" or "Killed"
- `docker stats` showed high memory before crash

**Resolution:**
```bash
# Check memory limit
docker inspect api-server | grep Memory

# Increase memory limit in docker-compose.yml
# mem_limit: 2g  # Change to 4g

# Restart with new limit
docker-compose down
docker-compose up -d

# Monitor memory usage
docker stats api-server
```

**Follow-up:**
- File bug for memory leak
- Review application code for memory issues
- Consider scaling horizontally

---

### Cause 3: Database Connection Failure

**Symptoms:**
- Logs show: "could not connect to database"
- Health check shows: `"postgres": "down"`

**Resolution:**
```bash
# Check database is running
docker ps | grep postgres

# Verify database connectivity
docker exec -it postgres psql -U structured_prompt -d structured_prompt_db -c "SELECT 1;"

# If database is up but API can't connect:
# Restart API to reset connection pool
docker-compose restart api
```

**If database is down:** See [DatabaseDown Runbook](./DatabaseDown.md)

---

### Cause 4: Port Conflict

**Symptoms:**
- Logs show: "Address already in use" or "bind failed"
- Container starts but immediately exits

**Resolution:**
```bash
# Check what's using port 8000
sudo lsof -i :8000

# If another process is using it:
# Option 1: Kill the process
sudo kill -9 <PID>

# Option 2: Change API port in docker-compose.yml
# ports:
#   - "8080:8000"  # Changed external port

# Restart
docker-compose up -d
```

---

### Cause 5: Configuration Error

**Symptoms:**
- Logs show: "Configuration error" or validation errors
- Recent deployment or config change

**Resolution:**
```bash
# Check environment variables
docker exec api-server env | grep -E '(DATABASE|REDIS|GEMINI)'

# Verify .env file
cat .env | grep -v '^#' | grep .

# If misconfigured:
# Fix .env file
nano .env

# Restart
docker-compose restart api
```

**Rollback (if recent deployment):**
```bash
# Roll back to previous version
git checkout HEAD~1
docker-compose build api
docker-compose up -d api
```

---

## Resolution Steps

### 1. Apply Fix
```bash
# Based on diagnosis above, apply appropriate fix
# Most common: docker-compose restart api
```

### 2. Verify Service is Up
```bash
# Health check should pass
curl http://localhost:8000/v1/health

# Expected output:
# {
#   "status": "healthy",
#   "version": "0.1.0",
#   "dependencies": {
#     "postgres": "up",
#     "redis": "up"
#   }
# }
```

### 3. Test API Functionality
```bash
# Test analyze endpoint
curl -X POST http://localhost:8000/v1/analyze/ \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: sp_e7f0...' \
  -d '{"prompt": "Post-incident test"}'

# Expected: 200 OK with valid response
```

### 4. Monitor for 15 Minutes
```bash
# Watch Grafana dashboard
# - Request rate should return to normal
# - Error rate should be 0%
# - P95 latency should be <10s

# Watch logs for errors
docker logs api-server --follow
```

---

## Escalation

### Escalate if:
- Service won't start after 3 restart attempts
- Unknown/complex error in logs
- Requires infrastructure changes
- Outage >15 minutes

### Escalate to:
- **Level 2:** Senior Engineer (Slack: @senior-oncall)
- **Level 3:** Engineering Lead (if >30 min outage)

---

## Prevention

### Short-term (This Week):
1. Add health check probes with auto-restart
   ```yaml
   # In docker-compose.yml
   healthcheck:
     test: ["CMD", "curl", "-f", "http://localhost:8000/v1/health"]
     interval: 30s
     timeout: 10s
     retries: 3
     start_period: 40s
   ```

2. Set resource limits
   ```yaml
   mem_limit: 2g
   mem_reservation: 1g
   cpus: '2'
   ```

3. Enable container auto-restart
   ```yaml
   restart: unless-stopped
   ```

### Medium-term (This Month):
1. Set up redundant API instances (3+)
2. Implement load balancer (nginx/HAProxy)
3. Add circuit breaker for dependencies
4. Implement graceful degradation

### Long-term (This Quarter):
1. Kubernetes with auto-scaling
2. Multi-region deployment
3. Chaos engineering tests
4. Self-healing infrastructure

---

## Post-Incident

### 1. Document Incident
```markdown
**Incident:** API Down
**Duration:** [START] - [END] (X minutes)
**Root Cause:** [Brief description]
**Impact:** 100% service outage
**Resolution:** [What fixed it]
**Follow-up Tasks:**
- [ ] Task 1
- [ ] Task 2
```

### 2. Create Jira Tickets
- Bug fix (if code issue)
- Infrastructure improvement
- Monitoring enhancement

### 3. Schedule Post-Mortem
- Within 48 hours
- Invite: Engineering team, stakeholders
- Agenda: Timeline, root cause, prevention

---

## Testing This Runbook

```bash
# Simulate API down (for training only!)
docker-compose stop api

# Follow runbook steps above

# Restore
docker-compose start api
```

---

## Related Runbooks
- [DatabaseDown](./DatabaseDown.md)
- [RedisDown](./RedisDown.md)
- [HighErrorRate](./HighErrorRate.md)

## Related Documentation
- [Architecture](../ARCHITECTURE.md)
- [Deployment Guide](../DEPLOYMENT.md)
- [Docker Compose Reference](../../docker-compose.yml)
