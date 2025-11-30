# GAF - Google Automation Framework

A powerful Flask-based API for automated E2E testing using Playwright with BDD (Behavior-Driven Development) support. Features real-time browser automation, async test execution, and Supabase integration for persistent test result storage.

## 🚀 Features

- **Real Browser Testing** - Automated E2E tests using Playwright (Chromium, Firefox, WebKit)
- **BDD Test Generation** - Generate Gherkin feature files from JSON specifications
- **Async Execution** - Non-blocking test execution with task-based result retrieval
- **Retry Logic** - Automatic retries with configurable attempts and delays
- **Response Code Capture** - HTTP status codes captured for every navigation
- **Supabase Integration** - Persistent storage of all test executions and results
- **Flexible Validation** - Multiple validation types (element_exists, element_visible, url_contains, text_content)
- **REST API** - Complete API for test management and execution

## 📋 Table of Contents

- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Test Specification Format](#test-specification-format)
- [Database Schema](#database-schema)
- [Examples](#examples)

## 🛠 Tech Stack

- **Backend**: Flask 3.0.0
- **Browser Automation**: Playwright 1.40.0
- **Database**: PostgreSQL (Supabase)
- **ORM**: SQLAlchemy 2.0.23
- **Template Engine**: Jinja2 3.1.2
- **Additional**: 
  - Flask-CORS for cross-origin requests
  - python-dotenv for environment management
  - psycopg2-binary for PostgreSQL connectivity

## 📦 Installation

### Prerequisites

- Python 3.8+
- PostgreSQL database (Supabase account)
- Node.js (for Playwright browsers)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd gaf
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install Playwright Browsers

```bash
playwright install chromium
```

### Step 5: Configure Environment Variables

Create a `.env` file in the project root:

```env
# Flask Configuration
FLASK_ENV=development
DEBUG=True

# Database (Supabase)
DATABASE_URL=postgresql://user:password@host:5432/database

# Google Search API (Optional)
GOOGLE_API_KEY=your_api_key
GOOGLE_CSE_ID=your_cse_id
```

### Step 6: Initialize Database

The database tables will be created automatically on first run. To manually initialize:

```python
from database.models import init_db
init_db()
```

### Step 7: Start the Server

```bash
python app.py
```

Server will start at `http://localhost:5001`

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `FLASK_ENV` | Environment (development/production) | No |
| `DEBUG` | Enable debug mode | No |
| `GOOGLE_API_KEY` | Google Search API key | No |
| `GOOGLE_CSE_ID` | Custom Search Engine ID | No |

### Test Configuration

Configure test behavior in your JSON specification:

```json
{
  "configuration": {
    "base_url": "https://example.com",
    "timeout": 60000,           // Default timeout in ms
    "browser": "chromium",      // chromium, firefox, webkit
    "headless": false           // Run in headless mode
  }
}
```

## 🎯 Usage

### Quick Start

1. **Create a test specification** (JSON file):

```json
{
  "specification": {
    "feature": {
      "name": "Login Test",
      "description": "Test user login functionality",
      "tags": ["@login", "@smoke"]
    },
    "scenarios": [
      {
        "scenario_id": "SC001",
        "scenario_name": "Successful login",
        "tags": ["@critical"],
        "given": [
          {
            "step": "User navigates to login page",
            "url": "https://example.com/login",
            "wait_until": "networkidle",
            "timeout": 60000,
            "retries": 2
          }
        ],
        "when": [
          {
            "step": "User enters credentials",
            "action": "fill",
            "element": {
              "locator": "#username",
              "locator_type": "css"
            },
            "value": "testuser"
          }
        ],
        "then": [
          {
            "step": "Dashboard should be visible",
            "validation_type": "element_exists",
            "element": {
              "locator": ".dashboard",
              "locator_type": "css"
            }
          }
        ]
      }
    ],
    "configuration": {
      "browser": "chromium",
      "headless": false,
      "timeout": 60000
    }
  },
  "async": true
}
```

2. **Execute the test**:

```bash
curl -X POST http://localhost:5001/api/bdd/generate-and-execute \
  -H "Content-Type: application/json" \
  -d @test_spec.json
```

3. **Get results**:

```bash
# Using task_id from response
curl http://localhost:5001/api/bdd/playwright/results/<task_id>

# Or from database
curl http://localhost:5001/api/bdd/executions/<task_id>
```

## 📡 API Endpoints

### Test Execution

#### Generate and Execute Test
```http
POST /api/bdd/generate-and-execute
Content-Type: application/json

{
  "specification": {...},
  "async": true  // Optional, default: false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "generation": {
      "test_id": "abc123",
      "feature_file": "features/generated/generated_abc123.feature"
    },
    "task_id": "task-uuid",
    "message": "Test execution started..."
  }
}
```

#### Execute Only (No Generation)
```http
POST /api/bdd/execute-playwright
Content-Type: application/json

{
  "specification": {...}
}
```

### Results Retrieval

#### Get Test Results (In-Memory)
```http
GET /api/bdd/playwright/results/<task_id>
```

#### Get All Executions (Database)
```http
GET /api/bdd/executions?limit=50
```

**Response:**
```json
{
  "success": true,
  "count": 10,
  "executions": [
    {
      "task_id": "...",
      "test_id": "...",
      "feature_name": "...",
      "status": "completed",
      "response_code": 200,
      "response_status": "OK",
      "pass_rate": "100.00%",
      "total_scenarios": 1,
      "passed_scenarios": 1,
      "failed_scenarios": 0,
      "created_at": "2025-11-30T10:00:00",
      "end_time": "2025-11-30T10:00:30"
    }
  ]
}
```

#### Get Specific Execution (Database)
```http
GET /api/bdd/executions/<task_id>
```

### Health Check
```http
GET /
```

## 📝 Test Specification Format

### Feature Structure

```json
{
  "feature": {
    "name": "Feature Name",
    "description": "Feature description",
    "tags": ["@tag1", "@tag2"]
  }
}
```

### Scenario Structure

```json
{
  "scenario_id": "SC001",
  "scenario_name": "Scenario description",
  "tags": ["@smoke"],
  "given": [...],   // Setup steps
  "when": [...],    // Action steps
  "then": [...]     // Validation steps
}
```

### Step Types

#### Given Steps (Setup)
```json
{
  "step": "User navigates to page",
  "url": "https://example.com",
  "wait_until": "networkidle",  // domcontentloaded, load, networkidle
  "timeout": 60000,
  "retries": 2
}
```

#### When Steps (Actions)
```json
{
  "step": "User clicks button",
  "action": "click",
  "element": {
    "locator": "#submit-btn",
    "locator_type": "css"
  }
}
```

#### Then Steps (Validations)
```json
{
  "step": "Element should be visible",
  "validation_type": "element_visible",
  "element": {
    "locator": ".success-message",
    "locator_type": "css"
  }
}
```

### Validation Types

| Type | Description | Example |
|------|-------------|---------|
| `element_exists` | Check if element exists | `{"validation_type": "element_exists", "element": {...}}` |
| `element_visible` | Check if element is visible | `{"validation_type": "element_visible", "element": {...}}` |
| `url_contains` | Check if URL contains text | `{"validation_type": "url_contains", "expected_text": "#section"}` |
| `text_content` | Validate text content | `{"validation_type": "text_content", "expected_text": "Success"}` |

## 🗄️ Database Schema

### test_executions Table

```sql
CREATE TABLE test_executions (
    task_id VARCHAR(100) PRIMARY KEY,
    test_id VARCHAR(100),
    feature_name VARCHAR(500),
    status VARCHAR(50),              -- pending, running, completed, failed
    specification JSON,
    configuration JSON,
    result JSON,
    error TEXT,
    total_scenarios INTEGER,
    passed_scenarios INTEGER,
    failed_scenarios INTEGER,
    pass_rate VARCHAR(20),
    response_code INTEGER,           -- HTTP status code
    response_status VARCHAR(20),     -- OK or ERROR
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    start_time TIMESTAMP,
    end_time TIMESTAMP
);
```

## 📚 Examples

### Example 1: Simple Page Load Test

```json
{
  "specification": {
    "feature": {
      "name": "Page Load Test",
      "description": "Verify page loads successfully"
    },
    "scenarios": [{
      "scenario_id": "SC001",
      "scenario_name": "Homepage loads",
      "given": [{
        "step": "Navigate to homepage",
        "url": "https://example.com",
        "timeout": 30000,
        "retries": 2
      }],
      "when": [],
      "then": [{
        "step": "Page body exists",
        "validation_type": "element_exists",
        "element": {
          "locator": "body",
          "locator_type": "css"
        }
      }]
    }],
    "configuration": {
      "browser": "chromium",
      "headless": false
    }
  },
  "async": true
}
```

### Example 2: Form Submission Test

```json
{
  "specification": {
    "feature": {
      "name": "Contact Form",
      "description": "Test contact form submission"
    },
    "scenarios": [{
      "scenario_id": "SC001",
      "scenario_name": "Submit contact form",
      "given": [{
        "step": "Navigate to contact page",
        "url": "https://example.com/contact"
      }],
      "when": [
        {
          "step": "Fill name field",
          "action": "fill",
          "element": {"locator": "#name", "locator_type": "css"},
          "value": "John Doe"
        },
        {
          "step": "Click submit",
          "action": "click",
          "element": {"locator": "#submit", "locator_type": "css"}
        }
      ],
      "then": [{
        "step": "Success message appears",
        "validation_type": "element_visible",
        "element": {"locator": ".success", "locator_type": "css"}
      }]
    }],
    "configuration": {
      "browser": "chromium",
      "headless": false
    }
  },
  "async": true
}
```

## 🔧 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   lsof -t -i:5001 | xargs kill -9
   ```

2. **Database connection failed**
   - Verify `DATABASE_URL` in `.env`
   - Check Supabase credentials
   - Ensure database is accessible

3. **Playwright browser not found**
   ```bash
   playwright install chromium
   ```

4. **Test timeout**
   - Increase `timeout` in configuration
   - Check `wait_until` strategy
   - Verify URL is accessible

## 📄 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

**Built with ❤️ using Flask and Playwright**
