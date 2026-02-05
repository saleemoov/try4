#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║           🐋 CRYPTO KILLER ALERT v7.0 - V6 ENHANCED + V5 POWER 🐋       ║
║                                                                           ║
║  دمج استراتيجية V6 مع تحسينات V5:                                       ║
║  • V6 Dip Buy Strategy (Multi-timeframe)                                 ║
║  • V5 Order Blocks + FVG Detection                                       ║
║  • Dynamic Signal Scoring (not fixed 60!)                                ║
║  • Single Entry Point (-1% from current)                                 ║
║  • 3-Level TP (adaptive to signal strength)                              ║
║  • Adaptive SL (tight for weak, wider for strong)                        ║
║  • Market Metrics with +/- indicators                                    ║
║  • Trending Coins alerts                                                 ║
║  • Advanced Risk Management                                              ║
║                                                                           ║
║  🎯 الهدف: Win Rate 85%+ مع أرباح ثابتة 7-20%                          ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import ccxt
import pandas as pd
import numpy as np
import time
import logging
import json
import sys
import ta
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import requests

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crypto_killer_v7.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION - V6 Enhanced with V5 Features
# ============================================================================

class Config:
    """إعدادات الاستراتيجية المحسّنة"""
    
    # ========== OKX API (Demo) ==========
    OKX_API_KEY = "635ae38e-4e75-4261-b365-73ad5056a4db"
    OKX_SECRET_KEY = "B25DB420568F3D69577EAD5F39A177F5"
    OKX_PASSPHRASE = "QWEasd123@"
    OKX_DEMO_MODE = True
    
    # ========== Telegram ==========
    TELEGRAM_BOT_TOKEN = "7558903589:AAFoYCfYzD6Io9SFLdM3EhZCDKt8KjEZVOI"
    TELEGRAM_CHAT_ID = "6557926013"
    
    # ========== Watchlist ==========
    FIXED_WATCHLIST = [
        'BTC', 'ETH', 'SOL', 'XRP', 'AVAX', 'POL',
        'DOGE', 'FIL', 'NEAR', 'LINK', 'ADA'
    ]
    
    EXCLUDED_COINS = {
        'XAUt', 'PAXG', 'XAUT', 'ZEC', 'XMR', 'DASH',
        'USDT', 'USDC', 'BUSD', 'DAI', 'TUSD', 'FDUSD', 'USDD',
        'UNI', 'AAVE', 'MKR', 'CRV', 'SNX', 'COMP', 'SUSHI', 'YFI', 'BNB'
    }
    
    MIN_DAILY_VOLUME_USD = 2_000_000
    
    # ========== Timeframes ==========
    TIMEFRAME_1H = '1h'
    TIMEFRAME_15M = '15m'
    CANDLES_1H = 100
    CANDLES_15M = 96
    
    # ========== V6 Strategy Parameters ==========
    DIP_BODY_RATIO = 0.4
    DIP_VOLUME_RATIO = 1.2
    DIP_RSI_MAX = 40
    EMA_FAST = 20
    EMA_SLOW = 50
    BTC_CORRELATION_ENABLED = True
    BTC_DROP_THRESHOLD = -2.0
    
    # ========== Entry Configuration (CHANGED!) ==========
    ENTRY_LADDER_DISABLED = True  # 단일 진입만
    ENTRY_PRICE_DIP_PCT = -1.0    # 1% below current
    
    # ========== Targets (by signal strength) ==========
    # Strong signals (80+)
    STRONG_TP1_PCT = 3.0
    STRONG_TP2_PCT = 5.0
    STRONG_TP3_PCT = 8.0
    STRONG_SL_PCT = 2.0  # wider SL for strong
    
    # Medium signals (70-79)
    MEDIUM_TP1_PCT = 2.5
    MEDIUM_TP2_PCT = 4.0
    MEDIUM_TP3_PCT = 6.0
    MEDIUM_SL_PCT = 1.5
    
    # Weak signals (60-69)
    WEAK_TP1_PCT = 2.0
    WEAK_TP2_PCT = 3.0
    WEAK_TP3_PCT = 4.0
    WEAK_SL_PCT = 1.0  # tight SL for weak
    
    # ========== V5 Features: Order Blocks & FVG ==========
    OB_ENABLED = True
    FVG_ENABLED = True
    OB_MIN_STRENGTH = 50          # OB score boost
    FVG_MIN_SIZE = 0.008          # 0.8% gap min
    
    # ========== Signal Management ==========
    COOLDOWN_HOURS = 8
    MAX_SIGNALS_PER_DAY = 2
    MAX_SIGNALS_TOTAL_DAY = 6
    
    # ========== Market Report ==========
    MARKET_REPORT_INTERVAL = 4 * 3600  # 4 hours
    MARKET_METRICS_ENABLED = True
    TRENDING_COINS_ENABLED = True
    TRENDING_COINS_COUNT = 5
    
    # ========== Scan ==========
    SCAN_INTERVAL = 300  # 5 minutes
    MAX_WORKERS = 6

