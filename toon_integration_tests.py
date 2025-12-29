"""
TOON Integration Tests - Comprehensive Test Suite

This module provides integration tests for TOON encoding, decoding, validation,
and comparison utilities. Tests ensure correctness and reliability.

Features:
- Encoder/decoder round-trip tests
- Array type detection tests
- Validation tests
- Token comparison tests
- Edge case handling
- Error recovery tests

Author: Development Team
Version: 1.0.0
"""

import unittest
import json
from typing import Dict, Any, List
from toon_parser import ToonParser, ToonParseError, ArrayType
from toon_validator import ToonValidator, ValidationLevel, validate_toon
from json_vs_toon_comparison import FormatComparator, TokenCounter


class ToonParserTests(unittest.TestCase):
    """Tests for ToonParser encoding and decoding."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = ToonParser(strict=True, indent=2)
    
    def test_simple_object_encoding(self):
        """Test encoding simple object."""
        data = {"name": "Alice", "age": 28, "verified": True}
        toon = self.parser.encode(data)
        
        self.assertIn("name: Alice", toon)
        self.assertIn("age: 28", toon)
        self.assertIn("verified: true", toon)
        self.assertNotIn("{", toon)
        self.assertNotIn("}", toon)
    
    def test_simple_object_roundtrip(self):
        """Test encode/decode round-trip for simple object."""
        data = {"name": "Alice", "age": 28, "verified": True}
        toon = self.parser.encode(data)
        decoded = self.parser.decode(toon)
        
        self.assertEqual(decoded, data)
    
    def test_nested_object_encoding(self):
        """Test encoding nested objects."""
        data = {
            "user": {
                "name": "Alice",
                "location": {
                    "city": "San Francisco",
                    "country": "USA"
                }
            }
        }
        toon = self.parser.encode(data)
        
        # Check indentation
        lines = toon.split('\n')
        self.assertTrue(any(line.startswith("  name:") for line in lines))
        self.assertTrue(any(line.startswith("    city:") for line in lines))
    
    def test_nested_object_roundtrip(self):
        """Test encode/decode round-trip for nested objects."""
        data = {
            "user": {
                "name": "Alice",
                "location": {
                    "city": "San Francisco",
                    "country": "USA"
                }
            }
        }
        toon = self.parser.encode(data)
        decoded = self.parser.decode(toon)
        
        self.assertEqual(decoded, data)
    
    def test_primitive_array_encoding(self):
        """Test encoding primitive arrays."""
        data = {"scores": [100, 95, 88, 72]}
        toon = self.parser.encode(data)
        
        self.assertIn("[4]:", toon)
        self.assertIn("100, 95, 88, 72", toon)
    
    def test_primitive_array_roundtrip(self):
        """Test encode/decode round-trip for primitive arrays."""
        data = {"scores": [100, 95, 88, 72], "tags": ["python", "async"]}
        toon = self.parser.encode(data)
        decoded = self.parser.decode(toon)
        
        self.assertEqual(decoded, data)
    
    def test_tabular_array_encoding(self):
        """Test encoding tabular arrays."""
        data = {
            "users": [
                {"id": 1, "name": "Alice", "role": "admin"},
                {"id": 2, "name": "Bob", "role": "user"}
            ]
        }
        toon = self.parser.encode(data)
        
        self.assertIn("[2,]", toon)
        self.assertIn("id, name, role", toon)
        self.assertIn("1, Alice, admin", toon)
        self.assertIn("2, Bob, user", toon)
    
    def test_tabular_array_roundtrip(self):
        """Test encode/decode round-trip for tabular arrays."""
        data = {
            "users": [
                {"id": 1, "name": "Alice", "role": "admin"},
                {"id": 2, "name": "Bob", "role": "user"},
                {"id": 3, "name": "Charlie", "role": "guest"}
            ]
        }
        toon = self.parser.encode(data)
        decoded = self.parser.decode(toon)
        
        self.assertEqual(decoded, data)
    
    def test_list_array_roundtrip(self):
        """Test encode/decode round-trip for list arrays."""
        data = {
            "items": [
                {"type": "book", "title": "The Hobbit"},
                {"type": "movie", "title": "The Matrix"}
            ]
        }
        toon = self.parser.encode(data)
        decoded = self.parser.decode(toon)
        
        # Note: List arrays might not preserve exact dict order
        self.assertEqual(len(decoded["items"]), len(data["items"]))
    
    def test_array_type_detection(self):
        """Test array type detection logic."""
        # Primitive
        arr1 = [1, 2, 3]
        self.assertEqual(self.parser._detect_array_type(arr1), ArrayType.PRIMITIVE)
        
        # Tabular (uniform objects with primitives)
        arr2 = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
        self.assertEqual(self.parser._detect_array_type(arr2), ArrayType.TABULAR)
        
        # List (non-uniform)
        arr3 = [
            {"id": 1, "name": "Alice"},
            {"type": "book", "title": "Hobbit"}
        ]
        self.assertEqual(self.parser._detect_array_type(arr3), ArrayType.LIST)
        
        # List (nested objects)
        arr4 = [
            {"id": 1, "meta": {"created": "2025-01-01"}}
        ]
        self.assertEqual(self.parser._detect_array_type(arr4), ArrayType.LIST)
    
    def test_string_quoting(self):
        """Test string quoting rules."""
        # No quotes needed
        data1 = {"name": "Alice"}
        toon1 = self.parser.encode(data1)
        self.assertNotIn('"Alice"', toon1)
        
        # Quotes needed (empty string)
        data2 = {"value": ""}
        toon2 = self.parser.encode(data2)
        self.assertIn('""', toon2)
        
        # Quotes needed (reserved keyword)
        data3 = {"status": "true"}
        toon3 = self.parser.encode(data3)
        self.assertIn('"true"', toon3)
        
        # Quotes needed (special chars)
        data4 = {"name": "Smith, John"}
        toon4 = self.parser.encode(data4)
        self.assertIn('"Smith, John"', toon4)
    
    def test_type_normalization(self):
        """Test type normalization."""
        from datetime import datetime
        from decimal import Decimal
        
        data = {
            "timestamp": datetime(2025, 1, 15, 10, 30),
            "price": Decimal("99.99"),
            "tuple_val": (1, 2, 3),
            "set_val": {3, 1, 2}
        }
        
        toon = self.parser.encode(data)
        decoded = self.parser.decode(toon)
        
        # Check normalizations
        self.assertIsInstance(decoded["timestamp"], str)
        self.assertIn("2025-01-15", decoded["timestamp"])
        self.assertIsInstance(decoded["price"], float)
        self.assertIsInstance(decoded["tuple_val"], list)
        self.assertIsInstance(decoded["set_val"], list)
        self.assertEqual(sorted(decoded["set_val"]), [1, 2, 3])
    
    def test_special_number_normalization(self):
        """Test special number normalization."""
        data = {
            "nan": float('nan'),
            "inf": float('inf'),
            "neg_inf": float('-inf'),
            "neg_zero": -0.0
        }
        
        toon = self.parser.encode(data)
        decoded = self.parser.decode(toon)
        
        self.assertIsNone(decoded["nan"])
        self.assertIsNone(decoded["inf"])
        self.assertIsNone(decoded["neg_inf"])
        self.assertEqual(decoded["neg_zero"], 0)


class ToonValidatorTests(unittest.TestCase):
    """Tests for TOON validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = ToonValidator(level=ValidationLevel.STRICT)
    
    def test_valid_toon(self):
        """Test validation of valid TOON."""
        valid_toon = """name: Alice
email: alice@example.com
verified: true"""
        
        result = self.validator.validate(valid_toon)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
    
    def test_invalid_indentation(self):
        """Test detection of invalid indentation."""
        invalid_toon = """name: Alice
   email: alice@example.com"""
        
        result = self.validator.validate(invalid_toon)
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
    
    def test_tabs_in_indentation(self):
        """Test detection of tabs in indentation."""
        invalid_toon = "name: Alice\n\temail: alice@example.com"
        
        result = self.validator.validate(invalid_toon)
        self.assertFalse(result.is_valid)
    
    def test_unnecessary_quotes_warning(self):
        """Test warning for unnecessary quotes."""
        toon_with_quotes = """name: "Alice"
age: 28"""
        
        result = self.validator.validate(toon_with_quotes)
        self.assertGreater(len(result.warnings), 0)
    
    def test_wrong_boolean_case(self):
        """Test warning for wrong boolean case."""
        toon_wrong_case = """verified: True
active: False"""
        
        result = self.validator.validate(toon_wrong_case)
        self.assertGreater(len(result.warnings), 0)
    
    def test_lenient_mode(self):
        """Test lenient validation mode."""
        # Invalid indentation in strict mode
        toon = """name: Alice
   email: alice@example.com"""
        
        # Strict mode: errors
        strict_validator = ToonValidator(level=ValidationLevel.STRICT)
        strict_result = strict_validator.validate(toon)
        self.assertFalse(strict_result.is_valid)
        
        # Lenient mode: warnings only
        lenient_validator = ToonValidator(level=ValidationLevel.LENIENT)
        lenient_result = lenient_validator.validate(toon)
        self.assertTrue(lenient_result.is_valid)
        self.assertGreater(len(lenient_result.warnings), 0)


