#!/usr/bin/env python3
"""
Enhanced JSON Prompt Converter - Production Ready Version
A comprehensive tool for converting natural language prompts into structured JSON format
with intelligent parsing, edge case handling, and user guidance.

Author: Enhanced AI Development
Version: 3.0
License: MIT
"""

import json
import re
import yaml
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, Optional, Union
from collections import defaultdict
from datetime import datetime
import sys
import os

class EnhancedJSONPromptConverter:
    """
    Production-ready JSON prompt converter with comprehensive edge case handling,
    intelligent parsing, validation, and user guidance.
    """
    
    def __init__(self):
        self.version = "3.0"
        self.valid_formats = [
            'json', 'text', 'table', 'markdown', 'html', 
            'csv', 'xml', 'code', 'yaml'
        ]
        
        # Enhanced category detection with weighted keywords
        self.prompt_categories = {
            'analysis': {
                'primary': ['analyze', 'compare', 'evaluate', 'assess', 'examine', 'review', 'audit', 'study'],
                'secondary': ['data', 'metrics', 'performance', 'trends', 'insights', 'statistics', 'benchmark']
            },
            'creative': {
                'primary': ['write', 'create', 'compose', 'generate', 'craft', 'design', 'draft'],
                'secondary': ['story', 'poem', 'article', 'content', 'creative', 'narrative', 'blog', 'copy']
            },
            'technical': {
                'primary': ['build', 'develop', 'code', 'implement', 'debug', 'optimize', 'deploy', 'program'],
                'secondary': ['API', 'database', 'software', 'system', 'application', 'script', 'function', 'algorithm']
            },
            'research': {
                'primary': ['research', 'investigate', 'study', 'explore', 'survey', 'analyze'],
                'secondary': ['market', 'literature', 'findings', 'methodology', 'sources', 'academic', 'scholarly']
            },
            'planning': {
                'primary': ['plan', 'strategy', 'roadmap', 'schedule', 'organize', 'structure'],
                'secondary': ['timeline', 'goals', 'objectives', 'framework', 'approach', 'methodology']
            },
            'educational': {
                'primary': ['explain', 'teach', 'tutorial', 'guide', 'lesson', 'demonstrate'],
                'secondary': ['learning', 'education', 'training', 'instruction', 'beginner', 'course']
            }
        }
        
        # Edge case detection patterns
        self.ambiguous_triggers = [
            'make it', 'fix it', 'improve', 'better', 'good', 'nice', 
            'enhance', 'optimize', 'update', 'modify'
        ]
        
        # Technical terminology with explanations
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
            'NLP': 'Natural Language Processing',
            'SQL': 'Structured Query Language',
            'NoSQL': 'Not Only SQL - non-relational database',
            'DevOps': 'Development and Operations integration',
            'CI/CD': 'Continuous Integration/Continuous Deployment',
            'SaaS': 'Software as a Service',
            'PaaS': 'Platform as a Service',
            'IaaS': 'Infrastructure as a Service'
        }
        
        # Contradiction detection patterns
        self.contradiction_patterns = {
            'length': {
                'short': ['brief', 'concise', 'short', 'minimal', 'summary', 'quick'],
                'long': ['comprehensive', 'detailed', 'thorough', 'extensive', 'in-depth', 'complete']
            },
            'complexity': {
                'simple': ['simple', 'basic', 'easy', 'straightforward', 'beginner'],
                'complex': ['complex', 'advanced', 'sophisticated', 'comprehensive', 'expert']
            },
            'tone': {
                'formal': ['formal', 'professional', 'academic', 'official'],
                'casual': ['casual', 'informal', 'friendly', 'conversational', 'relaxed']
            },
            'scope': {
                'narrow': ['focused', 'specific', 'targeted', 'limited'],
                'broad': ['broad', 'general', 'wide', 'comprehensive', 'all-encompassing']
            }
        }
    
    def detect_category_with_confidence(self, prompt: str) -> Tuple[str, float]:
        """Enhanced category detection with confidence scoring."""
        prompt_lower = prompt.lower()
        category_scores = defaultdict(float)
        
        for category, keywords in self.prompt_categories.items():
            # Weight primary keywords more heavily
            primary_score = sum(2.0 for keyword in keywords['primary'] 
                              if keyword in prompt_lower)
            secondary_score = sum(1.0 for keyword in keywords['secondary'] 
                                if keyword in prompt_lower)
            
            # Bonus for exact matches at start of prompt
            if any(prompt_lower.startswith(keyword) for keyword in keywords['primary']):
                primary_score += 1.0
            
            category_scores[category] = primary_score + secondary_score
        
        if not category_scores or max(category_scores.values()) == 0:
            return 'general', 0.0
        
        best_category = max(category_scores, key=category_scores.get)
        total_score = sum(category_scores.values())
        confidence = category_scores[best_category] / total_score if total_score > 0 else 0.0
        
        return best_category, min(confidence, 1.0)
    
    def extract_task_with_fallbacks(self, prompt: str) -> str:
        """Enhanced task extraction with comprehensive fallback strategies."""
        prompt = prompt.strip()
        
        # Handle very short prompts
        if len(prompt) <= 5:
            return f"Execute: {prompt}"
        
        # Strategy 1: Handle preposition patterns with exclusions
        preposition_patterns = [
            (r'^(.+?)\s+(?:on|about|regarding|concerning)\s+(.+)$', lambda m: m.group(1)),
            (r'^(.+?)\s+for\s+(.+)$', lambda m: m.group(1)),
            (r'^(.+?)\s+with\s+(.+)$', lambda m: m.group(1)),
            (r'^(.+?)\s+using\s+(.+)$', lambda m: m.group(1))
        ]
        
        # Exclusions for preposition patterns
        exclusions = [
            'turn on', 'based on', 'focus on', 'work on', 'click on',
            'rely on', 'depend on', 'built on', 'founded on'
        ]
        
        for pattern, extractor in preposition_patterns:
            if not any(prompt.lower().startswith(exclude) for exclude in exclusions):
                match = re.search(pattern, prompt, re.IGNORECASE)
                if match and len(match.group(1).strip()) > 3:
                    return match.group(1).strip()
        
        # Strategy 2: Enhanced verb detection with context
        verb_patterns = [
            r'^(?:please\s+|can you\s+|could you\s+|would you\s+)?(create|generate|write|build|develop|analyze|compare|make|design|implement|produce|construct|code|program|draft|compose)\s+(.+?)(?:\s+(?:for|with|using|in|about|on|that|which)|$)',
            r'^(?:help me\s+|assist me\s+(?:to\s+)?|i need\s+(?:to\s+)?|i want\s+(?:to\s+)?|i\'d like\s+(?:to\s+)?)(create|generate|write|build|develop|analyze|compare|make|design|implement|produce|construct|code|program|draft|compose)\s+(.+?)(?:\s+(?:for|with|using|in|about|on|that|which)|$)',
            r'^(?:let\'s\s+|we should\s+|we need to\s+)(create|generate|write|build|develop|analyze|compare|make|design|implement|produce|construct|code|program|draft|compose)\s+(.+?)(?:\s+(?:for|with|using|in|about|on|that|which)|$)'
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
            r'^(?:how\s+(?:do\s+i\s+|can\s+i\s+|to\s+)?)(create|generate|write|build|develop|analyze|compare|make|design|implement|code|program)\s+(.+?)(?:\?|$)',
            r'^(?:what\'s\s+the\s+best\s+way\s+to\s+)(create|generate|write|build|develop|analyze|compare|make|design|implement|code|program)\s+(.+?)(?:\?|$)',
            r'^(?:can you\s+help\s+me\s+)(create|generate|write|build|develop|analyze|compare|make|design|implement|code|program)\s+(.+?)(?:\?|$)'
        ]
        
        for pattern in question_patterns:
            match = re.search(pattern, prompt.lower())
            if match:
                verb, object_part = match.groups()
                return f"{verb.capitalize()} {object_part}"
        
        # Strategy 4: Smart truncation for very long prompts
        if len(prompt) > 150:
            # Try to find the main sentence
            sentences = re.split(r'[.!?]', prompt)
            if sentences and len(sentences[0].strip()) < len(prompt) * 0.7:
                main_sentence = sentences[0].strip()
                if main_sentence:
                    return self.extract_task_with_fallbacks(main_sentence)
            
            # Fallback to word truncation
            words = prompt.split()
            if len(words) > 20:
                return ' '.join(words[:20]) + '...'
        
        # Strategy 5: Return cleaned prompt
        return prompt
    
    def detect_ambiguity(self, prompt: str) -> Tuple[bool, str, List[str]]:
        """Detect if a prompt is too ambiguous and provide guidance."""
        prompt_lower = prompt.lower().strip()
        
        # Check for ultra-vague patterns
        vague_score = sum(1 for trigger in self.ambiguous_triggers 
                         if trigger in prompt_lower)
        
        if vague_score > 0 and len(prompt) < 25:
            return True, "Too vague - missing context", [
                "What specifically needs to be improved or created?",
                "What is the current state or problem?", 
                "What is the desired outcome or goal?",
                "Who is the target audience or user?",
                "What format should the output be in?"
            ]
        
        # Check for pronouns without context
        problematic_pronouns = ['it', 'this', 'that', 'these', 'those', 'them']
        pronoun_count = sum(1 for pronoun in problematic_pronouns 
                           if f" {pronoun} " in f" {prompt_lower} ")
        
        if pronoun_count > 0 and len(prompt) < 40:
            return True, "Unclear pronoun reference", [
                "Replace pronouns (it, this, that) with specific nouns",
                "Provide context about what the pronouns refer to",
                "Be more explicit about the main subject"
            ]
        
        # Check for single word or very short prompts
        word_count = len(prompt.split())
        if word_count <= 2:
            return True, "Insufficient detail", [
                "Add more context about the task",
                "Specify the desired format or output type",
                "Include any constraints or requirements",
                "Mention the target audience or use case"
            ]
        
        # Check for overly generic requests
        generic_patterns = ['help with', 'something about', 'stuff for', 'things related to']
        if any(pattern in prompt_lower for pattern in generic_patterns):
            return True, "Too generic", [
                "Be more specific about what kind of help you need",
                "Define the exact task or deliverable",
                "Specify the scope and requirements"
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
                        found_opposites.append({
                            'constraint': constraint, 
                            'side': side, 
                            'category': category
                        })
            
            # Check if we have conflicting sides
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
        suggestions = {
            'length': [
                "Choose either 'brief' OR 'comprehensive' - not both",
                "Consider 'moderately detailed' as a compromise",
                "Specify different length requirements for different sections"
            ],
            'complexity': [
                "Specify 'simple language but comprehensive coverage'",
                "Use 'beginner-friendly explanations of advanced concepts'",
                "Define target audience to resolve complexity level"
            ],
            'tone': [
                "Use 'professional but approachable' or similar combinations",
                "Separate tone requirements by section or audience",
                "Specify context: 'formal for documentation, casual for examples'"
            ],
            'scope': [
                "Clarify whether you want broad overview or deep dive",
                "Consider 'focused but thorough' as middle ground",
                "Specify scope for different sections if needed"
            ]
        }
        
        return suggestions.get(category, ["Consider clarifying your requirements"])
    
    def parse_constraints_intelligently(self, constraints_text: str) -> List[str]:
        """Parse constraints with smart detection of common patterns."""
        if not constraints_text:
            return []
        
        constraints = []
        
        # Split by common delimiters
        raw_constraints = re.split(r'[,;]|\band\b', constraints_text)
        
        for constraint in raw_constraints:
            constraint = constraint.strip()
            if not constraint:
                continue
            
            # Normalize common patterns
            constraint = re.sub(r'^(no|without)\s+', 'no ', constraint.lower())
            constraint = re.sub(r'^(use|include|with)\s+', 'include ', constraint.lower())
            constraint = re.sub(r'^(under|less than|max|maximum)\s+(\d+)\s+words?', 
                              r'under \2 words', constraint)
            constraint = re.sub(r'^(over|more than|min|minimum)\s+(\d+)\s+words?', 
                              r'over \2 words', constraint)
            
            constraints.append(constraint)
        
        return constraints
    
    def validate_input(self, text: str, field_name: str) -> Tuple[bool, str]:
        """Validate user input for safety and completeness."""
        if not text or not text.strip():
            return False, f"{field_name} cannot be empty"
        
        # Check for potentially problematic characters
        problematic_chars = ['"', "'", '\\', '\n', '\r', '\t']
        found_chars = [char for char in problematic_chars if char in text]
        
        if found_chars:
            warning = f"{field_name} contains special characters ({', '.join(found_chars)}) that may cause JSON issues"
            return True, warning  # Allow but warn
        
        return True, ""
    
    def get_safe_input(self, prompt: str, field_name: str, required: bool = True, 
                      valid_options: Optional[List[str]] = None, 
                      multiline: bool = False) -> str:
        """Get user input with validation and error handling."""
        while True:
            try:
                if multiline:
                    print(f"{prompt} (Press Ctrl+D or Ctrl+Z when done):")
                    lines = []
                    try:
                        while True:
                            line = input()
                            lines.append(line)
                    except EOFError:
                        user_input = '\n'.join(lines).strip()
                else:
                    user_input = input(prompt).strip()
                
                if not user_input and required:
                    print(f"❌ {field_name} is required. Please try again.")
                    continue
                
                if not user_input and not required:
                    return ""
                
                if valid_options:
                    # Case-insensitive validation
                    valid_lower = [opt.lower() for opt in valid_options]
                    if user_input.lower() not in valid_lower and user_input.lower() != '':
                        print(f"❌ Invalid option. Valid choices: {', '.join(valid_options)}")
                        continue
                
                is_valid, message = self.validate_input(user_input, field_name)
                if message:
                    print(f"⚠️  Warning: {message}")
                
                if is_valid:
                    return user_input
                else:
                    print(f"❌ {message}")
                    continue
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                sys.exit(0)
            except Exception as e:
                print(f"❌ Error reading input: {e}")
                continue
    
    def calculate_quality_score(self, json_prompt: Dict) -> int:
        """Calculate a quality score for the generated prompt."""
        score = 0
        
        # Base score for having a task
        if json_prompt.get('task'):
            score += 20
        
        # Category detection confidence
        confidence = json_prompt.get('confidence', 0)
        score += int(confidence * 20)
        
        # Format specification
        if json_prompt.get('format'):
            score += 10
        
        # Constraints provided
        constraints = json_prompt.get('constraints', [])
        if constraints:
            score += min(len(constraints) * 5, 20)
        
        # Additional fields
        additional_fields = ['complexity_level', 'tone', 'methodology', 'audience']
        for field in additional_fields:
            if json_prompt.get(field):
                score += 5
        
        # Penalty for ambiguity
        if json_prompt.get('original_ambiguity'):
            score -= 10
        
        # Bonus for technical explanations
        if json_prompt.get('technical_explanations'):
            score += 10
        
        return max(0, min(100, score))
    
    def convert_to_json_prompt(self) -> Dict:
        """Main conversion method with comprehensive edge case handling."""
        print("🚀 Enhanced JSON Prompt Converter v3.0")
        print("=" * 60)
        print("✨ Production-ready with intelligent edge case handling!")
        
        try:
            # Get main prompt
            prompt = self.get_safe_input(
                "\n📝 Enter your prompt: ",
                "Main prompt"
            )
            
            # Edge case analysis
            is_ambiguous, ambiguity_reason, clarifications = self.detect_ambiguity(prompt)
            
            if is_ambiguous:
                print(f"\n⚠️  Ambiguity detected: {ambiguity_reason}")
                print("💡 Clarifications needed:")
                for i, clarification in enumerate(clarifications, 1):
                    print(f"  {i}. {clarification}")
                
                enhance_choice = self.get_safe_input(
                    "\n🔧 Would you like to enhance this prompt? (y/n): ",
                    "Enhancement choice",
                    valid_options=['y', 'yes', 'n', 'no']
                ).lower()
                
                if enhance_choice in ['y', 'yes']:
                    prompt = self.get_safe_input(
                        "\n📝 Please provide a more detailed prompt: ",
                        "Enhanced prompt"
                    )
            
            # Extract and analyze
            task = self.extract_task_with_fallbacks(prompt)
            category, confidence = self.detect_category_with_confidence(prompt)
            
            print(f"\n🎯 Analysis Results:")
            print(f"   📋 Category: {category.upper()} (confidence: {confidence:.1%})")
            print(f"   🎯 Extracted task: {task}")
            
            # Check for technical jargon
            technical_explanations = []
            words_in_prompt = prompt.split()
            for word in words_in_prompt:
                clean_word = re.sub(r'[^\w]', '', word.upper())
                if clean_word in self.technical_terms:
                    explanation = f"{clean_word}: {self.technical_terms[clean_word]}"
                    if explanation not in technical_explanations:
                        technical_explanations.append(explanation)
            
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
            
            # Get format with smart defaults
            if category == 'technical':
                default_format = 'code'
            elif category == 'analysis':
                default_format = 'json'
            elif category == 'creative':
                default_format = 'text'
            else:
                default_format = 'text'
            
            format_choice = self.get_safe_input(
                f"\n📄 Output format (default: {default_format}): ",
                "Output format",
                required=False,
                valid_options=self.valid_formats + ['']
            )
            
            json_prompt["format"] = format_choice if format_choice else default_format
            
            # Handle constraints with contradiction detection
            constraints_input = self.get_safe_input(
                "\n🔒 Constraints (e.g., 'under 300 words, professional tone, include examples'): ",
                "Constraints",
                required=False
            )
            
            if constraints_input:
                constraint_list = self.parse_constraints_intelligently(constraints_input)
                contradictions = self.detect_contradictions(constraint_list)
                
                if contradictions:
                    print(f"\n⚠️  Contradictions detected:")
                    for contradiction in contradictions:
                        print(f"   📂 Category: {contradiction['category']}")
                        print(f"   ⚡ Conflicting: {', '.join(contradiction['conflicting_constraints'])}")
                        print("   💡 Suggestions:")
                        for suggestion in contradiction['suggestions']:
                            print(f"     • {suggestion}")
                    
                    resolve_choice = self.get_safe_input(
                        "\n🔧 Resolve contradictions? (y/n): ",
                        "Resolve choice",
                        valid_options=['y', 'yes', 'n', 'no']
                    ).lower()
                    
                    if resolve_choice in ['y', 'yes']:
                        constraints_input = self.get_safe_input(
                            "\n🔒 Please provide revised constraints: ",
                            "Revised constraints"
                        )
                        constraint_list = self.parse_constraints_intelligently(constraints_input)
                
                json_prompt["constraints"] = constraint_list
            
            # Category-specific fields
            if category == 'technical' and confidence > 0.3:
                complexity = self.get_safe_input(
                    "\n🔧 Technical complexity (beginner/intermediate/advanced): ",
                    "Technical complexity",
                    required=False,
                    valid_options=['beginner', 'intermediate', 'advanced', '']
                )
                if complexity:
                    json_prompt["complexity_level"] = complexity
            
            elif category == 'creative' and confidence > 0.3:
                tone = self.get_safe_input(
                    "\n🎨 Creative tone (professional/casual/humorous/serious): ",
                    "Creative tone",
                    required=False,
                    valid_options=['professional', 'casual', 'humorous', 'serious', '']
                )
                if tone:
                    json_prompt["tone"] = tone
            
            elif category == 'analysis' and confidence > 0.3:
                methodology = self.get_safe_input(
                    "\n📊 Analysis methodology (quantitative/qualitative/mixed): ",
                    "Analysis methodology",
                    required=False,
                    valid_options=['quantitative', 'qualitative', 'mixed', '']
                )
                if methodology:
                    json_prompt["methodology"] = methodology
            
            # Optional additional context
            context = self.get_safe_input(
                "\n📋 Additional context or input data (optional): ",
                "Additional context",
                required=False
            )
            if context:
                json_prompt["context"] = context
            
            # Add metadata
            json_prompt["metadata"] = {
                "version": self.version,
                "created_at": datetime.now().isoformat(),
                "quality_score": self.calculate_quality_score(json_prompt)
            }
            
            if technical_explanations:
                json_prompt["technical_explanations"] = technical_explanations
            
            if is_ambiguous and ambiguity_reason:
                json_prompt["original_ambiguity"] = ambiguity_reason
            
            return json_prompt
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            return {}
        except Exception as e:
            print(f"\n❌ An unexpected error occurred: {e}")
            print("Please try again with a simpler prompt.")
            return {}
    
    def display_result(self, json_prompt: Dict) -> None:
        """Display the result with formatting and analysis."""
        if not json_prompt:
            print("❌ No JSON prompt generated.")
            return
        
        print("\n" + "🎉 GENERATED JSON PROMPT:")
        print("─" * 50)
        
        try:
            # Create a clean version for display (remove metadata for main display)
            display_prompt = {k: v for k, v in json_prompt.items() if k != 'metadata'}
            json_output = json.dumps(display_prompt, indent=2, ensure_ascii=False)
            print(json_output)
            
            # Show analysis
            metadata = json_prompt.get('metadata', {})
            quality_score = metadata.get('quality_score', 0)
            
            print("\n📊 PROMPT ANALYSIS:")
            print("─" * 25)
            print(f"• Quality Score: {quality_score}/100 {'🟢' if quality_score >= 80 else '🟡' if quality_score >= 60 else '🔴'}")
            print(f"• Fields: {len(json_prompt) - 1}")  # -1 for metadata
            print(f"• Has constraints: {'Yes ✅' if 'constraints' in json_prompt else 'No ❌'}")
            print(f"• Has context: {'Yes ✅' if 'context' in json_prompt else 'No ❌'}")
            print(f"• Category: {json_prompt.get('category', 'general').title()}")
            print(f"• Confidence: {json_prompt.get('confidence', 0):.1%}")
            
            if quality_score < 70:
                print("\n💡 Suggestions for improvement:")
                if not json_prompt.get('constraints'):
                    print("  • Add specific constraints or requirements")
                if not json_prompt.get('context'):
                    print("  • Provide additional context or background")
                if json_prompt.get('confidence', 0) < 0.5:
                    print("  • Use more specific keywords for better categorization")
            
        except Exception as e:
            print(f"❌ Error generating output: {e}")
    
    def export_to_yaml(self, json_prompt: Dict) -> str:
        """Export prompt to YAML format."""
        return yaml.dump(json_prompt, default_flow_style=False, allow_unicode=True)
    
    def export_to_xml(self, json_prompt: Dict) -> str:
        """Export prompt to XML format."""
        root = ET.Element("prompt")
        
        def dict_to_xml(data, parent):
            for key, value in data.items():
                if isinstance(value, dict):
                    child = ET.SubElement(parent, key)
                    dict_to_xml(value, child)
                elif isinstance(value, list):
                    child = ET.SubElement(parent, key)
                    for item in value:
                        item_elem = ET.SubElement(child, "item")
                        item_elem.text = str(item)
                else:
                    child = ET.SubElement(parent, key)
                    child.text = str(value)
        
        dict_to_xml(json_prompt, root)
        return ET.tostring(root, encoding='unicode')
    
    def save_to_file(self, json_prompt: Dict) -> None:
        """Save the JSON prompt to a file with multiple format options."""
        try:
            # Get filename
            default_filename = f"prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            filename = self.get_safe_input(
                f"\n💾 Enter filename (default: {default_filename}): ",
                "Filename",
                required=False
            ) or default_filename
            
            # Get format
            export_format = self.get_safe_input(
                "\n📁 Export format (json/yaml/xml): ",
                "Export format",
                required=False,
                valid_options=['json', 'yaml', 'xml', '']
            ) or 'json'
            
            # Add appropriate extension
            if not filename.endswith(f'.{export_format}'):
                filename = f"{filename}.{export_format}"
            
            # Export in chosen format
            if export_format == 'yaml':
                content = self.export_to_yaml(json_prompt)
            elif export_format == 'xml':
                content = self.export_to_xml(json_prompt)
            else:  # default to json
                content = json.dumps(json_prompt, indent=2, ensure_ascii=False)
            
            # Write to file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Successfully saved to {filename}")
            print(f"📄 Format: {export_format.upper()}")
            print(f"📊 Size: {len(content)} characters")
            
        except Exception as e:
            print(f"❌ Error saving file: {e}")
    
    def load_from_file(self, filename: str) -> Optional[Dict]:
        """Load a previously saved prompt from file."""
        try:
            if not os.path.exists(filename):
                print(f"❌ File '{filename}' not found.")
                return None
            
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determine format by extension
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                return yaml.safe_load(content)
            elif filename.endswith('.xml'):
                # Simple XML parsing for our structure
                root = ET.fromstring(content)
                return self._xml_to_dict(root)
            else:  # assume json
                return json.loads(content)
                
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            return None
    
    def _xml_to_dict(self, element) -> Dict:
        """Convert XML element to dictionary."""
        result = {}
        
        for child in element:
            if len(child) == 0:
                result[child.tag] = child.text
            else:
                if child.tag == 'constraints' or child.tag == 'technical_explanations':
                    result[child.tag] = [item.text for item in child.findall('item')]
                else:
                    result[child.tag] = self._xml_to_dict(child)
        
        return result
    
    def show_statistics(self) -> None:
        """Show usage statistics if available."""
        stats_file = "converter_stats.json"
        
        try:
            if os.path.exists(stats_file):
                with open(stats_file, 'r') as f:
                    stats = json.load(f)
                
                print("\n📈 USAGE STATISTICS:")
                print("─" * 25)
                print(f"• Total prompts processed: {stats.get('total_prompts', 0)}")
                print(f"• Most common category: {stats.get('most_common_category', 'N/A')}")
                print(f"• Average quality score: {stats.get('avg_quality_score', 0):.1f}")
                print(f"• Files saved: {stats.get('files_saved', 0)}")
            else:
                print("\n📈 No usage statistics available yet.")
                
        except Exception as e:
            print(f"❌ Error loading statistics: {e}")
    
    def update_statistics(self, json_prompt: Dict) -> None:
        """Update usage statistics."""
        stats_file = "converter_stats.json"
        
        try:
            # Load existing stats
            if os.path.exists(stats_file):
                with open(stats_file, 'r') as f:
                    stats = json.load(f)
            else:
                stats = {
                    'total_prompts': 0,
                    'category_counts': {},
                    'quality_scores': [],
                    'files_saved': 0
                }
            
            # Update stats
            stats['total_prompts'] += 1
            
            category = json_prompt.get('category', 'general')
            stats['category_counts'][category] = stats['category_counts'].get(category, 0) + 1
            
            quality_score = json_prompt.get('metadata', {}).get('quality_score', 0)
            stats['quality_scores'].append(quality_score)
            
            # Calculate derived stats
            if stats['category_counts']:
                stats['most_common_category'] = max(stats['category_counts'], 
                                                  key=stats['category_counts'].get)
            
            if stats['quality_scores']:
                stats['avg_quality_score'] = sum(stats['quality_scores']) / len(stats['quality_scores'])
            
            # Save updated stats
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
                
        except Exception as e:
            print(f"⚠️  Warning: Could not update statistics: {e}")
    
    def show_help(self) -> None:
        """Display help information."""
        help_text = """
🆘 ENHANCED JSON PROMPT CONVERTER HELP

📋 BASIC USAGE:
  1. Enter your natural language prompt
  2. Review automatic analysis and suggestions
  3. Specify output format and constraints
  4. Get structured JSON output

🎯 WRITING EFFECTIVE PROMPTS:
  ✅ Good: "Create a Python web scraper for e-commerce sites with error handling"
  ❌ Avoid: "Make something good for websites"

  ✅ Good: "Analyze Q4 sales data focusing on mobile revenue trends"  
  ❌ Avoid: "Look at some data"

🏷️ CATEGORIES (Auto-detected):
  • Technical: build, code, develop, implement
  • Creative: write, create, compose, design
  • Analysis: analyze, compare, evaluate, assess
  • Research: research, investigate, study, explore
  • Planning: plan, strategy, roadmap, organize
  • Educational: explain, teach, tutorial, guide

🔒 CONSTRAINT EXAMPLES:
  • "under 300 words, professional tone"
  • "beginner-friendly, no technical jargon" 
  • "include examples, step-by-step format"

⚠️ COMMON ISSUES:
  • Ambiguous prompts → Tool provides clarifying questions
  • Contradictory constraints → Automatic detection and suggestions
  • Technical jargon → Automatic explanations provided

💾 FILE OPERATIONS:
  • Save in JSON, YAML, or XML formats
  • Load previously saved prompts
  • Automatic timestamping and metadata

📊 QUALITY SCORING:
  • 80-100: Excellent (comprehensive and clear)
  • 60-79: Good (minor improvements possible)  
  • 0-59: Needs improvement (add details/constraints)

🎨 TIPS FOR BETTER RESULTS:
  • Be specific about your goals
  • Include target audience information
  • Specify desired output format
  • Add relevant constraints
  • Use action-oriented language

🔧 COMMANDS:
  • Type 'help' for this information
  • Type 'stats' to see usage statistics
  • Type 'quit' or Ctrl+C to exit
        """
        print(help_text)


