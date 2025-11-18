"""Wildberries API client with all official endpoints."""
import requests
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class WBAPIClient:
    """
    Клиент для Wildberries Statistics API (v1).
    
    Официальная документация: https://dev.wildberries.ru/openapi/reports
    Базовый URL: https://statistics-api.wildberries.ru
    """
    
    def __init__(self, api_key: str, base_url: str = "https://statistics-api.wildberries.ru"):
        """
        Инициализация API клиента.
        
        Args:
            api_key: WB API ключ
            base_url: Базовый URL (statistics-api.wildberries.ru)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
    
    # ========== ОСНОВНЫЕ ОТЧЁТЫ (СТАТИСТИКА) ==========
    
    def get_incomes(self, date_from: str) -> List[Dict]:
        """
        Поставки - количество поставок товаров на склады WB.
        
        Endpoint: /api/v1/supplier/incomes
        Обновление: раз в 30 минут
        Лимит: 100000 строк
        
        Args:
            date_from: Дата и время последнего изменения (RFC3339): "2025-10-13T00:00:00Z"
            
        Returns:
            Список поставок
        """
        endpoint = f"{self.base_url}/api/v1/supplier/incomes"
        params = {"dateFrom": date_from}
        return self._make_request(endpoint, params)
    
    def get_stocks(self, date_from: str) -> List[Dict]:
        """
        Склады - остатки товаров на складах WB.
        
        Endpoint: /api/v1/supplier/stocks
        Обновление: раз в 30 минут
        Лимит: 60000 строк
        
        Args:
            date_from: Дата и время последнего изменения (RFC3339)
            
        Returns:
            Список остатков
        """
        endpoint = f"{self.base_url}/api/v1/supplier/stocks"
        params = {"dateFrom": date_from}
        return self._make_request(endpoint, params)
    
    def get_orders(self, date_from: str, flag: int = 0) -> List[Dict]:
        """
        Заказы - информация обо всех заказах.
        
        Endpoint: /api/v1/supplier/orders
        Обновление: раз в 30 минут
        Лимит: 80000 строк
        Хранение: 90 дней
        
        Args:
            date_from: Дата и время последнего изменения (RFC3339)
            flag: 0 (по умолчанию) - все заказы, 1 - только новые
            
        Returns:
            Список заказов (1 строка = 1 заказ = 1 единица товара)
        """
        endpoint = f"{self.base_url}/api/v1/supplier/orders"
        params = {"dateFrom": date_from, "flag": flag}
        return self._make_request(endpoint, params)
    
    def get_sales(self, date_from: str, flag: int = 0) -> List[Dict]:
        """
        Продажи - информация о продажах и возвратах.
        
        Endpoint: /api/v1/supplier/sales
        Обновление: раз в 30 минут
        Лимит: 80000 строк
        Хранение: 90 дней
        
        Args:
            date_from: Дата и время последнего изменения (RFC3339)
            flag: 0 (по умолчанию) - все продажи, 1 - только новые
            
        Returns:
            Список продаж и возвратов (1 строка = 1 заказ = 1 единица)
        """
        endpoint = f"{self.base_url}/api/v1/supplier/sales"
        params = {"dateFrom": date_from, "flag": flag}
        return self._make_request(endpoint, params)
    
    # ========== ФИНАНСОВЫЕ ОТЧЁТЫ ==========
    
    def get_excise_report(self, date_from: str, date_to: str, countries: Optional[List[str]] = None) -> Dict:
        """
        Отчёт о товарах с обязательной маркировкой.
        
        Endpoint: /api/v1/analytics/excise-report
        
        Args:
            date_from: Начало периода (YYYY-MM-DD)
            date_to: Конец периода (YYYY-MM-DD)
            countries: Коды стран ["AM", "BY", "KG", "KZ", "RU", "UZ"]
            
        Returns:
            Отчёт с операциями по маркированным товарам
        """
        endpoint = f"{self.base_url}/api/v1/analytics/excise-report"
        params = {"dateFrom": date_from, "dateTo": date_to}
        body = {"countries": countries} if countries else {}
        return self._make_request(endpoint, params, method="POST", json_body=body)
    
    def get_region_sales(self, date_from: str, date_to: str) -> Dict:
        """
        Продажи по регионам - данные продаж по регионам.
        
        Endpoint: /api/v1/analytics/region-sale
        Максимальный период: 31 день
        
        Args:
            date_from: Начало (YYYY-MM-DD)
            date_to: Конец (YYYY-MM-DD)
            
        Returns:
            Отчёт по регионам
        """
        endpoint = f"{self.base_url}/api/v1/analytics/region-sale"
        params = {"dateFrom": date_from, "dateTo": date_to}
        return self._make_request(endpoint, params)
    
    # ========== ОТЧЁТЫ ОБ УДЕРЖАНИЯХ (ШТРАФЫ) ==========
    
    def get_warehouse_measurements(self, date_from: str, date_to: str, tab: str, limit: int, offset: int = 0) -> Dict:
        """
        Занижение габаритов упаковки и замеры склада.
        
        Endpoint: /api/v1/analytics/warehouse-measurements
        
        Args:
            date_from: Начало (RFC3339): "2025-02-01T15:00:00Z"
            date_to: Конец (RFC3339): "2025-10-11T18:00:00Z"
            tab: "penalty" (удержания) или "measurement" (замеры)
            limit: Количество записей (<= 1000)
            offset: Смещение
            
        Returns:
            Отчёт об удержаниях/замерах
        """
        endpoint = f"{self.base_url}/api/v1/analytics/warehouse-measurements"
        params = {
            "dateFrom": date_from,
            "dateTo": date_to,
            "tab": tab,
            "limit": min(limit, 1000),
            "offset": offset
        }
        return self._make_request(endpoint, params)
    
    def get_antifraud_details(self, date: Optional[str] = None) -> Dict:
        """
        Самовыкупы - отчёт об удержаниях за самовыкупы (30% стоимости).
        
        Endpoint: /api/v1/analytics/antifraud-details
        Отчёт формируется каждую среду до 7:00 МСК за неделю
        Данные доступны с августа 2023
        
        Args:
            date: Дата в отчётном периоде (YYYY-MM-DD), например "2023-12-01"
            
        Returns:
            Отчёт об удержаниях за самовыкупы
        """
        endpoint = f"{self.base_url}/api/v1/analytics/antifraud-details"
        params = {"date": date} if date else {}
        return self._make_request(endpoint, params)
    
    def get_incorrect_attachments(self, date_from: str, date_to: str) -> Dict:
        """
        Подмена товара - удержания 100% стоимости.
        
        Endpoint: /api/v1/analytics/incorrect-attachments
        Максимальный период: 31 день
        Данные с июня 2023
        
        Args:
            date_from: Начало (YYYY-MM-DD)
            date_to: Конец (YYYY-MM-DD)
            
        Returns:
            Отчёт об удержаниях за подмену
        """
        endpoint = f"{self.base_url}/api/v1/analytics/incorrect-attachments"
        params = {"dateFrom": date_from, "dateTo": date_to}
        return self._make_request(endpoint, params)
    
    def get_goods_labeling(self, date_from: str, date_to: str) -> Dict:
        """
        Маркировка товара - штрафы за отсутствие маркировки.
        
        Endpoint: /api/v1/analytics/goods-labeling
        Максимальный период: 31 день
        Данные с марта 2024
        
        Args:
            date_from: Начало (YYYY-MM-DD)
            date_to: Конец (YYYY-MM-DD)
            
        Returns:
            Отчёт о штрафах
        """
        endpoint = f"{self.base_url}/api/v1/analytics/goods-labeling"
        params = {"dateFrom": date_from, "dateTo": date_to}
        return self._make_request(endpoint, params)
    
    def get_characteristics_change(self, date_from: str, date_to: str) -> Dict:
        """
        Смена характеристик - удержания за перемаркировку.
        
        Endpoint: /api/v1/analytics/characteristics-change
        Максимальный период: 31 день
        Данные с 28 декабря 2021
        
        Args:
            date_from: Начало (YYYY-MM-DD)
            date_to: Конец (YYYY-MM-DD)
            
        Returns:
            Отчёт об удержаниях
        """
        endpoint = f"{self.base_url}/api/v1/analytics/characteristics-change"
        params = {"dateFrom": date_from, "dateTo": date_to}
        return self._make_request(endpoint, params)
    
    # ========== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ==========
    
    def _make_request(self, endpoint: str, params: Dict, method: str = "GET", json_body: Optional[Dict] = None) -> any:
        """Выполнить HTTP запрос."""
        try:
            if method == "GET":
                response = requests.get(endpoint, headers=self.headers, params=params, timeout=30)
            elif method == "POST":
                response = requests.post(endpoint, headers=self.headers, params=params, json=json_body, timeout=30)
            else:
                raise ValueError(f"Неподдерживаемый метод: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("❌ Ошибка 401: Неверный API ключ")
            elif e.response.status_code == 403:
                raise Exception("❌ Ошибка 403: Нет доступа к этому ресурсу")
            elif e.response.status_code == 429:
                raise Exception("❌ Ошибка 429: Превышен лимит запросов")
            else:
                raise Exception(f"❌ HTTP ошибка {e.response.status_code}: {e}")
        except Exception as e:
            raise Exception(f"❌ Ошибка запроса: {e}")
    
    def test_connection(self) -> bool:
        """Проверить соединение с API."""
        try:
            # Тестовый запрос с минимальным периодом
            date_from = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")
            self.get_sales(date_from=date_from)
            return True
        except Exception as e:
            print(f"❌ Тест не пройден: {e}")
            return False