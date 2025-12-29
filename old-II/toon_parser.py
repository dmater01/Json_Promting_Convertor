"""
TOON Parser Module for Structured Prompt Service

This module provides parsing and generation capabilities for TOON 
(Token-Oriented Object Notation) format, designed to reduce token usage 
by 30-60% compared to JSON.

Author: Development Team
Version: 1.0.0
"""

import re
import json
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum


class ArrayType(Enum):
    """Types of arrays in TOON format."""
    PRIMITIVE = "primitive"  # [N]: val1, val2, val3
    TABULAR = "tabular"      # [N,] header\n rows
    LIST = "list"            # [N] - item1\n - item2


@dataclass
class ParseOptions:
    """Options for TOON parsing."""
    strict: bool = False           # Strict validation mode
    indent: int = 2                # Expected indent size
    allow_tabs: bool = True        # Allow tabs in non-strict mode
    allow_blank_lines: bool = True # Allow blank lines


@dataclass
class EncodeOptions:
    """Options for TOON generation."""
    delimiter: str = ","           # Array value separator (,|\t||)
    indent: int = 2                # Spaces per indent level
    length_marker: str = "#"       # Array length marker (#N or N)
    prefer_tabular: bool = True    # Prefer tabular for uniform objects


class ToonParseError(Exception):
    """Raised when TOON parsing fails."""
    def __init__(self, message: str, line: Optional[int] = None):
        self.message = message
        self.line = line
        super().__init__(f"Line {line}: {message}" if line else message)


