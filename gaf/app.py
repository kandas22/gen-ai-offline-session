"""
Flask API for Google Search Automation with BDD Testing
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flasgger import Swagger
import threading
import os
from typing import Dict, Any

from config import Config
from utils.logger import setup_logger
from utils.task_manager import task_manager, TaskStatus
from automation.google_search import perform_google_search
from bdd_engine.generator import generate_bdd_test
from bdd_engine.executor import execute_bdd_test
from bdd_engine.auto_fixer import auto_fix_test
from database.service import DatabaseService

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Swagger configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "GAF - Google Automation Framework API",
        "description": "Automated E2E testing with Playwright and BDD support",
        "version": "1.0.0",
        "contact": {
            "name": "API Support",
            "url": "https://github.com/your-repo"
        }
    },
    "host": "localhost:5001",
    "basePath": "/",
    "schemes": ["http", "https"],
    "tags": [
        {
            "name": "Health",
            "description": "Health check endpoints"
        },
        {
            "name": "BDD Tests",
            "description": "BDD test generation and execution"
        },
        {
            "name": "Playwright",
            "description": "Playwright test execution"
        },
        {
            "name": "Database",
            "description": "Test execution database queries"
        }
    ]
}

# Initialize Swagger
swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Setup logger
logger = setup_logger(__name__)

# Ensure directories exist
Config.ensure_directories()


@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint
    ---
    tags:
      - Health
    responses:
      200:
        description: API is healthy
        schema:
          type: object
          properties:
            status:
              type: string
              example: healthy
            service:
              type: string
              example: GAF Search Automation API
            version:
              type: string
              example: 1.0.0
    """
    return jsonify({
        'status': 'healthy',
        'service': 'GAF Search Automation API',
        'version': '1.0.0'
    }), 200


