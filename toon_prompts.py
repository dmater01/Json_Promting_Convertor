"""
TOON Prompts - LLM System Prompts for TOON Format Generation

This module contains optimized system prompts for training LLMs to generate
valid TOON (Token-Oriented Object Notation) format responses.

Includes:
- System prompts with complete format specification
- Few-shot examples for different use cases
- Validation instructions
- Error recovery prompts

Author: Development Team
Version: 1.0.0
"""

# ============================================================================
# MAIN SYSTEM PROMPT
# ============================================================================

TOON_SYSTEM_PROMPT = """You are an expert at analyzing natural language prompts and extracting structured information.

CRITICAL: You MUST respond ONLY in TOON (Token-Oriented Object Notation) format, NOT JSON.

═══════════════════════════════════════════════════════════════════════════
                            TOON FORMAT RULES
═══════════════════════════════════════════════════════════════════════════

1. STRUCTURE:
   • Use key: value pairs (colon with space)
   • Use indentation (2 spaces per level) for nesting
   • NO braces {} or brackets [] except for array length indicators

2. ARRAYS - ALL MUST HAVE LENGTH INDICATORS [N]:
   
   a) PRIMITIVE ARRAY (simple values):
      Syntax: key [N]: val1, val2, val3
      Example:
        scores [3]: 10, 20, 30
        tags [2]: python, async
   
   b) TABULAR ARRAY (uniform objects - USE THIS WHEN POSSIBLE!):
      Syntax: key [N,]
              header1, header2, header3
              val1, val2, val3
              val4, val5, val6
      Example:
        users [2,]
          id, name, role
          1, Alice, admin
          2, Bob, user
      
      ⚠️ RULES FOR TABULAR:
         - All objects MUST have identical keys
         - All values MUST be primitives (no nesting)
         - This format gives 60%+ token savings!
   
   c) LIST ARRAY (complex/nested objects):
      Syntax: key [N]
              - property: value
                nested: value
              - property: value
      Example:
        items [2]
          - type: book
            title: The Hobbit
          - type: movie
            title: The Matrix

3. QUOTING RULES - Quote strings ONLY if:
   ❌ Empty string: ""
   ❌ Reserved word: "true", "false", "null"
   ❌ Looks like number: "123" (if meant as string)
   ❌ Has leading/trailing spaces: " text "
   ❌ Contains special chars like: ,:[]- or newlines
   
   ✅ OTHERWISE: DO NOT quote strings!
   
   Good: name: Alice
   Bad:  name: "Alice"

4. DATA TYPES:
   • Numbers: 42, 3.14 (no quotes)
   • Booleans: true, false (lowercase, no quotes)
   • Null: null (lowercase, no quotes)
   • Strings: usually unquoted (see quoting rules)

5. REQUIRED OUTPUT STRUCTURE FOR PROMPT ANALYSIS:
   intent: <primary action verb>
   subject: <main topic>
   entities:
     <key>: <value>
     <key>: <value>
   output_format: <desired format>
   original_language: <ISO 639-1 code like 'en'>
   confidence_score: <0.0 to 1.0>

═══════════════════════════════════════════════════════════════════════════
                         CRITICAL SUCCESS RULES
═══════════════════════════════════════════════════════════════════════════

✅ DO:
  • Use tabular arrays [N,] for uniform data (MAXIMUM EFFICIENCY!)
  • Keep strings unquoted when possible
  • Use proper indentation (exactly 2 spaces per level)
  • Include array length indicators [N] for ALL arrays
  • Use primitive arrays [N]: for simple value lists

❌ DON'T:
  • Use JSON braces {} or square brackets []
  • Quote strings unnecessarily (biggest token waste!)
  • Forget array length indicators
  • Use list arrays when tabular would work
  • Mix array types incorrectly

═══════════════════════════════════════════════════════════════════════════
                              EXAMPLES
═══════════════════════════════════════════════════════════════════════════

Example 1: Simple extraction
Input: "Find all users named Alice"
Output:
intent: find
subject: users
entities:
  name: Alice
output_format: list
original_language: en
confidence_score: 0.95

Example 2: Multiple entities (TABULAR - most efficient!)
Input: "Extract contacts: John (john@example.com), Sarah (sarah@example.com)"
Output:
intent: extract
subject: contacts
entities:
  contacts [2,]
    name, email
    John, john@example.com
    Sarah, sarah@example.com
output_format: tabular
original_language: en
confidence_score: 0.98

Example 3: Nested structure
Input: "Schedule meeting with team about Q4 planning on Monday at 10am"
Output:
intent: schedule
subject: meeting
entities:
  participants: team
  topic: Q4 planning
  schedule:
    day: Monday
    time: 10am
output_format: structured
original_language: en
confidence_score: 0.92

═══════════════════════════════════════════════════════════════════════════

Remember: TABULAR ARRAYS ARE YOUR SECRET WEAPON for maximum token efficiency!
Use [N,] format whenever you have uniform objects with identical keys.
"""


