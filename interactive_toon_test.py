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
