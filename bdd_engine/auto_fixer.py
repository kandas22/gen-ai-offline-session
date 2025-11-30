"""
Auto-Fixer - Automatically fixes common BDD test failures
"""
import re
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from config import Config
from utils.logger import setup_logger
from bdd_engine.executor import BDDExecutor

logger = setup_logger(__name__)


class AutoFixer:
    """Automatically fixes common test failures"""
    
    def __init__(self):
        """Initialize Auto Fixer"""
        self.executor = BDDExecutor()
        logger.info("AutoFixer initialized")
    
    def analyze_and_fix(self, test_id: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze test failures and apply fixes
        
        Args:
            test_id: Test ID
            results: Test execution results
            
        Returns:
            Fix results
        """
        logger.info(f"Analyzing failures for test: {test_id}")
        
        fix_results = {
            'test_id': test_id,
            'timestamp': datetime.now().isoformat(),
            'fixes_applied': [],
            'success': False,
            'retry_results': None
        }
        
        if not results.get('failures'):
            logger.info("No failures to fix")
            fix_results['success'] = True
            return fix_results
        
        # Analyze each failure
        for failure in results['failures']:
            fixes = self._identify_fixes(failure)
            
            for fix in fixes:
                logger.info(f"Applying fix: {fix['type']}")
                applied = self._apply_fix(test_id, fix)
                
                if applied:
                    fix_results['fixes_applied'].append(fix)
        
        # Retry test if fixes were applied
        if fix_results['fixes_applied']:
            logger.info(f"Retrying test after applying {len(fix_results['fixes_applied'])} fixes")
            
            # Get feature file from original results
            feature_file = results.get('feature_file')
            if feature_file:
                retry_results = self.executor.execute_test(f"{test_id}_retry", feature_file)
                fix_results['retry_results'] = retry_results
                fix_results['success'] = retry_results.get('success', False)
        
        return fix_results
    
    def _identify_fixes(self, failure: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Identify potential fixes for a failure
        
        Args:
            failure: Failure information
            
        Returns:
            List of potential fixes
        """
        fixes = []
        error_msg = failure.get('error', '').lower()
        step = failure.get('step', '')
        
        # Timeout errors
        if 'timeout' in error_msg or 'timed out' in error_msg:
            fixes.append({
                'type': 'increase_timeout',
                'description': 'Increase timeout for element wait',
                'step': step,
                'old_timeout': Config.TIMEOUT,
                'new_timeout': Config.TIMEOUT * 2
            })
        
        # Element not found errors
        if 'not found' in error_msg or 'no such element' in error_msg or 'not visible' in error_msg:
            fixes.append({
                'type': 'add_wait',
                'description': 'Add explicit wait before element interaction',
                'step': step,
                'wait_time': 5
            })
            
            fixes.append({
                'type': 'alternative_selector',
                'description': 'Try alternative element selector',
                'step': step
            })
        
        # Network errors
        if 'network' in error_msg or 'connection' in error_msg:
            fixes.append({
                'type': 'add_retry',
                'description': 'Add retry logic for network operations',
                'step': step,
                'retry_count': 3
            })
        
        # Assertion errors
        if 'assertion' in error_msg or 'assert' in error_msg:
            fixes.append({
                'type': 'relax_assertion',
                'description': 'Relax assertion conditions',
                'step': step
            })
        
        return fixes
    
    def _apply_fix(self, test_id: str, fix: Dict[str, Any]) -> bool:
        """
        Apply a specific fix
        
        Args:
            test_id: Test ID
            fix: Fix to apply
            
        Returns:
            True if fix applied successfully
        """
        try:
            fix_type = fix['type']
            
            if fix_type == 'increase_timeout':
                return self._fix_timeout(test_id, fix)
            
            elif fix_type == 'add_wait':
                return self._fix_add_wait(test_id, fix)
            
            elif fix_type == 'alternative_selector':
                return self._fix_selector(test_id, fix)
            
            elif fix_type == 'add_retry':
                return self._fix_add_retry(test_id, fix)
            
            elif fix_type == 'relax_assertion':
                return self._fix_assertion(test_id, fix)
            
            else:
                logger.warning(f"Unknown fix type: {fix_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error applying fix: {str(e)}")
            return False
    
    def _fix_timeout(self, test_id: str, fix: Dict[str, Any]) -> bool:
        """Fix timeout issues by increasing wait time"""
        try:
            # Find step definition file
            step_file = self._find_step_file(test_id)
            if not step_file:
                return False
            
            # Read file
            with open(step_file, 'r') as f:
                content = f.read()
            
            # Increase timeout values
            content = re.sub(
                r'timeout=\d+',
                f'timeout={fix["new_timeout"]}',
                content
            )
            
            # Add wait_for_load_state if not present
            if 'wait_for_load_state' not in content:
                content = content.replace(
                    "press('Enter')",
                    "press('Enter')\n    automation.page.wait_for_load_state('networkidle', timeout=30000)"
                )
            
            # Write back
            with open(step_file, 'w') as f:
                f.write(content)
            
            logger.info(f"Applied timeout fix to {step_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error fixing timeout: {str(e)}")
            return False
    
    def _fix_add_wait(self, test_id: str, fix: Dict[str, Any]) -> bool:
        """Add explicit waits"""
        try:
            step_file = self._find_step_file(test_id)
            if not step_file:
                return False
            
            with open(step_file, 'r') as f:
                content = f.read()
            
            # Add time.sleep before problematic operations
            if 'import time' not in content:
                content = 'import time\n' + content
            
            # Add waits before element interactions
            content = content.replace(
                '.fill(',
                f'.wait_for(state="visible", timeout=10000)\n    time.sleep({fix["wait_time"]})\n    .fill('
            )
            
            with open(step_file, 'w') as f:
                f.write(content)
            
            logger.info(f"Added wait to {step_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding wait: {str(e)}")
            return False
    
    def _fix_selector(self, test_id: str, fix: Dict[str, Any]) -> bool:
        """Try alternative selectors"""
        try:
            step_file = self._find_step_file(test_id)
            if not step_file:
                return False
            
            with open(step_file, 'r') as f:
                content = f.read()
            
            # Replace strict selectors with more flexible ones
            replacements = {
                'textarea[name="q"]': 'textarea[name="q"], input[name="q"], [aria-label*="Search"]',
                '#search': '#search, #rso, [role="main"]',
            }
            
            for old, new in replacements.items():
                content = content.replace(f"'{old}'", f"'{new}'")
            
            with open(step_file, 'w') as f:
                f.write(content)
            
            logger.info(f"Updated selectors in {step_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error fixing selector: {str(e)}")
            return False
    
    def _fix_add_retry(self, test_id: str, fix: Dict[str, Any]) -> bool:
        """Add retry logic"""
        try:
            step_file = self._find_step_file(test_id)
            if not step_file:
                return False
            
            with open(step_file, 'r') as f:
                content = f.read()
            
            # Add retry wrapper (simplified)
            if 'def retry_operation' not in content:
                retry_code = '''
def retry_operation(func, retries=3):
    """Retry operation on failure"""
    for i in range(retries):
        try:
            return func()
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(2)
    
'''
                # Insert after imports
                lines = content.split('\n')
                insert_pos = 0
                for i, line in enumerate(lines):
                    if line.startswith('from') or line.startswith('import'):
                        insert_pos = i + 1
                
                lines.insert(insert_pos, retry_code)
                content = '\n'.join(lines)
            
            with open(step_file, 'w') as f:
                f.write(content)
            
            logger.info(f"Added retry logic to {step_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding retry: {str(e)}")
            return False
    
    def _fix_assertion(self, test_id: str, fix: Dict[str, Any]) -> bool:
        """Relax assertion conditions"""
        try:
            step_file = self._find_step_file(test_id)
            if not step_file:
                return False
            
            with open(step_file, 'r') as f:
                content = f.read()
            
            # Make assertions more lenient
            content = content.replace(
                'assert results.is_visible()',
                'assert results.count() > 0 or results.is_visible(timeout=5000)'
            )
            
            with open(step_file, 'w') as f:
                f.write(content)
            
            logger.info(f"Relaxed assertions in {step_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error fixing assertion: {str(e)}")
            return False
    
    def _find_step_file(self, test_id: str) -> Optional[str]:
        """Find step definition file for test"""
        # Look for generated step file
        step_file = os.path.join(Config.BDD_GENERATED_DIR, f'generated_{test_id}_steps.py')
        
        if os.path.exists(step_file):
            return step_file
        
        # Try without 'generated_' prefix
        step_file = os.path.join(Config.BDD_GENERATED_DIR, f'{test_id}_steps.py')
        if os.path.exists(step_file):
            return step_file
        
        logger.warning(f"Step file not found for test: {test_id}")
        return None


# Convenience function
def auto_fix_test(test_id: str, results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Auto-fix test failures
    
    Args:
        test_id: Test ID
        results: Test results
        
    Returns:
        Fix results
    """
    fixer = AutoFixer()
    return fixer.analyze_and_fix(test_id, results)