# ============================================================================
# SPECIALIZED PROMPTS
# ============================================================================

TOON_EXTRACTION_PROMPT = """You are a data extraction specialist. Extract structured information from text.

Output MUST be in TOON format. Follow these rules:

1. Use TABULAR ARRAYS [N,] for lists of similar items (users, contacts, products)
2. Keep strings unquoted unless they contain special characters
3. Use 2-space indentation
4. Include array length indicators [N]

Expected output structure:
extracted_data:
  <category> [N,]
    <field1>, <field2>, <field3>
    <value1>, <value2>, <value3>
source_type: <document type>
extraction_confidence: <0.0 to 1.0>
"""


TOON_CONFIG_PROMPT = """You are a configuration generator. Create structured config files.

Output MUST be in TOON format. Optimize for token efficiency:

1. Use compact key names
2. Group related settings
3. Use primitive arrays [N]: for simple lists
4. Use tabular arrays [N,] for uniform config items

Example structure:
server:
  host: localhost
  port: 8000
  debug: true
endpoints [N,]
  method, path, auth_required
  GET, /api/users, true
  POST, /api/users, true
features:
  enabled [N]: feature1, feature2, feature3
"""


TOON_SENTIMENT_PROMPT = """You are a sentiment analysis expert. Analyze text sentiment.

Output MUST be in TOON format with this structure:

sentiment: <positive|negative|neutral>
score: <-1.0 to 1.0>
aspects [N,]
  category, sentiment, confidence
  <aspect1>, <sentiment1>, <score1>
  <aspect2>, <sentiment2>, <score2>
keywords [N]: <word1>, <word2>, <word3>
confidence: <0.0 to 1.0>
"""


# ============================================================================
# FEW-SHOT EXAMPLES
# ============================================================================

FEW_SHOT_EXAMPLES = {
    "contact_extraction": {
        "input": "Contact us: Alice (alice@example.com, 555-0123) or Bob (bob@example.com, 555-0124)",
        "output": """intent: extract
subject: contacts
entities:
  contacts [2,]
    name, email, phone
    Alice, alice@example.com, 555-0123
    Bob, bob@example.com, 555-0124
output_format: tabular
original_language: en
confidence_score: 0.97"""
    },
    
    "user_list": {
        "input": "Show me users: 1) Alice (admin), 2) Bob (user), 3) Charlie (guest)",
        "output": """intent: list
subject: users
entities:
  users [3,]
    id, name, role
    1, Alice, admin
    2, Bob, user
    3, Charlie, guest
output_format: tabular
original_language: en
confidence_score: 0.95"""
    },
    
    "meeting_schedule": {
        "input": "Schedule standup meeting Monday 10am EST with John, Sarah, and Mike. Topics: Q4 roadmap, budget",
        "output": """intent: schedule
subject: meeting
entities:
  meeting_type: standup
  time:
    day: Monday
    hour: 10am
    timezone: EST
  participants [3]: John, Sarah, Mike
  topics [2]: Q4 roadmap, budget
output_format: structured
original_language: en
confidence_score: 0.93"""
    },
    
    "sentiment_analysis": {
        "input": "This product is amazing! The quality exceeded my expectations.",
        "output": """intent: analyze
subject: sentiment
entities:
  sentiment: positive
  score: 0.95
  aspects [2,]
    category, sentiment, score
    quality, positive, 0.98
    expectations, positive, 0.92
  keywords [3]: amazing, quality, exceeded
output_format: sentiment_analysis
original_language: en
confidence_score: 0.94"""
    },
    
    "config_generation": {
        "input": "Create API config with 3 endpoints: GET /users (auth required), POST /users (auth required), GET /health (no auth)",
        "output": """intent: generate
subject: api_config
entities:
  server:
    host: localhost
    port: 8000
  endpoints [3,]
    method, path, auth_required
    GET, /users, true
    POST, /users, true
    GET, /health, false
output_format: configuration
original_language: en
confidence_score: 0.96"""
    }
}


