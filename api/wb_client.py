"""Wildberries API client."""
import requests
from typing import Dict, List, Optional
from datetime import datetime

class WBAPIClient:
    """Client for Wildberries Supplier API."""
    
    def __init__(self, api_key: str, base_url: str = "https://suppliers-api.wildberries.ru"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_sales(self, date_from: str, date_to: str, nm_id: Optional[int] = None) -> List[Dict]:
        """
        Get sales data from WB API.
        
        Args:
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            nm_id: Optional product ID filter
            
        Returns:
            List of sales records
        """
        endpoint = f"{self.base_url}/api/v1/supplier/reportDetailByPeriod"
        
        params = {
            "dateFrom": date_from,
            "dateTo": date_to
        }
        
        if nm_id:
            params["nmId"] = nm_id
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка при запросе к WB API: {e}")
    
    def get_storage_data(self, date_from: str, date_to: str) -> List[Dict]:
        """
        Get storage cost data.
        
        Args:
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            
        Returns:
            List of storage records
        """
        endpoint = f"{self.base_url}/api/v1/supplier/reportSales"
        
        params = {
            "dateFrom": date_from,
            "dateTo": date_to
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка при запросе данных о хранении: {e}")
    
    def test_connection(self) -> bool:
        """
        Test API connection.
        
        Returns:
            True if connection successful
        """
        try:
            # Simple test endpoint
            endpoint = f"{self.base_url}/ping"
            response = requests.get(endpoint, headers=self.headers, timeout=10)
            return response.status_code == 200
        except:
            return False