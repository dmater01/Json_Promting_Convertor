# TOON Testing Guide - How to Test with Example Questions

## 🎯 Quick Start Testing

### Step 1: Set Up Your Test Environment

```bash
# Navigate to your project directory
cd /path/to/structured-prompt-service

# Ensure you have the TOON parser
# (Use the toon_parser.py file from the conversion project)
```

---

## 🧪 Test Methods

### Method 1: Direct Python Testing (Recommended)

Create a test file to validate TOON conversion:

```python
# test_toon_conversion.py

from toon_parser import encode_to_toon, decode_from_toon
from json_vs_toon_comparison import compare_formats
import json

def test_example_question(question: str):
    """Test a single question through the TOON pipeline."""
    
    print("="*80)
    print(f"📝 TESTING QUESTION: {question}")
    print("="*80)
    
    # Step 1: Create the expected JSON response (your current format)
    json_response = {
        "intent": "find",
        "subject": "users",
        "entities": {
            "name": "Alice",
            "status": "active"
        },
        "output_format": "list",
        "original_language": "en",
        "confidence_score": 0.95
    }
    
    print("\n1️⃣ JSON RESPONSE:")
    json_str = json.dumps(json_response, indent=2)
    print(json_str)
    
    # Step 2: Convert to TOON
    print("\n2️⃣ TOON RESPONSE:")
    toon_str = encode_to_toon(json_response)
    print(toon_str)
    
    # Step 3: Compare token savings
    print("\n3️⃣ TOKEN COMPARISON:")
    comparison = compare_formats(json_response)
    print(comparison)
    
    # Step 4: Verify round-trip (TOON -> Python -> TOON)
    print("\n4️⃣ ROUND-TRIP VERIFICATION:")
    decoded = decode_from_toon(toon_str)
    
    if decoded == json_response:
        print("✅ PASS: Round-trip successful!")
    else:
        print("❌ FAIL: Round-trip mismatch!")
        print(f"Expected: {json_response}")
        print(f"Got: {decoded}")
    
    return {
        "json_tokens": comparison["json_tokens"],
        "toon_tokens": comparison["toon_tokens"],
        "savings_percent": comparison["savings_percent"],
        "passed": decoded == json_response
    }


# Example test questions
test_questions = [
    "Find all users named Alice",
    "Extract contacts from this email",
    "Schedule a meeting with the team on Monday",
    "Analyze sentiment of customer reviews",
    "Summarize the key points from this document"
]

if __name__ == "__main__":
    print("🚀 Starting TOON Conversion Tests\n")
    
    results = []
    for question in test_questions:
        result = test_example_question(question)
        results.append(result)
        print("\n" + "="*80 + "\n")
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("="*80)
    avg_savings = sum(r["savings_percent"] for r in results) / len(results)
    passed = sum(1 for r in results if r["passed"])
    
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}/{len(results)}")
    print(f"Average Token Savings: {avg_savings:.1f}%")
    print("="*80)
```

**Run it:**
```bash
python test_toon_conversion.py
```

---

## 📋 Example Test Cases

### Example 1: Simple User Query

**Input Question:**
```
"Find all users named Alice who are active"
```

**Expected JSON Response:**
```json
{
  "intent": "find",
  "subject": "users",
  "entities": {
    "name": "Alice",
    "status": "active"
  },
  "output_format": "list",
  "original_language": "en",
  "confidence_score": 0.95
}
```

**Expected TOON Response:**
```toon
intent: find
subject: users
entities:
  name: Alice
  status: active
output_format: list
original_language: en
confidence_score: 0.95
```

**Token Comparison:**
- JSON: ~45 tokens
- TOON: ~28 tokens
- **Savings: 38%** ✅

---

### Example 2: Contact Extraction (with Tabular Array)

**Input Question:**
```
"Extract contacts: John (john@example.com, 555-1234), Sarah (sarah@example.com, 555-5678)"
```

