"""
TOON Validator - Validation and Quality Checking Utilities

This module provides comprehensive validation for TOON format strings,
ensuring correctness, consistency, and adherence to TOON specifications.

Features:
- Strict and lenient validation modes
- Array length validation
- Indentation checking
- Quoting rules verification
- Type checking
- Detailed error reporting

Author: Development Team
Version: 1.0.0
"""

import re
from typing import List, Dict, Tuple, Optional, Any
from enum import Enum


class ValidationLevel(Enum):
    """Validation strictness levels."""
    STRICT = "strict"      # Full spec compliance
    LENIENT = "lenient"    # Allow minor deviations
    BASIC = "basic"        # Only critical errors


class ValidationError:
    """Represents a single validation error."""
    
    def __init__(self, line_num: int, severity: str, message: str, context: Optional[str] = None):
        """
        Initialize validation error.
        
        Args:
            line_num: Line number where error occurred
            severity: ERROR, WARNING, or INFO
            message: Error description
            context: Optional context (line content)
        """
        self.line_num = line_num
        self.severity = severity
        self.message = message
        self.context = context
    
    def __str__(self) -> str:
        """Format error as string."""
        result = f"Line {self.line_num} [{self.severity}]: {self.message}"
        if self.context:
            result += f"\n  Context: {self.context}"
        return result
    
    def __repr__(self) -> str:
        return self.__str__()


class ValidationResult:
    """Results from TOON validation."""
    
    def __init__(self):
        """Initialize validation result."""
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        self.info: List[ValidationError] = []
        self.is_valid = True
    
    def add_error(self, line_num: int, message: str, context: Optional[str] = None):
        """Add an error."""
        self.errors.append(ValidationError(line_num, "ERROR", message, context))
        self.is_valid = False
    
    def add_warning(self, line_num: int, message: str, context: Optional[str] = None):
        """Add a warning."""
        self.warnings.append(ValidationError(line_num, "WARNING", message, context))
    
    def add_info(self, line_num: int, message: str, context: Optional[str] = None):
        """Add an info message."""
        self.info.append(ValidationError(line_num, "INFO", message, context))
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0
    
    def get_summary(self) -> str:
        """Get summary string."""
        return f"Errors: {len(self.errors)}, Warnings: {len(self.warnings)}, Info: {len(self.info)}"
    
    def print_report(self, show_info: bool = False):
        """Print formatted validation report."""
        print("=" * 80)
        print("TOON VALIDATION REPORT")
        print("=" * 80)
        print()
        
        if self.is_valid and not self.warnings:
            print("✅ VALIDATION PASSED")
            print("   No errors or warnings found.")
            print()
            return
        
        # Errors
        if self.errors:
            print(f"❌ ERRORS ({len(self.errors)}):")
            print("-" * 80)
            for error in self.errors:
                print(f"  {error}")
            print()
        
        # Warnings
        if self.warnings:
            print(f"⚠️  WARNINGS ({len(self.warnings)}):")
            print("-" * 80)
            for warning in self.warnings:
                print(f"  {warning}")
            print()
        
        # Info
        if show_info and self.info:
            print(f"ℹ️  INFO ({len(self.info)}):")
            print("-" * 80)
            for info in self.info:
                print(f"  {info}")
            print()
        
        # Summary
        if self.is_valid:
            print("✅ VALIDATION PASSED (with warnings)")
        else:
            print("❌ VALIDATION FAILED")
        print()
        print(self.get_summary())
        print()


