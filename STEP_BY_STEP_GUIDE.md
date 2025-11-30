# Step-by-Step Guide: Flask API with Playwright and Gherkin

This guide will walk you through setting up and using the Flask API for Google search automation with BDD testing.

## Table of Contents

1. [Initial Setup](#initial-setup)
2. [Running the API](#running-the-api)
3. [Testing with curl](#testing-with-curl)
4. [Running Gherkin Tests](#running-gherkin-tests)
5. [Auto-Generating BDD Tests](#auto-generating-bdd-tests)
6. [Auto-Fixing Failed Tests](#auto-fixing-failed-tests)
7. [Integration with Lovable UI](#integration-with-lovable-ui)

---

## Initial Setup

### Step 1: Navigate to Project Directory

```bash
cd /Users/kanda/Learning/GenAI/gen-ai-offline-session/gaf
```

### Step 2: Activate Virtual Environment

```bash
source .venv/bin/activate
```

If you don't have a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirement.txt
```

Expected output:
```
Successfully installed Flask-3.1.2 playwright-1.56.0 behave-1.2.6 ...
```

### Step 4: Install Playwright Browsers

```bash
python -m playwright install
```

This will download Chromium, Firefox, and WebKit browsers (~300MB).

### Step 5: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env (optional - defaults work fine)
nano .env
```

**Recommended settings for testing:**
```env
DEBUG=True
HEADLESS_MODE=False  # See browser in action
PORT=5000
SEARCH_QUERY=rain news today
```

---

## Running the API

### Step 1: Start Flask Server

```bash
python app.py
```

Expected output:
```
INFO - Starting Flask API on 0.0.0.0:5000
 * Running on http://0.0.0.0:5000
```

### Step 2: Verify Server is Running

Open another terminal and run:

```bash
curl http://localhost:5000/
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Google Search Automation API",
  "version": "1.0.0"
}
```

✅ **Success!** Your API is running.

---

## Testing with curl

### Test 1: Synchronous Search

```bash
curl -X POST http://localhost:5000/api/search/sync \
  -H "Content-Type: application/json" \
  -d '{"query": "rain news today"}'
```

**What happens:**
1. Browser launches (if HEADLESS_MODE=False)
2. Navigates to Google
3. Searches for "rain news today"
4. Extracts results
5. Takes screenshots
6. Returns JSON response

**Expected response:**
```json
{
  "success": true,
  "data": {
    "query": "rain news today",
    "success": true,
    "total_results": 10,
    "results": [
      {
        "title": "Latest Rain News...",
        "url": "https://...",
        "snippet": "...",
        "type": "news"
      }
    ],
    "screenshots": ["screenshots/google_homepage_20231129_123456.png"]
  }
}
```

### Test 2: Asynchronous Search

```bash
# Start search
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "weather forecast"}'
```

Response:
```json
{
  "success": true,
  "task_id": "abc-123-def-456",
  "message": "Search started"
}
```

**Check status:**
```bash
curl http://localhost:5000/api/search/status/abc-123-def-456
```

**Get results:**
```bash
curl http://localhost:5000/api/search/results/abc-123-def-456
```

---

## Running Gherkin Tests

### Step 1: Run All Tests

```bash
behave features/
```

**What happens:**
1. Behave reads `features/google_search.feature`
2. Executes step definitions from `features/steps/search_steps.py`
3. Launches browser for each scenario
4. Performs automated tests
5. Reports results

**Expected output:**
```
Feature: Google Search for Rain News

  Scenario: Search for rain news today
    Given I am on Google homepage ... passed
    When I search for "rain news today" ... passed
    Then I should see search results ... passed
    And the results should contain news articles ... passed

1 feature passed, 0 failed, 0 skipped
2 scenarios passed, 0 failed, 0 skipped
8 steps passed, 0 failed, 0 skipped
```

### Step 2: Run Specific Feature

```bash
behave features/google_search.feature
```

### Step 3: Run with Verbose Output

```bash
behave features/ --no-capture
```

---

## Auto-Generating BDD Tests

### Step 1: Generate Test from Specification

```bash
curl -X POST http://localhost:5000/api/bdd/generate \
  -H "Content-Type: application/json" \
  -d '{
    "specification": "Given I am on Google, When I search for python tutorials, Then I should see programming results"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "test_id": "a1b2c3d4",
    "feature_file": "features/generated/generated_a1b2c3d4.feature",
    "step_definitions": "features/generated/generated_a1b2c3d4_steps.py",
    "feature_name": "Python Tutorials"
  }
}
```

**What was created:**
1. ✅ Feature file: `features/generated/generated_a1b2c3d4.feature`
2. ✅ Step definitions: `features/generated/generated_a1b2c3d4_steps.py`

### Step 2: View Generated Files

```bash
# View feature file
cat features/generated/generated_a1b2c3d4.feature

# View step definitions
cat features/generated/generated_a1b2c3d4_steps.py
```

### Step 3: Execute Generated Test

```bash
curl -X POST http://localhost:5000/api/bdd/execute \
  -H "Content-Type: application/json" \
  -d '{"test_id": "a1b2c3d4"}'
```

**Response:**
```json
{
  "success": true,
  "task_id": "task-xyz-789",
  "message": "BDD test execution started"
}
```

### Step 4: Get Test Results

```bash
curl http://localhost:5000/api/bdd/results/a1b2c3d4
```

---

## Auto-Fixing Failed Tests

### Scenario: Test Fails Due to Timeout

**Step 1: Identify Failed Test**

```bash
curl http://localhost:5000/api/bdd/results/a1b2c3d4
```

Response shows failure:
```json
{
  "success": true,
  "data": {
    "test_id": "a1b2c3d4",
    "success": false,
    "failures": [
      {
        "scenario": "Execute Python Tutorials",
        "step": "When I search for python tutorials",
        "error": "TimeoutError: Timeout 30000ms exceeded"
      }
    ]
  }
}
```

**Step 2: Apply Auto-Fix**

```bash
curl -X POST http://localhost:5000/api/bdd/auto-fix \
  -H "Content-Type: application/json" \
  -d '{"test_id": "a1b2c3d4"}'
```

**What happens:**
1. 🔍 Analyzes failure (timeout detected)
2. 🔧 Applies fixes:
   - Increases timeout from 30s to 60s
   - Adds explicit waits
   - Updates selectors
3. 🔄 Retries test automatically
4. 📊 Returns results

**Response:**
```json
{
  "success": true,
  "data": {
    "test_id": "a1b2c3d4",
    "fixes_applied": [
      {
        "type": "increase_timeout",
        "description": "Increase timeout for element wait",
        "old_timeout": 30000,
        "new_timeout": 60000
      }
    ],
    "retry_results": {
      "success": true,
      "passed": 1,
      "failed": 0
    }
  }
}
```

✅ **Test now passes!**

---

## Integration with Lovable UI

### Frontend Setup

Your Lovable UI should make API calls to `http://localhost:5000`.

### Example: Search Component

```jsx
import { useState } from 'react';

function SearchComponent() {
  const [query, setQuery] = useState('rain news today');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/search/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      const data = await response.json();
      setResults(data.data);
    } catch (error) {
      console.error('Search failed:', error);
    }
    setLoading(false);
  };

  return (
    <div>
      <input 
        value={query} 
        onChange={(e) => setQuery(e.target.value)} 
      />
      <button onClick={handleSearch} disabled={loading}>
        {loading ? 'Searching...' : 'Search'}
      </button>
      
      {results && (
        <div>
          <h3>Results: {results.total_results}</h3>
          {results.results.map((result, i) => (
            <div key={i}>
              <h4>{result.title}</h4>
              <a href={result.url}>{result.url}</a>
              <p>{result.snippet}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

### Example: BDD Test Generator

```jsx
function BDDGenerator() {
  const [spec, setSpec] = useState('');
  const [testId, setTestId] = useState(null);

  const generateTest = async () => {
    const response = await fetch('http://localhost:5000/api/bdd/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ specification: spec })
    });
    const data = await response.json();
    setTestId(data.data.test_id);
  };

  const executeTest = async () => {
    await fetch('http://localhost:5000/api/bdd/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ test_id: testId })
    });
  };

  return (
    <div>
      <textarea 
        value={spec} 
        onChange={(e) => setSpec(e.target.value)}
        placeholder="Given I am on Google, When I search for..."
      />
      <button onClick={generateTest}>Generate Test</button>
      
      {testId && (
        <>
          <p>Test ID: {testId}</p>
          <button onClick={executeTest}>Execute Test</button>
        </>
      )}
    </div>
  );
}
```

---

## Common Issues & Solutions

### Issue 1: Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Change port in .env
PORT=5001

# Or kill existing process
lsof -ti:5000 | xargs kill -9
```

### Issue 2: Playwright Browser Not Found

**Error:** `Executable doesn't exist`

**Solution:**
```bash
python -m playwright install chromium
```

### Issue 3: Module Not Found

**Error:** `ModuleNotFoundError: No module named 'behave'`

**Solution:**
```bash
pip install -r requirement.txt
```

---

## Next Steps

1. ✅ **Test the API** - Run all curl examples
2. ✅ **Run Gherkin tests** - Execute `behave features/`
3. ✅ **Generate custom tests** - Try your own BDD specifications
4. ✅ **Build Lovable UI** - Integrate with your frontend
5. ✅ **Customize** - Modify search queries, add new features

---

## Quick Reference

```bash
# Start API
python app.py

# Run tests
behave features/

# Test search
curl -X POST http://localhost:5000/api/search/sync \
  -H "Content-Type: application/json" \
  -d '{"query": "rain news today"}'

# Generate BDD test
curl -X POST http://localhost:5000/api/bdd/generate \
  -H "Content-Type: application/json" \
  -d '{"specification": "Given..., When..., Then..."}'
```

---

**🎉 You're all set! Happy testing!**
