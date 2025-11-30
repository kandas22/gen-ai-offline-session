"""
SerpAPI-based Google search
Eliminates reCAPTCHA issues by using SerpAPI service
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from serpapi import GoogleSearch
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SerpAPISearch:
    """Google search using SerpAPI"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize SerpAPI search
        
        Args:
            api_key: SerpAPI key (uses config if not provided)
        """
        self.api_key = api_key or Config.SERPAPI_KEY
        if not self.api_key:
            raise ValueError("SerpAPI key is required. Set SERPAPI_KEY in .env file")
        logger.info("SerpAPISearch initialized")
    
    def search(self, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform Google search using SerpAPI
        
        Args:
            query: Search query (uses config default if not provided)
            
        Returns:
            Search results dictionary
        """
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
            logger.info(f"Searching via SerpAPI: {query}")
            
            # Configure SerpAPI search
            params = {
                "q": query,
                "api_key": self.api_key,
                "engine": "google",
                "num": 10,  # Number of results
                "hl": "en",  # Language
                "gl": "us"   # Country
            }
            
            # Perform search
            search = GoogleSearch(params)
            raw_results = search.get_dict()
            
            # Check for errors
            if "error" in raw_results:
                raise Exception(raw_results["error"])
            
            # Extract organic results
            organic_results = raw_results.get("organic_results", [])
            
            # Extract news results if available
            news_results = raw_results.get("news_results", [])
            
            # Parse results
            parsed_results = []
            
            # Add news results first
            for item in news_results:
                parsed_results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'type': 'news',
                    'source': item.get('source', ''),
                    'date': item.get('date', '')
                })
            
            # Add organic results
            for item in organic_results:
                parsed_results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'type': 'search',
                    'position': item.get('position', 0)
                })
            
            results['results'] = parsed_results
            results['total_results'] = len(parsed_results)
            results['success'] = True
            
            logger.info(f"SerpAPI search completed. Found {len(parsed_results)} results")
            
        except Exception as e:
            error_msg = f"Error during SerpAPI search: {str(e)}"
            logger.error(error_msg)
            results['error'] = error_msg
        
        return results


def perform_serpapi_search(query: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to perform SerpAPI search
    
    Args:
        query: Search query
        
    Returns:
        Search results
    """
    searcher = SerpAPISearch()
    return searcher.search(query)