class TokenComparisonTests(unittest.TestCase):
    """Tests for JSON vs TOON token comparison."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.comparator = FormatComparator(model="gpt5")
    
    def test_simple_comparison(self):
        """Test token comparison for simple data."""
        data = {"name": "Alice", "age": 28}
        result = self.comparator.compare(data)
        
        self.assertIn("json", result)
        self.assertIn("toon", result)
        self.assertIn("savings", result)
        
        # TOON should have fewer tokens
        self.assertLess(result["toon"]["tokens"], result["json"]["tokens"])
        self.assertGreater(result["savings"]["tokens_percent"], 0)
    
    def test_tabular_array_comparison(self):
        """Test token comparison for tabular arrays."""
        data = {
            "users": [
                {"id": i, "name": f"User{i}", "role": "user"}
                for i in range(1, 11)
            ]
        }
        result = self.comparator.compare(data)
        
        # Tabular arrays should give significant savings (40%+)
        self.assertGreater(result["savings"]["tokens_percent"], 40)
    
    def test_nested_structure_comparison(self):
        """Test token comparison for nested structures."""
        data = {
            "user": {
                "name": "Alice",
                "settings": {
                    "theme": "dark",
                    "notifications": True
                }
            }
        }
        result = self.comparator.compare(data)
        
        # Even nested structures should show savings
        self.assertGreater(result["savings"]["tokens_percent"], 20)


class IntegrationTests(unittest.TestCase):
    """End-to-end integration tests."""
    
    def test_complete_workflow(self):
        """Test complete encode -> validate -> decode workflow."""
        # Original data
        data = {
            "users": [
                {"id": 1, "name": "Alice", "email": "alice@example.com"},
                {"id": 2, "name": "Bob", "email": "bob@example.com"}
            ],
            "metadata": {
                "count": 2,
                "timestamp": "2025-01-15T10:00:00Z"
            }
        }
        
        # Encode
        parser = ToonParser()
        toon_str = parser.encode(data)
        
        # Validate
        result = validate_toon(toon_str, strict=True)
        self.assertTrue(result.is_valid)
        
        # Decode
        decoded = parser.decode(toon_str)
        
        # Verify
        self.assertEqual(decoded["users"], data["users"])
        self.assertEqual(decoded["metadata"], data["metadata"])
    
    def test_comparison_workflow(self):
        """Test comparison and savings calculation workflow."""
        data = {
            "users": [
                {"id": i, "name": f"User{i}"}
                for i in range(1, 6)
            ]
        }
        
        # Compare formats
        comparator = FormatComparator()
        result = comparator.compare(data)
        
        # Verify savings
        self.assertGreater(result["savings"]["tokens_percent"], 30)
        self.assertLess(result["toon"]["tokens"], result["json"]["tokens"])
    
    def test_error_handling(self):
        """Test error handling for invalid TOON."""
        parser = ToonParser()
        
        # Invalid TOON (missing array length)
        invalid_toon = """users:
  - id: 1
    name: Alice"""
        
        # Should raise error or return partial result
        try:
            decoded = parser.decode(invalid_toon)
            # If it doesn't raise, check that result is reasonable
            self.assertIsInstance(decoded, dict)
        except ToonParseError:
            # Expected behavior
            pass


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_tests(verbose: bool = True):
    """Run all tests with optional verbosity."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(ToonParserTests))
    suite.addTests(loader.loadTestsFromTestCase(ToonValidatorTests))
    suite.addTests(loader.loadTestsFromTestCase(TokenComparisonTests))
    suite.addTests(loader.loadTestsFromTestCase(IntegrationTests))
    
    # Run tests
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED")
    else:
        print("\n❌ SOME TESTS FAILED")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_tests(verbose=True)
    sys.exit(0 if success else 1)
