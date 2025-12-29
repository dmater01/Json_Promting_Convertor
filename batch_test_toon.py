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
