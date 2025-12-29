# TOON Conversion Quick Start Guide
## Structured Prompt Service → TOON Format

**Goal:** Convert your JSON-based Structured Prompt Service to support TOON format for 30-60% token savings.

**Timeline:** 3-4 weeks for full implementation
**Difficulty:** Medium
**Expected ROI:** $13,500/year (based on 500K requests/month)

---

## 📋 Prerequisites

Before you begin, ensure you have:

- ✅ Existing Structured Prompt Service running (FastAPI + Gemini)
- ✅ Python 3.11+ environment
- ✅ Access to modify backend code
- ✅ Test environment for validation
- ✅ Basic understanding of TOON format (see project documents)

---

## 🚀 Quick Start (Day 1)

### Step 1: Install Dependencies

```bash
# Option A: Use existing toon-format library (if available)
pip install toon-format

# Option B: Use custom parser provided
cp toon_parser.py app/services/
cp toon_prompts.py app/prompts/
```

### Step 2: Test TOON Parser

```bash
# Run the comparison example
python json_vs_toon_comparison.py
```

**Expected Output:**
```
JSON tokens: 150
TOON tokens: 72
Token savings: 78 (52%)
```

If you see ~30-60% savings, you're good to proceed!

### Step 3: Read the Strategy Document

Open `TOON_CONVERSION_STRATEGY.md` and review:
- [ ] Executive Summary
- [ ] Implementation Plan (Phases 1-6)
- [ ] Code Changes Required
- [ ] Risk Assessment

---

## 🛠️ Implementation Roadmap

### Week 1: Foundation + LLM Integration

**Phase 1: Foundation (Days 1-3)**

1. **Add TOON Parser to Project**
   ```bash
   mkdir -p app/services/toon
   cp toon_parser.py app/services/toon/
   cp toon_prompts.py app/prompts/
   ```

2. **Update Dependencies**
   ```python
   # requirements.txt (add if not using custom parser)
   toon-format>=1.0.0  # hypothetical package
   ```

3. **Update Request Models**
   ```python
   # app/models/requests.py
   
   class AnalyzeRequest(BaseModel):
       prompt: str = Field(..., min_length=1, max_length=10_000)
       output_format: Literal["json", "toon"] = "json"  # NEW
       schema_definition: Optional[Dict[str, Any]] = None
       llm_provider: Literal["auto", "gemini", "claude", "gpt-4"] = "auto"
       temperature: float = Field(default=0.1, ge=0.0, le=2.0)
       max_tokens: int = Field(default=2000, ge=50, le=8000)
       cache_ttl: int = Field(default=3600, ge=0, le=86400)
       metadata: Optional[Dict[str, Any]] = None
   ```

4. **Create Unit Tests**
   ```bash
   # tests/test_toon_parser.py
   pytest tests/test_toon_parser.py -v
   ```

**Phase 2: LLM Integration (Days 4-7)**

1. **Modify LLM Service**
   ```python
   # app/services/llm_service.py
   
   from app.prompts.toon_prompts import build_toon_prompt_for_gemini
   from app.services.toon.toon_parser import ToonParser
   
   class LLMService:
       async def analyze_prompt(
           self,
           prompt: str,
           output_format: str = "json",
           provider: str = "gemini",
           temperature: float = 0.1
       ) -> Dict[str, Any]:
           """Analyze prompt and return structured data in requested format."""
           
           if output_format == "toon":
               return await self._analyze_toon(prompt, provider, temperature)
           else:
               return await self._analyze_json(prompt, provider, temperature)
       
       async def _analyze_toon(
           self,
           prompt: str,
           provider: str,
           temperature: float
       ) -> Dict[str, Any]:
           """Generate TOON format response."""
           
           # Build TOON-specific prompt
           llm_prompt = build_toon_prompt_for_gemini(prompt)
           
           # Call LLM
           response = await self.client.generate(
               prompt=llm_prompt,
               temperature=temperature,
               max_tokens=2000
           )
           
           # Extract TOON from code block
           toon_string = self._extract_code_block(response, "toon")
           
           # Parse and validate
           parser = ToonParser()
           try:
               data = parser.parse(toon_string, strict=False)
               return data
           except Exception as e:
               logger.error(f"TOON parse failed: {e}")
               # Fallback to JSON
               return await self._analyze_json(prompt, provider, temperature)
   ```

2. **Test with Real LLM**
   ```python
   # tests/integration/test_toon_llm.py
   
   @pytest.mark.asyncio
   async def test_gemini_toon_generation():
       """Test Gemini generates valid TOON."""
       service = LLMService()
       result = await service.analyze_prompt(
           "Extract contacts from: John (john@example.com)",
           output_format="toon"
       )
       
       assert "intent" in result
       assert "entities" in result
   ```

---

### Week 2: API Endpoints + Monitoring

**Phase 3: API Endpoints (Days 8-10)**

