#!/usr/bin/env python3
"""
Final Enhanced JSON Prompt Converter with Comprehensive Edge Case Handling
Combines all refinements and testing improvements into a production-ready tool.
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import sys

class FinalEnhancedJSONPromptConverter:
    """
    Production-ready JSON prompt converter with comprehensive edge case handling,
    intelligent parsing, validation, and user guidance.
    """
    
    def __init__(self):
        self.valid_formats = ['json', 'text', 'table', 'markdown', 'html', 'csv', 'xml', 'code']
        
        # Enhanced category detection
        self.prompt_categories = {
            'analysis': {
                'primary': ['analyze', 'compare', 'evaluate', 'assess', 'examine', 'review', 'audit'],
                'secondary': ['data', 'metrics', 'performance', 'trends', 'insights', 'statistics']
            },
            'creative': {
                'primary': ['write', 'create', 'compose', 'generate', 'craft', 'design'],
                'secondary': ['story', 'poem', 'article', 'content', 'creative', 'narrative']
            },
            'technical': {
                'primary': ['build', 'develop', 'code', 'implement', 'debug', 'optimize', 'deploy'],
                'secondary': ['API', 'database', 'software', 'system', 'application', 'script', 'function']
            },
            'research': {
                'primary': ['research', 'investigate', 'study', 'explore', 'survey'],
                'secondary': ['market', 'literature', 'findings', 'methodology', 'sources']
            },
            'planning': {
                'primary': ['plan', 'strategy', 'roadmap', 'schedule', 'organize'],
                'secondary': ['timeline', 'goals', 'objectives', 'framework', 'approach']
            }
        }
        
        # Edge case detection
        self.ambiguous_triggers = ['make it', 'fix it', 'improve', 'better', 'good', 'nice']
        self.technical_terms = {
            'OAuth2': 'Open Authorization 2.0 - authentication protocol',
            'PKCE': 'Proof Key for Code Exchange - security extension', 
            'JWT': 'JSON Web Token - secure information transmission',
            'RS256': 'RSA Signature with SHA-256 - encryption algorithm',
            'API': 'Application Programming Interface',
            'REST': 'Representational State Transfer architecture',
            'CRUD': 'Create, Read, Update, Delete operations',
            'ML': 'Machine Learning',
            'AI': 'Artificial Intelligence',
            'NLP': 'Natural Language Processing'
        }
        
        # Contradiction patterns
        self.contradiction_patterns = {
            'length': {
                'short': ['brief', 'concise', 'short', 'minimal'],
                'long': ['comprehensive', 'detailed', 'thorough', 'extensive']
            },
            'complexity': {
                'simple': ['simple', 'basic', 'easy', 'straightforward'],
                'complex': ['complex', 'advanced', 'sophisticated', 'comprehensive']
            },
            'tone': {
                'formal': ['formal', 'professional', 'academic'],
                'casual': ['casual', 'informal', 'friendly', 'conversational']
            }
        }
    
    def detect_category_with_confidence(self, prompt: str) -> Tuple[str, float]:
        """Enhanced category detection with confidence scoring."""
        prompt_lower = prompt.lower()
        category_scores = defaultdict(float)
        
        for category, keywords in self.prompt_categories.items():
            primary_score = sum(2.0 for keyword in keywords['primary'] if keyword in prompt_lower)
            secondary_score = sum(1.0 for keyword in keywords['secondary'] if keyword in prompt_lower)
            category_scores[category] = primary_score + secondary_score
        
        if not category_scores or max(category_scores.values()) == 0:
            return 'general', 0.0
        
        best_category = max(category_scores, key=category_scores.get)
        confidence = category_scores[best_category] / (sum(category_scores.values()) or 1)
        
        return best_category, confidence
    
    def extract_task_with_fallbacks(self, prompt: str) -> str:
        """Enhanced task extraction with comprehensive fallback strategies."""
        prompt = prompt.strip()
        
        # Handle very short prompts
        if len(prompt) <= 5:
            return f"Execute: {prompt}"
        
        # Strategy 1: Handle preposition patterns with exclusions
        preposition_patterns = [
            (r'^(.+?)\s+on\s+(.+)$', ' on '),
            (r'^(.+?)\s+about\s+(.+)$', ' about '),
            (r'^(.+?)\s+regarding\s+(.+)$', ' regarding ')
        ]
        
        for pattern, prep in preposition_patterns:
            if prep in prompt and not any(prompt.lower().startswith(exclude) for exclude in 
                ['turn on', 'based on', 'focus on', 'work on', 'click on']):
                match = re.search(pattern, prompt)
                if match and len(match.group(1)) > 3:
                    return match.group(1).strip()
        
        # Strategy 2: Enhanced verb detection
        verb_patterns = [
            r'^(create|generate|write|build|develop|analyze|compare|make|design|implement|produce|construct)\s+(.+?)(?:\s+(?:for|with|using|in|about|on)|$)',
            r'^(?:please\s+|can you\s+|could you\s+)?(create|generate|write|build|develop|analyze|compare|make|design|implement|produce|construct)\s+(.+?)(?:\s+(?:for|with|using|in|about|on)|$)',
            r'^(?:help me\s+|assist me\s+to\s+)(create|generate|write|build|develop|analyze|compare|make|design|implement|produce|construct)\s+(.+?)(?:\s+(?:for|with|using|in|about|on)|$)',
            r'^(?:i need\s+|i want\s+|i\'d like\s+)(?:to\s+)?(create|generate|write|build|develop|analyze|compare|make|design|implement|produce|construct)\s+(.+?)(?:\s+(?:for|with|using|in|about|on)|$)'
        ]
        
        for pattern in verb_patterns:
            match = re.search(pattern, prompt.lower())
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    verb = groups[-2]
                    object_part = groups[-1]
                    return f"{verb.capitalize()} {object_part}"
        
        # Strategy 3: Question pattern extraction
        question_patterns = [
            r'^(?:how\s+(?:do\s+i\s+|can\s+i\s+|to\s+)?)(create|generate|write|build|develop|analyze|compare|make|design|implement)\s+(.+?)(?:\?|$)',
            r'^(?:what\'s\s+the\s+best\s+way\s+to\s+)(create|generate|write|build|develop|analyze|compare|make|design|implement)\s+(.+?)(?:\?|$)'
        ]
        
        for pattern in question_patterns:
            match = re.search(pattern, prompt.lower())
            if match:
                verb, object_part = match.groups()
                return f"{verb.capitalize()} {object_part}"
        
        # Strategy 4: Smart truncation for very long prompts
        if len(prompt) > 100:
            sentences = re.split(r'[.!?]', prompt)
            if sentences:
                main_sentence = sentences[0].strip()
                if main_sentence and len(main_sentence) < len(prompt):
                    return self.extract_task_with_fallbacks(main_sentence)
            
            words = prompt.split()
            if len(words) > 15:
                return ' '.join(words[:15]) + '...'
        
        return prompt
    
    def detect_ambiguity(self, prompt: str) -> Tuple[bool, str, List[str]]:
        """Detect if a prompt is too ambiguous and provide guidance."""
        prompt_lower = prompt.lower().strip()
        
        # Check for ultra-vague patterns
        if any(trigger in prompt_lower for trigger in self.ambiguous_triggers):
            if len(prompt) < 20:
                return True, "Too vague - missing context", [
                    "What specifically needs to be improved?",
                    "What is the current state or problem?", 
                    "What is the desired outcome?",
                    "Who is the target audience?"
                ]
        
        # Check for pronouns without context
        pronouns = ['it', 'this', 'that', 'these', 'those']
        if any(f" {pronoun} " in f" {prompt_lower} " for pronoun in pronouns):
            if len(prompt) < 30:
                return True, "Unclear pronoun reference", [
                    "Replace pronouns with specific nouns",
                    "Provide context about what 'it' refers to",
                    "Be more explicit about the subject"
                ]
        
        # Check for single word or very short prompts
        if len(prompt.split()) <= 2:
            return True, "Insufficient detail", [
                "Add more context about the task",
                "Specify the desired format or output",
                "Include any constraints or requirements"
            ]
        
        return False, "", []
    
    def detect_contradictions(self, constraints: List[str]) -> List[Dict[str, any]]:
        """Detect contradictory constraints and suggest resolutions."""
        contradictions = []
        
        for category, patterns in self.contradiction_patterns.items():
            found_opposites = []
            
            for constraint in constraints:
                constraint_lower = constraint.lower()
                
                for side, keywords in patterns.items():
                    if any(keyword in constraint_lower for keyword in keywords):
                        found_opposites.append({'constraint': constraint, 'side': side, 'category': category})
            
            # Check if we have both sides
            sides_found = set(item['side'] for item in found_opposites)
            if len(sides_found) > 1:
                contradictions.append({
                    'category': category,
                    'conflicting_constraints': [item['constraint'] for item in found_opposites],
                    'suggestions': self._generate_contradiction_suggestions(category)
                })
        
        return contradictions
    
    def _generate_contradiction_suggestions(self, category: str) -> List[str]:
        """Generate suggestions for resolving contradictions."""
        if category == 'length':
            return [
                "Choose either 'brief' OR 'comprehensive' - not both",
                "Consider 'moderately detailed' as a compromise",
                "Specify different length requirements for different sections"
            ]
        elif category == 'complexity':
            return [
                "Specify 'simple language but comprehensive coverage'",
                "Use 'beginner-friendly explanations of advanced concepts'",
                "Define target audience to resolve complexity level"
            ]
        elif category == 'tone':
            return [
                "Use 'professional but approachable' or similar combinations",
                "Separate tone requirements by section or audience"
            ]
        return ["Consider clarifying your requirements"]
    
    def convert_with_edge_case_handling(self) -> Dict[str, any]:
        """Main conversion method with comprehensive edge case handling."""
        print("🚀 Final Enhanced JSON Prompt Converter v3.0")
        print("=" * 60)
        print("✨ Now with intelligent edge case handling!")
        
        try:
            # Get main prompt
            prompt = input("\n📝 Enter your prompt: ").strip()
            
            # Edge case analysis
            is_ambiguous, ambiguity_reason, clarifications = self.detect_ambiguity(prompt)
            
            if is_ambiguous:
                print(f"\n⚠️  Ambiguity detected: {ambiguity_reason}")
                print("Clarifications needed:")
                for i, clarification in enumerate(clarifications, 1):
                    print(f"  {i}. {clarification}")
                
                enhance_choice = input("\n🔧 Would you like to enhance this prompt? (y/n): ").strip().lower()
                if enhance_choice in ['y', 'yes']:
                    prompt = input("Please provide a more detailed prompt: ").strip()
            
            # Extract and analyze
            task = self.extract_task_with_fallbacks(prompt)
            category, confidence = self.detect_category_with_confidence(prompt)
            
            print(f"\n🎯 Analysis:")
            print(f"   Category: {category.upper()} (confidence: {confidence:.1%})")
            print(f"   Extracted task: {task}")
            
            # Check for technical jargon
            technical_explanations = []
            for term, explanation in self.technical_terms.items():
                if term in prompt:
                    technical_explanations.append(f"{term}: {explanation}")
            
            if technical_explanations:
                print(f"\n📚 Technical terms detected:")
                for explanation in technical_explanations:
                    print(f"   • {explanation}")
            
            # Build JSON structure
            json_prompt = {
                "task": task,
                "category": category,
                "confidence": round(confidence, 2)
            }
            
            # Get format
            if category == 'technical':
                default_format = 'code'
            elif category == 'analysis':
                default_format = 'json'
            else:
                default_format = 'text'
            
            format_input = input(f"\n📄 Format (default: {default_format}): ").strip().lower()
            json_prompt["format"] = format_input if format_input else default_format
            
            # Handle constraints with contradiction detection
            constraints_input = input("\n🔒 Constraints: ").strip()
            
            if constraints_input:
                constraint_list = [c.strip() for c in re.split(r'[,;]', constraints_input) if c.strip()]
                contradictions = self.detect_contradictions(constraint_list)
                
                if contradictions:
                    print(f"\n⚠️  Contradictions detected:")
                    for contradiction in contradictions:
                        print(f"   Category: {contradiction['category']}")
                        print(f"   Conflicting: {', '.join(contradiction['conflicting_constraints'])}")
                        print("   Suggestions:")
                        for suggestion in contradiction['suggestions']:
                            print(f"     • {suggestion}")
                    
                    resolve_choice = input("\n🔧 Resolve contradictions? (y/n): ").strip().lower()
                    if resolve_choice in ['y', 'yes']:
                        constraints_input = input("Please provide revised constraints: ").strip()
                        constraint_list = [c.strip() for c in re.split(r'[,;]', constraints_input) if c.strip()]
                
                json_prompt["constraints"] = constraint_list
            
            # Category-specific fields
            if category == 'technical' and confidence > 0.3:
                complexity = input("\n🔧 Technical complexity (beginner/intermediate/advanced): ").strip()
                if complexity:
                    json_prompt["complexity_level"] = complexity
            
            elif category == 'creative' and confidence > 0.3:
                tone = input("\n🎨 Creative tone (professional/casual/humorous/serious): ").strip()
                if tone:
                    json_prompt["tone"] = tone
            
            # Add metadata
            if technical_explanations:
                json_prompt["technical_explanations"] = technical_explanations
            
            if is_ambiguous:
                json_prompt["original_ambiguity"] = ambiguity_reason
            
            return json_prompt
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            return {}
        except Exception as e:
            print(