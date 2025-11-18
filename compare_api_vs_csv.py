#!/usr/bin/env python
"""
📊 Сравнение данных из WB API с CSV отчётом и расчёт метрик.

Использование:
    # Базовое (последние 7 дней)
    python compare_api_vs_csv.py
    
    # С указанием периода
    python compare_api_vs_csv.py --from 2025-10-20 --to 2025-10-26
    
    # С указанием CSV файла
    python compare_api_vs_csv.py --csv data_samples/my_report.csv
    
    # Полная команда
    python compare_api_vs_csv.py --from 2025-10-20 --to 2025-10-26 --csv data_samples/43-nedelia.csv

Что делает:
1. Загружает данные через WB API (используя multi_report_loader)
2. Загружает данные из CSV файла
3. Рассчитывает метрики для обоих источников
4. Сравнивает результаты и показывает расхождения
"""

import os
import sys
import json
import argparse
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from api.multi_report_loader import MultiReportLoader
from analyzer.calculator import Calculator


class DataComparator:
    """Класс для сравнения данных из WB API и CSV файлов."""
    
    def __init__(self, api_key: str):
        """
        Инициализация компаратора.
        
        Args:
            api_key: WB API ключ
        """
        self.loader = MultiReportLoader(api_key)
        self.calculator = Calculator()
    
    def load_api_data(self, date_from: str, date_to: str, reports: list = None):
        """
        Загрузить данные через WB API.
        
        Args:
            date_from: Дата начала (RFC3339)
            date_to: Дата окончания (RFC3339)
            reports: Список отчётов для загрузки
            
        Returns:
            Словарь с данными из API
        """
        if reports is None:
            reports = ["reportDetail"]
        
        print("\n📡 Загрузка данных через WB API...")
        print(f"   Период: {date_from} → {date_to}")
        print(f"   Отчёты: {', '.join(reports)}\n")
        
        results = self.loader.load_reports_sync(
            report_keys=reports,
            date_from=date_from,
            date_to=date_to
        )
        
        self.loader.print_summary(results)
        return results
    
    def load_csv_data(self, csv_path: Path):
        """
        Загрузить данные из CSV файла WB.
        
        Args:
            csv_path: Путь к CSV файлу
            
        Returns:
            DataFrame с данными из CSV
        """
        print(f"\n📄 Загрузка CSV: {csv_path}")
        
        # Читаем CSV, пропуская первые строки с комментариями
        df = pd.read_csv(csv_path, skiprows=8, encoding='utf-8')
        
        print(f"   Загружено строк: {len(df)}")
        print(f"   Колонок: {len(df.columns)}")
        
        return df
    
    def calculate_metrics_from_api(self, api_data: dict):
        """
        Рассчитать метрики из данных API.
        
        Args:
            api_data: Данные из WB API
            
        Returns:
            Словарь с рассчитанными метриками
        """
        print("\n🧮 Расчёт метрик из данных API...")
        
        metrics = {}
        
        # Если есть главный отчёт о реализации (v5)
        if "reportDetail" in api_data and api_data["reportDetail"]["status"] == "success":
            report_data = api_data["reportDetail"]["data"]
            
            if report_data and len(report_data) > 0:
                # Группируем по nm_id (артикулу)
                by_article = {}
                
                for row in report_data:
                    nm_id = row.get("nm_id")
                    if not nm_id:
                        continue
                    
                    if nm_id not in by_article:
                        by_article[nm_id] = {
                            "nm_id": nm_id,
                            "subject_name": row.get("subject_name", ""),
                            "brand_name": row.get("brand_name", ""),
                            "quantity": 0,
                            "ppvz_for_pay": 0,  # К выплате
                            "retail_amount": 0,  # Выручка
                            "ppvz_sales_commission": 0,  # Комиссия
                            "delivery_rub": 0,  # Логистика
                            "storage_fee": 0,  # Хранение
                            "penalty": 0,  # Штрафы
                            "acceptance": 0,  # Приёмка
                        }
                    
                    # Суммируем показатели
                    by_article[nm_id]["quantity"] += row.get("quantity", 0)
                    by_article[nm_id]["ppvz_for_pay"] += row.get("ppvz_for_pay", 0)
                    by_article[nm_id]["retail_amount"] += row.get("retail_amount", 0)
                    by_article[nm_id]["ppvz_sales_commission"] += row.get("ppvz_sales_commission", 0)
                    by_article[nm_id]["delivery_rub"] += row.get("delivery_rub", 0)
                    by_article[nm_id]["storage_fee"] += row.get("storage_fee", 0)
                    by_article[nm_id]["penalty"] += row.get("penalty", 0)
                    by_article[nm_id]["acceptance"] += row.get("acceptance", 0)
                
                metrics["by_article"] = by_article
                metrics["total_articles"] = len(by_article)
                metrics["total_quantity"] = sum(a["quantity"] for a in by_article.values())
                metrics["total_to_pay"] = sum(a["ppvz_for_pay"] for a in by_article.values())
                
                print(f"   ✅ Всего артикулов: {metrics['total_articles']}")
                print(f"   ✅ Всего продаж: {metrics['total_quantity']} шт")
                print(f"   ✅ К выплате: {metrics['total_to_pay']:.2f} руб")
        
        return metrics
    
    def calculate_metrics_from_csv(self, df: pd.DataFrame):
        """
        Рассчитать метрики из CSV данных.
        
        Args:
            df: DataFrame с данными из CSV
            
        Returns:
            Словарь с рассчитанными метриками
        """
        print("\n🧮 Расчёт метрик из CSV...")
        
        # Очищаем DataFrame от пустых строк и комментариев
        df = df[df.iloc[:, 2].notna()]  # Артикул ВБ не должен быть пустым
        df = df[df.iloc[:, 2] != '-1']  # Исключаем "Нераспределенное"
        
        metrics = {}
        by_article = {}
        
        # Предполагаемая структура колонок (по примеру из файла)
        # Колонка 2: Артикул ВБ (nm_id)
        # Колонка 3: Артикул продавца
        # Колонка 5: НазваниеГруппы
        # Колонка 9: Продажи (количество)
        # Колонка 48: К перечислению за товар
        
        for idx, row in df.iterrows():
            try:
                nm_id = str(row.iloc[2]).strip()  # Артикул ВБ
                if not nm_id or nm_id == 'nan':
                    continue
                
                article = {
                    "nm_id": nm_id,
                    "seller_article": str(row.iloc[3]) if len(row) > 3 else "",
                    "name": str(row.iloc[5]) if len(row) > 5 else "",
                    "quantity": self._safe_float(row.iloc[9]) if len(row) > 9 else 0,
                    "to_pay": self._safe_float(row.iloc[48]) if len(row) > 48 else 0,
                }
                
                by_article[nm_id] = article
            except Exception as e:
                continue
        
        metrics["by_article"] = by_article
        metrics["total_articles"] = len(by_article)
        metrics["total_quantity"] = sum(a["quantity"] for a in by_article.values())
        metrics["total_to_pay"] = sum(a["to_pay"] for a in by_article.values())
        
        print(f"   ✅ Всего артикулов: {metrics['total_articles']}")
        print(f"   ✅ Всего продаж: {metrics['total_quantity']:.0f} шт")
        print(f"   ✅ К выплате: {metrics['total_to_pay']:.2f} руб")
        
        return metrics
    
    def compare_metrics(self, api_metrics: dict, csv_metrics: dict):
        """
        Сравнить метрики из API и CSV.
        
        Args:
            api_metrics: Метрики из API
            csv_metrics: Метрики из CSV
        """
        print("\n" + "="*70)
        print("📊 СРАВНЕНИЕ ДАННЫХ API vs CSV")
        print("="*70)
        
        # Общие метрики
        print("\n🔢 Общие показатели:")
        self._compare_value("Артикулов", 
                           api_metrics.get("total_articles", 0),
                           csv_metrics.get("total_articles", 0))
        
        self._compare_value("Продаж (шт)", 
                           api_metrics.get("total_quantity", 0),
                           csv_metrics.get("total_quantity", 0))
        
        self._compare_value("К выплате (руб)", 
                           api_metrics.get("total_to_pay", 0),
                           csv_metrics.get("total_to_pay", 0))
        
        # Детальное сравнение по артикулам
        if "by_article" in api_metrics and "by_article" in csv_metrics:
            print("\n📦 Сравнение по артикулам:")
            
            api_articles = set(api_metrics["by_article"].keys())
            csv_articles = set(csv_metrics["by_article"].keys())
            
            common = api_articles & csv_articles
            only_api = api_articles - csv_articles
            only_csv = csv_articles - api_articles
            
            print(f"   Общих артикулов: {len(common)}")
            print(f"   Только в API: {len(only_api)}")
            print(f"   Только в CSV: {len(only_csv)}")
            
            if only_api:
                print(f"\n   ⚠️ Артикулы только в API: {list(only_api)[:5]}")
            
            if only_csv:
                print(f"\n   ⚠️ Артикулы только в CSV: {list(only_csv)[:5]}")
    
    def _compare_value(self, name: str, api_val, csv_val):
        """Сравнить одно значение."""
        diff = api_val - csv_val
        diff_pct = (diff / csv_val * 100) if csv_val != 0 else 0
        
        status = "✅" if abs(diff_pct) < 5 else "⚠️"
        
        print(f"\n{status} {name}:")
        print(f"   API: {api_val:,.2f}")
        print(f"   CSV: {csv_val:,.2f}")
        print(f"   Разница: {diff:+,.2f} ({diff_pct:+.1f}%)")
    
    def _safe_float(self, value):
        """Безопасное преобразование в float."""
        try:
            if pd.isna(value):
                return 0.0
            if isinstance(value, str):
                # Удаляем пробелы, запятые, символы валют
                value = value.replace(' ', '').replace(',', '.').replace('₽', '').replace('%', '')
            return float(value)
        except:
            return 0.0
    
    def save_comparison_report(self, api_metrics: dict, csv_metrics: dict, output_path: Path):
        """
        Сохранить отчёт о сравнении.
        
        Args:
            api_metrics: Метрики из API
            csv_metrics: Метрики из CSV
            output_path: Путь для сохранения
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "api_metrics": api_metrics,
            "csv_metrics": csv_metrics,
            "comparison": {
                "articles_diff": api_metrics.get("total_articles", 0) - csv_metrics.get("total_articles", 0),
                "quantity_diff": api_metrics.get("total_quantity", 0) - csv_metrics.get("total_quantity", 0),
                "to_pay_diff": api_metrics.get("total_to_pay", 0) - csv_metrics.get("total_to_pay", 0),
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Отчёт сохранён: {output_path}")


def parse_arguments():
    """Парсинг аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description='Сравнение данных из WB API с CSV отчётом',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  # Базовое (последние 7 дней)
  python compare_api_vs_csv.py
  
  # С указанием периода
  python compare_api_vs_csv.py --from 2025-10-20 --to 2025-10-26
  
  # С указанием CSV файла
  python compare_api_vs_csv.py --csv data_samples/my_report.csv
  
  # Полная команда
  python compare_api_vs_csv.py --from 2025-10-20 --to 2025-10-26 --csv data_samples/43-nedelia.csv
        """
    )
    
    parser.add_argument(
        '--from', '-f',
        dest='date_from',
        type=str,
        help='Дата начала периода (YYYY-MM-DD), по умолчанию 7 дней назад'
    )
    
    parser.add_argument(
        '--to', '-t',
        dest='date_to',
        type=str,
        help='Дата окончания периода (YYYY-MM-DD), по умолчанию сегодня'
    )
    
    parser.add_argument(
        '--csv', '-c',
        dest='csv_file',
        type=str,
        default='data_samples/43-nedelia-2-List1.csv',
        help='Путь к CSV файлу WB (по умолчанию: data_samples/43-nedelia-2-List1.csv)'
    )
    
    return parser.parse_args()


def main():
    """Главная функция."""
    args = parse_arguments()
    
    print("\n" + "="*70)
    print("📊 СРАВНЕНИЕ ДАННЫХ WB API vs CSV")
    print("="*70)
    
    # Загружаем переменные окружения
    load_dotenv()
    
    api_key = os.getenv("WB_API_KEY")
    if not api_key:
        print("\n❌ Ошибка: WB_API_KEY не найден в .env файле")
        print("💡 Создайте .env файл и добавьте: WB_API_KEY=ваш_ключ\n")
        return
    
    # Создаём компаратор
    comparator = DataComparator(api_key)
    
    # Определяем период
    if args.date_from and args.date_to:
        # Используем указанные даты
        date_from = datetime.strptime(args.date_from, "%Y-%m-%d")
        date_to = datetime.strptime(args.date_to, "%Y-%m-%d")
    else:
        # По умолчанию последние 7 дней
        date_to = datetime.now()
        date_from = date_to - timedelta(days=7)
    
    date_from_str = date_from.strftime("%Y-%m-%dT00:00:00Z")
    date_to_str = date_to.strftime("%Y-%m-%dT23:59:59Z")
    
    # 1. Загружаем данные из API
    try:
        api_data = comparator.load_api_data(
            date_from=date_from_str,
            date_to=date_to_str,
            reports=["reportDetail"]  # Главный отчёт
        )
    except Exception as e:
        print(f"\n❌ Ошибка загрузки из API: {e}")
        print("💡 Проверьте API ключ и подождите 1-2 минуты (rate limit)\n")
        return
    
    # 2. Загружаем данные из CSV
    csv_path = Path(args.csv_file)
    
    if not csv_path.exists():
        print(f"\n⚠️ CSV файл не найден: {csv_path}")
        print("💡 Укажите корректный путь через --csv параметр")
        print(f"   Пример: python compare_api_vs_csv.py --csv data_samples/ваш_файл.csv\n")
        return
    
    try:
        csv_data = comparator.load_csv_data(csv_path)
    except Exception as e:
        print(f"\n❌ Ошибка загрузки CSV: {e}\n")
        return
    
    # 3. Рассчитываем метрики
    api_metrics = comparator.calculate_metrics_from_api(api_data)
    csv_metrics = comparator.calculate_metrics_from_csv(csv_data)
    
    # 4. Сравниваем
    comparator.compare_metrics(api_metrics, csv_metrics)
    
    # 5. Сохраняем отчёт
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    report_path = output_dir / f"comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    comparator.save_comparison_report(api_metrics, csv_metrics, report_path)
    
    print("\n" + "="*70)
    print("✅ СРАВНЕНИЕ ЗАВЕРШЕНО!")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Прервано пользователем\n")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}\n")
        import traceback
        traceback.print_exc()