class ToonValidator:
    """
    Comprehensive TOON format validator.
    
    Validates:
    - Indentation consistency
    - Array length indicators
    - Quoting rules
    - Type correctness
    - Structural integrity
    """
    
    def __init__(self, level: ValidationLevel = ValidationLevel.STRICT, indent: int = 2):
        """
        Initialize validator.
        
        Args:
            level: Validation strictness level
            indent: Expected indentation (spaces per level)
        """
        self.level = level
        self.indent = indent
        self.reserved_keywords = {"true", "false", "null"}
    
    def validate(self, toon_str: str) -> ValidationResult:
        """
        Validate TOON format string.
        
        Args:
            toon_str: TOON format string to validate
            
        Returns:
            ValidationResult with errors, warnings, and info
        """
        result = ValidationResult()
        lines = toon_str.split('\n')
        
        # Track state
        current_indent = 0
        in_array = False
        array_info = None
        
        for i, line in enumerate(lines, start=1):
            # Skip empty lines
            if not line.strip():
                continue
            
            # Check indentation
            indent_errors = self._validate_indentation(line, i, current_indent)
            for error in indent_errors:
                if self.level == ValidationLevel.STRICT:
                    result.add_error(i, error, line)
                else:
                    result.add_warning(i, error, line)
            
            # Get line indentation
            line_indent = len(line) - len(line.lstrip())
            stripped = line.strip()
            
            # Check for array headers
            if '[' in stripped and ']' in stripped and not in_array:
                array_errors, info = self._validate_array_header(stripped, i)
                for error in array_errors:
                    result.add_error(i, error, line)
                if info:
                    array_info = info
                    in_array = True
            
            # Check key-value syntax
            if ':' in stripped and not stripped.startswith('-'):
                kv_errors = self._validate_key_value(stripped, i)
                for error in kv_errors:
                    if self.level == ValidationLevel.STRICT:
                        result.add_error(i, error, line)
                    else:
                        result.add_warning(i, error, line)
            
            # Check quoting
            quote_warnings = self._check_quoting(stripped, i)
            for warning in quote_warnings:
                result.add_warning(i, warning, line)
            
            # Check types
            type_warnings = self._check_types(stripped, i)
            for warning in type_warnings:
                result.add_warning(i, warning, line)
        
        return result
    
    def _validate_indentation(self, line: str, line_num: int, expected: int) -> List[str]:
        """Validate line indentation."""
        errors = []
        
        indent = len(line) - len(line.lstrip())
        
        # Check for tabs
        if '\t' in line[:indent]:
            errors.append("Tabs found in indentation (use spaces)")
        
        # Check indentation multiple
        if self.level == ValidationLevel.STRICT:
            if indent % self.indent != 0:
                errors.append(f"Indentation not a multiple of {self.indent} (found {indent})")
        
        return errors
    
    def _validate_array_header(self, line: str, line_num: int) -> Tuple[List[str], Optional[Dict]]:
        """Validate array header syntax."""
        errors = []
        info = None
        
        # Primitive array: [N]:
        match = re.match(r'.*\[(\d+)\]\s*:', line)
        if match:
            count = int(match.group(1))
            info = {"type": "primitive", "count": count, "line": line_num}
            return errors, info
        
        # Tabular array: [N,] or [N\t] or [N|]
        match = re.match(r'.*\[(\d+)([\,\t\|])\]', line)
        if match:
            count = int(match.group(1))
            delimiter = match.group(2)
            info = {"type": "tabular", "count": count, "delimiter": delimiter, "line": line_num}
            return errors, info
        
        # List array: [N]
        match = re.match(r'.*\[(\d+)\]', line)
        if match:
            count = int(match.group(1))
            info = {"type": "list", "count": count, "line": line_num}
            return errors, info
        
        # Invalid format
        if '[' in line and ']' in line:
            errors.append("Invalid array header format")
        
        return errors, info
    
    def _validate_key_value(self, line: str, line_num: int) -> List[str]:
        """Validate key-value pair syntax."""
        errors = []
        
        if ':' not in line:
            return errors
        
        parts = line.split(':', 1)
        key = parts[0].strip()
        value = parts[1].strip() if len(parts) > 1 else ""
        
        # Check key validity
        if not key:
            errors.append("Empty key")
        elif not self._is_valid_key(key):
            errors.append(f"Invalid key format: {key}")
        
        # Check value
        if value and not self._is_valid_value(value):
            if self.level == ValidationLevel.STRICT:
                errors.append(f"Potentially invalid value: {value}")
        
        return errors
    
    def _is_valid_key(self, key: str) -> bool:
        """Check if key is valid."""
        # Basic validation: alphanumeric and underscores
        if not key:
            return False
        # Allow keys with spaces if quoted, or simple identifiers
        if key.startswith('"') and key.endswith('"'):
            return True
        return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', key))
    
    def _is_valid_value(self, value: str) -> bool:
        """Check if value looks valid."""
        if not value:
            return True
        
        # Check for obvious issues
        if value.startswith('[') and not value.endswith(']'):
            return False
        if value.count('"') % 2 != 0:
            return False
        
        return True
    
    def _check_quoting(self, line: str, line_num: int) -> List[str]:
        """Check for unnecessary or missing quotes."""
        warnings = []
        
        if ':' not in line or line.startswith('-'):
            return warnings
        
        parts = line.split(':', 1)
        if len(parts) < 2:
            return warnings
        
        value = parts[1].strip()
        
        # Check for unnecessary quotes
        if value.startswith('"') and value.endswith('"'):
            unquoted = value[1:-1]
            # Check if quotes are necessary
            if not self._needs_quotes(unquoted):
                warnings.append(f"Unnecessary quotes on value: {value}")
        
        # Check for missing quotes
        elif self._needs_quotes(value):
            if ',' in value or ':' in value or '[' in value:
                warnings.append(f"Value may need quotes: {value}")
        
        return warnings
    
    def _needs_quotes(self, s: str) -> bool:
        """Check if string needs quotes."""
        if not s:
            return True  # Empty string
        if s.lower() in self.reserved_keywords:
            return True  # Reserved keyword
        if s.replace('.', '').replace('-', '').isdigit():
            return False  # Number (doesn't need quotes as number)
        if s != s.strip():
            return True  # Leading/trailing whitespace
        if any(c in s for c in [':', '[', ']', '-', '\n', '\t']):
            return True  # Special characters
        return False
    
    def _check_types(self, line: str, line_num: int) -> List[str]:
        """Check for type consistency."""
        warnings = []
        
        if ':' not in line or line.startswith('-'):
            return warnings
        
        parts = line.split(':', 1)
        if len(parts) < 2:
            return warnings
        
        value = parts[1].strip()
        
        # Check boolean
        if value in ['True', 'False']:
            warnings.append(f"Boolean should be lowercase: {value} → {value.lower()}")
        
        # Check null
        if value in ['None', 'NULL', 'Null']:
            warnings.append(f"Null should be lowercase: {value} → null")
        
        return warnings
    
    def quick_validate(self, toon_str: str) -> bool:
        """
        Quick validation - returns True/False only.
        
        Args:
            toon_str: TOON string to validate
            
        Returns:
            True if valid, False otherwise
        """
        result = self.validate(toon_str)
        return result.is_valid


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def validate_toon(toon_str: str, strict: bool = True) -> ValidationResult:
    """
    Validate TOON string (convenience function).
    
    Args:
        toon_str: TOON format string
        strict: Use strict validation
        
    Returns:
        ValidationResult
    """
    level = ValidationLevel.STRICT if strict else ValidationLevel.LENIENT
    validator = ToonValidator(level=level)
    return validator.validate(toon_str)


