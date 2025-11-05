
import os
import json
import argparse
import google.generativeai as genai

def main():
    """
    Analyzes a natural language prompt using the Gemini API and extracts structured data.
    """
    # 1. Configure API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        return
    genai.configure(api_key=api_key)

    # 2. Command-Line Input
    parser = argparse.ArgumentParser(description="A smart assistant CLI to extract structured data from a prompt.")
    parser.add_argument("prompt", type=str, help="The natural language prompt to analyze.")
    args = parser.parse_args()
    user_prompt = args.prompt

    # 3. Define the meta-prompt and JSON schema for the model
    meta_prompt = f"""
    Analyze the following user prompt and extract the information into a structured JSON object.
    Adhere strictly to the schema below. The keys must be in English.

    **Important Instructions for Language Detection:**
    - For the "original_language" field, you MUST identify the language of the main subject or the text that is being acted upon.
    - Do NOT use the language of the instructions. For example, if the prompt is "Translate 'Bonjour' to English", the original_language is 'fr', not 'en'.

    JSON Schema:
    {{
      "intent": "The primary action the user wants to perform (e.g., 'create', 'analyze', 'translate').",
      "subject": "The main topic or object of the intent (e.g., 'a website', 'sales data', 'the sentence `Bonjour`').",
      "entities": {{
        "key_details": ["A list of specific details, constraints, or parameters mentioned."],
        "source": "The origin of the data or subject, if mentioned.",
        "target": "The destination or desired outcome, if mentioned."
      }},
      "output_format": "The desired format for the final result (e.g., 'JSON', 'a 3-bullet summary').",
      "original_language": "The detected two-letter language code of the primary subject or text to be processed, NOT the language of the instructions. (e.g., 'en', 'es', 'fr')."
    }}

    User Prompt:
    "{user_prompt}"

    Respond ONLY with the generated JSON object. Do not include any other text or formatting.
    """

    # 4. Core Logic: Send request to Gemini API
    try:
        model = genai.GenerativeModel('gemini-pro-latest')
        response = model.generate_content(meta_prompt)
        
        # Clean up the response to ensure it's a valid JSON string
        # The model sometimes wraps the JSON in ```json ... ```
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        
        # 5. Parse and print the JSON output
        parsed_json = json.loads(response_text)
        print(json.dumps(parsed_json, indent=2, ensure_ascii=False))

    except json.JSONDecodeError:
        print("Error: The model returned a malformed JSON string. Please try again.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
