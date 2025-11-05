import json
import re
from typing import Dict, List, Optional, Union
import sys

class JSONPromptConverter:
    """
    Enhanced JSON prompt converter with validation, smart parsing, and templates.
    """
    
    def __init__(self):
        self.valid_formats = ['json', 'text', 'table', 'markdown', 'html', 'csv', 'xml']
        self.prompt_categories = {
            'analysis': ['analyze', 'compare', 'evaluate', 'assess', 'examine', 'review'],
            'creative': ['write', 'create', 'compose', 'generate', 'craft', 'design'],
            'technical': ['build', 'develop', 'code', 'implement', 'debug', 'optimize'],
            'research': ['research', 'investigate', 'study', 'explore', 'survey'],
            'planning': ['plan', 'strategy', 'roadmap', 'schedule', 'organize']
        }
    
    def validate_input(self, text: str, field_name: str) -> bool:
        """Validate user input for safety and completeness."""
        if not text or not text.strip():
            print(f"⚠️  Warning: {field_name} cannot be empty")
            return False
        
        # Check for potentially problematic characters
        if any(char in text for char in ['"', "'", '\\', '\n', '\r']):
            print(f"⚠️  Warning: {field_name} contains special characters that may cause JSON issues")
            return True  # Allow but warn
        
        return True
    
    def detect_category(self, prompt: str) -> str:
        """Detect the category of the prompt based on keywords."""
        prompt_lower = prompt.lower()
        category_scores = {}
        
        for category, keywords in self.prompt_categories.items():
            score = sum(1 for keyword in keywords if keyword in prompt_lower)
            category_scores[category] = score
        
        if max(category_scores.values()) == 0:
            return 'general'
        
        return max(category_scores, key=category_scores.get)
    
    def extract_task_intelligently(self, prompt: str) -> str:
        """
        Extract the main task from a prompt using multiple parsing strategies.
        """
        prompt = prompt.strip()
        
        # Strategy 1: Handle "X on Y" pattern (original logic)
        if " on " in prompt and not prompt.startswith("Turn on") and not prompt.startswith("Based on"):
            parts = prompt.split(" on ", 1)
            if len(parts[0]) > 3:  # Ensure meaningful task
                return parts[0].strip()
        
        # Strategy 2: Handle "X for Y" pattern
        if " for " in prompt:
            parts = prompt.split(" for ", 1)
            if len(parts[0]) > 3:
                return parts[0].strip()
        
        # Strategy 3: Handle imperative verbs at start
        verb_patterns = [
            r'^(create|generate|write|build|develop|analyze|compare|make|design|implement)\s+(.+?)(?:\s+(?:for|with|using|in|about)|$)',
            r'^(help me|please)\s+(create|generate|write|build|develop|analyze|compare|make|design|implement)\s+(.+?)(?:\s+(?:for|with|using|in|about)|$)'
        ]
        
        for pattern in verb_patterns:
            match = re.search(pattern, prompt.lower())
            if match:
                if len(match.groups()) == 2:
                    return f"{match.group(1).capitalize()} {match.group(2)}"
                elif len(match.groups()) == 3:
                    return f"{match.group(2).capitalize()} {match.group(3)}"
        
        # Strategy 4: Return full prompt if no pattern matches
        return prompt
    
    def parse_constraints_intelligently(self, constraints_text: str) -> List[str]:
        """Parse constraints with smart detection of common patterns."""
        if not constraints_text:
            return []
        
        constraints = []
        
        # Split by common delimiters
        raw_constraints = re.split(r'[,;]|\\band\\b', constraints_text)
        
        for constraint in raw_constraints:
            constraint = constraint.strip()
            if not constraint:
                continue
            
            # Normalize common patterns
            constraint = re.sub(r'^(no|without)\\s+', 'no ', constraint.lower())
            constraint = re.sub(r'^(use|include|with)\\s+', 'include ', constraint.lower())
            constraint = re.sub(r'^(under|less than|max|maximum)\\s+(\\d+)\\s+words?', r'under \\2 words', constraint)
            
            constraints.append(constraint)
        
        return constraints
    
    def get_safe_input(self, prompt: str, field_name: str, required: bool = True, 
                      valid_options: Optional[List[str]] = None) -> str:
        """Get user input with validation and error handling."""
        while True:
            try:
                user_input = input(prompt).strip()
                
                if not user_input and required:
                    print(f"❌ {field_name} is required. Please try again.")
                    continue
                
                if not user_input and not required:
                    return ""
                
                if valid_options and user_input.lower() not in [opt.lower() for opt in valid_options]:
                    print(f"❌ Invalid option. Valid choices: {', '.join(valid_options)}")
                    continue
                
                if self.validate_input(user_input, field_name):
                    return user_input
                    
            except KeyboardInterrupt:
                print("\\n👋 Goodbye!")
                sys.exit(0)
            except Exception as e:
                print(f"❌ Error reading input: {e}")
                continue
    
    def convert_to_json_prompt(self) -> Dict:
        """
        Enhanced conversion with better UX and validation.
        """
        print("🚀 Enhanced JSON Prompt Converter")
        print("=" * 50)
        
        try:
            # Get the main prompt
            generic_prompt = self.get_safe_input(
                "\\n📝 Enter your prompt: ",
                "Main prompt"
            )
            
            # Detect category and show it
            category = self.detect_category(generic_prompt)
            print(f"\\n🎯 Detected category: {category.upper()}")
            
            # Extract task intelligently
            extracted_task = self.extract_task_intelligently(generic_prompt)
            print(f"📋 Extracted task: {extracted_task}")
            
            # Ask user to confirm or modify task
            task_confirmed = self.get_safe_input(
                f"\\n✏️  Confirm task (press Enter to keep '{extracted_task}' or type new): ",
                "Task confirmation",
                required=False
            )
            
            final_task = task_confirmed if task_confirmed else extracted_task
            
            # Build the JSON structure
            json_prompt = {"task": final_task}
            
            # Get output format with validation
            output_format = self.get_safe_input(
                f"\\n📄 Output format ({'/'.join(self.valid_formats)}): ",
                "Output format",
                valid_options=self.valid_formats
            ).lower()
            json_prompt["format"] = output_format
            
            # Get constraints with smart parsing
            constraints_input = self.get_safe_input(
                "\\n🔒 Constraints (e.g., 'under 200 words, no jargon') or press Enter to skip: ",
                "Constraints",
                required=False
            )
            
            if constraints_input:
                json_prompt["constraints"] = self.parse_constraints_intelligently(constraints_input)
            
            # Get input data
            input_data = self.get_safe_input(
                "\\n📊 Input data/context (optional): ",
                "Input data",
                required=False
            )
            
            if input_data:
                json_prompt["input"] = input_data
            
            # Add category-specific fields
            if category != 'general':
                json_prompt["category"] = category
                
                # Category-specific enhancements
                if category == 'technical':
                    tech_level = self.get_safe_input(
                        "\\n🔧 Technical level (beginner/intermediate/advanced) or press Enter to skip: ",
                        "Technical level",
                        required=False,
                        valid_options=['beginner', 'intermediate', 'advanced', '']
                    )
                    if tech_level:
                        json_prompt["complexity_level"] = tech_level
                
                elif category == 'creative':
                    tone = self.get_safe_input(
                        "\\n🎨 Tone (professional/casual/humorous/serious) or press Enter to skip: ",
                        "Tone",
                        required=False,
                        valid_options=['professional', 'casual', 'humorous', 'serious', '']
                    )
                    if tone:
                        json_prompt["tone"] = tone
            
            return json_prompt
            
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            return {}
    
    def display_result(self, json_prompt: Dict) -> None:
        """Display the result with formatting and validation."""
        if not json_prompt:
            print("❌ No JSON prompt generated.")
            return
        
        print("\\n" + "🎉 GENERATED JSON PROMPT:")
        print("─" * 40)
        
        try:
            json_output = json.dumps(json_prompt, indent=2, ensure_ascii=False)
            print(json_output)
            
            # Provide some analysis
            print("\\n📊 PROMPT ANALYSIS:")
            print("─" * 20)
            print(f"• Fields: {len(json_prompt)}")
            print(f"• Has constraints: {'Yes' if 'constraints' in json_prompt else 'No'}")
            print(f"• Has input data: {'Yes' if 'input' in json_prompt else 'No'}")
            print(f"• Category: {json_prompt.get('category', 'general')}")
            
        except Exception as e:
            print(f"❌ Error generating JSON: {e}")
    
    def save_to_file(self, json_prompt: Dict) -> None:
        """Save the JSON prompt to a file."""
        try:
            filename = self.get_safe_input(
                "\\n💾 Enter filename (default: prompt.json): ",
                "Filename",
                required=False
            ) or "prompt.json"
            
            if not filename.endswith('.json'):
                filename += '.json'
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(json_prompt, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved to {filename}")
            
        except Exception as e:
            print(f"❌ Error saving file: {e}")

def main():
    """Main function with error handling and user experience improvements."""
    converter = JSONPromptConverter()
    
    try:
        while True:
            json_prompt = converter.convert_to_json_prompt()
            
            if json_prompt:
                converter.display_result(json_prompt)
                
                # Ask if user wants to save
                save_choice = converter.get_safe_input(
                    "\\n💾 Save to file? (y/n): ",
                    "Save choice",
                    required=False,
                    valid_options=['y', 'n', 'yes', 'no', '']
                ).lower()
                
                if save_choice in ['y', 'yes']:
                    converter.save_to_file(json_prompt)
            
            # Ask if user wants to continue
            continue_choice = converter.get_safe_input(
                "\\n🔄 Create another prompt? (y/n): ",
                "Continue choice",
                required=False,
                valid_options=['y', 'n', 'yes', 'no', '']
            ).lower()
            
            if continue_choice in ['n', 'no', '']:
                print("\\n👋 Thank you for using JSON Prompt Converter!")
                break
                
    except KeyboardInterrupt:
        print("\\n\\n👋 Goodbye!")
    except Exception as e:
        print(f"\\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()