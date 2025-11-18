"""Export results to files."""
import json
import csv
from typing import List, Dict
from pathlib import Path
from models.product import ProductMetrics

class Exporter:
    """Экспортер результатов."""
    
    @staticmethod
    def export_to_json(metrics: List[ProductMetrics], output_path: Path) -> None:
        """
        Экспортировать результаты в JSON.
        
        Args:
            metrics: Список метрик
            output_path: Путь к выходному файлу
        """
        data = [m.to_dict() for m in metrics]
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\u2705 Результаты экспортированы в: {output_path}")
    
    @staticmethod
    def export_to_csv(metrics: List[ProductMetrics], output_path: Path) -> None:
        """
        Экспортировать результаты в CSV.
        
        Args:
            metrics: Список метрик
            output_path: Путь к выходному файлу
        """
        if not metrics:
            print("⚠️  Нет данных для экспорта")
            return
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = [m.to_dict() for m in metrics]
        fieldnames = data[0].keys()
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"\u2705 Результаты экспортированы в: {output_path}")
    
    @staticmethod
    def print_summary(metrics: List[ProductMetrics]) -> None:
        """
        Вывести сводку по товарам.
        
        Args:
            metrics: Список метрик
        """
        if not metrics:
            print("⚠️  Нет данных для отображения")
            return
        
        print("\n" + "="*80)
        print("📊 СВОДКА ПО ТОВАРАМ")
        print("="*80)
        
        total_revenue = sum(m.product.sales_amount_after_spp for m in metrics)
        total_cogs = sum(m.cogs for m in metrics)
        total_gross_profit = sum(m.gross_profit for m in metrics)
        total_net_profit = sum(m.net_profit for m in metrics)
        
        print(f"\n💰 ОБЩИЕ ПОКАЗАТЕЛИ:")
        print(f"   Выручка: {total_revenue:,.2f} руб")
        print(f"   COGS: {total_cogs:,.2f} руб")
        print(f"   Валовая прибыль: {total_gross_profit:,.2f} руб")
        print(f"   Чистая прибыль: {total_net_profit:,.2f} руб")
        
        # Сортируем по чистой прибыли
        sorted_metrics = sorted(metrics, key=lambda m: m.net_profit, reverse=True)
        
        print(f"\n🏆 ТОП-3 ПРИБЫЛЬНЫХ:")
        for i, m in enumerate(sorted_metrics[:3], 1):
            print(f"   {i}. {m.product.product_name or f'nm_id {m.product.nm_id}'}")
            print(f"      Прибыль: {m.net_profit:,.2f} руб | Маржа: {m.profit_margin_percent:.1f}% | ROI: {m.roi_percent:.1f}%")
        
        print(f"\n📉 ТОП-3 УБЫТОЧНЫХ:")
        for i, m in enumerate(sorted_metrics[-3:][::-1], 1):
            print(f"   {i}. {m.product.product_name or f'nm_id {m.product.nm_id}'}")
            print(f"      Прибыль: {m.net_profit:,.2f} руб | Маржа: {m.profit_margin_percent:.1f}% | ROI: {m.roi_percent:.1f}%")
        
        print("\n" + "="*80)