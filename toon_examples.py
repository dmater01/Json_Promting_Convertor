"""
TOON Examples - Real-World Conversion Examples

This module provides comprehensive examples of converting various data structures
from JSON to TOON format, demonstrating the 30-60% token savings in practice.

Includes:
- 12 real-world use case examples
- Before/after comparisons
- Token savings calculations
- Best practice demonstrations

Author: Development Team
Version: 1.0.0
"""

import json
from typing import Dict, Any
from toon_parser import ToonParser
from json_vs_toon_comparison import FormatComparator


# ============================================================================
# EXAMPLE 1: SIMPLE USER PROFILE
# ============================================================================

EXAMPLE_1_NAME = "Simple User Profile"
EXAMPLE_1_DATA = {
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "verified": True,
    "age": 28,
    "role": "admin"
}

EXAMPLE_1_JSON = json.dumps(EXAMPLE_1_DATA, indent=2)

EXAMPLE_1_TOON = """name: Alice Johnson
email: alice@example.com
verified: true
age: 28
role: admin"""


# ============================================================================
# EXAMPLE 2: USER LIST (TABULAR - MAXIMUM EFFICIENCY)
# ============================================================================

EXAMPLE_2_NAME = "User List (Tabular Array)"
EXAMPLE_2_DATA = {
    "users": [
        {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "admin"},
        {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "user"},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com", "role": "guest"}
    ]
}

EXAMPLE_2_JSON = json.dumps(EXAMPLE_2_DATA, indent=2)

EXAMPLE_2_TOON = """users [3,]
  id, name, email, role
  1, Alice, alice@example.com, admin
  2, Bob, bob@example.com, user
  3, Charlie, charlie@example.com, guest"""


# ============================================================================
# EXAMPLE 3: NESTED CONFIGURATION
# ============================================================================

EXAMPLE_3_NAME = "Nested Configuration"
EXAMPLE_3_DATA = {
    "server": {
        "host": "localhost",
        "port": 8000,
        "debug": True
    },
    "database": {
        "url": "postgresql://localhost/mydb",
        "pool_size": 10,
        "timeout": 30
    },
    "features": {
        "auth": True,
        "logging": True,
        "caching": False
    }
}

EXAMPLE_3_JSON = json.dumps(EXAMPLE_3_DATA, indent=2)

EXAMPLE_3_TOON = """server:
  host: localhost
  port: 8000
  debug: true
database:
  url: postgresql://localhost/mydb
  pool_size: 10
  timeout: 30
features:
  auth: true
  logging: true
  caching: false"""


# ============================================================================
# EXAMPLE 4: CONTACT EXTRACTION
# ============================================================================

EXAMPLE_4_NAME = "Contact Extraction"
EXAMPLE_4_DATA = {
    "intent": "extract",
    "subject": "contacts",
    "entities": {
        "contacts": [
            {"name": "Alice", "email": "alice@example.com", "phone": "555-0123"},
            {"name": "Bob", "email": "bob@example.com", "phone": "555-0124"},
            {"name": "Charlie", "email": "charlie@example.com", "phone": "555-0125"}
        ]
    },
    "output_format": "tabular",
    "original_language": "en",
    "confidence_score": 0.97
}

EXAMPLE_4_JSON = json.dumps(EXAMPLE_4_DATA, indent=2)

EXAMPLE_4_TOON = """intent: extract
subject: contacts
entities:
  contacts [3,]
    name, email, phone
    Alice, alice@example.com, 555-0123
    Bob, bob@example.com, 555-0124
    Charlie, charlie@example.com, 555-0125
output_format: tabular
original_language: en
confidence_score: 0.97"""


# ============================================================================
# EXAMPLE 5: SENTIMENT ANALYSIS
# ============================================================================

EXAMPLE_5_NAME = "Sentiment Analysis Result"
EXAMPLE_5_DATA = {
    "intent": "analyze",
    "subject": "sentiment",
    "entities": {
        "sentiment": "positive",
        "score": 0.95,
        "aspects": [
            {"category": "quality", "sentiment": "positive", "score": 0.98},
            {"category": "price", "sentiment": "neutral", "score": 0.50},
            {"category": "service", "sentiment": "positive", "score": 0.92}
        ],
        "keywords": ["amazing", "quality", "exceeded", "expectations"]
    },
    "output_format": "sentiment_analysis",
    "original_language": "en",
    "confidence_score: 0.94
}

EXAMPLE_5_JSON = json.dumps(EXAMPLE_5_DATA, indent=2)

