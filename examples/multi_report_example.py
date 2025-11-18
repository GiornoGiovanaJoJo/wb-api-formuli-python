"""Пример использования MultiReportLoader для массовой загрузки отчётов WB."""
import os
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

from api.multi_report_loader import MultiReportLoader

# Загружаем переменные окружения
load_dotenv()

def main():
    """
    Пример 1: Загрузка всех основных отчётов за неделю.
    """
    print("\n" + "="*70)
    print("📦 ПРИМЕР 1: Загрузка всех основных отчётов WB за неделю")
    print("="*70 + "\n")
    
    # Получаем API ключ
    api_key = os.getenv("WB_API_KEY")
    if not api_key:
        print("❌ Ошибка: WB_API_KEY не найден в .env файле")
        return
    
    # Создаём загрузчик
    loader = MultiReportLoader(api_key)
    
    # Определяем период (последние 7 дней)
    date_to = datetime.now()
    date_from = date_to - timedelta(days=7)
    
    date_from_str = date_from.strftime("%Y-%m-%dT00:00:00Z")
    date_to_str = date_to.strftime("%Y-%m-%dT23:59:59Z")
    
    print(f"📅 Период: {date_from_str} → {date_to_str}\n")
    
    # Выбираем все доступные отчёты
    reports_to_load = [
        "reportDetail",   # 📊 Главный финансовый отчёт (v5)
        "sales",          # 💰 Продажи и возвраты
        "orders",         # 📦 Заказы
        "stocks",         # 📦 Остатки
        "incomes",        # 🚚 Поставки
        "antifraud",      # 🚫 Самовыкупы
        "penalties",      # ⚠️ Штрафы за габариты
        "balance",        # 💳 Текущий баланс
    ]
    
    print(f"📋 Загружаем {len(reports_to_load)} отчётов параллельно...\n")
    
    # Загружаем все отчёты параллельно
    results = loader.load_reports_sync(
        report_keys=reports_to_load,
        date_from=date_from_str,
        date_to=date_to_str
    )
    
    # Выводим сводку
    loader.print_summary(results)
    
    # Сохраняем в файл
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"wb_multi_reports_{timestamp}.json"
    
    loader.save_to_json(results, output_file)
    
    print(f"\n🎉 Готово! Все отчёты объединены в один файл:")
    print(f"   📄 {output_file}")
    print(f"   📏 Размер: {output_file.stat().st_size / 1024:.1f} KB\n")


def example_custom_reports():
    """
    Пример 2: Загрузка только выбранных отчётов.
    """
    print("\n" + "="*70)
    print("📦 ПРИМЕР 2: Загрузка только финансовых отчётов")
    print("="*70 + "\n")
    
    api_key = os.getenv("WB_API_KEY")
    if not api_key:
        print("❌ WB_API_KEY не найден")
        return
    
    loader = MultiReportLoader(api_key)
    
    # Только финансовые отчёты
    financial_reports = [
        "reportDetail",  # Детализация реализации
        "balance",       # Баланс
        "antifraud",     # Самовыкупы
        "penalties"      # Штрафы
    ]
    
    results = loader.load_reports_sync(
        report_keys=financial_reports,
        date_from="2025-10-01T00:00:00Z",
        date_to="2025-10-31T23:59:59Z"
    )
    
    loader.print_summary(results)
    
    # Сохраняем
    output_file = Path("output") / "wb_financial_only.json"
    loader.save_to_json(results, output_file)
    
    print(f"\n💰 Финансовые отчёты сохранены: {output_file}\n")


if __name__ == "__main__":
    # Запускаем примеры
    main()
    
    print("\n" + "-"*70 + "\n")
    
    example_custom_reports()