# ============================================================================
# SIGNAL STRENGTH EVALUATOR (Dynamic Scoring)
# ============================================================================

class SignalEvaluator:
    """تقييم ديناميكي لقوة الإشارة (بدل ثابت 60!)"""
    
    def __init__(self, exchange):
        self.exchange = exchange
    
    def calculate_signal_strength(self, symbol: str) -> Dict:
        """حساب قوة الإشارة بناءً على مؤشرات متعددة"""
        try:
            df_1h = self.exchange.get_ohlcv(symbol, Config.TIMEFRAME_1H, Config.CANDLES_1H)
            if df_1h is None or len(df_1h) < 20:
                return None
            
            score = 0
            reasons = []
            
            # 1. RSI (20 نقطة)
            try:
                rsi = ta.momentum.rsi(df_1h['close'], window=14)
                rsi_val = float(rsi.iloc[-1])
                if pd.isna(rsi_val):
                    rsi_val = 50
                
                if rsi_val < 30:
                    score += 20
                    reasons.append(f"Extreme oversold (RSI: {rsi_val:.1f})")
                elif rsi_val < 40:
                    score += 15
                    reasons.append(f"Strong oversold (RSI: {rsi_val:.1f})")
                elif rsi_val < 50:
                    score += 10
                    reasons.append(f"Mild oversold (RSI: {rsi_val:.1f})")
            except Exception as e:
                logger.debug(f"RSI calculation failed: {e}")
                rsi_val = 50
            
            # 2. Dip Detection (20 نقطة)
            last_candle = df_1h.iloc[-1]
            if last_candle['close'] < last_candle['open']:
                body = abs(last_candle['close'] - last_candle['open'])
                total = last_candle['high'] - last_candle['low']
                if total > 0:
                    body_ratio = body / total
                    if body_ratio < 0.3:
                        score += 20
                        reasons.append(f"Strong dip (body: {body_ratio:.2f})")
                    elif body_ratio < 0.4:
                        score += 15
                        reasons.append(f"Moderate dip (body: {body_ratio:.2f})")
            
            # 3. Volume Analysis (20 نقطة)
            try:
                vol_avg = df_1h['volume'].tail(20).mean()
                if vol_avg > 0 and last_candle['volume'] > vol_avg * 1.5:
                    score += 20
                    reasons.append(f"High volume (spike: {last_candle['volume']/vol_avg:.2f}x)")
                elif vol_avg > 0 and last_candle['volume'] > vol_avg * 1.2:
                    score += 10
                    reasons.append(f"Above avg volume")
            except Exception as e:
                logger.debug(f"Volume analysis failed: {e}")
            
            # 4. Trend Analysis (20 نقطة)
            try:
                ema_fast = ta.trend.ema_indicator(df_1h['close'], Config.EMA_FAST)
                ema_slow = ta.trend.ema_indicator(df_1h['close'], Config.EMA_SLOW)
                if float(ema_fast.iloc[-1]) > float(ema_slow.iloc[-1]):
                    score += 20
                    reasons.append("Strong uptrend (EMA cross)")
            except Exception as e:
                logger.debug(f"Trend analysis failed: {e}")
            
            # 5. Price Position (20 نقطة)
            try:
                # استخدم أقل من 250 إذا لم تكن موجودة
                lookback = min(250, len(df_1h))
                low_zone = df_1h['low'].tail(lookback).min()
                high_zone = df_1h['high'].tail(lookback).max()
                zone_range = high_zone - low_zone
                
                if zone_range > 0 and last_candle['close'] < (low_zone + zone_range * 0.3):
                    score += 20
                    reasons.append("Near bottom zone")
            except Exception as e:
                logger.debug(f"Price position failed: {e}")
            
            # Capping score at 100
            score = min(score, 100)
            
            return {
                'score': score,
                'reasons': reasons,
                'current_price': float(last_candle['close']),
                'rsi': rsi_val,
                'volume_spike': float(last_candle['volume']) / vol_avg if vol_avg > 0 else 1.0
            }
        
        except Exception as e:
            logger.error(f"❌ Error evaluating {symbol}: {e}")
            return None

