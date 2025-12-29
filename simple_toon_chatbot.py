#!/usr/bin/env python3
"""
Simple Chatbot with TOON Format Integration

This example shows how to use TOON format in a chatbot to:
1. Save 30-60% tokens on LLM API calls
2. Reduce costs
3. Get structured responses efficiently

Usage:
    python simple_toon_chatbot.py
"""

import json
from typing import Dict, List, Any
from toon_parser import encode_to_toon
from json_vs_toon_comparison import estimate_savings


class SimpleToonChatbot:
    """
    A simple chatbot that uses TOON format for efficient LLM communication.
    """
    
    def __init__(self, use_toon: bool = True):
        """
        Initialize chatbot.
        
        Args:
            use_toon: If True, use TOON format. If False, use JSON.
        """
        self.use_toon = use_toon
        self.conversation_history = []
        self.total_tokens_saved = 0
        
    def create_system_prompt(self) -> str:
        """Create system prompt with TOON format instructions."""
        if not self.use_toon:
            return "You are a helpful assistant. Respond with structured JSON."
        
        return """You are a helpful assistant. Respond in TOON format (Token-Oriented Object Notation).

TOON FORMAT RULES:
1. Use key: value pairs (no braces)
2. Use indentation for nesting (2 spaces)
3. Arrays: [N] for length, [N,] for tabular
4. Quote strings only when necessary
5. No JSON braces {} or brackets []

Example TOON response:
response_type: answer
content: Here is my response
confidence: 0.95
follow_up_questions [2]: What else?, Tell me more?
"""
    
    def format_response(self, response_data: Dict[str, Any]) -> str:
        """
        Format response in chosen format (TOON or JSON).
        
        Args:
            response_data: Dictionary with response data
            
        Returns:
            Formatted response string
        """
        if self.use_toon:
            return encode_to_toon(response_data)
        else:
            return json.dumps(response_data, indent=2)
    
    def parse_user_message(self, message: str) -> Dict[str, Any]:
        """
        Parse user message and create structured response data.
        
        Args:
            message: User's input message
            
        Returns:
            Structured response dictionary
        """
        # Simple intent detection (in real chatbot, use NLP/LLM)
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            return {
                "response_type": "greeting",
                "message": "Hello! How can I help you today?",
                "suggested_actions": ["Ask a question", "Get help", "Start tutorial"],
                "confidence": 0.98
            }
        
        elif any(word in message_lower for word in ["help", "support", "assist"]):
            return {
                "response_type": "help",
                "message": "I'm here to help! What do you need assistance with?",
                "help_topics": [
                    {"topic": "Getting Started", "id": 1},
                    {"topic": "Advanced Features", "id": 2},
                    {"topic": "Troubleshooting", "id": 3}
                ],
                "confidence": 0.92
            }
        
        elif "?" in message:
            return {
                "response_type": "answer",
                "question": message,
                "answer": "That's a great question! Let me help you with that.",
                "sources": ["Knowledge Base", "Documentation"],
                "confidence": 0.85,
                "related_topics": ["topic1", "topic2"]
            }
        
        else:
            return {
                "response_type": "general",
                "message": "I understand. Tell me more about that.",
                "sentiment": "neutral",
                "confidence": 0.75
            }
    
    def chat(self, user_message: str) -> Dict[str, Any]:
        """
        Process user message and generate response.
        
        Args:
            user_message: User's input
            
        Returns:
            Dictionary with response and metrics
        """
        # Parse message and create response data
        response_data = self.parse_user_message(user_message)
        
        # Format in chosen format
        formatted_response = self.format_response(response_data)
        
        # Calculate metrics
        metrics = estimate_savings(response_data)
        self.total_tokens_saved += metrics['savings']
        
        # Store in history
        self.conversation_history.append({
            "user": user_message,
            "response": formatted_response,
            "format": "TOON" if self.use_toon else "JSON",
            "tokens": metrics['toon_tokens'] if self.use_toon else metrics['json_tokens']
        })
        
        return {
            "response": formatted_response,
            "metrics": metrics,
            "format": "TOON" if self.use_toon else "JSON"
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get conversation statistics."""
        total_messages = len(self.conversation_history)
        total_tokens = sum(msg['tokens'] for msg in self.conversation_history)
        
        return {
            "total_messages": total_messages,
            "total_tokens": total_tokens,
            "tokens_saved": self.total_tokens_saved if self.use_toon else 0,
            "format": "TOON" if self.use_toon else "JSON"
        }


def demo_conversation():
    """Run a demo conversation comparing JSON vs TOON."""
    
    print("=" * 80)
    print("🤖 SIMPLE CHATBOT WITH TOON FORMAT")
    print("=" * 80)
    print()
    
    # Test messages
    test_messages = [
        "Hello!",
        "I need help with something",
        "What is machine learning?",
        "Thanks for your help"
    ]
    
    # Run with TOON
    print("\n📊 TEST 1: Using TOON Format")
    print("=" * 80)
    toon_bot = SimpleToonChatbot(use_toon=True)
    
    for msg in test_messages:
        print(f"\n👤 User: {msg}")
        result = toon_bot.chat(msg)
        print(f"\n🤖 Bot (TOON format):")
        print(result['response'])
        print(f"\n📈 Tokens: {result['metrics']['toon_tokens']}")
    
    toon_stats = toon_bot.get_stats()
    
    # Run with JSON
    print("\n\n📊 TEST 2: Using JSON Format")
    print("=" * 80)
    json_bot = SimpleToonChatbot(use_toon=False)
    
    for msg in test_messages:
        print(f"\n👤 User: {msg}")
        result = json_bot.chat(msg)
        print(f"\n🤖 Bot (JSON format):")
        print(result['response'])
        print(f"\n📈 Tokens: {result['metrics']['json_tokens']}")
    
    json_stats = json_bot.get_stats()
    
    # Compare results
    print("\n\n" + "=" * 80)
    print("📊 COMPARISON RESULTS")
    print("=" * 80)
    print(f"\nFormat       Messages    Total Tokens")
    print("-" * 80)
    print(f"JSON         {json_stats['total_messages']:>8}    {json_stats['total_tokens']:>12}")
    print(f"TOON         {toon_stats['total_messages']:>8}    {toon_stats['total_tokens']:>12}")
    print("-" * 80)
    
    tokens_saved = json_stats['total_tokens'] - toon_stats['total_tokens']
    savings_percent = (tokens_saved / json_stats['total_tokens']) * 100
    
    print(f"Saved                     {tokens_saved:>12} ({savings_percent:.1f}%)")
    print("=" * 80)
    
    # Cost calculation
    print("\n💰 COST IMPACT (at $0.03 per 1K tokens)")
    print("-" * 80)
    json_cost = (json_stats['total_tokens'] / 1000) * 0.03
    toon_cost = (toon_stats['total_tokens'] / 1000) * 0.03
    
    print(f"JSON cost:  ${json_cost:.4f}")
    print(f"TOON cost:  ${toon_cost:.4f}")
    print(f"Savings:    ${json_cost - toon_cost:.4f}")
    
    # Scale to 100K messages
    print("\n📈 SCALED TO 100K MESSAGES:")
    scale_factor = 100000 / json_stats['total_messages']
    scaled_json_cost = json_cost * scale_factor
    scaled_toon_cost = toon_cost * scale_factor
    scaled_savings = scaled_json_cost - scaled_toon_cost
    
    print(f"JSON cost:  ${scaled_json_cost:,.2f}")
    print(f"TOON cost:  ${scaled_toon_cost:,.2f}")
    print(f"💰 Savings: ${scaled_savings:,.2f}/month")
    print(f"💰 Annual:  ${scaled_savings * 12:,.2f}/year")
    print("=" * 80)


def interactive_chatbot():
    """Run interactive chatbot session."""
    
    print("\n" + "=" * 80)
    print("🤖 INTERACTIVE TOON CHATBOT")
    print("=" * 80)
    print("\nCommands:")
    print("  • Type your message to chat")
    print("  • Type 'stats' to see statistics")
    print("  • Type 'json' to switch to JSON format")
    print("  • Type 'toon' to switch to TOON format")
    print("  • Type 'quit' to exit")
    print("=" * 80 + "\n")
    
    bot = SimpleToonChatbot(use_toon=True)
    
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'quit':
                print("\n👋 Thanks for chatting! Goodbye!")
                break
            
            elif user_input.lower() == 'stats':
                stats = bot.get_stats()
                print(f"\n📊 Conversation Statistics:")
                print(f"   Messages: {stats['total_messages']}")
                print(f"   Tokens: {stats['total_tokens']}")
                print(f"   Format: {stats['format']}")
                if bot.use_toon:
                    print(f"   Tokens Saved: {stats['tokens_saved']} ({(stats['tokens_saved']/(stats['total_tokens']+stats['tokens_saved'])*100):.1f}%)")
                print()
                continue
            
            elif user_input.lower() == 'json':
                bot.use_toon = False
                print("✅ Switched to JSON format\n")
                continue
            
            elif user_input.lower() == 'toon':
                bot.use_toon = True
                print("✅ Switched to TOON format\n")
                continue
            
            # Process message
            result = bot.chat(user_input)
            
            print(f"\n🤖 Bot ({result['format']}):")
            print(result['response'])
            print(f"\n📊 Tokens: {result['metrics']['toon_tokens'] if bot.use_toon else result['metrics']['json_tokens']}")
            if bot.use_toon:
                print(f"💰 Saved: {result['metrics']['savings']} tokens ({result['metrics']['savings_percent']:.1f}%)")
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def main():
    """Main function with menu."""
    
    print("\n" + "=" * 80)
    print("🤖 SIMPLE TOON CHATBOT - DEMO")
    print("=" * 80)
    print("\nChoose an option:")
    print("  1. Run demo conversation (automated)")
    print("  2. Interactive chatbot session")
    print("  3. Both")
    print("=" * 80)
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        demo_conversation()
    elif choice == "2":
        interactive_chatbot()
    elif choice == "3":
        demo_conversation()
        input("\nPress Enter to start interactive session...")
        interactive_chatbot()
    else:
        print("Invalid choice. Running demo...")
        demo_conversation()


if __name__ == "__main__":
    main()
