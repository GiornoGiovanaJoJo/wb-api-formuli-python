"""Financial metrics calculator."""
from models.product import Product, ProductMetrics

class Calculator:
    """Калькулятор финансовых метрик."""
    
    @staticmethod
    def calculate_cogs(product: Product) -> float:
        """
        Рассчитать себестоимость проданного товара (COGS).
        
        Формула: COGS = (Продажи - Возвраты - Самовыкупы - Раздачи) × Себестоимость/ед
        """
        net_sold = (
            product.sales 
            - product.returns 
            - product.manual_data.self_purchase_count
            - product.manual_data.giveaway_count
        )
        
        # Себестоимость проданного товара
        cogs = net_sold * product.manual_data.cost_per_unit
        
        # Добавляем себестоимость раздач
        cogs += product.manual_data.giveaway_cost
        
        return cogs
    
    @staticmethod
    def calculate_gross_profit(product: Product, cogs: float) -> float:
        """
        Рассчитать валовую прибыль.
        
        Формула: Валовая прибыль = Выручка после СПП - COGS
        """
        return product.sales_amount_after_spp - cogs
    
    @staticmethod
    def calculate_total_expenses(product: Product) -> float:
        """
        Рассчитать все расходы WB.
        
        Формула: Расходы = Логистика + Хранение + Штрафы + Приёмка + Комиссия + ДРР + Маркетинг
        """
        return (
            product.logistics_cost
            + product.storage_cost
            + product.penalty_cost
            + product.acceptance_cost
            + product.commission_with_spp
            + product.drr_cost
            + product.manual_data.marketing_cost
            - product.surcharges  # Доплаты вычитаются
        )
    
    @staticmethod
    def calculate_net_profit(gross_profit: float, total_expenses: float) -> float:
        """
        Рассчитать чистую прибыль.
        
        Формула: Чистая прибыль = Валовая прибыль - Все расходы
        """
        return gross_profit - total_expenses
    
    @staticmethod
    def calculate_profit_margin(gross_profit: float, revenue: float) -> float:
        """
        Рассчитать маржинальность (%).
        
        Формула: Маржа = (Валовая прибыль / Выручка) × 100
        """
        if revenue == 0:
            return 0.0
        return (gross_profit / revenue) * 100
    
    @staticmethod
    def calculate_roi(net_profit: float, cogs: float) -> float:
        """
        Рассчитать ROI (%).
        
        Формула: ROI = (Чистая прибыль / COGS) × 100
        """
        if cogs == 0:
            return 0.0
        return (net_profit / cogs) * 100
    
    @staticmethod
    def calculate_avg_check(revenue: float, sales: int) -> float:
        """
        Рассчитать средний чек.
        
        Формула: Средний чек = Выручка / Продажи
        """
        if sales == 0:
            return 0.0
        return revenue / sales
    
    def calculate_all_metrics(self, product: Product) -> ProductMetrics:
        """
        Рассчитать все метрики для товара.
        """
        cogs = self.calculate_cogs(product)
        gross_profit = self.calculate_gross_profit(product, cogs)
        total_expenses = self.calculate_total_expenses(product)
        net_profit = self.calculate_net_profit(gross_profit, total_expenses)
        profit_margin = self.calculate_profit_margin(gross_profit, product.sales_amount_after_spp)
        roi = self.calculate_roi(net_profit, cogs)
        avg_check = self.calculate_avg_check(product.sales_amount_after_spp, product.sales)
        
        return ProductMetrics(
            product=product,
            cogs=cogs,
            gross_profit=gross_profit,
            total_expenses=total_expenses,
            net_profit=net_profit,
            profit_margin_percent=profit_margin,
            roi_percent=roi,
            avg_check=avg_check
        )