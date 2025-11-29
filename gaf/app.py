"""
Flask API for Google Search Automation with BDD Testing
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
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

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Setup logger
logger = setup_logger(__name__)

# Ensure directories exist
Config.ensure_directories()


@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'GAF Search Automation API',
        'version': '1.0.0'
    }), 200


@app.route('/api/docs', methods=['GET'])
def api_docs():
    """Serve API documentation (Swagger UI)"""
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'api-docs.html')


@app.route('/swagger', methods=['GET'])
def swagger():
    """Serve API documentation (Swagger UI) - alias for /api/docs"""
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'api-docs.html')


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


if __name__ == '__main__':
    logger.info(f"Starting Flask API on {Config.HOST}:{Config.PORT}")
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
