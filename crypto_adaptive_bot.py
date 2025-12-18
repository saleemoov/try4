#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                    🚀 CRYPTO ADAPTIVE BOT v3.0 🚀                         ║
║                                                                           ║
║  استراتيجية متكيفة مع جميع ظروف السوق:                                  ║
║  • STRONG UPTREND: مسك الموجة الصاعدة كاملة 📈                           ║
║  • STRONG DOWNTREND: استفادة من الارتدادات السريعة ⚡                     ║
║  • RANGE: دخول من مناطق consolidation 📊                                 ║
║                                                                           ║
║  المبدأ: "البوت يتكيف، أنت تربح!" 💰                                     ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import ccxt
import pandas as pd
import numpy as np
import time
import logging
import json
import sys
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
        logging.FileHandler('adaptive_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

class AdaptiveConfig:
    """إعدادات البوت الشاملة"""
    
    # General Settings
    TIMEFRAME = '15m'
    CANDLES_LOOKBACK = 200
    MIN_VOLUME_USDT = 1_000_000
    SCAN_INTERVAL_SECONDS = 300
    MAX_WORKERS = 10
    
    # EMA Settings (للفلتر الهجين)
    EMA_LONG = 200    # الاتجاه الرئيسي (50 ساعة)
    EMA_SHORT = 50    # الاتجاه القصير (12.5 ساعة)
    EMA_FAST = 5      # للدخول السريع
    EMA_MID = 8
    EMA_SLOW = 13
    
    # Market Mode Thresholds
    STRONG_TREND_THRESHOLD = 0.03  # 3% slope للترند القوي
    RANGE_THRESHOLD = 0.015        # 1.5% للسوق الجانبي
    
    # RSI Settings
    RSI_PERIOD = 14
    RSI_OVERSOLD_EXTREME = 25  # Downtrend entries
    RSI_OVERSOLD = 30
    RSI_PULLBACK_MIN = 40      # Uptrend pullback
    RSI_PULLBACK_MAX = 55
    
    # Volume Analysis
    VOLUME_MA_PERIOD = 20
    VOLUME_SPIKE_THRESHOLD = 1.5
    VOLUME_LOW_THRESHOLD = 0.7
    
    # Risk Management - STRONG UPTREND
    UPTREND_TARGET1 = 3.0
    UPTREND_TARGET2 = 5.0
    UPTREND_STOPLOSS = 1.5
    UPTREND_TRAILING_TRIGGER = 4.0
    UPTREND_TRAILING_DISTANCE = 1.8
    UPTREND_MAX_HOURS = 4
    
    # Risk Management - STRONG DOWNTREND
    DOWNTREND_TARGET1 = 2.0
    DOWNTREND_TARGET2 = 3.0
    DOWNTREND_STOPLOSS = 1.0
    DOWNTREND_MAX_HOURS = 1.5
    
    # Risk Management - PULLBACK/BOUNCE
    PULLBACK_TARGET1 = 2.5
    PULLBACK_TARGET2 = 4.0
    PULLBACK_STOPLOSS = 1.2
    PULLBACK_MAX_HOURS = 3
    
    # Risk Management - RANGE
    RANGE_TARGET1 = 2.5
    RANGE_TARGET2 = 4.0
    RANGE_STOPLOSS = 1.2
    RANGE_MAX_HOURS = 3
    
    # Pattern Detection
    CONSOLIDATION_MIN_CANDLES = 16
    CONSOLIDATION_MAX_CANDLES = 32
    CONSOLIDATION_MAX_RANGE_PCT = 1.8
    
    # Scoring System
    MIN_SCORE_UPTREND = 180      # من 400
    MIN_SCORE_DOWNTREND = 160    # أقل لأن الفرص نادرة
    MIN_SCORE_RANGE = 200        # أعلى للدقة

# ============================================================================
# 1️⃣ MARKET MODE DETECTOR (الفلتر الهجين)
# ============================================================================

class MarketModeDetector:
    """
    يحدد حالة السوق باستخدام EMA 200 + EMA 50
    
    الأوضاع الممكنة:
    - STRONG_UPTREND: صاعد قوي (السعر فوق 200 و 50، والاثنان صاعدان)
    - UPTREND_PULLBACK: تصحيح في ترند صاعد
    - STRONG_DOWNTREND: هابط قوي (السعر تحت 200 و 50، والاثنان هابطان)
    - DOWNTREND_BOUNCE: ارتداد في ترند هابط
    - RANGE: سوق جانبي
    """
    
    def __init__(self):
        self.ema_long = AdaptiveConfig.EMA_LONG
        self.ema_short = AdaptiveConfig.EMA_SHORT
    
    def detect_mode(self, df: pd.DataFrame) -> Dict:
        """تحليل وضع السوق"""
        
        # حساب EMAs
        df['ema200'] = df['close'].ewm(span=self.ema_long, adjust=False).mean()
        df['ema50'] = df['close'].ewm(span=self.ema_short, adjust=False).mean()
        
        current_price = df['close'].iloc[-1]
        ema200_now = df['ema200'].iloc[-1]
        ema50_now = df['ema50'].iloc[-1]
        
        # حساب الميول (slope)
        ema200_slope = (df['ema200'].iloc[-1] - df['ema200'].iloc[-20]) / df['ema200'].iloc[-20]
        ema50_slope = (df['ema50'].iloc[-1] - df['ema50'].iloc[-10]) / df['ema50'].iloc[-10]
        
        # تحليل Higher Highs / Lower Lows
        recent_highs = df['high'].iloc[-20:].values
        recent_lows = df['low'].iloc[-20:].values
        
        higher_highs = self._check_higher_highs(recent_highs)
        lower_lows = self._check_lower_lows(recent_lows)
        
        # القرار النهائي
        mode = self._determine_mode(
            current_price, ema200_now, ema50_now,
            ema200_slope, ema50_slope,
            higher_highs, lower_lows
        )
        
        return {
            'mode': mode,
            'price': current_price,
            'ema200': ema200_now,
            'ema50': ema50_now,
            'ema200_slope': ema200_slope * 100,  # كنسبة مئوية
            'ema50_slope': ema50_slope * 100,
            'higher_highs': higher_highs,
            'lower_lows': lower_lows,
            'distance_from_ema200': ((current_price - ema200_now) / ema200_now) * 100,
            'distance_from_ema50': ((current_price - ema50_now) / ema50_now) * 100
        }
    
    def _check_higher_highs(self, highs: np.ndarray) -> bool:
        """فحص وجود higher highs"""
        if len(highs) < 6:
            return False
        
        peaks = []
        for i in range(1, len(highs) - 1):
            if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                peaks.append(highs[i])
        
        if len(peaks) >= 2:
            return peaks[-1] > peaks[-2]
        return False
    
    def _check_lower_lows(self, lows: np.ndarray) -> bool:
        """فحص وجود lower lows"""
        if len(lows) < 6:
            return False
        
        troughs = []
        for i in range(1, len(lows) - 1):
            if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                troughs.append(lows[i])
        
        if len(troughs) >= 2:
            return troughs[-1] < troughs[-2]
        return False
    
    def _determine_mode(self, price, ema200, ema50, slope200, slope50, hh, ll) -> str:
        """تحديد الوضع النهائي"""
        
        threshold_strong = AdaptiveConfig.STRONG_TREND_THRESHOLD
        threshold_range = AdaptiveConfig.RANGE_THRESHOLD
        
        # 1. STRONG UPTREND
        if (price > ema200 and price > ema50 and 
            slope200 > threshold_strong and slope50 > threshold_strong and hh):
            return "STRONG_UPTREND"
        
        # 2. UPTREND PULLBACK
        if (price > ema200 and price < ema50 and slope200 > 0):
            return "UPTREND_PULLBACK"
        
        # 3. STRONG DOWNTREND
        if (price < ema200 and price < ema50 and 
            slope200 < -threshold_strong and slope50 < -threshold_strong and ll):
            return "STRONG_DOWNTREND"
        
        # 4. DOWNTREND BOUNCE
        if (price < ema200 and price > ema50 and slope200 < 0):
            return "DOWNTREND_BOUNCE"
        
        # 5. RANGE (default)
        return "RANGE"

# ============================================================================
# 2️⃣ TECHNICAL INDICATORS
# ============================================================================

class TechnicalIndicators:
    """المؤشرات الفنية المشتركة"""
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """حساب RSI"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int) -> pd.Series:
        """حساب EMA"""
        return df['close'].ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def find_support_resistance(df: pd.DataFrame, lookback: int = 50) -> Dict:
        """إيجاد مناطق الدعم والمقاومة"""
        highs = df['high'].iloc[-lookback:].values
        lows = df['low'].iloc[-lookback:].values
        
        # Support: أقل 3 قيعان
        support_levels = sorted(lows)[:3]
        
        # Resistance: أعلى 3 قمم
        resistance_levels = sorted(highs, reverse=True)[:3]
        
        return {
            'support': np.mean(support_levels),
            'resistance': np.mean(resistance_levels)
        }
    
    @staticmethod
    def detect_divergence(df: pd.DataFrame, rsi: pd.Series) -> Dict:
        """كشف Bullish Divergence"""
        
        # آخر 20 شمعة
        recent_df = df.iloc[-20:].copy()
        recent_rsi = rsi.iloc[-20:].values
        recent_lows = recent_df['low'].values
        
        # إيجاد القيعان
        price_troughs = []
        rsi_troughs = []
        
        for i in range(1, len(recent_lows) - 1):
            if recent_lows[i] < recent_lows[i-1] and recent_lows[i] < recent_lows[i+1]:
                price_troughs.append((i, recent_lows[i]))
                rsi_troughs.append((i, recent_rsi[i]))
        
        # فحص Bullish Divergence
        if len(price_troughs) >= 2 and len(rsi_troughs) >= 2:
            last_price_trough = price_troughs[-1][1]
            prev_price_trough = price_troughs[-2][1]
            last_rsi_trough = rsi_troughs[-1][1]
            prev_rsi_trough = rsi_troughs[-2][1]
            
            if last_price_trough < prev_price_trough and last_rsi_trough > prev_rsi_trough:
                return {
                    'found': True,
                    'score': 80,
                    'strength': 'STRONG'
                }
        
        return {'found': False, 'score': 0}
    
    @staticmethod
    def analyze_volume(df: pd.DataFrame) -> Dict:
        """تحليل الحجم"""
        df['volume_ma'] = df['volume'].rolling(window=AdaptiveConfig.VOLUME_MA_PERIOD).mean()
        
        current_volume = df['volume'].iloc[-1]
        avg_volume = df['volume_ma'].iloc[-1]
        
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        # فحص Volume Spike
        is_spike = volume_ratio > AdaptiveConfig.VOLUME_SPIKE_THRESHOLD
        
        # فحص Declining Volume
        last_3_volumes = df['volume'].iloc[-3:].values
        is_declining = (last_3_volumes[0] > last_3_volumes[1] > last_3_volumes[2])
        
        return {
            'current': current_volume,
            'average': avg_volume,
            'ratio': volume_ratio,
            'is_spike': is_spike,
            'is_declining': is_declining,
            'score': 50 if is_spike else (30 if is_declining else 0)
        }
    
    @staticmethod
    def detect_candlestick_patterns(df: pd.DataFrame) -> Dict:
        """كشف أنماط الشموع"""
        last_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]
        
        open_price = last_candle['open']
        close_price = last_candle['close']
        high_price = last_candle['high']
        low_price = last_candle['low']
        
        body = abs(close_price - open_price)
        upper_wick = high_price - max(open_price, close_price)
        lower_wick = min(open_price, close_price) - low_price
        total_range = high_price - low_price
        
        patterns = []
        score = 0
        
        # Hammer (صاعد)
        if (lower_wick > body * 2 and upper_wick < body * 0.5 and close_price > open_price):
            patterns.append('HAMMER')
            score += 40
        
        # Bullish Engulfing
        if (close_price > open_price and 
            prev_candle['close'] < prev_candle['open'] and
            close_price > prev_candle['open'] and 
            open_price < prev_candle['close']):
            patterns.append('BULLISH_ENGULFING')
            score += 50
        
        # Doji (تردد)
        if body < total_range * 0.1:
            patterns.append('DOJI')
            score += 20
        
        return {
            'patterns': patterns,
            'score': score,
            'body_pct': (body / total_range * 100) if total_range > 0 else 0,
            'lower_wick_pct': (lower_wick / total_range * 100) if total_range > 0 else 0
        }

# ============================================================================
# 3️⃣ UPTREND STRATEGY (مسك الموجة الصاعدة)
# ============================================================================

class UptrendStrategy:
    """
    استراتيجية الترند الصاعد
    الهدف: مسك الموجة الصاعدة كاملة 📈
    الدخول: عند pullback لـ EMA 50 أو EMA 13
    """
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
    
    def analyze(self, symbol: str, df: pd.DataFrame, mode_data: Dict) -> Dict:
        """تحليل فرصة الدخول في الترند الصاعد"""
        
        # حساب المؤشرات
        df['ema5'] = self.indicators.calculate_ema(df, AdaptiveConfig.EMA_FAST)
        df['ema8'] = self.indicators.calculate_ema(df, AdaptiveConfig.EMA_MID)
        df['ema13'] = self.indicators.calculate_ema(df, AdaptiveConfig.EMA_SLOW)
        df['rsi'] = self.indicators.calculate_rsi(df)
        
        current_price = df['close'].iloc[-1]
        ema5 = df['ema5'].iloc[-1]
        ema8 = df['ema8'].iloc[-1]
        ema13 = df['ema13'].iloc[-1]
        ema50 = mode_data['ema50']
        rsi = df['rsi'].iloc[-1]
        
        # تحليل الحجم
        volume_data = self.indicators.analyze_volume(df)
        
        # تحليل الشموع
        candle_data = self.indicators.detect_candlestick_patterns(df)
        
        # نظام التسجيل
        total_score = 0
        breakdown = {}
        
        # 1. EMA Pullback (150 نقطة)
        ema_score = self._score_ema_pullback(current_price, ema5, ema8, ema13, ema50)
        total_score += ema_score['score']
        breakdown['ema'] = ema_score
        
        # 2. RSI في منطقة Pullback (80 نقطة)
        if AdaptiveConfig.RSI_PULLBACK_MIN <= rsi <= AdaptiveConfig.RSI_PULLBACK_MAX:
            rsi_score = 80
            breakdown['rsi'] = {'value': rsi, 'score': 80, 'status': 'PULLBACK_ZONE'}
        elif rsi < AdaptiveConfig.RSI_PULLBACK_MIN:
            rsi_score = 50
            breakdown['rsi'] = {'value': rsi, 'score': 50, 'status': 'OVERSOLD'}
        else:
            rsi_score = 0
            breakdown['rsi'] = {'value': rsi, 'score': 0, 'status': 'OVERBOUGHT'}
        
        total_score += rsi_score
        
        # 3. Volume Analysis (50 نقطة)
        total_score += volume_data['score']
        breakdown['volume'] = volume_data
        
        # 4. Candlestick Patterns (50 نقطة)
        total_score += candle_data['score']
        breakdown['candle'] = candle_data
        
        # 5. Higher Lows Confirmation (70 نقطة)
        higher_lows_score = self._check_higher_lows(df)
        total_score += higher_lows_score
        breakdown['higher_lows'] = {'score': higher_lows_score}
        
        # تحديد الإشارة
        signal = 'BUY' if total_score >= AdaptiveConfig.MIN_SCORE_UPTREND else 'WAIT'
        
        if signal == 'BUY':
            targets = self._calculate_targets_uptrend(current_price)
        else:
            targets = None
        
        # بناء ملخص المؤشرات
        indicators_summary = {
            'rsi': rsi,
            'ema_bullish': ema5 > ema8 > ema13,
            'volume_spike': volume_data.get('is_spike', False),
            'higher_lows': higher_lows_score > 0,
            'at_support': False
        }
        
        return {
            'signal': signal,
            'mode': 'STRONG_UPTREND',
            'score': total_score,
            'max_score': 400,
            'percentage': (total_score / 400) * 100,
            'breakdown': breakdown,
            'entry': current_price,
            'targets': targets,
            'reason': self._generate_reason(breakdown, mode_data),
            'indicators': indicators_summary
        }
    
    def _score_ema_pullback(self, price, ema5, ema8, ema13, ema50) -> Dict:
        """تقييم pullback للـ EMA"""
        
        # القرب من EMA 13 أو EMA 50
        dist_ema13 = abs(price - ema13) / ema13
        dist_ema50 = abs(price - ema50) / ema50
        
        if dist_ema13 < 0.005:  # 0.5%
            return {'score': 150, 'level': 'EMA13', 'distance_pct': dist_ema13 * 100}
        elif dist_ema50 < 0.01:  # 1%
            return {'score': 120, 'level': 'EMA50', 'distance_pct': dist_ema50 * 100}
        elif price > ema5 > ema8 > ema13:
            return {'score': 80, 'level': 'ALIGNED', 'distance_pct': 0}
        else:
            return {'score': 30, 'level': 'WEAK', 'distance_pct': 0}
    
    def _check_higher_lows(self, df: pd.DataFrame) -> int:
        """فحص Higher Lows"""
        lows = df['low'].iloc[-20:].values
        
        troughs = []
        for i in range(1, len(lows) - 1):
            if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                troughs.append(lows[i])
        
        if len(troughs) >= 3:
            if troughs[-1] > troughs[-2] > troughs[-3]:
                return 70
            elif troughs[-1] > troughs[-2]:
                return 40
        
        return 0
    
    def _calculate_targets_uptrend(self, entry: float) -> Dict:
        """حساب الأهداف للترند الصاعد"""
        return {
            'target1': entry * (1 + AdaptiveConfig.UPTREND_TARGET1 / 100),
            'target1_pct': AdaptiveConfig.UPTREND_TARGET1,
            'target2': entry * (1 + AdaptiveConfig.UPTREND_TARGET2 / 100),
            'target2_pct': AdaptiveConfig.UPTREND_TARGET2,
            'stop_loss': entry * (1 - AdaptiveConfig.UPTREND_STOPLOSS / 100),
            'stop_loss_pct': AdaptiveConfig.UPTREND_STOPLOSS,
            'max_hours': AdaptiveConfig.UPTREND_MAX_HOURS
        }
    
    def _generate_reason(self, breakdown: Dict, mode_data: Dict) -> str:
        """توليد سبب الإشارة"""
        reasons = []
        
        if 'ema' in breakdown and breakdown['ema']['score'] > 100:
            reasons.append(f"Pullback @ {breakdown['ema']['level']}")
        
        if 'rsi' in breakdown and breakdown['rsi']['score'] > 50:
            reasons.append(f"RSI {breakdown['rsi']['value']:.0f}")
        
        if 'volume' in breakdown and breakdown['volume']['is_spike']:
            reasons.append("Volume Spike")
        
        if 'candle' in breakdown and breakdown['candle']['patterns']:
            reasons.append(breakdown['candle']['patterns'][0])
        
        return " + ".join(reasons) if reasons else "Uptrend Setup"

# ============================================================================
# 4️⃣ DOWNTREND STRATEGY (الارتدادات السريعة)
# ============================================================================

class DowntrendStrategy:
    """
    استراتيجية الترند الهابط
    الهدف: الاستفادة من الارتدادات السريعة ⚡
    الدخول: عند oversold extreme + divergence
    """
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
    
    def analyze(self, symbol: str, df: pd.DataFrame, mode_data: Dict) -> Dict:
        """تحليل فرصة الارتداد في الترند الهابط"""
        
        # حساب المؤشرات
        df['rsi'] = self.indicators.calculate_rsi(df)
        
        current_price = df['close'].iloc[-1]
        rsi = df['rsi'].iloc[-1]
        
        # تحليل Divergence
        divergence_data = self.indicators.detect_divergence(df, df['rsi'])
        
        # تحليل الحجم
        volume_data = self.indicators.analyze_volume(df)
        
        # تحليل الدعم
        support_resistance = self.indicators.find_support_resistance(df)
        
        # تحليل الشموع
        candle_data = self.indicators.detect_candlestick_patterns(df)
        
        # نظام التسجيل
        total_score = 0
        breakdown = {}
        
        # 1. RSI Oversold Extreme (120 نقطة)
        if rsi < AdaptiveConfig.RSI_OVERSOLD_EXTREME:
            rsi_score = 120
            rsi_status = 'EXTREME_OVERSOLD'
        elif rsi < AdaptiveConfig.RSI_OVERSOLD:
            rsi_score = 80
            rsi_status = 'OVERSOLD'
        else:
            rsi_score = 0
            rsi_status = 'NORMAL'
        
        total_score += rsi_score
        breakdown['rsi'] = {'value': rsi, 'score': rsi_score, 'status': rsi_status}
        
        # 2. Bullish Divergence (80 نقطة)
        if divergence_data['found']:
            total_score += divergence_data['score']
        breakdown['divergence'] = divergence_data
        
        # 3. Support Level (70 نقطة)
        dist_from_support = abs(current_price - support_resistance['support']) / current_price
        if dist_from_support < 0.01:  # 1%
            support_score = 70
        elif dist_from_support < 0.02:
            support_score = 40
        else:
            support_score = 0
        
        total_score += support_score
        breakdown['support'] = {
            'level': support_resistance['support'],
            'distance_pct': dist_from_support * 100,
            'score': support_score
        }
        
        # 4. Volume Spike (50 نقطة)
        if volume_data['is_spike']:
            total_score += 50
        breakdown['volume'] = volume_data
        
        # 5. Bullish Candlestick (50 نقطة)
        total_score += candle_data['score']
        breakdown['candle'] = candle_data
        
        # 6. Extreme Lower Wicks (30 نقطة)
        lower_wick_score = self._check_lower_wicks(df)
        total_score += lower_wick_score
        breakdown['lower_wicks'] = {'score': lower_wick_score}
        
        # تحديد الإشارة
        signal = 'BUY' if total_score >= AdaptiveConfig.MIN_SCORE_DOWNTREND else 'WAIT'
        
        if signal == 'BUY':
            targets = self._calculate_targets_downtrend(current_price)
        else:
            targets = None
        
        # بناء ملخص المؤشرات
        indicators_summary = {
            'rsi': rsi,
            'ema_bullish': False,
            'volume_spike': volume_data.get('is_spike', False),
            'divergence': divergence_data['found'],
            'at_support': support_score > 0,
            'higher_lows': False
        }
        
        return {
            'signal': signal,
            'mode': mode_data['mode'],
            'score': total_score,
            'max_score': 400,
            'percentage': (total_score / 400) * 100,
            'breakdown': breakdown,
            'entry': current_price,
            'targets': targets,
            'reason': self._generate_reason(breakdown),
            'indicators': indicators_summary
        }
    
    def _check_lower_wicks(self, df: pd.DataFrame) -> int:
        """فحص Lower Wicks القوية"""
        last_10 = df.iloc[-10:]
        
        strong_wicks = 0
        for _, candle in last_10.iterrows():
            body = abs(candle['close'] - candle['open'])
            lower_wick = min(candle['open'], candle['close']) - candle['low']
            total_range = candle['high'] - candle['low']
            
            if total_range > 0 and lower_wick > total_range * 0.3:
                strong_wicks += 1
        
        if strong_wicks >= 3:
            return 30
        return 0
    
    def _calculate_targets_downtrend(self, entry: float) -> Dict:
        """حساب الأهداف للترند الهابط (سريعة!)"""
        return {
            'target1': entry * (1 + AdaptiveConfig.DOWNTREND_TARGET1 / 100),
            'target1_pct': AdaptiveConfig.DOWNTREND_TARGET1,
            'target2': entry * (1 + AdaptiveConfig.DOWNTREND_TARGET2 / 100),
            'target2_pct': AdaptiveConfig.DOWNTREND_TARGET2,
            'stop_loss': entry * (1 - AdaptiveConfig.DOWNTREND_STOPLOSS / 100),
            'stop_loss_pct': AdaptiveConfig.DOWNTREND_STOPLOSS,
            'max_hours': AdaptiveConfig.DOWNTREND_MAX_HOURS
        }
    
    def _generate_reason(self, breakdown: Dict) -> str:
        """توليد سبب الإشارة"""
        reasons = []
        
        if breakdown['rsi']['score'] >= 120:
            reasons.append(f"RSI {breakdown['rsi']['value']:.0f} Extreme!")
        
        if breakdown['divergence']['found']:
            reasons.append("Bullish Divergence")
        
        if breakdown['support']['score'] > 0:
            reasons.append("Support Touch")
        
        if breakdown['volume']['is_spike']:
            reasons.append("Volume Spike")
        
        return " + ".join(reasons) if reasons else "Oversold Bounce"

# ============================================================================
# 5️⃣ RANGE STRATEGY (مناطق التجميع)
# ============================================================================

class RangeStrategy:
    """
    استراتيجية السوق الجانبي
    الهدف: الدخول من مناطق consolidation 📊
    """
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
    
    def analyze(self, symbol: str, df: pd.DataFrame, mode_data: Dict) -> Dict:
        """تحليل فرصة في السوق الجانبي"""
        
        # حساب المؤشرات
        df['ema5'] = self.indicators.calculate_ema(df, AdaptiveConfig.EMA_FAST)
        df['ema8'] = self.indicators.calculate_ema(df, AdaptiveConfig.EMA_MID)
        df['ema13'] = self.indicators.calculate_ema(df, AdaptiveConfig.EMA_SLOW)
        df['rsi'] = self.indicators.calculate_rsi(df)
        
        current_price = df['close'].iloc[-1]
        
        # نظام التسجيل
        total_score = 0
        breakdown = {}
        
        # 1. Consolidation Detection (100 نقطة)
        consolidation_data = self._detect_consolidation(df)
        if not consolidation_data['found']:
            return {
                'signal': 'WAIT',
                'mode': 'RANGE',
                'score': 0,
                'reason': 'No consolidation detected'
            }
        
        total_score += consolidation_data['score']
        breakdown['consolidation'] = consolidation_data
        
        # 2. EMA Pre-Crossover (80 نقطة)
        ema_data = self._analyze_ema_cross(df)
        total_score += ema_data['score']
        breakdown['ema'] = ema_data
        
        # 3. Volume Pattern (70 نقطة)
        volume_data = self.indicators.analyze_volume(df)
        if volume_data['is_declining']:
            volume_score = 40
        if volume_data['is_spike']:
            volume_score = 70
        else:
            volume_score = volume_data['score']
        
        total_score += volume_score
        breakdown['volume'] = volume_data
        
        # 4. RSI (50 نقطة)
        rsi = df['rsi'].iloc[-1]
        if 45 <= rsi <= 55:
            rsi_score = 50
        elif 40 <= rsi <= 60:
            rsi_score = 30
        else:
            rsi_score = 0
        
        total_score += rsi_score
        breakdown['rsi'] = {'value': rsi, 'score': rsi_score}
        
        # 5. Higher Lows (50 نقطة)
        higher_lows_score = self._check_higher_lows(df)
        total_score += higher_lows_score
        breakdown['higher_lows'] = {'score': higher_lows_score}
        
        # 6. Support/Resistance (50 نقطة)
        sr_data = self.indicators.find_support_resistance(df)
        dist_support = abs(current_price - sr_data['support']) / current_price
        if dist_support < 0.01:
            sr_score = 50
        else:
            sr_score = 0
        
        total_score += sr_score
        breakdown['support'] = {'level': sr_data['support'], 'score': sr_score}
        
        # تحديد الإشارة
        signal = 'BUY' if total_score >= AdaptiveConfig.MIN_SCORE_RANGE else 'WAIT'
        
        if signal == 'BUY':
            targets = self._calculate_targets_range(current_price)
        else:
            targets = None
        
        # بناء ملخص المؤشرات
        indicators_summary = {
            'rsi': rsi,
            'ema_bullish': ema_data['score'] >= 60,
            'volume_spike': volume_data.get('is_spike', False),
            'higher_lows': higher_lows_score > 0,
            'at_support': sr_score > 0,
            'divergence': False
        }
        
        return {
            'signal': signal,
            'mode': 'RANGE',
            'score': total_score,
            'max_score': 400,
            'percentage': (total_score / 400) * 100,
            'breakdown': breakdown,
            'entry': current_price,
            'targets': targets,
            'reason': self._generate_reason(breakdown),
            'indicators': indicators_summary
        }
    
    def _detect_consolidation(self, df: pd.DataFrame) -> Dict:
        """كشف مناطق consolidation"""
        min_candles = AdaptiveConfig.CONSOLIDATION_MIN_CANDLES
        max_candles = AdaptiveConfig.CONSOLIDATION_MAX_CANDLES
        max_range = AdaptiveConfig.CONSOLIDATION_MAX_RANGE_PCT / 100
        
        for lookback in range(max_candles, min_candles - 1, -1):
            window = df.iloc[-lookback:]
            high = window['high'].max()
            low = window['low'].min()
            range_pct = (high - low) / low
            
            if range_pct <= max_range:
                current_price = df['close'].iloc[-1]
                position_in_range = (current_price - low) / (high - low) if high > low else 0.5
                
                return {
                    'found': True,
                    'score': 100,
                    'duration_candles': lookback,
                    'range_pct': range_pct * 100,
                    'high': high,
                    'low': low,
                    'position': position_in_range * 100,
                    'in_discount': position_in_range < 0.4
                }
        
        return {'found': False, 'score': 0}
    
    def _analyze_ema_cross(self, df: pd.DataFrame) -> Dict:
        """تحليل EMA crossover"""
        ema5 = df['ema5'].iloc[-1]
        ema8 = df['ema8'].iloc[-1]
        ema13 = df['ema13'].iloc[-1]
        
        # Full crossover
        if ema5 > ema8 > ema13:
            return {'score': 80, 'status': 'FULL_CROSS'}
        
        # Pre-crossover
        dist_5_8 = abs(ema5 - ema8) / ema8
        if dist_5_8 < 0.003 and ema5 > ema8:
            return {'score': 60, 'status': 'PRE_CROSS'}
        
        return {'score': 20, 'status': 'WEAK'}
    
    def _check_higher_lows(self, df: pd.DataFrame) -> int:
        """فحص Higher Lows"""
        lows = df['low'].iloc[-16:].values
        
        troughs = []
        for i in range(1, len(lows) - 1):
            if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                troughs.append(lows[i])
        
        if len(troughs) >= 2:
            if troughs[-1] > troughs[-2]:
                return 50
        
        return 0
    
    def _calculate_targets_range(self, entry: float) -> Dict:
        """حساب الأهداف للسوق الجانبي"""
        return {
            'target1': entry * (1 + AdaptiveConfig.RANGE_TARGET1 / 100),
            'target1_pct': AdaptiveConfig.RANGE_TARGET1,
            'target2': entry * (1 + AdaptiveConfig.RANGE_TARGET2 / 100),
            'target2_pct': AdaptiveConfig.RANGE_TARGET2,
            'stop_loss': entry * (1 - AdaptiveConfig.RANGE_STOPLOSS / 100),
            'stop_loss_pct': AdaptiveConfig.RANGE_STOPLOSS,
            'max_hours': AdaptiveConfig.RANGE_MAX_HOURS
        }
    
    def _generate_reason(self, breakdown: Dict) -> str:
        """توليد سبب الإشارة"""
        reasons = []
        
        if 'consolidation' in breakdown and breakdown['consolidation']['in_discount']:
            reasons.append(f"Consolidation {breakdown['consolidation']['duration_candles']}c")
        
        if 'ema' in breakdown and breakdown['ema']['score'] >= 60:
            reasons.append("EMA Cross")
        
        if 'volume' in breakdown and breakdown['volume']['is_spike']:
            reasons.append("Volume Breakout")
        
        return " + ".join(reasons) if reasons else "Range Breakout"

# ============================================================================
# 6️⃣ TELEGRAM NOTIFIER (التنبيهات الجذابة)
# ============================================================================

class TelegramNotifier:
    """إرسال تنبيهات Telegram جذابة"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_adaptive_alert(self, signal_data: Dict):
        """إرسال تنبيه متكيف حسب وضع السوق"""
        
        mode = signal_data['mode']
        symbol = signal_data.get('symbol', 'UNKNOWN')
        
        # اختيار الإيموجي والعنوان حسب الوضع
        if mode == 'STRONG_UPTREND':
            emoji = '🚀📈'
            title = 'UPTREND WAVE'
            color = '🟢'
        elif mode in ['STRONG_DOWNTREND', 'DOWNTREND_BOUNCE']:
            emoji = '⚡💎'
            title = 'BOUNCE PLAY'
            color = '🔴'
        else:  # RANGE
            emoji = '📊🎯'
            title = 'RANGE BREAKOUT'
            color = '🟡'
        
        # بناء الرسالة
        message = self._build_message(signal_data, emoji, title, color)
        
        # إرسال
        try:
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json={
                    'chat_id': self.chat_id,
                    'text': message,
                    'parse_mode': 'HTML'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Alert sent for {symbol}")
            else:
                logger.error(f"❌ Telegram error: {response.text}")
        
        except Exception as e:
            logger.error(f"❌ Failed to send alert: {e}")
    
    def _build_message(self, data: Dict, emoji: str, title: str, color: str) -> str:
        """بناء رسالة جذابة"""
        
        symbol = data.get('symbol', 'UNKNOWN')
        mode = data['mode']
        score = data['score']
        max_score = data['max_score']
        percentage = data['percentage']
        entry = data['entry']
        targets = data['targets']
        reason = data['reason']
        indicators = data.get('indicators', {})
        
        # قوة الإشارة
        if percentage >= 70:
            strength = "EXTREME 🔥"
        elif percentage >= 60:
            strength = "HIGH ⭐"
        else:
            strength = "GOOD ✅"
        
        # بناء مختصر المؤشرات
        indicators_text = self._build_indicators_summary(indicators)
        
        # إضافة # قبل اسم العملة
        clean_symbol = symbol.replace('/USDT', '').replace('/', '')
        
        message = f"""
{emoji} <b>{title}</b> {emoji}

{color} <b>#{clean_symbol}</b>
━━━━━━━━━━━━━━━━━
💪 <b>القوة:</b> {strength} ({score}/{max_score}) {indicators_text}
📍 <b>الدخول:</b> ${entry:.6f}

🎯 <b>الأهداف:</b>
  T1: ${targets['target1']:.6f} (+{targets['target1_pct']:.1f}%)
  T2: ${targets['target2']:.6f} (+{targets['target2_pct']:.1f}%)

🛡 <b>وقف الخسارة:</b> ${targets['stop_loss']:.6f} (-{targets['stop_loss_pct']:.1f}%)
⏰ <b>المدة القصوى:</b> {targets['max_hours']:.1f}h

📋 <b>السبب:</b> {reason}

━━━━━━━━━━━━━━━━━
#{mode.replace('_', '')} #{clean_symbol} #CryptoAdaptive
        """.strip()
        
        return message
    
    def _build_indicators_summary(self, indicators: Dict) -> str:
        """بناء مختصر المؤشرات"""
        if not indicators:
            return ""
        
        parts = []
        
        # RSI
        if 'rsi' in indicators:
            rsi_val = indicators['rsi']
            if rsi_val < 30:
                parts.append("RSI⬇️")
            elif rsi_val > 70:
                parts.append("RSI⬆️")
        
        # EMA
        if indicators.get('ema_bullish'):
            parts.append("EMA✅")
        
        # Volume
        if indicators.get('volume_spike'):
            parts.append("VOL🔥")
        
        # Divergence
        if indicators.get('divergence'):
            parts.append("DIV💎")
        
        # Support
        if indicators.get('at_support'):
            parts.append("SUP🛡")
        
        # Higher Lows
        if indicators.get('higher_lows'):
            parts.append("HL📈")
        
        if parts:
            return "| " + " ".join(parts)
        return ""

# ============================================================================
# 7️⃣ ADAPTIVE BOT (البوت الرئيسي)
# ============================================================================

class CryptoAdaptiveBot:
    """البوت الرئيسي المتكيف"""
    
    def __init__(self, api_key: str, api_secret: str, passphrase: str,
                 telegram_token: str, telegram_chat_id: str):
        
        # إعداد Exchange
        self.exchange = ccxt.okx({
            'apiKey': api_key,
            'secret': api_secret,
            'password': passphrase,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        
        # إعداد الاستراتيجيات
        self.mode_detector = MarketModeDetector()
        self.uptrend_strategy = UptrendStrategy()
        self.downtrend_strategy = DowntrendStrategy()
        self.range_strategy = RangeStrategy()
        
        # إعداد التنبيهات
        self.notifier = TelegramNotifier(telegram_token, telegram_chat_id)
        
        logger.info("🚀 Crypto Adaptive Bot v3.0 initialized!")
    
    def run(self):
        """تشغيل البوت"""
        logger.info("🔥 Starting adaptive market scanning...")
        
        while True:
            try:
                logger.info("=" * 60)
                logger.info("📊 Scanning market...")
                
                # جلب العملات
                symbols = self._get_top_symbols()
                logger.info(f"✅ Found {len(symbols)} symbols")
                
                # تحليل متوازي
                with ThreadPoolExecutor(max_workers=AdaptiveConfig.MAX_WORKERS) as executor:
                    executor.map(self._analyze_symbol, symbols)
                
                logger.info(f"⏳ Waiting {AdaptiveConfig.SCAN_INTERVAL_SECONDS}s...")
                time.sleep(AdaptiveConfig.SCAN_INTERVAL_SECONDS)
            
            except KeyboardInterrupt:
                logger.info("⛔ Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Main loop error: {e}", exc_info=True)
                time.sleep(60)
    
    def _get_top_symbols(self) -> List[str]:
        """جلب أفضل 30 عملة حسب الحجم"""
        try:
            markets = self.exchange.fetch_tickers()
            
            usdt_pairs = []
            for symbol, ticker in markets.items():
                if '/USDT' in symbol and ticker.get('quoteVolume', 0) > AdaptiveConfig.MIN_VOLUME_USDT:
                    usdt_pairs.append({
                        'symbol': symbol,
                        'volume': ticker['quoteVolume']
                    })
            
            usdt_pairs.sort(key=lambda x: x['volume'], reverse=True)
            return [p['symbol'] for p in usdt_pairs[:30]]
        
        except Exception as e:
            logger.error(f"Failed to fetch symbols: {e}")
            return []
    
    def _analyze_symbol(self, symbol: str):
        """تحليل عملة واحدة"""
        try:
            # جلب البيانات
            ohlcv = self.exchange.fetch_ohlcv(
                symbol,
                AdaptiveConfig.TIMEFRAME,
                limit=AdaptiveConfig.CANDLES_LOOKBACK
            )
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # كشف وضع السوق
            mode_data = self.mode_detector.detect_mode(df)
            mode = mode_data['mode']
            
            # اختيار الاستراتيجية المناسبة
            if mode == 'STRONG_UPTREND':
                signal = self.uptrend_strategy.analyze(symbol, df, mode_data)
            elif mode in ['STRONG_DOWNTREND', 'DOWNTREND_BOUNCE']:
                signal = self.downtrend_strategy.analyze(symbol, df, mode_data)
            else:  # RANGE, UPTREND_PULLBACK
                signal = self.range_strategy.analyze(symbol, df, mode_data)
            
            # معالجة الإشارة
            if signal['signal'] == 'BUY':
                signal['symbol'] = symbol
                logger.info(f"🔥 {symbol} [{mode}]: BUY! Score {signal['score']}/{signal['max_score']} ({signal['percentage']:.1f}%)")
                self.notifier.send_adaptive_alert(signal)
            
            elif signal.get('score', 0) > 150:
                logger.info(f"📊 {symbol} [{mode}]: {signal['score']}/{signal.get('max_score', 400)} - قريب")
        
        except Exception as e:
            logger.warning(f"⚠️ {symbol} analysis failed: {e}")

# ============================================================================
# 8️⃣ ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        # قراءة الإعدادات
        with open('trading_config.json', 'r') as f:
            config = json.load(f)
        
        # تشغيل البوت
        bot = CryptoAdaptiveBot(
            api_key=config['okx']['api_key'],
            api_secret=config['okx']['api_secret'],
            passphrase=config['okx']['passphrase'],
            telegram_token=config['telegram']['bot_token'],
            telegram_chat_id=config['telegram']['chat_id']
        )
        
        bot.run()
    
    except FileNotFoundError:
        print("❌ trading_config.json not found!")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Startup error: {e}")
        logger.error(f"Startup error: {e}", exc_info=True)
        sys.exit(1)
