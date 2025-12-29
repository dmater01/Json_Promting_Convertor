"""
TOON Prompt Templates for Structured Prompt Service

This module contains optimized prompts for generating TOON format
responses from LLMs. Includes system prompts, few-shot examples,
and validation instructions.

Author: Development Team
Version: 1.0.0
"""

# TOON System Prompt - Complete format specification
TOON_SYSTEM_PROMPT = """You are an expert at analyzing natural language prompts and extracting structured information.

CRITICAL: You MUST respond ONLY in TOON (Token-Oriented Object Notation) format, NOT JSON.

=== TOON FORMAT RULES ===

1. STRUCTURE:
   - Use key: value pairs (with colon and space)
   - Use indentation (2 spaces) for nesting
   - NO braces {} or brackets [] except for array indicators

2. ARRAYS:
   - ALL arrays must have length indicators: [N]
   - Three types:
     
     a) PRIMITIVE ARRAY (simple values):
        numbers [3]: 10, 20, 30
     
     b) TABULAR ARRAY (uniform objects - USE THIS WHEN POSSIBLE!):
        users [2,]
          name, email, role
          Alice, alice@example.com, admin
          Bob, bob@example.com, user
     
     c) LIST ARRAY (complex/nested objects):
        items [2]
          - type: book
            title: The Hobbit
          - type: movie
            title: The Matrix

3. QUOTING RULES (Quote strings ONLY if):
   - Empty string: ""
   - Reserved word: "true", "false", "null"
   - Looks like number: "123"
   - Has leading/trailing spaces: " text "
   - Contains special chars: "Smith, John"
   
   OTHERWISE: DO NOT quote strings!

4. DATA TYPES:
   - Numbers: 42, 3.14 (no quotes)
   - Booleans: true, false (no quotes)
   - Null: null (no quotes)
   - Strings: usually unquoted, see quoting rules

5. REQUIRED OUTPUT STRUCTURE:
   intent: <primary action>
   subject: <main topic>
   entities:
     <key>: <value>
     ...
   output_format: <desired format>
   original_language: <ISO 639-1 code>
   confidence_score: <0.0 to 1.0>

=== CRITICAL RULES ===
✅ DO:
  - Use tabular arrays [N,] for uniform data (MOST EFFICIENT!)
  - Keep strings unquoted when possible
  - Use proper indentation (2 spaces per level)
  - Include array length indicators [N]

❌ DON'T:
  - Use JSON braces {} or brackets []
  - Quote all strings (only when necessary!)
  - Forget array length indicators
  - Use wrong array type (prefer tabular!)

=== EXAMPLES ===

Example 1 - Simple Translation:
```toon
intent: translate
subject: text
entities:
  source: Bonjour le monde
  target_language: English
  translation: Hello world
output_format: text
original_language: fr
confidence_score: 0.95
```

Example 2 - Contact Extraction (TABULAR ARRAY):
```toon
intent: extract
subject: contacts
entities:
  contacts [3,]
    name, email, phone
    John Doe, john@example.com, 555-1234
    Jane Smith, jane@example.com, 555-5678
    Bob Jones, bob@example.com, 555-9999
output_format: tabular
original_language: en
confidence_score: 0.92
```

Example 3 - Multi-Entity Extraction:
```toon
intent: parse
subject: meeting request
entities:
  meeting_type: standup
  day: Monday
  time: 10am EST
  participants [3]: John, Sarah, Mike
  topics [2]: Q4 roadmap, budget allocation
output_format: structured
original_language: en
confidence_score: 0.89
```

Now analyze the user's prompt and respond in TOON format. Use tabular arrays whenever you have uniform data!
"""


# Shorter version for faster processing
TOON_SYSTEM_PROMPT_COMPACT = """You are an expert prompt analyzer. Respond ONLY in TOON format.

TOON RULES:
- key: value with indentation (NO braces/brackets)
- Arrays: [N] for length
- Tabular arrays [N,] for uniform data: header\nrows
- Quote strings only if: empty, keyword, number-like, or special chars
- Required fields: intent, subject, entities, output_format, original_language, confidence_score

STRUCTURE:
intent: <action>
subject: <topic>
entities:
  <key>: <value>
output_format: <format>
original_language: <lang>
confidence_score: <0-1>

Use tabular arrays [N,] for uniform data. Keep strings unquoted when possible.
"""