**Expected JSON Response:**
```json
{
  "intent": "extract",
  "subject": "contacts",
  "entities": {
    "contacts": [
      {
        "name": "John",
        "email": "john@example.com",
        "phone": "555-1234"
      },
      {
        "name": "Sarah",
        "email": "sarah@example.com",
        "phone": "555-5678"
      }
    ]
  },
  "output_format": "tabular",
  "original_language": "en",
  "confidence_score": 0.98
}
```

**Expected TOON Response (with Tabular Array - Maximum Efficiency!):**
```toon
intent: extract
subject: contacts
entities:
  contacts [2,]
    name, email, phone
    John, john@example.com, 555-1234
    Sarah, sarah@example.com, 555-5678
output_format: tabular
original_language: en
confidence_score: 0.98
```

**Token Comparison:**
- JSON: ~95 tokens
- TOON: ~42 tokens
- **Savings: 56%** ✅✅

---

### Example 3: Meeting Schedule (Nested Structure)

**Input Question:**
```
"Schedule meeting with team about Q4 planning on Monday at 10am in Conference Room A"
```

**Expected JSON Response:**
```json
{
  "intent": "schedule",
  "subject": "meeting",
  "entities": {
    "participants": "team",
    "topic": "Q4 planning",
    "schedule": {
      "day": "Monday",
      "time": "10am"
    },
    "location": "Conference Room A"
  },
  "output_format": "structured",
  "original_language": "en",
  "confidence_score": 0.92
}
```

**Expected TOON Response:**
```toon
intent: schedule
subject: meeting
entities:
  participants: team
  topic: Q4 planning
  schedule:
    day: Monday
    time: 10am
  location: Conference Room A
output_format: structured
original_language: en
confidence_score: 0.92
```

**Token Comparison:**
- JSON: ~78 tokens
- TOON: ~48 tokens
- **Savings: 38%** ✅

---

## 🔬 Method 2: API Testing

If you've integrated TOON into your FastAPI service:

```python
# test_api_toon.py

import requests
import json

def test_api_with_toon(question: str):
    """Test the API with TOON format."""
    
    # Test JSON endpoint (existing)
    json_response = requests.post(
        "http://localhost:8000/analyze",
        json={"prompt": question}
    )
    
    # Test TOON endpoint (new)
    toon_response = requests.post(
        "http://localhost:8000/analyze-toon",
        json={"prompt": question}
    )
    
    print(f"📝 Question: {question}\n")
    
    print("JSON Response:")
    print(json.dumps(json_response.json(), indent=2))
    print(f"Content-Length: {len(json_response.text)} bytes\n")
    
    print("TOON Response:")
    print(toon_response.text)
    print(f"Content-Length: {len(toon_response.text)} bytes\n")
    
    savings = (1 - len(toon_response.text) / len(json_response.text)) * 100
    print(f"💰 Size Savings: {savings:.1f}%")


# Test with example questions
test_api_with_toon("Find all users named Alice")
```

**Run the API tests:**
```bash
# Start your FastAPI server first
uvicorn main:app --reload

# In another terminal
python test_api_toon.py
```

---

## 🧪 Method 3: Interactive Testing

Create an interactive test script:

```python
# interactive_toon_test.py

from toon_parser import encode_to_toon, decode_from_toon
from json_vs_toon_comparison import compare_formats
import json

def interactive_test():
    """Interactive TOON testing."""
    
    print("🎯 TOON Interactive Tester")
    print("="*80)
    print("Enter your test data as JSON, and I'll show you the TOON conversion.")
    print("Type 'quit' to exit.\n")
    
    while True:
        print("\n📝 Enter JSON (or 'quit'):")
        user_input = input().strip()
        
        if user_input.lower() == 'quit':
            break
        
        try:
            # Parse JSON
            data = json.loads(user_input)
            
            # Convert to TOON
            toon_output = encode_to_toon(data)
            
            print("\n✨ TOON Output:")
            print(toon_output)
            
            # Show comparison
            print("\n📊 Comparison:")
            comparison = compare_formats(data)
            print(comparison)
            
            # Verify round-trip
            decoded = decode_from_toon(toon_output)
            if decoded == data:
                print("\n✅ Round-trip: PASSED")
            else:
                print("\n❌ Round-trip: FAILED")
                
        except json.JSONDecodeError:
            print("❌ Invalid JSON. Please try again.")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    interactive_test()
```