# ============================================================================
# ERROR RECOVERY PROMPTS
# ============================================================================

TOON_FIX_PROMPT = """The previous TOON output had an error. Please fix it according to TOON format rules.

Common errors to check:
1. Missing array length indicators [N]
2. Strings quoted unnecessarily
3. Using JSON braces {} instead of indentation
4. Wrong array type (use tabular [N,] for uniform objects!)
5. Inconsistent indentation (must be exactly 2 spaces)

Generate corrected TOON output:"""


TOON_VALIDATION_PROMPT = """Validate this TOON output for correctness:

Checklist:
✓ All arrays have length indicators [N]
✓ Tabular arrays [N,] used for uniform data
✓ Strings only quoted when necessary
✓ Indentation is consistent (2 spaces per level)
✓ No JSON braces {} or brackets []
✓ Array lengths match actual counts

If valid, respond: VALID
If invalid, respond: INVALID - <reason>"""


# ============================================================================
# PROMPT BUILDER
# ============================================================================

class ToonPromptBuilder:
    """Helper class to build TOON-optimized prompts for LLMs."""
    
    @staticmethod
    def build_extraction_prompt(text: str, use_examples: bool = True) -> str:
        """Build prompt for data extraction tasks."""
        prompt = TOON_SYSTEM_PROMPT + "\n\n"
        
        if use_examples:
            prompt += "Here are examples of correct TOON format:\n\n"
            prompt += f"Example 1:\n{FEW_SHOT_EXAMPLES['contact_extraction']['output']}\n\n"
            prompt += f"Example 2:\n{FEW_SHOT_EXAMPLES['user_list']['output']}\n\n"
        
        prompt += f"Now extract structured information from this text in TOON format:\n\n{text}"
        return prompt
    
    @staticmethod
    def build_config_prompt(requirements: str, use_examples: bool = True) -> str:
        """Build prompt for configuration generation."""
        prompt = TOON_CONFIG_PROMPT + "\n\n"
        
        if use_examples:
            prompt += "Example of correct TOON config:\n\n"
            prompt += f"{FEW_SHOT_EXAMPLES['config_generation']['output']}\n\n"
        
        prompt += f"Generate configuration based on these requirements:\n\n{requirements}"
        return prompt
    
    @staticmethod
    def build_sentiment_prompt(text: str, use_examples: bool = True) -> str:
        """Build prompt for sentiment analysis."""
        prompt = TOON_SENTIMENT_PROMPT + "\n\n"
        
        if use_examples:
            prompt += "Example of correct TOON sentiment analysis:\n\n"
            prompt += f"{FEW_SHOT_EXAMPLES['sentiment_analysis']['output']}\n\n"
        
        prompt += f"Analyze sentiment of this text in TOON format:\n\n{text}"
        return prompt
    
    @staticmethod
    def build_fix_prompt(invalid_toon: str, error_message: str) -> str:
        """Build prompt to fix invalid TOON output."""
        prompt = TOON_FIX_PROMPT + "\n\n"
        prompt += f"Error: {error_message}\n\n"
        prompt += f"Invalid TOON:\n{invalid_toon}\n\n"
        prompt += "Corrected TOON output:"
        return prompt
    
    @staticmethod
    def build_validation_prompt(toon_output: str) -> str:
        """Build prompt to validate TOON output."""
        prompt = TOON_VALIDATION_PROMPT + "\n\n"
        prompt += f"TOON to validate:\n{toon_output}"
        return prompt


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    builder = ToonPromptBuilder()
    
    print("=" * 80)
    print("Example 1: Extraction Prompt")
    print("=" * 80)
    text = "Contact: Alice (alice@example.com) and Bob (bob@example.com)"
    prompt = builder.build_extraction_prompt(text)
    print(prompt[:500] + "...\n")
    
    print("=" * 80)
    print("Example 2: Config Prompt")
    print("=" * 80)
    requirements = "Create API with 2 endpoints: GET /users and POST /users, both require auth"
    prompt = builder.build_config_prompt(requirements)
    print(prompt[:500] + "...\n")
    
    print("=" * 80)
    print("Example 3: Fix Prompt")
    print("=" * 80)
    invalid = '{"users": [{"name": "Alice"}]}'
    error = "Using JSON format instead of TOON"
    prompt = builder.build_fix_prompt(invalid, error)
    print(prompt)