# Few-shot examples for better LLM performance
TOON_FEW_SHOT_EXAMPLES = [
    {
        "user_prompt": 'Translate "Hello world" to French',
        "toon_response": """intent: translate
subject: text
entities:
  source: Hello world
  target_language: French
  translation: Bonjour le monde
output_format: text
original_language: en
confidence_score: 0.95"""
    },
    {
        "user_prompt": "Extract users from: Alice (admin), Bob (user), Charlie (guest)",
        "toon_response": """intent: extract
subject: users
entities:
  users [3,]
    name, role
    Alice, admin
    Bob, user
    Charlie, guest
output_format: tabular
original_language: en
confidence_score: 0.93"""
    },
    {
        "user_prompt": "Analyze sentiment: This product is absolutely amazing!",
        "toon_response": """intent: analyze
subject: sentiment
entities:
  text: This product is absolutely amazing!
  sentiment: positive
  score: 0.95
output_format: sentiment_analysis
original_language: en
confidence_score: 0.91"""
    },
    {
        "user_prompt": "Parse email: john@example.com, jane@example.com, bob@company.org",
        "toon_response": """intent: parse
subject: emails
entities:
  emails [3]: john@example.com, jane@example.com, bob@company.org
output_format: list
original_language: en
confidence_score: 0.97"""
    }
]


def build_toon_prompt(
    user_prompt: str,
    use_few_shot: bool = True,
    use_compact: bool = False
) -> str:
    """
    Build complete LLM prompt for TOON generation.
    
    Args:
        user_prompt: The user's natural language prompt
        use_few_shot: Include few-shot examples
        use_compact: Use compact system prompt (faster)
    
    Returns:
        Complete prompt for LLM
    """
    # Choose system prompt
    system_prompt = TOON_SYSTEM_PROMPT_COMPACT if use_compact else TOON_SYSTEM_PROMPT
    
    # Build prompt
    parts = [system_prompt]
    
    # Add few-shot examples if requested
    if use_few_shot:
        parts.append("\n=== FEW-SHOT EXAMPLES ===\n")
        for i, example in enumerate(TOON_FEW_SHOT_EXAMPLES[:2], 1):  # Use 2 examples
            parts.append(f"Example {i}:")
            parts.append(f"User: {example['user_prompt']}")
            parts.append(f"Response:\n```toon\n{example['toon_response']}\n```\n")
    
    # Add user prompt
    parts.append(f"\n=== YOUR TASK ===")
    parts.append(f"User prompt: {user_prompt}")
    parts.append(f"\nAnalyze this prompt and respond in TOON format. Wrap your response in ```toon...``` code block.")
    
    return "\n".join(parts)


def build_toon_prompt_for_gemini(user_prompt: str) -> str:
    """
    Build Gemini-optimized prompt for TOON generation.
    
    Gemini-specific optimizations:
    - Clearer structure
    - More explicit examples
    - Stronger formatting enforcement
    """
    return f"""You will analyze a prompt and return structured data in TOON format.

TOON FORMAT SPECIFICATION:
• Use "key: value" with indentation (2 spaces per level)
• Arrays have length indicators: [N]
• For uniform objects, use tabular arrays: [N,] with header + rows
• Quote strings only when: empty, keyword, number-like, or containing special chars
• Required output: intent, subject, entities, output_format, original_language, confidence_score

TABULAR ARRAY EXAMPLE (use for uniform data!):
```toon
contacts [2,]
  name, email, phone
  John, john@example.com, 555-1234
  Jane, jane@example.com, 555-5678
```

USER PROMPT:
{user_prompt}

Respond with TOON format ONLY. Use tabular arrays for uniform data. Wrap in ```toon code block.
"""