class ToonParser:
    """
    Parser for TOON (Token-Oriented Object Notation) format.
    
    Usage:
        parser = ToonParser()
        data = parser.parse(toon_string)
        toon_str = parser.generate(data)
    """
    
    def __init__(self, options: Optional[ParseOptions] = None):
        self.options = options or ParseOptions()
        
    def parse(self, toon_string: str) -> Dict[str, Any]:
        """
        Parse TOON string to Python dictionary.
        
        Args:
            toon_string: TOON formatted string
            
        Returns:
            Parsed dictionary
            
        Raises:
            ToonParseError: If parsing fails
        """
        lines = toon_string.strip().split('\n')
        result = {}
        
        try:
            self._parse_object(lines, result, 0, 0)
        except Exception as e:
            raise ToonParseError(f"Parse failed: {str(e)}")
        
        return result
    
    def _parse_object(
        self, 
        lines: List[str], 
        obj: Dict[str, Any],
        start_idx: int,
        base_indent: int
    ) -> int:
        """Parse object from lines starting at start_idx."""
        i = start_idx
        
        while i < len(lines):
            line = lines[i]
            
            # Skip empty lines
            if not line.strip():
                i += 1
                continue
            
            # Calculate indent
            indent = len(line) - len(line.lstrip())
            
            # If indent decreased, we're done with this object
            if indent < base_indent:
                break
            
            # Skip if this line is more indented (nested object, handled recursively)
            if indent > base_indent:
                i += 1
                continue
            
            # Parse key-value pair
            if ':' in line:
                key, value_part = line.split(':', 1)
                key = key.strip()
                value_part = value_part.strip()
                
                # Check if next line is more indented (nested object)
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    
                    if next_indent > indent:
                        # Nested object
                        nested_obj = {}
                        i = self._parse_object(lines, nested_obj, i + 1, next_indent)
                        obj[key] = nested_obj
                        continue
                
                # Parse value
                if value_part:
                    obj[key] = self._parse_value(value_part)
                else:
                    # Value on next line(s)
                    obj[key] = None
            
            i += 1
        
        return i
    
    def _parse_value(self, value_str: str) -> Any:
        """Parse a value string to appropriate Python type."""
        value_str = value_str.strip()
        
        # Check for array indicator
        if value_str.startswith('['):
            return self._parse_array_indicator(value_str)
        
        # Boolean
        if value_str == 'true':
            return True
        if value_str == 'false':
            return False
        
        # Null
        if value_str == 'null':
            return None
        
        # Number
        try:
            if '.' in value_str:
                return float(value_str)
            else:
                return int(value_str)
        except ValueError:
            pass
        
        # String (remove quotes if present)
        if value_str.startswith('"') and value_str.endswith('"'):
            return value_str[1:-1]
        
        return value_str
    
    def _parse_array_indicator(self, indicator: str) -> Dict[str, Any]:
        """Parse array length indicator like [5], [3,], [2|]."""
        match = re.match(r'\[(#?)(\d+)([,|\t|])?\]', indicator)
        if match:
            has_marker = bool(match.group(1))
            length = int(match.group(2))
            delimiter = match.group(3) or None
            
            return {
                'length': length,
                'delimiter': delimiter,
                'type': self._infer_array_type(delimiter)
            }
        
        return {'length': 0, 'delimiter': None, 'type': ArrayType.LIST}
    
    def _infer_array_type(self, delimiter: Optional[str]) -> ArrayType:
        """Infer array type from delimiter."""
        if delimiter in [',', '|', '\t']:
            return ArrayType.TABULAR
        return ArrayType.LIST
    
    def generate(self, data: Dict[str, Any], options: Optional[EncodeOptions] = None) -> str:
        """
        Generate TOON string from Python dictionary.
        
        Args:
            data: Python dictionary to convert
            options: Encoding options
            
        Returns:
            TOON formatted string
        """
        opts = options or EncodeOptions()
        lines = []
        
        self._generate_object(data, lines, 0, opts)
        
        return '\n'.join(lines)
    
    def _generate_object(
        self,
        obj: Dict[str, Any],
        lines: List[str],
        indent_level: int,
        options: EncodeOptions
    ):
        """Generate TOON lines for an object."""
        indent = ' ' * (indent_level * options.indent)
        
        for key, value in obj.items():
            if isinstance(value, dict):
                # Nested object
                lines.append(f"{indent}{key}:")
                self._generate_object(value, lines, indent_level + 1, options)
            elif isinstance(value, list):
                # Array
                lines.append(f"{indent}{key} {self._generate_array(value, options)}:")
                if options.prefer_tabular and self._is_uniform_objects(value):
                    self._generate_tabular_array(value, lines, indent_level + 1, options)
                else:
                    self._generate_list_array(value, lines, indent_level + 1, options)
            else:
                # Simple value
                value_str = self._format_value(value)
                lines.append(f"{indent}{key}: {value_str}")
    
    def _generate_array(self, arr: List[Any], options: EncodeOptions) -> str:
        """Generate array length indicator."""
        length = len(arr)
        marker = options.length_marker if options.length_marker else ""
        
        # Determine array type
        if self._is_uniform_objects(arr):
            return f"[{marker}{length}{options.delimiter}]"
        elif all(not isinstance(item, (dict, list)) for item in arr):
            return f"[{marker}{length}]"
        else:
            return f"[{marker}{length}]"
    
    def _is_uniform_objects(self, arr: List[Any]) -> bool:
        """Check if array contains uniform objects (same keys, all primitives)."""
        if not arr or not all(isinstance(item, dict) for item in arr):
            return False
        
        # Get keys from first object
        first_keys = set(arr[0].keys())
        
        # Check all objects have same keys and all values are primitives
        for obj in arr:
            if set(obj.keys()) != first_keys:
                return False
            if any(isinstance(v, (dict, list)) for v in obj.values()):
                return False
        
        return True
    
    def _generate_tabular_array(
        self,
        arr: List[Dict[str, Any]],
        lines: List[str],
        indent_level: int,
        options: EncodeOptions
    ):
        """Generate tabular array (CSV-like)."""
        if not arr:
            return
        
        indent = ' ' * (indent_level * options.indent)
        
        # Header (keys)
        keys = list(arr[0].keys())
        header = options.delimiter.join(keys)
        lines.append(f"{indent}{header}")
        
        # Rows (values)
        for obj in arr:
            values = [self._format_value(obj[key]) for key in keys]
            row = options.delimiter.join(values)
            lines.append(f"{indent}{row}")
    
    def _generate_list_array(
        self,
        arr: List[Any],
        lines: List[str],
        indent_level: int,
        options: EncodeOptions
    ):
        """Generate list array with - markers."""
        indent = ' ' * (indent_level * options.indent)
        
        for item in arr:
            if isinstance(item, dict):
                lines.append(f"{indent}-")
                self._generate_object(item, lines, indent_level + 1, options)
            else:
                value_str = self._format_value(item)
                lines.append(f"{indent}- {value_str}")
    
    def _format_value(self, value: Any) -> str:
        """Format a value for TOON output."""
        # Null
        if value is None:
            return "null"
        
        # Boolean
        if isinstance(value, bool):
            return "true" if value else "false"
        
        # Number
        if isinstance(value, (int, float)):
            return str(value)
        
        # String - quote only if necessary
        if isinstance(value, str):
            return self._quote_string(value)
        
        return str(value)
    
    def _quote_string(self, s: str) -> str:
        """
        Quote string only if necessary per TOON rules.
        
        Quote if:
        - Empty string
        - Reserved keyword (true, false, null)
        - Looks like a number
        - Has leading/trailing whitespace
        - Contains structural characters (:, [, ], -)
        - Contains control characters
        """
        # Empty string
        if not s:
            return '""'
        
        # Reserved keywords
        if s in ['true', 'false', 'null']:
            return f'"{s}"'
        
        # Looks like a number
        try:
            float(s)
            return f'"{s}"'
        except ValueError:
            pass
        
        # Leading/trailing whitespace
        if s != s.strip():
            return f'"{s}"'
        
        # Structural characters
        if any(c in s for c in ':[]- \t\n'):
            return f'"{s}"'
        
        # No quoting needed
        return s


