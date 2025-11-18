"""Параллельная загрузка нескольких отчётов WB API."""
import asyncio
import aiohttp
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

class MultiReportLoader:
    """
    Класс для параллельной загрузки множества отчётов WB API.
    Результаты объединяются в один JSON/CSV файл.
    """
    
    # Конфигурация всех доступных отчётов
    ENDPOINTS = {
        "reportDetail": {
            "name": "Отчёт о реализации (v5)",
            "url": "https://statistics-api.wildberries.ru/api/v5/supplier/reportDetailByPeriod",
            "params_builder": lambda df, dt: {"dateFrom": df[:10], "dateTo": dt[:10], "limit": 100000}
        },
        "sales": {
            "name": "Продажи и возвраты",
            "url": "https://statistics-api.wildberries.ru/api/v1/supplier/sales",
            "params_builder": lambda df, dt: {"dateFrom": df}
        },
        "orders": {
            "name": "Заказы",
            "url": "https://statistics-api.wildberries.ru/api/v1/supplier/orders",
            "params_builder": lambda df, dt: {"dateFrom": df}
        },
        "stocks": {
            "name": "Остатки на складах",
            "url": "https://statistics-api.wildberries.ru/api/v1/supplier/stocks",
            "params_builder": lambda df, dt: {"dateFrom": df}
        },
        "incomes": {
            "name": "Поставки",
            "url": "https://statistics-api.wildberries.ru/api/v1/supplier/incomes",
            "params_builder": lambda df, dt: {"dateFrom": df}
        },
        "antifraud": {
            "name": "Самовыкупы (30%)",
            "url": "https://statistics-api.wildberries.ru/api/v1/analytics/antifraud-details",
            "params_builder": lambda df, dt: {"date": dt[:10] if dt else df[:10]}
        },
        "penalties": {
            "name": "Габариты/штрафы",
            "url": "https://statistics-api.wildberries.ru/api/v1/analytics/warehouse-measurements",
            "params_builder": lambda df, dt: {"dateFrom": df, "dateTo": dt, "tab": "penalty", "limit": 1000}
        },
        "balance": {
            "name": "Баланс продавца",
            "url": "https://statistics-api.wildberries.ru/api/v1/account/balance",
            "params_builder": lambda df, dt: {}
        },
        "region_sales": {
            "name": "Продажи по регионам",
            "url": "https://statistics-api.wildberries.ru/api/v1/analytics/region-sale",
            "params_builder": lambda df, dt: {"dateFrom": df[:10], "dateTo": dt[:10]}
        },
        "excise": {
            "name": "Маркированные товары",
            "url": "https://statistics-api.wildberries.ru/api/v1/analytics/excise-report",
            "params_builder": lambda df, dt: {"dateFrom": df[:10], "dateTo": dt[:10]}
        }
    }
    
    def __init__(self, api_key: str):
        """Инициализация с API ключом."""
        self.api_key = api_key
        self.headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
    
    async def _fetch_report(self, session: aiohttp.ClientSession, report_key: str, 
                           date_from: str, date_to: str) -> tuple:
        """
        Загрузить один отчёт асинхронно.
        
        Returns:
            (report_key, data_or_error)
        """
        endpoint_config = self.ENDPOINTS.get(report_key)
        if not endpoint_config:
            return report_key, {"error": "Unknown report type"}
        
        url = endpoint_config["url"]
        params = endpoint_config["params_builder"](date_from, date_to)
        
        try:
            async with session.get(url, headers=self.headers, params=params, timeout=60) as response:
                if response.status == 200:
                    data = await response.json()
                    return report_key, {
                        "name": endpoint_config["name"],
                        "status": "success",
                        "count": len(data) if isinstance(data, list) else 1,
                        "data": data
                    }
                else:
                    text = await response.text()
                    return report_key, {
                        "name": endpoint_config["name"],
                        "status": "error",
                        "http_code": response.status,
                        "error": text or f"HTTP {response.status}"
                    }
        except Exception as e:
            return report_key, {
                "name": endpoint_config["name"],
                "status": "error",
                "error": str(e)
            }
    
    async def fetch_multiple_reports(self, report_keys: List[str], 
                                    date_from: str, date_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Параллельная загрузка нескольких отчётов.
        
        Args:
            report_keys: Список ключей отчётов из ENDPOINTS
            date_from: Дата начала (RFC3339): "2025-10-13T00:00:00Z"
            date_to: Дата окончания (RFC3339), опционально
            
        Returns:
            Словарь {report_key: result}
        """
        if not date_to:
            date_to = date_from
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._fetch_report(session, key, date_from, date_to)
                for key in report_keys
            ]
            results = await asyncio.gather(*tasks)
        
        return dict(results)
    
    def load_reports_sync(self, report_keys: List[str], 
                         date_from: str, date_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Синхронная обёртка для загрузки отчётов.
        
        Args:
            report_keys: Список ключей отчётов
            date_from: Дата начала (RFC3339)
            date_to: Дата окончания (RFC3339)
            
        Returns:
            Словарь с результатами всех отчётов
        """
        return asyncio.run(self.fetch_multiple_reports(report_keys, date_from, date_to))
    
    def save_to_json(self, data: Dict[str, Any], output_path: Path) -> None:
        """
        Сохранить объединённые результаты в JSON.
        
        Args:
            data: Данные всех отчётов
            output_path: Путь для сохранения
        """
        # Добавляем метаданные
        output = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "reports_count": len(data),
                "reports_loaded": list(data.keys())
            },
            "reports": data
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Данные сохранены: {output_path}")
    
    def print_summary(self, data: Dict[str, Any]) -> None:
        """
        Вывести сводку по загруженным отчётам.
        
        Args:
            data: Результаты загрузки
        """
        print("\n" + "="*60)
        print("📊 СВОДКА ЗАГРУЗКИ ОТЧЁТОВ")
        print("="*60)
        
        for key, result in data.items():
            name = result.get("name", key)
            status = result.get("status", "unknown")
            
            if status == "success":
                count = result.get("count", 0)
                print(f"✅ {name}: {count} записей")
            else:
                error = result.get("error", "Unknown error")
                print(f"❌ {name}: {error}")
        
        print("="*60 + "\n")


# Пример использования
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_key = os.getenv("WB_API_KEY")
    if not api_key:
        print("❌ WB_API_KEY не найден в .env")
        exit(1)
    
    # Создаём загрузчик
    loader = MultiReportLoader(api_key)
    
    # Выбираем отчёты для загрузки
    reports_to_load = [
        "reportDetail",  # Главный финансовый отчёт
        "sales",
        "orders",
        "stocks",
        "balance"
    ]
    
    # Загружаем параллельно
    print("⏳ Загрузка отчётов WB...")
    results = loader.load_reports_sync(
        report_keys=reports_to_load,
        date_from="2025-10-13T00:00:00Z",
        date_to="2025-10-19T23:59:59Z"
    )
    
    # Выводим сводку
    loader.print_summary(results)
    
    # Сохраняем в файл
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"wb_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    loader.save_to_json(results, output_file)
    
    print(f"\n🎉 Готово! Все отчёты в одном файле: {output_file}")