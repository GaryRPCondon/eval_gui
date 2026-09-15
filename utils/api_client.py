"""
API client utilities for communicating with the evaluation service
"""

import requests
from typing import List
from config.settings import API_BASE_URL, API_KEY

class APIClient:
    def __init__(self, base_url: str = API_BASE_URL, api_key: str = API_KEY):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.last_error: str = ""
    
    def get_llm_providers(self) -> List[str]:
        """List of available LLM providers from the evaluation service.

        Returns an empty list (and records last_error) when the service is
        unreachable; callers fall back to reading llm_providers.py from disk,
        which is the same list the endpoint serves.
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/tasks/llm-providers",
                headers=self.headers,
                timeout=5
            )
            response.raise_for_status()
            self.last_error = ""
            return list(response.json())
        except Exception as e:
            self.last_error = str(e)
            return []

# Global API client instance
api_client = APIClient()
