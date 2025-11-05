#!/usr/bin/env python3
"""
LLM-Powered JSON Prompt Converter - Clean Version
Uses Claude AI to intelligently detect and enhance vague prompts
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from datetime import datetime
import sys
import os

class LLMEnhancedJSONPromptConverter:
    """
    LLM-powered JSON prompt converter with intelligent prompt analysis and enhancement.
    """
    
    def __init__(self):
        self.version = "3.2"
        self.api_key = None
        self.valid_formats = [
            'json', 'text', 'table', 'markdown', 'html', 
            'csv', 'xml', 'code', 'yaml'
        ]
        
        # Enhanced category detection with technical keywords
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
    
    def setup_api_key(self):
        """Setup Anthropic API key from environment or user input."""
        import os
        
        # Try to get API key from environment variable first
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not self.api_key:
            print("\n🔑 Anthropic API Key Setup")
            print("=" * 40)
            print("To use AI-powered prompt enhancement, you need an Anthropic API key.")
            print("Get your API key from: https://console.anthropic.com/")
            print("\nOptions:")
            print("1. Set environment variable: ANTHROPIC_API_KEY=your_key_here")
            print("2. Enter key now (will be used for this session only)")
            print("3. Skip AI enhancement (use rule-based fallback)")
            
            choice = input("\nEnter choice (1/2/3): ").strip()
            
            if choice == "2":
                self.api_key = input("Enter your Anthropic API key: ").strip()
                if self.api_key:
                    print("✅ API key set for this session")
                else:
                    print("⚠️  No API key provided, using fallback enhancement")
            elif choice == "1":
                print("💡 Set your environment variable and restart the application")
                self.api_key = None
            else:
                print("⚠️  Skipping AI enhancement, using rule-based fallback")
                self.api_key = None
    
    def _call_claude_api(self, prompt: str) -> str:
        """Make API call to Claude for prompt enhancement."""
        if not self.api_key:
            return None
            
        try:
            import requests
            
            # Claude API endpoint
            url = "https://api.anthropic.com/v1/messages"
            
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 150,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                return result["content"][0]["text"]
            elif response.status_code == 401:
                print(f"❌ API Authentication failed. Please check your API key.")
                return None
            elif response.status_code == 429:
                print(f"⚠️  API rate limit exceeded. Using fallback enhancement.")
                return None
            else:
                print(f"⚠️  API Error {response.status_code}")
                return None
                
        except ImportError:
            print("⚠️  requests library not available. Install with: pip install requests")
            return None
        except Exception as e:
            print(f"⚠️  API call failed: {e}")
            return None
    
    def detect_ambiguity_with_llm(self, prompt: str) -> Tuple[bool, str, str, str]:
        """Use LLM to intelligently detect if a prompt is too vague or simple."""
        analysis_prompt = f"""
You are a prompt quality analyzer. Evaluate if the following prompt is clear and specific enough for execution.

PROMPT TO ANALYZE: "{prompt}"

Analyze this prompt and determine:
1. Is it too vague or ambiguous?
2. Does it lack necessary context or details?
3. Is it clear what the user wants?

Respond ONLY with a JSON object in this exact format:
{{
  "is_problematic": true/false,
  "issue_type": "vague|ambiguous|unclear|missing_context|too_simple|acceptable",
  "enhanced_prompt": "improved version of the prompt with specific details",
  "explanation": "brief explanation of what was unclear"
}}

Examples:
- "fix the code" → is_problematic: true, issue_type: "vague"
- "create a Python web scraper for e-commerce sites" → is_problematic: false, issue_type: "acceptable"