def build_toon_prompt_for_claude(user_prompt: str) -> str:
    """
    Build Claude-optimized prompt for TOON generation.
    
    Claude-specific optimizations:
    - Detailed format rules
    - Clear examples
    - Explicit error prevention
    """
    return f"""{TOON_SYSTEM_PROMPT}

USER PROMPT TO ANALYZE:
{user_prompt}

INSTRUCTIONS:
1. Carefully analyze the prompt above
2. Extract intent, subject, and all relevant entities
3. Format response in TOON notation (NOT JSON!)
4. Use tabular arrays [N,] for any uniform data
5. Wrap response in ```toon code block

Begin your TOON response now:
"""


def build_toon_prompt_for_gpt4(user_prompt: str) -> str:
    """
    Build GPT-4 optimized prompt for TOON generation.
    
    GPT-4-specific optimizations:
    - Concise but complete rules
    - Strong format enforcement
    - Clear examples
    """
    return f"""Analyze the following prompt and return structured data in TOON (Token-Oriented Object Notation) format.

TOON RULES (CRITICAL):
1. Use "key: value" with indentation (NOT JSON with {{}})
2. Arrays have [N] length indicators
3. Uniform objects → tabular arrays [N,]: header, then rows
4. Quote strings ONLY when: empty/"", keyword/true/false/null, number-like/"123", or special-chars/"Smith, John"
5. Output: intent, subject, entities, output_format, original_language, confidence_score

EXAMPLE TABULAR ARRAY (preferred for uniform data):
users [2,]
  name, email
  Alice, alice@example.com
  Bob, bob@example.com

USER PROMPT:
{user_prompt}

Return ONLY TOON format (no JSON, no explanation). Use tabular arrays for uniform data.
"""


# Validation prompt for fixing malformed TOON
TOON_FIX_PROMPT = """The following TOON response has formatting errors. Fix it to be valid TOON format.

RULES:
- Use "key: value" with indentation
- Arrays need [N] indicators
- Use tabular arrays [N,] for uniform data
- Quote strings only when necessary
- Required fields: intent, subject, entities, output_format, original_language, confidence_score

MALFORMED TOON:
{malformed_toon}

Return the corrected TOON (wrapped in ```toon code block):
"""


def build_toon_fix_prompt(malformed_toon: str) -> str:
    """Build prompt to fix malformed TOON output."""
    return TOON_FIX_PROMPT.format(malformed_toon=malformed_toon)


# Token savings explanation for documentation
TOKEN_SAVINGS_EXPLANATION = """
Why TOON Saves Tokens:

1. NO BRACES/BRACKETS (except array indicators):
   JSON:  {"users": [{"name": "Alice"}]}     → ~15 tokens
   TOON:  users [1,]                         → ~5 tokens
          name                               
          Alice                              

2. MINIMAL QUOTING:
   JSON:  "name": "Alice"                    → ~4 tokens
   TOON:  name: Alice                        → ~2 tokens

3. TABULAR ARRAYS (most efficient!):
   JSON:  [{"id":1,"name":"Alice"},{"id":2,"name":"Bob"}]   → ~20 tokens
   TOON:  users [2,]                                        → ~8 tokens
          id, name
          1, Alice
          2, Bob

4. NO REPEATED KEYS:
   JSON repeats keys for each object: "id", "name" × N
   TOON defines keys once in header

RESULT: 30-60% token reduction (average 45-50%)
"""


if __name__ == "__main__":
    # Example usage
    print("=== TOON Prompt Templates ===\n")
    
    test_prompt = "Extract contacts from: John Doe (john@example.com, 555-1234), Jane Smith (jane@example.com, 555-5678)"
    
    print("--- Full Prompt (with few-shot) ---")
    full_prompt = build_toon_prompt(test_prompt, use_few_shot=True)
    print(full_prompt[:500] + "...\n")
    
    print("--- Compact Prompt ---")
    compact_prompt = build_toon_prompt(test_prompt, use_compact=True)
    print(compact_prompt[:300] + "...\n")
    
    print("--- Gemini-Optimized ---")
    gemini_prompt = build_toon_prompt_for_gemini(test_prompt)
    print(gemini_prompt[:300] + "...\n")
    
    print(f"Full prompt length: {len(full_prompt)} chars")
    print(f"Compact prompt length: {len(compact_prompt)} chars")
    print(f"Gemini prompt length: {len(gemini_prompt)} chars")
