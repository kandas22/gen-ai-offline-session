"""
Configuration management for Flask API
Loads settings from environment variables
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.')
    PORT = int(os.getenv('PORT', 5001))
    
    # Playwright Configuration
    HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'True').lower() == 'true'
    BROWSER_TYPE = os.getenv('BROWSER_TYPE', 'chromium')  # chromium, firefox, webkit
    SLOW_MO = int(os.getenv('SLOW_MO', 0))  # Slow down operations by N milliseconds
    TIMEOUT = int(os.getenv('TIMEOUT', 30000))  # Default timeout in milliseconds
    
    # Google Search Configuration
    GOOGLE_URL = os.getenv('GOOGLE_URL', 'https://www.google.com')
    SEARCH_QUERY = os.getenv('SEARCH_QUERY', 'rain news today')
    
    # SerpAPI Configuration
    USE_SERPAPI = os.getenv('USE_SERPAPI', 'True').lower() == 'true'
    SERPAPI_KEY = os.getenv('SERPAPI_KEY', '')
    
    # 2FA Configuration (if needed)
    ENABLE_2FA = os.getenv('ENABLE_2FA', 'False').lower() == 'true'
    GOOGLE_EMAIL = os.getenv('GOOGLE_EMAIL', '')
    GOOGLE_PASSWORD = os.getenv('GOOGLE_PASSWORD', '')
    
    # PyAutoGUI Configuration
    PYAUTOGUI_PAUSE = float(os.getenv('PYAUTOGUI_PAUSE', 1.0))
    PYAUTOGUI_FAILSAFE = os.getenv('PYAUTOGUI_FAILSAFE', 'True').lower() == 'true'
    
    # BDD Configuration
    BDD_FEATURES_DIR = os.getenv('BDD_FEATURES_DIR', 'features')
    BDD_STEPS_DIR = os.getenv('BDD_STEPS_DIR', 'features/steps')
    BDD_GENERATED_DIR = os.getenv('BDD_GENERATED_DIR', 'features/generated')
    
    # Storage Configuration
    SCREENSHOTS_DIR = os.getenv('SCREENSHOTS_DIR', 'screenshots')
    RESULTS_DIR = os.getenv('RESULTS_DIR', 'results')
    LOGS_DIR = os.getenv('LOGS_DIR', 'logs')

    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    @classmethod
    def get_database_url(cls):
        """
        Get database URL with IPv4 resolution to avoid Docker networking issues
        """
        url = cls.DATABASE_URL
        if not url:
            return None
            
        try:
            # Parse the URL to extract hostname
            # Format: postgresql://user:pass@host:port/dbname
            # Use rsplit to handle passwords containing '@'
            if '@' in url:
                prefix, _, suffix = url.rpartition('@')
                
                host_part = suffix.split('/')[0]
                if ':' in host_part:
                    hostname = host_part.split(':')[0]
                    port = host_part.split(':')[1]
                else:
                    hostname = host_part
                    port = '5432'
                
                print(f"Resolving database host: {hostname}")
                
                # Resolve hostname to IPv4
                import socket
                try:
                    # AF_INET forces IPv4
                    addr_info = socket.getaddrinfo(hostname, port, socket.AF_INET)
                    if addr_info:
                        ip_address = addr_info[0][4][0]
                        print(f"Resolved {hostname} to IPv4: {ip_address}")
                        
                        # Replace hostname with IP in the URL
                        new_suffix = suffix.replace(hostname, ip_address, 1)
                        return f"{prefix}@{new_suffix}"
                except Exception as e:
                    print(f"Warning: Failed to resolve database host {hostname} to IPv4: {e}")
                    print("CRITICAL: Your database host appears to be IPv6-only.")
                    print("Docker environments (like Render) often require IPv4.")
                    print("Please update your DATABASE_URL to use the Supabase Connection Pooler:")
                    print("1. Go to Supabase Dashboard -> Database -> Connection Pooling")
                    print("2. Copy the 'Transaction' or 'Session' connection string")
                    print("3. Update your DATABASE_URL environment variable")
                    
        except Exception as e:
            print(f"Warning: Error parsing database URL: {e}")
            
        return url
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        directories = [
            cls.SCREENSHOTS_DIR,
            cls.RESULTS_DIR,
            cls.LOGS_DIR,
            cls.BDD_FEATURES_DIR,
            cls.BDD_STEPS_DIR,
            cls.BDD_GENERATED_DIR,
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
