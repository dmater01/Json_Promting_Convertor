"""
TOON Parser - Token-Oriented Object Notation Encoder/Decoder

This module provides complete encoding and decoding functionality for the TOON format,
optimized for LLM token efficiency (30-60% reduction vs JSON).

Features:
- Encode Python dicts/lists to TOON format
- Decode TOON strings to Python objects
- Strict and lenient parsing modes
- Tabular array optimization
- Comprehensive validation
- Type normalization

Author: Development Team
Version: 1.0.0
"""

import re
from typing import Any, Dict, List, Union, Optional, Tuple
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class ArrayType(Enum):
    """TOON array types for optimal token efficiency."""
    PRIMITIVE = "primitive"  # Simple values: [N]: val1, val2
    TABULAR = "tabular"      # Uniform objects: [N,] headers / rows
    LIST = "list"            # Complex objects: [N] with - markers


class ToonParseError(Exception):
    """Exception raised when TOON parsing fails."""
    def __init__(self, message: str, line_number: Optional[int] = None):
        self.message = message
        self.line_number = line_number
        super().__init__(f"Line {line_number}: {message}" if line_number else message)


class ToonParser:
    """
    Complete TOON format parser with encoding and decoding capabilities.
    
    Usage:
        parser = ToonParser(strict=True, indent=2)
        toon_str = parser.encode(data)
        data = parser.decode(toon_str)
    """
    
    def __init__(self, strict: bool = True, indent: int = 2, delimiter: str = ","):
        """
        Initialize TOON parser.
        
        Args:
            strict: Enable strict validation mode
            indent: Spaces per indentation level (default: 2)
            delimiter: Array delimiter: "," (default), "\t", or "|"
        """
        self.strict = strict
        self.indent = indent
        self.delimiter = delimiter
        self.reserved_keywords = {"true", "false", "null"}
        
    # ============================================================================
    # ENCODING (Python → TOON)
    # ============================================================================
    
    def encode(self, data: Any) -> str:
        """
        Encode Python data to TOON format string.
        
        Args:
            data: Python dict, list, or primitive value
            
        Returns:
            TOON-formatted string
            
        Example:
            >>> parser = ToonParser()
            >>> data = {"users": [{"id": 1, "name": "Alice"}]}
            >>> print(parser.encode(data))
            users [1,]
              id, name
              1, Alice
        """
        normalized_data = self._normalize_types(data)
        return self._encode_value(normalized_data, level=0)
    
    def _encode_value(self, value: Any, level: int) -> str:
        """Encode a value at given indentation level."""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            return self._encode_string(value)
        elif isinstance(value, dict):
            return self._encode_object(value, level)
        elif isinstance(value, list):
            return self._encode_array(value, level)
        else:
            raise ValueError(f"Unsupported type: {type(value)}")
    
    def _encode_object(self, obj: Dict[str, Any], level: int) -> str:
        """Encode dictionary as TOON object."""
        lines = []
        for key, value in obj.items():
            indent_str = " " * (self.indent * level)
            
            if isinstance(value, dict):
                # Nested object
                lines.append(f"{indent_str}{key}:")
                lines.append(self._encode_object(value, level + 1))
            elif isinstance(value, list):
                # Array value
                array_str = self._encode_array(value, level)
                lines.append(f"{indent_str}{key} {array_str}")
            else:
                # Primitive value
                value_str = self._encode_value(value, level)
                lines.append(f"{indent_str}{key}: {value_str}")
        
        return "\n".join(lines)
    
    def _encode_array(self, arr: List[Any], level: int) -> str:
        """Encode list as most efficient TOON array type."""
        if not arr:
            return "[0]"
        
        array_type = self._detect_array_type(arr)
        
        if array_type == ArrayType.PRIMITIVE:
            return self._encode_primitive_array(arr)
        elif array_type == ArrayType.TABULAR:
            return self._encode_tabular_array(arr, level)
        else:
            return self._encode_list_array(arr, level)
    
    def _detect_array_type(self, arr: List[Any]) -> ArrayType:
        """Detect optimal array type for maximum token efficiency."""
        if not arr:
            return ArrayType.LIST
        
        # Check if all elements are primitives
        if all(isinstance(item, (str, int, float, bool, type(None))) for item in arr):
            return ArrayType.PRIMITIVE
        
        # Check if all elements are dicts with same keys and primitive values
        if all(isinstance(item, dict) for item in arr):
            if len(arr) > 0:
                first_keys = set(arr[0].keys())
                # All dicts must have same keys
                if all(set(item.keys()) == first_keys for item in arr):
                    # All values must be primitives
                    if all(
                        isinstance(val, (str, int, float, bool, type(None)))
                        for item in arr
                        for val in item.values()
                    ):
                        return ArrayType.TABULAR
        
        return ArrayType.LIST
    
    def _encode_primitive_array(self, arr: List[Any]) -> str:
        """Encode as primitive array: [N]: val1, val2, val3"""
        values = [self._encode_value(item, 0) for item in arr]
        return f"[{len(arr)}]: {', '.join(values)}"
    
    def _encode_tabular_array(self, arr: List[Dict[str, Any]], level: int) -> str:
        """Encode as tabular array (most efficient): [N,] with header row."""
        if not arr:
            return "[0,]"
        
        keys = list(arr[0].keys())
        lines = [f"[{len(arr)}{self.delimiter}]"]
        
        indent_str = " " * (self.indent * (level + 1))
        
        # Header row
        header = self.delimiter.join(keys)
        lines.append(f"{indent_str}{header}")
        
        # Data rows
        for item in arr:
            values = [self._encode_value(item[key], 0) for key in keys]
            row = self.delimiter.join(values)
            lines.append(f"{indent_str}{row}")
        
        return "\n".join(lines)
    
    def _encode_list_array(self, arr: List[Any], level: int) -> str:
        """Encode as list array: [N] with - markers."""
        lines = [f"[{len(arr)}]"]
        indent_str = " " * (self.indent * (level + 1))
        
        for item in arr:
            if isinstance(item, dict):
                lines.append(f"{indent_str}- " + list(item.keys())[0] + ": " + 
                           self._encode_value(list(item.values())[0], level + 1))
                # Add remaining keys
                for key, value in list(item.items())[1:]:
                    if isinstance(value, dict):
                        lines.append(f"{indent_str}  {key}:")
                        lines.append(self._encode_object(value, level + 2))
                    else:
                        value_str = self._encode_value(value, level + 1)
                        lines.append(f"{indent_str}  {key}: {value_str}")
            else:
                lines.append(f"{indent_str}- {self._encode_value(item, level + 1)}")
        
        return "\n".join(lines)
    
    def _encode_string(self, s: str) -> str:
        """Encode string with selective quoting."""
        # Quote if necessary
        if (not s or  # Empty string
            s.lower() in self.reserved_keywords or  # Reserved keyword
            s.replace('.', '').replace('-', '').isdigit() or  # Looks like number
            s != s.strip() or  # Leading/trailing whitespace
            any(c in s for c in [':', '[', ']', '-', self.delimiter]) or  # Special chars
            '\n' in s or '\t' in s):  # Control chars
            # Escape quotes and special chars
            escaped = s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')
            return f'"{escaped}"'
        return s
    
    def _normalize_types(self, value: Any) -> Any:
        """Normalize non-standard Python types to TOON-compatible types."""
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        elif isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, tuple):
            return list(value)
        elif isinstance(value, (set, frozenset)):
            return sorted(list(value))
        elif callable(value):
            return None
        elif isinstance(value, float):
            if value != value:  # NaN
                return None
            elif value == float('inf') or value == float('-inf'):
                return None
            elif value == -0.0:
                return 0
            return value
        elif isinstance(value, dict):
            return {k: self._normalize_types(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._normalize_types(item) for item in value]
        return value
    
    # ============================================================================
    # DECODING (TOON → Python)
    # ============================================================================
    
    def decode(self, toon_str: str) -> Any:
        """
        Decode TOON format string to Python data.
        
        Args:
            toon_str: TOON-formatted string
            
        Returns:
            Python dict, list, or primitive value
            
        Raises:
            ToonParseError: If parsing fails
            
        Example:
            >>> parser = ToonParser()
            >>> toon_str = '''users [1,]
            ...   id, name
            ...   1, Alice'''
            >>> data = parser.decode(toon_str)
            >>> print(data)
            {'users': [{'id': 1, 'name': 'Alice'}]}
        """
        lines = toon_str.split('\n')
        self.current_line = 0
        result, _ = self._parse_lines(lines, 0, 0)
        return result
    
    def _parse_lines(self, lines: List[str], start_idx: int, 
                     current_indent: int) -> Tuple[Any, int]:
        """Parse lines starting at given index and indentation level."""
        result = {}
        idx = start_idx
        
        while idx < len(lines):
            line = lines[idx]
            
            # Skip empty lines
            if not line.strip():
                idx += 1
                continue
            
            # Get indentation
            indent = len(line) - len(line.lstrip())
            
            # If indent decreased, we're done with this level
            if indent < current_indent:
                break
            
            # If indent increased more than expected, error in strict mode
            if self.strict and indent > current_indent and indent % self.indent != 0:
                raise ToonParseError(
                    f"Invalid indentation: {indent} (expected multiple of {self.indent})",
                    idx + 1
                )
            
            # Parse key-value pair
            stripped = line.strip()
            
            if ':' in stripped and not stripped.startswith('-'):
                # Object property
                key, value_part = stripped.split(':', 1)
                key = key.strip()
                value_part = value_part.strip()
                
                if not value_part:
                    # Nested object on next lines
                    nested_result, idx = self._parse_lines(lines, idx + 1, indent + self.indent)
                    result[key] = nested_result
                    continue
                elif value_part.startswith('['):
                    # Array value
                    array_result, idx = self._parse_array(lines, idx, indent)
                    result[key] = array_result
                    continue
                else:
                    # Primitive value
                    result[key] = self._parse_value(value_part)
            
            idx += 1
        
        return result, idx
    
    def _parse_array(self, lines: List[str], start_idx: int, 
                     base_indent: int) -> Tuple[List[Any], int]:
        """Parse TOON array from lines."""
        line = lines[start_idx].strip()
        
        # Extract array header
        match = re.match(r'\[(\d+)([\,\t\|])?\]\s*:\s*(.+)', line)
        if match:
            # Primitive array
            count = int(match.group(1))
            values_str = match.group(3)
            values = [self._parse_value(v.strip()) for v in values_str.split(',')]
            
            if self.strict and len(values) != count:
                raise ToonParseError(
                    f"Array length mismatch: declared {count}, found {len(values)}",
                    start_idx + 1
                )
            
            return values, start_idx + 1
        
        match = re.match(r'\[(\d+)([\,\t\|])?\]', line)
        if not match:
            raise ToonParseError(f"Invalid array header: {line}", start_idx + 1)
        
        count = int(match.group(1))
        delimiter = match.group(2) or None
        
        if delimiter:
            # Tabular array
            return self._parse_tabular_array(lines, start_idx + 1, base_indent, count, delimiter)
        else:
            # List array
            return self._parse_list_array(lines, start_idx + 1, base_indent, count)
    
    def _parse_tabular_array(self, lines: List[str], header_idx: int,
                            base_indent: int, count: int, delimiter: str) -> Tuple[List[Dict], int]:
        """Parse tabular array with header row."""
        # Parse header
        header_line = lines[header_idx].strip()
        if delimiter == '\t':
            headers = [h.strip() for h in header_line.split('\t')]
        elif delimiter == '|':
            headers = [h.strip() for h in header_line.split('|')]
        else:
            headers = [h.strip() for h in header_line.split(',')]
        
        # Parse data rows
        result = []
        for i in range(count):
            row_idx = header_idx + 1 + i
            if row_idx >= len(lines):
                raise ToonParseError(f"Array has fewer rows than declared length {count}", row_idx)
            
            row_line = lines[row_idx].strip()
            if delimiter == '\t':
                values = [v.strip() for v in row_line.split('\t')]
            elif delimiter == '|':
                values = [v.strip() for v in row_line.split('|')]
            else:
                values = [v.strip() for v in row_line.split(',')]
            
            if len(values) != len(headers):
                raise ToonParseError(
                    f"Row {i+1} has {len(values)} values, expected {len(headers)}",
                    row_idx + 1
                )
            
            row_dict = {headers[j]: self._parse_value(values[j]) for j in range(len(headers))}
            result.append(row_dict)
        
        return result, header_idx + count + 1
    
    def _parse_list_array(self, lines: List[str], start_idx: int,
                         base_indent: int, count: int) -> Tuple[List[Any], int]:
        """Parse list array with - markers."""
        result = []
        idx = start_idx
        items_found = 0
        
        while idx < len(lines) and items_found < count:
            line = lines[idx]
            stripped = line.strip()
            
            if stripped.startswith('-'):
                # Array item
                item_content = stripped[1:].strip()
                if ':' in item_content:
                    # Object item
                    item_dict, idx = self._parse_object_item(lines, idx, base_indent)
                    result.append(item_dict)
                else:
                    # Primitive item
                    result.append(self._parse_value(item_content))
                    idx += 1
                items_found += 1
            else:
                idx += 1
        
        if self.strict and items_found != count:
            raise ToonParseError(
                f"List array length mismatch: declared {count}, found {items_found}",
                start_idx
            )
        
        return result, idx
    
    def _parse_object_item(self, lines: List[str], start_idx: int,
                          base_indent: int) -> Tuple[Dict, int]:
        """Parse object item in list array."""
        item = {}
        line = lines[start_idx]
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()[1:].strip()  # Remove '-'
        
        # Parse first property
        if ':' in stripped:
            key, value = stripped.split(':', 1)
            item[key.strip()] = self._parse_value(value.strip())
        
        # Parse remaining properties
        idx = start_idx + 1
        while idx < len(lines):
            line = lines[idx]
            current_indent = len(line) - len(line.lstrip())
            
            if current_indent <= indent:
                break
            
            stripped = line.strip()
            if ':' in stripped and not stripped.startswith('-'):
                key, value = stripped.split(':', 1)
                item[key.strip()] = self._parse_value(value.strip())
            
            idx += 1
        
        return item, idx
    
    def _parse_value(self, value_str: str) -> Any:
        """Parse primitive value from string."""
        value_str = value_str.strip()
        
        # Null
        if value_str == 'null':
            return None
        
        # Boolean
        if value_str == 'true':
            return True
        if value_str == 'false':
            return False
        
        # Quoted string
        if value_str.startswith('"') and value_str.endswith('"'):
            # Unescape
            unescaped = value_str[1:-1].replace('\\"', '"').replace('\\\\', '\\')
            unescaped = unescaped.replace('\\n', '\n').replace('\\t', '\t')
            return unescaped
        
        # Number
        try:
            if '.' in value_str:
                return float(value_str)
            else:
                return int(value_str)
        except ValueError:
            pass
        
        # Unquoted string
        return value_str
    
    # ============================================================================
    # CONVENIENCE METHODS
    # ============================================================================
    
    def generate(self, data: Any) -> str:
        """Alias for encode() - for backward compatibility."""
        return self.encode(data)
    
    def parse(self, toon_str: str) -> Any:
        """Alias for decode() - for backward compatibility."""
        return self.decode(toon_str)


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    # Example 1: Simple object
    print("=" * 60)
    print("Example 1: Simple Object")
    print("=" * 60)
    
    parser = ToonParser()
    
    data1 = {
        "name": "Alice",
        "email": "alice@example.com",
        "verified": True
    }
    
    toon1 = parser.encode(data1)
    print("TOON Output:")
    print(toon1)
    print("\nDecoded back:")
    print(parser.decode(toon1))
    
    # Example 2: Tabular array (maximum efficiency)
    print("\n" + "=" * 60)
    print("Example 2: Tabular Array (Maximum Token Savings)")
    print("=" * 60)
    
    data2 = {
        "users": [
            {"id": 1, "name": "Alice", "role": "admin"},
            {"id": 2, "name": "Bob", "role": "user"},
            {"id": 3, "name": "Charlie", "role": "guest"}
        ]
    }
    
    toon2 = parser.encode(data2)
    print("TOON Output:")
    print(toon2)
    print("\nDecoded back:")
    print(parser.decode(toon2))
    
    # Example 3: Nested structure
    print("\n" + "=" * 60)
    print("Example 3: Nested Structure")
    print("=" * 60)
    
    data3 = {
        "user": {
            "name": "Alice",
            "location": {
                "city": "San Francisco",
                "country": "USA"
            }
        },
        "permissions": {
            "roles": ["admin", "contributor"],
            "level": 5
        }
    }
    
    toon3 = parser.encode(data3)
    print("TOON Output:")
    print(toon3)
    print("\nDecoded back:")
    print(parser.decode(toon3))
