#!/usr/bin/env python3
"""
Enhanced TOON Chatbot - Standalone Version
No external dependencies needed for mock mode!
"""

import json
from typing import Dict, Any, List


# ============================================================================
# INLINE TOON PARSER (No external imports needed!)
# ============================================================================

def encode_to_toon(data: Any, indent: int = 2) -> str:
    """Convert Python dict to TOON format."""
    lines = []
    
    def format_value(value: Any, level: int = 0):
        prefix = " " * (indent * level)
        
        if isinstance(value, dict):
            for key, val in value.items():
                if isinstance(val, dict):
                    lines.append(f"{prefix}{key}:")
                    format_value(val, level + 1)
                elif isinstance(val, list) and val and isinstance(val[0], dict):
                    # Tabular array
                    lines.append(f"{prefix}{key} [{len(val)},]")
                    keys = list(val[0].keys())
                    lines.append(f"{prefix}{' ' * indent}{', '.join(keys)}")
                    for item in val:
                        values = [str(item[k]) for k in keys]
                        lines.append(f"{prefix}{' ' * indent}{', '.join(values)}")
                elif isinstance(val, list):
                    # Primitive array
                    lines.append(f"{prefix}{key} [{len(val)}]: {', '.join(map(str, val))}")
                else:
                    # Simple value
                    val_str = "true" if val is True else "false" if val is False else "null" if val is None else str(val)
                    lines.append(f"{prefix}{key}: {val_str}")
    
    format_value(data)
    return "\n".join(lines)


def count_tokens(text: str) -> int:
    """Approximate token count."""
    return len(text) // 4


def estimate_savings(data: Any) -> Dict[str, int]:
    """Calculate token savings."""
    json_str = json.dumps(data, indent=2)
    toon_str = encode_to_toon(data)
    
    json_tokens = count_tokens(json_str)
    toon_tokens = count_tokens(toon_str)
    
    return {
        'json_tokens': json_tokens,
        'toon_tokens': toon_tokens,
        'savings': json_tokens - toon_tokens,
        'savings_percent': ((json_tokens - toon_tokens) / json_tokens * 100) if json_tokens > 0 else 0
    }


# ============================================================================
# ENHANCED CHATBOT
# ============================================================================