EXAMPLE_5_TOON = """intent: analyze
subject: sentiment
entities:
  sentiment: positive
  score: 0.95
  aspects [3,]
    category, sentiment, score
    quality, positive, 0.98
    price, neutral, 0.50
    service, positive, 0.92
  keywords [4]: amazing, quality, exceeded, expectations
output_format: sentiment_analysis
original_language: en
confidence_score: 0.94"""


# ============================================================================
# EXAMPLE 6: API ENDPOINTS CONFIGURATION
# ============================================================================

EXAMPLE_6_NAME = "API Endpoints Configuration"
EXAMPLE_6_DATA = {
    "api_version": "v1",
    "base_url": "https://api.example.com",
    "endpoints": [
        {"method": "GET", "path": "/users", "auth_required": True, "rate_limit": 100},
        {"method": "POST", "path": "/users", "auth_required": True, "rate_limit": 50},
        {"method": "GET", "path": "/users/{id}", "auth_required": True, "rate_limit": 200},
        {"method": "DELETE", "path": "/users/{id}", "auth_required": True, "rate_limit": 20},
        {"method": "GET", "path": "/health", "auth_required": False, "rate_limit": 1000}
    ]
}

EXAMPLE_6_JSON = json.dumps(EXAMPLE_6_DATA, indent=2)

EXAMPLE_6_TOON = """api_version: v1
base_url: https://api.example.com
endpoints [5,]
  method, path, auth_required, rate_limit
  GET, /users, true, 100
  POST, /users, true, 50
  GET, /users/{id}, true, 200
  DELETE, /users/{id}, true, 20
  GET, /health, false, 1000"""


# ============================================================================
# EXAMPLE 7: MEETING SCHEDULE EXTRACTION
# ============================================================================

EXAMPLE_7_NAME = "Meeting Schedule Extraction"
EXAMPLE_7_DATA = {
    "intent": "schedule",
    "subject": "meeting",
    "entities": {
        "meeting_type": "standup",
        "schedule": {
            "day": "Monday",
            "time": "10:00 AM",
            "timezone": "EST",
            "duration": "30 minutes"
        },
        "participants": ["John", "Sarah", "Mike", "Emily"],
        "topics": ["Q4 roadmap", "budget allocation", "team expansion"],
        "location": "Conference Room A"
    },
    "output_format": "structured",
    "original_language": "en",
    "confidence_score": 0.89
}

EXAMPLE_7_JSON = json.dumps(EXAMPLE_7_DATA, indent=2)

EXAMPLE_7_TOON = """intent: schedule
subject: meeting
entities:
  meeting_type: standup
  schedule:
    day: Monday
    time: 10:00 AM
    timezone: EST
    duration: 30 minutes
  participants [4]: John, Sarah, Mike, Emily
  topics [3]: Q4 roadmap, budget allocation, team expansion
  location: Conference Room A
output_format: structured
original_language: en
confidence_score: 0.89"""


# ============================================================================
# EXAMPLE 8: PRODUCT INVENTORY
# ============================================================================

EXAMPLE_8_NAME = "Product Inventory"
EXAMPLE_8_DATA = {
    "products": [
        {"sku": "PROD-001", "name": "Laptop", "price": 999.99, "stock": 45, "category": "electronics"},
        {"sku": "PROD-002", "name": "Mouse", "price": 29.99, "stock": 150, "category": "electronics"},
        {"sku": "PROD-003", "name": "Desk", "price": 349.99, "stock": 12, "category": "furniture"},
        {"sku": "PROD-004", "name": "Chair", "price": 199.99, "stock": 28, "category": "furniture"},
        {"sku": "PROD-005", "name": "Monitor", "price": 399.99, "stock": 67, "category": "electronics"}
    ],
    "last_updated": "2025-01-15T10:30:00Z",
    "total_items": 5
}

EXAMPLE_8_JSON = json.dumps(EXAMPLE_8_DATA, indent=2)

EXAMPLE_8_TOON = """products [5,]
  sku, name, price, stock, category
  PROD-001, Laptop, 999.99, 45, electronics
  PROD-002, Mouse, 29.99, 150, electronics
  PROD-003, Desk, 349.99, 12, furniture
  PROD-004, Chair, 199.99, 28, furniture
  PROD-005, Monitor, 399.99, 67, electronics
last_updated: 2025-01-15T10:30:00Z
total_items: 5"""


# ============================================================================
# EXAMPLE 9: INVOICE DATA
# ============================================================================