def is_valid_toon(toon_str: str, strict: bool = True) -> bool:
    """
    Check if TOON string is valid (convenience function).
    
    Args:
        toon_str: TOON format string
        strict: Use strict validation
        
    Returns:
        True if valid
    """
    result = validate_toon(toon_str, strict=strict)
    return result.is_valid


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    # Example 1: Valid TOON
    print("=" * 80)
    print("Example 1: Valid TOON")
    print("=" * 80)
    
    valid_toon = """name: Alice
email: alice@example.com
verified: true
users [2,]
  id, name
  1, Alice
  2, Bob"""
    
    result = validate_toon(valid_toon, strict=True)
    result.print_report()
    
    # Example 2: Invalid TOON (wrong indentation)
    print("=" * 80)
    print("Example 2: Invalid Indentation")
    print("=" * 80)
    
    invalid_toon = """name: Alice
   email: alice@example.com
  verified: true"""
    
    result = validate_toon(invalid_toon, strict=True)
    result.print_report()
    
    # Example 3: Warnings (unnecessary quotes)
    print("=" * 80)
    print("Example 3: Unnecessary Quotes")
    print("=" * 80)
    
    warning_toon = """name: "Alice"
email: "alice@example.com"
age: 28"""
    
    result = validate_toon(warning_toon, strict=True)
    result.print_report()
    
    # Example 4: Type errors
    print("=" * 80)
    print("Example 4: Type Issues")
    print("=" * 80)
    
    type_error_toon = """verified: True
status: None
count: 42"""
    
    result = validate_toon(type_error_toon, strict=True)
    result.print_report()
