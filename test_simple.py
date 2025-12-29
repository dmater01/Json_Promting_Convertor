#!/usr/bin/env python3
"""Quick test script to verify TOON parser fixes."""

from toon_parser import ToonParser

def test_tabular():
    """Test tabular array."""
    print("Testing tabular array...")
    parser = ToonParser()
    
    data = {
        "users": [
            {"id": 1, "name": "Alice", "role": "admin"},
            {"id": 2, "name": "Bob", "role": "user"}
        ]
    }
    
    toon = parser.encode(data)
    print("Encoded:")
    print(toon)
    print()
    
    decoded = parser.decode(toon)
    print("Decoded:")
    print(decoded)
    print()
    
    if "users" in decoded and len(decoded["users"]) == 2:
        print("✅ PASS")
    else:
        print("❌ FAIL")
    print()

def test_primitive():
    """Test primitive array."""
    print("Testing primitive array...")
    parser = ToonParser()
    
    data = {
        "scores": [100, 95, 88]
    }
    
    toon = parser.encode(data)
    print("Encoded:")
    print(toon)
    print()
    
    decoded = parser.decode(toon)
    print("Decoded:")
    print(decoded)
    print()
    
    if "scores" in decoded and decoded["scores"] == [100, 95, 88]:
        print("✅ PASS")
    else:
        print("❌ FAIL")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("TOON PARSER QUICK TEST")
    print("=" * 60)
    print()
    
    test_tabular()
    test_primitive()