Respond with ONLY the JSON object, no other text.
"""

        try:
            # Try LLM analysis first
            response = self._call_claude_api(analysis_prompt)
            
            if response:
                # Clean the response to extract just the JSON
                json_response = self._extract_json_from_response(response)
                
                if json_response:
                    is_problematic = json_response.get('is_problematic', False)
                    issue_type = json_response.get('issue_type', 'unknown')
                    enhanced_prompt = json_response.get('enhanced_prompt', prompt)
                    explanation = json_response.get('explanation', 'No explanation provided')
                    
                    return is_problematic, issue_type, enhanced_prompt, explanation
            
            # Fallback to simple rule-based detection
            return self._fallback_detect_ambiguity(prompt)
            
        except Exception as e:
            print(f"⚠️  LLM analysis failed: {e}")
            return self._fallback_detect_ambiguity(prompt)
    
    def _extract_json_from_response(self, response: str) -> dict:
        """Extract JSON object from LLM response."""
        try:
            # Remove any markdown formatting
            response = response.replace('```json', '').replace('```', '').strip()
            
            # Try to find JSON object in the response
            import json
            
            # First try to parse the entire response
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # If that fails, try to find JSON within the response
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    return json.loads(json_str)
                
                return None
                
        except Exception as e:
            print(f"⚠️  JSON extraction failed: {e}")
            return None
    
    def _fallback_detect_ambiguity(self, prompt: str) -> Tuple[bool, str, str, str]:
        """Fallback ambiguity detection when LLM is unavailable."""
        prompt_lower = prompt.lower().strip()
        
        # Simple rules as fallback
        vague_patterns = [
            'fix code', 'fix the code', 'debug code', 'create app', 'build system',
            'make website', 'write function', 'improve performance'
        ]
        
        # Check for obviously vague patterns
        if any(pattern in prompt_lower for pattern in vague_patterns):
            enhanced = self._simple_enhance(prompt)
            return True, "vague", enhanced, "Prompt lacks specific context and details"
        
        # Check for very short prompts
        if len(prompt.split()) <= 2:
            enhanced = f"Create a detailed implementation of {prompt}"
            return True, "too_simple", enhanced, "Prompt is too brief and lacks detail"
        
        # Check for pronouns without context
        if any(f" {pronoun} " in f" {prompt_lower} " for pronoun in ['it', 'this', 'that']):
            enhanced = self._simple_enhance(prompt)
            return True, "ambiguous", enhanced, "Contains unclear pronoun references"
        
        return False, "acceptable", prompt, "Prompt appears to be clear and specific"
    
    def _simple_enhance(self, prompt: str) -> str:
        """Simple rule-based enhancement as fallback."""
        prompt_lower = prompt.lower()
        
        # Basic improvements
        if 'fix code' in prompt_lower or 'fix the code' in prompt_lower:
            return "debug and resolve specific issues in code implementation"
        elif 'create app' in prompt_lower:
            return "develop a complete application with core functionality"
        elif 'build system' in prompt_lower:
            return "design and implement a comprehensive system architecture"
        else:
            return f"create a detailed and specific implementation of {prompt}"
    
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
        
        # Penalty for original issues
        if json_prompt.get('original_issue'):
            score -= 10
        
        return max(0, min(100, score))
    
    def convert_to_json_prompt(self) -> Dict:
        """Main conversion method with LLM-powered enhancement."""
        print("🚀 LLM-Enhanced JSON Prompt Converter v3.2")
        print("=" * 60)
        print("🤖 Powered by Claude AI for intelligent prompt analysis!")
        
        try:
            # Get main prompt
            prompt = self.get_safe_input(
                "\n📝 Enter your prompt: ",
                "Main prompt"
            )
            
            # LLM-powered ambiguity detection
            is_problematic, issue_type, enhanced_prompt, explanation = self.detect_ambiguity_with_llm(prompt)
            
            if is_problematic:
                print(f"\n⚠️  Issue detected: {issue_type}")
                print(f"💡 Analysis: {explanation}")
                print("🤖 Auto-enhancing with AI...")
                
                print(f"📝 Original: '{prompt}'")
                print(f"✨ AI Enhanced: '{enhanced_prompt}'")
                
                # Use the enhanced prompt
                prompt = enhanced_prompt
            
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
            
            # Add enhancement information if detected
            if is_problematic and issue_type:
                json_prompt["original_issue"] = issue_type
                json_prompt["enhancement_explanation"] = explanation
            
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
    converter = LLMEnhancedJSONPromptConverter()
    
    print("🚀 Welcome to LLM-Enhanced JSON Prompt Converter v3.2!")
    print("🤖 Powered by Claude AI for intelligent prompt analysis and enhancement!")
    
    # Setup API key for AI enhancement
    converter.setup_api_key()
    
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