@app.route('/api/docs', methods=['GET'])
@app.route('/apidocs/', methods=['GET'])
@app.route('/swagger', methods=['GET'])
def api_docs():
    """Serve Swagger UI for API documentation"""
    swagger_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GAF API Documentation</title>
        <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
        <style>
            body { margin: 0; padding: 0; }
            .swagger-ui .topbar { background-color: #2c3e50; }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
        <script>
            window.onload = function() {
                const ui = SwaggerUIBundle({
                    url: "/apispec.json",
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIStandalonePreset
                    ],
                    plugins: [
                        SwaggerUIBundle.plugins.DownloadUrl
                    ],
                    layout: "StandaloneLayout"
                });
                window.ui = ui;
            };
        </script>
    </body>
    </html>
    """
    return swagger_html


@app.route('/openapi.yaml', methods=['GET'])
def openapi_spec():
    """Serve OpenAPI specification"""
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'openapi.yaml')


@app.route('/api/search/sync', methods=['POST'])
def search_sync():
    """
    Synchronous Google search endpoint
    
    Request body:
    {
        "query": "rain news today"  // optional
    }
    """
    try:
        data = request.get_json() or {}
        query = data.get('query')
        
        logger.info(f"Synchronous search request: {query}")
        
        # Perform search
        results = perform_google_search(query)
        
        return jsonify({
            'success': True,
            'data': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error in sync search: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/search', methods=['POST'])
def search_async():
    """
    Asynchronous Google search endpoint
    
    Request body:
    {
        "query": "rain news today"  // optional
    }
    
    Returns task_id for status checking
    """
    try:
        data = request.get_json() or {}
        query = data.get('query')
        
        logger.info(f"Async search request: {query}")
        
        # Create task
        task_id = task_manager.create_task('search', {'query': query})
        
        # Start search in background thread
        thread = threading.Thread(
            target=_perform_search_async,
            args=(task_id, query)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Search started'
        }), 202
        
    except Exception as e:
        logger.error(f"Error starting async search: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/search/status/<task_id>', methods=['GET'])
def get_search_status(task_id: str):
    """Get search task status"""
    try:
        task = task_manager.get_task(task_id)
        
        if not task:
            return jsonify({
                'success': False,
                'error': 'Task not found'
            }), 404
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'status': task['status'],
            'created_at': task['created_at'],
            'updated_at': task['updated_at']
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/search/results/<task_id>', methods=['GET'])
def get_search_results(task_id: str):
    """Get search task results"""
    try:
        task = task_manager.get_task(task_id)
        
        if not task:
            return jsonify({
                'success': False,
                'error': 'Task not found'
            }), 404
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'status': task['status'],
            'result': task.get('result'),
            'error': task.get('error')
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting task results: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/bdd/generate', methods=['POST'])
def generate_bdd():
    """
    Generate BDD test from specification
    
    Request body:
    {
        "specification": "Given I am on Google, When I search for rain news today, Then I should see news results"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'specification' not in data:
            return jsonify({
                'success': False,
                'error': 'specification is required'
            }), 400
        
        specification = data['specification']
        logger.info(f"Generating BDD test from specification")
        
        # Generate test
        result = generate_bdd_test(specification)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating BDD test: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/bdd/generate-and-execute', methods=['POST'])
def generate_and_execute_playwright():
    """Generate BDD test and execute with Playwright
    ---
    tags:
      - Playwright
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - specification
          properties:
            specification:
              type: object
              properties:
                feature:
                  type: object
                  properties:
                    name:
                      type: string
                      example: "Login Test"
                    description:
                      type: string
                      example: "Test user login functionality"
                    tags:
                      type: array
                      items:
                        type: string
                      example: ["@login", "@smoke"]
                scenarios:
                  type: array
                  items:
                    type: object
                configuration:
                  type: object
                  properties:
                    browser:
                      type: string
                      example: "chromium"
                    headless:
                      type: boolean
                      example: false
                    timeout:
                      type: integer
                      example: 60000
            async:
              type: boolean
              example: true
              description: "Run test asynchronously"
            execute_immediately:
              type: boolean
              example: true
    responses:
      200:
        description: Test executed successfully (synchronous)
        schema:
          type: object
          properties:
            success:
              type: boolean
            data:
              type: object
              properties:
                generation:
                  type: object
                execution:
                  type: object
      202:
        description: Test execution started (asynchronous)
        schema:
          type: object
          properties:
            success:
              type: boolean
            data:
              type: object
              properties:
                task_id:
                  type: string
                  example: "abc-123-def-456"
                message:
                  type: string
      400:
        description: Bad request
      500:
        description: Server error
    """
    try:
        data = request.get_json()
        
        if not data or 'specification' not in data:
            return jsonify({
                'success': False,
                'error': 'specification is required'
            }), 400
        
        specification = data['specification']
        execute_immediately = data.get('execute_immediately', True)
        run_async = data.get('async', False)
        
        logger.info(f"Generating and executing Playwright test (async={run_async})")
        
        # Generate BDD feature file first
        result = generate_bdd_test(specification)
        
        # Execute with Playwright if requested
        if execute_immediately:
            if run_async:
                # Run asynchronously - return task ID immediately
                task_id = task_manager.create_task('playwright_execute', {
                    'test_id': result['test_id'],
                    'specification': specification
                })
                
                thread = threading.Thread(
                    target=_execute_playwright_async,
                    args=(task_id, specification)
                )
                thread.daemon = True
                thread.start()
                
                return jsonify({
                    'success': True,
                    'data': {
                        'generation': result,
                        'task_id': task_id,
                        'message': 'Test execution started. Use /api/bdd/playwright/results/<task_id> to check status.'
                    }
                }), 202
            else:
                # Run synchronously (may timeout for long tests)
                from automation.playwright_executor import execute_amazon_test
                
                execution_result = execute_amazon_test(specification)
                
                return jsonify({
                    'success': True,
                    'data': {
                        'generation': result,
                        'execution': execution_result
                    }
                }), 200
        else:
            return jsonify({
                'success': True,
                'data': {
                    'generation': result,
                    'message': 'Test generated. Call /api/bdd/execute-playwright to run it.'
                }
            }), 200
        
    except Exception as e:
        logger.error(f"Error in generate-and-execute: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/bdd/execute-playwright', methods=['POST'])
def execute_playwright():
    """
    Execute Playwright test from specification
    
    Request body:
    {
        "specification": {
            "feature": {...},
            "scenarios": [...],
            "configuration": {...}
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'specification' not in data:
            return jsonify({
                'success': False,
                'error': 'specification is required'
            }), 400
        
        specification = data['specification']
        
        logger.info(f"Executing Playwright test")
        
        from automation.playwright_executor import execute_amazon_test
        
        execution_result = execute_amazon_test(specification)
        
        return jsonify({
            'success': True,
            'data': execution_result
        }), 200
        
    except Exception as e:
        logger.error(f"Error executing Playwright test: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/bdd/execute', methods=['POST'])
def execute_bdd():
    """
    Execute BDD test
    
    Request body:
    {
        "test_id": "abc123",
        "feature_file": "/path/to/feature.feature"  // optional if test_id is from generation
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'test_id' not in data:
            return jsonify({
                'success': False,
                'error': 'test_id is required'
            }), 400
        
        test_id = data['test_id']
        feature_file = data.get('feature_file')
        
        # If no feature file provided, construct from test_id
        if not feature_file:
            import os
            feature_file = os.path.join(
                Config.BDD_GENERATED_DIR,
                f'generated_{test_id}.feature'
            )
        
        logger.info(f"Executing BDD test: {test_id}")
        
        # Execute test in background
        task_id = task_manager.create_task('bdd_execute', {
            'test_id': test_id,
            'feature_file': feature_file
        })
        
        thread = threading.Thread(
            target=_execute_bdd_async,
            args=(task_id, test_id, feature_file)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'BDD test execution started'
        }), 202
        
    except Exception as e:
        logger.error(f"Error executing BDD test: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/bdd/results/<test_id>', methods=['GET'])
def get_bdd_results(test_id: str):
    """Get BDD test results"""
    try:
        from bdd_engine.executor import BDDExecutor
        
        executor = BDDExecutor()
        results = executor.get_results(test_id)
        
        if not results:
            return jsonify({
                'success': False,
                'error': 'Results not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting BDD results: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/bdd/auto-fix', methods=['POST'])
def auto_fix():
    """
    Auto-fix failed BDD test
    
    Request body:
    {
        "test_id": "abc123"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'test_id' not in data:
            return jsonify({
                'success': False,
                'error': 'test_id is required'
            }), 400
        
        test_id = data['test_id']
        logger.info(f"Auto-fixing test: {test_id}")
        
        # Get test results
        from bdd_engine.executor import BDDExecutor
        executor = BDDExecutor()
        results = executor.get_results(test_id)
        
        if not results:
            return jsonify({
                'success': False,
                'error': 'Test results not found'
            }), 404
        
        # Apply auto-fix
        fix_results = auto_fix_test(test_id, results)
        
        return jsonify({
            'success': True,
            'data': fix_results
        }), 200
        
    except Exception as e:
        logger.error(f"Error auto-fixing test: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Background task functions
def _perform_search_async(task_id: str, query: str):
    """Perform search in background"""
    try:
        task_manager.update_task_status(task_id, TaskStatus.RUNNING)
        
        results = perform_google_search(query)
        
        task_manager.update_task_status(
            task_id,
            TaskStatus.COMPLETED,
            result=results
        )
        
    except Exception as e:
        logger.error(f"Error in async search: {str(e)}")
        task_manager.update_task_status(
            task_id,
            TaskStatus.FAILED,
            error=str(e)
        )


def _execute_bdd_async(task_id: str, test_id: str, feature_file: str):
    """Execute BDD test in background"""
    try:
        task_manager.update_task_status(task_id, TaskStatus.RUNNING)
        
        results = execute_bdd_test(test_id, feature_file)
        
        task_manager.update_task_status(
            task_id,
            TaskStatus.COMPLETED,
            result=results
        )
        
    except Exception as e:
        logger.error(f"Error in async BDD execution: {str(e)}")
        task_manager.update_task_status(
            task_id,
            TaskStatus.FAILED,
            error=str(e)
        )


def _execute_playwright_async(task_id: str, specification: Dict[str, Any]):
    """Execute Playwright test in background"""
    try:
        # Update task status to running
        task_manager.update_task_status(task_id, TaskStatus.RUNNING)
        
        # Save to database - initial state
        feature = specification.get('feature', {})
        feature_name = feature.get('name', 'Unknown Test')
        test_id = task_id[:8]  # Use first 8 chars of task_id as test_id
        
        DatabaseService.save_test_execution(
            task_id=task_id,
            test_id=test_id,
            feature_name=feature_name,
            specification=specification,
            configuration=specification.get('configuration', {})
        )
        
        # Update database status to running
        DatabaseService.update_test_status(task_id, 'running')
        
        # Execute test
        from automation.playwright_executor import execute_amazon_test
        
        results = execute_amazon_test(specification)
        
        # Update task manager
        task_manager.update_task_status(
            task_id,
            TaskStatus.COMPLETED,
            result=results
        )
        
        # Save results to database
        DatabaseService.update_test_status(
            task_id,
            'completed',
            result=results
        )
        
    except Exception as e:
        logger.error(f"Error in async Playwright execution: {str(e)}")
        
        # Update task manager
        task_manager.update_task_status(
            task_id,
            TaskStatus.FAILED,
            error=str(e)
        )
        
        # Update database
        DatabaseService.update_test_status(
            task_id,
            'failed',
            error=str(e)
        )


@app.route('/api/bdd/playwright/results/<task_id>', methods=['GET'])
def get_playwright_results(task_id: str):
    """Get Playwright test results by task ID
    ---
    tags:
      - Playwright
    parameters:
      - name: task_id
        in: path
        type: string
        required: true
        description: Task ID returned from test execution
    responses:
      200:
        description: Test results
        schema:
          type: object
          properties:
            success:
              type: boolean
            task_id:
              type: string
            status:
              type: string
              enum: [pending, running, completed, failed]
            result:
              type: object
              properties:
                status:
                  type: string
                summary:
                  type: object
                  properties:
                    total:
                      type: integer
                    passed:
                      type: integer
                    failed:
                      type: integer
                    pass_rate:
                      type: string
                scenarios:
                  type: array
                  items:
                    type: object
            error:
              type: string
            created_at:
              type: string
            updated_at:
              type: string
      404:
        description: Task not found
      500:
        description: Server error
    """
    try:
        task = task_manager.get_task(task_id)
        
        if not task:
            return jsonify({
                'success': False,
                'error': 'Task not found'
            }), 404
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'status': task['status'],
            'result': task.get('result'),
            'error': task.get('error'),
            'created_at': task['created_at'],
            'updated_at': task['updated_at']
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting Playwright results: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/bdd/executions', methods=['GET'])
def get_all_executions():
    """Get all test executions from database
    ---
    tags:
      - Database
    parameters:
      - name: limit
        in: query
        type: integer
        default: 50
        description: Maximum number of executions to return
    responses:
      200:
        description: List of test executions
        schema:
          type: object
          properties:
            success:
              type: boolean
            count:
              type: integer
            executions:
              type: array
              items:
                type: object
                properties:
                  task_id:
                    type: string
                  test_id:
                    type: string
                  feature_name:
                    type: string
                  status:
                    type: string
                    enum: [pending, running, completed, failed]
                  response_code:
                    type: integer
                  response_status:
                    type: string
                  pass_rate:
                    type: string
                  total_scenarios:
                    type: integer
                  passed_scenarios:
                    type: integer
                  failed_scenarios:
                    type: integer
                  created_at:
                    type: string
                    format: date-time
                  end_time:
                    type: string
                    format: date-time
      500:
        description: Server error
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        executions = DatabaseService.get_all_test_executions(limit=limit)
        
        return jsonify({
            'success': True,
            'count': len(executions),
            'executions': executions
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting all executions: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/bdd/executions/<task_id>', methods=['GET'])
def get_execution_by_id(task_id: str):
    """Get specific test execution from database
    ---
    tags:
      - Database
    parameters:
      - name: task_id
        in: path
        type: string
        required: true
        description: Task ID of the test execution
    responses:
      200:
        description: Test execution details
        schema:
          type: object
          properties:
            success:
              type: boolean
            execution:
              type: object
              properties:
                task_id:
                  type: string
                test_id:
                  type: string
                feature_name:
                  type: string
                status:
                  type: string
                result:
                  type: object
                error:
                  type: string
                response_code:
                  type: integer
                response_status:
                  type: string
                created_at:
                  type: string
                updated_at:
                  type: string
      404:
        description: Execution not found
      500:
        description: Server error
    """
    try:
        execution = DatabaseService.get_test_execution(task_id)
        
        if not execution:
            return jsonify({
                'success': False,
                'error': 'Execution not found in database'
            }), 404
        
        return jsonify({
            'success': True,
            'execution': execution
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting execution: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    logger.info(f"Starting Flask API on {Config.HOST}:{Config.PORT}")
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
