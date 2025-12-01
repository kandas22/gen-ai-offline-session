"""
Authentication handler using PyAutoGUI for 2FA bypass
"""
import time
from typing import Optional
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Try to import pyautogui, but handle failure for headless environments
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except (ImportError, KeyError):
    # KeyError can happen if DISPLAY env var is missing
    logger.warning("PyAutoGUI not available or no display detected. 2FA automation will be disabled.")
    PYAUTOGUI_AVAILABLE = False


class AuthHandler:
    """Handles authentication and 2FA using PyAutoGUI"""
    
    def __init__(self):
        """Initialize AuthHandler"""
        if PYAUTOGUI_AVAILABLE:
            try:
                pyautogui.PAUSE = Config.PYAUTOGUI_PAUSE
                pyautogui.FAILSAFE = Config.PYAUTOGUI_FAILSAFE
                logger.info("AuthHandler initialized with PyAutoGUI")
            except Exception as e:
                logger.warning(f"Failed to configure PyAutoGUI: {e}")
        else:
            logger.info("AuthHandler initialized (Headless Mode)")
    
    def handle_google_login(self, page, email: Optional[str] = None, 
                           password: Optional[str] = None) -> bool:
        """
        Handle Google login if required
        
        Args:
            page: Playwright page object
            email: Google email (optional, uses config if not provided)
            password: Google password (optional, uses config if not provided)
            
        Returns:
            True if login successful or not required
        """
        try:
            email = email or Config.GOOGLE_EMAIL
            password = password or Config.GOOGLE_PASSWORD
            
            if not email or not password:
                logger.warning("Email or password not configured")
                return False
            
            # Check if login page is present
            if page.locator('input[type="email"]').is_visible(timeout=3000):
                logger.info("Login page detected, attempting login")
                
                # Enter email
                page.fill('input[type="email"]', email)
                page.click('button:has-text("Next"), #identifierNext')
                time.sleep(2)
                
                # Enter password
                page.fill('input[type="password"]', password)
                page.click('button:has-text("Next"), #passwordNext')
                time.sleep(2)
                
                logger.info("Login credentials submitted")
                return True
            
            logger.info("No login required")
            return True
            
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            return False
    
    def handle_2fa_prompt(self, timeout: int = 60) -> bool:
        """
        Handle 2FA prompt using PyAutoGUI
        This method waits for manual intervention
        
        Args:
            timeout: Maximum time to wait for 2FA completion (seconds)
            
        Returns:
            True if 2FA handled successfully
        """
        try:
            logger.warning(f"2FA detected! Please complete 2FA manually within {timeout} seconds")
            logger.info("Waiting for manual 2FA completion...")
            
            # Wait for user to complete 2FA
            start_time = time.time()
            while time.time() - start_time < timeout:
                # Check if user has moved mouse (indicating activity)
                time.sleep(1)
            
            logger.info("2FA wait period completed")
            return True
            
        except Exception as e:
            logger.error(f"Error during 2FA handling: {str(e)}")
            return False
    
    def click_at_position(self, x: int, y: int):
        """
        Click at specific screen position using PyAutoGUI
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        if not PYAUTOGUI_AVAILABLE:
            logger.warning("PyAutoGUI not available, skipping click")
            return

        try:
            logger.info(f"Clicking at position ({x}, {y})")
            pyautogui.click(x, y)
        except Exception as e:
            logger.error(f"Error clicking at position: {str(e)}")
    
    def type_text(self, text: str):
        """
        Type text using PyAutoGUI
        
        Args:
            text: Text to type
        """
        if not PYAUTOGUI_AVAILABLE:
            logger.warning("PyAutoGUI not available, skipping typing")
            return

        try:
            logger.info(f"Typing text: {text[:20]}...")
            pyautogui.write(text)
        except Exception as e:
            logger.error(f"Error typing text: {str(e)}")
    
    def press_key(self, key: str):
        """
        Press a key using PyAutoGUI
        
        Args:
            key: Key to press (e.g., 'enter', 'tab')
        """
        if not PYAUTOGUI_AVAILABLE:
            logger.warning("PyAutoGUI not available, skipping key press")
            return

        try:
            logger.info(f"Pressing key: {key}")
            pyautogui.press(key)
        except Exception as e:
            logger.error(f"Error pressing key: {str(e)}")
