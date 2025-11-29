# E2E Test Guide

## Running the E2E Test

This test validates the complete BDD workflow:
1. **API Call** - Generates BDD test via `/api/bdd/generate`
2. **Feature Validation** - Verifies generated Gherkin file
3. **Playwright Execution** - Runs real Google search scenario
4. **Result Validation** - Checks search results and titles

## Prerequisites

1. **Start the Flask API:**
   ```bash
   python app.py
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

## Run the Test

```bash
python test_e2e_bdd_api.py
```

## What the Test Does

### Test 1: Complete E2E with Playwright
1. Sends YAML spec to `/api/bdd/generate`
2. Validates generated feature file
3. Opens browser with Playwright
4. Executes the scenario:
   - Navigate to Google
   - Search for "rain news today"
   - Wait for results
   - Validate results are visible
   - Check titles contain relevant keywords
5. Takes screenshot
6. Reports success/failure

### Test 2: JSON Format
- Tests BDD generation with JSON input

### Test 3: Natural Language Format
- Tests BDD generation with Gherkin text input

## Expected Output

```
🚀 Starting E2E Tests...

============================================================
E2E Test: BDD Generation + Playwright Validation
============================================================

[Step 1] Generating BDD test via API...
✅ BDD test generated successfully
   Test ID: abc123
   Feature: Google Search Real Scenario
   Scenarios: 1
   Background: True

[Step 2] Validating generated feature file...
✅ Feature file exists: features/generated/generated_abc123.feature
✅ Feature file validation passed

[Step 3] Executing scenario with Playwright...
   🔹 Background: Navigating to Google...
   ✅ Background completed
   🔹 When I search for 'rain news today'...
   ✅ Search executed
   🔹 And I wait for results to load...
   ✅ Results loaded
   🔹 Then I should see search results...
   ✅ Search results visible
   🔹 And results should contain relevant titles...
   ✅ Found 5 result titles
   ✅ Results contain relevant titles

   Sample titles found:
      1. Little Rock Weather | News, Weather, Sports...
      2. NWS Forecast Office Little Rock, AR...
      3. Rainy start to the weekend in Arkansas...

   📸 Screenshot saved: screenshots/e2e_test_abc123.png

============================================================
✅ E2E TEST PASSED
============================================================

Test Summary:
  • API Generation: ✅ PASSED
  • Feature File Validation: ✅ PASSED
  • Playwright Execution: ✅ PASSED
  • Search Results: ✅ PASSED
  • Title Validation: ✅ PASSED

============================================================
🎉 ALL TESTS PASSED!
============================================================
```

## Test Scenarios

The test validates:
- ✅ API endpoint responds correctly
- ✅ YAML format is parsed
- ✅ Feature file is generated with correct structure
- ✅ Background section is included
- ✅ Tags are preserved
- ✅ Playwright can execute the scenario
- ✅ Google search works
- ✅ Results are visible
- ✅ Titles contain relevant keywords
- ✅ Screenshot is captured

## Troubleshooting

### API Connection Error
- Make sure Flask app is running: `python app.py`
- Check port 5001 is not in use

### Playwright Error
- Install browsers: `playwright install chromium`
- Check internet connection

### Search Results Not Found
- Google might show reCAPTCHA (use SerpAPI instead)
- Adjust timeout values in the test

## Files Generated

After running the test, you'll find:
- `features/generated/generated_*.feature` - Generated Gherkin file
- `screenshots/e2e_test_*.png` - Screenshot of search results

## Customizing the Test

Edit `test_e2e_bdd_api.py` to:
- Change search query
- Add more validation steps
- Test different scenarios
- Modify timeout values
- Add more assertions
