# YAML Format Examples for BDD Generator

## Example 1: Simple YAML Format

```yaml
feature: Google Search
description: Test Google search functionality
tags:
  - "@smoke"
  - "@search"

scenarios:
  - name: Search for rain news
    steps:
      - Given I am on Google
      - When I search for "rain news today"
      - Then I should see search results
```

## Example 2: YAML with Background

```yaml
feature: Google Search Automation
description: Comprehensive search testing

background:
  - Given I have a browser open
  - And I navigate to Google homepage

scenarios:
  - name: Search for news
    tags:
      - "@news"
    steps:
      - When I search for "rain news"
      - And I press Enter
      - Then I should see news results
      - And the results should be relevant
  
  - name: Search for weather
    tags:
      - "@weather"
    steps:
      - When I search for "weather forecast"
      - Then I should see weather information
      - And I should see a 7-day forecast
```

## Example 3: Multi-Scenario YAML

```yaml
feature: E2E Search Tests
description: End-to-end testing for various search types

tags:
  - "@regression"
  - "@e2e"

background:
  - Given the browser is configured
  - And I am on the Google homepage
  - And cookies are accepted

scenarios:
  - name: News search
    tags:
      - "@news"
      - "@priority-high"
    steps:
      - When I search for "breaking news today"
      - And I click on the News tab
      - Then I should see recent news articles
      - And articles should have timestamps
  
  - name: Image search
    tags:
      - "@images"
    steps:
      - When I search for "nature photography"
      - And I click on the Images tab
      - Then I should see image results
      - And images should be displayed in a grid
  
  - name: Video search
    tags:
      - "@videos"
    steps:
      - When I search for "cooking tutorials"
      - And I click on the Videos tab
      - Then I should see video results
      - And videos should have thumbnails
```

## API Usage with YAML

### Using curl
```bash
curl -X POST http://localhost:5001/api/bdd/generate \
  -H "Content-Type: application/json" \
  -d '{
    "specification": "feature: Google Search\ndescription: Test search\nscenarios:\n  - name: Search test\n    steps:\n      - When I search\n      - Then I see results"
  }'
```

### Using Python
```python
import yaml
from bdd_engine.generator import generate_bdd_test

# Load YAML from file
with open('test_spec.yaml', 'r') as f:
    yaml_content = f.read()

# Generate BDD test
result = generate_bdd_test(yaml_content)
print(f"Generated: {result['feature_name']}")
```

### Using Python with dict
```python
import yaml
from bdd_engine.generator import generate_bdd_test

# Define spec as YAML string
yaml_spec = """
feature: Google Search
background:
  - Given I am on Google
scenarios:
  - name: Search for news
    steps:
      - When I search for news
      - Then I see results
"""

# Generate test (auto-detects YAML format)
result = generate_bdd_test(yaml_spec)
```

## YAML File Example

Create a file `test_spec.yaml`:

```yaml
feature: Google Search Automation
description: Automated testing for Google search functionality

tags:
  - "@smoke"
  - "@search"
  - "@automated"

background:
  - Given I have Playwright configured
  - And I have a browser instance
  - And I navigate to https://www.google.com
  - And I accept cookies if prompted

scenarios:
  - name: Basic search functionality
    tags:
      - "@basic"
      - "@priority-high"
    steps:
      - When I enter "rain news today" in the search box
      - And I press the Enter key
      - And I wait for results to load
      - Then I should see the search results page
      - And the results should contain at least 5 items
      - And each result should have a title and URL
  
  - name: Search with filters
    tags:
      - "@filters"
    steps:
      - When I search for "technology news"
      - And I click on the Tools button
      - And I select "Past 24 hours" from the time filter
      - Then I should see recent technology news
      - And all results should be from the last 24 hours
  
  - name: Search autocomplete
    tags:
      - "@autocomplete"
      - "@ui"
    steps:
      - When I type "weath" in the search box
      - And I wait for autocomplete suggestions
      - Then I should see search suggestions
      - And suggestions should include "weather"
      - And I can click on a suggestion to search
```

## Benefits of YAML Format

✅ **Human-readable** - Clean, easy to read and write  
✅ **Hierarchical** - Natural structure for nested data  
✅ **No quotes needed** - Less syntax than JSON  
✅ **Comments supported** - Add notes with `#`  
✅ **Multi-line strings** - Easy to write long descriptions  
✅ **Lists** - Simple array syntax with `-`  
✅ **Auto-detected** - Generator automatically recognizes YAML

## YAML vs JSON vs Natural Language

| Feature | YAML | JSON | Natural Language |
|---------|------|------|------------------|
| Readability | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Structure | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Easy to write | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Comments | ✅ | ❌ | ✅ |
| Multi-line | ✅ | ⚠️ | ✅ |
| Validation | ✅ | ✅ | ❌ |

**Recommendation:** Use YAML for complex test suites with multiple scenarios and background steps!
