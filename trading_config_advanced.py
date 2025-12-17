#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚙️ Advanced Configuration Module
إدارة متقدمة لإعدادات البوت
"""

from dataclasses import dataclass
from typing import Dict, List
from enum import Enum

# ============================================================================
# تعريفات الإشارات والحالات
# ============================================================================

class SignalType(Enum):
    """أنواع الإشارات"""
    BUY = "BUY"
    SELL = "SELL"
    NEUTRAL = "NEUTRAL"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"

class TimeFrame(Enum):
    """الأطر الزمنية المدعومة"""
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    MINUTE_30 = "30m"
    HOUR_1 = "1h"
    HOUR_4 = "4h"
    HOUR_8 = "8h"
    DAILY = "1d"
    WEEKLY = "1w"

class RiskLevel(Enum):
    """مستويات المخاطرة"""
    CONSERVATIVE = "CONSERVATIVE"    # 0.5-1%
    MODERATE = "MODERATE"            # 1-2%
    AGGRESSIVE = "AGGRESSIVE"        # 2-5%
    VERY_AGGRESSIVE = "VERY_AGGRESSIVE"  # 5-10%

# ============================================================================
# إعدادات المؤشرات الفنية
# ============================================================================

@dataclass
class EMAsConfig:
    """إعدادات المتوسطات المتحركة الأسية"""
    short_period: int = 5         # EMA قصير الأجل
    medium_period: int = 8        # EMA متوسط الأجل
    long_period: int = 13         # EMA طويل الأجل
    
    # إعدادات الوزن
    weight_alignment: float = 0.25  # وزن ترتيب EMA
    weight_price_distance: float = 0.10  # وزن بعد السعر عن EMA

@dataclass
class RSIConfig:
    """إعدادات مؤشر القوة النسبية"""
    period: int = 14
    overbought_level: int = 70      # مستوى الإفراط في الشراء
    oversold_level: int = 30        # مستوى الإفراط في البيع
    
    weight_oversold: float = 0.20   # وزن إشارة البيع الزائد
    weight_overbought: float = 0.20 # وزن إشارة الشراء الزائد

@dataclass
class MACDConfig:
    """إعدادات MACD"""
    fast_ema: int = 12      # EMA السريعة
    slow_ema: int = 26      # EMA البطيئة
    signal_period: int = 9  # فترة خط الإشارة
    
    weight_crossover: float = 0.25   # وزن التقاطعات
    weight_histogram: float = 0.15   # وزن الرسم البياني

@dataclass
class SupportResistanceConfig:
    """إعدادات مستويات الدعم والمقاومة"""
    lookback_periods: int = 100  # عدد الشموع للنظر للخلف
    
    # مستويات فيبوناتشي المهمة
    fibonacci_levels: List[float] = None
    
    weight_exact: float = 0.20   # وزن التقاطع الدقيق
    weight_proximity: float = 0.15  # وزن القرب من المستوى

@dataclass
class TrendConfig:
    """إعدادات تحليل الاتجاه"""
    timeframe: TimeFrame = TimeFrame.HOUR_4
    min_bars: int = 20              # الحد الأدنى للشموع للتأكد
    
    weight_trend: float = 0.15  # وزن اتجاه الـ 4 ساعات

# ============================================================================
# إعدادات التداول والربح
# ============================================================================

@dataclass
class ProfitTargetConfig:
    """إعدادات أهداف الربح"""
    target_min_percent: float = 2.0   # الحد الأدنى 2%
    target_max_percent: float = 7.0   # الحد الأقصى 7%
    
    # أهداف متعددة المستويات
    target_1_percent: float = 3.0     # الهدف الأول
    target_2_percent: float = 5.0     # الهدف الثاني
    target_3_percent: float = 7.0     # الهدف الثالث (اختياري)
    
    # تعديل بناءً على قوة الإشارة
    strength_adjustment: bool = True  # تعديل الأهداف حسب القوة
    strength_multiplier: float = 0.08 # معامل التعديل

@dataclass
class StopLossConfig:
    """إعدادات إيقاف الخسارة"""
    stop_loss_percent: float = 2.0    # 2% أقل من أقل نقطة دعم
    trailing_stop: bool = True         # تحريك الحد الثابت
    trailing_percentage: float = 1.0   # نسبة التحريك
    
    # عدم وضع Stop في مناطق معينة
    avoid_gap_risk: bool = True
    gap_percent: float = 3.0

@dataclass
class PositionSizeConfig:
    """إعدادات حجم المركز"""
    position_size_usdt: float = 100.0  # بالدولار الأمريكي
    max_concurrent_positions: int = 5  # الحد الأقصى للمراكز المتزامنة
    percentage_per_coin: float = 20.0  # نسبة من رأس المال لكل عملة
    
    # تعديل حسب قوة الإشارة
    adjust_by_strength: bool = True

# ============================================================================
# إعدادات التصفية والفلاتر
# ============================================================================

@dataclass
class VolumeFilterConfig:
    """إعدادات فلترة الحجم"""
    min_volume_usdt_24h: float = 10000000.0   # 10 مليون دولار
    min_volume_usdt_4h: float = 500000.0      # 500 ألف دولار
    
    # تجنب الأحجام المنخفضة جداً
    min_bid_ask_spread_bps: float = 5.0  # أساس النقاط

@dataclass
class PriceFilterConfig:
    """إعدادات فلترة السعر"""
    min_price: float = 0.00001
    max_price: float = 1000000.0
    
    # تجنب الأسعار غير المستقرة
    max_price_change_24h_percent: float = -5.0

@dataclass
class CoinFilterConfig:
    """إعدادات فلترة العملات"""
    max_coins_to_analyze: int = 25
    
    # العملات المستقرة المستثناة
    excluded_coins: List[str] = None
    
    # العملات المفضلة
    preferred_coins: List[str] = None
    
    # العملات المحظورة
    blacklist_coins: List[str] = None

@dataclass
class TimeFilterConfig:
    """إعدادات فلترة الوقت"""
    # أوقات التداول المسموحة (بصيغة الـ UTC)
    trading_start_hour: int = 0
    trading_end_hour: int = 24
    
    # تجنب أوقات معينة
    avoid_high_volatility_hours: List[int] = None
    avoid_low_liquidity_hours: List[int] = None
    
    # تجنب نهاية الأسبوع
    avoid_weekends: bool = False

# ============================================================================
# إعدادات منع التكرار والتنبيهات
# ============================================================================

@dataclass
class DuplicateFilterConfig:
    """إعدادات منع تكرار الإشارات"""
    avoid_duplicate_within_hours: int = 1  # ساعة واحدة
    
    # السماح بإشارات معاكسة
    allow_opposite_signal: bool = True
    
    # تذكر آخر إشارة لكل عملة
    remember_history_hours: int = 24

@dataclass
class NotificationConfig:
    """إعدادات التنبيهات"""
    # Telegram
    use_telegram: bool = True
    telegram_parse_mode: str = "HTML"
    
    # محتويات التنبيه
    include_technical_details: bool = True
    include_fibonacci_levels: bool = True
    include_volume_info: bool = True
    include_recommendation: bool = True
    
    # مستويات التنبيه
    notify_strong_buy: bool = True
    notify_strong_sell: bool = True
    notify_medium_signals: bool = True
    notify_weak_signals: bool = False

# ============================================================================
# إعدادات الأداء والتخزين
# ============================================================================

@dataclass
class PerformanceConfig:
    """إعدادات الأداء والتحسين"""
    # التخزين المؤقت
    enable_caching: bool = True
    cache_timeout_seconds: int = 300  # 5 دقائق
    
    # عدد المحاولات المتزامنة
    max_concurrent_requests: int = 10
    
    # حد أقصى لطلبات API في الدقيقة
    api_rate_limit_per_minute: int = 1200
    
    # تقليل استهلاك الموارد
    optimize_memory: bool = True
    optimize_cpu: bool = True

@dataclass
class LoggingConfig:
    """إعدادات السجلات والتسجيل"""
    log_file: str = "trading_bot.log"
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # تحديد حجم الملف
    max_log_size_mb: int = 50
    backup_log_files: int = 10
    
    # تسجيل حساس
    log_api_calls: bool = False  # لا تسجل مفاتيح API
    log_trades: bool = True
    log_signals: bool = True

# ============================================================================
# إعدادات الأمان
# ============================================================================

@dataclass
class SecurityConfig:
    """إعدادات الأمان"""
    # تشفير البيانات
    encrypt_credentials: bool = True
    credentials_file: str = "trading_config.json"
    credentials_file_permissions: int = 0o600  # Unix permissions
    
    # التحقق من الاتصال
    verify_ssl: bool = True
    timeout_seconds: int = 10
    
    # المفاتيح الاحتياطية
    backup_credentials: bool = True
    backup_directory: str = ".backups"

# ============================================================================
# الإعداد الرئيسي المتكامل
# ============================================================================

@dataclass
class BotConfig:
    """إعداد شامل للبوت"""
    
    # المعرفات الأساسية
    bot_name: str = "Advanced OKX Trading Bot"
    bot_version: str = "1.0.0"
    
    # إعدادات المؤشرات
    emas: EMAsConfig = None
    rsi: RSIConfig = None
    macd: MACDConfig = None
    support_resistance: SupportResistanceConfig = None
    trend: TrendConfig = None
    
    # إعدادات التداول
    profit_targets: ProfitTargetConfig = None
    stop_loss: StopLossConfig = None
    position_size: PositionSizeConfig = None
    
    # الفلاتر
    volume_filter: VolumeFilterConfig = None
    price_filter: PriceFilterConfig = None
    coin_filter: CoinFilterConfig = None
    time_filter: TimeFilterConfig = None
    
    # التنبيهات والتكرار
    duplicate_filter: DuplicateFilterConfig = None
    notifications: NotificationConfig = None
    
    # الأداء والأمان
    performance: PerformanceConfig = None
    logging: LoggingConfig = None
    security: SecurityConfig = None
    
    # مستوى المخاطرة الكلي
    risk_level: RiskLevel = RiskLevel.MODERATE
    
    def __post_init__(self):
        """التهيئة الافتراضية"""
        if self.emas is None:
            self.emas = EMAsConfig()
        if self.rsi is None:
            self.rsi = RSIConfig()
        if self.macd is None:
            self.macd = MACDConfig()
        if self.support_resistance is None:
            self.support_resistance = SupportResistanceConfig(
                fibonacci_levels=[0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
            )
        if self.trend is None:
            self.trend = TrendConfig()
        if self.profit_targets is None:
            self.profit_targets = ProfitTargetConfig()
        if self.stop_loss is None:
            self.stop_loss = StopLossConfig()
        if self.position_size is None:
            self.position_size = PositionSizeConfig()
        if self.volume_filter is None:
            self.volume_filter = VolumeFilterConfig()
        if self.price_filter is None:
            self.price_filter = PriceFilterConfig()
        if self.coin_filter is None:
            self.coin_filter = CoinFilterConfig(
                excluded_coins=['USDT', 'USDC', 'DAI', 'BUSD', 'TUSD'],
                preferred_coins=[],
                blacklist_coins=[]
            )
        if self.time_filter is None:
            self.time_filter = TimeFilterConfig(
                avoid_high_volatility_hours=[],
                avoid_low_liquidity_hours=[]
            )
        if self.duplicate_filter is None:
            self.duplicate_filter = DuplicateFilterConfig()
        if self.notifications is None:
            self.notifications = NotificationConfig()
        if self.performance is None:
            self.performance = PerformanceConfig()
        if self.logging is None:
            self.logging = LoggingConfig()
        if self.security is None:
            self.security = SecurityConfig()
    
    def to_dict(self) -> Dict:
        """تحويل الإعدادات إلى قاموس"""
        return {
            'bot_name': self.bot_name,
            'bot_version': self.bot_version,
            'risk_level': self.risk_level.value,
            'emas': self.emas.__dict__,
            'rsi': self.rsi.__dict__,
            'macd': self.macd.__dict__,
            'support_resistance': self.support_resistance.__dict__,
            'trend': self.trend.__dict__,
            'profit_targets': self.profit_targets.__dict__,
            'stop_loss': self.stop_loss.__dict__,
            'position_size': self.position_size.__dict__,
            'volume_filter': self.volume_filter.__dict__,
            'price_filter': self.price_filter.__dict__,
            'coin_filter': self.coin_filter.__dict__,
            'time_filter': self.time_filter.__dict__,
            'duplicate_filter': self.duplicate_filter.__dict__,
            'notifications': self.notifications.__dict__,
            'performance': self.performance.__dict__,
            'logging': self.logging.__dict__,
            'security': self.security.__dict__
        }

# ============================================================================
# الإعدادات الجاهزة المسبقة
# ============================================================================

# إعدادات متحفظة (Conservative)
CONSERVATIVE_CONFIG = BotConfig(
    risk_level=RiskLevel.CONSERVATIVE,
    position_size=PositionSizeConfig(position_size_usdt=50.0),
    profit_targets=ProfitTargetConfig(target_min_percent=1.5, target_max_percent=3.0),
    stop_loss=StopLossConfig(stop_loss_percent=1.5)
)

# إعدادات معتدلة (Moderate)
MODERATE_CONFIG = BotConfig(
    risk_level=RiskLevel.MODERATE,
    position_size=PositionSizeConfig(position_size_usdt=100.0),
    profit_targets=ProfitTargetConfig(target_min_percent=2.0, target_max_percent=7.0),
    stop_loss=StopLossConfig(stop_loss_percent=2.0)
)

# إعدادات عدوانية (Aggressive)
AGGRESSIVE_CONFIG = BotConfig(
    risk_level=RiskLevel.AGGRESSIVE,
    position_size=PositionSizeConfig(position_size_usdt=250.0),
    profit_targets=ProfitTargetConfig(target_min_percent=3.0, target_max_percent=10.0),
    stop_loss=StopLossConfig(stop_loss_percent=3.0)
)

# ============================================================================
# دالات المساعدة
# ============================================================================

def get_default_config() -> BotConfig:
    """الحصول على الإعدادات الافتراضية"""
    return BotConfig()

def get_config_by_risk_level(risk_level: RiskLevel) -> BotConfig:
    """الحصول على إعدادات حسب مستوى المخاطرة"""
    if risk_level == RiskLevel.CONSERVATIVE:
        return CONSERVATIVE_CONFIG
    elif risk_level == RiskLevel.AGGRESSIVE:
        return AGGRESSIVE_CONFIG
    else:
        return MODERATE_CONFIG

if __name__ == "__main__":
    # اختبار الإعدادات
    config = BotConfig()
    print("✅ تم تحميل الإعدادات بنجاح")
    print(f"اسم البوت: {config.bot_name}")
    print(f"الإصدار: {config.bot_version}")
    print(f"مستوى المخاطرة: {config.risk_level.value}")
    print(f"الحد الأدنى للحجم: ${config.volume_filter.min_volume_usdt_24h:,.0f}")
    print(f"الهدف الأول: {config.profit_targets.target_1_percent}%")
    print(f"الهدف الثاني: {config.profit_targets.target_2_percent}%")
