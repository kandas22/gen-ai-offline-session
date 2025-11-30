# BDD Generator Examples

## Example 1: Simple Format (Backward Compatible)

```python
specification = "Given I am on Google, When I search for rain news today, Then I should see news results"
```

## Example 2: Natural Language Format

```python
specification = """
Feature: Google Search for News
  As a user I want to search for news

Background:
  Given I have a browser open
  And I am connected to the internet

Scenario: Search for rain news
  Given I am on Google homepage
  When I search for "rain news today"
  And I wait for results to load
  Then I should see search results
  And the results should contain news articles

Scenario: Search for weather
  Given I am on Google homepage
  When I search for "weather forecast"
  Then I should see weather information
"""
```

## Example 3: Structured JSON Format

```python
specification = {
    "feature": "Google Search Automation",
    "description": "Test Google search functionality with different queries",
    "tags": ["@smoke", "@search"],
    "background": [
        "Given I have a browser configured",
        "And I am on the Google homepage"
    ],
    "scenarios": [
        {
            "name": "Search for rain news",
            "tags": ["@news"],
            "steps": [
                "When I search for 'rain news today'",
                "And I press Enter",
                "Then I should see search results",
                "And the results should be relevant"
            ]
        },
        {
            "name": "Search for weather",
            "tags": ["@weather"],
            "steps": [
                "When I search for 'weather forecast'",
                "And I click the search button",
                "Then I should see weather information",
                "And I should see a 7-day forecast"
            ]
        }
    ]
}
```

## API Usage

### Using Simple Format
```bash
curl -X POST http://localhost:5001/api/bdd/generate \
  -H "Content-Type: application/json" \
  -d '{
    "specification": "Given I am on Google, When I search for rain news, Then I should see results"
  }'
```

### Using Natural Language Format
```bash
curl -X POST http://localhost:5001/api/bdd/generate \
  -H "Content-Type: application/json" \
  -d '{
    "specification": "Feature: Google Search\nBackground:\n  Given I open browser\nScenario: Search news\n  When I search for rain\n  Then I see results"
  }'
```

### Using Structured JSON Format
```bash
curl -X POST http://localhost:5001/api/bdd/generate \
  -H "Content-Type: application/json" \
  -d '{
    "specification": {
      "feature": "Google Search",
      "description": "Search functionality tests",
      "background": ["Given I am on Google"],
      "scenarios": [
        {
          "name": "Search for news",
          "steps": [
            "When I search for rain news",
            "Then I should see results"
          ]
        }
      ]
    }
  }'
```

## Generated Output Example

```gherkin
Feature: Google Search Automation
  Test Google search functionality with different queries
  @smoke @search

  Background:
    Given I have a browser configured
    And I am on the Google homepage

  Scenario: Search for rain news
    @news
    When I search for 'rain news today'
    And I press Enter
    Then I should see search results
    And the results should be relevant

  Scenario: Search for weather
    @weather
    When I search for 'weather forecast'
    And I click the search button
    Then I should see weather information
    And I should see a 7-day forecast
```

## Supported Gherkin Keywords

- **Feature:** - Feature name and description
- **Background:** - Common setup steps for all scenarios
- **Scenario:** - Individual test scenario
- **Given** - Preconditions
- **When** - Actions
- **Then** - Expected outcomes
- **And** - Additional steps (continues previous step type)
- **But** - Negative conditions
- **Tags:** - @tag1 @tag2 (for categorization)

## Key Features

✅ **Multiple Input Formats** - Simple, natural language, or JSON  
✅ **Background Support** - Common setup steps  
✅ **Multiple Scenarios** - Test multiple cases in one feature  
✅ **Tags** - Organize and filter tests  
✅ **And/But Steps** - Complex step chains  
✅ **Backward Compatible** - Works with existing simple format