EXAMPLE_9_NAME = "Invoice Data"
EXAMPLE_9_DATA = {
    "invoice_id": "INV-2025-001",
    "date": "2025-01-15",
    "customer": {
        "name": "Acme Corp",
        "email": "billing@acme.com",
        "address": "123 Main St, San Francisco, CA"
    },
    "items": [
        {"description": "Consulting Services", "quantity": 40, "rate": 150.00, "amount": 6000.00},
        {"description": "Software License", "quantity": 5, "rate": 299.00, "amount": 1495.00},
        {"description": "Support Package", "quantity": 1, "rate": 500.00, "amount": 500.00}
    ],
    "subtotal": 7995.00,
    "tax": 799.50,
    "total": 8794.50
}

EXAMPLE_9_JSON = json.dumps(EXAMPLE_9_DATA, indent=2)

EXAMPLE_9_TOON = """invoice_id: INV-2025-001
date: 2025-01-15
customer:
  name: Acme Corp
  email: billing@acme.com
  address: "123 Main St, San Francisco, CA"
items [3,]
  description, quantity, rate, amount
  Consulting Services, 40, 150.00, 6000.00
  Software License, 5, 299.00, 1495.00
  Support Package, 1, 500.00, 500.00
subtotal: 7995.00
tax: 799.50
total: 8794.50"""


# ============================================================================
# EXAMPLE 10: LOG ENTRIES
# ============================================================================

EXAMPLE_10_NAME = "Application Log Entries"
EXAMPLE_10_DATA = {
    "logs": [
        {"timestamp": "2025-01-15T10:00:00Z", "level": "INFO", "message": "User logged in", "user_id": "user123"},
        {"timestamp": "2025-01-15T10:01:00Z", "level": "WARN", "message": "Password nearing expiration", "user_id": "user123"},
        {"timestamp": "2025-01-15T10:02:00Z", "level": "INFO", "message": "Profile updated", "user_id": "user123"},
        {"timestamp": "2025-01-15T10:03:00Z", "level": "ERROR", "message": "Failed to send email", "user_id": "user123"},
        {"timestamp": "2025-01-15T10:05:00Z", "level": "INFO", "message": "User logged out", "user_id": "user123"}
    ]
}

EXAMPLE_10_JSON = json.dumps(EXAMPLE_10_DATA, indent=2)

EXAMPLE_10_TOON = """logs [5,]
  timestamp, level, message, user_id
  2025-01-15T10:00:00Z, INFO, User logged in, user123
  2025-01-15T10:01:00Z, WARN, Password nearing expiration, user123
  2025-01-15T10:02:00Z, INFO, Profile updated, user123
  2025-01-15T10:03:00Z, ERROR, Failed to send email, user123
  2025-01-15T10:05:00Z, INFO, User logged out, user123"""


# ============================================================================
# EXAMPLE 11: FEATURE FLAGS
# ============================================================================

EXAMPLE_11_NAME = "Feature Flags Configuration"
EXAMPLE_11_DATA = {
    "environment": "production",
    "features": {
        "new_ui": {"enabled": True, "rollout": 100, "description": "New user interface"},
        "beta_search": {"enabled": True, "rollout": 25, "description": "Beta search algorithm"},
        "dark_mode": {"enabled": True, "rollout": 100, "description": "Dark mode theme"},
        "ai_assist": {"enabled": False, "rollout": 0, "description": "AI assistance feature"},
        "analytics": {"enabled": True, "rollout": 100, "description": "Advanced analytics"}
    },
    "updated": "2025-01-15T10:00:00Z"
}

EXAMPLE_11_JSON = json.dumps(EXAMPLE_11_DATA, indent=2)

EXAMPLE_11_TOON = """environment: production
features [5]
  - name: new_ui
    enabled: true
    rollout: 100
    description: New user interface
  - name: beta_search
    enabled: true
    rollout: 25
    description: Beta search algorithm
  - name: dark_mode
    enabled: true
    rollout: 100
    description: Dark mode theme
  - name: ai_assist
    enabled: false
    rollout: 0
    description: AI assistance feature
  - name: analytics
    enabled: true
    rollout: 100
    description: Advanced analytics
updated: 2025-01-15T10:00:00Z"""


# ============================================================================
# EXAMPLE 12: LARGE USER LIST
# ============================================================================

EXAMPLE_12_NAME = "Large User List (50 users)"
EXAMPLE_12_DATA = {
    "users": [
        {"id": i, "name": f"User{i}", "email": f"user{i}@example.com", 
         "role": "admin" if i % 5 == 0 else "user", "active": True}
        for i in range(1, 51)
    ]
}

