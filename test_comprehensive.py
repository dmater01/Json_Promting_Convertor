#!/usr/bin/env python3
"""Comprehensive TOON Parser Test - All Features"""

from toon_parser import ToonParser

print("=" * 70)
print(" " * 15 + "COMPREHENSIVE TOON PARSER TEST")
print("=" * 70)
print()

parser = ToonParser()
passed = 0
failed = 0

# Test 1: Simple Object
print("Test 1: Simple Object")
data1 = {"name": "Alice", "age": 28, "verified": True}
toon1 = parser.encode(data1)
decoded1 = parser.decode(toon1)
if decoded1 == data1:
    print("✅ PASS")
    passed += 1
else:
    print(f"❌ FAIL: {decoded1} != {data1}")
    failed += 1
print()

# Test 2: Tabular Array
print("Test 2: Tabular Array (Maximum Efficiency)")
data2 = {
    "users": [
        {"id": 1, "name": "Alice", "role": "admin"},
        {"id": 2, "name": "Bob", "role": "user"}
    ]
}
toon2 = parser.encode(data2)
decoded2 = parser.decode(toon2)
if decoded2 == data2:
    print("✅ PASS")
    passed += 1
else:
    print(f"❌ FAIL")
    print(f"Expected: {data2}")
    print(f"Got: {decoded2}")
    failed += 1
print()

# Test 3: Primitive Array
print("Test 3: Primitive Array")
data3 = {"scores": [100, 95, 88, 72], "tags": ["python", "async"]}
toon3 = parser.encode(data3)
decoded3 = parser.decode(toon3)
if decoded3 == data3:
    print("✅ PASS")
    passed += 1
else:
    print(f"❌ FAIL: {decoded3} != {data3}")
    failed += 1
print()

# Test 4: Nested Structure
print("Test 4: Nested Structure")
data4 = {
    "user": {
        "name": "Alice",
        "location": {
            "city": "San Francisco",
            "country": "USA"
        }
    },
    "permissions": {
        "roles": ["admin", "contributor"],
        "level": 5
    }
}
toon4 = parser.encode(data4)
decoded4 = parser.decode(toon4)
if decoded4 == data4:
    print("✅ PASS")
    passed += 1
else:
    print(f"❌ FAIL")
    print(f"Expected: {data4}")
    print(f"Got: {decoded4}")
    failed += 1
print()

# Test 5: Mixed Types
print("Test 5: Mixed Data Types")
data5 = {
    "string": "hello",
    "number": 42,
    "float": 3.14,
    "boolean": True,
    "null_value": None,
    "array": [1, 2, 3]
}
toon5 = parser.encode(data5)
decoded5 = parser.decode(toon5)
if decoded5 == data5:
    print("✅ PASS")
    passed += 1
else:
    print(f"❌ FAIL: {decoded5} != {data5}")
    failed += 1
print()

# Test 6: Empty Arrays
print("Test 6: Empty Arrays")
data6 = {"empty_list": [], "items": [{"id": 1}]}
toon6 = parser.encode(data6)
decoded6 = parser.decode(toon6)
# Check if decoded has the right structure
if "empty_list" in decoded6 and "items" in decoded6:
    print("✅ PASS")
    passed += 1
else:
    print(f"❌ FAIL: Missing keys in {decoded6}")
    failed += 1
print()

# Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Passed: {passed}/{passed + failed}")
print(f"Failed: {failed}/{passed + failed}")
print()

if failed == 0:
    print("🎉 ALL TESTS PASSED! Parser is working correctly.")
else:
    print(f"⚠️  {failed} test(s) failed. Review output above.")
print()
