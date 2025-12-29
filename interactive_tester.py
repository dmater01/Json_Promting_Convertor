#!/usr/bin/env python3
"""
Interactive TOON Tester - Test your own questions!

Usage:
    python interactive_tester.py
"""

import json


def encode_to_toon(data, indent=2):
    """Convert Python dict to TOON format string."""
    lines = []
    
    def format_value(value, level=0):
        prefix = "  " * level
        
        if isinstance(value, dict):
            for key, val in value.items():
                if isinstance(val, dict):
                    lines.append(f"{prefix}{key}:")
                    format_value(val, level + 1)
                elif isinstance(val, list) and val and isinstance(val[0], dict):
                    # Tabular array - maximum efficiency!
                    lines.append(f"{prefix}{key} [{len(val)},]")
                    keys = list(val[0].keys())
                    lines.append(f"{prefix}  {', '.join(keys)}")
                    for item in val:
                        values = [str(item[k]) for k in keys]
                        lines.append(f"{prefix}  {', '.join(values)}")
                elif isinstance(val, list):
                    # Primitive array
                    lines.append(f"{prefix}{key} [{len(val)}]: {', '.join(map(str, val))}")
                else:
                    # Simple value
                    lines.append(f"{prefix}{key}: {val}")
        
        return "\n".join(lines)
    
    format_value(data)
    return "\n".join(lines)


def count_tokens(text):
    """Approximate token count (1 token ≈ 4 characters)."""
    return len(text) // 4


def compare_formats(data):
    """Compare JSON vs TOON token usage."""
    json_str = json.dumps(data, indent=2)
    toon_str = encode_to_toon(data)
    
    json_tokens = count_tokens(json_str)
    toon_tokens = count_tokens(toon_str)
    
    savings = (1 - toon_tokens / json_tokens) * 100
    
    return {
        "json_str": json_str,
        "toon_str": toon_str,
        "json_tokens": json_tokens,
        "toon_tokens": toon_tokens,
        "savings_percent": savings,
        "tokens_saved": json_tokens - toon_tokens
    }


def print_banner():
    """Print welcome banner."""
    print("\n" + "=" * 80)
    print("🎯 INTERACTIVE TOON TESTER")
    print("=" * 80)
    print("\nTest your own JSON data and see the TOON conversion!")
    print("\nCommands:")
    print("  • Type JSON data to test conversion")
    print("  • Type 'example' to see sample data")
    print("  • Type 'help' for tips")
    print("  • Type 'quit' to exit")
    print("=" * 80 + "\n")


def show_example():
    """Show example JSON data."""
    example = {
        "intent": "extract",
        "subject": "contacts",
        "entities": {
            "contacts": [
                {"name": "Alice", "email": "alice@example.com", "phone": "555-0001"},
                {"name": "Bob", "email": "bob@example.com", "phone": "555-0002"}
            ]
        },
        "output_format": "tabular",
        "original_language": "en",
        "confidence_score": 0.95
    }
    
    print("\n📋 Example JSON:")
    print(json.dumps(example, indent=2))
    print("\n💡 Copy and paste this to test!")


def show_help():
    """Show helpful tips."""
    print("\n💡 TIPS FOR MAXIMUM TOKEN SAVINGS:")
    print("=" * 80)
    print("\n✅ DO:")
    print("  • Use arrays of uniform objects (tabular arrays save 60%+)")
    print("  • Keep string values simple (unquoted saves tokens)")
    print("  • Use short key names")
    print("  • Minimize nesting depth")
    print("\n❌ DON'T:")
    print("  • Use deeply nested structures")
    print("  • Use verbose key names")
    print("  • Mix different object structures in arrays")
    print("\n🎯 TARGET: 30-60% token reduction vs JSON")
    print("=" * 80 + "\n")


def test_input(data_str):
    """Test user input."""
    try:
        # Parse JSON
        data = json.loads(data_str)
        
        print("\n" + "=" * 80)
        print("🔍 TESTING YOUR INPUT")
        print("=" * 80)
        
        # Compare formats
        comparison = compare_formats(data)
        
        print("\n1️⃣  JSON FORMAT:")
        print(comparison["json_str"])
        print(f"\n   Size: {len(comparison['json_str'])} chars")
        print(f"   Tokens: ~{comparison['json_tokens']}")
        
        print("\n2️⃣  TOON FORMAT:")
        print(comparison["toon_str"])
        print(f"\n   Size: {len(comparison['toon_str'])} chars")
        print(f"   Tokens: ~{comparison['toon_tokens']}")
        
        print("\n3️⃣  SAVINGS:")
        char_savings = (1 - len(comparison['toon_str']) / len(comparison['json_str'])) * 100
        print(f"   Character reduction: {char_savings:.1f}%")
        print(f"   Token reduction: {comparison['savings_percent']:.1f}%")
        print(f"   Tokens saved: {comparison['tokens_saved']}")
        
        # Evaluation
        if comparison['savings_percent'] >= 50:
            print("\n   ✅ EXCELLENT: >50% savings!")
        elif comparison['savings_percent'] >= 30:
            print("\n   ✅ GOOD: Target savings achieved (30-60%)")
        elif comparison['savings_percent'] >= 20:
            print("\n   ⚠️  OK: Below target but still saving tokens")
        else:
            print("\n   ⚠️  LOW: Consider using tabular arrays for better savings")
        
        print("\n" + "=" * 80 + "\n")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"\n❌ Invalid JSON: {e}")
        print("💡 Tip: Make sure to use double quotes for strings")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def main():
    """Main interactive loop."""
    print_banner()
    
    while True:
        try:
            print("📝 Enter JSON (or command):")
            user_input = input("> ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() == 'quit':
                print("\n👋 Thanks for testing TOON format!")
                break
            
            elif user_input.lower() == 'example':
                show_example()
            
            elif user_input.lower() == 'help':
                show_help()
            
            else:
                # Test the input
                test_input(user_input)
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