EXAMPLE_12_JSON = json.dumps(EXAMPLE_12_DATA, indent=2)

# TOON version (will be generated)
EXAMPLE_12_TOON = None  # Generated dynamically


# ============================================================================
# EXAMPLE RUNNER
# ============================================================================

class ExampleRunner:
    """Run and display all examples with comparisons."""
    
    def __init__(self):
        """Initialize runner."""
        self.parser = ToonParser()
        self.comparator = FormatComparator()
        
        self.examples = [
            (EXAMPLE_1_NAME, EXAMPLE_1_DATA, EXAMPLE_1_TOON),
            (EXAMPLE_2_NAME, EXAMPLE_2_DATA, EXAMPLE_2_TOON),
            (EXAMPLE_3_NAME, EXAMPLE_3_DATA, EXAMPLE_3_TOON),
            (EXAMPLE_4_NAME, EXAMPLE_4_DATA, EXAMPLE_4_TOON),
            (EXAMPLE_5_NAME, EXAMPLE_5_DATA, EXAMPLE_5_TOON),
            (EXAMPLE_6_NAME, EXAMPLE_6_DATA, EXAMPLE_6_TOON),
            (EXAMPLE_7_NAME, EXAMPLE_7_DATA, EXAMPLE_7_TOON),
            (EXAMPLE_8_NAME, EXAMPLE_8_DATA, EXAMPLE_8_TOON),
            (EXAMPLE_9_NAME, EXAMPLE_9_DATA, EXAMPLE_9_TOON),
            (EXAMPLE_10_NAME, EXAMPLE_10_DATA, EXAMPLE_10_TOON),
            (EXAMPLE_11_NAME, EXAMPLE_11_DATA, EXAMPLE_11_TOON),
        ]
    
    def run_example(self, example_num: int, show_output: bool = True):
        """
        Run a specific example.
        
        Args:
            example_num: Example number (1-11)
            show_output: Whether to show JSON/TOON output
        """
        if example_num < 1 or example_num > len(self.examples):
            print(f"Example {example_num} not found.")
            return
        
        name, data, expected_toon = self.examples[example_num - 1]
        
        print("=" * 80)
        print(f"EXAMPLE {example_num}: {name}")
        print("=" * 80)
        print()
        
        # Generate TOON
        generated_toon = self.parser.encode(data)
        
        # Compare
        result = self.comparator.compare(data)
        
        print(f"Token Savings: {result['savings']['tokens_percent']:.1f}% "
              f"({result['savings']['tokens']} tokens)")
        print(f"JSON: {result['json']['tokens']} tokens")
        print(f"TOON: {result['toon']['tokens']} tokens")
        print()
        
        if show_output:
            print("JSON Output:")
            print("-" * 80)
            print(json.dumps(data, indent=2))
            print()
            print("TOON Output:")
            print("-" * 80)
            print(generated_toon)
            print()
    
    def run_all(self, show_output: bool = False):
        """Run all examples."""
        print("\n")
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 25 + "TOON EXAMPLES SHOWCASE" + " " * 31 + "║")
        print("╚" + "=" * 78 + "╝")
        print()
        
        for i in range(1, len(self.examples) + 1):
            self.run_example(i, show_output=show_output)
            if i < len(self.examples):
                print()
        
        # Summary
        print()
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print()
        
        total_json = 0
        total_toon = 0
        
        for name, data, _ in self.examples:
            result = self.comparator.compare(data)
            total_json += result['json']['tokens']
            total_toon += result['toon']['tokens']
        
        total_savings = total_json - total_toon
        percent = (total_savings / total_json * 100) if total_json > 0 else 0
        
        print(f"Total Examples: {len(self.examples)}")
        print(f"Total JSON Tokens: {total_json}")
        print(f"Total TOON Tokens: {total_toon}")
        print(f"Total Savings: {total_savings} tokens ({percent:.1f}%)")
        print()
        print(f"🎯 Average Token Savings: {percent:.1f}%")
        print()


# ============================================================================
# MAIN DEMO
# ============================================================================

def main():
    """Run all examples."""
    runner = ExampleRunner()
    runner.run_all(show_output=False)
    
    # Show one detailed example
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 27 + "DETAILED EXAMPLE" + " " * 35 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    runner.run_example(2, show_output=True)  # Show user list example


if __name__ == "__main__":
    main()
