"""Data loading from various sources."""
import json
import csv
import pandas as pd
from typing import List, Dict, Optional
from pathlib import Path
from models.product import Product, ManualInputData

class DataLoader:
    """Загрузчик данных из разных источников."""
    
    @staticmethod
    def load_from_csv(file_path: str) -> List[Dict]:
        """
        Загрузить данные из CSV файла.
        
        Args:
            file_path: Путь к CSV файлу
            
        Returns:
            Список словарей с данными
        """
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            return df.to_dict('records')
        except Exception as e:
            raise Exception(f"Ошибка чтения CSV: {e}")
    
    @staticmethod
    def load_from_json(file_path: str) -> List[Dict]:
        """
        Загрузить данные из JSON файла.
        
        Args:
            file_path: Путь к JSON файлу
            
        Returns:
            Список словарей с данными
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Если данные не в виде списка, оборачиваем
                if isinstance(data, dict):
                    return [data]
                return data
        except Exception as e:
            raise Exception(f"Ошибка чтения JSON: {e}")
    
    @staticmethod
    def parse_wb_csv_to_product(row: Dict, manual_data: Optional[ManualInputData] = None) -> Product:
        """
        Преобразовать строку WB CSV в объект Product.
        
        Args:
            row: Строка из CSV
            manual_data: Ручной ввод данных
            
        Returns:
            Объект Product
        """
        # Примерные названия колонок из WB отчёта
        # Нужно адаптировать под реальные названия
        return Product(
            nm_id=int(row.get('nm_id', row.get('nmId', 0))),
            product_name=row.get('product_name', row.get('sa_name', '')),
            deliveries=int(row.get('deliveries', row.get('Доставки', 0))),
            sales=int(row.get('sales', row.get('Продажи', 0))),
            returns=int(row.get('returns', row.get('Возвраты', 0))),
            refusals=int(row.get('refusals', row.get('Отказы', 0))),
            sales_amount_before_spp=float(row.get('sales_before_spp', 0)),
            sales_amount_after_spp=float(row.get('sales_after_spp', 0)),
            returns_amount=float(row.get('returns_amount', 0)),
            logistics_cost=float(row.get('logistics', 0)),
            storage_cost=float(row.get('storage', 0)),
            acceptance_cost=float(row.get('acceptance', 0)),
            penalty_cost=float(row.get('penalty', 0)),
            surcharges=float(row.get('surcharges', 0)),
            commission_with_spp=float(row.get('commission_with_spp', 0)),
            commission_without_spp=float(row.get('commission_without_spp', 0)),
            drr_cost=float(row.get('drr', 0)),
            manual_data=manual_data or ManualInputData()
        )