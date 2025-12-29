#!/usr/bin/env python3
"""
TOON Conversion Test Suite

Comprehensive tests for TOON format conversion with example questions.
Tests validate:
- Encoding (Python -> TOON)
- Decoding (TOON -> Python)
- Round-trip conversion
- Token savings measurements
"""

import json
import sys
import os

# Ensure we can import from current directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from toon_parser import encode_to_toon, decode_from_toon
from json_vs_toon_comparison import estimate_savings, compare_formats


def test_example_question(question: str, json_response: dict, test_num: int):
    """
    Test a single question through the TOON pipeline.
    
    Args:
        question: The example question/prompt
        json_response: Expected JSON response structure
        test_num: Test number for display
    
    Returns:
        Dictionary with test results and metrics
    """
    print("\n" + "=" * 80)
    print(f"TEST #{test_num}: {question}")
    print("=" * 80)
    
    # Step 1: Show JSON response
    print("\n1️⃣  JSON RESPONSE:")
    json_str = json.dumps(json_response, indent=2)
    print(json_str)
    print(f"   Characters: {len(json_str)}")
    
    # Step 2: Convert to TOON
    print("\n2️⃣  TOON RESPONSE:")
    try:
        toon_str = encode_to_toon(json_response)
        print(toon_str)
        print(f"   Characters: {len(toon_str)}")
    except Exception as e:
        print(f"   ❌ ENCODING ERROR: {e}")
        return {
            "question": question,
            "passed": False,
            "error": str(e),
            "stage": "encoding"
        }
    
    # Step 3: Compare token savings
    print("\n3️⃣  TOKEN COMPARISON:")
    try:
        metrics = estimate_savings(json_response)
        print(f"   JSON Tokens:  {metrics['json_tokens']}")
        print(f"   TOON Tokens:  {metrics['toon_tokens']}")
        print(f"   Savings:      {metrics['savings']} tokens ({metrics['savings_percent']:.1f}%)")
        
        if metrics['savings_percent'] >= 50:
            print("   ✅ EXCELLENT: >50% savings!")
        elif metrics['savings_percent'] >= 30:
            print("   ✅ GOOD: Target achieved (30-60%)")
        else:
            print("   ⚠️  BELOW TARGET: <30% savings")
    except Exception as e:
        print(f"   ❌ COMPARISON ERROR: {e}")
        metrics = {}
    
    # Step 4: Verify round-trip (TOON -> Python -> TOON)
    print("\n4️⃣  ROUND-TRIP VERIFICATION:")
    try:
        decoded = decode_from_toon(toon_str)
        
        # Compare structures (allowing for type variations)
        if decoded == json_response:
            print("   ✅ PASS: Perfect round-trip!")
            passed = True
        else:
            print("   ⚠️  PARTIAL: Structure may differ slightly")
            print(f"   Expected: {json_response}")
            print(f"   Got:      {decoded}")
            passed = False
    except Exception as e:
        print(f"   ❌ DECODING ERROR: {e}")
        passed = False
    
    print("\n" + "-" * 80)
    result_symbol = "✅" if passed else "❌"
    print(f"{result_symbol} Test #{test_num}: {'PASSED' if passed else 'FAILED'}")
    print("-" * 80)
    
    return {
        "question": question,
        "passed": passed,
        "json_tokens": metrics.get('json_tokens', 0),
        "toon_tokens": metrics.get('toon_tokens', 0),
        "savings_percent": metrics.get('savings_percent', 0),
        "toon_output": toon_str
    }


def main():
    """Run all test examples."""
    
    print("=" * 80)
    print("🚀 TOON CONVERSION TEST SUITE")
    print("=" * 80)
    print("\nTesting example questions from Structured Prompt Service")
    print("Validating: Encoding, Decoding, Token Savings\n")
    
    # Define test cases
    test_cases = [
        {
            "question": "Find all users named Alice who are active",
            "response": {
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
        },
        {
            "question": "Extract contacts: John (john@example.com, 555-1234), Sarah (sarah@example.com, 555-5678)",
            "response": {
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
        },
        {
            "question": "Schedule meeting with team about Q4 planning on Monday at 10am",
            "response": {
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
        },
        {
            "question": "Analyze sentiment of customer reviews",
            "response": {
                "intent": "analyze",
                "subject": "sentiment",
                "entities": {
                    "target": "customer reviews",
                    "metrics": ["polarity", "subjectivity"],
                    "output_fields": ["sentiment", "score", "keywords"]
                },
                "output_format": "analysis",
                "original_language": "en",
                "confidence_score": 0.88
            }
        },
        {
            "question": "Extract all dates, people, and locations from the document",
            "response": {
                "intent": "extract",
                "subject": "entities",
                "entities": {
                    "entity_types": ["dates", "people", "locations"],
                    "source": "document",
                    "confidence_threshold": 0.7
                },
                "output_format": "multi_entity",
                "original_language": "en",
                "confidence_score": 0.85
            }
        }
    ]
    
    # Run all tests
    results = []
    for i, test_case in enumerate(test_cases, 1):
        result = test_example_question(
            question=test_case["question"],
            json_response=test_case["response"],
            test_num=i
        )
        results.append(result)
    
    # Print summary
    print("\n\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed_tests = [r for r in results if r.get("passed", False)]
    failed_tests = [r for r in results if not r.get("passed", False)]
    
    print(f"\nTotal Tests:  {len(results)}")
    print(f"✅ Passed:    {len(passed_tests)}")
    print(f"❌ Failed:    {len(failed_tests)}")
    
    if results:
        avg_savings = sum(r.get("savings_percent", 0) for r in results) / len(results)
        total_json_tokens = sum(r.get("json_tokens", 0) for r in results)
        total_toon_tokens = sum(r.get("toon_tokens", 0) for r in results)
        
        print(f"\n📊 TOKEN METRICS:")
        print(f"   Total JSON Tokens:  {total_json_tokens}")
        print(f"   Total TOON Tokens:  {total_toon_tokens}")
        print(f"   Total Saved:        {total_json_tokens - total_toon_tokens}")
        print(f"   Average Savings:    {avg_savings:.1f}%")
        
        if avg_savings >= 30:
            print("\n   ✅ SUCCESS: Target savings achieved!")
        else:
            print("\n   ⚠️  WARNING: Below target savings")
    
    # Failed test details
    if failed_tests:
        print("\n" + "=" * 80)
        print("❌ FAILED TESTS")
        print("=" * 80)
        for test in failed_tests:
            print(f"\n• {test['question']}")
            if 'error' in test:
                print(f"  Error: {test['error']} ({test.get('stage', 'unknown')})")
    
    print("\n" + "=" * 80)
    print("🎯 RECOMMENDATIONS:")
    print("=" * 80)
    print("• Use tabular arrays [N,] for uniform objects (maximum savings)")
    print("• Quote strings only when necessary")
    print("• Keep nesting minimal")
    print("• Use compact key names")
    print("• Target: 30-60% token reduction")
    print("=" * 80 + "\n")
    
    # Exit with appropriate code
    sys.exit(0 if len(failed_tests) == 0 else 1)


if __name__ == "__main__":
    main()
