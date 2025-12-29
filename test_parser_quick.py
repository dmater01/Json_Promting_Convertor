#!/usr/bin/env python3
"""
Quick test script to verify TOON parser fixes.
Run this to check that encoding and decoding work correctly.
"""

from toon_parser import ToonParser

def test_simple_object():
    """Test 1: Simple object encoding and decoding."""
    print("=" * 60)
    print("TEST 1: Simple Object")
    print("=" * 60)
    
    parser = ToonParser()
    data = {
        "name": "Alice",
        "email": "alice@example.com",
        "verified": True
    }
    
    toon = parser.encode(data)
    print("Encoded TOON:")
    print(toon)
    print()
    
    decoded = parser.decode(toon)
    print("Decoded back:")
    print(decoded)
    print()
    
    # Verify
    assert decoded == data, f"Mismatch! Expected {data}, got {decoded}"
    print("✅ PASS: Simple object round-trip successful")
    print()

def test_tabular_array():
    """Test 2: Tabular array encoding and decoding."""
    print("=" * 60)
    print("TEST 2: Tabular Array (Maximum Efficiency)")
    print("=" * 60)
    
    parser = ToonParser()
    data = {
        "users": [
            {"id": 1, "name": "Alice", "role": "admin"},
            {"id": 2, "name": "Bob", "role": "user"},
            {"id": 3, "name": "Charlie", "role": "guest"}
        ]
    }
    
    toon = parser.encode(data)
    print("Encoded TOON:")
    print(toon)
    print()
    
    decoded = parser.decode(toon)
    print("Decoded back:")
    print(decoded)
    print()
    
    # Verify
    assert "users" in decoded, "Missing 'users' key in decoded data"
    assert len(decoded["users"]) == 3, f"Expected 3 users, got {len(decoded['users'])}"
    assert decoded["users"][0]["name"] == "Alice", f"Expected Alice, got {decoded['users'][0]['name']}"
    print("✅ PASS: Tabular array round-trip successful")
    print()

def test_nested_structure():
    """Test 3: Nested structure with primitive array."""
    print("=" * 60)
    print("TEST 3: Nested Structure with Primitive Array")
    print("=" * 60)
    
    parser = ToonParser()
    data = {
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
    
    toon = parser.encode(data)
    print("Encoded TOON:")
    print(toon)
    print()
    
    decoded = parser.decode(toon)
    print("Decoded back:")
    print(decoded)
    print()
    
    # Verify
    assert "user" in decoded, "Missing 'user' key"
    assert decoded["user"]["name"] == "Alice", f"Expected Alice, got {decoded['user']['name']}"
    assert "permissions" in decoded, "Missing 'permissions' key"
    assert "roles" in decoded["permissions"], "Missing 'roles' key"
    assert isinstance(decoded["permissions"]["roles"], list), f"Expected list, got {type(decoded['permissions']['roles'])}"
    assert len(decoded["permissions"]["roles"]) == 2, f"Expected 2 roles, got {len(decoded['permissions']['roles'])}"
    assert decoded["permissions"]["level"] == 5, f"Expected level 5, got {decoded['permissions']['level']}"
    print("✅ PASS: Nested structure round-trip successful")
    print()

def test_mixed_arrays():
    """Test 4: Mixed array types."""
    print("=" * 60)
    print("TEST 4: Mixed Array Types")
    print("=" * 60)
    
    parser = ToonParser()
    data = {
        "primitive_array": [1, 2, 3, 4, 5],
        "string_array": ["apple", "banana", "cherry"],
        "tabular_data": [
            {"id": 1, "name": "Item A", "price": 9.99},
            {"id": 2, "name": "Item B", "price": 19.99}
        ]
    }
    
    toon = parser.encode(data)
    print("Encoded TOON:")
    print(toon)
    print()
    
    decoded = parser.decode(toon)
    print("Decoded back:")
    print(decoded)
    print()
    
    # Verify
    assert decoded["primitive_array"] == data["primitive_array"], "Primitive array mismatch"
    assert decoded["string_array"] == data["string_array"], "String array mismatch"
    assert len(decoded["tabular_data"]) == 2, f"Expected 2 items, got {len(decoded['tabular_data'])}"
    print("✅ PASS: Mixed arrays round-trip successful")
    print()

def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "TOON PARSER VERIFICATION" + " " * 19 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    all_passed = True
    
    try:
        test_simple_object()
    except AssertionError as e:
        print(f"❌ FAIL: {e}")
        all_passed = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        all_passed = False
    
    try:
        test_tabular_array()
    except AssertionError as e:
        print(f"❌ FAIL: {e}")
        all_passed = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        all_passed = False
    
    try:
        test_nested_structure()
    except AssertionError as e:
        print(f"❌ FAIL: {e}")
        all_passed = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        all_passed = False
    
    try:
        test_mixed_arrays()
    except AssertionError as e:
        print(f"❌ FAIL: {e}")
        all_passed = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        all_passed = False
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print()
        print("Your TOON parser is working correctly.")
        print("You can now use it for production applications.")
    else:
        print("❌ SOME TESTS FAILED")
        print()
        print("Please review the errors above.")
    print()

if __name__ == "__main__":
    main()
