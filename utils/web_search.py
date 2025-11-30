import os
import json
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

from config.config import SERPER_API_KEY, MAX_WEB_RESULTS

class WebSearchError(Exception):
    """Custom exception for web search related errors."""
    pass

class WebSearch:
    """Handles web search functionality for the chatbot."""
    
    def __init__(self, api_key: str = None):
        """Initialize the web search with an optional API key."""
        self.api_key = api_key or SERPER_API_KEY
        if not self.api_key:
            raise WebSearchError("No API key provided for web search")
        
        self.base_url = "https://google.serper.dev/search"
        self.headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def search(self, query: str, num_results: int = None) -> List[Dict[str, Any]]:
        """
        Perform a web search and return the results.
        
        Args:
            query: The search query
            num_results: Maximum number of results to return
            
        Returns:
            List of search results with title, link, and snippet
        """
        num_results = min(num_results or MAX_WEB_RESULTS, 10)  # Max 10 results
        
        try:
            payload = json.dumps({
                "q": query,
                "num": num_results
            })
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                data=payload,
                timeout=10
            )
            response.raise_for_status()
            
            return self._process_search_results(response.json())
            
        except requests.exceptions.RequestException as e:
            raise WebSearchError(f"Error performing web search: {str(e)}")
    
    def _process_search_results(self, search_response: Dict[str, Any]) -> List[Dict[str, str]]:
        """Process the raw search response into a structured format."""
        results = []
        
        # Extract organic results
        for result in search_response.get('organic', [])[:MAX_WEB_RESULTS]:
            if 'title' in result and 'link' in result:
                results.append({
                    'title': result.get('title', 'No title'),
                    'link': result.get('link', ''),
                    'snippet': result.get('snippet', 'No description available'),
                    'source': self._get_domain(result.get('link', ''))
                })
        
        # If no organic results, try to extract from answer box
        if not results and 'answerBox' in search_response:
            answer = search_response['answerBox']
            results.append({
                'title': answer.get('title', 'Answer'),
                'link': answer.get('link', ''),
                'snippet': answer.get('answer', answer.get('snippet', 'No description available')),
                'source': self._get_domain(answer.get('link', ''))
            })
        
        return results
    
    @staticmethod
    def _get_domain(url: str) -> str:
        """Extract domain from URL."""
        if not url:
            return "Unknown source"
        try:
            domain = urlparse(url).netloc
            return domain.replace('www.', '') if domain else "Unknown source"
        except:
            return "Unknown source"

def get_web_searcher() -> WebSearch:
    """Factory function to get a WebSearch instance."""
    return WebSearch()
