"""Wildberries API client."""
import requests
from typing import Dict, List, Optional
from datetime import datetime

class WBAPIClient:
    """Client for Wildberries Statistics API v5."""
    
    def __init__(self, api_key: str, base_url: str = "https://statistics-api.wildberries.ru"):
        """
        Initialize WB API client.
        
        Args:
            api_key: WB API key
            base_url: Base URL (default: statistics-api.wildberries.ru)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": api_key,  # WB использует прямую передачу ключа
            "Content-Type": "application/json"
        }
    
    def get_sales(self, date_from: str, date_to: str, limit: int = 1000000) -> List[Dict]:
        """
        Получить детальный отчёт о продажах за период.
        
        Endpoint: /api/v5/supplier/reportDetailByPeriod
        
        Args:
            date_from: Дата начала (YYYY-MM-DD)
            date_to: Дата окончания (YYYY-MM-DD)
            limit: Максимальное количество записей (по умолчанию 1000000)
            
        Returns:
            Список записей о продажах
            
        Example:
            >>> client = WBAPIClient(api_key="your_key")
            >>> data = client.get_sales("2025-10-13", "2025-10-19")
        """
        endpoint = f"{self.base_url}/api/v5/supplier/reportDetailByPeriod"
        
        params = {
            "limit": limit,
            "dateFrom": date_from,
            "dateTo": date_to
        }
        
        try:
            print(f"🔄 Запрос к WB API: {endpoint}")
            print(f"📅 Период: {date_from} - {date_to}")
            
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if isinstance(data, list):
                print(f"✅ Получено {len(data)} записей")
                return data
            else:
                print("⚠️  Неожиданный формат ответа")
                return []
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("❌ Ошибка авторизации. Проверьте API ключ в .env файле")
            elif e.response.status_code == 403:
                raise Exception("❌ Доступ запрещён. Убедитесь, что у API ключа есть права на статистику")
            else:
                raise Exception(f"❌ HTTP ошибка {e.response.status_code}: {e}")
        except requests.exceptions.ConnectionError:
            raise Exception("❌ Ошибка соединения. Проверьте интернет-подключение")
        except requests.exceptions.Timeout:
            raise Exception("❌ Превышено время ожидания ответа от API")
        except requests.exceptions.RequestException as e:
            raise Exception(f"❌ Ошибка при запросе к WB API: {e}")
        except ValueError as e:
            raise Exception(f"❌ Ошибка парсинга JSON ответа: {e}")
    
    def get_sales_by_nm_id(self, date_from: str, date_to: str, nm_id: int, limit: int = 1000000) -> List[Dict]:
        """
        Получить данные о продажах конкретного товара.
        
        Args:
            date_from: Дата начала
            date_to: Дата окончания
            nm_id: ID товара (Артикул WB)
            limit: Максимальное количество записей
            
        Returns:
            Отфильтрованный список записей
        """
        all_data = self.get_sales(date_from, date_to, limit)
        
        # Фильтруем по nm_id
        filtered = [item for item in all_data if item.get('nm_id') == nm_id or item.get('nmId') == nm_id]
        
        print(f"🔍 Найдено {len(filtered)} записей для nm_id={nm_id}")
        return filtered
    
    def test_connection(self) -> bool:
        """
        Проверить соединение с API.
        
        Returns:
            True если соединение успешно
        """
        try:
            # Тестовый запрос с минимальным периодом
            from datetime import date, timedelta
            today = date.today()
            yesterday = today - timedelta(days=1)
            
            self.get_sales(
                date_from=yesterday.strftime("%Y-%m-%d"),
                date_to=today.strftime("%Y-%m-%d"),
                limit=1
            )
            return True
        except Exception as e:
            print(f"❌ Тест соединения не пройден: {e}")
            return False
    
    def print_sample_record(self, date_from: str, date_to: str):
        """
        Вывести пример записи для понимания структуры данных.
        
        Args:
            date_from: Дата начала
            date_to: Дата окончания
        """
        try:
            data = self.get_sales(date_from, date_to, limit=1)
            
            if data:
                print("\n📋 ПРИМЕР ЗАПИСИ ИЗ API:")
                print("=" * 60)
                import json
                print(json.dumps(data[0], indent=2, ensure_ascii=False))
                print("=" * 60)
                
                print("\n🔑 ДОСТУПНЫЕ ПОЛЯ:")
                for key in sorted(data[0].keys()):
                    print(f"  - {key}")
            else:
                print("⚠️  Нет данных за указанный период")
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")