class ToonTokenCalculator:
    """Calculate token savings for TOON vs JSON."""
    
    @staticmethod
    def estimate_savings(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate token savings for TOON vs JSON.
        
        Args:
            data: Python dictionary
            
        Returns:
            Dictionary with token counts and savings
        """
        # Generate both formats
        json_str = json.dumps(data, indent=2)
        
        parser = ToonParser()
        toon_str = parser.generate(data)
        
        # Estimate tokens (rough approximation)
        json_tokens = ToonTokenCalculator._count_tokens(json_str)
        toon_tokens = ToonTokenCalculator._count_tokens(toon_str)
        
        savings = json_tokens - toon_tokens
        savings_percent = (savings / json_tokens) * 100 if json_tokens > 0 else 0
        
        return {
            "json_tokens": json_tokens,
            "toon_tokens": toon_tokens,
            "savings": savings,
            "savings_percent": round(savings_percent, 2),
            "json_chars": len(json_str),
            "toon_chars": len(toon_str)
        }
    
    @staticmethod
    def _count_tokens(text: str) -> int:
        """
        Rough token estimation (actual tokenization depends on model).
        
        Approximation: ~4 characters per token for English text
        """
        # Simple character-based estimation
        # Real implementation would use tiktoken library
        return len(text) // 4


# Convenience functions
def parse_toon(toon_string: str, strict: bool = False) -> Dict[str, Any]:
    """Parse TOON string to dictionary."""
    parser = ToonParser(ParseOptions(strict=strict))
    return parser.parse(toon_string)


def generate_toon(data: Dict[str, Any], prefer_tabular: bool = True) -> str:
    """Generate TOON string from dictionary."""
    parser = ToonParser()
    return parser.generate(data, EncodeOptions(prefer_tabular=prefer_tabular))


def estimate_token_savings(data: Dict[str, Any]) -> Dict[str, Any]:
    """Estimate token savings for TOON vs JSON."""
    return ToonTokenCalculator.estimate_savings(data)


if __name__ == "__main__":
    # Example usage
    print("TOON Parser Module - Example Usage\n")
    
    # Example data
    data = {
        "request_id": "abc123",
        "data": {
            "intent": "extract",
            "subject": "contacts",
            "entities": {
                "contacts": [
                    {"name": "John Doe", "email": "john@example.com", "phone": "555-1234"},
                    {"name": "Jane Smith", "email": "jane@example.com", "phone": "555-5678"}
                ]
            },
            "output_format": "tabular",
            "original_language": "en",
            "confidence_score": 0.92
        },
        "llm_provider": "gemini",
        "tokens_used": 67,
        "cached": False
    }
    
    # Generate TOON
    print("=== TOON Format ===")
    parser = ToonParser()
    toon_str = parser.generate(data, EncodeOptions(prefer_tabular=True))
    print(toon_str)
    
    # JSON for comparison
    print("\n=== JSON Format ===")
    print(json.dumps(data, indent=2))
    
    # Token savings
    print("\n=== Token Savings ===")
    savings = estimate_token_savings(data)
    print(f"JSON tokens: {savings['json_tokens']}")
    print(f"TOON tokens: {savings['toon_tokens']}")
    print(f"Savings: {savings['savings']} tokens ({savings['savings_percent']}%)")
    print(f"JSON chars: {savings['json_chars']}")
    print(f"TOON chars: {savings['toon_chars']}")