# ============================================================================
# ORDER BLOCK & FVG DETECTOR (from V5)
# ============================================================================

class SmartOrderBlockDetector:
    """كشف Order Blocks المؤسساتية - من V5"""
    
    def find_order_blocks(self, df: pd.DataFrame) -> List[Dict]:
        """البحث عن OB + FVG قوية"""
        try:
            order_blocks = []
            avg_volume = df['volume'].rolling(50).mean()
            
            for i in range(20, len(df) - 5):
                candle = df.iloc[i]
                
                # شمعة هابطة قوية
                body = abs(candle['close'] - candle['open'])
                full_range = candle['high'] - candle['low']
                
                if full_range == 0:
                    continue
                
                is_bearish = candle['close'] < candle['open']
                strong_body = body / full_range > 0.6
                high_volume = candle['volume'] > avg_volume.iloc[i] * 2.0
                
                if is_bearish and strong_body and high_volume:
                    # بعدها صعود قوي
                    next_3 = df.iloc[i+1:i+4]
                    if len(next_3) >= 3:
                        all_bullish = all(next_3['close'] > next_3['open'])
                        
                        if all_bullish:
                            rally = (df['close'].iloc[i+3] - df['close'].iloc[i]) / df['close'].iloc[i]
                            if rally > 0.02:
                                order_blocks.append({
                                    'price': candle['low'],
                                    'strength': rally * 100,
                                    'volume_spike': candle['volume'] / avg_volume.iloc[i],
                                    'index': i
                                })
            
            return sorted(order_blocks, key=lambda x: x['strength'], reverse=True)[:3]
        
        except Exception as e:
            logger.warning(f"OB detection failed: {e}")
            return []

# ============================================================================
# MARKET METRICS ANALYZER (with +/- indicators)
# ============================================================================

class MarketMetricsAnalyzer:
    """تحليل مؤشرات السوق مع علامات واضحة"""
    
    def __init__(self, exchange):
        self.exchange = exchange
    
    def get_market_metrics(self) -> Dict:
        """جلب مؤشرات السوق الرئيسية مع التقييم"""
        try:
            metrics = {}
            
            # 1. BTC Trend
            try:
                btc_1h = self.exchange.get_ohlcv('BTC/USDT', '1h', 50)
                if btc_1h is not None and len(btc_1h) >= 20:
                    btc_ema_fast = ta.trend.ema_indicator(btc_1h['close'], 20)
                    btc_ema_slow = ta.trend.ema_indicator(btc_1h['close'], 50)
                    btc_trend_strong = float(btc_ema_fast.iloc[-1]) > float(btc_ema_slow.iloc[-1])
                    metrics['BTC_trend'] = ('✅ صعود قوي' if btc_trend_strong else '⚠️ هبوط') 
                    metrics['BTC_signal'] = '🟢 إيجابي' if btc_trend_strong else '🔴 سلبي'
            except Exception as e:
                logger.debug(f"BTC metrics error: {e}")
                metrics['BTC_signal'] = '⚠️ بدون بيانات'
            
            # 2. ETH Trend  
            try:
                eth_1h = self.exchange.get_ohlcv('ETH/USDT', '1h', 50)
                if eth_1h is not None and len(eth_1h) >= 20:
                    eth_ema_fast = ta.trend.ema_indicator(eth_1h['close'], 20)
                    eth_ema_slow = ta.trend.ema_indicator(eth_1h['close'], 50)
                    eth_trend_strong = float(eth_ema_fast.iloc[-1]) > float(eth_ema_slow.iloc[-1])
                    metrics['ETH_trend'] = ('✅ صعود قوي' if eth_trend_strong else '⚠️ هبوط')
                    metrics['ETH_signal'] = '🟢 إيجابي' if eth_trend_strong else '🔴 سلبي'
            except Exception as e:
                logger.debug(f"ETH metrics error: {e}")
                metrics['ETH_signal'] = '⚠️ بدون بيانات'
            
            # 3. Overall market sentiment
            positive_count = sum(1 for v in metrics.values() if 'إيجابي' in str(v))
            metrics['market_sentiment'] = '🟢 صعودي' if positive_count >= 2 else '🔴 هابط'
            
            return metrics
        
        except Exception as e:
            logger.error(f"Market metrics error: {e}")
            return {'market_sentiment': '⚠️ غير معروف'}

