"""
API client utilities for communicating with the evaluation service
"""

import requests
from typing import List, Dict, Any, Optional
from config.settings import API_BASE_URL, API_KEY

class APIClient:
    def __init__(self, base_url: str = API_BASE_URL, api_key: str = API_KEY):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_llm_providers(self) -> List[str]:
        """Get list of available LLM providers"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/tasks/llm-providers",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to fetch LLM providers: {str(e)}")
    
    def get_scenarios(self, scenario_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of available scenarios"""
        try:
            params = {}
            if scenario_type:
                params["scenario_type"] = scenario_type
                
            response = requests.get(
                f"{self.base_url}/api/v1/tasks",
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to fetch scenarios: {str(e)}")
    
    def get_scenario(self, scenario_id: str) -> Dict[str, Any]:
        """Get specific scenario details"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/tasks/{scenario_id}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to fetch scenario {scenario_id}: {str(e)}")

# Global API client instance
api_client = APIClient()