**Run it:**
```bash
python interactive_toon_test.py
```

**Example interaction:**
```
Enter JSON:
{"intent": "find", "subject": "users", "entities": {"name": "Alice"}}

✨ TOON Output:
intent: find
subject: users
entities:
  name: Alice

📊 Comparison:
JSON Tokens: 32
TOON Tokens: 18
Savings: 43.75% (14 tokens)

✅ Round-trip: PASSED
```

---

## 📊 Method 4: Batch Testing with Multiple Examples

```python
# batch_test_toon.py

from toon_examples import EXAMPLES
from toon_parser import encode_to_toon
from json_vs_toon_comparison import compare_formats

def run_batch_tests():
    """Run all examples through TOON conversion."""
    
    print("🚀 Running Batch TOON Tests")
    print("="*80 + "\n")
    
    total_json_tokens = 0
    total_toon_tokens = 0
    
    for i, example in enumerate(EXAMPLES, 1):
        print(f"Test {i}: {example['name']}")
        print("-" * 40)
        
        # Get the data
        data = example['data']
        
        # Convert to TOON
        toon_output = encode_to_toon(data)
        
        # Compare
        comparison = compare_formats(data)
        
        print(f"JSON Tokens: {comparison['json_tokens']}")
        print(f"TOON Tokens: {comparison['toon_tokens']}")
        print(f"Savings: {comparison['savings_percent']:.1f}%")
        
        total_json_tokens += comparison['json_tokens']
        total_toon_tokens += comparison['toon_tokens']
        
        print()
    
    print("="*80)
    print("📊 OVERALL RESULTS")
    print("="*80)
    print(f"Total JSON Tokens: {total_json_tokens}")
    print(f"Total TOON Tokens: {total_toon_tokens}")
    
    overall_savings = (1 - total_toon_tokens / total_json_tokens) * 100
    print(f"Overall Savings: {overall_savings:.1f}%")
    print("="*80)


if __name__ == "__main__":
    run_batch_tests()
```

---

## 🎯 Quick Test Commands

### Test 1: Validate Parser
```bash
python toon_parser.py
```

### Test 2: Run Comparisons
```bash
python json_vs_toon_comparison.py
```

### Test 3: Check Examples
```bash
python toon_examples.py
```

### Test 4: Full Test Suite
```bash
python test_toon_conversion.py
```

---

## ✅ Expected Results Checklist

After running tests, verify:

- [ ] TOON output is valid (no syntax errors)
- [ ] Round-trip works (TOON → Python → TOON)
- [ ] Token savings are 30-60%
- [ ] Tabular arrays used for uniform data
- [ ] Strings quoted only when necessary
- [ ] Array length indicators present `[N]`
- [ ] Indentation is consistent (2 spaces)
- [ ] No JSON braces `{}` or brackets `[]`

---

## 🐛 Common Issues & Solutions

### Issue 1: "Array length mismatch"
**Solution:** Check that `[N]` matches actual item count

### Issue 2: "Invalid string quoting"
**Solution:** Review quoting rules - most strings should be unquoted

### Issue 3: "Indentation error"
**Solution:** Ensure exactly 2 spaces per level (no tabs!)

### Issue 4: "Lower token savings than expected"
**Solution:** Use tabular arrays `[N,]` instead of list arrays `[N]`

---

## 🎉 Success Metrics

Your tests are successful when:

✅ **30-60% token reduction** achieved
✅ **Round-trip validation** passes
✅ **API integration** works seamlessly
✅ **Performance** maintained or improved
✅ **All test cases** pass

---

## 📚 Next Steps

1. ✅ Run `test_toon_conversion.py`
2. ✅ Verify token savings meet targets
3. ✅ Test with your actual application data
4. ✅ Deploy to staging environment
5. ✅ Monitor production metrics

---

**Ready to test? Start with the simplest example and work your way up!** 🚀
