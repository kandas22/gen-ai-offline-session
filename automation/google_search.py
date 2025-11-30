"""
Google search automation using Playwright
"""
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext
from config import Config
from utils.logger import setup_logger
from automation.auth_handler import AuthHandler

logger = setup_logger(__name__)


class GoogleSearchAutomation:
    """Automates Google search using Playwright"""
    
    def __init__(self):
        """Initialize Google Search Automation"""
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.auth_handler = AuthHandler()
        Config.ensure_directories()
        logger.info("GoogleSearchAutomation initialized")
    
    def start_browser(self):
        """Start Playwright browser with anti-detection features"""
        try:
            logger.info(f"Starting {Config.BROWSER_TYPE} browser (headless={Config.HEADLESS_MODE})")
            self.playwright = sync_playwright().start()
            
            # Browser launch arguments to avoid detection
            launch_args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-infobars',
                '--window-position=0,0',
                '--ignore-certifcate-errors',
                '--ignore-certifcate-errors-spki-list',
                '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
            
            # Select browser type
            if Config.BROWSER_TYPE == 'firefox':
                self.browser = self.playwright.firefox.launch(
                    headless=Config.HEADLESS_MODE,
                    slow_mo=Config.SLOW_MO,
                    args=launch_args
                )
            elif Config.BROWSER_TYPE == 'webkit':
                self.browser = self.playwright.webkit.launch(
                    headless=Config.HEADLESS_MODE,
                    slow_mo=Config.SLOW_MO,
                    args=launch_args
                )
            else:  # chromium (default)
                self.browser = self.playwright.chromium.launch(
                    headless=Config.HEADLESS_MODE,
                    slow_mo=Config.SLOW_MO,
                    args=launch_args
                )
            
            # Create context with realistic settings
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York',
                permissions=['geolocation'],
                geolocation={'latitude': 40.7128, 'longitude': -74.0060},
                color_scheme='light',
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1'
                }
            )
            
            self.page = self.context.new_page()
            self.page.set_default_timeout(Config.TIMEOUT)
            
            # Remove webdriver property to avoid detection
            self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Override the navigator.plugins to avoid detection
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // Override the navigator.languages to avoid detection
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                
                // Override the chrome property
                window.chrome = {
                    runtime: {}
                };
                
                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
            
            logger.info("Browser started successfully with anti-detection features")
            
        except Exception as e:
            logger.error(f"Error starting browser: {str(e)}")
            raise
    
    def stop_browser(self):
        """Stop Playwright browser"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("Browser stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping browser: {str(e)}")
    
    def take_screenshot(self, name: str = "screenshot") -> str:
        """
        Take screenshot of current page
        
        Args:
            name: Screenshot name
            
        Returns:
            Screenshot file path
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"
            filepath = os.path.join(Config.SCREENSHOTS_DIR, filename)
            
            self.page.screenshot(path=filepath, full_page=True)
            logger.info(f"Screenshot saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            return ""
    
    def search_google(self, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform Google search
        
        Args:
            query: Search query (uses config default if not provided)
            
        Returns:
            Search results dictionary
        """
        import random
        
        query = query or Config.SEARCH_QUERY
        results = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'results': [],
            'screenshots': [],
            'error': None
        }
        
        try:
            # Start browser if not already started
            if not self.page:
                self.start_browser()
            
            logger.info(f"Navigating to Google: {Config.GOOGLE_URL}")
            self.page.goto(Config.GOOGLE_URL, wait_until='domcontentloaded')
            
            # Random delay to mimic human behavior
            time.sleep(random.uniform(1.5, 3.0))
            
            # Take screenshot of Google homepage
            screenshot1 = self.take_screenshot("google_homepage")
            results['screenshots'].append(screenshot1)
            
            # Handle authentication if enabled
            if Config.ENABLE_2FA:
                logger.info("2FA enabled, checking for login")
                self.auth_handler.handle_google_login(self.page)
            
            # Wait for search box and enter query with human-like typing
            logger.info(f"Searching for: {query}")
            search_box = self.page.locator('textarea[name="q"], input[name="q"]').first
            search_box.wait_for(state='visible', timeout=10000)
            
            # Click on search box first (human-like behavior)
            search_box.click()
            time.sleep(random.uniform(0.3, 0.7))
            
            # Type with random delays between characters
            for char in query:
                search_box.type(char, delay=random.randint(50, 150))
            
            # Random delay before pressing Enter
            time.sleep(random.uniform(0.5, 1.2))
            search_box.press('Enter')
            
            # Wait for results to load
            logger.info("Waiting for search results...")
            self.page.wait_for_load_state('networkidle', timeout=15000)
            time.sleep(random.uniform(2.0, 3.5))  # Random wait for dynamic content
            
            # Take screenshot of search results
            screenshot2 = self.take_screenshot("search_results")
            results['screenshots'].append(screenshot2)
            
            # Extract search results
            logger.info("Extracting search results...")
            search_results = self.extract_search_results()
            results['results'] = search_results
            results['success'] = True
            results['total_results'] = len(search_results)
            
            logger.info(f"Search completed successfully. Found {len(search_results)} results")
            
        except Exception as e:
            error_msg = f"Error during Google search: {str(e)}"
            logger.error(error_msg)
            results['error'] = error_msg
            
            # Take error screenshot
            try:
                error_screenshot = self.take_screenshot("error")
                results['screenshots'].append(error_screenshot)
            except:
                pass
        
        finally:
            # Stop browser
            self.stop_browser()
        
        return results
    
    def extract_search_results(self) -> List[Dict[str, str]]:
        """
        Extract search results from Google results page
        
        Returns:
            List of search results
        """
        results = []
        
        try:
            # Wait for search results container
            self.page.wait_for_selector('#search, #rso', timeout=10000)
            
            # Extract news results (if present)
            news_items = self.page.locator('div[data-hveid] article, div.SoaBEf, div.dbsr').all()
            
            if news_items:
                logger.info(f"Found {len(news_items)} news items")
                for item in news_items[:10]:  # Limit to top 10
                    try:
                        result = self._extract_news_item(item)
                        if result:
                            results.append(result)
                    except Exception as e:
                        logger.debug(f"Error extracting news item: {str(e)}")
                        continue
            
            # Extract regular search results if no news found
            if not results:
                logger.info("No news items found, extracting regular search results")
                search_items = self.page.locator('div.g, div[data-sokoban-container]').all()
                
                for item in search_items[:10]:  # Limit to top 10
                    try:
                        result = self._extract_search_item(item)
                        if result:
                            results.append(result)
                    except Exception as e:
                        logger.debug(f"Error extracting search item: {str(e)}")
                        continue
            
            logger.info(f"Extracted {len(results)} total results")
            
        except Exception as e:
            logger.error(f"Error extracting search results: {str(e)}")
        
        return results
    
    def _extract_news_item(self, item) -> Optional[Dict[str, str]]:
        """Extract data from news item"""
        try:
            title_elem = item.locator('div[role="heading"], h3, h4').first
            link_elem = item.locator('a').first
            snippet_elem = item.locator('div.GI74Re, div.Y3v8qd').first
            
            title = title_elem.inner_text() if title_elem.count() > 0 else ""
            url = link_elem.get_attribute('href') if link_elem.count() > 0 else ""
            snippet = snippet_elem.inner_text() if snippet_elem.count() > 0 else ""
            
            if title and url:
                return {
                    'title': title.strip(),
                    'url': url,
                    'snippet': snippet.strip(),
                    'type': 'news'
                }
        except Exception as e:
            logger.debug(f"Error in _extract_news_item: {str(e)}")
        
        return None
    
    def _extract_search_item(self, item) -> Optional[Dict[str, str]]:
        """Extract data from regular search item"""
        try:
            title_elem = item.locator('h3').first
            link_elem = item.locator('a').first
            snippet_elem = item.locator('div.VwiC3b, span.aCOpRe').first
            
            title = title_elem.inner_text() if title_elem.count() > 0 else ""
            url = link_elem.get_attribute('href') if link_elem.count() > 0 else ""
            snippet = snippet_elem.inner_text() if snippet_elem.count() > 0 else ""
            
            if title and url:
                return {
                    'title': title.strip(),
                    'url': url,
                    'snippet': snippet.strip(),
                    'type': 'search'
                }
        except Exception as e:
            logger.debug(f"Error in _extract_search_item: {str(e)}")
        
        return None


# Convenience function
def perform_google_search(query: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to perform Google search
    Routes to SerpAPI or Playwright based on configuration
    
    Args:
        query: Search query
        
    Returns:
        Search results
    """
    # Check if SerpAPI should be used
    if Config.USE_SERPAPI:
        try:
            from automation.serpapi_search import perform_serpapi_search
            logger.info("Using SerpAPI for search")
            return perform_serpapi_search(query)
        except Exception as e:
            logger.error(f"SerpAPI failed, falling back to Playwright: {str(e)}")
            # Fall through to Playwright
    
    # Use Playwright
    logger.info("Using Playwright for search")
    automation = GoogleSearchAutomation()
    return automation.search_google(query)

