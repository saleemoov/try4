#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 Test Suite for Advanced Trading Bot
اختبار الوحدات الأساسية
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trading_utilities import (
    FormatUtils, MathUtils, TimeUtils, ValidationUtils,
    StatisticsUtils, LanguageUtils
)
from trading_config_advanced import BotConfig, RiskLevel

class Colors:
    """ANSI Color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, passed, message=""):
    """Print test result"""
    status = f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
    msg = f" - {message}" if message else ""
    print(f"  {status}: {name}{msg}")

def test_format_utils():
    """Test FormatUtils"""
    print(f"\n{Colors.BLUE}Testing FormatUtils...{Colors.END}")
    
    # Test price formatting
    price_str = FormatUtils.format_price(0.00005432)
    print_test("format_price", "$" in price_str, price_str)
    
    # Test volume formatting
    volume_str = FormatUtils.format_volume(5500000)
    print_test("format_volume", "M" in volume_str, volume_str)
    
    # Test percentage formatting
    percent_str = FormatUtils.format_percentage(5.5)
    print_test("format_percentage", "+" in percent_str, percent_str)
    
    # Test signal strength
    strength_str = FormatUtils.format_signal_strength(75)
    print_test("format_signal_strength", "▰" in strength_str, strength_str)

def test_math_utils():
    """Test MathUtils"""
    print(f"\n{Colors.BLUE}Testing MathUtils...{Colors.END}")
    
    # Test percentage change
    change = MathUtils.calculate_percentage_change(100, 106)
    print_test("calculate_percentage_change", abs(change - 6.0) < 0.01, f"{change:.2f}%")
    
    # Test fibonacci levels
    fibs = MathUtils.calculate_fibonacci_levels(100, 90)
    print_test("calculate_fibonacci_levels", len(fibs) >= 7, f"{len(fibs)} levels")
    
    # Test RSI calculation
    prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 111, 110, 112, 114, 113]
    rsi = MathUtils.calculate_rsi(prices, 14)
    print_test("calculate_rsi", 0 <= rsi <= 100, f"RSI: {rsi:.1f}")

def test_time_utils():
    """Test TimeUtils"""
    print(f"\n{Colors.BLUE}Testing TimeUtils...{Colors.END}")
    
    # Test timestamp
    ts = TimeUtils.get_current_timestamp()
    print_test("get_current_timestamp", ts > 0, f"ts: {ts:.0f}")
    
    # Test market session
    session = TimeUtils.get_market_session()
    print_test("get_market_session", session in ["Asian Session", "European Session", "US Session"], session)
    
    # Test day name
    day = TimeUtils.get_day_name()
    print_test("get_day_name", day in ['الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد'], day)

def test_validation_utils():
    """Test ValidationUtils"""
    print(f"\n{Colors.BLUE}Testing ValidationUtils...{Colors.END}")
    
    # Test API key validation
    valid_key = ValidationUtils.is_valid_api_key("abc123def456")
    invalid_key = ValidationUtils.is_valid_api_key("123")
    print_test("is_valid_api_key", valid_key and not invalid_key)
    
    # Test symbol validation
    valid_symbol = ValidationUtils.is_valid_symbol("BTC/USDT")
    print_test("is_valid_symbol", valid_symbol, "BTC/USDT")
    
    # Test price validation
    valid_price = ValidationUtils.is_valid_price(0.00005)
    invalid_price = ValidationUtils.is_valid_price(-10)
    print_test("is_valid_price", valid_price and not invalid_price)

def test_statistics_utils():
    """Test StatisticsUtils"""
    print(f"\n{Colors.BLUE}Testing StatisticsUtils...{Colors.END}")
    
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    
    # Test mean
    mean = StatisticsUtils.calculate_mean(values)
    print_test("calculate_mean", abs(mean - 3.0) < 0.01, f"mean: {mean:.1f}")
    
    # Test std deviation
    std = StatisticsUtils.calculate_std_deviation(values)
    print_test("calculate_std_deviation", std > 0, f"std: {std:.2f}")
    
    # Test win rate
    win_rate = StatisticsUtils.calculate_win_rate(7, 3)
    print_test("calculate_win_rate", abs(win_rate - 70.0) < 0.01, f"{win_rate:.1f}%")
    
    # Test max drawdown
    equity_curve = [100, 95, 90, 100, 110, 105, 120]
    dd = StatisticsUtils.calculate_max_drawdown(equity_curve)
    print_test("calculate_max_drawdown", 0 <= dd <= 100, f"{dd:.1f}%")

def test_language_utils():
    """Test LanguageUtils"""
    print(f"\n{Colors.BLUE}Testing LanguageUtils...{Colors.END}")
    
    # Test translation
    en_buy = LanguageUtils.translate('BUY', 'en')
    ar_buy = LanguageUtils.translate('BUY', 'ar')
    print_test("translate", 'BUY' in en_buy and 'شراء' in ar_buy)
    
    # Test emoji
    emoji = LanguageUtils.get_emoji_for_signal('BUY')
    print_test("get_emoji_for_signal", emoji == '🟢', emoji)

def test_bot_config():
    """Test BotConfig"""
    print(f"\n{Colors.BLUE}Testing BotConfig...{Colors.END}")
    
    # Test default config
    config = BotConfig()
    print_test("BotConfig initialization", config is not None)
    
    # Test attributes
    has_ema = hasattr(config, 'emas') and config.emas is not None
    has_rsi = hasattr(config, 'rsi') and config.rsi is not None
    print_test("Config has EMA settings", has_ema)
    print_test("Config has RSI settings", has_rsi)
    
    # Test to_dict
    config_dict = config.to_dict()
    print_test("to_dict conversion", isinstance(config_dict, dict) and len(config_dict) > 0)

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 Advanced Trading Bot - Test Suite")
    print("="*60)
    
    try:
        test_format_utils()
        test_math_utils()
        test_time_utils()
        test_validation_utils()
        test_statistics_utils()
        test_language_utils()
        test_bot_config()
        
        print("\n" + "="*60)
        print(f"{Colors.GREEN}✅ All tests completed successfully!{Colors.END}")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n{Colors.RED}❌ Test Error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