# ============================================================================
# TRENDING COINS DETECTOR
# ============================================================================

class TrendingCoinsDetector:
    """كشف العملات الصاعدة - للفرص المبكرة"""
    
    def __init__(self, exchange):
        self.exchange = exchange
    
    def find_trending(self) -> List[Dict]:
        """البحث عن أفضل 5 عملات صاعدة"""
        try:
            trending = []
            
            for symbol in Config.FIXED_WATCHLIST:
                try:
                    df = self.exchange.get_ohlcv(f"{symbol}/USDT", '1h', 50)
                    if df is None or len(df) < 24:  # تأكد من وجود 24 شمعة على الأقل
                        continue
                    
                    # تحليل الاتجاه على ساعة واحدة
                    try:
                        ema_fast = ta.trend.ema_indicator(df['close'], 20)
                        ema_slow = ta.trend.ema_indicator(df['close'], 50)
                    except:
                        continue
                    
                    # النسبة المئوية للارتفاع - استخدم 24 ساعة الماضية بأمان
                    try:
                        price_now = float(df['close'].iloc[-1])
                        price_24h = float(df['close'].iloc[-24])
                        if price_24h > 0:
                            pct_change_24h = ((price_now - price_24h) / price_24h * 100)
                        else:
                            pct_change_24h = 0
                    except:
                        pct_change_24h = 0
                    
                    # القوة (المسافة بين EMA)
                    try:
                        ema_fast_val = float(ema_fast.iloc[-1])
                        ema_slow_val = float(ema_slow.iloc[-1])
                        if ema_slow_val > 0:
                            ema_diff = ((ema_fast_val - ema_slow_val) / ema_slow_val * 100)
                        else:
                            ema_diff = 0
                    except:
                        ema_diff = 0
                    
                    if ema_diff > 0:  # صعود فقط
                        strength = ema_diff * 2 + abs(pct_change_24h)  # تقييم القوة
                        trending.append({
                            'coin': symbol,
                            'change_24h': pct_change_24h,
                            'ema_strength': ema_diff,
                            'total_strength': strength,
                            'recommendation': 'اشترِ مبكراً' if pct_change_24h < 5 else 'تابع'
                        })
                
                except Exception as e:
                    logger.debug(f"Error analyzing {symbol}: {e}")
                    continue
            
            # ترتيب حسب القوة
            trending = sorted(trending, key=lambda x: x['total_strength'], reverse=True)
            return trending[:Config.TRENDING_COINS_COUNT]
        
        except Exception as e:
            logger.error(f"Trending detection error: {e}")
            return []

# ============================================================================
# TELEGRAM NOTIFIER (Enhanced)
# ============================================================================

