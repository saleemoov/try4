#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
💀 Crypto Killer Bot - استراتيجية سفّاح الكريبتو
Win Rate Target: 70%+ 
Pure ICT + Smart Money Concepts + Whale Tracking
"""

import os
import sys
import time
import json
import logging
import threading
from datetime import datetime, timezone, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import ccxt
import pandas as pd
import numpy as np
import requests

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crypto_killer.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# ============================================================================
# CONFIGURATION
# ============================================================================

class KillerConfig:
    """إعدادات استراتيجية سفّاح الكريبتو - النسخة القاتلة 💀"""
    
    # Scoring System
    MIN_SCORE = 200              # الحد الأدنى للدخول (من 400)
    EXTREME_THRESHOLD = 290      # إشارة خرافية
    HIGH_THRESHOLD = 245         # إشارة قوية جداً
    
    # Risk Management - محسّن!
    EXTREME_TARGET1 = 2.0        # T1 سريع (50% من المحفظة)
    EXTREME_TARGET2 = 3.5        # T2 (الباقي)
    EXTREME_SL = 1.0             # SL
    
    HIGH_TARGET1 = 2.0           # T1 سريع
    HIGH_TARGET2 = 3.5           # T2
    HIGH_SL = 1.2                # SL
    
    GOOD_TARGET1 = 2.0           # T1 سريع
    GOOD_TARGET2 = 3.5           # T2
    GOOD_SL = 1.5                # SL
    
    # Range Detection (NEW!)
    RANGE_MAX_PCT = 1.8          # Range أقصى 1.8%
    RANGE_MIN_DURATION = 16      # 4 ساعات على الأقل (16 شمعة 15m)
    RANGE_MAX_DURATION = 32      # 8 ساعات كحد أقصى
    
    # EMA Settings (NEW!)
    EMA_FAST = 5
    EMA_MID = 8
    EMA_SLOW = 13
    EMA_PROXIMITY = 0.003        # 0.3% قرب للتقاطع المبكر
    
    # Volume (NEW!)
    VOLUME_DECLINING_CANDLES = 3 # آخر 3 شموع تتناقص
    VOLUME_LOW_THRESHOLD = 0.7   # 70% من المتوسط
    BREAKOUT_VOLUME_MIN = 1.2    # 120% volume عند الكسر
    
    # Exit Strategy (NEW!)
    MAX_TRADE_HOURS = 3          # خروج إجباري بعد 3 ساعات
    TRAILING_STOP_TRIGGER = 3.0  # تفعيل trailing عند 3%
    TRAILING_STOP_PCT = 1.5      # trailing stop 1.5%
    QUICK_EXIT_TIME = 60         # T1 خلال ساعة
    
    # Volatility-Based Scoring (أذكى من Session Timing!)
    HIGH_VOLATILITY_THRESHOLD = 1.3    # ATR أعلى من 1.3x المتوسط
    MEDIUM_VOLATILITY_THRESHOLD = 1.0  # ATR متوسط
    HIGH_VOLATILITY_SCORE = 50         # نقاط للتذبذب العالي
    MEDIUM_VOLATILITY_SCORE = 35       # نقاط للتذبذب المتوسط
    LOW_VOLATILITY_SCORE = 20          # نقاط للتذبذب المنخفض
    
    # Market Structure
    SWING_PERIOD = 10            # فترة البحث عن Swing Points
    STRUCTURE_LOOKBACK = 3       # آخر 3 قمم/قيعان
    BOS_THRESHOLD = 0.005        # 0.5% فوق القمة = Break of Structure
    
    # Order Blocks
    OB_BODY_THRESHOLD = 0.6      # 60% من الشمعة = body قوي
    OB_VOLUME_MULTIPLIER = 2.0   # حجم 2x = دخول مؤسسي
    OB_RALLY_MIN = 0.02          # صعود 2%+ بعد OB
    OB_MAX_TOUCHES = 1           # اختبار واحد فقط
    OB_FRESH_ONLY = True         # Order Blocks جديدة فقط
    OB_PROXIMITY_THRESHOLD = 0.015  # السعر قريب من OB (1.5%)
    
    # Fair Value Gaps
    FVG_MIN_SIZE = 0.008         # فجوة 0.8%+ فقط
    FVG_MAX_FILLED = 70          # مملوءة أقل من 70%
    
    # Liquidity
    EQUAL_LEVEL_TOLERANCE = 0.003  # 0.3% تفاوت للمستويات المتساوية
    LIQUIDITY_VOLUME_MULTIPLIER = 1.5  # 1.5x حجم = Stop Hunt
    
    # Whale Detection
    WHALE_VOLUME_SPIKE = 5.0     # حجم 5x = حوت نشط
    WHALE_MIN_SCORE = 50         # حد أدنى لنشاط الحيتان
    
    # Data & Performance
    CANDLES_LOOKBACK = 500       # عدد الشموع للتحليل
    TIMEFRAME = '15m'            # الإطار الزمني - محسّن لـ ICT
    MIN_VOLUME_USDT = 5_000_000  # 5 مليون حد أدنى
    MAX_CONCURRENT = 10          # تحليل متوازي
    SCAN_INTERVAL = 300          # 5 دقائق بين المسحات
    
    # Higher Lows (NEW!)
    HIGHER_LOWS_MIN = 3          # 3 قيعان صاعدة على الأقل
    
    # Lower Wicks (NEW!)
    LOWER_WICK_MIN = 0.3         # 30% من الشمعة
    
    # Alerts
    AVOID_DUPLICATE_HOURS = 2    # لا تكرار خلال ساعتين

# ============================================================================
# MARKET STRUCTURE ANALYZER
# ============================================================================

class MarketStructureAnalyzer:
    """
    تحليل هيكل السوق - أساس الاستراتيجية
    - Bullish BOS: استمرار صعود
    - Bearish BOS: استمرار هبوط
    - Bullish CHoCH: انعكاس صاعد (ذهبي!)
    - Bearish CHoCH: انعكاس هابط
    - Range: لا تدخل
    """
    
    def analyze_structure(self, df: pd.DataFrame) -> Dict:
        """تحديد هيكل السوق الحالي"""
        try:
            swing_highs = self._find_swing_highs(df)
            swing_lows = self._find_swing_lows(df)
            
            if len(swing_highs) < 3 or len(swing_lows) < 3:
                return {'structure': 'RANGE', 'strength': 0}
            
            recent_highs = swing_highs[-KillerConfig.STRUCTURE_LOOKBACK:]
            recent_lows = swing_lows[-KillerConfig.STRUCTURE_LOOKBACK:]
            current_price = df['close'].iloc[-1]
            
            # Bullish Structure: Higher Highs + Higher Lows
            is_hh = all(recent_highs[i]['price'] > recent_highs[i-1]['price'] 
                       for i in range(1, len(recent_highs)))
            is_hl = all(recent_lows[i]['price'] > recent_lows[i-1]['price'] 
                       for i in range(1, len(recent_lows)))
            
            if is_hh and is_hl:
                # هل كسر القمة السابقة بقوة؟
                prev_high = swing_highs[-2]['price']
                if current_price > prev_high * (1 + KillerConfig.BOS_THRESHOLD):
                    return {
                        'structure': 'BULLISH_BOS',
                        'strength': 120,
                        'last_low': recent_lows[-1]['price'],
                        'invalidation': recent_lows[-2]['price'],
                        'prev_high': prev_high
                    }
            
            # Bullish CHoCH: كسر قمة بعد هبوط
            is_ll = all(recent_highs[i]['price'] < recent_highs[i-1]['price'] 
                       for i in range(1, len(recent_highs)-1))
            
            if is_ll and current_price > swing_highs[-2]['price']:
                return {
                    'structure': 'BULLISH_CHoCH',
                    'strength': 150,  # 🔥 الأقوى!
                    'entry_zone': (recent_lows[-1]['price'], recent_lows[-1]['price'] * 1.01),
                    'invalidation': recent_lows[-2]['price'],
                    'breakout_level': swing_highs[-2]['price']
                }
            
            # Bearish Structure
            is_lh = all(recent_highs[i]['price'] < recent_highs[i-1]['price'] 
                       for i in range(1, len(recent_highs)))
            is_ll_bear = all(recent_lows[i]['price'] < recent_lows[i-1]['price'] 
                            for i in range(1, len(recent_lows)))
            
            if is_lh and is_ll_bear:
                return {'structure': 'BEARISH_BOS', 'strength': 0}  # لا ندخل
            
            return {'structure': 'RANGE', 'strength': 0}
            
        except Exception as e:
            logging.warning(f"Market structure analysis failed: {e}")
            return {'structure': 'RANGE', 'strength': 0}
    
    def _find_swing_highs(self, df: pd.DataFrame) -> List[Dict]:
        """البحث عن القمم المحلية"""
        highs = []
        period = KillerConfig.SWING_PERIOD
        
        for i in range(period, len(df) - period):
            if df['high'].iloc[i] == df['high'].iloc[i-period:i+period+1].max():
                highs.append({
                    'price': df['high'].iloc[i],
                    'index': i,
                    'time': df.index[i]
                })
        return highs
    
    def _find_swing_lows(self, df: pd.DataFrame) -> List[Dict]:
        """البحث عن القيعان المحلية"""
        lows = []
        period = KillerConfig.SWING_PERIOD
        
        for i in range(period, len(df) - period):
            if df['low'].iloc[i] == df['low'].iloc[i-period:i+period+1].min():
                lows.append({
                    'price': df['low'].iloc[i],
                    'index': i,
                    'time': df.index[i]
                })
        return lows

# ============================================================================
# SMART ORDER BLOCK DETECTOR
# ============================================================================

class SmartOrderBlockDetector:
    """
    كشف Order Blocks المؤسساتية
    - شمعة هابطة قوية + Volume ضخم
    - بعدها صعود متفجر (3+ شموع)
    - Fresh فقط (0-1 اختبار)
    """
    
    def find_institutional_order_blocks(self, df: pd.DataFrame) -> List[Dict]:
        """البحث عن OB المؤسساتية"""
        order_blocks = []
        avg_volume = df['volume'].rolling(50).mean()
        
        for i in range(20, len(df) - 5):
            candle = df.iloc[i]
            
            # 1. شمعة هابطة قوية
            body = abs(candle['close'] - candle['open'])
            full_range = candle['high'] - candle['low']
            
            if full_range == 0:
                continue
            
            is_bearish = candle['close'] < candle['open']
            strong_body = body / full_range > KillerConfig.OB_BODY_THRESHOLD
            high_volume = candle['volume'] > avg_volume.iloc[i] * KillerConfig.OB_VOLUME_MULTIPLIER
            
            if is_bearish and strong_body and high_volume:
                # 2. بعدها صعود قوي
                next_3 = df.iloc[i+1:i+4]
                all_bullish = all(next_3['close'] > next_3['open'])
                
                if all_bullish:
                    rally_size = (df['close'].iloc[i+3] - df['close'].iloc[i]) / df['close'].iloc[i]
                    
                    if rally_size > KillerConfig.OB_RALLY_MIN:
                        # 3. حساب عدد الاختبارات
                        ob_high = candle['high']
                        ob_low = candle['low']
                        touches = 0
                        
                        for j in range(i+4, len(df)):
                            if df['low'].iloc[j] <= ob_high and df['high'].iloc[j] >= ob_low:
                                touches += 1
                        
                        if touches <= KillerConfig.OB_MAX_TOUCHES:
                            order_blocks.append({
                                'high': ob_high,
                                'low': ob_low,
                                'mid': (ob_high + ob_low) / 2,
                                'volume': candle['volume'],
                                'strength': rally_size * 100,
                                'touches': touches,
                                'index': i
                            })
        
        return sorted(order_blocks, key=lambda x: x['strength'], reverse=True)

# ============================================================================
# VOLATILITY ANALYZER
# ============================================================================

class VolatilityAnalyzer:
    """
    محلل التذبذب - أذكى من Session Timing!
    يقيس التذبذب الفعلي بدلاً من الاعتماد على الوقت فقط
    """
    
    def get_volatility_score(self, df: pd.DataFrame) -> Dict:
        """
        حساب نقاط التذبذب بناءً على ATR
        - High Volatility (1.3x+): 50 نقطة
        - Medium Volatility (1.0-1.3x): 35 نقطة
        - Low Volatility (<1.0x): 20 نقطة
        """
        try:
            # حساب ATR (Average True Range)
            atr = df['high'].rolling(14).mean() - df['low'].rolling(14).mean()
            current_atr = atr.iloc[-1]
            avg_atr = atr.mean()
            
            if avg_atr == 0:
                return {'score': KillerConfig.LOW_VOLATILITY_SCORE, 'ratio': 0, 'level': 'LOW'}
            
            volatility_ratio = current_atr / avg_atr
            
            # تصنيف التذبذب
            if volatility_ratio >= KillerConfig.HIGH_VOLATILITY_THRESHOLD:
                return {
                    'score': KillerConfig.HIGH_VOLATILITY_SCORE,
                    'ratio': volatility_ratio,
                    'level': 'HIGH',
                    'reason': f'تذبذب عالي ({volatility_ratio:.2f}x)'
                }
            elif volatility_ratio >= KillerConfig.MEDIUM_VOLATILITY_THRESHOLD:
                return {
                    'score': KillerConfig.MEDIUM_VOLATILITY_SCORE,
                    'ratio': volatility_ratio,
                    'level': 'MEDIUM',
                    'reason': f'تذبذب متوسط ({volatility_ratio:.2f}x)'
                }
            else:
                return {
                    'score': KillerConfig.LOW_VOLATILITY_SCORE,
                    'ratio': volatility_ratio,
                    'level': 'LOW',
                    'reason': f'تذبذب منخفض ({volatility_ratio:.2f}x)'
                }
        
        except Exception as e:
            logging.warning(f"Volatility analysis failed: {e}")
            return {'score': KillerConfig.MEDIUM_VOLATILITY_SCORE, 'ratio': 1.0, 'level': 'MEDIUM'}

# ============================================================================
# FVG HUNTER
# ============================================================================

class FVGHunter:
    """
    صياد Fair Value Gaps
    - فجوات كبيرة (0.8%+)
    - غير مملوءة (<70%)
    - خلال London/NY Session (أفضلية)
    """
    
    def detect_premium_fvg(self, df: pd.DataFrame) -> List[Dict]:
        """كشف FVG عالية الجودة"""
        fvg_zones = []
        
        for i in range(1, len(df) - 1):
            # Bullish FVG: gap بين candle[i-1].high و candle[i+1].low
            gap_size = df['low'].iloc[i+1] - df['high'].iloc[i-1]
            
            if gap_size > 0:
                gap_percent = gap_size / df['close'].iloc[i] * 100
                
                if gap_percent > KillerConfig.FVG_MIN_SIZE * 100:
                    # Volatility Score (بدلاً من Session)
                    # سيتم حسابه لاحقاً في CryptoKillerStrategy
                    volatility_score = 0  # placeholder
                    
                    # حساب نسبة الملء
                    filled_percent = 0
                    for j in range(i+2, len(df)):
                        if df['low'].iloc[j] <= df['high'].iloc[i-1]:
                            penetration = (df['high'].iloc[i-1] - df['low'].iloc[j]) / gap_size
                            filled_percent = max(filled_percent, penetration * 100)
                    
                    if filled_percent < KillerConfig.FVG_MAX_FILLED:
                        fvg_zones.append({
                            'type': 'BULLISH',
                            'top': df['low'].iloc[i+1],
                            'bottom': df['high'].iloc[i-1],
                            'mid': (df['low'].iloc[i+1] + df['high'].iloc[i-1]) / 2,
                            'size_percent': gap_percent,
                            'filled_percent': filled_percent,
                            'volatility_score': volatility_score,  # سيتم حسابه لاحقاً
                            'total_score': (gap_percent * 20) - filled_percent,  # base score
                            'index': i
                        })
        
        return sorted(fvg_zones, key=lambda x: x['total_score'], reverse=True)

# ============================================================================
# LIQUIDITY HUNTER
# ============================================================================

class LiquidityHunter:
    """
    صياد السيولة - كشف Stop Hunts
    - Equal Highs/Lows
    - Round Numbers
    - Stop Hunt Detection
    """
    
    def find_liquidity_pools(self, df: pd.DataFrame) -> List[Dict]:
        """البحث عن مناطق السيولة"""
        pools = []
        
        # Equal Highs
        equal_highs = self._find_equal_levels(df['high'])
        for level in equal_highs:
            pools.append({
                'type': 'SELL_SIDE_LIQUIDITY',
                'price': level['price'],
                'touches': level['touches'],
                'strength': level['touches'] * 30,
                'action': 'BUY_AFTER_SWEEP'
            })
        
        # Equal Lows
        equal_lows = self._find_equal_levels(df['low'])
        for level in equal_lows:
            pools.append({
                'type': 'BUY_SIDE_LIQUIDITY',
                'price': level['price'],
                'touches': level['touches'],
                'strength': level['touches'] * 30,
                'action': 'BUY_AFTER_SWEEP'
            })
        
        # Round Numbers
        current_price = df['close'].iloc[-1]
        nearest_1000 = round(current_price / 1000) * 1000
        nearest_500 = round(current_price / 500) * 500
        
        pools.append({
            'type': 'PSYCHOLOGICAL',
            'price': nearest_1000,
            'strength': 50,
            'action': 'WATCH'
        })
        
        return pools
    
    def _find_equal_levels(self, series: pd.Series) -> List[Dict]:
        """البحث عن مستويات متساوية"""
        levels = []
        tolerance = KillerConfig.EQUAL_LEVEL_TOLERANCE
        
        # تجميع المستويات المتقاربة
        for i in range(len(series) - 20):
            price = series.iloc[i]
            touches = 1
            
            for j in range(i+1, min(i+50, len(series))):
                if abs(series.iloc[j] - price) / price < tolerance:
                    touches += 1
            
            if touches >= 2:
                levels.append({'price': price, 'touches': touches})
        
        # إزالة المكررات
        unique_levels = []
        for level in levels:
            is_duplicate = any(abs(level['price'] - ul['price']) / level['price'] < tolerance 
                             for ul in unique_levels)
            if not is_duplicate:
                unique_levels.append(level)
        
        return unique_levels
    
    def detect_liquidity_sweep(self, df: pd.DataFrame, pool: Dict) -> Dict:
        """كشف Stop Hunt"""
        last_3 = df.iloc[-3:]
        avg_volume = df['volume'].rolling(20).mean().iloc[-1]
        
        for idx, candle in last_3.iterrows():
            # كسر المستوى بـ wick ثم أغلق فوقه
            if (candle['low'] < pool['price'] < candle['high'] and
                candle['close'] > pool['price'] and
                candle['volume'] > avg_volume * KillerConfig.LIQUIDITY_VOLUME_MULTIPLIER):
                
                return {
                    'swept': True,
                    'strength': 100,
                    'entry_price': pool['price'] * 1.002,
                    'stop_loss': pool['price'] * 0.997
                }
        
        return {'swept': False}

# ============================================================================
# WHALE WATCHER
# ============================================================================

class WhaleWatcher:
    """
    مراقب الحيتان
    - Volume Spikes (5x+)
    - Clean Accumulation
    - Support Defense
    """
    
    def analyze_whale_activity(self, df: pd.DataFrame) -> Dict:
        """تحليل نشاط الحيتان"""
        whale_score = 0
        signals = []
        
        # 1. Volume Spike
        avg_volume = df['volume'].rolling(50).mean().iloc[-1]
        recent_volume = df['volume'].iloc[-3:].mean()
        
        if recent_volume > avg_volume * KillerConfig.WHALE_VOLUME_SPIKE:
            whale_score += 50
            signals.append({
                'type': 'VOLUME_SPIKE',
                'message': f'🐋 حجم {KillerConfig.WHALE_VOLUME_SPIKE}x - حيتان نشطة!',
                'strength': 50
            })
        
        # 2. Clean Accumulation (Bodies > Wicks)
        last_10 = df.iloc[-10:]
        avg_body = abs(last_10['close'] - last_10['open']).mean()
        avg_range = (last_10['high'] - last_10['low']).mean()
        avg_wick = avg_range - avg_body
        
        if avg_body > avg_wick * 1.5:
            whale_score += 30
            signals.append({
                'type': 'CLEAN_ACCUMULATION',
                'message': 'تجميع نظيف - الحيتان تشتري',
                'strength': 30
            })
        
        # 3. Support Defense (Lower Wicks كبيرة)
        for i in range(-5, 0):
            candle = df.iloc[i]
            is_bullish = candle['close'] > candle['open']
            lower_wick = (candle['open'] if is_bullish else candle['close']) - candle['low']
            body = abs(candle['close'] - candle['open'])
            
            if body > 0 and lower_wick > body * 2:
                whale_score += 20
                signals.append({
                    'type': 'SUPPORT_DEFENSE',
                    'message': f'دفاع قوي عند {candle["low"]:.2f}',
                    'strength': 20
                })
                break
        
        return {
            'whale_score': whale_score,
            'signals': signals,
            'is_active': whale_score >= KillerConfig.WHALE_MIN_SCORE
        }

# ============================================================================
# RANGE DETECTOR (NEW!)
# ============================================================================

class RangeDetector:
    """
    كاشف المستطيلات الذهبية 💎
    - Range ضيق (<1.8%)
    - مدة 4-8 ساعات
    - Consolidation واضح
    """
    
    def detect_consolidation(self, df: pd.DataFrame) -> Dict:
        """كشف Range/Consolidation"""
        try:
            # آخر N شمعة للتحليل
            lookback = int(KillerConfig.RANGE_MAX_DURATION)
            recent = df.tail(lookback)
            
            if len(recent) < KillerConfig.RANGE_MIN_DURATION:
                return {'in_range': False, 'reason': 'بيانات غير كافية'}
            
            # حساب Range
            high = recent['high'].max()
            low = recent['low'].min()
            range_pct = ((high - low) / low) * 100
            
            # التحقق من Range الضيق
            if range_pct > KillerConfig.RANGE_MAX_PCT:
                return {
                    'in_range': False,
                    'range_pct': range_pct,
                    'reason': f'Range واسع ({range_pct:.1f}%)'
                }
            
            # التحقق من المدة
            # نعد الشموع التي في نطاق ضيق
            candles_in_range = 0
            for i in range(len(recent)):
                candle_high = recent.iloc[i]['high']
                candle_low = recent.iloc[i]['low']
                if candle_low >= low * 0.995 and candle_high <= high * 1.005:
                    candles_in_range += 1
            
            if candles_in_range < KillerConfig.RANGE_MIN_DURATION:
                return {
                    'in_range': False,
                    'reason': f'مدة قصيرة ({candles_in_range} شموع)'
                }
            
            # نجح! Range مثالي
            current_price = df['close'].iloc[-1]
            position_in_range = ((current_price - low) / (high - low)) if (high - low) > 0 else 0.5
            
            return {
                'in_range': True,
                'range_pct': range_pct,
                'duration': candles_in_range,
                'high': high,
                'low': low,
                'position': position_in_range,
                'is_discount': position_in_range < 0.4,  # أقل من 40% = Discount
                'score': 60 if position_in_range < 0.4 else 40,
                'reason': f'Range {range_pct:.1f}% لمدة {candles_in_range} شموع'
            }
            
        except Exception as e:
            logging.warning(f"Range detection failed: {e}")
            return {'in_range': False, 'reason': str(e)}

# ============================================================================
# EMA ANALYZER (NEW!)
# ============================================================================

class EMAAnalyzer:
    """
    محلل EMA 5/8/13 + Pre-Crossover Detection
    - تقاطع مبكر (قبل 1-2 شمعة)
    - Momentum confirmation
    """
    
    def analyze_ema_setup(self, df: pd.DataFrame) -> Dict:
        """تحليل EMA وكشف التقاطع المبكر"""
        try:
            # حساب EMAs
            ema5 = df['close'].ewm(span=KillerConfig.EMA_FAST, adjust=False).mean()
            ema8 = df['close'].ewm(span=KillerConfig.EMA_MID, adjust=False).mean()
            ema13 = df['close'].ewm(span=KillerConfig.EMA_SLOW, adjust=False).mean()
            
            current_ema5 = ema5.iloc[-1]
            current_ema8 = ema8.iloc[-1]
            current_ema13 = ema13.iloc[-1]
            
            # التقاطع الكامل (Full Crossover)
            full_bullish = (current_ema5 > current_ema8) and (current_ema8 > current_ema13)
            
            # التقاطع المبكر (Pre-Crossover)
            ema5_near_8 = abs(current_ema5 - current_ema8) / current_ema8 < KillerConfig.EMA_PROXIMITY
            ema8_near_13 = abs(current_ema8 - current_ema13) / current_ema13 < KillerConfig.EMA_PROXIMITY
            
            # Momentum: EMA 5 يصعد
            ema5_rising = ema5.iloc[-1] > ema5.iloc[-3]
            ema5_slope = (ema5.iloc[-1] - ema5.iloc[-3]) / ema5.iloc[-3]
            
            # Pre-crossover مع momentum
            early_signal = (
                (current_ema5 >= current_ema8 * 0.998) and
                (current_ema8 >= current_ema13 * 0.998) and
                ema5_rising and
                (ema5_slope > 0.002)  # يصعد بسرعة
            )
            
            # النقاط
            if full_bullish:
                score = 70
                status = 'FULL_CROSS'
                reason = 'EMA 5>8>13 ✅'
            elif early_signal:
                score = 55
                status = 'PRE_CROSS'
                reason = 'EMA قريب من التقاطع (مبكر!)'
            elif ema5_near_8 and ema5_rising:
                score = 40
                status = 'PREPARING'
                reason = 'EMA يستعد للتقاطع'
            else:
                score = 0
                status = 'NO_SIGNAL'
                reason = 'EMA ليس جاهزاً'
            
            return {
                'score': score,
                'status': status,
                'reason': reason,
                'ema5': current_ema5,
                'ema8': current_ema8,
                'ema13': current_ema13,
                'full_bullish': full_bullish,
                'early_signal': early_signal,
                'slope': ema5_slope
            }
            
        except Exception as e:
            logging.warning(f"EMA analysis failed: {e}")
            return {'score': 0, 'status': 'ERROR', 'reason': str(e)}
    
    def check_ema_exit(self, df: pd.DataFrame) -> bool:
        """فحص إشارة خروج EMA (EMA 5 تقطع تحت EMA 8)"""
        try:
            ema5 = df['close'].ewm(span=KillerConfig.EMA_FAST, adjust=False).mean()
            ema8 = df['close'].ewm(span=KillerConfig.EMA_MID, adjust=False).mean()
            
            # Death Cross
            return ema5.iloc[-1] < ema8.iloc[-1]
        except:
            return False

# ============================================================================
# VOLUME ANALYZER (NEW!)
# ============================================================================

class VolumeAnalyzer:
    """
    محلل Volume المتقدم
    - Volume declining pattern
    - Breakout volume confirmation
    """
    
    def analyze_volume_pattern(self, df: pd.DataFrame) -> Dict:
        """تحليل نمط Volume"""
        try:
            volume = df['volume']
            avg_volume = volume.rolling(20).mean().iloc[-1]
            
            # آخر N شموع
            recent_volume = volume.tail(KillerConfig.VOLUME_DECLINING_CANDLES)
            
            # Volume declining؟
            is_declining = all(
                recent_volume.iloc[i] > recent_volume.iloc[i+1]
                for i in range(len(recent_volume)-1)
            )
            
            # Volume منخفض؟
            current_volume = volume.iloc[-1]
            is_low = current_volume < avg_volume * KillerConfig.VOLUME_LOW_THRESHOLD
            
            # النقاط
            if is_declining and is_low:
                score = 50
                reason = f'Volume يتناقص ({current_volume/avg_volume:.1%} من المتوسط)'
            elif is_low:
                score = 30
                reason = f'Volume منخفض'
            else:
                score = 0
                reason = 'Volume عادي أو مرتفع'
            
            return {
                'score': score,
                'is_declining': is_declining,
                'is_low': is_low,
                'current': current_volume,
                'average': avg_volume,
                'ratio': current_volume / avg_volume if avg_volume > 0 else 1,
                'reason': reason
            }
            
        except Exception as e:
            logging.warning(f"Volume analysis failed: {e}")
            return {'score': 0, 'reason': str(e)}
    
    def check_breakout_volume(self, df: pd.DataFrame) -> bool:
        """تحقق من Volume الكسر"""
        try:
            volume = df['volume']
            avg_volume = volume.rolling(20).mean().iloc[-1]
            current_volume = volume.iloc[-1]
            
            return current_volume >= avg_volume * KillerConfig.BREAKOUT_VOLUME_MIN
        except:
            return False

# ============================================================================
# PATTERN DETECTOR (NEW!)
# ============================================================================

class PatternDetector:
    """
    كاشف الأنماط الإضافية
    - Higher lows
    - Lower wicks
    - Break confirmation
    """
    
    def detect_higher_lows(self, df: pd.DataFrame) -> Dict:
        """كشف قيعان صاعدة"""
        try:
            lows = df['low'].tail(15)
            
            # إيجاد local lows (swing lows)
            swing_lows = []
            for i in range(2, len(lows)-2):
                if lows.iloc[i] < lows.iloc[i-1] and lows.iloc[i] < lows.iloc[i+1]:
                    swing_lows.append(lows.iloc[i])
            
            if len(swing_lows) < KillerConfig.HIGHER_LOWS_MIN:
                return {
                    'found': False,
                    'score': 0,
                    'reason': f'قيعان قليلة ({len(swing_lows)})'
                }
            
            # التحقق من الصعود
            last_lows = swing_lows[-KillerConfig.HIGHER_LOWS_MIN:]
            is_ascending = all(
                last_lows[i] < last_lows[i+1]
                for i in range(len(last_lows)-1)
            )
            
            if is_ascending:
                return {
                    'found': True,
                    'score': 45,
                    'count': len(last_lows),
                    'reason': f'{len(last_lows)} قيعان صاعدة ✅'
                }
            else:
                return {
                    'found': False,
                    'score': 0,
                    'reason': 'القيعان ليست صاعدة'
                }
                
        except Exception as e:
            logging.warning(f"Higher lows detection failed: {e}")
            return {'found': False, 'score': 0, 'reason': str(e)}
    
    def check_lower_wicks(self, df: pd.DataFrame) -> Dict:
        """فحص Lower wicks الطويلة"""
        try:
            recent = df.tail(10)
            strong_wicks = 0
            
            for _, candle in recent.iterrows():
                low = candle['low']
                close = candle['close']
                open_price = candle['open']
                high = candle['high']
                
                full_range = high - low
                if full_range == 0:
                    continue
                
                lower_wick = min(close, open_price) - low
                wick_ratio = lower_wick / full_range
                
                if wick_ratio >= KillerConfig.LOWER_WICK_MIN:
                    strong_wicks += 1
            
            if strong_wicks >= 3:
                return {
                    'found': True,
                    'score': 35,
                    'count': strong_wicks,
                    'reason': f'{strong_wicks} lower wicks قوية (rejection!)'
                }
            else:
                return {
                    'found': False,
                    'score': 0,
                    'reason': 'lower wicks ضعيفة'
                }
                
        except Exception as e:
            logging.warning(f"Lower wicks check failed: {e}")
            return {'found': False, 'score': 0, 'reason': str(e)}

# ============================================================================
# CRYPTO KILLER STRATEGY (MAIN ENGINE)
# ============================================================================

class CryptoKillerStrategy:
    """
    💀 محرك استراتيجية سفّاح الكريبتو - النسخة القاتلة!
    نظام النقاط المحسّن: 550 نقطة كحد أقصى
    - Range Detection: 60
    - EMA Setup: 70
    - Volume Pattern: 50
    - Higher Lows: 45
    - Lower Wicks: 35
    - Market Structure: 150
    - Order Block: 80
    - Volatility: 40
    - Liquidity: 30
    - Whales: 30
    """
    
    def __init__(self):
        # المحللات الأصلية
        self.market_structure = MarketStructureAnalyzer()
        self.ob_detector = SmartOrderBlockDetector()
        self.fvg_hunter = FVGHunter()
        self.liq_hunter = LiquidityHunter()
        self.whale_watcher = WhaleWatcher()
        self.volatility_analyzer = VolatilityAnalyzer()
        
        # المحللات الجديدة (السلاح السري!)
        self.range_detector = RangeDetector()
        self.ema_analyzer = EMAAnalyzer()
        self.volume_analyzer = VolumeAnalyzer()
        self.pattern_detector = PatternDetector()
    
    def generate_signal(self, symbol: str, df: pd.DataFrame) -> Dict:
        """توليد إشارة تداول مع نظام النقاط المحسّن"""
        
        total_score = 0
        breakdown = {}
        current_price = df['close'].iloc[-1]
        
        # ═══════════════════════════════════════
        # 🔥 الفلاتر الجديدة (يجب النجاح قبل المتابعة!)
        # ═══════════════════════════════════════
        
        # 1. Range Detection (إلزامي!)
        range_data = self.range_detector.detect_consolidation(df)
        if not range_data['in_range']:
            return {
                'signal': 'WAIT',
                'score': 0,
                'reason': f'خارج Range: {range_data["reason"]}'
            }
        
        breakdown['range'] = range_data
        total_score += range_data['score']
        
        # 2. EMA Setup (إلزامي!)
        ema_data = self.ema_analyzer.analyze_ema_setup(df)
        if ema_data['score'] < 40:  # على الأقل Preparing
            return {
                'signal': 'WAIT',
                'score': total_score,
                'reason': f'EMA ليس جاهزاً: {ema_data["reason"]}'
            }
        
        breakdown['ema'] = ema_data
        total_score += ema_data['score']
        
        # 3. Volume Pattern (اختياري لكن مهم)
        volume_data = self.volume_analyzer.analyze_volume_pattern(df)
        breakdown['volume'] = volume_data
        total_score += volume_data['score']
        
        # 4. Higher Lows (اختياري)
        higher_lows = self.pattern_detector.detect_higher_lows(df)
        if higher_lows['found']:
            breakdown['higher_lows'] = higher_lows
            total_score += higher_lows['score']
        
        # 5. Lower Wicks (اختياري)
        lower_wicks = self.pattern_detector.check_lower_wicks(df)
        if lower_wicks['found']:
            breakdown['lower_wicks'] = lower_wicks
            total_score += lower_wicks['score']
        
        # 6. Breakout Volume Confirmation
        has_breakout_volume = self.volume_analyzer.check_breakout_volume(df)
        if not has_breakout_volume:
            # لا نرفض الإشارة، لكن نخفض النقاط
            total_score = int(total_score * 0.9)
        
        # ═══════════════════════════════════════
        # 1️⃣ MARKET STRUCTURE (150 max)
        # ═══════════════════════════════════════
        structure = self.market_structure.analyze_structure(df)
        
        if structure['structure'] == 'BULLISH_CHoCH':
            structure_score = 150  # 🔥
            breakdown['structure'] = {
                'type': 'CHoCH (انعكاس)',
                'score': 150,
                'reason': 'أقوى إشارة - انعكاس صاعد جديد'
            }
        elif structure['structure'] == 'BULLISH_BOS':
            structure_score = 120
            breakdown['structure'] = {
                'type': 'BOS (استمرار)',
                'score': 120,
                'reason': 'ترند صاعد قوي'
            }
        elif structure['structure'] == 'RANGE':
            return {'signal': 'WAIT', 'score': 0, 'reason': 'السوق في Range'}
        else:
            structure_score = 0
        
        total_score += structure_score
        
        # ═══════════════════════════════════════
        # 2️⃣ ORDER BLOCK (80 max)
        # ═══════════════════════════════════════
        order_blocks = self.ob_detector.find_institutional_order_blocks(df)
        ob_score = 0
        
        for ob in order_blocks[:3]:
            if ob['low'] <= current_price <= ob['high']:
                ob_score = min(80, ob['strength'])
                breakdown['order_block'] = {
                    'price': ob['mid'],
                    'score': ob_score,
                    'touches': ob['touches'],
                    'reason': f'داخل OB قوي (قوة: {ob["strength"]:.0f})'
                }
                break
            elif abs(current_price - ob['mid']) / current_price < 0.005:
                ob_score = min(60, ob['strength'] * 0.7)
                breakdown['order_block'] = {
                    'price': ob['mid'],
                    'score': ob_score,
                    'reason': f'قريب من OB ({abs(current_price - ob["mid"])/current_price*100:.2f}%)'
                }
                break
        
        total_score += ob_score
        
        # ═══════════════════════════════════════
        # 3️⃣ FAIR VALUE GAP (70 max)
        # ═══════════════════════════════════════
        fvg_zones = self.fvg_hunter.detect_premium_fvg(df)
        volatility_data = self.volatility_analyzer.get_volatility_score(df)
        fvg_score = 0
        
        for fvg in fvg_zones[:2]:
            if fvg['bottom'] <= current_price <= fvg['top']:
                # إضافة Volatility Score
                adjusted_score = fvg['total_score'] + volatility_data['score']
                fvg_score = min(70, adjusted_score)
                
                breakdown['fvg'] = {
                    'zone': f"{fvg['bottom']:.2f} - {fvg['top']:.2f}",
                    'score': fvg_score,
                    'filled': f"{fvg['filled_percent']:.0f}%",
                    'volatility': volatility_data['level'],
                    'reason': f'FVG ({100-fvg["filled_percent"]:.0f}% fresh) + {volatility_data["reason"]}'
                }
                break
        
        total_score += fvg_score
        
        # إضافة Volatility إلى Breakdown إذا كانت مهمة
        if volatility_data['level'] in ['HIGH', 'MEDIUM']:
            breakdown['volatility'] = {
                'level': volatility_data['level'],
                'ratio': f"{volatility_data['ratio']:.2f}x",
                'reason': volatility_data['reason']
            }
        
        # ═══════════════════════════════════════
        # 4️⃣ LIQUIDITY SWEEP (50 max)
        # ═══════════════════════════════════════
        liq_pools = self.liq_hunter.find_liquidity_pools(df)
        liq_score = 0
        
        for pool in liq_pools:
            sweep = self.liq_hunter.detect_liquidity_sweep(df, pool)
            if sweep['swept']:
                liq_score = 50
                breakdown['liquidity'] = {
                    'level': pool['price'],
                    'score': 50,
                    'type': pool['type'],
                    'reason': '🎯 Stop Hunt! اصطياد السيولة'
                }
                break
        
        total_score += liq_score
        
        # ═══════════════════════════════════════
        # 5️⃣ WHALE ACTIVITY (50 max)
        # ═══════════════════════════════════════
        whale_data = self.whale_watcher.analyze_whale_activity(df)
        whale_score = min(50, whale_data['whale_score'])
        total_score += whale_score
        
        if whale_data['is_active']:
            breakdown['whales'] = {
                'score': whale_score,
                'signals': [s['message'] for s in whale_data['signals']],
                'reason': '🐋 نشاط حيتان مكثف!'
            }
        
        # ═══════════════════════════════════════
        # ✅ ENTRY FILTERS (NEW!)
        # ═══════════════════════════════════════
        
        # 1. Pullback Filter: هل السعر في تصحيح؟
        if KillerConfig.REQUIRE_PULLBACK:
            recent_high = df['high'].tail(20).max()
            pullback_pct = (recent_high - current_price) / recent_high
            
            if not (KillerConfig.PULLBACK_MIN <= pullback_pct <= KillerConfig.PULLBACK_MAX):
                return {
                    'signal': 'WAIT',
                    'score': total_score,
                    'percentage': (total_score / 400) * 100,
                    'reason': f'ننتظر pullback أفضل (حالياً: {pullback_pct:.1%})',
                    'breakdown': breakdown
                }
        
        # 2. Premium/Discount Filter: هل السعر في منطقة خصم؟
        if KillerConfig.PREMIUM_DISCOUNT_FILTER:
            swing_high = df['high'].tail(50).max()
            swing_low = df['low'].tail(50).min()
            range_size = swing_high - swing_low
            
            if range_size > 0:
                position_in_range = (current_price - swing_low) / range_size
                
                # نريد شراء في Discount zone فقط (أقل من 40% من النطاق)
                if position_in_range > KillerConfig.DISCOUNT_ZONE_MAX:
                    return {
                        'signal': 'WAIT',
                        'score': total_score,
                        'percentage': (total_score / 400) * 100,
                        'reason': f'السعر في Premium zone ({position_in_range:.0%}) - ننتظر Discount',
                        'breakdown': breakdown
                    }
        
        # ═══════════════════════════════════════
        # 📊 FINAL DECISION - محسّن!
        # ═══════════════════════════════════════
        
        if total_score >= KillerConfig.MIN_SCORE:
            # حساب Targets & SL حسب قوة الإشارة (محسّن!)
            if total_score >= KillerConfig.EXTREME_THRESHOLD:
                t1, t2, sl = KillerConfig.EXTREME_TARGET1, KillerConfig.EXTREME_TARGET2, KillerConfig.EXTREME_SL
                confidence = 'EXTREME'
            elif total_score >= KillerConfig.HIGH_THRESHOLD:
                t1, t2, sl = KillerConfig.HIGH_TARGET1, KillerConfig.HIGH_TARGET2, KillerConfig.HIGH_SL
                confidence = 'HIGH'
            else:
                t1, t2, sl = KillerConfig.GOOD_TARGET1, KillerConfig.GOOD_TARGET2, KillerConfig.GOOD_SL
                confidence = 'GOOD'
            
            return {
                'signal': 'BUY',
                'symbol': symbol,
                'score': total_score,
                'max_score': 550,  # محدّث!
                'percentage': (total_score / 550) * 100,
                'entry': current_price,
                'target1': current_price * (1 + t1/100),
                'target2': current_price * (1 + t2/100),
                'stop_loss': current_price * (1 - sl/100),
                'breakdown': breakdown,
                'confidence': confidence,
                'structure_type': structure['structure'],
                'entry_time': datetime.now(timezone.utc),  # للـ Exit strategy
                'range_high': range_data['high'],  # للمراقبة
                'ema_exit_active': True  # تفعيل EMA exit
            }
        else:
            return {
                'signal': 'WAIT',
                'score': total_score,
                'percentage': (total_score / 550) * 100,
                'reason': f'نقاط قليلة ({total_score}/550)',
                'breakdown': breakdown
            }

# ============================================================================
# TELEGRAM NOTIFIER
# ============================================================================

class TelegramNotifier:
    """نظام التنبيهات"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self.session = requests.Session()
        self.history = defaultdict(deque)
    
    def send_killer_alert(self, signal: Dict) -> bool:
        """إرسال تنبيه سفّاح الكريبتو"""
        
        if self._is_duplicate(signal['symbol']):
            return False
        
        message = self._format_killer_alert(signal)
        
        try:
            response = self.session.post(
                f"{self.api_url}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True
                },
                timeout=10
            )
            
            if response.status_code == 200:
                self._record_alert(signal['symbol'])
                return True
            
        except Exception as e:
            logging.error(f"Failed to send alert: {e}")
        
        return False
    
    def _format_killer_alert(self, signal: Dict) -> str:
        """تنسيق التنبيه"""
        
        # حساب R:R
        risk = abs(signal['entry'] - signal['stop_loss'])
        reward1 = abs(signal['target1'] - signal['entry'])
        rr = reward1 / risk if risk > 0 else 0
        
        # Emojis
        confidence_emoji = "💀" if signal['confidence'] == 'EXTREME' else ("⚡" if signal['confidence'] == 'HIGH' else "🎯")
        setup_emoji = "🔥" if 'CHoCH' in signal['structure_type'] else "📊"
        
        # Hashtag للعملة (بدون /)
        symbol_tag = signal['symbol'].replace('/', '')
        
        # Breakdown
        breakdown_text = ' • '.join([f"{k.replace('_', ' ').title()}: ✓" 
                                    for k in signal['breakdown'].keys()])
        
        message = f"""
{confidence_emoji} <b>#{symbol_tag}</b> | 🟢 BUY @ {signal['entry']:.4f}

{setup_emoji} <b>Setup:</b> {signal['structure_type'].replace('_', ' ')}
📊 <b>Score:</b> {signal['score']}/400 ({signal['percentage']:.1f}%)
{breakdown_text}

🎯 <b>T1:</b> {signal['target1']:.4f} (+{((signal['target1']/signal['entry']-1)*100):.1f}%)
🎯 <b>T2:</b> {signal['target2']:.4f} (+{((signal['target2']/signal['entry']-1)*100):.1f}%)
🛡️ <b>SL:</b> {signal['stop_loss']:.4f} (-{((1-signal['stop_loss']/signal['entry'])*100):.1f}%) | R:R {rr:.1f}:1

💀 <i>Crypto Killer - {signal['confidence']}</i>
        """.strip()
        
        return message
    
    def _is_duplicate(self, symbol: str) -> bool:
        """تحقق من التكرار"""
        cutoff = datetime.now() - timedelta(hours=KillerConfig.AVOID_DUPLICATE_HOURS)
        recent = [t for t in self.history[symbol] if t > cutoff]
        return len(recent) > 0
    
    def _record_alert(self, symbol: str):
        """تسجيل التنبيه"""
        self.history[symbol].append(datetime.now())
        if len(self.history[symbol]) > 10:
            self.history[symbol].popleft()