1. **Update /v1/analyze Endpoint**
   ```python
   # app/api/v1/analyze.py
   
   @router.post("/")
   async def analyze_prompt(
       request: AnalyzeRequest,
       api_key: APIKey = Depends(get_api_key),
       db: AsyncSession = Depends(get_db),
       redis: Redis = Depends(get_redis)
   ):
       """Analyze prompt with JSON or TOON output."""
       
       # Check cache (include format in key)
       cache_key = generate_cache_key(
           request.prompt,
           request.llm_provider,
           request.temperature,
           request.output_format  # NEW
       )
       
       cached = await redis.get(cache_key)
       if cached:
           if request.output_format == "toon":
               return Response(content=cached, media_type="application/toon")
           else:
               return JSONResponse(content=json.loads(cached))
       
       # Generate response
       llm_service = LLMService()
       result = await llm_service.analyze_prompt(
           request.prompt,
           request.output_format,
           request.llm_provider,
           request.temperature
       )
       
       # Build response object
       response_data = {
           "request_id": str(uuid.uuid4()),
           "data": result,
           "llm_provider": request.llm_provider,
           "output_format": request.output_format,
           "cached": False,
           "timestamp": datetime.utcnow().isoformat() + "Z"
       }
       
       # Convert to requested format
       if request.output_format == "toon":
           parser = ToonParser()
           toon_string = parser.generate(response_data)
           
           # Cache TOON
           await redis.setex(cache_key, request.cache_ttl, toon_string)
           
           return Response(
               content=toon_string,
               media_type="application/toon",
               headers={
                   "X-Output-Format": "toon",
                   "X-Token-Savings": "45%"  # Calculate actual
               }
           )
       else:
           # JSON response (existing code)
           json_string = json.dumps(response_data)
           await redis.setex(cache_key, request.cache_ttl, json_string)
           return JSONResponse(content=response_data)
   ```

**Phase 4: Monitoring (Days 11-14)**

1. **Add Prometheus Metrics**
   ```python
   # app/monitoring/metrics.py
   
   from prometheus_client import Counter, Histogram
   
   toon_requests_total = Counter(
       "toon_requests_total",
       "Total TOON format requests",
       ["provider", "status"]
   )
   
   toon_token_savings = Histogram(
       "toon_token_savings_percent",
       "Token savings percentage vs JSON",
       buckets=[10, 20, 30, 40, 50, 60, 70, 80]
   )
   
   toon_parse_errors = Counter(
       "toon_parse_errors_total",
       "TOON parsing failures"
   )
   
   # Track in endpoint
   if output_format == "toon":
       toon_requests_total.labels(provider=provider, status="success").inc()
       toon_token_savings.observe(45.0)  # Calculate actual savings
   ```

2. **Update Grafana Dashboard**
   - Add TOON metrics panel
   - Token savings graph
   - Format usage pie chart (JSON vs TOON)
   - Error rate comparison

---

### Week 3: Testing + Validation

**Phase 5: Comprehensive Testing (Days 15-21)**

1. **Unit Tests**
   ```bash
   pytest tests/test_toon_parser.py -v
   pytest tests/test_toon_validation.py -v
   pytest tests/test_toon_prompts.py -v
   ```

2. **Integration Tests**
   ```bash
   pytest tests/integration/test_toon_api.py -v
   ```

3. **Load Testing**
   ```bash
   # Create load test
   locust -f load_tests/toon_load_test.py \
          --host http://localhost:8000 \
          --users 50 \
          --spawn-rate 5 \
          --run-time 120s
   ```

4. **Validation Tests**
   - Verify 30-60% token savings
   - Check parse success rate >95%
   - Confirm backward compatibility (JSON still works)
   - Test error recovery

---

### Week 4: Documentation + Deployment

**Phase 6: Documentation (Days 22-25)**

1. **API Documentation**
   ```markdown
   # docs/TOON_API_GUIDE.md
   
   # Using TOON Format
   
   Request TOON output by setting `output_format: "toon"`:
   
   \`\`\`bash
   curl -X POST https://api.example.com/v1/analyze \\
     -H "X-API-Key: sp_your_key" \\
     -d '{
       "prompt": "Extract users",
       "output_format": "toon"
     }'
   \`\`\`
   ```

2. **Migration Guide**
   - Document for existing clients
   - Provide code examples
   - Explain benefits

**Deployment (Days 26-28)**

1. **Deploy to Staging**
   ```bash
   docker-compose -f docker-compose.staging.yml up -d
   ```

2. **Run Smoke Tests**
   - Test JSON endpoint (backward compat)
   - Test TOON endpoint
   - Verify metrics collection

3. **Production Rollout**
   ```bash
   # Deploy with feature flag (disabled)
   ENABLE_TOON=false docker-compose up -d
   
   # Enable for 10% of traffic
   ENABLE_TOON=true TOON_ROLLOUT_PERCENT=10
   
   # Monitor for 24 hours, then increase to 100%
   ```

---

## ✅ Validation Checklist

Before marking complete, verify:

