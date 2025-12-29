#!/usr/bin/env python3
"""
Advanced TOON Chatbot with LLM API Integration

Shows how to integrate TOON format with:
- OpenAI API
- Anthropic Claude API
- Token savings tracking
- Real-world structured responses

Usage:
    export OPENAI_API_KEY="your-key"
    python llm_toon_chatbot.py
"""

import json
import os
from typing import Dict, List, Any, Optional
from toon_parser import encode_to_toon
from json_vs_toon_comparison import estimate_savings


class LLMToonChatbot:
    """
    Advanced chatbot using TOON format with LLM APIs.
    """
    
    def __init__(self, provider: str = "mock", use_toon: bool = True):
        """
        Initialize LLM chatbot.
        
        Args:
            provider: "openai", "anthropic", or "mock"
            use_toon: Use TOON format for structured responses
        """
        self.provider = provider
        self.use_toon = use_toon
        self.conversation_history = []
        self.total_tokens_used = 0
        self.total_tokens_saved = 0
        
        # Initialize API client (mock for this example)
        self.client = None
        if provider == "openai":
            # import openai
            # self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            pass
        elif provider == "anthropic":
            # import anthropic
            # self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            pass
    
    def create_system_prompt_with_toon(self) -> str:
        """Create system prompt that instructs LLM to use TOON format."""
        
        if not self.use_toon:
            return """You are a helpful assistant. Always respond with structured data in JSON format.

Example JSON response:
{
  "response_type": "answer",
  "content": "Your answer here",
  "confidence": 0.95,
  "sources": ["source1", "source2"]
}"""
        
        return """You are a helpful assistant. Always respond with structured data in TOON format.

TOON FORMAT RULES:
1. Use key: value pairs (no JSON braces {})
2. Use 2-space indentation for nested objects
3. Arrays: [N] for length indicator
4. Tabular arrays [N,] for uniform objects (MAXIMUM EFFICIENCY!)
5. Quote strings only when necessary
6. No JSON braces or brackets

Example TOON response:
response_type: answer
content: Your answer here
confidence: 0.95
sources [2]: source1, source2

For lists of uniform objects, use tabular arrays:
contacts [2,]
  name, email, role
  Alice, alice@example.com, admin
  Bob, bob@example.com, user

ALWAYS use TOON format. NEVER use JSON format."""
    
    def build_messages(self, user_message: str) -> List[Dict[str, str]]:
        """
        Build message history for LLM API call.
        
        Args:
            user_message: Current user message
            
        Returns:
            List of message dictionaries for API
        """
        messages = [
            {"role": "system", "content": self.create_system_prompt_with_toon()}
        ]
        
        # Add conversation history (last 5 exchanges)
        for entry in self.conversation_history[-5:]:
            messages.append({"role": "user", "content": entry['user_message']})
            messages.append({"role": "assistant", "content": entry['assistant_response']})
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def call_llm(self, messages: List[Dict[str, str]]) -> str:
        """
        Call LLM API.
        
        Args:
            messages: Conversation messages
            
        Returns:
            LLM response string
        """
        if self.provider == "openai" and self.client:
            # Real OpenAI call
            # response = self.client.chat.completions.create(
            #     model="gpt-4",
            #     messages=messages,
            #     temperature=0.7
            # )
            # return response.choices[0].message.content
            pass
        
        elif self.provider == "anthropic" and self.client:
            # Real Anthropic call
            # response = self.client.messages.create(
            #     model="claude-3-sonnet-20240229",
            #     messages=messages[1:],  # Skip system message
            #     system=messages[0]["content"],
            #     max_tokens=1024
            # )
            # return response.content[0].text
            pass
        
        # Mock response for demonstration
        return self._mock_llm_response(messages[-1]["content"])
    
    def _mock_llm_response(self, user_message: str) -> str:
        """Generate mock LLM response in chosen format."""
        
        # Determine response type
        message_lower = user_message.lower()
        
        if "search" in message_lower or "find" in message_lower:
            response_data = {
                "response_type": "search_results",
                "query": user_message,
                "results": [
                    {
                        "title": "Result 1",
                        "url": "https://example.com/1",
                        "snippet": "This is the first result",
                        "relevance": 0.95
                    },
                    {
                        "title": "Result 2",
                        "url": "https://example.com/2",
                        "snippet": "This is the second result",
                        "relevance": 0.88
                    }
                ],
                "total_results": 2,
                "confidence": 0.92
            }
        
        elif "recommend" in message_lower or "suggest" in message_lower:
            response_data = {
                "response_type": "recommendations",
                "items": [
                    {"name": "Option A", "score": 0.95, "reason": "Best fit"},
                    {"name": "Option B", "score": 0.88, "reason": "Good alternative"},
                    {"name": "Option C", "score": 0.75, "reason": "Budget option"}
                ],
                "criteria": ["quality", "price", "availability"],
                "confidence": 0.90
            }
        
        elif "analyze" in message_lower:
            response_data = {
                "response_type": "analysis",
                "subject": user_message,
                "findings": {
                    "sentiment": "positive",
                    "key_points": ["point1", "point2", "point3"],
                    "confidence": 0.87
                },
                "metrics": {
                    "relevance": 0.92,
                    "complexity": "medium"
                }
            }
        
        else:
            response_data = {
                "response_type": "general_answer",
                "content": f"I understand you're asking about: {user_message}",
                "helpful": True,
                "follow_up_questions": [
                    "Would you like more details?",
                    "Should I explain further?"
                ],
                "confidence": 0.85
            }
        
        # Format response
        if self.use_toon:
            return encode_to_toon(response_data)
        else:
            return json.dumps(response_data, indent=2)
    
    def chat(self, user_message: str) -> Dict[str, Any]:
        """
        Process chat message.
        
        Args:
            user_message: User's input
            
        Returns:
            Response with metrics
        """
        # Build messages for LLM
        messages = self.build_messages(user_message)
        
        # Get LLM response
        llm_response = self.call_llm(messages)
        
        # Parse response to get data (for metrics calculation)
        # In real implementation, you'd parse the TOON/JSON response
        # For now, use mock data
        response_data = {
            "response_type": "general",
            "content": llm_response
        }
        
        # Calculate metrics
        metrics = estimate_savings(response_data)
        tokens_used = metrics['toon_tokens'] if self.use_toon else metrics['json_tokens']
        
        self.total_tokens_used += tokens_used
        if self.use_toon:
            self.total_tokens_saved += metrics['savings']
        
        # Store in history
        self.conversation_history.append({
            "user_message": user_message,
            "assistant_response": llm_response,
            "tokens": tokens_used
        })
        
        return {
            "response": llm_response,
            "tokens_used": tokens_used,
            "tokens_saved": metrics['savings'] if self.use_toon else 0,
            "savings_percent": metrics['savings_percent'] if self.use_toon else 0
        }
    
    def get_total_stats(self) -> Dict[str, Any]:
        """Get cumulative statistics."""
        return {
            "total_messages": len(self.conversation_history),
            "total_tokens_used": self.total_tokens_used,
            "total_tokens_saved": self.total_tokens_saved,
            "format": "TOON" if self.use_toon else "JSON",
            "provider": self.provider
        }


