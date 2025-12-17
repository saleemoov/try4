#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🛠️ Helper Functions & Utilities
دوال مساعدة متقدمة
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import hashlib
import hmac
import base64

# ============================================================================
# أدوات التحويل والصيغ
# ============================================================================

class FormatUtils:
    """أدوات تنسيق البيانات"""
    
    @staticmethod
    def format_price(price: float, decimals: int = 8) -> str:
        """تنسيق السعر"""
        if price > 1:
            return f"${price:,.2f}"
        else:
            return f"${price:.{decimals}f}"
    
    @staticmethod
    def format_volume(volume: float) -> str:
        """تنسيق حجم التداول"""
        if volume >= 1_000_000_000:
            return f"${volume/1_000_000_000:.2f}B"
        elif volume >= 1_000_000:
            return f"${volume/1_000_000:.2f}M"
        elif volume >= 1_000:
            return f"${volume/1_000:.2f}K"
        else:
            return f"${volume:.2f}"
    
    @staticmethod
    def format_percentage(percent: float, decimals: int = 2) -> str:
        """تنسيق النسبة المئوية"""
        sign = "+" if percent >= 0 else ""
        emoji = "📈" if percent > 0 else "📉" if percent < 0 else "➡️"
        return f"{emoji} {sign}{percent:.{decimals}f}%"
    
    @staticmethod
    def format_time_remaining(seconds: int) -> str:
        """تنسيق الوقت المتبقي"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds//60}m {seconds%60}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    @staticmethod
    def format_signal_strength(strength: float) -> str:
        """تنسيق قوة الإشارة"""
        bars = "▰" * int(strength / 10)
        empty = "▱" * (10 - int(strength / 10))
        return f"{bars}{empty} {strength:.0f}%"

# ============================================================================
# أدوات التحليل الرياضية
# ============================================================================

class MathUtils:
    """أدوات حسابية للتحليل"""
    
    @staticmethod
    def calculate_percentage_change(old_value: float, new_value: float) -> float:
        """حساب النسبة المئوية للتغير"""
        if old_value == 0:
            return 0
        return ((new_value - old_value) / old_value) * 100
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """حساب RSI يدوياً"""
        if len(prices) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains[-period:]) / period if len(gains) >= period else 0
        avg_loss = sum(losses[-period:]) / period if len(losses) >= period else 0
        
        if avg_loss == 0:
            return 100 if avg_gain > 0 else 50
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_fibonacci_levels(high: float, low: float) -> Dict[str, float]:
        """حساب مستويات فيبوناتشي"""
        diff = high - low
        
        return {
            '0.0': low,
            '0.236': low + (diff * 0.236),
            '0.382': low + (diff * 0.382),
            '0.5': low + (diff * 0.5),
            '0.618': low + (diff * 0.618),
            '0.786': low + (diff * 0.786),
            '1.0': high,
            '1.27': high + (diff * 0.27),
            '1.618': high + (diff * 0.618)
        }
    
    @staticmethod
    def calculate_average_true_range(highs: List[float], lows: List[float], 
                                     closes: List[float], period: int = 14) -> float:
        """حساب متوسط النطاق الحقيقي"""
        if len(highs) < period:
            return 0
        
        true_ranges = []
        
        for i in range(len(highs)):
            if i == 0:
                tr = highs[i] - lows[i]
            else:
                h_l = highs[i] - lows[i]
                h_c = abs(highs[i] - closes[i-1])
                l_c = abs(lows[i] - closes[i-1])
                tr = max(h_l, h_c, l_c)
            
            true_ranges.append(tr)
        
        atr = sum(true_ranges[-period:]) / period
        return atr

# ============================================================================
# أدوات إدارة الأوقات
# ============================================================================

class TimeUtils:
    """أدوات التعامل مع الأوقات"""
    
    @staticmethod
    def get_current_timestamp() -> float:
        """الحصول على الوقت الحالي (Unix timestamp)"""
        return datetime.now().timestamp()
    
    @staticmethod
    def get_hours_difference(timestamp1: float, timestamp2: float) -> float:
        """حساب الفرق بالساعات بين وقتين"""
        return abs(timestamp2 - timestamp1) / 3600
    
    @staticmethod
    def is_within_last_n_hours(timestamp: float, n_hours: int) -> bool:
        """التحقق من أن الوقت ضمن آخر N ساعة"""
        current_timestamp = TimeUtils.get_current_timestamp()
        hours_diff = TimeUtils.get_hours_difference(timestamp, current_timestamp)
        return hours_diff <= n_hours
    
    @staticmethod
    def get_market_session() -> str:
        """تحديد جلسة السوق الحالية (UTC)"""
        hour = datetime.utcnow().hour
        
        if 0 <= hour < 8:
            return "Asian Session"
        elif 8 <= hour < 16:
            return "European Session"
        elif 16 <= hour < 24:
            return "US Session"
        else:
            return "Unknown"
    
    @staticmethod
    def get_day_name(timestamp: float = None) -> str:
        """الحصول على اسم اليوم"""
        if timestamp is None:
            dt = datetime.now()
        else:
            dt = datetime.fromtimestamp(timestamp)
        
        days = ['الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']
        return days[dt.weekday()]

# ============================================================================
# أدوات إدارة الملفات
# ============================================================================

class FileUtils:
    """أدوات التعامل مع الملفات"""
    
    @staticmethod
    def save_json(data: Dict, filename: str, protect: bool = False):
        """حفظ البيانات في ملف JSON"""
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            if protect:
                os.chmod(filename, 0o600)
            
            return True
        except Exception as e:
            print(f"❌ خطأ في حفظ الملف: {e}")
            return False
    
    @staticmethod
    def load_json(filename: str) -> Optional[Dict]:
        """تحميل البيانات من ملف JSON"""
        if not os.path.exists(filename):
            return None
        
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ خطأ في تحميل الملف: {e}")
            return None
    
    @staticmethod
    def append_to_file(filename: str, content: str):
        """إضافة محتوى إلى ملف"""
        try:
            with open(filename, 'a') as f:
                f.write(content + '\n')
            return True
        except Exception as e:
            print(f"❌ خطأ في الكتابة: {e}")
            return False
    
    @staticmethod
    def get_file_size_mb(filename: str) -> float:
        """الحصول على حجم الملف بالميجابايت"""
        if not os.path.exists(filename):
            return 0
        return os.path.getsize(filename) / (1024 * 1024)
    
    @staticmethod
    def rotate_log_file(filename: str, max_size_mb: int = 50):
        """تدوير ملف السجل عند الوصول للحد الأقصى"""
        if FileUtils.get_file_size_mb(filename) > max_size_mb:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_filename = f"{filename}.{timestamp}"
            os.rename(filename, new_filename)
            return True
        return False

# ============================================================================
# أدوات التشفير والأمان
# ============================================================================

class SecurityUtils:
    """أدوات الأمان والتشفير"""
    
    @staticmethod
    def hash_string(text: str, algorithm: str = 'sha256') -> str:
        """تشفير نص"""
        if algorithm == 'sha256':
            return hashlib.sha256(text.encode()).hexdigest()
        elif algorithm == 'sha512':
            return hashlib.sha512(text.encode()).hexdigest()
        else:
            return hashlib.md5(text.encode()).hexdigest()
    
    @staticmethod
    def verify_hmac(message: str, secret: str, signature: str) -> bool:
        """التحقق من التوقيع HMAC"""
        computed_sig = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return computed_sig == signature
    
    @staticmethod
    def mask_sensitive_data(data: str, show_chars: int = 4) -> str:
        """إخفاء البيانات الحساسة"""
        if len(data) <= show_chars:
            return "*" * len(data)
        
        return data[:show_chars] + "*" * (len(data) - show_chars)
    
    @staticmethod
    def generate_random_string(length: int = 16) -> str:
        """توليد نص عشوائي"""
        import secrets
        import string
        
        chars = string.ascii_letters + string.digits
        return ''.join(secrets.choice(chars) for _ in range(length))

# ============================================================================
# أدوات التحقق والتحديث
# ============================================================================

class ValidationUtils:
    """أدوات التحقق من البيانات"""
    
    @staticmethod
    def is_valid_api_key(api_key: str) -> bool:
        """التحقق من صحة مفتاح API"""
        if not api_key or len(api_key) < 10:
            return False
        
        # يجب أن يحتوي على أحرف وأرقام
        has_letters = any(c.isalpha() for c in api_key)
        has_digits = any(c.isdigit() for c in api_key)
        
        return has_letters and has_digits
    
    @staticmethod
    def is_valid_symbol(symbol: str) -> bool:
        """التحقق من صحة رمز العملة"""
        if not symbol or len(symbol) < 3:
            return False
        
        # يجب أن يكون بصيغة XXX/USDT أو XXXUSDT
        if '/' in symbol:
            parts = symbol.split('/')
            return len(parts) == 2 and len(parts[0]) >= 1 and len(parts[1]) >= 1
        else:
            return len(symbol) >= 4 and symbol.endswith(('USDT', 'BTC', 'ETH'))
    
    @staticmethod
    def is_valid_percentage(value: float) -> bool:
        """التحقق من أن القيمة نسبة مئوية صحيحة"""
        return -100 <= value <= 1000  # من -100% إلى 1000%
    
    @staticmethod
    def is_valid_price(price: float) -> bool:
        """التحقق من صحة السعر"""
        return price > 0 and price < 1_000_000

# ============================================================================
# أدوات الإحصاء والتحليل
# ============================================================================

class StatisticsUtils:
    """أدوات إحصائية"""
    
    @staticmethod
    def calculate_mean(values: List[float]) -> float:
        """حساب المتوسط الحسابي"""
        if not values:
            return 0
        return sum(values) / len(values)
    
    @staticmethod
    def calculate_std_deviation(values: List[float]) -> float:
        """حساب الانحراف المعياري"""
        if len(values) < 2:
            return 0
        
        mean = StatisticsUtils.calculate_mean(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    @staticmethod
    def calculate_win_rate(wins: int, losses: int) -> float:
        """حساب معدل الفوز"""
        total = wins + losses
        if total == 0:
            return 0
        return (wins / total) * 100
    
    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
        """حساب نسبة شارب (Sharpe Ratio)"""
        if not returns or len(returns) < 2:
            return 0
        
        mean_return = StatisticsUtils.calculate_mean(returns)
        std_dev = StatisticsUtils.calculate_std_deviation(returns)
        
        if std_dev == 0:
            return 0
        
        # نسبة شارب = (العائد - معدل خالي من المخاطر) / الانحراف المعياري
        return (mean_return - risk_free_rate) / std_dev
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: List[float]) -> float:
        """حساب أقصى انخفاض (Maximum Drawdown)"""
        if not equity_curve or len(equity_curve) < 2:
            return 0
        
        max_equity = equity_curve[0]
        max_drawdown = 0
        
        for equity in equity_curve:
            if equity > max_equity:
                max_equity = equity
            
            drawdown = (max_equity - equity) / max_equity
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return max_drawdown * 100

# ============================================================================
# أدوات الترجمة والدعم اللغوي
# ============================================================================

class LanguageUtils:
    """أدوات دعم اللغات"""
    
    TRANSLATIONS = {
        'BUY': {
            'en': '🟢 BUY',
            'ar': '🟢 شراء'
        },
        'SELL': {
            'en': '🔴 SELL',
            'ar': '🔴 بيع'
        },
        'NEUTRAL': {
            'en': '⚪ NEUTRAL',
            'ar': '⚪ محايد'
        },
        'STRONG': {
            'en': '💪 STRONG',
            'ar': '💪 قوية'
        },
        'WEAK': {
            'en': '⚠️ WEAK',
            'ar': '⚠️ ضعيفة'
        }
    }
    
    @staticmethod
    def translate(key: str, language: str = 'ar') -> str:
        """ترجمة نص"""
        if key in LanguageUtils.TRANSLATIONS:
            return LanguageUtils.TRANSLATIONS[key].get(language, key)
        return key
    
    @staticmethod
    def get_emoji_for_signal(signal_type: str) -> str:
        """الحصول على emoji مناسب للإشارة"""
        emojis = {
            'BUY': '🟢',
            'SELL': '🔴',
            'NEUTRAL': '⚪',
            'STRONG_BUY': '🟢💪',
            'STRONG_SELL': '🔴💪',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'SUCCESS': '✅'
        }
        return emojis.get(signal_type, '❓')

# ============================================================================
# اختبار الأدوات
# ============================================================================

if __name__ == "__main__":
    print("🧪 اختبار الأدوات المساعدة\n")
    
    # اختبار FormatUtils
    print("📊 اختبار تنسيق البيانات:")
    print(f"  السعر: {FormatUtils.format_price(0.00005432)}")
    print(f"  الحجم: {FormatUtils.format_volume(5500000)}")
    print(f"  النسبة: {FormatUtils.format_percentage(5.5)}")
    print(f"  قوة الإشارة: {FormatUtils.format_signal_strength(75)}")
    
    # اختبار MathUtils
    print("\n🔢 اختبار الحسابات:")
    prices = [100, 102, 101, 103, 105, 104, 106]
    print(f"  التغير: {MathUtils.calculate_percentage_change(100, 106):.2f}%")
    
    # اختبار TimeUtils
    print("\n⏰ اختبار الأوقات:")
    print(f"  جلسة السوق: {TimeUtils.get_market_session()}")
    print(f"  اليوم: {TimeUtils.get_day_name()}")
    
    # اختبار StatisticsUtils
    print("\n📈 اختبار الإحصاء:")
    values = [1.0, 1.5, 2.0, 2.5, 3.0]
    print(f"  المتوسط: {StatisticsUtils.calculate_mean(values):.2f}")
    print(f"  معدل الفوز: {StatisticsUtils.calculate_win_rate(7, 3):.1f}%")
    
    print("\n✅ انتهى الاختبار")
