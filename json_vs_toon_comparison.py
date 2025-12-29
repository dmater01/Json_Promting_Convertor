"""
JSON vs TOON Comparison Tool

Compare token usage between JSON and TOON formats.
Provides utilities to measure actual token savings.
"""

import json
from typing import Any, Dict
from toon_parser import encode_to_toon


def count_tokens(text: str, encoding: str = "gpt2") -> int:
    """
    Count tokens in text string.
    
    Uses rough approximation: 1 token ≈ 4 characters
    For production, use tiktoken library for accurate counts.
    
    Args:
        text: Text to count tokens for
        encoding: Token encoding (ignored in this approximation)
    
    Returns:
        Approximate token count
    """
    # Simple approximation: ~4 chars per token
    # This matches well with GPT models for structured data
    return max(1, len(text) // 4)


def estimate_savings(data: Any, encoding: str = "gpt2") -> Dict[str, Any]:
    """
    Compare token usage: JSON vs TOON.
    
    Args:
        data: Python dict or list to compare
        encoding: Token encoding to use
    
    Returns:
        Dictionary with comparison metrics:
        - json_tokens: Token count for JSON
        - toon_tokens: Token count for TOON
        - savings: Absolute token savings
        - savings_percent: Percentage savings
    """
    # Generate both formats
    json_str = json.dumps(data, indent=2)
    toon_str = encode_to_toon(data)
    
    # Count tokens
    json_tokens = count_tokens(json_str)
    toon_tokens = count_tokens(toon_str)
    
    # Calculate savings
    savings = json_tokens - toon_tokens
    savings_percent = (savings / json_tokens * 100) if json_tokens > 0 else 0
    
    return {
        "json_tokens": json_tokens,
        "toon_tokens": toon_tokens,
        "savings": savings,
        "savings_percent": savings_percent,
        "json_chars": len(json_str),
        "toon_chars": len(toon_str)
    }


def compare_formats(data: Any, encoding: str = "gpt2") -> str:
    """
    Generate formatted comparison table.
    
    Args:
        data: Python dict or list to compare
        encoding: Token encoding to use
    
    Returns:
        Formatted string with comparison table
    """
    metrics = estimate_savings(data, encoding)
    
    output = []
    output.append("=" * 80)
    output.append("TOKEN COMPARISON: JSON vs TOON")
    output.append("=" * 80)
    output.append("")
    output.append(f"Format          Characters    Tokens    ")
    output.append("-" * 80)
    output.append(f"JSON            {metrics['json_chars']:>10}    {metrics['json_tokens']:>6}")
    output.append(f"TOON            {metrics['toon_chars']:>10}    {metrics['toon_tokens']:>6}")
    output.append("-" * 80)
    output.append(f"Savings         {metrics['json_chars'] - metrics['toon_chars']:>10}    {metrics['savings']:>6}")
    output.append(f"Percentage      {((metrics['json_chars'] - metrics['toon_chars']) / metrics['json_chars'] * 100):>9.1f}%    {metrics['savings_percent']:>5.1f}%")
    output.append("=" * 80)
    
    if metrics['savings_percent'] >= 50:
        output.append("✅ EXCELLENT: >50% token savings!")
    elif metrics['savings_percent'] >= 30:
        output.append("✅ GOOD: Target savings achieved (30-60%)")
    elif metrics['savings_percent'] >= 20:
        output.append("⚠️  OK: Below target but still saving")
    else:
        output.append("⚠️  LOW: Consider using tabular arrays")
    
    output.append("=" * 80)
    
    return "\n".join(output)


def detailed_comparison(data: Any) -> None:
    """
    Print detailed side-by-side comparison.
    
    Args:
        data: Python dict or list to compare
    """
    json_str = json.dumps(data, indent=2)
    toon_str = encode_to_toon(data)
    
    print("\n" + "=" * 80)
    print("DETAILED COMPARISON")
    print("=" * 80)
    
    print("\n📄 JSON FORMAT:")
    print("-" * 80)
    print(json_str)
    
    print("\n📄 TOON FORMAT:")
    print("-" * 80)
    print(toon_str)
    
    print("\n" + compare_formats(data))


# Example usage
if __name__ == "__main__":
    print("🚀 JSON vs TOON Comparison Tool\n")
    
    # Example 1: Simple config
    print("\n1️⃣ Example: Simple Configuration")
    example1 = {
        "server": {
            "host": "localhost",
            "port": 8000,
            "debug": True
        },
        "database": {
            "name": "mydb",
            "user": "admin"
        }
    }
    detailed_comparison(example1)
    
    # Example 2: User list (tabular)
    print("\n\n2️⃣ Example: User List (Tabular Array)")
    example2 = {
        "users": [
            {"id": 1, "name": "Alice", "role": "admin"},
            {"id": 2, "name": "Bob", "role": "user"},
            {"id": 3, "name": "Charlie", "role": "guest"}
        ]
    }
    detailed_comparison(example2)
    
    # Example 3: Mixed data
    print("\n\n3️⃣ Example: Mixed Structure")
    example3 = {
        "intent": "extract",
        "subject": "contacts",
        "entities": {
            "contacts": [
                {"name": "John", "email": "john@example.com", "phone": "555-1234"},
                {"name": "Sarah", "email": "sarah@example.com", "phone": "555-5678"}
            ]
        },
        "confidence": 0.95
    }
    detailed_comparison(example3)
    
    print("\n" + "=" * 80)
    print("💡 KEY TAKEAWAY: Tabular arrays provide maximum token savings!")
    print("=" * 80)
