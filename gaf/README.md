# Flask API - Google Search Automation with BDD Testing

A comprehensive Flask API that automates Google search using Playwright, with Gherkin BDD testing capabilities, auto-generation of tests from specifications, and intelligent auto-fix for test failures.

## Features

- 🔍 **Google Search Automation** - Automated search with Playwright
- 🧪 **Gherkin BDD Tests** - Behavior-driven development testing
- 🤖 **Auto-Generation** - Generate BDD tests from natural language specifications
- 🔧 **Auto-Fix** - Intelligent automatic fixing of common test failures
- 🔐 **2FA Support** - PyAutoGUI integration for 2FA bypass
- 📸 **Screenshots** - Automatic screenshot capture
- 🔄 **Async/Sync** - Both synchronous and asynchronous API endpoints

## Project Structure

```
gaf/
├── app.py                      # Main Flask application
├── config.py                   # Configuration management
├── requirement.txt             # Python dependencies
├── .env.example               # Example environment file
├── automation/                # Playwright automation
│   ├── google_search.py       # Google search automation
│   └── auth_handler.py        # 2FA authentication handler
├── bdd_engine/                # BDD auto-generation & auto-fix
│   ├── generator.py           # BDD test generator
│   ├── executor.py            # BDD test executor
│   └── auto_fixer.py          # Intelligent auto-fixer
├── features/                  # Gherkin feature files
│   ├── google_search.feature  # Google search scenarios
│   ├── environment.py         # Behave configuration
│   ├── steps/                 # Step definitions
│   └── generated/             # Auto-generated tests
├── utils/                     # Utilities
│   ├── logger.py              # Logging configuration
│   └── task_manager.py        # Task management
├── screenshots/               # Screenshot storage
├── results/                   # Test results
└── logs/                      # Application logs
```

## Installation

### 1. Clone or Navigate to Directory

```bash
cd /Users/kanda/Learning/GenAI/gen-ai-offline-session/gaf
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Mac/Linux
```

### 3. Install Dependencies

```bash
pip install -r requirement.txt
```

### 4. Install Playwright Browsers

```bash
python -m playwright install
```

### 5. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

## Configuration

Edit `.env` file with your settings:

```env
# Flask
DEBUG=True
PORT=5000

# Playwright
HEADLESS_MODE=True
BROWSER_TYPE=chromium

# Google Search
SEARCH_QUERY=rain news today

# 2FA (optional)
ENABLE_2FA=False
```

## Running the Application

### Start Flask API

```bash
python app.py
```

The API will be available at `http://localhost:5001`

### Run Gherkin Tests

```bash
behave features/
```

## API Endpoints

### Health Check
```bash
GET /
```

### Synchronous Search
```bash
POST /api/search/sync
Content-Type: application/json

{
  "query": "rain news today"
}
```

### Asynchronous Search
```bash
POST /api/search
Content-Type: application/json

{
  "query": "rain news today"
}

# Returns task_id for status checking
```

### Get Search Status
```bash
GET /api/search/status/<task_id>
```

### Get Search Results
```bash
GET /api/search/results/<task_id>
```

### Generate BDD Test
```bash
POST /api/bdd/generate
Content-Type: application/json

{
  "specification": "Given I am on Google, When I search for rain news today, Then I should see news results"
}
```

### Execute BDD Test
```bash
POST /api/bdd/execute
Content-Type: application/json

{
  "test_id": "generated_test_id"
}
```

### Get BDD Results
```bash
GET /api/bdd/results/<test_id>
```

### Auto-Fix Failed Test
```bash
POST /api/bdd/auto-fix
Content-Type: application/json

{
  "test_id": "failed_test_id"
}
```

## Usage Examples

### Example 1: Simple Search

```bash
curl -X POST http://localhost:5000/api/search/sync \
  -H "Content-Type: application/json" \
  -d '{"query": "rain news today"}'
```

### Example 2: Generate and Execute BDD Test

```bash
# Step 1: Generate test
curl -X POST http://localhost:5000/api/bdd/generate \
  -H "Content-Type: application/json" \
  -d '{"specification": "Given I am on Google, When I search for weather, Then I should see results"}'

# Step 2: Execute generated test (use test_id from step 1)
curl -X POST http://localhost:5000/api/bdd/execute \
  -H "Content-Type: application/json" \
  -d '{"test_id": "abc123"}'

# Step 3: Get results
curl http://localhost:5000/api/bdd/results/abc123
```

### Example 3: Auto-Fix Failed Test

```bash
# If test fails, auto-fix it
curl -X POST http://localhost:5000/api/bdd/auto-fix \
  -H "Content-Type: application/json" \
  -d '{"test_id": "failed_test_id"}'
```

## Integration with Lovable UI

This API is designed to be consumed by a frontend built with Lovable. Here are the key integration points:

### Frontend Integration

```javascript
// Search for news
const searchNews = async (query) => {
  const response = await fetch('http://localhost:5000/api/search/sync', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  });
  return await response.json();
};

// Generate BDD test
const generateTest = async (specification) => {
  const response = await fetch('http://localhost:5000/api/bdd/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ specification })
  });
  return await response.json();
};

// Execute test
const executeTest = async (testId) => {
  const response = await fetch('http://localhost:5000/api/bdd/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ test_id: testId })
  });
  return await response.json();
};
```

## Troubleshooting

### Playwright Installation Issues

```bash
# Reinstall Playwright
pip uninstall playwright
pip install playwright
python -m playwright install
```

### Port Already in Use

```bash
# Change port in .env
PORT=5001
```

### Browser Not Found

```bash
# Install specific browser
python -m playwright install chromium
```

## Development

### Running in Debug Mode

```bash
# Set in .env
DEBUG=True
HEADLESS_MODE=False  # See browser actions
```

### Viewing Logs

```bash
tail -f logs/app_*.log
```

## License

MIT

## Support

For issues or questions, please check the logs in the `logs/` directory or review screenshots in `screenshots/`.
