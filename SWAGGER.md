# Swagger API Documentation

## Access Swagger UI

### Option 1: Flasgger Built-in UI
```
http://localhost:5001/apidocs/
```

### Option 2: Custom Swagger UI
```
http://localhost:5001/api/docs
```

### Option 3: OpenAPI JSON Spec
```
http://localhost:5001/apispec.json
```

## Features

✅ **Interactive API Documentation**
- Try out endpoints directly from the browser
- View request/response schemas
- See example payloads

✅ **Auto-generated from Code**
- Swagger specs embedded in route docstrings
- Automatically updated when code changes

✅ **Organized by Tags**
- Health - Health check endpoints
- Playwright - Test execution endpoints
- BDD Tests - BDD generation endpoints
- Database - Database query endpoints

## Example: Using Swagger UI

1. **Open Swagger UI**
   ```
   http://localhost:5001/apidocs/
   ```

2. **Select an Endpoint**
   - Click on any endpoint (e.g., `/api/bdd/generate-and-execute`)

3. **Try it Out**
   - Click "Try it out" button
   - Fill in the request body
   - Click "Execute"

4. **View Response**
   - See the response code, headers, and body

## Adding Documentation to New Endpoints

Add Swagger documentation to any Flask route using docstrings:

```python
@app.route('/api/example', methods=['POST'])
def example_endpoint():
    """Example endpoint description
    ---
    tags:
      - Examples
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: "John Doe"
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            message:
              type: string
    """
    # Your code here
    pass
```

## Swagger Configuration

Located in `app.py`:

```python
swagger_config = {
    "specs_route": "/api/docs"  # Swagger UI route
}

swagger_template = {
    "info": {
        "title": "GAF - Google Automation Framework API",
        "version": "1.0.0"
    }
}
```

## Testing with Swagger

1. **Health Check**
   - GET `/`
   - Should return `{"status": "healthy"}`

2. **Execute Test**
   - POST `/api/bdd/generate-and-execute`
   - Paste your test JSON
   - Click Execute
   - Get task_id in response

3. **Check Results**
   - GET `/api/bdd/executions/{task_id}`
   - View test results

## Export API Spec

Download the OpenAPI specification:

```bash
curl http://localhost:5001/apispec.json > openapi.json
```

Use this with:
- Postman (import collection)
- Insomnia (import spec)
- API testing tools
- Code generators

## Benefits

✅ **Self-documenting** - Code is the documentation
✅ **Always up-to-date** - Generated from live code
✅ **Interactive** - Test endpoints in browser
✅ **Standardized** - OpenAPI 2.0 compliant
✅ **Shareable** - Export and share with team
