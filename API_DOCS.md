# API Documentation

## Overview

Your Flask API now includes comprehensive OpenAPI 3.0 (Swagger) documentation.

## Accessing the Documentation

### Interactive Swagger UI
Open in your browser:
```
http://localhost:5001/api/docs
```

This provides:
- ✅ Interactive API explorer
- ✅ Try-it-out functionality for all endpoints
- ✅ Request/response examples
- ✅ Schema definitions

### OpenAPI Specification
Download the spec:
```
http://localhost:5001/openapi.yaml
```

## API Endpoints Summary

### Health
- `GET /` - Health check

### Search Operations
- `POST /api/search/sync` - Synchronous search (immediate results)
- `POST /api/search` - Asynchronous search (returns task_id)
- `GET /api/search/status/{task_id}` - Check task status
- `GET /api/search/results/{task_id}` - Get task results

### BDD Testing
- `POST /api/bdd/generate` - Generate BDD test from specification
- `POST /api/bdd/execute` - Execute BDD test
- `GET /api/bdd/results/{test_id}` - Get test results
- `POST /api/bdd/auto-fix` - Auto-fix failed test

## Quick Examples

### Synchronous Search
```bash
curl -X POST http://localhost:5001/api/search/sync \
  -H "Content-Type: application/json" \
  -d '{"query": "rain news today"}'
```

### Asynchronous Search
```bash
# Start search
curl -X POST http://localhost:5001/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "weather forecast"}'

# Response: {"success": true, "task_id": "abc123", "message": "Search started"}

# Check status
curl http://localhost:5001/api/search/status/abc123

# Get results
curl http://localhost:5001/api/search/results/abc123
```

### Generate BDD Test
```bash
curl -X POST http://localhost:5001/api/bdd/generate \
  -H "Content-Type: application/json" \
  -d '{"specification": "Given I am on Google, When I search for rain news, Then I should see results"}'
```

## Files Created

- [`openapi.yaml`](file:///Users/kanda/Learning/GenAI/gen-ai-offline-session/gaf/openapi.yaml) - OpenAPI 3.0 specification
- [`api-docs.html`](file:///Users/kanda/Learning/GenAI/gen-ai-offline-session/gaf/api-docs.html) - Swagger UI page
- Updated [`app.py`](file:///Users/kanda/Learning/GenAI/gen-ai-offline-session/gaf/app.py) - Added documentation routes

## Using the Documentation

1. **Start the Flask app:**
   ```bash
   python app.py
   ```

2. **Open Swagger UI:**
   ```
   http://localhost:5001/api/docs
   ```

3. **Try the endpoints:**
   - Click on any endpoint
   - Click "Try it out"
   - Fill in parameters
   - Click "Execute"
   - View the response

## Integration

Import the OpenAPI spec into:
- Postman (File → Import → openapi.yaml)
- Insomnia
- API testing tools
- Code generators (OpenAPI Generator, Swagger Codegen)