def demo_llm_chatbot():
    """Demonstrate LLM chatbot with TOON format."""
    
    print("=" * 80)
    print("🤖 LLM CHATBOT WITH TOON FORMAT")
    print("=" * 80)
    print()
    
    # Test queries
    test_queries = [
        "Search for information about machine learning",
        "Recommend some good books about AI",
        "Analyze the sentiment of this review: Great product!",
        "What is the weather like today?"
    ]
    
    # Test with TOON
    print("📊 TEST 1: Using TOON Format")
    print("=" * 80)
    
    toon_bot = LLMToonChatbot(provider="mock", use_toon=True)
    
    for query in test_queries:
        print(f"\n👤 User: {query}")
        result = toon_bot.chat(query)
        print(f"\n🤖 Bot Response (TOON):")
        print(result['response'])
        print(f"\n📊 Tokens: {result['tokens_used']}")
        print(f"💰 Saved: {result['tokens_saved']} ({result['savings_percent']:.1f}%)")
        print("-" * 80)
    
    toon_stats = toon_bot.get_total_stats()
    
    # Test with JSON
    print("\n\n📊 TEST 2: Using JSON Format")
    print("=" * 80)
    
    json_bot = LLMToonChatbot(provider="mock", use_toon=False)
    
    for query in test_queries:
        print(f"\n👤 User: {query}")
        result = json_bot.chat(query)
        print(f"\n🤖 Bot Response (JSON):")
        print(result['response'][:300] + "..." if len(result['response']) > 300 else result['response'])
        print(f"\n📊 Tokens: {result['tokens_used']}")
        print("-" * 80)
    
    json_stats = json_bot.get_total_stats()
    
    # Summary
    print("\n\n" + "=" * 80)
    print("📊 FINAL COMPARISON")
    print("=" * 80)
    print(f"\nFormat    Messages    Tokens Used    Tokens Saved    Savings %")
    print("-" * 80)
    print(f"JSON      {json_stats['total_messages']:>8}    {json_stats['total_tokens_used']:>11}    {json_stats['total_tokens_saved']:>12}    {'N/A':>9}")
    print(f"TOON      {toon_stats['total_messages']:>8}    {toon_stats['total_tokens_used']:>11}    {toon_stats['total_tokens_saved']:>12}    {(toon_stats['total_tokens_saved']/(toon_stats['total_tokens_used']+toon_stats['total_tokens_saved'])*100):>8.1f}%")
    print("=" * 80)
    
    # Cost analysis
    cost_per_1k = 0.03  # Example: GPT-4 pricing
    json_cost = (json_stats['total_tokens_used'] / 1000) * cost_per_1k
    toon_cost = (toon_stats['total_tokens_used'] / 1000) * cost_per_1k
    
    print(f"\n💰 COST COMPARISON (at ${cost_per_1k} per 1K tokens):")
    print(f"   JSON: ${json_cost:.6f}")
    print(f"   TOON: ${toon_cost:.6f}")
    print(f"   Savings: ${json_cost - toon_cost:.6f} ({((json_cost-toon_cost)/json_cost*100):.1f}%)")
    
    # Scale up
    print(f"\n📈 SCALED TO 1 MILLION MESSAGES:")
    scale = 1_000_000 / json_stats['total_messages']
    scaled_json_cost = json_cost * scale
    scaled_toon_cost = toon_cost * scale
    print(f"   JSON: ${scaled_json_cost:,.2f}")
    print(f"   TOON: ${scaled_toon_cost:,.2f}")
    print(f"   💰 Annual Savings: ${(scaled_json_cost - scaled_toon_cost):,.2f}")
    print("=" * 80)


if __name__ == "__main__":
    demo_llm_chatbot()