def main():
    """Main function with enhanced menu system and error handling."""
    converter = EnhancedJSONPromptConverter()
    
    print("🚀 Welcome to Enhanced JSON Prompt Converter v3.0!")
    print("Type 'help' for guidance, 'stats' for statistics, or 'quit' to exit.")
    
    try:
        while True:
            print("\n" + "═" * 60)
            
            # Check for special commands
            command = converter.get_safe_input(
                "\n🎯 Ready to convert a prompt? (or type 'help'/'stats'/'quit'): ",
                "Command",
                required=False
            ).lower().strip()
            
            if command in ['quit', 'exit', 'q']:
                print("\n👋 Thank you for using Enhanced JSON Prompt Converter!")
                break
            elif command in ['help', 'h', '?']:
                converter.show_help()
                continue
            elif command in ['stats', 'statistics']:
                converter.show_statistics()
                continue
            elif command in ['load', 'open']:
                filename = converter.get_safe_input(
                    "\n📁 Enter filename to load: ",
                    "Load filename"
                )
                loaded_prompt = converter.load_from_file(filename)
                if loaded_prompt:
                    print("\n✅ Loaded prompt:")
                    converter.display_result(loaded_prompt)
                continue
            elif command and command not in ['', 'y', 'yes']:
                print("❓ Unknown command. Type 'help' for available commands.")
                continue
            
            # Main conversion process
            json_prompt = converter.convert_to_json_prompt()
            
            if json_prompt:
                converter.display_result(json_prompt)
                converter.update_statistics(json_prompt)
                
                # Ask if user wants to save
                save_choice = converter.get_safe_input(
                    "\n💾 Save to file? (y/n): ",
                    "Save choice",
                    required=False,
                    valid_options=['y', 'yes', 'n', 'no', '']
                ).lower()
                
                if save_choice in ['y', 'yes']:
                    converter.save_to_file(json_prompt)
                    # Update file save statistics
                    try:
                        stats_file = "converter_stats.json"
                        if os.path.exists(stats_file):
                            with open(stats_file, 'r') as f:
                                stats = json.load(f)
                            stats['files_saved'] = stats.get('files_saved', 0) + 1
                            with open(stats_file, 'w') as f:
                                json.dump(stats, f, indent=2)
                    except:
                        pass  # Silently fail on stats update
            
            # Ask if user wants to continue
            continue_choice = converter.get_safe_input(
                "\n🔄 Create another prompt? (y/n): ",
                "Continue choice",
                required=False,
                valid_options=['y', 'yes', 'n', 'no', '']
            ).lower()
            
            if continue_choice in ['n', 'no']:
                print("\n🎉 Session complete! Thank you for using Enhanced JSON Prompt Converter!")
                converter.show_statistics()
                break
                
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Thanks for using Enhanced JSON Prompt Converter!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please restart the application.")


if __name__ == "__main__":
    # Check for required dependencies
    try:
        import yaml
    except ImportError:
        print("⚠️  Warning: PyYAML not installed. YAML export will not be available.")
        print("Install with: pip install PyYAML")
    
    main()