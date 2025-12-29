"""
TOON Parser - Encode/Decode TOON Format

This module provides functions to convert between Python data structures
and TOON (Token-Oriented Object Notation) format.

Functions:
    encode_to_toon(data, options=None) -> str
    decode_from_toon(toon_string, options=None) -> dict/list
"""

import re
from typing import Any, Dict, List, Union, Optional


class ToonEncodeOptions:
    """Options for encoding to TOON format."""
    def __init__(self, delimiter: str = ",", indent: int = 2, length_marker: bool = False):
        self.delimiter = delimiter
        self.indent = indent
        self.length_marker = length_marker


class ToonDecodeOptions:
    """Options for decoding from TOON format."""
    def __init__(self, indent: int = 2, strict: bool = True):
        self.indent = indent
        self.strict = strict


class ToonDecodeError(Exception):
    """Exception raised when TOON decoding fails."""
    def __init__(self, message: str, line: Optional[int] = None):
        self.message = message
        self.line = line
        super().__init__(self.message)


def encode_to_toon(data: Any, options: Optional[ToonEncodeOptions] = None) -> str:
    """
    Convert Python data structure to TOON format string.
    
    Args:
        data: Python dict, list, or primitive value
        options: Encoding options (delimiter, indent, length_marker)
    
    Returns:
        TOON-formatted string
    
    Example:
        >>> data = {"name": "Alice", "age": 30}
        >>> print(encode_to_toon(data))
        name: Alice
        age: 30
    """
    if options is None:
        options = ToonEncodeOptions()
    
    lines = []
    
    def format_value(value: Any, level: int = 0) -> None:
        """Recursively format value to TOON."""
        prefix = " " * (options.indent * level)
        
        if isinstance(value, dict):
            for key, val in value.items():
                if isinstance(val, dict):
                    # Nested object
                    lines.append(f"{prefix}{key}:")
                    format_value(val, level + 1)
                
                elif isinstance(val, list) and val and isinstance(val[0], dict):
                    # Tabular array (uniform objects)
                    if all(isinstance(item, dict) and set(item.keys()) == set(val[0].keys()) for item in val):
                        length_prefix = "#" if options.length_marker else ""
                        lines.append(f"{prefix}{key} [{length_prefix}{len(val)}{options.delimiter}]")
                        
                        # Header row (column names)
                        keys = list(val[0].keys())
                        lines.append(f"{prefix}{' ' * options.indent}{options.delimiter.join(keys)}")
                        
                        # Data rows
                        for item in val:
                            values = [_format_primitive(item[k]) for k in keys]
                            lines.append(f"{prefix}{' ' * options.indent}{options.delimiter.join(values)}")
                    else:
                        # List array (non-uniform)
                        length_prefix = "#" if options.length_marker else ""
                        lines.append(f"{prefix}{key} [{length_prefix}{len(val)}]")
                        for item in val:
                            lines.append(f"{prefix}{' ' * options.indent}- ")
                            format_value(item, level + 2)
                
                elif isinstance(val, list):
                    # Primitive array
                    length_prefix = "#" if options.length_marker else ""
                    formatted_values = [_format_primitive(v) for v in val]
                    lines.append(f"{prefix}{key} [{length_prefix}{len(val)}]: {', '.join(formatted_values)}")
                
                else:
                    # Simple key-value
                    lines.append(f"{prefix}{key}: {_format_primitive(val)}")
        
        elif isinstance(value, list):
            # Top-level array
            for item in value:
                format_value(item, level)
    
    format_value(data)
    return "\n".join(lines)


def decode_from_toon(toon_string: str, options: Optional[ToonDecodeOptions] = None) -> Any:
    """
    Convert TOON format string to Python data structure.
    
    Args:
        toon_string: TOON-formatted string
        options: Decoding options (indent, strict)
    
    Returns:
        Python dict, list, or primitive value
    
    Raises:
        ToonDecodeError: If the TOON string is malformed
    
    Example:
        >>> toon_str = "name: Alice\\nage: 30"
        >>> decode_from_toon(toon_str)
        {'name': 'Alice', 'age': 30}
    """
    if options is None:
        options = ToonDecodeOptions()
    
    lines = toon_string.strip().split("\n")
    result = {}
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip blank lines
        if not line.strip():
            i += 1
            continue
        
        # Get indentation level
        indent_level = len(line) - len(line.lstrip())
        stripped = line.strip()
        
        # Parse key-value pair
        if ":" in stripped and not stripped.startswith("-"):
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()
            
            # Check if next line is indented (nested object)
            if i + 1 < len(lines):
                next_indent = len(lines[i + 1]) - len(lines[i + 1].lstrip())
                if next_indent > indent_level:
                    # Nested object
                    result[key], i = _parse_nested_object(lines, i + 1, indent_level + options.indent, options)
                    continue
            
            # Check for array
            if "[" in key:
                array_key, array_info = key.split("[", 1)
                array_key = array_key.strip()
                array_info = array_info.rstrip("]")
                
                # Determine array type
                if "," in array_info:
                    # Tabular array
                    result[array_key], i = _parse_tabular_array(lines, i + 1, indent_level + options.indent, options)
                elif ":" in value:
                    # Primitive array
                    result[array_key] = _parse_primitive_array(value)
                else:
                    # List array
                    result[array_key], i = _parse_list_array(lines, i + 1, indent_level + options.indent, options)
                
                i += 1
                continue
            
            # Simple value
            result[key] = _parse_primitive(value)
        
        i += 1
    
    return result


