"""Interactive prompts for CLI."""
from typing import Optional
from models.product import ManualInputData

class Prompts:
    """Интерактивные запросы для CLI."""
    
    @staticmethod
    def get_float_input(prompt: str, default: float = 0.0) -> float:
        """Получить float значение от пользователя."""
        while True:
            try:
                value = input(f"{prompt} [{default}]: ").strip()
                return float(value) if value else default
            except ValueError:
                print("❌ Неверное значение. Попробуйте снова.")
    
    @staticmethod
    def get_int_input(prompt: str, default: int = 0) -> int:
        """Получить int значение от пользователя."""
        while True:
            try:
                value = input(f"{prompt} [{default}]: ").strip()
                return int(value) if value else default
            except ValueError:
                print("❌ Неверное значение. Попробуйте снова.")
    
    @staticmethod
    def get_string_input(prompt: str, default: str = "") -> str:
        """Получить строку от пользователя."""
        value = input(f"{prompt} [{default}]: ").strip()
        return value if value else default
    
    @classmethod
    def get_manual_input_data(cls) -> ManualInputData:
        """
        Получить данные ручного ввода от пользователя.
        """
        print("\n📝 РУЧНОЙ ВВОД ДАННЫХ:")
        print("-" * 50)
        
        cost_per_unit = cls.get_float_input("Себестоимость на единицу (руб)")
        
        self_purchase_count = cls.get_int_input("Количество самовыкупов (шт)")
        self_purchase_cost = self_purchase_count * cost_per_unit if self_purchase_count > 0 else 0
        
        giveaway_count = cls.get_int_input("Количество раздач (шт)")
        giveaway_cost = giveaway_count * cost_per_unit if giveaway_count > 0 else 0
        
        marketing_cost = cls.get_float_input("Доп. маркетинговые расходы (руб)")
        
        return ManualInputData(
            cost_per_unit=cost_per_unit,
            self_purchase_count=self_purchase_count,
            self_purchase_cost=self_purchase_cost,
            giveaway_count=giveaway_count,
            giveaway_cost=giveaway_cost,
            marketing_cost=marketing_cost
        )
    
    @staticmethod
    def display_menu() -> str:
        """Отобразить главное меню."""
        print("\n" + "="*60)
        print("📈 WB ANALYTICS - ГЛАВНОЕ МЕНЮ")
        print("="*60)
        print("\n1️⃣  Загрузить данные из WB API")
        print("2️⃣  Загрузить данные из CSV")
        print("3️⃣  Загрузить данные из JSON")
        print("4️⃣  Выйти")
        
        return input("\nВыберите опцию [1-4]: ").strip()