**Functionality:**
- [ ] TOON parser works (parse + generate)
- [ ] LLM generates valid TOON >95% of time
- [ ] API accepts `output_format: "toon"`
- [ ] API returns TOON responses
- [ ] Cache works with TOON format
- [ ] JSON endpoints still work (backward compat)

**Performance:**
- [ ] Token savings: 30-60% (measure actual)
- [ ] Parse success rate: >95%
- [ ] Latency impact: <+10%
- [ ] Cache hit rate: maintained (~15-20%)
- [ ] Error rate: <5%

**Monitoring:**
- [ ] Prometheus metrics collecting
- [ ] Grafana dashboard shows TOON usage
- [ ] Alerts configured (error rate, savings)
- [ ] Logs capture TOON events

**Documentation:**
- [ ] API docs updated
- [ ] Migration guide complete
- [ ] Code examples provided
- [ ] README mentions TOON support

**Testing:**
- [ ] Unit tests pass (>85% coverage)
- [ ] Integration tests pass
- [ ] Load tests show 0% failure rate
- [ ] Token savings validated in tests

---

## 🎯 Success Metrics

Track these KPIs after deployment:

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Token Savings | 35-55% | ? | ⏳ |
| Parse Success Rate | >95% | ? | ⏳ |
| Adoption Rate | 50% in 3 months | ? | ⏳ |
| Cost Savings | Match token savings | ? | ⏳ |
| Latency Impact | <+10% | ? | ⏳ |
| Error Rate | <5% | ? | ⏳ |

---

## 🐛 Troubleshooting

### Problem: LLM generates invalid TOON

**Solution:**
1. Check prompt includes TOON format rules
2. Add few-shot examples (use `toon_prompts.py`)
3. Enable lenient parsing mode
4. Implement retry with JSON fallback

### Problem: Token savings below 30%

**Solution:**
1. Verify tabular arrays used for uniform data
2. Check strings are unquoted when possible
3. Measure actual token counts (not character counts)
4. Review LLM-generated TOON structure

### Problem: Parse errors >5%

**Solution:**
1. Enable lenient parsing mode
2. Add error recovery logic
3. Improve LLM prompts (more examples)
4. Log raw TOON strings for debugging

### Problem: Cache keys conflicting

**Solution:**
1. Include `output_format` in cache key
2. Use separate Redis namespaces for JSON/TOON
3. Update cache key generation function

---

## 📚 Additional Resources

**Files Provided:**
- `TOON_CONVERSION_STRATEGY.md` - Complete strategy document
- `toon_parser.py` - TOON parser implementation
- `toon_prompts.py` - LLM prompt templates
- `json_vs_toon_comparison.py` - Comparison examples

**Project Documentation:**
- `Understanding_TOON__A_Beginner_s_Guide_to_the_Data_Format` - TOON basics
- `TOON_Integration_for_Large_Language_Models` - LLM best practices
- `TOON_Format_Type_Normalization_and_Encoding_Rules` - Format spec
- `TOON_SKILL_GUIDE.md` - Claude skill for TOON

**External Resources:**
- TOON GitHub: [hypothetical URL]
- TOON Documentation: [hypothetical URL]

---

## 💰 ROI Calculation

**Assumptions:**
- Current traffic: 500K requests/month
- Average JSON tokens: 150 per response
- Average TOON tokens: 75 per response (50% savings)
- Token cost: $0.03 per 1K tokens

**Current Cost (JSON):**
```
500K × 150 tokens = 75M tokens/month
Cost: 75,000 × $0.03 = $2,250/month
```

**TOON Cost:**
```
500K × 75 tokens = 37.5M tokens/month
Cost: 37,500 × $0.03 = $1,125/month
```

**Savings:**
- Monthly: $1,125 (50%)
- Annual: $13,500
- 3-year: $40,500

**Development Cost:**
- 3-4 weeks × $2,000/week = ~$8,000

**ROI:**
- Break-even: 7 months
- 3-year ROI: 406% ($40.5K savings - $8K cost)

---

## 🎉 Next Steps

**Right Now:**
1. Review `TOON_CONVERSION_STRATEGY.md`
2. Run `json_vs_toon_comparison.py` to see savings
3. Read TOON project documentation

**This Week:**
1. Set up development environment
2. Implement Phase 1 (Foundation)
3. Write unit tests

**Next Steps:**
1. Complete Phases 2-3 (LLM + API)
2. Add monitoring (Phase 4)
3. Test thoroughly (Phase 5)
4. Deploy to staging
5. Production rollout

---

## ❓ Questions?

**Technical Questions:**
- Review `TOON_CONVERSION_STRATEGY.md` Risk Assessment section
- Check `TOON_SKILL_GUIDE.md` Troubleshooting section
- Examine code examples in `toon_*.py` files

**Business Questions:**
- See ROI calculation above
- Review Expected Token Savings in strategy doc
- Consider gradual migration path (low risk)

---

**Version:** 1.0
**Last Updated:** [Current Date]
**Estimated Completion:** 3-4 weeks
**Expected Savings:** 30-60% token reduction, $13.5K/year cost savings

**Ready to start? Begin with Phase 1! 🚀**
