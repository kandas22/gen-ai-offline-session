"""
Playwright Executor for Amazon E2E Tests
Executes JSON-based test specifications in real-time
"""
import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from utils.logger import setup_logger
from config import Config

logger = setup_logger(__name__)


class PlaywrightAmazonExecutor:
    """Execute Amazon test scenarios using Playwright"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.test_results = []
        
    async def initialize_browser(self, config: Dict[str, Any]):
        """Initialize Playwright browser"""
        try:
            playwright = await async_playwright().start()
            
            headless = config.get('headless', False)
            browser_type = config.get('browser', 'chromium')
            
            if browser_type == 'chromium':
                self.browser = await playwright.chromium.launch(headless=headless)
            elif browser_type == 'firefox':
                self.browser = await playwright.firefox.launch(headless=headless)
            elif browser_type == 'webkit':
                self.browser = await playwright.webkit.launch(headless=headless)
            else:
                self.browser = await playwright.chromium.launch(headless=headless)
                
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            
            # Set timeout
            timeout = config.get('timeout', 30000)
            self.page.set_default_timeout(timeout)
            
            logger.info(f"Browser initialized: {browser_type}, headless={headless}")
            
        except Exception as e:
            logger.error(f"Error initializing browser: {str(e)}")
            raise
            
    async def close_browser(self):
        """Close browser and cleanup"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")
            
    async def execute_step(self, step: Dict[str, Any], step_type: str) -> Dict[str, Any]:
        """Execute a single test step"""
        result = {
            'step': step.get('step', 'Unknown step'),
            'type': step_type,
            'status': 'pending',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Given steps
            if step_type == 'given':
                if 'url' in step:
                    url = step['url']
                    wait_until = step.get('wait_until', 'domcontentloaded')  # domcontentloaded, load, networkidle
                    timeout = step.get('timeout', 60000)  # 60 seconds default
                    max_retries = step.get('retries', 2)  # Default 2 retries
                    
                    last_error = None
                    response_code = None
                    
                    for attempt in range(max_retries):
                        try:
                            logger.info(f"Attempting to navigate to {url} (attempt {attempt + 1}/{max_retries})")
                            response = await self.page.goto(url, wait_until=wait_until, timeout=timeout)
                            
                            # Capture response code
                            if response:
                                response_code = response.status
                            
                            result['status'] = 'passed'
                            result['message'] = f"Navigated to {url} (attempt {attempt + 1})"
                            result['response_code'] = response_code
                            result['response_status'] = 'OK' if response_code and 200 <= response_code < 300 else 'ERROR'
                            break  # Success, exit retry loop
                        except Exception as e:
                            last_error = e
                            logger.warning(f"Navigation attempt {attempt + 1} failed: {str(e)}")
                            if attempt < max_retries - 1:
                                await asyncio.sleep(2)  # Wait 2 seconds before retry
                            else:
                                # All retries failed
                                result['status'] = 'failed'
                                result['error'] = str(last_error)
                                result['message'] = f"Failed to navigate to {url} after {max_retries} attempts: {str(last_error)}"
                                result['response_code'] = response_code
                                raise last_error  # Re-raise to stop scenario execution
                    
            # When steps
            elif step_type == 'when':
                action = step.get('action')
                
                if action == 'search':
                    element = step.get('element', {})
                    locator = element.get('locator')
                    search_term = step.get('search_term')
                    
                    if locator and search_term:
                        await self.page.fill(locator, search_term)
                        result['status'] = 'passed'
                        result['message'] = f"Entered '{search_term}' in search box"
                        
                elif action == 'click':
                    element = step.get('element', {})
                    locator = element.get('locator')
                    
                    if locator:
                        await self.page.click(locator)
                        result['status'] = 'passed'
                        result['message'] = f"Clicked element: {locator}"
                        
                elif action == 'navigate':
                    url = step.get('url')
                    if url:
                        await self.page.goto(url)
                        result['status'] = 'passed'
                        result['message'] = f"Navigated to {url}"
                        
            # Then steps (validations)
            elif step_type == 'then':
                validation_type = step.get('validation_type')
                
                if validation_type == 'element_visible':
                    element = step.get('element', {})
                    locator = element.get('locator')
                    
                    if locator:
                        is_visible = await self.page.is_visible(locator)
                        if is_visible:
                            result['status'] = 'passed'
                            result['message'] = f"Element {locator} is visible"
                        else:
                            result['status'] = 'failed'
                            result['message'] = f"Element {locator} is not visible"
                            
                elif validation_type == 'element_exists':
                    element = step.get('element', {})
                    locator = element.get('locator')
                    
                    if locator:
                        count = await self.page.locator(locator).count()
                        if count > 0:
                            result['status'] = 'passed'
                            result['message'] = f"Element {locator} exists (count: {count})"
                        else:
                            result['status'] = 'failed'
                            result['message'] = f"Element {locator} does not exist"
                            
                elif validation_type == 'cart_items_count':
                    expected = step.get('expected_result')
                    # Get cart count from page
                    cart_count_element = await self.page.locator('#nav-cart-count').text_content()
                    cart_count = int(cart_count_element) if cart_count_element else 0
                    
                    if expected == 'greater_than_0':
                        if cart_count > 0:
                            result['status'] = 'passed'
                            result['message'] = f"Cart count is {cart_count} (> 0)"
                        else:
                            result['status'] = 'failed'
                            result['message'] = f"Cart is empty (count: {cart_count})"
                    elif isinstance(expected, int):
                        if cart_count == expected:
                            result['status'] = 'passed'
                            result['message'] = f"Cart count matches expected: {cart_count}"
                        else:
                            result['status'] = 'failed'
                            result['message'] = f"Cart count {cart_count} != expected {expected}"
                            
                elif validation_type == 'text_content':
                    element = step.get('element', {})
                    locator = element.get('locator')
                    expected_text = step.get('expected_text')
                    
                    if locator and expected_text:
                        actual_text = await self.page.locator(locator).text_content()
                        if expected_text in actual_text:
                            result['status'] = 'passed'
                            result['message'] = f"Text matches: {expected_text}"
                        else:
                            result['status'] = 'failed'
                            result['message'] = f"Text mismatch. Expected: {expected_text}, Got: {actual_text}"
                            
                elif validation_type == 'url_contains':
                    expected_text = step.get('expected_text')
                    current_url = self.page.url
                    
                    if expected_text:
                        if expected_text in current_url:
                            result['status'] = 'passed'
                            result['message'] = f"URL contains '{expected_text}': {current_url}"
                        else:
                            result['status'] = 'failed'
                            result['message'] = f"URL does not contain '{expected_text}'. Current URL: {current_url}"
                            
                # If action is specified in then step (like navigate)
                if 'action' in step:
                    action = step['action']
                    if action == 'click':
                        element = step.get('element', {})
                        locator = element.get('locator')
                        if locator:
                            await self.page.click(locator)
                            result['status'] = 'passed'
                            result['message'] = f"Clicked element: {locator}"
                            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            result['message'] = f"Error executing step: {str(e)}"
            logger.error(f"Step execution error: {str(e)}")
            
        return result
        
    async def execute_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single scenario"""
        scenario_result = {
            'scenario_id': scenario.get('scenario_id'),
            'scenario_name': scenario.get('scenario_name'),
            'tags': scenario.get('tags', []),
            'status': 'pending',
            'steps': [],
            'start_time': datetime.now().isoformat()
        }
        
        try:
            # Execute Given steps
            for step in scenario.get('given', []):
                step_result = await self.execute_step(step, 'given')
                scenario_result['steps'].append(step_result)
                if step_result['status'] == 'failed':
                    scenario_result['status'] = 'failed'
                    return scenario_result
                    
            # Execute When steps
            for step in scenario.get('when', []):
                step_result = await self.execute_step(step, 'when')
                scenario_result['steps'].append(step_result)
                if step_result['status'] == 'failed':
                    scenario_result['status'] = 'failed'
                    return scenario_result
                    
            # Execute Then steps
            for step in scenario.get('then', []):
                step_result = await self.execute_step(step, 'then')
                scenario_result['steps'].append(step_result)
                if step_result['status'] == 'failed':
                    scenario_result['status'] = 'failed'
                    
            # Set overall scenario status
            if all(s['status'] == 'passed' for s in scenario_result['steps']):
                scenario_result['status'] = 'passed'
            elif scenario_result['status'] != 'failed':
                scenario_result['status'] = 'partial'
                
        except Exception as e:
            scenario_result['status'] = 'failed'
            scenario_result['error'] = str(e)
            logger.error(f"Scenario execution error: {str(e)}")
            
        scenario_result['end_time'] = datetime.now().isoformat()
        return scenario_result
        
    async def execute_specification(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Execute full test specification"""
        test_result = {
            'feature': spec.get('feature', {}),
            'configuration': spec.get('configuration', {}),
            'scenarios': [],
            'start_time': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        try:
            # Initialize browser
            config = spec.get('configuration', {})
            await self.initialize_browser(config)
            
            # Execute each scenario
            for scenario in spec.get('scenarios', []):
                scenario_result = await self.execute_scenario(scenario)
                test_result['scenarios'].append(scenario_result)
                
            # Determine overall status
            passed = sum(1 for s in test_result['scenarios'] if s['status'] == 'passed')
            failed = sum(1 for s in test_result['scenarios'] if s['status'] == 'failed')
            total = len(test_result['scenarios'])
            
            test_result['summary'] = {
                'total': total,
                'passed': passed,
                'failed': failed,
                'pass_rate': f"{(passed/total*100):.2f}%" if total > 0 else "0%"
            }
            
            if failed == 0:
                test_result['status'] = 'passed'
            elif passed == 0:
                test_result['status'] = 'failed'
            else:
                test_result['status'] = 'partial'
                
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['error'] = str(e)
            logger.error(f"Test execution error: {str(e)}")
            
        finally:
            await self.close_browser()
            
        test_result['end_time'] = datetime.now().isoformat()
        return test_result


def execute_amazon_test(specification: Dict[str, Any]) -> Dict[str, Any]:
    """Synchronous wrapper for executing Amazon tests"""
    executor = PlaywrightAmazonExecutor()
    return asyncio.run(executor.execute_specification(specification))
