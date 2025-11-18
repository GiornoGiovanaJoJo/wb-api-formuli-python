"""Product data models."""
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ManualInputData:
    """Данные для ручного ввода."""
    cost_per_unit: float = 0.0  # Себестоимость на единицу
    self_purchase_count: int = 0  # Количество самовыкупов
    self_purchase_cost: float = 0.0  # Сумма самовыкупов
    giveaway_count: int = 0  # Количество раздач
    giveaway_cost: float = 0.0  # Себестоимость раздач
    marketing_cost: float = 0.0  # Дополнительные маркетинговые расходы

@dataclass
class Product:
    """Модель товара с данными WB."""
    # Идентификация
    nm_id: int
    product_name: str = ""
    
    # Объёмы (шт)
    deliveries: int = 0
    sales: int = 0
    returns: int = 0
    refusals: int = 0
    
    # Финансы (руб)
    sales_amount_before_spp: float = 0.0  # Выручка до СПП
    sales_amount_after_spp: float = 0.0  # Выручка после СПП
    returns_amount: float = 0.0  # Сумма возвратов
    
    # Расходы WB (руб)
    logistics_cost: float = 0.0  # Логистика
    storage_cost: float = 0.0  # Хранение
    acceptance_cost: float = 0.0  # Приёмка
    penalty_cost: float = 0.0  # Штрафы
    surcharges: float = 0.0  # Доплаты
    commission_with_spp: float = 0.0  # Комиссия с СПП
    commission_without_spp: float = 0.0  # Комиссия без СПП
    drr_cost: float = 0.0  # Реклама (ДРР)
    
    # Ручной ввод
    manual_data: ManualInputData = field(default_factory=ManualInputData)
    
    @property
    def net_sales(self) -> int:
        """Чистые продажи (шт)."""
        return self.sales - self.returns - self.manual_data.self_purchase_count
    
    @property
    def percent_refusals(self) -> float:
        """Процент отказов."""
        if self.deliveries == 0:
            return 0.0
        return (self.refusals / self.deliveries) * 100
    
    @property
    def percent_returns(self) -> float:
        """Процент возвратов."""
        if self.sales == 0:
            return 0.0
        return (self.returns / self.sales) * 100

@dataclass
class ProductMetrics:
    """Рассчитанные метрики товара."""
    product: Product
    
    # Рассчитываемые показатели
    cogs: float = 0.0  # Себестоимость проданного товара
    gross_profit: float = 0.0  # Валовая прибыль
    total_expenses: float = 0.0  # Все расходы
    net_profit: float = 0.0  # Чистая прибыль
    profit_margin_percent: float = 0.0  # Маржинальность (%)
    roi_percent: float = 0.0  # ROI (%)
    avg_check: float = 0.0  # Средний чек
    
    def to_dict(self) -> dict:
        """Конвертировать в словарь."""
        return {
            'nm_id': self.product.nm_id,
            'product_name': self.product.product_name,
            'sales': self.product.sales,
            'returns': self.product.returns,
            'net_sales': self.product.net_sales,
            'revenue': self.product.sales_amount_after_spp,
            'cogs': self.cogs,
            'gross_profit': self.gross_profit,
            'total_expenses': self.total_expenses,
            'net_profit': self.net_profit,
            'profit_margin_percent': round(self.profit_margin_percent, 2),
            'roi_percent': round(self.roi_percent, 2),
            'avg_check': round(self.avg_check, 2)
        }