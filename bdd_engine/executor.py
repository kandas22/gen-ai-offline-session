"""
BDD Test Executor - Executes generated BDD tests
"""
import os
import subprocess
import json
from typing import Dict, Any, Optional
from datetime import datetime
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class BDDExecutor:
    """Executes BDD tests and captures results"""
    
    def __init__(self):
        """Initialize BDD Executor"""
        Config.ensure_directories()
        logger.info("BDDExecutor initialized")
    
    def execute_test(self, test_id: str, feature_file: str) -> Dict[str, Any]:
        """
        Execute BDD test
        
        Args:
            test_id: Test ID
            feature_file: Path to feature file
            
        Returns:
            Test execution results
        """
        logger.info(f"Executing BDD test: {test_id}")
        
        results = {
            'test_id': test_id,
            'feature_file': feature_file,
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'output': '',
            'error': None,
            'failures': [],
            'passed': 0,
            'failed': 0,
            'skipped': 0
        }
        
        try:
            # Prepare behave command
            cmd = [
                'behave',
                feature_file,
                '--no-capture',
                '--format', 'json',
                '--outfile', os.path.join(Config.RESULTS_DIR, f'{test_id}_results.json')
            ]
            
            logger.info(f"Running command: {' '.join(cmd)}")
            
            # Execute behave
            process = subprocess.run(
                cmd,
                cwd=os.path.dirname(os.path.dirname(feature_file)),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            results['output'] = process.stdout
            results['return_code'] = process.returncode
            
            if process.returncode == 0:
                results['success'] = True
                logger.info(f"Test {test_id} passed successfully")
            else:
                results['error'] = process.stderr
                logger.warning(f"Test {test_id} failed with return code {process.returncode}")
            
            # Parse JSON results if available
            json_results_file = os.path.join(Config.RESULTS_DIR, f'{test_id}_results.json')
            if os.path.exists(json_results_file):
                with open(json_results_file, 'r') as f:
                    json_results = json.load(f)
                    results['detailed_results'] = json_results
                    results = self._parse_behave_results(results, json_results)
            
        except subprocess.TimeoutExpired:
            error_msg = f"Test execution timeout after 120 seconds"
            logger.error(error_msg)
            results['error'] = error_msg
            
        except Exception as e:
            error_msg = f"Error executing test: {str(e)}"
            logger.error(error_msg)
            results['error'] = error_msg
        
        # Save results
        self._save_results(test_id, results)
        
        return results
    
    def _parse_behave_results(self, results: Dict[str, Any], 
                             json_results: list) -> Dict[str, Any]:
        """
        Parse behave JSON results
        
        Args:
            results: Current results dictionary
            json_results: Behave JSON output
            
        Returns:
            Updated results dictionary
        """
        try:
            for feature in json_results:
                for scenario in feature.get('elements', []):
                    scenario_status = scenario.get('status', 'unknown')
                    
                    if scenario_status == 'passed':
                        results['passed'] += 1
                    elif scenario_status == 'failed':
                        results['failed'] += 1
                        
                        # Extract failure information
                        for step in scenario.get('steps', []):
                            if step.get('result', {}).get('status') == 'failed':
                                results['failures'].append({
                                    'scenario': scenario.get('name'),
                                    'step': step.get('name'),
                                    'error': step.get('result', {}).get('error_message', '')
                                })
                    elif scenario_status == 'skipped':
                        results['skipped'] += 1
            
        except Exception as e:
            logger.error(f"Error parsing behave results: {str(e)}")
        
        return results
    
    def _save_results(self, test_id: str, results: Dict[str, Any]):
        """
        Save test results to file
        
        Args:
            test_id: Test ID
            results: Results dictionary
        """
        try:
            results_file = os.path.join(Config.RESULTS_DIR, f'{test_id}_summary.json')
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results saved: {results_file}")
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
    
    def get_results(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Get test results by ID
        
        Args:
            test_id: Test ID
            
        Returns:
            Test results or None
        """
        try:
            results_file = os.path.join(Config.RESULTS_DIR, f'{test_id}_summary.json')
            if os.path.exists(results_file):
                with open(results_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading results: {str(e)}")
        
        return None


# Convenience function
def execute_bdd_test(test_id: str, feature_file: str) -> Dict[str, Any]:
    """
    Execute BDD test
    
    Args:
        test_id: Test ID
        feature_file: Feature file path
        
    Returns:
        Test results
    """
    executor = BDDExecutor()
    return executor.execute_test(test_id, feature_file)
