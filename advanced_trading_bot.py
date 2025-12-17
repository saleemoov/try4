#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 Advanced OKX Trading Bot
تطبيق احترافي للتداول اليومي (Spot Only)
مع تحليل متقدم ومؤشرات فنية وتنبيهات Telegram
"""

import os
import sys
import time
import json
import hashlib
import hmac
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Optional
import logging

# المكتبات الأساسية
try:
    import ccxt
    import pandas as pd
    import ta  # Technical Analysis Library
    from dotenv import load_dotenv
except ImportError:
    print("❌ تثبيت المكتبات المفقودة...")
    os.system("pip install ccxt pandas ta python-dotenv requests")
    import ccxt
    import pandas as pd
    import ta
    from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()

# ============================================================================
# إعدادات الأمان والحماية
# ============================================================================

class EncryptionManager:
    """إدارة تشفير البيانات الحساسة"""
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """تشفير مفتاح API للحفظ الآمن"""
        return hashlib.sha256(api_key.encode()).hexdigest()[:16]
    
    @staticmethod
    def load_credentials(config_file: str = "trading_config.json") -> Dict:
        """تحميل بيانات الاعتماد من ملف محمي"""
        if not os.path.exists(config_file):
            return None
        
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except:
            return None
    
    @staticmethod
    def save_credentials(data: Dict, config_file: str = "trading_config.json"):
        """حفظ بيانات الاعتماد بشكل آمن"""
        os.chmod(config_file, 0o600) if os.path.exists(config_file) else None
        with open(config_file, 'w') as f:
            json.dump(data, f, indent=2)
        os.chmod(config_file, 0o600)

# ============================================================================
# نظام الإعدادات
# ============================================================================

class TradingConfig:
    """إدارة الإعدادات المركزية"""
    
    # إعدادات التداول الأساسية
    TARGET_PROFIT_MIN = 2.0  # الحد الأدنى للربح 2%
    TARGET_PROFIT_MAX = 7.0  # الحد الأقصى للربح 7%
    
    # ============================================================
    # 🚀 وضع Scalping - اقتناص الفرص الصغيرة المتكررة
    # ============================================================
    SCALPING_MODE = True  # تفعيل/تعطيل وضع Scalping
    
    # إعدادات Scalping
    SCALPING_TARGET_MIN = 2.0    # هدف أول صغير (2%)
    SCALPING_TARGET_MAX = 3.5    # هدف ثاني صغير (3.5%)
    SCALPING_STOP_LOSS = 1.2     # SL صغير (1.2%)
    SCALPING_MIN_STRENGTH = 50   # قبول إشارات 50%+ (بدلاً من 60%)
    
    # المؤشرات الفنية
    EMA_SHORT = 5        # EMA قصير الأجل
    EMA_MEDIUM = 8       # EMA متوسط الأجل
    EMA_LONG = 13        # EMA طويل الأجل
    RSI_PERIOD = 14      # فترة RSI
    RSI_OVERBOUGHT = 70  # مستوى الإفراط في الشراء
    RSI_OVERSOLD = 30    # مستوى الإفراط في البيع
    MACD_FAST = 12       # EMA سريعة للـ MACD
    MACD_SLOW = 26       # EMA بطيئة للـ MACD
    MACD_SIGNAL = 9      # خط الإشارة
    
    # الأطر الزمنية
    TREND_TIMEFRAME = '4h'    # تحديد الاتجاه
    ENTRY_TIMEFRAME = '15m'   # إشارات الدخول (15 دقيقة أو 5 دقائق)
    
    # الفلاتر
    MIN_VOLUME_USDT = 10000000  # 10 مليون دولار حد أدنى
    MIN_24H_CHANGE = -5.0       # تقليل عدد العملات الضعيفة
    STABLE_COINS = ['USDT', 'USDC', 'DAI', 'BUSD', 'TUSD']  # عملات مستقرة
    
    # إعدادات الرسائل
    AVOID_DUPLICATE_HOURS = 1  # عدم تكرار الإشارات خلال ساعة واحدة
    
    # إعدادات الأداء
    MAX_CONCURRENT_ANALYSIS = 10  # عدد العملات التي تحلل بالتوازي
    CACHE_TIMEOUT = 300           # مدة كاش البيانات (5 دقائق)
    
    # API Rate Limiting
    API_CALLS_PER_MINUTE = 1200  # حد أقصى للطلبات
    HEARTBEAT_INTERVAL = 3600    # ثانية بين رسائل heartbeat (1 ساعة)
    
    # قاموس القطاعات
    CRYPTO_SECTORS = {
        # Layer 1 / Blockchain
        'BTC': 'Layer 1 (Bitcoin)',
        'ETH': 'Layer 1 (Ethereum)',
        'SOL': 'Layer 1 (Solana)',
        'AVAX': 'Layer 1 (Avalanche)',
        'LUNA': 'Layer 1 (Terra)',
        'NEAR': 'Layer 1 (Near)',
        'FTM': 'Layer 1 (Fantom)',
        'HBAR': 'Layer 1 (Hedera)',
        'ATOM': 'Layer 1 (Cosmos)',
        
        # Layer 2
        'ARB': 'Layer 2 (Arbitrum)',
        'OP': 'Layer 2 (Optimism)',
        'MATIC': 'Layer 2 (Polygon)',
        
        # DeFi
        'AAVE': 'DeFi (Lending)',
        'COMP': 'DeFi (Lending)',
        'SUSHI': 'DeFi (DEX)',
        'UNI': 'DeFi (DEX)',
        'CURVE': 'DeFi (DEX)',
        'LIDO': 'DeFi (Staking)',
        '1INCH': 'DeFi (DEX)',
        'DYDX': 'DeFi (DEX)',
        'GMX': 'DeFi (Derivatives)',
        'PERP': 'DeFi (Derivatives)',
        
        # NFT / Metaverse
        'BLUR': 'NFT',
        'LOOKS': 'NFT',
        'SAND': 'Metaverse',
        'MANA': 'Metaverse',
        'ENJ': 'NFT/Gaming',
        'AXS': 'Gaming',
        'GALA': 'Gaming',
        'FLOW': 'NFT',
        
        # Artificial Intelligence / ML
        'AGIX': 'AI (Singularity)',
        'RENDER': 'AI/Computing',
        'FET': 'AI (Fetch)',
        'OCEAN': 'AI/Data',
        'TAO': 'AI (Bittensor)',
        'ARKM': 'AI (Arkham)',
        'ALI': 'AI (Alchemix)',
        
        # Privacy / Security
        'MONERO': 'Privacy',
        'ZCASH': 'Privacy',
        'DASH': 'Privacy',
        'TORNADO': 'Privacy',
        'XMR': 'Privacy',
        'ZEC': 'Privacy',
        
        # Stablecoins
        'USDT': 'Stablecoin',
        'USDC': 'Stablecoin',
        'DAI': 'Stablecoin',
        'BUSD': 'Stablecoin',
        'TUSD': 'Stablecoin',
        'FRAX': 'Stablecoin',
        
        # Memecoin / Social
        'DOGE': 'Memecoin',
        'SHIB': 'Memecoin',
        'PEPE': 'Memecoin',
        'DOGWIFHAT': 'Memecoin',
        'BONK': 'Memecoin',
        'WIF': 'Memecoin',
        'PUMP': 'Memecoin',
        'HYPE': 'Memecoin',
        
        # Exchange Tokens
        'BNB': 'CEX Token',
        'OKB': 'CEX Token',
        'FTT': 'CEX Token',
        'KCS': 'CEX Token',
        'GT': 'CEX Token',
        
        # Infrastructure / Tools
        'LINK': 'Infrastructure (Oracle)',
        'THE': 'Infrastructure',
        'GRT': 'Infrastructure (Indexing)',
        'API3': 'Infrastructure (Oracle)',
        'BAND': 'Infrastructure (Oracle)',
        'AKRO': 'Infrastructure',
        
        # Payment / Commerce
        'XRP': 'Payment',
        'LTC': 'Payment',
        'BCH': 'Payment',
        'DASH': 'Payment',
        'DOGE': 'Payment',
        
        # RWA / Real World Assets
        'ONDO': 'RWA',
        'MKR': 'RWA/Governance',
        
        # Governance
        'AAVE': 'Governance',
        'UNI': 'Governance',
        'MKR': 'Governance',
        'ENS': 'Governance',
    }
    
    @staticmethod
    def get_sector(symbol: str) -> str:
        """احصل على قطاع العملة من الرمز"""
        symbol_clean = symbol.replace('/USDT', '').replace('USDT', '').strip()
        return TradingConfig.CRYPTO_SECTORS.get(symbol_clean, 'Other')

# ============================================================================
# نظام التنبيهات عبر Telegram
# ============================================================================

class TelegramNotifier:
    """إرسال التنبيهات عبر Telegram مع دعم استرجاع سجل التنبيهات بالهاشتاق"""
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self.session = requests.Session()
        self.notification_history = defaultdict(deque)  # ذاكرة الإشارات
        self._last_update_id = None
        self._update_bot_commands()
        listener = threading.Thread(target=self._start_update_listener, daemon=True)
        listener.start()

    def _update_bot_commands(self):
        commands = [
            {"command": "start", "description": "بدء البوت"},
            {"command": "status", "description": "حالة التداول الحالية"},
            {"command": "pause", "description": "إيقاف مؤقت"},
            {"command": "resume", "description": "استئناف"},
            {"command": "settings", "description": "الإعدادات"},
            {"command": "alerts", "description": "عرض التنبيهات"},
            {"command": "hammer", "description": "تنشيط الهامر"},
        ]
        try:
            self.session.post(f"{self.api_url}/setMyCommands", json={"commands": commands})
        except Exception:
            pass

    def send_alert(self, symbol: str, alert_data: Dict) -> bool:
        if self._is_duplicate_alert(symbol, alert_data):
            return False
        message = self._format_alert_message(symbol, alert_data)
        attempts = 3
        for attempt in range(1, attempts + 1):
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
                    self._record_alert(symbol, alert_data)
                    return True
                else:
                    logging.warning(f"⚠️ إرسال تنبيه [{symbol}] حاول {attempt}/{attempts} - status={response.status_code} body={response.text[:200]}")
            except Exception as e:
                logging.error(f"❌ خطأ في إرسال التنبيه [{symbol}] حاول {attempt}/{attempts}: {e}")
            time.sleep(1 + attempt)
        return False

    def _is_duplicate_alert(self, symbol: str, alert_data: Dict) -> bool:
        history = self.notification_history[symbol]
        for timestamp, prev_signal in history:
            if (datetime.now() - timestamp).seconds < 3600:
                if prev_signal.get('signal_type') == alert_data.get('signal_type'):
                    return True
        return False

    def _record_alert(self, symbol: str, alert_data: Dict):
        self.notification_history[symbol].append((datetime.now(), alert_data))

    def _format_alert_message(self, symbol: str, data: Dict) -> str:
        """
        تنبيه مضغوط ذكي - كل المعلومات المهمة في 6-8 أسطر فقط
        """
        signal_emoji = "🟢" if data.get('signal_type') == 'BUY' else "🔴"
        signal_type = "شراء" if data.get('signal_type') == 'BUY' else "بيع"
        strength = data.get('signal_strength', 0)
        signal_category = data.get('signal_category', 'عادي')
        
        # مؤشر الوضع (Scalping أو Normal)
        mode_badge = "⚡ Scalp" if TradingConfig.SCALPING_MODE else "📊 Normal"
        
        # رموز القوة المضغوطة
        if strength >= 80:
            power = "🔥🔥🔥"
        elif strength >= 70:
            power = "🔥🔥"
        elif strength >= 60:
            power = "🔥"
        else:
            power = "⚡"
        
        # اختصارات المؤشرات
        rsi = data.get('rsi', 0)
        rsi_icon = "🟢" if rsi < 35 else "🔴" if rsi > 70 else "🟡"
        
        # السعر والأهداف مختصرة
        price = data.get('current_price', 0)
        change = data.get('change_24h', 0)
        t1 = data.get('target1', 0)
        t2 = data.get('target2', 0)
        sl = data.get('stop_loss', 0)
        
        # حساب النسب بدلاً من الأسعار الطويلة
        t1_pct = ((t1 - price) / price * 100) if price > 0 else 0
        t2_pct = ((t2 - price) / price * 100) if price > 0 else 0
        sl_pct = abs((sl - price) / price * 100) if price > 0 else 0
        
        # التنبيه المضغوط الذكي مع مؤشر الوضع
        message = f"""
