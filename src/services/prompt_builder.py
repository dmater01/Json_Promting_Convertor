"""Prompt builder for constructing meta-prompts for LLM processing.

This module implements the meta-prompt pattern validated in the research CLI tools
(json_assistant_cli.py and structured_assistant_cli.py).
"""

from typing import Any, Dict, Optional

from src.schemas.requests import AnalyzeRequest, OutputFormat


class PromptBuilder:
    """
    Builds structured meta-prompts for LLM analysis.

    Based on the research from json_assistant_cli.py and structured_assistant_cli.py,
    this class constructs prompts that instruct the LLM to extract structured data
    from natural language inputs.
    """

    # Core schema template based on research CLI tools
    CORE_SCHEMA = {
        "intent": "The primary action the user wants to perform (e.g., 'create', 'analyze', 'translate').",
        "subject": "The main topic or object of the intent (e.g., 'a website', 'sales data', 'the sentence `Bonjour`').",
        "entities": {
            "key_details": ["A list of specific details, constraints, or parameters mentioned."],
            "source": "The origin of the data or subject, if mentioned.",
            "target": "The destination or desired outcome, if mentioned.",
        },
        "output_format": "The desired format for the final result (e.g., 'JSON', 'a 3-bullet summary').",
        "original_language": "The detected two-letter language code of the primary subject or text to be processed, NOT the language of the instructions. (e.g., 'en', 'es', 'fr').",
    }

    LANGUAGE_DETECTION_INSTRUCTIONS = """
**Important Instructions for Language Detection:**
- For the "original_language" field, you MUST identify the language of the main subject or the text that is being acted upon.
- Do NOT use the language of the instructions. For example, if the prompt is "Translate 'Bonjour' to English", the original_language is 'fr', not 'en'.
"""

    def __init__(self):
        """Initialize the prompt builder."""
        pass

    def build_meta_prompt(
        self,
        request: AnalyzeRequest,
        custom_schema: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Build a meta-prompt for LLM analysis.

        Args:
            request: The analyze request containing the user prompt
            custom_schema: Optional custom JSON schema to override the default

        Returns:
            Formatted meta-prompt string for the LLM
        """
        user_prompt = request.prompt
        schema = custom_schema or self.CORE_SCHEMA

        # Format the schema as a readable JSON-like structure
        schema_str = self._format_schema(schema)

        meta_prompt = f"""
Analyze the following user prompt and extract the information into a structured JSON object.
Adhere strictly to the schema below. The keys must be in English.

{self.LANGUAGE_DETECTION_INSTRUCTIONS}

JSON Schema:
{schema_str}

User Prompt:
"{user_prompt}"

Respond ONLY with the generated JSON object. Do not include any other text or formatting.
"""
        return meta_prompt.strip()

    def build_custom_schema_prompt(
        self,
        request: AnalyzeRequest,
        schema: Dict[str, Any],
    ) -> str:
        """
        Build a meta-prompt with a custom JSON schema.

        This is used when the user provides their own schema_definition in the request.

        Args:
            request: The analyze request
            schema: Custom JSON schema provided by the user

        Returns:
            Formatted meta-prompt with custom schema
        """
        user_prompt = request.prompt
        schema_str = self._format_schema(schema)

        meta_prompt = f"""
Analyze the following user prompt and extract the information according to the custom schema provided below.
Adhere strictly to this schema. Return valid JSON.

Custom Schema:
{schema_str}

User Prompt:
"{user_prompt}"

Respond ONLY with the generated JSON object matching the schema. Do not include any other text or formatting.
"""
        return meta_prompt.strip()

    def _format_schema(self, schema: Dict[str, Any], indent: int = 0) -> str:
        """
        Format a JSON schema as a readable string for inclusion in the prompt.

        Args:
            schema: JSON schema dictionary
            indent: Current indentation level

        Returns:
            Formatted schema string
        """
        lines = []
        indent_str = "  " * indent

        if isinstance(schema, dict):
            lines.append("{")
            for i, (key, value) in enumerate(schema.items()):
                comma = "," if i < len(schema) - 1 else ""
                if isinstance(value, (dict, list)):
                    formatted_value = self._format_schema(value, indent + 1)
                    lines.append(f'{indent_str}  "{key}": {formatted_value}{comma}')
                elif isinstance(value, str):
                    # Escape quotes in strings
                    escaped_value = value.replace('"', '\\"')
                    lines.append(f'{indent_str}  "{key}": "{escaped_value}"{comma}')
                else:
                    lines.append(f'{indent_str}  "{key}": {value}{comma}')
            lines.append(f"{indent_str}}}")
        elif isinstance(schema, list):
            if len(schema) == 0:
                return "[]"
            lines.append("[")
            for i, item in enumerate(schema):
                comma = "," if i < len(schema) - 1 else ""
                formatted_item = self._format_schema(item, indent + 1)
                lines.append(f"{indent_str}  {formatted_item}{comma}")
            lines.append(f"{indent_str}]")
        else:
            return str(schema)

        return "\n".join(lines)

    def add_confidence_scoring(self, base_prompt: str) -> str:
        """
        Add confidence scoring instructions to the prompt.

        Args:
            base_prompt: The base meta-prompt

        Returns:
            Enhanced prompt with confidence scoring
        """
        confidence_instruction = """
Additionally, include a "confidence_score" field (0.0 to 1.0) indicating your confidence in the extraction accuracy.
"""
        # Insert before the "Respond ONLY" instruction
        parts = base_prompt.split("Respond ONLY")
        if len(parts) == 2:
            return parts[0] + confidence_instruction + "\nRespond ONLY" + parts[1]
        return base_prompt

    def add_xml_formatting(self, base_prompt: str) -> str:
        """
        Modify the prompt to request XML output instead of JSON.

        Args:
            base_prompt: The base meta-prompt requesting JSON

        Returns:
            Modified prompt requesting XML output
        """
        # Replace JSON references with XML
        xml_prompt = base_prompt.replace("JSON object", "XML structure")
        xml_prompt = xml_prompt.replace("JSON Schema:", "XML Structure:")
        xml_prompt = xml_prompt.replace(
            "Respond ONLY with the generated JSON object",
            "Respond ONLY with the generated XML structure",
        )
        return xml_prompt

    @staticmethod
    def extract_json_from_response(response_text: str) -> str:
        """
        Extract JSON from LLM response, handling markdown code fences.

        Based on the cleanup logic from the research CLI tools.

        Args:
            response_text: Raw LLM response text

        Returns:
            Cleaned JSON string

        Example:
            Input: "```json\\n{...}\\n```"
            Output: "{...}"
        """
        cleaned = response_text.strip()

        # Remove markdown code fences if present
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]  # Remove ```json
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]  # Remove trailing ```
            cleaned = cleaned.strip()
        elif cleaned.startswith("```"):
            # Handle generic code fence
            cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

        return cleaned

    def build_batch_prompt(
        self,
        prompts: list[str],
        schema: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Build a prompt for batch processing multiple prompts at once.

        Args:
            prompts: List of user prompts to analyze
            schema: Optional schema to apply to all prompts

        Returns:
            Meta-prompt for batch analysis
        """
        schema_str = self._format_schema(schema or self.CORE_SCHEMA)
        prompts_str = "\n".join([f'{i+1}. "{p}"' for i, p in enumerate(prompts)])

        meta_prompt = f"""
Analyze the following user prompts and extract information for each into structured JSON objects.
Each response should adhere to the schema below.

{self.LANGUAGE_DETECTION_INSTRUCTIONS}

JSON Schema (apply to each prompt):
{schema_str}

User Prompts:
{prompts_str}

Respond with a JSON array where each element corresponds to one prompt in order.
Do not include any other text or formatting.
"""
        return meta_prompt.strip()
