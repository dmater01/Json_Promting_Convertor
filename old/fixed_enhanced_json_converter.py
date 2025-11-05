#!/usr/bin/env python3
"""
Fixed Enhanced JSON Prompt Converter - Addressing Categorization Issues
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from datetime import datetime
import sys
import os

class FixedEnhancedJSONPromptConverter:
    """
    Fixed version with improved categorization and better handling of technical prompts.
    """
    
    def __init__(self):
        self.version = "3.1"
        self.valid_formats = [
            'json', 'text', 'table', 'markdown', 'html', 
            'csv', 'xml', 'code', 'yaml'
        ]
        
        # FIXED: Better category detection with more specific technical keywords
        self.prompt_categories = {
            'technical': {
                'primary': ['build', 'develop', 'code', 'implement', 'debug', 'optimize', 'deploy', 'program', 'script', 'api'],
                'secondary': ['python', 'javascript', 'database', 'software', 'system', 'application', 'function', 'algorithm', 'web scraper', 'scraping']
            },
            'analysis': {
                'primary': ['analyze', 'compare', 'evaluate', 'assess', 'examine', 'review', 'audit', 'study'],
                'secondary': ['data', 'metrics', 'performance', 'trends', 'insights', 'statistics', 'benchmark']
            },
            'creative': {
                'primary': ['write', 'compose', 'draft', 'story', 'poem', 'article'],
                'secondary': ['creative', 'narrative', 'blog', 'copy', 'content marketing']
            },
            'research': {
                'primary': ['research', 'investigate', 'study', 'explore', 'survey'],
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
        
        # Technical indicators for better detection
        self.technical_indicators = [
            'web scraper', 'scraping', 'python', 'javascript', 'api', 'database', 
            'script', 'function', 'code', 'programming', 'software', 'app',
            'error handling', 'exception handling', 'logging'
        ]
    
    def detect_category_with_confidence(self, prompt: str) -> Tuple[str, float]:
        """Improved category detection with better technical recognition."""
        prompt_lower = prompt.lower()
        category_scores = defaultdict(float)
        
        # Special handling for technical prompts
        tech_score = 0
        for indicator in self.technical_indicators:
            if indicator in prompt_lower:
                tech_score += 3.0  # High weight for technical indicators
        
        if tech_score > 0:
            category_scores['technical'] = tech_score
        
        # Regular category scoring
        for category, keywords in self.prompt_categories.items():
            primary_score = sum(2.0 for keyword in keywords['primary'] 
                              if keyword in prompt_lower)
            secondary_score = sum(1.0 for keyword in keywords['secondary'] 
                                if keyword in prompt_lower)
            
            if any(prompt_lower.startswith(keyword) for keyword in keywords['primary']):
                primary_score += 1.0
            
            category_scores[category] += primary_score + secondary_score
        
        if not category_scores or max(category_scores.values()) == 0:
            return 'general', 0.0
        
        best_category = max(category_scores, key=category_scores.get)
        total_score = sum(category_scores.values())
        confidence = category_scores[best_category] / total_score if total_score > 0 else 0.0
        
        return best_category, min(confidence, 0.95)
    
    def extract_task_with_fallbacks(self, prompt: str) -> str:
        """Enhanced task extraction with better handling of technical prompts."""
        prompt = prompt.strip()
        
        if len(prompt) <= 5:
            return f"Execute: {prompt}"
        
        # Strategy 1: Handle technical verb patterns first
        tech_patterns = [
            r'^(create|build|develop|implement|code|program|write)\s+(?:a\s+)?(.+?)(?:\s+(?:for|with|using|that|which).*)?$',
            r'^(?:please\s+|can you\s+)?(create|build|develop|implement|code|program|write)\s+(?:a\s+)?(.+?)(?:\s+(?:for|with|using|that|which).*)?$'
        ]
        
        for pattern in tech_patterns:
            match = re.search(pattern, prompt.lower())
            if match:
                verb, object_part = match.groups()
                return f"{verb.capitalize()} {object_part.strip()}"
        
        # Strategy 2: Handle preposition patterns with exclusions
        exclusions = ['turn on', 'based on', 'focus on', 'work on', 'click on']
        
        if " with " in prompt and not any(prompt.lower().startswith(exclude) for exclude in exclusions):
            parts = prompt.split(" with ", 1)
            if len(parts[0].strip()) > 3:
                return parts[0].strip()
        
        # Strategy 3: Smart truncation for long prompts
        if len(prompt) > 100:
            sentences = re.split(r'[.!?]', prompt)
            if sentences and len(sentences[0].strip()) < len(prompt) * 0.7:
                return sentences[0].strip()
            
            words = prompt.split()
            if len(words) > 15:
                return ' '.join(words[:15]) + '...'
        
        return prompt
    
    def detect_ambiguity(self, prompt: str) -> Tuple[bool, str, List[str]]:
        """Detect if a prompt is too ambiguous and provide guidance."""
        prompt_lower = prompt.lower().strip()
        
        # Check for ultra-vague patterns
        ambiguous_triggers = [
            'make it', 'fix it', 'improve', 'better', 'good', 'nice', 
            'enhance', 'optimize', 'update', 'modify'
        ]
        
        vague_score = sum(1 for trigger in ambiguous_triggers 
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
    
    def get_safe_input(self, prompt_text: str, field_name: str, required: bool = True, 
                      valid_options: Optional[List[str]] = None) -> str:
        """Simplified safe input with better validation."""
        while True:
            try:
                user_input = input(prompt_text).strip()
                
                if not user_input and required:
                    print(f"❌ {field_name} is required. Please try again.")
                    continue
                
                if not user_input and not required:
                    return ""
                
                if valid_options:
                    valid_lower = [opt.lower() for opt in valid_options]
                    if user_input.lower() not in valid_lower and user_input.lower() != '':
                        print(f"❌ Invalid option. Valid choices: {', '.join(valid_options)}")
                        continue
                
                # Basic validation for problematic characters
                if field_name == "Filename" and ('\\' in user_input or '/' in user_input):
                    print("❌ Please use only the filename without path separators.")
                    continue
                
                return user_input
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                sys.exit(0)
            except Exception as e:
                print(f"❌ Error reading input: {e}")
                continue
    
    def calculate_quality_score(self, json_prompt: Dict) -> int:
        """Calculate quality score for the prompt."""
        score = 20  # Base score
        
        # Category confidence
        confidence = json_prompt.get('confidence', 0)
        score += int(confidence * 20)
        
        # Format specification
        if json_prompt.get('format'):
            score += 10
        
        # Constraints
        constraints = json_prompt.get('constraints', [])
        if constraints:
            score += min(len(constraints) * 5, 20)
        
        # Additional fields
        additional_fields = ['complexity_level', 'tone', 'methodology', 'context']
        for field in additional_fields:
            if json_prompt.get(field):
                score += 5
        
        # Penalty for ambiguity
        if json_prompt.get('original_ambiguity'):
            score -= 10
        
        return max(0, min(100, score))
    
    def convert_to_json_prompt(self) -> Dict:
        """Main conversion method with fixes."""
        print("🚀 Fixed Enhanced JSON Prompt Converter v3.1")
        print("=" * 60)
        print("✨ Fixed categorization and file handling issues!")
        
        try:
            # Get main prompt
            prompt = self.get_safe_input(
                "\n📝 Enter your prompt: ",
                "Main prompt"
            )
            
            # Edge case analysis - RESTORED!
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
            
            # Build JSON structure
            json_prompt = {
                "task": task,
                "category": category,
                "confidence": round(confidence, 2)
            }
            
            # Smart format defaults
            if category == 'technical' or any(word in prompt.lower() for word in ['code', 'script', 'api', 'program']):
                default_format = 'code'
            elif category == 'analysis':
                default_format = 'json'
            else:
                default_format = 'text'
            
            format_choice = self.get_safe_input(
                f"\n📄 Output format (default: {default_format}) - Options: {'/'.join(self.valid_formats)}: ",
                "Output format",
                required=False,
                valid_options=self.valid_formats + ['']
            )
            
            json_prompt["format"] = format_choice if format_choice else default_format
            
            # Get constraints
            constraints_input = self.get_safe_input(
                "\n🔒 Constraints (e.g., 'under 300 words, professional tone, include examples'): ",
                "Constraints",
                required=False
            )
            
            if constraints_input:
                constraint_list = [c.strip() for c in re.split(r'[,;]', constraints_input) if c.strip()]
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
            
            # Optional context
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
            
            # Add ambiguity information if detected
            if is_ambiguous and ambiguity_reason:
                json_prompt["original_ambiguity"] = ambiguity_reason
            
            return json_prompt
            
        except Exception as e:
            print(f"\n❌ An unexpected error occurred: {e}")
            return {}
    
    def display_result(self, json_prompt: Dict) -> None:
        """Display results with better formatting."""
        if not json_prompt:
            print("❌ No JSON prompt generated.")
            return
        
        print("\n" + "🎉 GENERATED JSON PROMPT:")
        print("─" * 50)
        
        try:
            # Clean version for display
            display_prompt = {k: v for k, v in json_prompt.items() if k != 'metadata'}
            json_output = json.dumps(display_prompt, indent=2, ensure_ascii=False)
            print(json_output)
            
            # Analysis
            metadata = json_prompt.get('metadata', {})
            quality_score = metadata.get('quality_score', 0)
            
            print("\n📊 PROMPT ANALYSIS:")
            print("─" * 25)
            print(f"• Quality Score: {quality_score}/100 {'🟢' if quality_score >= 80 else '🟡' if quality_score >= 60 else '🔴'}")
            print(f"• Fields: {len(json_prompt) - 1}")
            print(f"• Has constraints: {'Yes ✅' if 'constraints' in json_prompt else 'No ❌'}")
            print(f"• Has context: {'Yes ✅' if 'context' in json_prompt else 'No ❌'}")
            print(f"• Category: {json_prompt.get('category', 'general').title()}")
            print(f"• Confidence: {json_prompt.get('confidence', 0):.1%}")
            
        except Exception as e:
            print(f"❌ Error displaying results: {e}")
    
    def save_to_file(self, json_prompt: Dict) -> None:
        """Simplified file saving with better validation."""
        try:
            default_filename = f"prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            filename = self.get_safe_input(
                f"\n💾 Enter filename (default: {default_filename}): ",
                "Filename",
                required=False
            ) or default_filename
            
            # Ensure .json extension
            if not filename.endswith('.json'):
                filename += '.json'
            
            # Save file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(json_prompt, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Successfully saved to {filename}")
            
        except Exception as e:
            print(f"❌ Error saving file: {e}")


def main():
    """Main function with better error handling."""
    converter = FixedEnhancedJSONPromptConverter()
    
    print("🚀 Welcome to Fixed Enhanced JSON Prompt Converter v3.1!")
    print("This version fixes the categorization and file handling issues.")
    
    try:
        while True:
            print("\n" + "═" * 60)
            
            command = converter.get_safe_input(
                "\n🎯 Ready to convert a prompt? (or type 'quit' to exit): ",
                "Command",
                required=False
            ).lower().strip()
            
            if command in ['quit', 'exit', 'q']:
                print("\n👋 Thank you for using the converter!")
                break
            
            # Main conversion
            json_prompt = converter.convert_to_json_prompt()
            
            if json_prompt:
                converter.display_result(json_prompt)
                
                # Save option
                save_choice = converter.get_safe_input(
                    "\n💾 Save to file? (y/n): ",
                    "Save choice",
                    required=False,
                    valid_options=['y', 'yes', 'n', 'no', '']
                ).lower()
                
                if save_choice in ['y', 'yes']:
                    converter.save_to_file(json_prompt)
            
            # Continue option
            continue_choice = converter.get_safe_input(
                "\n🔄 Create another prompt? (y/n): ",
                "Continue choice",
                required=False,
                valid_options=['y', 'yes', 'n', 'no', '']
            ).lower()
            
            if continue_choice in ['n', 'no']:
                print("\n🎉 Session complete!")
                break
                
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()