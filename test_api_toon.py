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
