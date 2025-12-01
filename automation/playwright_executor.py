"""
Playwright Executor for Amazon E2E Tests
Executes JSON-based test specifications in real-time
"""
import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser, BrowserContext, Error as PlaywrightError
from utils.logger import setup_logger
from config import Config

logger = setup_logger(__name__)


class PlaywrightAmazonExecutor:
    """Execute Amazon test scenarios using Playwright"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.test_results = []
        self.browser_crashed = False
        
    async def initialize_browser(self, config: Dict[str, Any]):
        """Initialize Playwright browser"""
        try:
            # Start playwright with timeout
            logger.info("Starting Playwright...")
            try:
                self.playwright = await asyncio.wait_for(
                    async_playwright().start(),
                    timeout=30.0
                )
                logger.info("✓ Playwright started successfully")
            except Exception as e:
                logger.error(f"Failed to start Playwright: {str(e)}")
                raise
            
            headless = config.get('headless', False)
            browser_type = config.get('browser', 'chromium')
            
            # Check if display is available for headed mode
            import platform
            if not headless and platform.system() != 'Windows':
                import os
                if not os.environ.get('DISPLAY'):
                    logger.warning("No DISPLAY environment variable - forcing headless mode")
                    headless = True
            
            logger.info(f"Launching {browser_type} browser (headless={headless})...")
            if browser_type == 'chromium':
                # Add args for stability in Docker/Server environments (Linux)
                import platform
                launch_args = []
                
                if platform.system() == 'Linux':
                    launch_args = [
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-setuid-sandbox',
                        '--no-zygote'
                    ]
                
                # Add stability args for all platforms  
                # Note: Be conservative with args to avoid browser instability
                launch_args.extend([
                    '--disable-blink-features=AutomationControlled'
                ])
                
                self.browser = await self.playwright.chromium.launch(
                    headless=headless,
                    args=launch_args
                )
            elif browser_type == 'firefox':
                self.browser = await self.playwright.firefox.launch(headless=headless)
            elif browser_type == 'webkit':
                self.browser = await self.playwright.webkit.launch(headless=headless)
            else:
                self.browser = await self.playwright.chromium.launch(headless=headless)
            
            # Verify browser launched successfully
            if not self.browser:
                raise Exception("Browser failed to launch - returned None")
            
            if not self.browser.is_connected():
                raise Exception("Browser launched but is not connected")
            
            logger.info("✓ Browser launched successfully")
            
            # Create context with stable options
            context_options = {
                'viewport': {'width': 1280, 'height': 720},
                'ignore_https_errors': True,
                'java_script_enabled': True,
            }
            logger.info("Creating browser context...")
            try:
                self.context = await self.browser.new_context(**context_options)
            except Exception as e:
                logger.error(f"Failed to create context: {str(e)}")
                raise Exception(f"Failed to create browser context: {str(e)}")
            
            logger.info("Creating new page...")
            max_page_retries = 3
            page_created = False
            last_page_error = None
            
            for attempt in range(max_page_retries):
                try:
                    self.page = await self.context.new_page()
                    
                    # Wait a bit longer for page to stabilize
                    await asyncio.sleep(1.0)
                    
                    # Check if page is still alive
                    if self.page.is_closed():
                        raise Exception("Page closed immediately after creation")
                    
                    # Set up page event listeners
                    def on_crash():
                        self.browser_crashed = True
                        logger.error('⚠️  Page crashed!')
                    
                    def on_close():
                        if not self.browser_crashed:
                            logger.warning('⚠️  Page closed unexpectedly')
                    
                    self.page.on('crash', on_crash)
                    self.page.on('close', on_close)
                    
                    # Set timeout
                    timeout = config.get('timeout', 30000)
                    self.page.set_default_timeout(timeout)
                    
                    # Final check
                    if not self.page.is_closed():
                        page_created = True
                        logger.info(f"✓ Page created successfully (attempt {attempt + 1})")
                        break
                    else:
                        raise Exception("Page closed after initialization")
                        
                except Exception as e:
                    last_page_error = e
                    logger.warning(f"Page creation attempt {attempt + 1}/{max_page_retries} failed: {str(e)}")
                    
                    # Clean up failed page
                    if self.page:
                        try:
                            await self.page.close()
                        except:
                            pass
                        self.page = None
                    
                    if attempt < max_page_retries - 1:
                        # Wait before retry, increasing delay
                        wait_time = (attempt + 1) * 1.0
                        logger.info(f"Waiting {wait_time}s before retry...")
                        await asyncio.sleep(wait_time)
                        
                        # If not headless and failing, try switching to headless
                        if not headless and attempt == 1:
                            logger.warning("Switching to headless mode due to repeated failures...")
                            headless = True
                            
                            # Recreate browser in headless mode
                            try:
                                await self.browser.close()
                            except:
                                pass
                            
                            if browser_type == 'chromium':
                                launch_args = ['--disable-blink-features=AutomationControlled']
                                self.browser = await self.playwright.chromium.launch(
                                    headless=True,
                                    args=launch_args
                                )
                            else:
                                self.browser = await self.playwright.chromium.launch(headless=True)
                            
                            logger.info("✓ Browser relaunched in headless mode")
                            
                            # Recreate context
                            self.context = await self.browser.new_context(**context_options)
                            logger.info("✓ Context recreated")
            
            if not page_created:
                raise Exception(f"Failed to create page after {max_page_retries} attempts: {str(last_page_error)}")
            
            logger.info(f"Browser initialized successfully: {browser_type}, headless={headless}")
            
        except asyncio.TimeoutError:
            error_msg = "Browser initialization timed out after 30 seconds"
            logger.error(error_msg)
            try:
                await self.close_browser()  # Cleanup any partial initialization
            except:
                pass  # Ignore cleanup errors during failed init
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Error initializing browser: {str(e)}")
            logger.error(f"Browser state at error: browser={self.browser is not None}, context={self.context is not None}, page={self.page is not None}")
            try:
                await self.close_browser()  # Cleanup any partial initialization
            except Exception as cleanup_error:
                logger.debug(f"Error during cleanup: {str(cleanup_error)}")
            raise
    
    def _check_browser_state(self) -> tuple[bool, str]:
        """Check if browser is in a valid state for operations"""
        if self.browser_crashed:
            return False, "Browser has crashed"
        if not self.browser:
            return False, "Browser not initialized"
        if not self.browser.is_connected():
            return False, "Browser disconnected"
        if not self.page:
            return False, "Page not initialized"
        if self.page.is_closed():
            return False, "Page is closed"
        return True, "OK"
            
    async def close_browser(self):
        """Close browser and cleanup"""
        try:
            # Close page if it exists and is not closed
            if self.page:
                try:
                    if not self.page.is_closed():
                        await self.page.close()
                except Exception as e:
                    logger.debug(f"Page already closed or error closing: {str(e)}")
            
            # Close context if it exists
            if self.context:
                try:
                    await self.context.close()
                except Exception as e:
                    logger.debug(f"Context already closed or error closing: {str(e)}")
            
            # Close browser if it exists and is connected
            if self.browser:
                try:
                    if self.browser.is_connected():
                        await self.browser.close()
                except Exception as e:
                    logger.debug(f"Browser already closed or error closing: {str(e)}")
            
            # Stop playwright
            if self.playwright:
                try:
                    await self.playwright.stop()
                except Exception as e:
                    logger.debug(f"Playwright already stopped or error stopping: {str(e)}")
            
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error during browser cleanup: {str(e)}")
            
    async def execute_step(self, step: Dict[str, Any], step_type: str) -> Dict[str, Any]:
        """Execute a single test step"""
        result = {
            'step': step.get('step', 'Unknown step'),
            'type': step_type,
            'status': 'pending',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Check if browser/page is still available
            is_valid, error_msg = self._check_browser_state()
            if not is_valid:
                raise Exception(f"Cannot execute step: {error_msg}")
            
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
                            # Check browser is still connected before navigation
                            if not self.browser or not self.browser.is_connected():
                                raise Exception("Browser disconnected before navigation")
                            if not self.page or self.page.is_closed():
                                raise Exception("Page closed before navigation")
                            
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
                        except PlaywrightError as e:
                            last_error = e
                            error_msg = str(e)
                            if "Target closed" in error_msg or "browser has been closed" in error_msg:
                                logger.error(f"Browser/page closed during navigation: {error_msg}")
                                result['status'] = 'failed'
                                result['error'] = 'Browser closed during navigation'
                                result['message'] = 'The browser or page was closed unexpectedly during navigation. This may indicate a crash or external closure.'
                                raise  # Don't retry on browser close
                            logger.warning(f"Navigation attempt {attempt + 1} failed: {error_msg}")
                            if attempt < max_retries - 1:
                                await asyncio.sleep(2)  # Wait 2 seconds before retry
                            else:
                                result['status'] = 'failed'
                                result['error'] = str(last_error)
                                result['message'] = f"Failed to navigate to {url} after {max_retries} attempts: {str(last_error)}"
                                result['response_code'] = response_code
                                raise last_error
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
                            
        except PlaywrightError as e:
            error_msg = str(e)
            if "Target closed" in error_msg or "browser has been closed" in error_msg:
                result['status'] = 'failed'
                result['error'] = "Browser or page was closed unexpectedly"
                result['message'] = "Browser connection lost - the page, context, or browser was closed during execution"
                logger.error(f"❌ Browser closed error: {error_msg}")
                logger.error(f"Browser state: crashed={self.browser_crashed}, connected={self.browser.is_connected() if self.browser else False}")
                if self.browser_crashed:
                    result['message'] += " (Browser crashed - this may be due to memory issues, page complexity, or browser bugs)"
            else:
                result['status'] = 'failed'
                result['error'] = error_msg
                result['message'] = f"Playwright error: {error_msg}"
                logger.error(f"Playwright error: {error_msg}")
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
            # Check if browser is still connected before starting
            if not self.browser or not self.browser.is_connected():
                scenario_result['status'] = 'failed'
                scenario_result['error'] = 'Browser connection lost before scenario execution'
                return scenario_result
            
            # Execute Given steps
            for step in scenario.get('given', []):
                step_result = await self.execute_step(step, 'given')
                scenario_result['steps'].append(step_result)
                if step_result['status'] == 'failed':
                    scenario_result['status'] = 'failed'
                    # Check if it's a browser closed error
                    if 'Browser' in step_result.get('error', '') and 'closed' in step_result.get('error', ''):
                        scenario_result['error'] = 'Browser closed during execution'
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
                
        except PlaywrightError as e:
            scenario_result['status'] = 'failed'
            error_msg = str(e)
            if "Target closed" in error_msg or "browser has been closed" in error_msg:
                scenario_result['error'] = 'Browser or page closed unexpectedly during scenario execution'
            else:
                scenario_result['error'] = f"Playwright error: {error_msg}"
            logger.error(f"Scenario execution error: {error_msg}")
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
                
        except PlaywrightError as e:
            test_result['status'] = 'failed'
            error_msg = str(e)
            if "Target closed" in error_msg or "browser has been closed" in error_msg:
                test_result['error'] = 'Browser or page closed unexpectedly during test execution'
            else:
                test_result['error'] = f"Playwright error: {error_msg}"
            logger.error(f"Test execution error: {error_msg}")
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
    
    # Check if there's already a running event loop
    try:
        loop = asyncio.get_running_loop()
        logger.info("Event loop already running, creating new loop in thread")
        # If we're already in an event loop, create a new one
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            result = new_loop.run_until_complete(executor.execute_specification(specification))
            return result
        finally:
            new_loop.close()
            # Restore the original loop
            asyncio.set_event_loop(loop)
    except RuntimeError:
        # No event loop running, safe to use asyncio.run()
        logger.info("No existing event loop, using asyncio.run()")
        return asyncio.run(executor.execute_specification(specification))