class EnhancedToonChatbot:
    """Enhanced chatbot with smart responses and TOON format."""
    
    def __init__(self):
        self.conversation_history = []
        self.total_tokens_saved = 0
    
    def chat(self, user_message: str) -> Dict[str, Any]:
        """Process user message and generate smart response."""
        message_lower = user_message.lower()
        
        # Question detection
        if "?" in user_message or any(word in message_lower for word in 
                                      ["why", "what", "how", "when", "where", "who", "explain"]):
            
            # Specific topics
            if "sky blue" in message_lower:
                response_data = {
                    "response_type": "answer",
                    "question": user_message,
                    "answer": "The sky appears blue due to Rayleigh scattering. Sunlight contains all colors, but blue light waves are shorter and scatter more easily in Earth's atmosphere.",
                    "key_points": [
                        "Sunlight contains all colors of spectrum",
                        "Blue light has shorter wavelengths",
                        "Blue scatters more than other colors",
                        "Our eyes perceive scattered blue light"
                    ],
                    "confidence": 0.95,
                    "sources": ["Physics", "Atmospheric Science"]
                }
            elif "ai" in message_lower or "artificial intelligence" in message_lower:
                response_data = {
                    "response_type": "answer",
                    "question": user_message,
                    "answer": "AI (Artificial Intelligence) is technology that enables machines to perform tasks that typically require human intelligence, such as learning, reasoning, and problem-solving.",
                    "types": [
                        {"name": "Machine Learning", "description": "Learning from data"},
                        {"name": "Deep Learning", "description": "Neural networks"},
                        {"name": "NLP", "description": "Understanding language"}
                    ],
                    "confidence": 0.93,
                    "sources": ["Computer Science", "Technology"]
                }
            else:
                response_data = {
                    "response_type": "answer",
                    "question": user_message,
                    "answer": f"That's a great question about '{user_message[:50]}'. This is a complex topic with several key aspects to consider.",
                    "key_points": [
                        "First important aspect to understand",
                        "Second key consideration",
                        "Third relevant factor"
                    ],
                    "confidence": 0.85,
                    "sources": ["General Knowledge"]
                }
        
        # Story request
        elif any(word in message_lower for word in ["story", "tale", "narrative", "tell me"]):
            response_data = {
                "response_type": "story",
                "title": "The Curious Explorer",
                "content": "Once upon a time, there was a curious explorer who asked many questions. Each question led to a new discovery, and each discovery opened new doors to understanding. The explorer learned that curiosity is the key to wisdom.",
                "genre": "adventure",
                "moral": "Curiosity and questions lead to knowledge",
                "characters": ["The Explorer", "Knowledge", "Discovery"],
                "confidence": 0.92
            }
        
        # Help request
        elif any(word in message_lower for word in ["help", "assist", "support", "guide"]):
            response_data = {
                "response_type": "help",
                "message": "I'm here to help you!",
                "capabilities": [
                    {"feature": "Answer Questions", "description": "Ask me anything", "example": "What is Python?"},
                    {"feature": "Tell Stories", "description": "Request a story", "example": "Tell me a story"},
                    {"feature": "Explain Concepts", "description": "Learn about topics", "example": "Explain AI"},
                    {"feature": "Have Conversations", "description": "Just chat", "example": "Let's talk"}
                ],
                "confidence": 0.98
            }
        
        # Greeting
        elif any(word in message_lower for word in ["hello", "hi", "hey", "greetings", "good morning", "good afternoon"]):
            response_data = {
                "response_type": "greeting",
                "message": "Hello! It's wonderful to chat with you!",
                "mood": "friendly",
                "time_of_day": "anytime",
                "suggestions": [
                    "Ask me a question",
                    "Request a story",
                    "Get help",
                    "Just chat"
                ],
                "confidence": 0.98
            }
        
        # Thanks
        elif any(word in message_lower for word in ["thank", "thanks", "appreciate"]):
            response_data = {
                "response_type": "acknowledgment",
                "message": "You're very welcome! I'm happy to help.",
                "mood": "pleased",
                "follow_up": "Is there anything else you'd like to know?",
                "confidence": 0.95
            }
        
        # Default
        else:
            response_data = {
                "response_type": "general",
                "message": f"I understand you're talking about: {user_message[:60]}",
                "sentiment": "attentive",
                "follow_up": "Could you ask a specific question or tell me more?",
                "suggestions": [
                    "Ask 'why' or 'what' questions",
                    "Request help or a story",
                    "Greet me"
                ],
                "confidence": 0.80
            }
        
        # Convert to TOON
        toon_response = encode_to_toon(response_data)
        
        # Calculate metrics
        metrics = estimate_savings(response_data)
        
        # Store in history
        self.conversation_history.append({
            "user": user_message,
            "response": toon_response,
            "tokens": metrics['toon_tokens']
        })
        
        self.total_tokens_saved += metrics['savings']
        
        return {
            "response": toon_response,
            "tokens_used": metrics['toon_tokens'],
            "tokens_saved": metrics['savings'],
            "savings_percent": metrics['savings_percent']
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get conversation statistics."""
        total_messages = len(self.conversation_history)
        total_tokens = sum(msg['tokens'] for msg in self.conversation_history)
        
        return {
            "total_messages": total_messages,
            "total_tokens_used": total_tokens,
            "total_tokens_saved": self.total_tokens_saved,
            "average_savings": (self.total_tokens_saved / (total_tokens + self.total_tokens_saved) * 100) if total_tokens > 0 else 0
        }


# ============================================================================
# INTERACTIVE SESSION
# ============================================================================

def main():
    """Run interactive chatbot."""
    print("\n" + "=" * 80)
    print("🤖 ENHANCED TOON CHATBOT - STANDALONE VERSION")
    print("=" * 80)
    print("\n✨ Features:")
    print("  • Smart question answering")
    print("  • Story generation")
    print("  • Help system")
    print("  • Conversation tracking")
    print("  • 30-60% token savings!")
    print("\n" + "=" * 80)
    print("Commands:")
    print("  • Type your message to chat")
    print("  • Type 'stats' to see statistics")
    print("  • Type 'quit' to exit")
    print("=" * 80 + "\n")
    
    bot = EnhancedToonChatbot()
    
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'quit':
                stats = bot.get_stats()
                print(f"\n📊 Session Summary:")
                print(f"   Messages: {stats['total_messages']}")
                print(f"   Tokens used: {stats['total_tokens_used']}")
                print(f"   Tokens saved: {stats['total_tokens_saved']}")
                print(f"   Average savings: {stats['average_savings']:.1f}%")
                print("\n👋 Thanks for chatting! Goodbye!\n")
                break
            
            elif user_input.lower() == 'stats':
                stats = bot.get_stats()
                print(f"\n📊 Conversation Statistics:")
                print(f"   Messages: {stats['total_messages']}")
                print(f"   Tokens used: {stats['total_tokens_used']}")
                print(f"   Tokens saved: {stats['total_tokens_saved']}")
                print(f"   Average savings: {stats['average_savings']:.1f}%")
                print()
                continue
            
            # Get response
            result = bot.chat(user_input)
            
            print(f"\n🤖 Bot (TOON):")
            print(result['response'])
            print(f"\n📊 Tokens: {result['tokens_used']} | Saved: {result['tokens_saved']} ({result['savings_percent']:.1f}%)")
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