# ============================================================================
# MAIN BOT
# ============================================================================

class CryptoKillerBot:
    """💀 البوت الرئيسي"""
    
    def __init__(self, api_key: str, api_secret: str, passphrase: str,
                 telegram_token: str, telegram_chat_id: str):
        
        self.exchange = ccxt.okx({
            'apiKey': api_key,
            'secret': api_secret,
            'password': passphrase,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        
        self.notifier = TelegramNotifier(telegram_token, telegram_chat_id)
        self.strategy = CryptoKillerStrategy()
        self.running = True
        
        logging.info("💀 Crypto Killer Bot initialized!")
    
    def run(self):
        """حلقة التشغيل الرئيسية"""
        
        self.notifier.session.post(
            f"{self.notifier.api_url}/sendMessage",
            json={
                "chat_id": self.notifier.chat_id,
                "text": "💀 <b>Crypto Killer Bot Started!</b>\n\n⚡ Win Rate Target: 70%+\n📊 Min Score: 250/400",
                "parse_mode": "HTML"
            }
        )
        
        logging.info("🚀 Starting main loop...")
        
        while self.running:
            try:
                logging.info("=" * 60)
                logging.info("📊 Scanning market...")
                
                # جلب العملات
                symbols = self._get_top_symbols()
                logging.info(f"✅ Found {len(symbols)} symbols")
                
                # تحليل متوازي
                with ThreadPoolExecutor(max_workers=KillerConfig.MAX_CONCURRENT) as executor:
                    futures = {executor.submit(self._analyze_symbol, sym): sym 
                              for sym in symbols}
                    
                    for future in as_completed(futures):
                        try:
                            future.result()
                        except Exception as e:
                            logging.error(f"Analysis error: {e}")
                
                logging.info(f"⏳ Waiting {KillerConfig.SCAN_INTERVAL}s...")
                time.sleep(KillerConfig.SCAN_INTERVAL)
                
            except KeyboardInterrupt:
                logging.info("⛔ Stopping bot...")
                self.running = False
            except Exception as e:
                logging.error(f"Main loop error: {e}")
                time.sleep(60)
    
    def _get_top_symbols(self) -> List[str]:
        """جلب أفضل العملات للتحليل"""
        try:
            markets = self.exchange.fetch_tickers()
            
            usdt_pairs = []
            for symbol, ticker in markets.items():
                if '/USDT' in symbol and ticker.get('quoteVolume', 0) > KillerConfig.MIN_VOLUME_USDT:
                    usdt_pairs.append({
                        'symbol': symbol,
                        'volume': ticker['quoteVolume']
                    })
            
            # ترتيب حسب الحجم
            usdt_pairs.sort(key=lambda x: x['volume'], reverse=True)
            
            return [p['symbol'] for p in usdt_pairs[:30]]  # أفضل 30
            
        except Exception as e:
            logging.error(f"Failed to fetch symbols: {e}")
            return []
    
    def _analyze_symbol(self, symbol: str):
        """تحليل عملة واحدة"""
        try:
            # جلب البيانات
            ohlcv = self.exchange.fetch_ohlcv(
                symbol, 
                KillerConfig.TIMEFRAME, 
                limit=KillerConfig.CANDLES_LOOKBACK
            )
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # توليد الإشارة
            signal = self.strategy.generate_signal(symbol, df)
            
            if signal['signal'] == 'BUY':
                logging.info(f"💀 {symbol}: BUY signal! Score: {signal['score']}/400 ({signal['percentage']:.1f}%)")
                self.notifier.send_killer_alert(signal)
            elif signal['score'] > 200:
                logging.info(f"📊 {symbol}: {signal['score']}/400 ({signal['percentage']:.1f}%) - قريب")
            
        except Exception as e:
            logging.warning(f"⚠️ {symbol} analysis failed: {e}")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        with open('trading_config.json', 'r') as f:
            config = json.load(f)
        
        bot = CryptoKillerBot(
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
        logging.error(f"Startup error: {e}", exc_info=True)
        sys.exit(1)