╔═══ {signal_emoji} <b>{signal_type}</b> {mode_badge} ═══╗
<b>{symbol}</b> {power} {strength:.0f}% · {signal_category}
💲 <code>${price:.6f}</code> ({change:+.1f}%)

🎯 T1: <code>+{t1_pct:.1f}%</code> | T2: <code>+{t2_pct:.1f}%</code> | SL: <code>-{sl_pct:.1f}%</code>
📊 RSI {rsi_icon}<code>{rsi:.0f}</code> · {data.get('macd_signal', 'N/A')[:8]} · {data.get('ema_status', 'N/A')[:8]}

<code>#{symbol}</code> · {datetime.now().strftime('%H:%M')}
        """
        return message.strip()

    def _start_update_listener(self):
        url = f"{self.api_url}/getUpdates"
        while True:
            try:
                params = {'timeout': 20, 'offset': self._last_update_id + 1 if self._last_update_id else None}
                r = self.session.get(url, params={k: v for k, v in params.items() if v is not None}, timeout=30)
                data = r.json()
                if not data.get('ok'):
                    time.sleep(5)
                    continue
                for update in data.get('result', []):
                    self._last_update_id = update['update_id']
                    msg = update.get('message') or update.get('edited_message')
                    if not msg:
                        continue
                    text = msg.get('text', '').strip()
                    chat = msg.get('chat', {}).get('id')
                    if str(chat) != str(self.chat_id):
                        continue
                    if text.startswith('#') and len(text) > 1:
                        symbol = text.lstrip('#').strip().upper()
                        self._reply_with_symbol_history(chat, symbol)
            except Exception:
                time.sleep(5)

    def _reply_with_symbol_history(self, chat_id, symbol: str):
        history = list(self.notification_history.get(symbol, []))
        if not history:
            text = f"لا توجد تنبيهات سابقة لـ {symbol}."
            try:
                self.session.post(f"{self.api_url}/sendMessage", json={'chat_id': chat_id, 'text': text}, timeout=10)
            except Exception:
                pass
            return
        lines = [f"تنبيهات لـ {symbol}: (آخر {min(len(history),10)})"]
        for ts, data in history[-10:]:
            tstr = ts.strftime('%Y-%m-%d %H:%M')
            price = data.get('current_price')
            sig = data.get('signal_type', '')
            strength = data.get('signal_strength', 0)
            lines.append(f"• {tstr} — {sig} — {price:.8f} — قوة {strength:.0f}%")
        text = "\n".join(lines)
        try:
            self.session.post(f"{self.api_url}/sendMessage", json={'chat_id': chat_id, 'text': text}, timeout=10)
        except Exception:
            pass

# ============================================================================
# نظام تحليل ICT (Institutional Client Theory) المتقدم
# ============================================================================

class ICTAnalyzer:
    """تحليل احترافي بناءً على نظرية العميل المؤسسي (ICT)"""
    
    def __init__(self):
        self.order_blocks_cache = {}
        self.fvg_cache = {}
        self.liquidity_zones_cache = {}
    
    def analyze_ict(self, df: pd.DataFrame, symbol: str) -> Dict:
        """تحليل ICT شامل"""
        if len(df) < 50:
            return None
        
        ict_analysis = {
            'order_blocks': self._detect_order_blocks(df),
            'fair_value_gaps': self._detect_fvg(df),
            'liquidity_zones': self._detect_liquidity_zones(df),
            'supply_demand': self._detect_supply_demand(df),
            'ict_signal': None,
            'ict_strength': 0
        }
        
        # توليد إشارة ICT
        ict_analysis['ict_signal'], ict_analysis['ict_strength'] = self._generate_ict_signal(ict_analysis)
        
        return ict_analysis
    
    def _detect_order_blocks(self, df: pd.DataFrame, lookback: int = 50) -> Dict:
        """
        كشف Order Blocks (مناطق الكسر)
        آخر شمعة قبل الكسر = منطقة إعادة الترتد
        """
        recent = df.tail(lookback)
        close = recent['close'].values
        high = recent['high'].values
        low = recent['low'].values
        
        order_blocks = {
            'buy_blocks': [],      # مناطق شراء (كسر لأعلى)
            'sell_blocks': [],     # مناطق بيع (كسر لأسفل)
            'nearest_buy': None,
            'nearest_sell': None
        }
        
        # البحث عن كسور صاعدة وهابطة
        for i in range(2, len(close) - 1):
            # كسر صاعد: اثنين من الشموع الهابطة تليها شمعة صاعدة قوية
            if (close[i-2] > close[i-1] and close[i] > close[i-1] and 
                close[i] > close[i-2] and (high[i] - low[i]) > (high[i-1] - low[i-1])):
                
                block_high = max(high[i-2], high[i-1])
                block_low = min(low[i-2], low[i-1])
                order_blocks['buy_blocks'].append({
                    'high': float(block_high),
                    'low': float(block_low),
                    'strength': float((high[i] - low[i]) / (high[i-1] - low[i-1])) if (high[i-1] - low[i-1]) > 0 else 1.0,
                    'bars_ago': len(close) - 1 - i
                })
            
            # كسر هابط: اثنين من الشموع الصاعدة تليها شمعة هابطة قوية
            if (close[i-2] < close[i-1] and close[i] < close[i-1] and 
                close[i] < close[i-2] and (high[i] - low[i]) > (high[i-1] - low[i-1])):
                
                block_high = max(high[i-2], high[i-1])
                block_low = min(low[i-2], low[i-1])
                order_blocks['sell_blocks'].append({
                    'high': float(block_high),
                    'low': float(block_low),
                    'strength': float((high[i] - low[i]) / (high[i-1] - low[i-1])) if (high[i-1] - low[i-1]) > 0 else 1.0,
                    'bars_ago': len(close) - 1 - i
                })
        
        # أقرب order block
        current_price = df['close'].iloc[-1]
        
        if order_blocks['buy_blocks']:
            nearest_buy = min(order_blocks['buy_blocks'], key=lambda x: abs(x['bars_ago']))
            if nearest_buy['low'] < current_price < nearest_buy['high']:
                order_blocks['nearest_buy'] = nearest_buy
        
        if order_blocks['sell_blocks']:
            nearest_sell = min(order_blocks['sell_blocks'], key=lambda x: abs(x['bars_ago']))
            if nearest_sell['low'] < current_price < nearest_sell['high']:
                order_blocks['nearest_sell'] = nearest_sell
        
        return order_blocks
    
    def _detect_fvg(self, df: pd.DataFrame, lookback: int = 50) -> Dict:
        """
        كشف Fair Value Gaps (الفراغات السعرية)
        فراغات غير مملوءة = السعر عادة يعود لملئها
        """
        recent = df.tail(lookback).copy()
        high = recent['high'].values
        low = recent['low'].values
        
        fvgs = {
            'bullish_fvgs': [],    # فراغات صاعدة
            'bearish_fvgs': [],    # فراغات هابطة
            'active_fvg': None
        }
        
        # البحث عن فراغات
        for i in range(2, len(high)):
            # Fair Value Gap صاعد: الشمعة الحالية فوق high السابقة بفراغ
            if low[i] > high[i-1] and high[i] > high[i-1]:
                gap_start = high[i-1]
                gap_end = low[i]
                gap_size = gap_end - gap_start
                
                if gap_size > 0:
                    fvgs['bullish_fvgs'].append({
                        'top': float(gap_end),
                        'bottom': float(gap_start),
                        'size': float(gap_size),
                        'bars_ago': len(high) - 1 - i
                    })
            
            # Fair Value Gap هابط: الشمعة الحالية تحت low السابقة بفراغ
            if high[i] < low[i-1] and low[i] < low[i-1]:
                gap_start = low[i-1]
                gap_end = high[i]
                gap_size = gap_start - gap_end
                
                if gap_size > 0:
                    fvgs['bearish_fvgs'].append({
                        'top': float(gap_start),
                        'bottom': float(gap_end),
                        'size': float(gap_size),
                        'bars_ago': len(high) - 1 - i
                    })
        
        # أقرب FVG نشط
        current_price = df['close'].iloc[-1]
        
        for fvg in fvgs['bullish_fvgs']:
            if fvg['bottom'] < current_price < fvg['top']:
                fvgs['active_fvg'] = {'type': 'bullish', **fvg}
                break
        
        if not fvgs['active_fvg']:
            for fvg in fvgs['bearish_fvgs']:
                if fvg['bottom'] < current_price < fvg['top']:
                    fvgs['active_fvg'] = {'type': 'bearish', **fvg}
                    break
        
        return fvgs
    
    def _detect_liquidity_zones(self, df: pd.DataFrame, lookback: int = 100) -> Dict:
        """
        كشف Liquidity Zones (مناطق السيولة)
        تجمعات الأسعار القديمة = السعر يذهب إليها
        """
        recent = df.tail(lookback)
        close = recent['close'].values
        high = recent['high'].values
        low = recent['low'].values
        volume = recent['volume'].values if 'volume' in recent.columns else None
        
        # تحديد مناطق التجمع (Clustering)
        liquidity_zones = {
            'supply_zones': [],     # تجمعات البيع (أعلى)
            'demand_zones': [],     # تجمعات الشراء (أسفل)
            'active_zone': None
        }
        
        # تقسيم السعر إلى نطاقات
        price_min = low.min()
        price_max = high.max()
        price_range = price_max - price_min
        zone_size = price_range / 10  # 10 مناطق
        
        zone_counts = {}
        
        for i in range(len(close)):
            zone_level = int((close[i] - price_min) / zone_size)
            if zone_level not in zone_counts:
                zone_counts[zone_level] = {'count': 0, 'high': 0, 'low': close[i], 'volume': 0}
            
            zone_counts[zone_level]['count'] += 1
            zone_counts[zone_level]['high'] = max(zone_counts[zone_level]['high'], high[i])
            zone_counts[zone_level]['low'] = min(zone_counts[zone_level]['low'], low[i])
            if volume is not None:
                zone_counts[zone_level]['volume'] += volume[i]
        
        # تحديد مناطق قوية (تجمعات)
        current_price = df['close'].iloc[-1]
        current_zone = int((current_price - price_min) / zone_size)
        
        for zone_level, data in sorted(zone_counts.items(), key=lambda x: x[1]['count'], reverse=True):
            if data['count'] >= 5:  # على الأقل 5 شموع في المنطقة
                zone_price = price_min + (zone_level * zone_size)
                
                if zone_price > current_price:
                    liquidity_zones['supply_zones'].append({
                        'level': float(zone_price),
                        'strength': data['count'],
                        'volume': float(data['volume']) if volume is not None else 0,
                        'high': float(data['high']),
                        'low': float(data['low'])
                    })
                else:
                    liquidity_zones['demand_zones'].append({
                        'level': float(zone_price),
                        'strength': data['count'],
                        'volume': float(data['volume']) if volume is not None else 0,
                        'high': float(data['high']),
                        'low': float(data['low'])
                    })
        
        # أقرب zone نشط
        if liquidity_zones['demand_zones']:
            nearest_demand = max(liquidity_zones['demand_zones'], key=lambda x: x['level'])
            liquidity_zones['active_zone'] = {'type': 'demand', **nearest_demand}
        
        return liquidity_zones
    
    def _detect_supply_demand(self, df: pd.DataFrame) -> Dict:
        """
        كشف مناطق Supply & Demand
        منطقة حمراء (ضغط بيع) = Supply
        منطقة خضراء (ضغط شراء) = Demand
        """
        if len(df) < 20:
            return {'supply_level': None, 'demand_level': None, 'imbalance': None}
        
        recent = df.tail(20)
        close = recent['close'].values
        volume = recent['volume'].values if 'volume' in recent.columns else np.ones(len(close))
        
        # حساب ضغط البيع والشراء
        price_changes = np.diff(close)
        volume_weighted_up = np.sum([volume[i] if price_changes[i] > 0 else 0 for i in range(len(price_changes))])
        volume_weighted_down = np.sum([volume[i] if price_changes[i] < 0 else 0 for i in range(len(price_changes))])
        
        # تحديد مستويات Supply و Demand
        recent_high = recent['high'].max()
        recent_low = recent['low'].min()
        
        supply_level = recent_high if volume_weighted_down > volume_weighted_up else None
        demand_level = recent_low if volume_weighted_up > volume_weighted_down else None
        
        imbalance = abs(volume_weighted_up - volume_weighted_down) / (volume_weighted_up + volume_weighted_down) if (volume_weighted_up + volume_weighted_down) > 0 else 0
        
        return {
            'supply_level': float(supply_level) if supply_level else None,
            'demand_level': float(demand_level) if demand_level else None,
            'volume_buy': float(volume_weighted_up),
            'volume_sell': float(volume_weighted_down),
            'imbalance': float(imbalance)
        }
    
    def _generate_ict_signal(self, ict_analysis: Dict) -> Tuple[str, float]:
        """توليد إشارة ICT قوية"""
        signal_score = 0
        max_score = 0
        details = []
        
        # 1. Order Blocks (30 نقطة)
        if ict_analysis['order_blocks']['nearest_buy']:
            signal_score += 30
            details.append("✅ السعر في منطقة Order Block شراء قوية")
            max_score += 30
        elif ict_analysis['order_blocks']['nearest_sell']:
            signal_score -= 30
            details.append("❌ السعر في منطقة Order Block بيع قوية")
        else:
            max_score += 30
        
        # 2. Fair Value Gaps (25 نقطة)
        if ict_analysis['fair_value_gaps']['active_fvg']:
            fvg = ict_analysis['fair_value_gaps']['active_fvg']
            if fvg['type'] == 'bullish':
                signal_score += 25
                details.append(f"✅ منطقة FVG صاعدة (سيعود السعر لملؤها)")
            else:
                signal_score -= 25
                details.append(f"❌ منطقة FVG هابطة")
            max_score += 25
        else:
            max_score += 25
        
        # 3. Liquidity Zones (25 نقطة)
        if ict_analysis['liquidity_zones']['active_zone']:
            zone = ict_analysis['liquidity_zones']['active_zone']
            if zone['type'] == 'demand':
                signal_score += 25
                details.append(f"✅ السعر في منطقة Demand قوية (تجمع الشراء)")
            else:
                signal_score -= 25
                details.append(f"❌ السعر بعيد عن مناطق الشراء")
            max_score += 25
        else:
            max_score += 25
        
        # 4. Supply/Demand Imbalance (20 نقطة)
        supply_demand = ict_analysis['supply_demand']
        if supply_demand['imbalance'] > 0.3:
            if supply_demand['volume_buy'] > supply_demand['volume_sell']:
                signal_score += 20
                details.append("✅ عدم توازن قوي لصالح الشراء")
            else:
                signal_score -= 20
                details.append("❌ عدم توازن قوي لصالح البيع")
            max_score += 20
        else:
            max_score += 20
        
        # حساب النسبة المئوية
        if max_score > 0:
            signal_strength = ((signal_score + max_score) / (2 * max_score)) * 100
        else:
            signal_strength = 50
        
        # تحديد الإشارة
        if signal_strength > 60:
            signal = "BUY"
        elif signal_strength < 40:
            signal = "SELL"
        else:
            signal = "NEUTRAL"
        
        return signal, signal_strength

# ============================================================================
# محرك التحليل الفني المتقدم
# ============================================================================

class TechnicalAnalyzer:
    """تحليل المؤشرات الفنية المتقدمة"""
    
    def __init__(self):
        self.support_resistance_cache = {}
        self.ict_analyzer = ICTAnalyzer()
    
    def analyze_candles(self, df: pd.DataFrame, symbol: str = "") -> Dict:
        """تحليل شامل للشموع والمؤشرات + ICT + كشف القيعان"""
        
        if len(df) < 50:
            return None
        
        # التحليل الفني التقليدي
        analysis = {
            'ema': self._calculate_ema(df),
            'rsi': self._calculate_rsi(df),
            'stochastic_rsi': self._calculate_stochastic_rsi(df),
            'macd': self._calculate_macd(df),
            'bollinger_bands': self._calculate_bollinger_bands(df),
            'adx': self._calculate_adx(df),
            'support_resistance': self._find_support_resistance(df),
            'trend_strength': self._calculate_trend_strength(df),
            'fibonacci': self._calculate_fibonacci_levels(df),
            'consolidation': self._detect_consolidation(df),
            'bounce': self._detect_bounce_opportunities(df)  # ← كشف القيعان والارتدادات
        }
        analysis['current_price'] = float(df['close'].iloc[-1])
        
        # تحديد نوع الإشارة
        signal_type = self._determine_signal_type(analysis, analysis.get('bounce', {}))
        analysis['signal_type'] = signal_type
        
        # تحليل ICT المتقدم
        ict_analysis = self.ict_analyzer.analyze_ict(df, symbol)
        analysis['ict'] = ict_analysis
        
        return analysis
    
    def _calculate_ema(self, df: pd.DataFrame) -> Dict:
        """حساب EMA بثلاث فترات"""
        ema5 = ta.trend.ema_indicator(df['close'], window=5)
        ema8 = ta.trend.ema_indicator(df['close'], window=8)
        ema13 = ta.trend.ema_indicator(df['close'], window=13)
        
        current_price = df['close'].iloc[-1]
        
        # تحديد حالة EMA
        if ema5.iloc[-1] > ema8.iloc[-1] > ema13.iloc[-1]:
            status = "قوي صاعد 📈"
            signal = "BUY"
        elif ema5.iloc[-1] < ema8.iloc[-1] < ema13.iloc[-1]:
            status = "قوي هابط 📉"
            signal = "SELL"
        else:
            status = "متشابك"
            signal = "NEUTRAL"
        
        return {
            'ema5': ema5.iloc[-1],
            'ema8': ema8.iloc[-1],
            'ema13': ema13.iloc[-1],
            'status': status,
            'signal': signal,
            'distance_from_ema5': ((current_price - ema5.iloc[-1]) / ema5.iloc[-1]) * 100
        }
    
    def _calculate_rsi(self, df: pd.DataFrame) -> Dict:
        """حساب مؤشر القوة النسبية"""
        rsi = ta.momentum.rsi(df['close'], window=14)
        current_rsi = rsi.iloc[-1]
        if current_rsi >= 70:
            condition = "إفراط في الشراء ⚠️"
            signal = "OVERBOUGHT"
        elif current_rsi <= 30:
            condition = "إفراط في البيع 💚"
            signal = "OVERSOLD"
        else:
            condition = "محايد"
            signal = "NEUTRAL"
        return {
            'value': current_rsi,
            'condition': condition,
            'signal': signal
        }
    
    def _calculate_bollinger_bands(self, df: pd.DataFrame) -> Dict:
        """حساب قنوات بولينجر - مؤشر قوة الاتجاه والتطرف"""
        try:
            bb = ta.volatility.bollinger_wband(df['close'], window=20, window_dev=2)
            current_price = df['close'].iloc[-1]
            
            # الحسابات الأساسية
            bb_sma = ta.trend.sma_indicator(df['close'], window=20)
            bb_std = df['close'].rolling(window=20).std()
            
            upper_band = bb_sma + (bb_std * 2)
            lower_band = bb_sma - (bb_std * 2)
            middle_band = bb_sma
            
            upper_val = upper_band.iloc[-1]
            lower_val = lower_band.iloc[-1]
            middle_val = middle_band.iloc[-1]
            
            # تحديد الموقع والإشارة
            if current_price >= upper_val:
                position = "فوق القناة العليا"
                signal = "OVERBOUGHT"  # قد يحدث تصحيح
            elif current_price <= lower_val:
                position = "أسفل القناة السفلى"
                signal = "OVERSOLD"  # قد يحدث ارتداد
            elif current_price > middle_val:
                position = "في النصف العلوي (قوي)"
                signal = "BULLISH"
            else:
                position = "في النصف السفلي (ضعيف)"
                signal = "BEARISH"
            
            # قوة الاتجاه (عرض القناة)
            band_width = ((upper_val - lower_val) / middle_val) * 100
            
            return {
                'upper_band': upper_val,
                'middle_band': middle_val,
                'lower_band': lower_val,
                'position': position,
                'signal': signal,
                'band_width': band_width,
                'squeeze': band_width < 10  # ضغط = انفجار وشيك
            }
        except Exception as e:
            logging.warning(f"⚠️ Bollinger Bands calculation failed: {e}")
            return {
                'upper_band': 0, 'middle_band': 0, 'lower_band': 0,
                'position': 'N/A', 'signal': 'N/A', 'band_width': 0, 'squeeze': False
            }
    
    def _calculate_adx(self, df: pd.DataFrame) -> Dict:
        """
        حساب ADX (Average Directional Index)
        يحدد قوة الاتجاه (0-100):
        - 0-25: اتجاه ضعيف
        - 25-50: اتجاه متوسط
        - 50-75: اتجاه قوي
        - 75+: اتجاه قوي جداً
        """
        try:
            adx = ta.trend.adx(df['high'], df['low'], df['close'], window=14)
            current_adx = adx.iloc[-1]
            
            if current_adx < 25:
                trend_strength = "ضعيف جداً (نطاق)"
                score = 20
            elif current_adx < 50:
                trend_strength = "متوسط"
                score = 60
            elif current_adx < 75:
                trend_strength = "قوي"
                score = 85
            else:
                trend_strength = "قوي جداً"
                score = 100
            
            return {
                'adx_value': current_adx,
                'trend_strength': trend_strength,
                'score': score,
                'is_trending': current_adx > 25
            }
        except Exception as e:
            logging.warning(f"⚠️ ADX calculation failed: {e}")
            return {
                'adx_value': 0, 'trend_strength': 'N/A', 'score': 0, 'is_trending': False
            }
    
    def _calculate_stochastic_rsi(self, df: pd.DataFrame) -> Dict:
        """
        حساب Stochastic RSI
        نسخة محسّنة من RSI تقيس موقع RSI ضمن نطاق الفترات الأخيرة
        أكثر حساسية من RSI العادي لالتقاط الانعكاسات المبكرة
        """
        try:
            # حساب RSI الأساسي
            rsi = ta.momentum.rsi(df['close'], window=14)
            
            # حساب الـ Stochastic RSI (النسبة ضمن نطاق آخر 14 قيمة)
            lowest_rsi = rsi.rolling(window=14).min()
            highest_rsi = rsi.rolling(window=14).max()
            
            stoch_rsi = (rsi - lowest_rsi) / (highest_rsi - lowest_rsi) * 100
            
            current_stoch_rsi = stoch_rsi.iloc[-1]
            
            # تحديد الإشارة
            if current_stoch_rsi > 80:
                condition = "إفراط شراء قوي جداً"
                signal = "OVERBOUGHT"
                strength = 100
            elif current_stoch_rsi > 70:
                condition = "إفراط شراء"
                signal = "OVERBOUGHT"
                strength = 80
            elif current_stoch_rsi < 20:
                condition = "إفراط بيع قوي جداً"
                signal = "OVERSOLD"
                strength = 100
            elif current_stoch_rsi < 30:
                condition = "إفراط بيع"
                signal = "OVERSOLD"
                strength = 80
            else:
                condition = "محايد"
                signal = "NEUTRAL"
                strength = 50
            
            return {
                'value': current_stoch_rsi,
                'condition': condition,
                'signal': signal,
                'strength': strength
            }
        except Exception as e:
            logging.warning(f"⚠️ Stochastic RSI calculation failed: {e}")
            return {
                'value': 50, 'condition': 'N/A', 'signal': 'NEUTRAL', 'strength': 50
            }

    def _calculate_macd(self, df: pd.DataFrame) -> Dict:
        """حساب مؤشر MACD"""
        macd = ta.trend.macd(df['close'])
        
        if len(macd) == 0:
            return {
                'macd': 0,
                'signal': 0,
                'histogram': 0,
                'condition': 'N/A',
                'trend': 'NEUTRAL'
            }
        
        # MACD يرجع عمود واحد أو عدة أعمدة حسب الإصدار
        if isinstance(macd, pd.DataFrame):
            macd_line = macd.iloc[:, 0] if len(macd.columns) > 0 else macd.iloc[:, -1]
        else:
            macd_line = macd
        
        macd_val = macd_line.iloc[-1]
        
        # حساب خط الإشارة (EMA بـ 9 فترات من MACD)
        signal_val = ta.trend.ema_indicator(pd.Series(macd_line), window=9).iloc[-1]
        
        # الهيستوجرام
        histogram = macd_val - signal_val
        
        # تحديد الحالة
        if histogram > 0 and histogram > 0:
            condition = "تقاطع ذهبي صاعد 📈"
            trend = "BUY"
        elif histogram < 0 and histogram < 0:
            condition = "تقاطع مميت هابط 📉"
            trend = "SELL"
        else:
            condition = "محايد"
            trend = "NEUTRAL"
        
        return {
            'macd': float(macd_val),
            'signal': float(signal_val),
            'histogram': float(histogram),
            'condition': condition,
            'trend': trend
        }

    def _detect_consolidation(self, df: pd.DataFrame, lookback: int = 20, range_pct_thresh: float = 0.012) -> Dict:
        """
        كشف منطقة التوحيد المتقدم
        - نطاق صغير (Range < 1.2% من السعر)
        - حجم منخفض (Volume Low)
        - ATR منخفض
        - استقرار السعر (Low Volatility)
        """
        if len(df) < lookback:
            return {'is_consolidating': False, 'strength': 0}

        recent = df.tail(lookback)
        high = recent['high'].values
        low = recent['low'].values
        close = recent['close'].values
        volume = recent['volume'].values if 'volume' in recent.columns else np.ones(len(close))
        
        # 1. حساب نطاق السعر
        range_high = high.max()
        range_low = low.min()
        range_value = range_high - range_low
        avg_price = close.mean()
        range_pct = (range_value / avg_price) if avg_price > 0 else 0
        
        # 2. حساب ATR (التقلب)
        try:
            atr = ta.volatility.average_true_range(
                pd.Series(high), 
                pd.Series(low), 
                pd.Series(close)
            )
            atr_recent = atr.iloc[-lookback:].mean()
            atr_ratio = range_value / atr_recent if atr_recent > 0 else 0
        except Exception:
            atr_recent = 0
            atr_ratio = 999
        
        # 3. حساب متوسط الحجم (يجب أن يكون منخفضاً)
        avg_volume = volume.mean()
        recent_volume = volume[-5:].mean()  # متوسط آخر 5 شموع
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 0
        
        # 4. حساب الاستقرار (انحراف معياري منخفض)
        close_std = np.std(close)
        close_variation = (close_std / avg_price * 100) if avg_price > 0 else 0
        
        # 5. حساب نسبة التوحيد
        consolidation_score = 0
        
        # النطاق الصغير (40%)
        if range_pct < range_pct_thresh:
            consolidation_score += 40
        elif range_pct < range_pct_thresh * 1.5:
            consolidation_score += 20
        
        # ATR منخفض (30%)
        if atr_ratio < 1.5:
            consolidation_score += 30
        elif atr_ratio < 2.0:
            consolidation_score += 15
        
        # الحجم المنخفض (20%)
        if volume_ratio < 0.8:
            consolidation_score += 20
        elif volume_ratio < 1.0:
            consolidation_score += 10
        
        # استقرار السعر (10%)
        if close_variation < 1.0:
            consolidation_score += 10
        
        is_consolidating = consolidation_score >= 50
        
        return {
            'is_consolidating': is_consolidating,
            'strength': float(consolidation_score),
            'low': float(range_low),
            'high': float(range_high),
            'range_pct': float(range_pct),
            'range_value': float(range_value),
            'atr_ratio': float(atr_ratio),
            'volume_ratio': float(volume_ratio),
            'close_variation': float(close_variation),
            'details': {
                'range_score': int(min(40, int((1 - min(range_pct / range_pct_thresh, 1.0)) * 40))),
                'atr_score': int(min(30, int((1 - min(atr_ratio / 1.5, 1.0)) * 30))),
                'volume_score': int(min(20, int((1 - min(volume_ratio, 1.0)) * 20))),
                'stability_score': int(min(10, int((1 - min(close_variation / 1.0, 1.0)) * 10)))
            }
        }
    
    def _detect_bounce_opportunities(self, df: pd.DataFrame) -> Dict:
        try:
            if len(df) < 20:
                return {'found_bounce': False, 'strength': 0}
            
            recent = df.tail(20)
            close = recent['close'].values
            low = recent['low'].values
            volume = recent['volume'].values if 'volume' in recent.columns else np.ones(len(close))
            rsi = ta.momentum.rsi(df['close'], window=14)
            
            current_price = close[-1]
            current_rsi = rsi.iloc[-1]
            current_volume = volume[-1] if len(volume) else 1
            avg_volume_20 = volume.mean() if len(volume) else 1
            volume_ratio = (current_volume / avg_volume_20) if avg_volume_20 > 0 else 1
            
            # 1. كشف القاع (Lower Low ثم Higher Low)
            lowest_5_bars_ago = min(low[-5:-1])
            current_low = low[-1]
            is_lower_low = lowest_5_bars_ago > current_low
            is_higher_than_low = current_price > current_low
            
            # 2. RSI إفراط البيع (< 30)
            is_oversold = current_rsi < 30
            recovery = False
            if is_oversold and len(rsi) > 2:
                recovery = rsi.iloc[-1] > rsi.iloc[-2]  # RSI يبدأ بالصعود
            
            # 3. حجم الانخفاض
            lowest_20 = min(close)
            highest_20 = max(close)
            drop_ratio = (highest_20 - current_price) / highest_20 * 100 if highest_20 > 0 else 0
            
            # 4. نقطة الارتداد
            bounce_strength = 0
            bounce_reasons = []
            
            if is_lower_low and is_higher_than_low:
                bounce_strength += 30
                bounce_reasons.append("تشكيل قاع (قاع أقل ثم قاع أعلى)")
            
            if is_oversold:
                bounce_strength += 25
                bounce_reasons.append(f"RSI إفراط بيع ({current_rsi:.0f})")
                if recovery:
                    bounce_strength += 15
                    bounce_reasons.append("RSI يبدأ بالصعود")
            
            if drop_ratio > 5:
                bounce_strength += 20
                bounce_reasons.append(f"انخفاض كبير ({drop_ratio:.1f}%)")
            
            found_bounce = bounce_strength >= 50
            
            return {
                'found_bounce': found_bounce,
                'strength': float(bounce_strength),
                'is_lower_low': bool(is_lower_low),
                'is_oversold': bool(is_oversold),
                'recovery_signal': bool(recovery),
                'drop_ratio': float(drop_ratio),
                'volume_ratio': float(volume_ratio),
                'reasons': bounce_reasons
            }
        except Exception as e:
            logging.warning(f"⚠️ Bounce detection failed: {e}")
            return {'found_bounce': False, 'strength': 0, 'volume_ratio': 1.0}
    
    def _determine_signal_type(self, analysis: Dict, bounce_info: Dict) -> str:
        """تحديد نوع الإشارة (استراتيجية التداول)"""
        try:
            bounce_strength = bounce_info.get('strength', 0)
            consolidation = analysis.get('consolidation', {})
            is_consolidating = consolidation.get('is_consolidating', False)
            adx = analysis.get('adx', {})
            is_trending = adx.get('is_trending', False)
            
            # 1. اصطياد القاع والارتداد (الأولوية الأولى)
            if bounce_strength >= 60:
                return "🎣 اصطياد قاع وارتداد"
            
            # 2. استمرارية الترند القوي
            if is_trending and adx.get('adx_value', 0) > 50:
                return "📈 ركوب ترند قوي"
            
            # 3. الخروج من التوحيد
            if is_consolidating and bounce_strength >= 40:
                return "💥 انفجار من توحيد"
            
            # 4. استمرارية ترند عادية
            if is_trending:
                return "📊 استمرارية ترند"
            
            # 5. تصحيح في ترند صاعد
            if bounce_strength > 30:
                return "♻️ تصحيح وارتداد"
            
            return "⚪ إشارة محايدة"
        except Exception as e:
            logging.warning(f"⚠️ Signal type determination failed: {e}")
            return "⚪ إشارة محايدة"
    
    def _find_support_resistance(self, df: pd.DataFrame) -> Dict:
        """حساب مستويات الدعم والمقاومة"""
        # استخدام آخر 100 شمعة
        recent = df.tail(100)
        
        # الحد الأعلى والأدنى
        high = recent['high'].max()
        low = recent['low'].min()
        
        # مستويات الدعم والمقاومة الأساسية
        resistance1 = high
        support1 = low
        
        # مستويات وسيطة
        pivot = (high + low) / 2
        resistance2 = high + (high - low) * 0.618  # نسبة ذهبية
        support2 = low - (high - low) * 0.618
        
        current_price = df['close'].iloc[-1]
        
        return {
            'resistance': resistance1,
            'support': support1,
            'pivot': pivot,
            'resistance2': resistance2,
            'support2': support2,
            'nearest_resistance': resistance1 if current_price < resistance1 else resistance2,
            'nearest_support': support1 if current_price > support1 else support2
        }
    
    def _calculate_trend_strength(self, df: pd.DataFrame) -> Dict:
        """قياس قوة الاتجاه"""
        # استخدام ADX أو حساب بسيط
        atr = ta.volatility.average_true_range(df['high'], df['low'], df['close'])
        current_atr = atr.iloc[-1]
        avg_price = df['close'].mean()
        
        volatility_percent = (current_atr / avg_price) * 100
        
        if volatility_percent < 1:
            strength = "ضعيفة"
            strength_score = 30
        elif volatility_percent < 2:
            strength = "متوسطة"
            strength_score = 60
        else:
            strength = "قوية"
            strength_score = 90
        
        return {
            'strength': strength,
            'score': strength_score,
            'atr': current_atr,
            'volatility_percent': volatility_percent
        }
    
    def _calculate_fibonacci_levels(self, df: pd.DataFrame) -> Dict:
        """حساب مستويات فيبوناتشي"""
        high = df['high'].max()
        low = df['low'].min()
        diff = high - low
        
        return {
            '0.0': low,
            '0.236': low + (diff * 0.236),
            '0.382': low + (diff * 0.382),
            '0.5': low + (diff * 0.5),
            '0.618': low + (diff * 0.618),
            '0.786': low + (diff * 0.786),
            '1.0': high
        }
    
    def generate_trading_signal(self, analysis: Dict, trend_analysis: Dict) -> Tuple[str, float, List]:
        """توليد إشارة تداول احترافية تدمج التحليل الفني + ICT"""
        
        buy_score = 0
        sell_score = 0
        details = []
        
        # ============================================================
        # 1. تحليل ICT (الأساس - 40%)
        # ============================================================
        ict = analysis.get('ict', {})
        if ict and ict.get('ict_signal'):
            ict_strength = ict.get('ict_strength', 50)
            
            if ict['ict_signal'] == 'BUY':
                ict_weight = (ict_strength - 50) / 50 * 40  # تحويل إلى وزن من 0-40
                buy_score += max(0, ict_weight)
                details.append(f"🎯 ICT إشارة شراء قوية ({ict_strength:.0f}%)")
                
                # تفاصيل ICT
                order_blocks = ict.get('order_blocks', {})
                if order_blocks.get('nearest_buy'):
                    details.append("✅ السعر في منطقة Order Block قوية")
                
                fvgs = ict.get('fair_value_gaps', {})
                if fvgs.get('active_fvg') and fvgs['active_fvg'].get('type') == 'bullish':
                    details.append("✅ FVG صاعدة نشطة (سيعود السعر لملؤها)")
                
                liquidity = ict.get('liquidity_zones', {})
                if liquidity.get('active_zone') and liquidity['active_zone'].get('type') == 'demand':
                    details.append("✅ منطقة Demand قوية (تجمع الشراء)")
            
            elif ict['ict_signal'] == 'SELL':
                ict_weight = (100 - ict_strength) / 50 * 40
                sell_score += max(0, ict_weight)
                details.append(f"⚠️ ICT إشارة بيع ({100-ict_strength:.0f}%)")
        
        # ============================================================
        # 2. مؤشرات الترند (EMA + MACD + RSI + Bollinger Bands + ADX - 50%)
        # ============================================================
        
        # EMA Signals (15%)
        if analysis['ema']['signal'] == 'BUY':
            buy_score += 15
            details.append("✅ EMA في ترتيب صاعد قوي")
        elif analysis['ema']['signal'] == 'SELL':
            sell_score += 15
            details.append("❌ EMA في ترتيب هابط")
        
        # RSI Signals (10%)
        rsi_value = analysis['rsi']['value']
        if rsi_value < 30:
            buy_score += 10
            details.append(f"✅ RSI في البيع الزائد ({rsi_value:.0f})")
        elif rsi_value > 70:
            sell_score += 10
            details.append(f"❌ RSI في الشراء الزائد ({rsi_value:.0f})")
        
        # Stochastic RSI Signals (5%) - إضافة جديدة
        if 'stochastic_rsi' in analysis:
            stoch_rsi = analysis['stochastic_rsi']
            if stoch_rsi.get('signal') == 'OVERSOLD':
                buy_score += 5
                details.append(f"✅ Stochastic RSI إفراط بيع ({stoch_rsi.get('value', 0):.0f})")
            elif stoch_rsi.get('signal') == 'OVERBOUGHT':
                sell_score += 5
                details.append(f"❌ Stochastic RSI إفراط شراء ({stoch_rsi.get('value', 0):.0f})")
        
        # MACD Signals (10%)
        if analysis['macd']['trend'] == 'BUY':
            buy_score += 10
            details.append("✅ MACD تقاطع ذهبي صاعد")
        elif analysis['macd']['trend'] == 'SELL':
            sell_score += 10
            details.append("❌ MACD تقاطع مميت")
        
        # Bollinger Bands Signals (8%)
        if 'bollinger_bands' in analysis:
            bb = analysis['bollinger_bands']
            if bb.get('signal') == 'BULLISH':
                buy_score += 8
                details.append("✅ قنوات بولينجر: ضغط/انفجار صاعد")
            elif bb.get('signal') == 'BEARISH':
                sell_score += 8
                details.append("❌ قنوات بولينجر: انحدار هابط")
            elif bb.get('squeeze'):
                # الضغط = انفجار وشيك
                if analysis['ema']['signal'] == 'BUY':
                    buy_score += 5
                    details.append("⚡ قنوات بولينجر: ضغط قوي مع صعود متوقع")
        
        # ADX Trend Confirmation (7%)
        consolidation = analysis.get('consolidation', {})
        if 'adx' in analysis:
            adx = analysis['adx']
            if adx.get('is_trending') and adx.get('score') > 50:
                # في حالة اتجاه قوي
                if analysis['ema']['signal'] == 'BUY':
                    buy_score += 7
                    details.append(f"💪 ADX: اتجاه صاعد قوي ({adx.get('adx_value', 0):.0f})")
                elif analysis['ema']['signal'] == 'SELL':
                    sell_score += 7
                    details.append(f"📉 ADX: اتجاه هابط قوي ({adx.get('adx_value', 0):.0f})")
            elif not adx.get('is_trending'):
                # في حالة النطاق (لا تجاه واضح)
                if consolidation.get('is_consolidating'):
                    buy_score += 3
                    details.append("🔄 ADX: سوق نطاق/توحيد")
        
        # ============================================================
        # 3. اصطياد القيعان والارتدادات (15%) ← جديد
        # ============================================================
        bounce = analysis.get('bounce', {})
        if bounce and bounce.get('found_bounce'):
            bounce_strength = bounce.get('strength', 0)
            rsi_val = analysis['rsi'].get('value', 50)
            stoch_val = analysis['stochastic_rsi'].get('value', 50)
            stoch_signal = analysis['stochastic_rsi'].get('signal', 'NEUTRAL')
            volume_ratio = bounce.get('volume_ratio', 1)
            current_price = analysis.get('current_price', 0) or 0
            support = analysis['support_resistance'].get('nearest_support')
            support_distance_pct = abs(current_price - support) / current_price * 100 if current_price and support else 100
            adx = analysis.get('adx', {})
            ema_signal = analysis['ema'].get('signal')
            macd_trend = analysis['macd'].get('trend')
            ict = analysis.get('ict') or {}
            ict_demand = False
            if ict:
                # نشط منطقة طلب (Demand) أو أقرب Order Block شراء
                active_zone = ict.get('liquidity_zones', {}).get('active_zone')
                if active_zone and active_zone.get('type') == 'demand':
                    ict_demand = True
                if ict.get('order_blocks', {}).get('nearest_buy'):
                    ict_demand = True
                if ict.get('supply_demand', {}).get('demand_level'):
                    ict_demand = True
            # شروط الاصطياد (متوازنة - جودة عالية مع فرص معقولة)
            rsi_ok = rsi_val < 40  # تم التخفيف من 35 إلى 40
            stoch_ok = stoch_val < 85 and stoch_signal != 'OVERBOUGHT'
            volume_ok = volume_ratio >= 1.0  # تم التخفيف من 1.05 إلى 1.0
            support_ok = support_distance_pct <= 3.0  # تم التخفيف من 1.5% إلى 3%
            trend_not_strong_down = not (ema_signal == 'SELL' and adx.get('is_trending') and adx.get('adx_value', 0) > 40)
            if rsi_val < 30:
                trend_not_strong_down = True  # استثناء إذا كان RSI < 30
            momentum_conflict = (ema_signal == 'SELL' and macd_trend == 'SELL' and adx.get('is_trending'))
            avoid_high_stoch = stoch_val > 85
            avoid_low_liquidity = volume_ratio < 0.7  # تم التخفيف من 0.8 إلى 0.7
            
            # الشروط الأساسية (إلزامية)
            core_filters = [rsi_ok, stoch_ok, volume_ok, trend_not_strong_down]
            # الشروط الإضافية (اختيارية - تزيد القوة)
            bonus_filters = [support_ok, ict_demand]
            # علامات التجنب
            avoid_flags = [avoid_high_stoch, avoid_low_liquidity, momentum_conflict]
            
            core_pass = all(core_filters)
            bonus_count = sum(bonus_filters)
            
            # يكفي تحقق الشروط الأساسية + واحد إضافي على الأقل
            if core_pass and bonus_count >= 1 and not any(avoid_flags):
                # إضافة نقاط بناءً على قوة الارتداد + المكافأة من ICT/Support
                base_points = 10
                if bounce_strength >= 70:
                    base_points = 15
                elif bounce_strength >= 50:
                    base_points = 12
                
                # مكافأة إضافية إذا تحققت الشروط الإضافية
                if ict_demand and support_ok:
                    base_points += 3  # أعلى جودة: ICT + دعم قريب
                    details.append(f"🎣 اصطياد قاع قوي ({bounce_strength:.0f}%) + ICT Demand + دعم قريب")
                elif ict_demand:
                    base_points += 2
                    details.append(f"🎣 اصطياد قاع ({bounce_strength:.0f}%) + ICT Demand")
                elif support_ok:
                    base_points += 2
                    details.append(f"🎣 اصطياد قاع ({bounce_strength:.0f}%) + دعم قريب")
                else:
                    details.append(f"♻️ ارتداد محتمل ({bounce_strength:.0f}%)")
                
                buy_score += base_points
                reasons = bounce.get('reasons', [])
                if reasons:
                    details.append(f"   └─ {', '.join(reasons[:2])}")
            else:
                reasons_block = []
                if not rsi_ok: reasons_block.append(f"RSI {rsi_val:.0f} ليس تحت 40")
                if not stoch_ok: reasons_block.append(f"Stoch {stoch_val:.0f} مرتفع")
                if not volume_ok: reasons_block.append(f"حجم {volume_ratio:.1f}x منخفض")
                if not trend_not_strong_down: reasons_block.append("ترند 4H هابط قوي")
                if bonus_count == 0: reasons_block.append("لا ICT ولا دعم قريب")
                if avoid_high_stoch: reasons_block.append("Stoch > 85")
                if avoid_low_liquidity: reasons_block.append("سيولة < 0.7x")
                if momentum_conflict: reasons_block.append("هبوط قوي متزامن")
                details.append("🚫 تم تجاهل اصطياد القاع: " + " | ".join(reasons_block[:3]))
        
        # ============================================================
        # 4. توافق الاتجاه الرئيسي (15%)
        # ============================================================
        if trend_analysis and trend_analysis.get('ema'):
            if trend_analysis['ema']['signal'] == 'BUY':
                buy_score += 15
                details.append("✅ الاتجاه الرئيسي (4H) صاعد قوي")
            elif trend_analysis['ema']['signal'] == 'SELL':
                sell_score += 15
                details.append("❌ الاتجاه الرئيسي (4H) هابط")
        
        # ============================================================
        # 5. منطقة التوحيد + مستويات التحليل (10%)
        # ============================================================
        if consolidation.get('is_consolidating'):
            consolidation_strength = consolidation.get('strength', 50)
            if consolidation_strength >= 50:
                buy_score += 10
                details.append(f"🔎 منطقة توحيد قوية ({consolidation_strength:.0f}/100)")
        
        # ============================================================
        # 6. حساب الإشارة النهائية
        # ============================================================
        total_score = buy_score + sell_score
        
        if total_score == 0:
            return "NEUTRAL", 50, details
        
        buy_percent = (buy_score / total_score) * 100
        
        # تطبيق معايير إضافية (متوازنة)
        # تم تخفيف العتبة لإتاحة فرص أكثر مع الحفاظ على الجودة
        if buy_percent >= 60 and buy_score >= 35:
            return "BUY", buy_percent, details
        elif buy_percent <= 40 and sell_score >= 35:
            return "SELL", buy_percent, details
        else:
            return "NEUTRAL", buy_percent, details

# ============================================================================
# محرك التداول الرئيسي
# ============================================================================

class AdvancedTradingBot:
    """محرك التداول المتقدم الاحترافي"""
    
    def __init__(self, api_key: str, api_secret: str, passphrase: str, telegram_token: str, telegram_chat_id: str):
        """
        التهيئة الأساسية
        
        Args:
            api_key: مفتاح OKX API
            api_secret: سر OKX API
            passphrase: جملة السر
            telegram_token: توكن Telegram Bot
            telegram_chat_id: معرف الدردشة
        """
        
        # تهيئة logging
        self._setup_logging()
        
        # OKX Exchange
        self.exchange = ccxt.okx({
            'apiKey': api_key,
            'secret': api_secret,
            'password': passphrase,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot'
            }
        })
        
        # Telegram
        self.notifier = TelegramNotifier(telegram_token, telegram_chat_id)

        # Start heartbeat thread
        self._start_time = time.time()
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
        
        # Technical Analyzer
        self.analyzer = TechnicalAnalyzer()
        
        # ذاكرة الحالة
        self.top_coins = []
        self.last_analysis_time = {}
        self.paused = False
        self.hammer_active = False
        
        # تخزين مؤقت للبيانات
        self.kline_cache = {}
        self.cache_timestamp = {}
        
        logging.info("🚀 تم تهيئة البوت بنجاح")

    def _heartbeat_loop(self):
        """Send periodic heartbeat messages via Telegram to indicate liveness."""
        try:
            while True:
                uptime = int(time.time() - self._start_time)
                # رسالة heartbeat بسيطة
                heartbeat_msg = f"💓 البوت يعمل بشكل طبيعي | Uptime: {uptime//3600}h {(uptime%3600)//60}m"
                try:
                    self.notifier.session.post(
                        f"{self.notifier.api_url}/sendMessage",
                        json={
                            'chat_id': self.notifier.chat_id,
                            'text': heartbeat_msg,
                            'parse_mode': 'HTML'
                        },
                        timeout=10
                    )
                except Exception as e:
                    logging.warning(f"⚠️ فشل إرسال heartbeat: {e}")
                
                time.sleep(TradingConfig.HEARTBEAT_INTERVAL)
        except Exception:
            pass
    
    def _setup_logging(self):
        """إعداد نظام التسجيل"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('trading_bot.log'),
                logging.StreamHandler()
            ]
        )
    
    def run(self):
        """الحلقة الرئيسية للبوت"""
        logging.info("🚀 بدء حلقة المراقبة الرئيسية")
        
        check_interval = 300  # 5 دقائق
        
        try:
            while True:
                # الخطوة 1: جلب أعلى 25 عملة
                logging.info("\n" + "="*70)
                logging.info("📊 جلب قائمة العملات الجديدة...")
                self.top_coins = self._get_top_25_coins()
                
                if not self.top_coins:
                    logging.warning("⚠️ فشل جلب العملات")
                    time.sleep(60)
                    continue
                
                logging.info(f"✅ تم جلب {len(self.top_coins)} عملة")
                
                # الخطوة 2: تحليل كل عملة
                if not self.paused:
                    self._analyze_all_coins()
                else:
                    logging.info("⏸️ البوت موقوف مؤقتاً")
                
                # الخطوة 3: الانتظار حتى الدورة التالية
                logging.info(f"⏳ الانتظار {check_interval} ثانية...")
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            logging.info("\n⏹️ تم إيقاف البوت")
        except Exception as e:
            logging.error(f"❌ خطأ في الحلقة الرئيسية: {e}", exc_info=True)
    
    def _get_top_25_coins(self) -> List[Dict]:
        """جلب أعلى 25 عملة بحجم التداول"""
        try:
            # use safe fetch with retries/backoff
            markets, tickers = self._safe_fetch_markets_and_tickers()
            
            coins_data = []
            
            for market in markets:
                if market['quote'] == 'USDT' and market['spot']:
                    symbol = market['symbol']
                    
                    # تخطي العملات المستقرة
                    base = market['base']
                    if base in TradingConfig.STABLE_COINS:
                        continue
                    
                    if symbol in tickers:
                        ticker = tickers[symbol]
                        volume = ticker.get('quoteVolume', 0)
                        change_24h = ticker.get('percentage', 0)
                        
                        # تطبيق الفلاتر
                        if volume > TradingConfig.MIN_VOLUME_USDT:
                            coins_data.append({
                                'symbol': symbol,
                                'base': base,
                                'volume': volume,
                                'price': ticker.get('last', 0),
                                'change_24h': change_24h,
                                'high_24h': ticker.get('high', 0),
                                'low_24h': ticker.get('low', 0),
                                'bid': ticker.get('bid', 0),
                                'ask': ticker.get('ask', 0)
                            })
            
            # الترتيب والتصفية
            coins_data.sort(key=lambda x: x['volume'], reverse=True)
            return coins_data[:25]
        
        except Exception as e:
            logging.error(f"❌ خطأ في جلب العملات: {e}")
            return []

    def _safe_fetch_markets_and_tickers(self, retries: int = 3, backoff: float = 1.0):
        """Fetch markets and tickers with simple retry/backoff to handle transient network errors."""
        attempt = 0
        last_exc = None
        while attempt < retries:
            try:
                markets = self.exchange.fetch_markets()
                tickers = self.exchange.fetch_tickers()
                return markets, tickers
            except Exception as e:
                last_exc = e
                wait = backoff * (2 ** attempt)
                logging.warning(f"⚠️ fetch_markets/tickers failed (attempt {attempt+1}/{retries}): {e}; retrying in {wait}s")
                time.sleep(wait)
                attempt += 1
        raise last_exc
    
    def _analyze_all_coins(self):
        """تحليل كل العملات بكفاءة"""
        # Use a thread pool to analyze coins concurrently for speed
        def _process_coin(idx_coin):
            idx, coin = idx_coin
            symbol = coin['symbol']
            try:
                logging.info(f"\n[{idx}/{len(self.top_coins)}] 📊 تحليل {symbol}...")

                # load cached or fetch
                trend_df = self._get_cached_klines(symbol, TradingConfig.TREND_TIMEFRAME)
                entry_df = self._get_cached_klines(symbol, TradingConfig.ENTRY_TIMEFRAME)

                if trend_df is None or entry_df is None:
                    logging.warning(f"⚠️ فشل جلب بيانات {symbol}")
                    return

                # تمرير symbol للتحليل
                trend_analysis = self.analyzer.analyze_candles(trend_df, symbol)
                entry_analysis = self.analyzer.analyze_candles(entry_df, symbol)

                if trend_analysis is None or entry_analysis is None:
                    return

                signal, strength, details = self.analyzer.generate_trading_signal(entry_analysis, trend_analysis)

                # معايير ديناميكية حسب الوضع (Scalping أو Normal)
                min_strength = TradingConfig.SCALPING_MIN_STRENGTH if TradingConfig.SCALPING_MODE else 60
                
                if signal != 'NEUTRAL' and strength >= min_strength:
                    self._send_trading_alert(symbol, coin, signal, strength, entry_analysis, trend_analysis, details)
                else:
                    logging.info(f"📊 {symbol}: {signal} (قوة: {strength:.0f}%) - ضعيفة")

            except Exception as e:
                logging.error(f"❌ خطأ في تحليل {symbol}: {e}", exc_info=True)

        # Prepare list with indices
        items = list(enumerate(self.top_coins, start=1))

        max_workers = min(TradingConfig.MAX_CONCURRENT_ANALYSIS, max(1, len(items)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(_process_coin, item) for item in items]
            for f in as_completed(futures):
                # exceptions are logged inside _process_coin; just ensure completion
                try:
                    f.result()
                except Exception:
                    pass
    
    def _get_cached_klines(self, symbol: str, timeframe: str, limit: int = 100) -> Optional[pd.DataFrame]:
        """جلب البيانات مع التخزين المؤقت"""
        
        cache_key = f"{symbol}_{timeframe}"
        current_time = time.time()
        
        # التحقق من صحة الكاش
        if (cache_key in self.kline_cache and 
            current_time - self.cache_timestamp.get(cache_key, 0) < TradingConfig.CACHE_TIMEOUT):
            return self.kline_cache[cache_key]
        
        try:
            klines = self._safe_fetch_ohlcv(symbol, timeframe, limit=limit)
            
            df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.set_index('timestamp')
            
            # حفظ في الكاش
            self.kline_cache[cache_key] = df
            self.cache_timestamp[cache_key] = current_time
            
            return df
        
        except Exception as e:
            logging.error(f"❌ خطأ في جلب البيانات {symbol}/{timeframe}: {e}")
            return None

    def _safe_fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 100, retries: int = 3, backoff: float = 1.0):
        """Fetch OHLCV with retries/backoff for transient errors."""
        attempt = 0
        last_exc = None
        while attempt < retries:
            try:
                return self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            except Exception as e:
                last_exc = e
                wait = backoff * (2 ** attempt)
                logging.warning(f"⚠️ fetch_ohlcv {symbol} {timeframe} failed (attempt {attempt+1}/{retries}): {e}; retrying in {wait}s")
                time.sleep(wait)
                attempt += 1
        raise last_exc
    
    def _send_trading_alert(self, symbol: str, coin: Dict, signal: str, strength: float,
                           entry_analysis: Dict, trend_analysis: Dict, details: List):
        """إرسال تنبيه التداول عبر Telegram مع تفاصيل ICT"""
        
        current_price = coin['price']
        
        # ============================================================
        # حساب الأهداف بناءً على الوضع (Scalping أو Normal)
        # ============================================================
        if TradingConfig.SCALPING_MODE:
            # وضع Scalping - أهداف صغيرة، SL صغير، فرص متكررة
            if signal == 'BUY':
                target1_percent = TradingConfig.SCALPING_TARGET_MIN
                target2_percent = TradingConfig.SCALPING_TARGET_MAX
                sl_percent = TradingConfig.SCALPING_STOP_LOSS
            else:
                target1_percent = -TradingConfig.SCALPING_TARGET_MIN
                target2_percent = -TradingConfig.SCALPING_TARGET_MAX
                sl_percent = TradingConfig.SCALPING_STOP_LOSS
            
            target1 = current_price * (1 + target1_percent / 100)
            target2 = current_price * (1 + target2_percent / 100)
            stop_loss = current_price * (1 - sl_percent / 100) if signal == 'BUY' else current_price * (1 + sl_percent / 100)
        else:
            # وضع Normal - أهداف أكبر، SL أكبر
            if signal == 'BUY':
                target1_percent = TradingConfig.TARGET_PROFIT_MIN + (strength - 50) * 0.08
                target2_percent = TradingConfig.TARGET_PROFIT_MAX + (strength - 50) * 0.12
            else:
                target1_percent = -TradingConfig.TARGET_PROFIT_MIN - (strength - 50) * 0.08
                target2_percent = -TradingConfig.TARGET_PROFIT_MAX - (strength - 50) * 0.12
            
            # تأكد من الحد الأدنى
            if signal == 'BUY':
                target1_percent = max(target1_percent, 4.0)
                target2_percent = max(target2_percent, 6.0)
            else:
                target1_percent = min(target1_percent, -4.0)
                target2_percent = min(target2_percent, -6.0)

            target1 = current_price * (1 + target1_percent / 100)
            target2 = current_price * (1 + target2_percent / 100)
            stop_loss = current_price * (1 - (strength - 50) / 100 * 0.05) if signal == 'BUY' else current_price * (1 + (strength - 50) / 100 * 0.05)
        
        # تجميع تفاصيل ICT
        ict_details = "\n".join(details) if details else "بيانات غير متوفرة"
        
        # تحديد نوع الإشارة (Signal Category)
        signal_category = self._determine_signal_category(entry_analysis, entry_analysis.get('bounce', {}), trend_analysis)
        
        # إعداد بيانات التنبيه (مضغوطة - المعلومات الأساسية فقط)
        alert_data = {
            'signal_type': signal,
            'signal_category': signal_category,
            'signal_strength': strength,
            'current_price': current_price,
            'change_24h': coin['change_24h'],
            'target1': target1,
            'target2': target2,
            'stop_loss': stop_loss,
            'rsi': entry_analysis['rsi']['value'],
            'macd_signal': entry_analysis['macd']['condition'],
            'ema_status': entry_analysis['ema']['status']
        }
        
        # إرسال التنبيه (الآن نتحقق من نجاح الإرسال قبل تسجيله)
        sent = self.notifier.send_alert(symbol, alert_data)
        if sent:
            logging.info(f"✅ تم إرسال تنبيه جديد {symbol}: {signal} (قوة: {strength:.0f}%) - الصيغة الجديدة مع ICT")
            logging.info(f"   🎯 تحليل ICT: {ict_details[:150]}")
        else:
            logging.warning(f"❌ فشل إرسال التنبيه {symbol}: {signal} (قوة: {strength:.0f}%) — راجع اتصال الشبكة / إعدادات Telegram")
    


    def _detect_bottom_bounce(self, df: pd.DataFrame) -> Dict:
        """
        كشف فرص القيعان والارتدادات المحتملة
        - Support Bounce: ارتداد من مستوى دعم
        - RSI Oversold Bounce: ارتداد من إفراط بيع
        - Bollinger Bottom Bounce: ارتداد من القناة السفلى
        """
        try:
            current_price = df['close'].iloc[-1]
            prev_price = df['close'].iloc[-2]
            
            bounce_signals = {
                'support_bounce': False,
                'rsi_bounce': False,
                'bb_bounce': False,
                'bounce_strength': 0,
                'bounce_type': 'NONE'
            }
            
            # 1. كشف الارتداد من الدعم
            support_levels = self._find_support_resistance(df).get('support', current_price)
            if current_price > support_levels and prev_price <= support_levels:
                bounce_signals['support_bounce'] = True
                bounce_signals['bounce_type'] = 'SUPPORT_BOUNCE'
            
            # 2. كشف الارتداد من إفراط البيع (RSI < 30)
            rsi = ta.momentum.rsi(df['close'], window=14)
            current_rsi = rsi.iloc[-1]
            if current_rsi < 30 and current_rsi > rsi.iloc[-2]:  # يرتفع من تحت 30
                bounce_signals['rsi_bounce'] = True
                if bounce_signals['bounce_type'] == 'NONE':
                    bounce_signals['bounce_type'] = 'RSI_BOUNCE'
            
            # 3. كشف الارتداد من قناة بولينجر السفلى
            bb = self._calculate_bollinger_bands(df)
            bb_lower = bb.get('lower_band', current_price)
            if current_price > bb_lower and prev_price <= bb_lower:
                bounce_signals['bb_bounce'] = True
                if bounce_signals['bounce_type'] == 'NONE':
                    bounce_signals['bounce_type'] = 'BB_BOUNCE'
            
            # حساب قوة الارتداد
            if bounce_signals['support_bounce'] or bounce_signals['rsi_bounce'] or bounce_signals['bb_bounce']:
                bounce_signals['bounce_strength'] = 60  # نقاط إضافية
            
            return bounce_signals
            
        except Exception as e:
            logging.warning(f"⚠️ Bottom bounce detection failed: {e}")
            return {
                'support_bounce': False,
                'rsi_bounce': False,
                'bb_bounce': False,
                'bounce_strength': 0,
                'bounce_type': 'NONE'
            }
    
    def _determine_signal_category(self, analysis: Dict, bounce_data: Dict, trend_analysis: Dict) -> str:
        """
        تحديد نوع الإشارة لعرضها في التنبيه
        - Trend Continuation: استمرار ترند قوي
        - Bottom Bounce: ارتداد من قاع
        - Support Bounce: ارتداد من دعم
        - RSI Bounce: ارتداد من إفراط بيع
        - Breakout: كسر مقاومة
        - Pullback Entry: دخول في تراجع
        """
        
        # الحصول على البيانات الأساسية
        ict = analysis.get('ict', {})
        ema = analysis.get('ema', {})
        adx = analysis.get('adx', {})
        trend_4h = trend_analysis.get('ema', {}).get('signal', 'NEUTRAL')
        
        # 1. استمرار الترند القوي
        if ema.get('signal') == 'BUY' and adx.get('is_trending') and adx.get('score', 0) > 50:
            return "استمرار ترند قوي 📈"
        elif ema.get('signal') == 'SELL' and adx.get('is_trending') and adx.get('score', 0) > 50:
            return "استمرار هبوط قوي 📉"
        
        # 2. الارتدادات المختلفة
        if bounce_data.get('bounce_type') != 'NONE':
            if bounce_data['bounce_type'] == 'SUPPORT_BOUNCE':
                return "ارتداد من مستوى دعم 🎯"
            elif bounce_data['bounce_type'] == 'RSI_BOUNCE':
                return "ارتداد من إفراط بيع 💪"
            elif bounce_data['bounce_type'] == 'BB_BOUNCE':
                return "ارتداد من قناة بولينجر 📊"
        
        # 3. كسر مقاومة
        if ema.get('signal') == 'BUY' and adx.get('score', 0) > 40:
            return "كسر مقاومة صاعد 🚀"
        
        # 4. دخول في تراجع (Pullback)
        if ema.get('signal') == 'BUY' and 30 <= analysis.get('rsi', {}).get('value', 50) <= 50:
            return "دخول في تراجع 📍"
        
        # 5. قاع من ترند هابط في الإطار الأكبر (4H) يرتفع الآن
        if ema.get('signal') == 'BUY' and trend_4h == 'NEUTRAL':
            return "قاع مع تغيير اتجاه 🔄"
        
        # الافتراضي
        return "إشارة عادية ✅"

# ============================================================================
# نقطة الدخول الرئيسية
# ============================================================================

if __name__ == "__main__":
    # تحميل الإعدادات من trading_config.json
    try:
        with open('trading_config.json', 'r') as f:
            config = json.load(f)
        
        # تهيئة البوت
        bot = AdvancedTradingBot(
            api_key=config['okx']['api_key'],
            api_secret=config['okx']['api_secret'],
            passphrase=config['okx']['passphrase'],
            telegram_token=config['telegram']['bot_token'],
            telegram_chat_id=config['telegram']['chat_id']
        )
        
        # بدء التشغيل
        bot.run()
        
    except FileNotFoundError:
        print("❌ ملف trading_config.json غير موجود!")
        sys.exit(1)
    except KeyError as e:
        print(f"❌ مفتاح مفقود في الإعدادات: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        logging.error(f"❌ خطأ في التشغيل: {e}", exc_info=True)
        sys.exit(1)
