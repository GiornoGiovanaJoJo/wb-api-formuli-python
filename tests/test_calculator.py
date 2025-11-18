"""Tests for Calculator."""
import pytest
from models.product import Product, ManualInputData
from analyzer.calculator import Calculator

def test_calculate_cogs():
    """Test COGS calculation."""
    product = Product(
        nm_id=123,
        sales=100,
        returns=10,
        manual_data=ManualInputData(
            cost_per_unit=100,
            self_purchase_count=5,
            giveaway_count=5
        )
    )
    
    calc = Calculator()
    cogs = calc.calculate_cogs(product)
    
    # (100 - 10 - 5 - 5) * 100 = 8000
    assert cogs == 8000

def test_calculate_gross_profit():
    """Test gross profit calculation."""
    product = Product(
        nm_id=123,
        sales_amount_after_spp=10000
    )
    
    calc = Calculator()
    gross_profit = calc.calculate_gross_profit(product, cogs=6000)
    
    # 10000 - 6000 = 4000
    assert gross_profit == 4000

def test_calculate_profit_margin():
    """Test profit margin calculation."""
    calc = Calculator()
    margin = calc.calculate_profit_margin(gross_profit=4000, revenue=10000)
    
    # (4000 / 10000) * 100 = 40%
    assert margin == 40.0

def test_calculate_roi():
    """Test ROI calculation."""
    calc = Calculator()
    roi = calc.calculate_roi(net_profit=2000, cogs=6000)
    
    # (2000 / 6000) * 100 = 33.33%
    assert abs(roi - 33.33) < 0.01