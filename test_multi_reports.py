#!/usr/bin/env python
"""
🧪 Быстрый тест мультирепортера WB API.
Загружает несколько отчётов параллельно и сохраняет в один JSON.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from api.multi_report_loader import MultiReportLoader

def main():
    """Главная функция тестирования."""
    print("\n" + "="*70)
    print("🧪 WB API MULTI-REPORT LOADER - БЫСТРЫЙ ТЕСТ")
    print("="*70 + "\n")
    
    # Загружаем переменные окружения
    load_dotenv()
    
    api_key = os.getenv("WB_API_KEY")
    if not api_key:
        print("❌ Ошибка: WB_API_KEY не найден в .env файле")
        print("💡 Создайте .env файл и добавьте:")
        print("   WB_API_KEY=ваш_ключ_здесь\n")
        return
    
    print(f"✅ API ключ найден: {api_key[:20]}...\n")
    
    # Создаём загрузчик
    loader = MultiReportLoader(api_key)
    
    # Определяем период (последние 7 дней)
    date_to = datetime.now()
    date_from = date_to - timedelta(days=7)
    
    date_from_str = date_from.strftime("%Y-%m-%dT00:00:00Z")
    date_to_str = date_to.strftime("%Y-%m-%dT23:59:59Z")
    
    print(f"📅 Период: {date_from_str} → {date_to_str}\n")
    
    # Выбираем отчёты для теста
    reports_to_test = [
        "reportDetail",   # 📊 ГЛАВНЫЙ финансовый отчёт (v5)
        "sales",          # 💰 Продажи и возвраты
        "orders",         # 📦 Заказы
        "stocks",         # 📦 Остатки
        "balance"         # 💳 Баланс
    ]
    
    print(f"📋 Загружаем {len(reports_to_test)} отчётов параллельно...")
    print("⏱️  Ожидайте 2-5 секунд...\n")
    
    # Загружаем все отчёты параллельно
    try:
        results = loader.load_reports_sync(
            report_keys=reports_to_test,
            date_from=date_from_str,
            date_to=date_to_str
        )
    except Exception as e:
        print(f"\n❌ Ошибка при загрузке: {e}")
        print("💡 Проверьте:")
        print("   1. API ключ в .env корректен")
        print("   2. Установлен aiohttp: pip install aiohttp")
        print("   3. Есть интернет-соединение\n")
        return
    
    # Выводим сводку
    loader.print_summary(results)
    
    # Сохраняем результат
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"wb_test_reports_{timestamp}.json"
    
    loader.save_to_json(results, output_file)
    
    # Итоговая информация
    file_size = output_file.stat().st_size / 1024
    
    print(f"\n🎉 ГОТОВО! Все отчёты обьединены в один файл:")
    print(f"   📄 {output_file}")
    print(f"   📏 Размер: {file_size:.1f} KB")
    
    # Показываем пример данных из главного отчёта
    if "reportDetail" in results and results["reportDetail"]["status"] == "success":
        report_data = results["reportDetail"]["data"]
        if report_data and len(report_data) > 0:
            print(f"\n🔍 Пример данных из отчёта о реализации (v5):")
            sample = report_data[0]
            print(f"   nm_id: {sample.get('nm_id', 'N/A')}")
            print(f"   Товар: {sample.get('subject_name', 'N/A')}")
            print(f"   К выплате: {sample.get('ppvz_for_pay', 0)} руб")
            print(f"   Комиссия: {sample.get('ppvz_sales_commission', 0)} руб")
            print(f"   Логистика: {sample.get('delivery_rub', 0)} руб")
            print(f"   Хранение: {sample.get('storage_fee', 0)} руб")
            print(f"   Штраф: {sample.get('penalty', 0)} руб")
    
    print("\n🚀 Тест завершён успешно!\n")
    print("📖 Для полной документации см.: docs/MULTI_REPORT_LOADER.md")
    print("📚 Примеры использования: examples/multi_report_example.py\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Прервано пользователем\n")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}\n")
        import traceback
        traceback.print_exc()