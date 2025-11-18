"""Main CLI application."""
import sys
from pathlib import Path
from typing import List
from datetime import datetime

from config.config import Config
from api.wb_client import WBAPIClient
from data.loader import DataLoader
from analyzer.calculator import Calculator
from storage.export import Exporter
from models.product import Product, ProductMetrics
from cli.prompts import Prompts

def load_from_api() -> List[Product]:
    """Загрузить данные из WB API."""
    try:
        Config.validate()
        print("\n🔗 Подключение к WB API...")
        
        client = WBAPIClient(Config.WB_API_KEY, Config.WB_API_URL)
        
        # Запрашиваем дату начала в формате RFC3339
        print("\n📅 Формат даты: YYYY-MM-DDTHH:MM:SSZ (RFC3339)")
        print("Пример: 2025-10-13T00:00:00Z")
        
        date_from = Prompts.get_string_input(
            "Дата начала (RFC3339)", 
            f"{Config.DATE_FROM}T00:00:00Z"
        )
        
        print("\n⏳ Загрузка данных о продажах...")
        print("💡 WB API обновляет данные раз в 30 минут")
        
        # Вызываем API с правильным количеством аргументов
        sales_data = client.get_sales(date_from=date_from)
        
        if not sales_data:
            print("⚠️  Данные не найдены")
            print("💡 Попробуйте:")
            print("   - Изменить дату начала")
            print("   - Проверить API ключ в .env")
            print("   - Убедиться, что есть продажи за этот период")
            return []
        
        print(f"✅ Загружено {len(sales_data)} записей")
        
        # Показываем пример полей
        if sales_data:
            print("\n🔑 Доступные поля в данных:")
            for key in list(sales_data[0].keys())[:10]:
                value = sales_data[0].get(key)
                print(f"  - {key}: {value}")
            if len(sales_data[0].keys()) > 10:
                print(f"  ... и ещё {len(sales_data[0].keys()) - 10} полей")
        
        # TODO: Преобразовать данные WB API в Product
        print("\n⚠️  Преобразование данных WB API в Product ещё не реализовано")
        print("💡 Используйте опцию 2 (Загрузка из CSV) для полного анализа")
        return []
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return []

def load_from_csv() -> List[Product]:
    """Загрузить данные из CSV."""
    try:
        file_path = Prompts.get_string_input("Путь к CSV файлу", "data_samples/43-nedelia-2-List1.csv")
        
        if not Path(file_path).exists():
            print(f"❌ Файл не найден: {file_path}")
            return []
        
        print("\n⏳ Загрузка CSV...")
        data = DataLoader.load_from_csv(file_path)
        
        if not data:
            print("⚠️  CSV пуст")
            return []
        
        print(f"✅ Загружено {len(data)} записей")
        
        # Получаем ручной ввод для каждого товара
        products = []
        for row in data[:5]:  # Ограничим первыми 5 для демо
            print(f"\n📦 Товар: {row.get('nm_id', 'N/A')}")
            manual_data = Prompts.get_manual_input_data()
            product = DataLoader.parse_wb_csv_to_product(row, manual_data)
            products.append(product)
        
        return products
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return []

def load_from_json() -> List[Product]:
    """Загрузить данные из JSON."""
    try:
        file_path = Prompts.get_string_input("Путь к JSON файлу", "data_samples/test.txt")
        
        if not Path(file_path).exists():
            print(f"❌ Файл не найден: {file_path}")
            return []
        
        print("\n⏳ Загрузка JSON...")
        data = DataLoader.load_from_json(file_path)
        
        print(f"✅ Загружено {len(data)} записей")
        
        # TODO: Реализовать парсинг JSON в Product
        return []
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return []

def process_products(products: List[Product]) -> List[ProductMetrics]:
    """Обработать товары и рассчитать метрики."""
    if not products:
        return []
    
    print("\n📊 Расчёт метрик...")
    
    calculator = Calculator()
    metrics = [calculator.calculate_all_metrics(p) for p in products]
    
    print(f"✅ Метрики рассчитаны для {len(metrics)} товаров")
    
    return metrics

def export_results(metrics: List[ProductMetrics]):
    """Экспортировать результаты."""
    if not metrics:
        return
    
    Config.ensure_output_dir()
    
    # Экспорт в JSON
    json_path = Config.OUTPUT_DIR / "report.json"
    Exporter.export_to_json(metrics, json_path)
    
    # Экспорт в CSV
    csv_path = Config.OUTPUT_DIR / "report.csv"
    Exporter.export_to_csv(metrics, csv_path)
    
    # Вывод сводки
    Exporter.print_summary(metrics)

def main():
    """Главная функция."""
    print("\n" + "="*60)
    print("🚀 WB API Formuli Python")
    print("📊 Python API для работы с формулами Wildberries")
    print("="*60)
    
    while True:
        choice = Prompts.display_menu()
        
        products = []
        
        if choice == "1":
            products = load_from_api()
        elif choice == "2":
            products = load_from_csv()
        elif choice == "3":
            products = load_from_json()
        elif choice == "4":
            print("\n👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор")
            continue
        
        if products:
            metrics = process_products(products)
            export_results(metrics)
            
            input("\n⏸️  Нажмите Enter для продолжения...")

if __name__ == "__main__":
    main()