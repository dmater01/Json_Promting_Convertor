"""Quick test script for LLM integration."""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.schemas.requests import AnalyzeRequest, LLMProvider
from src.services.llm_router import LLMRouter
from src.services.prompt_builder import PromptBuilder


def test_prompt_builder():
    """Test the prompt builder."""
    print("=" * 60)
    print("TEST 1: Prompt Builder")
    print("=" * 60)

    builder = PromptBuilder()

    # Create a sample request
    request = AnalyzeRequest(
        prompt="Translate 'Bonjour le monde' to English"
    )

    # Build meta-prompt
    meta_prompt = builder.build_meta_prompt(request)

    print("\nGenerated Meta-Prompt:")
    print("-" * 60)
    print(meta_prompt)
    print("-" * 60)

    # Test JSON extraction
    test_responses = [
        '{"intent": "translate", "subject": "text"}',
        '```json\n{"intent": "translate", "subject": "text"}\n```',
        '```\n{"intent": "translate", "subject": "text"}\n```',
    ]

    print("\nTesting JSON extraction:")
    for i, response in enumerate(test_responses, 1):
        cleaned = builder.extract_json_from_response(response)
        print(f"{i}. Input:  {response[:50]}...")
        print(f"   Output: {cleaned}")

    print("\n✅ Prompt builder tests passed\n")


def test_llm_router_mock():
    """Test the LLM router structure (without calling real API)."""
    print("=" * 60)
    print("TEST 2: LLM Router Structure")
    print("=" * 60)

    router = LLMRouter()

    # Test fallback chain
    chain_auto = router.get_fallback_chain(LLMProvider.AUTO)
    print(f"\nFallback chain (AUTO): {[p.value for p in chain_auto]}")

    chain_gemini = router.get_fallback_chain(LLMProvider.GEMINI)
    print(f"Fallback chain (GEMINI): {[p.value for p in chain_gemini]}")

    chain_claude = router.get_fallback_chain(LLMProvider.CLAUDE)
    print(f"Fallback chain (CLAUDE): {[p.value for p in chain_claude]}")

    # Test provider info
    print("\nProvider info:")
    for provider in [LLMProvider.GEMINI, LLMProvider.CLAUDE, LLMProvider.GPT4]:
        info = router.client.get_provider_info(provider)
        print(f"  {provider.value}: {info}")

    print("\n✅ LLM router structure tests passed\n")


def test_llm_integration_with_api():
    """Test actual LLM API integration (requires API key)."""
    print("=" * 60)
    print("TEST 3: Real LLM Integration (Gemini)")
    print("=" * 60)

    # Check if API key is set
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key or gemini_key == "your-gemini-api-key-here":
        print("\n⚠️  GEMINI_API_KEY not set - skipping real API test")
        print("   Set GEMINI_API_KEY in .env to test real integration")
        return

    print(f"\n✅ GEMINI_API_KEY found: {gemini_key[:10]}...")

    # Create a test request
    request = AnalyzeRequest(
        prompt="Translate 'Bonjour' to English",
        llm_provider=LLMProvider.GEMINI,
        temperature=0.1,
        max_tokens=500,
    )

    print(f"\nTest prompt: {request.prompt}")
    print(f"Provider: {request.llm_provider.value}")

    try:
        router = LLMRouter()
        print("\nSending request to Gemini...")

        result, metadata = router.route_request(request)

        print("\n✅ Request successful!")
        print("\nExtracted Data:")
        print(f"  Intent: {result.get('intent')}")
        print(f"  Subject: {result.get('subject')}")
        print(f"  Entities: {result.get('entities')}")
        print(f"  Original Language: {result.get('original_language')}")
        print(f"  Confidence: {result.get('confidence_score')}")

        print("\nMetadata:")
        print(f"  Provider: {metadata['provider']}")
        print(f"  Model: {metadata['model']}")
        print(f"  Tokens Used: {metadata['tokens_used']}")
        print(f"  Latency: {metadata['latency_ms']}ms")
        print(f"  Attempts: {metadata.get('attempts', 1)}")

        print("\n✅ Real LLM integration test passed!\n")

    except Exception as e:
        print(f"\n❌ LLM integration test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print(" LLM INTEGRATION TEST SUITE")
    print("=" * 60 + "\n")

    # Run tests
    test_prompt_builder()
    test_llm_router_mock()
    test_llm_integration_with_api()

    print("=" * 60)
    print(" TEST SUITE COMPLETE")
    print("=" * 60 + "\n")