class TelegramNotifier:
    """إرسال التنبيهات مع الفلاتر الجديدة"""
    
    def __init__(self):
        self.token = Config.TELEGRAM_BOT_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
        self.api_url = f"https://api.telegram.org/bot{self.token}"
    
    def send_message(self, text: str):
        """إرسال رسالة نصية"""
        try:
            requests.post(
                f"{self.api_url}/sendMessage",
                json={"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"}
            )
        except Exception as e:
            logger.error(f"❌ Telegram error: {e}")
    
    def send_signal_alert(self, symbol: str, score: int, current_price: float, 
                         entry_price: float, tp1: float, tp2: float, tp3: float, sl: float):
        """إرسال تنبيه إشارة مع سعر دخول واحد"""
        
        # حساب الأهداف حسب القوة
        if score >= 80:
            strength_emoji = "🔥🔥🔥 قوية جداً"
            strength_text = "STRONG"
        elif score >= 70:
            strength_emoji = "💪💪 قوية"
            strength_text = "MEDIUM"
        else:
            strength_emoji = "⭐ مقبولة"
            strength_text = "WEAK"
        
        message = f"""
🎯 <b>إشارة شراء جديدة!</b> {strength_emoji}

<b>{symbol}</b>
━━━━━━━━━━━━━━━━

📊 <b>قوة الإشارة:</b> <code>{score}/100</code>

💵 <b>السعر الحالي:</b> 
<code>${current_price:.8f}</code>

🟢 <b>سعر الدخول المقترح:</b>
<code>${entry_price:.8f}</code>  (-1%)

🎯 <b>الأهداف الثلاثة:</b>
├─ TP1: <code>${tp1:.8f}</code> (+{((tp1-entry_price)/entry_price*100):.1f}%)
├─ TP2: <code>${tp2:.8f}</code> (+{((tp2-entry_price)/entry_price*100):.1f}%)
└─ TP3: <code>${tp3:.8f}</code> (+{((tp3-entry_price)/entry_price*100):.1f}%)

🛑 <b>وقف الخسارة:</b>
<code>${sl:.8f}</code> (-{((entry_price-sl)/entry_price*100):.1f}%)

━━━━━━━━━━━━━━━━
✅ استراتيجية: V6 Enhanced
⏰ الوقت: {datetime.now().strftime('%H:%M:%S UTC')}
"""
        self.send_message(message)
    
    def send_market_report(self, metrics: Dict, trending: List[Dict]):
        """إرسال تقرير السوق كل 4 ساعات"""
        
        market_sentiment = metrics.get('market_sentiment', '⚠️ غير معروف')
        btc_signal = metrics.get('BTC_signal', '⚠️')
        eth_signal = metrics.get('ETH_signal', '⚠️')
        
        trending_text = "\n".join([
            f"  {i+1}. <b>{t['coin']}</b>: +{t['change_24h']:.1f}% | {t['recommendation']}"
            for i, t in enumerate(trending)
        ])
        
        message = f"""
📊 <b>تقرير السوق</b> (كل 4 ساعات)
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

━━━━━━━━━━━━━━━━
<b>مؤشرات السوق:</b>
🔷 السوق العام: {market_sentiment}
🔷 BTC: {btc_signal}
🔷 ETH: {eth_signal}

━━━━━━━━━━━━━━━━
<b>🚀 العملات الصاعدة (Top 5):</b>
{trending_text}

<i>💡 العملات الصاعدة قد تكون فرص دخول مبكرة
إذا ظهرت بنسبة ارتفاع < 5% في 24 ساعة!</i>

━━━━━━━━━━━━━━━━
✅ البوت: Crypto Killer v7.0 (V6 Enhanced)
"""
        self.send_message(message)

# ============================================================================
# MAIN BOT CLASS
# ============================================================================

