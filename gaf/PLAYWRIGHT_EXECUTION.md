# Amazon E2E Testing with Playwright

## Overview
The `/api/bdd/generate-and-execute` endpoint now supports real-time Playwright execution for Amazon E2E tests using your JSON specification format.

## New Endpoints

### 1. Generate and Execute (Recommended)
**POST** `/api/bdd/generate-and-execute`

Generates BDD feature file AND executes it with Playwright in real-time.

**Request Body:**
```json
{
  "specification": {
    "feature": {
      "name": "Amazon Product Search and Cart Validation",
      "description": "As a user, I want to search for products...",
      "tags": ["@amazon", "@e2e"]
    },
    "scenarios": [...],
    "configuration": {
      "base_url": "https://www.amazon.com",
      "timeout": 30000,
      "browser": "chromium",
      "headless": false
    }
  },
  "execute_immediately": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "generation": {
      "test_id": "abc123",
      "feature_file": "/path/to/feature.feature"
    },
    "execution": {
      "feature": {...},
      "scenarios": [
        {
          "scenario_id": "SC001",
          "scenario_name": "Successfully add single product to cart",
          "status": "passed",
          "steps": [...]
        }
      ],
      "summary": {
        "total": 4,
        "passed": 3,
        "failed": 1,
        "pass_rate": "75.00%"
      }
    }
  }
}
```

### 2. Execute Only
**POST** `/api/bdd/execute-playwright`

Execute Playwright test from specification (without generating BDD file).

## Supported Step Types

### Given Steps
- Navigate to URL
- Set up preconditions

```json
{
  "step": "User navigates to Amazon homepage",
  "url": "https://www.amazon.com",
  "expected_state": "homepage_loaded"
}
```

### When Steps
- **Search**: Fill input and search
- **Click**: Click elements
- **Navigate**: Go to URL

```json
{
  "step": "User searches for product",
  "action": "search",
  "search_term": "iPhone 15",
  "element": {
    "type": "input",
    "locator": "#twotabsearchtextbox",
    "locator_type": "css"
  }
}
```

### Then Steps (Validations)
- **element_visible**: Check if element is visible
- **element_exists**: Check if element exists
- **cart_items_count**: Validate cart count
- **text_content**: Validate text content
- **text_contains**: Check if text contains substring

```json
{
  "step": "Validate cart is not empty",
  "validation_type": "cart_items_count",
  "expected_result": "greater_than_0"
}
```

## Configuration Options

```json
{
  "base_url": "https://www.amazon.com",
  "timeout": 30000,           // Default timeout in ms
  "implicit_wait": 10,        // Implicit wait in seconds
  "browser": "chromium",      // chromium, firefox, or webkit
  "headless": false           // Run in headless mode
}
```

## Example Usage

### Using curl:
```bash
curl -X POST http://localhost:5001/api/bdd/generate-and-execute \
  -H "Content-Type: application/json" \
  -d @amazon_test_spec.json
```

### Using Python:
```python
import requests

spec = {
    "specification": {
        "feature": {
            "name": "Amazon Cart Test",
            "description": "Test cart functionality"
        },
        "scenarios": [...],
        "configuration": {
            "browser": "chromium",
            "headless": False
        }
    }
}

response = requests.post(
    'http://localhost:5001/api/bdd/generate-and-execute',
    json=spec
)

result = response.json()
print(f"Test Status: {result['data']['execution']['status']}")
print(f"Pass Rate: {result['data']['execution']['summary']['pass_rate']}")
```

## Test Results Structure

Each scenario returns detailed step-by-step results:

```json
{
  "scenario_id": "SC001",
  "scenario_name": "Successfully add single product to cart",
  "status": "passed",
  "steps": [
    {
      "step": "User navigates to Amazon homepage",
      "type": "given",
      "status": "passed",
      "message": "Navigated to https://www.amazon.com",
      "timestamp": "2025-11-30T09:00:00"
    },
    {
      "step": "User searches for product",
      "type": "when",
      "status": "passed",
      "message": "Entered 'iPhone 15' in search box",
      "timestamp": "2025-11-30T09:00:01"
    }
  ],
  "start_time": "2025-11-30T09:00:00",
  "end_time": "2025-11-30T09:00:30"
}
```

## Notes

- The browser will use your existing Amazon login session if you're already logged in
- Set `headless: false` to see the browser automation in action
- All steps are executed sequentially
- Failed steps will stop scenario execution
- Screenshots can be captured on failure (coming soon)