def _format_primitive(value: Any) -> str:
    """Format a primitive value for TOON output."""
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        # Quote if necessary
        if _needs_quotes(value):
            return f'"{value}"'
        return value
    else:
        return str(value)


def _needs_quotes(value: str) -> bool:
    """Check if a string needs quotes in TOON format."""
    if not value:  # Empty string
        return True
    if value in ("true", "false", "null"):  # Reserved words
        return True
    if value[0].isdigit() or value[0] in "+-":  # Looks like number
        try:
            float(value)
            return True
        except ValueError:
            pass
    if value[0].isspace() or value[-1].isspace():  # Leading/trailing whitespace
        return True
    if any(c in value for c in ":[],-\n\r\t"):  # Special characters
        return True
    return False


def _parse_primitive(value: str) -> Any:
    """Parse a primitive value from TOON string."""
    value = value.strip()
    
    # Handle quoted strings
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    
    # Handle null
    if value == "null":
        return None
    
    # Handle booleans
    if value == "true":
        return True
    if value == "false":
        return False
    
    # Handle numbers
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        pass
    
    # Return as string
    return value


def _parse_primitive_array(value: str) -> List[Any]:
    """Parse a primitive array from inline format."""
    items = value.split(",")
    return [_parse_primitive(item.strip()) for item in items if item.strip()]


def _parse_nested_object(lines: List[str], start_idx: int, base_indent: int, 
                        options: ToonDecodeOptions) -> tuple:
    """Parse a nested object."""
    obj = {}
    i = start_idx
    
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        
        indent = len(line) - len(line.lstrip())
        if indent < base_indent:
            break
        
        stripped = line.strip()
        if ":" in stripped:
            key, _, value = stripped.partition(":")
            obj[key.strip()] = _parse_primitive(value.strip())
        
        i += 1
    
    return obj, i - 1


def _parse_tabular_array(lines: List[str], start_idx: int, base_indent: int,
                        options: ToonDecodeOptions) -> tuple:
    """Parse a tabular array."""
    if start_idx >= len(lines):
        return [], start_idx
    
    # Parse header row (column names)
    header_line = lines[start_idx].strip()
    columns = [col.strip() for col in header_line.split(",")]
    
    # Parse data rows
    items = []
    i = start_idx + 1
    
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        
        indent = len(line) - len(line.lstrip())
        if indent < base_indent:
            break
        
        values = [val.strip() for val in line.strip().split(",")]
        if len(values) == len(columns):
            item = {columns[j]: _parse_primitive(values[j]) for j in range(len(columns))}
            items.append(item)
        
        i += 1
    
    return items, i - 1


def _parse_list_array(lines: List[str], start_idx: int, base_indent: int,
                     options: ToonDecodeOptions) -> tuple:
    """Parse a list array."""
    items = []
    i = start_idx
    
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        
        indent = len(line) - len(line.lstrip())
        if indent < base_indent:
            break
        
        if line.strip().startswith("-"):
            # New item
            item, i = _parse_nested_object(lines, i + 1, indent + options.indent, options)
            items.append(item)
        
        i += 1
    
    return items, i - 1


# Main execution for testing
if __name__ == "__main__":
    print("=" * 80)
    print("TOON Parser - Self Test")
    print("=" * 80)
    
    # Test 1: Simple object
    print("\n1️⃣ Test: Simple Object")
    test1 = {
        "name": "Alice",
        "age": 30,
        "active": True
    }
    toon1 = encode_to_toon(test1)
    print("Python ->")
    print(test1)
    print("\nTOON ->")
    print(toon1)
    decoded1 = decode_from_toon(toon1)
    print("\nDecoded ->")
    print(decoded1)
    print("✅ PASS" if decoded1 == test1 else "❌ FAIL")
    
    # Test 2: Nested object
    print("\n\n2️⃣ Test: Nested Object")
    test2 = {
        "user": "Alice",
        "profile": {
            "age": 30,
            "city": "NYC"
        }
    }
    toon2 = encode_to_toon(test2)
    print("TOON ->")
    print(toon2)
    
    # Test 3: Tabular array
    print("\n\n3️⃣ Test: Tabular Array (Maximum Efficiency!)")
    test3 = {
        "intent": "extract",
        "contacts": [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob", "email": "bob@example.com"}
        ]
    }
    toon3 = encode_to_toon(test3)
    print("TOON ->")
    print(toon3)
    
    print("\n" + "=" * 80)
    print("✅ All tests completed!")
    print("=" * 80)