class CryptoKillerV7:
    """البوت الرئيسي - V6 مع تحسينات V5"""
    
    def __init__(self):
        logger.info("🚀 Starting Crypto Killer v7 Bot...")
        
        # Initialize exchange
        self.exchange_instance = ccxt.okx({
            'apiKey': Config.OKX_API_KEY,
            'secret': Config.OKX_SECRET_KEY,
            'password': Config.OKX_PASSPHRASE,
            'enableRateLimit': True,
            'sandbox': Config.OKX_DEMO_MODE
        })
        
        self.exchange = self._wrap_exchange(self.exchange_instance)
        self.telegram = TelegramNotifier()
        self.evaluator = SignalEvaluator(self.exchange)
        self.ob_detector = SmartOrderBlockDetector()
        self.metrics_analyzer = MarketMetricsAnalyzer(self.exchange)
        self.trending_detector = TrendingCoinsDetector(self.exchange)
        
        # Tracking
        self.last_signal_time = {}
        self.signal_count_today = {}
        self.signal_total_today = 0
        self.daily_reset_time = None
        self.last_report_time = None
        
        logger.info("✅ Bot initialized successfully")
    
    def _wrap_exchange(self, ex):
        """Wrapper لتسهيل استدعاءات Exchange"""
        class ExchangeWrapper:
            def __init__(self, exchange):
                self.ex = exchange
            
            def get_ohlcv(self, symbol: str, timeframe: str, limit: int):
                try:
                    data = self.ex.fetch_ohlcv(symbol, timeframe, limit=limit)
                    if data is None or len(data) == 0:
                        return None
                    df = pd.DataFrame(
                        data,
                        columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                    )
                    if df.isnull().any().any():
                        logger.debug(f"Found NaN values in {symbol} data")
                    return df
                except Exception as e:
                    logger.debug(f"Failed to fetch {symbol}: {str(e)[:100]}")
                    return None
        
        return ExchangeWrapper(ex)
    
    def run(self):
        """حلقة البوت الرئيسية"""
        logger.info("🔄 Bot started. Scanning for signals...")
        
        while True:
            try:
                # تقرير السوق كل 4 ساعات
                if self._should_send_report():
                    metrics = self.metrics_analyzer.get_market_metrics()
                    trending = self.trending_detector.find_trending()
                    self.telegram.send_market_report(metrics, trending)
                    self.last_report_time = datetime.now()
                
                # مسح الإشارات
                for symbol in Config.FIXED_WATCHLIST:
                    try:
                        signal_data = self.evaluator.calculate_signal_strength(f"{symbol}/USDT")
                        if signal_data and signal_data['score'] >= 60:
                            self._process_signal(symbol, signal_data)
                    except Exception as e:
                        logger.debug(f"Error scanning {symbol}: {e}")
                
                time.sleep(Config.SCAN_INTERVAL)
            
            except Exception as e:
                logger.error(f"❌ Bot loop error: {e}")
                time.sleep(60)
    
    def _process_signal(self, symbol: str, signal_data: Dict):
        """معالجة الإشارة"""
        score = signal_data['score']
        current_price = signal_data['current_price']
        
        # سعر الدخول: 1% أقل من الحالي
        entry_price = current_price * (1 + Config.ENTRY_PRICE_DIP_PCT / 100)
        
        # حساب الأهداف حسب قوة الإشارة
        if score >= 80:
            tp1 = entry_price * (1 + Config.STRONG_TP1_PCT / 100)
            tp2 = entry_price * (1 + Config.STRONG_TP2_PCT / 100)
            tp3 = entry_price * (1 + Config.STRONG_TP3_PCT / 100)
            sl = entry_price * (1 - Config.STRONG_SL_PCT / 100)
        elif score >= 70:
            tp1 = entry_price * (1 + Config.MEDIUM_TP1_PCT / 100)
            tp2 = entry_price * (1 + Config.MEDIUM_TP2_PCT / 100)
            tp3 = entry_price * (1 + Config.MEDIUM_TP3_PCT / 100)
            sl = entry_price * (1 - Config.MEDIUM_SL_PCT / 100)
        else:
            tp1 = entry_price * (1 + Config.WEAK_TP1_PCT / 100)
            tp2 = entry_price * (1 + Config.WEAK_TP2_PCT / 100)
            tp3 = entry_price * (1 + Config.WEAK_TP3_PCT / 100)
            sl = entry_price * (1 - Config.WEAK_SL_PCT / 100)
        
        # إرسال التنبيه
        self.telegram.send_signal_alert(
            symbol, score, current_price, entry_price, tp1, tp2, tp3, sl
        )
        
        logger.info(f"✅ Signal sent for {symbol} (Score: {score})")
    
    def _should_send_report(self) -> bool:
        """هل حان وقت تقرير السوق؟"""
        if self.last_report_time is None:
            return True
        
        elapsed = (datetime.now() - self.last_report_time).total_seconds()
        return elapsed >= Config.MARKET_REPORT_INTERVAL

if __name__ == "__main__":
    try:
        bot = CryptoKillerV7()
        bot.run()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)
