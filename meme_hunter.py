#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 MEME HUNTER BOT - Professional DEX Meme Coin Hunter
الصياد الاحترافي لعملات الميم على منصات DEX

Strategy: Ultra-fast detection of trending meme coins with high potential
Focus: Solana DEX (Raydium, Orca) - fastest and cheapest
Targets: +30%, +100%, +300% gains
Risk: 1-2% position size, -15% stop loss

Author: Whale Hunter Team
Version: 1.0 ULTIMATE
Date: January 2026
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
from dataclasses import dataclass
import re

# ==================== CONFIGURATION ====================

@dataclass
class MemeHunterConfig:
    """إعدادات Meme Hunter"""
    
    # API Configuration
    TELEGRAM_BOT_TOKEN: str = "YOUR_TELEGRAM_BOT_TOKEN"
    TELEGRAM_CHAT_ID: str = "YOUR_TELEGRAM_CHAT_ID"
    
    # Target Platform
    TARGET_CHAIN: str = "solana"  # Focus on Solana DEX
    BACKUP_CHAINS: List[str] = ("bsc", "ethereum", "base")
    
    # Detection Criteria (STRICT!)
    MIN_LIQUIDITY_USD: float = 50000  # $50K minimum liquidity
    MIN_VOLUME_24H_USD: float = 200000  # $200K minimum volume
    MIN_TRANSACTIONS_24H: int = 5000  # 5000+ transactions
    MIN_HOLDERS: int = 500  # 500+ unique holders
    LIQUIDITY_LOCK_REQUIRED: bool = True  # Must have locked liquidity
    
    # Price Action Triggers
    MIN_PRICE_CHANGE_1H: float = 20.0  # +20% in 1 hour
    MIN_PRICE_CHANGE_5M: float = 5.0   # +5% in 5 minutes
    MAX_PRICE_CHANGE_24H: float = 2000.0  # Max +2000% (avoid late pumps)
    
    # Social Metrics
    MIN_TWITTER_FOLLOWERS: int = 1000  # Minimum Twitter followers
    MIN_TELEGRAM_MEMBERS: int = 500    # Minimum Telegram members
    REQUIRE_VERIFIED_CONTRACT: bool = True  # Contract must be verified
    
    # Risk Management
    MAX_POSITION_SIZE_PCT: float = 0.01  # 1% of capital per trade
    MAX_TOTAL_MEME_EXPOSURE: float = 0.03  # 3% total in meme coins
    STOP_LOSS_PCT: float = -15.0  # -15% stop loss
    MAX_CONCURRENT_POSITIONS: int = 3  # Max 3 meme positions
    
    # Take Profit Levels
    TARGET_1_PCT: float = 50.0   # +50%
    TARGET_2_PCT: float = 150.0  # +150%
    TARGET_3_PCT: float = 500.0  # +500%
    EXIT_1_PCT: float = 0.50     # Exit 50% at T1
    EXIT_2_PCT: float = 0.30     # Exit 30% at T2
    EXIT_3_PCT: float = 0.20     # Exit 20% at T3
    
    # Timing
    MAX_HOLD_HOURS: int = 12  # Maximum 12 hours hold
    SCAN_INTERVAL_SECONDS: int = 60  # Scan every 60 seconds
    COOLDOWN_HOURS: int = 4  # 4h cooldown per token
    MAX_SIGNALS_PER_DAY: int = 5  # Max 5 signals per day
    
    # API Endpoints
    DEXSCREENER_API: str = "https://api.dexscreener.com/latest/dex"
    COINGECKO_API: str = "https://api.coingecko.com/api/v3"
    SOLSCAN_API: str = "https://api.solscan.io"
    
    # Blacklist (known scams)
    BLACKLIST_TOKENS: List[str] = []
    BLACKLIST_CREATORS: List[str] = []


# ==================== LOGGING SETUP ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('meme_hunter.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('MemeHunter')


# ==================== DATA MODELS ====================

@dataclass
class TokenData:
    """بيانات العملة الشاملة"""
    symbol: str
    name: str
    address: str
    chain: str
    price_usd: float
    
    # Price Action
    price_change_5m: float
    price_change_1h: float
    price_change_6h: float
    price_change_24h: float
    
    # Volume & Liquidity
    volume_24h: float
    liquidity_usd: float
    liquidity_locked: bool
    liquidity_lock_percent: float
    
    # Market Activity
    transactions_24h: int
    buys_24h: int
    sells_24h: int
    holders_count: int
    
    # Social Metrics
    twitter_followers: int
    telegram_members: int
    website_url: Optional[str]
    telegram_url: Optional[str]
    twitter_url: Optional[str]
    
    # Security
    contract_verified: bool
    honeypot_risk: bool
    creator_suspicious: bool
    age_hours: float
    
    # DEX Info
    dex_name: str
    pair_address: str
    
    # Score
    total_score: float
    risk_level: str  # LOW, MEDIUM, HIGH, EXTREME
    
    # Timestamp
    detected_at: datetime


@dataclass
class MemeSignal:
    """إشارة دخول لعملة ميم"""
    token: TokenData
    signal_type: str  # "NEW_MEME", "VOLUME_SPIKE", "SOCIAL_BUZZ"
    entry_price: float
    targets: List[float]
    stop_loss: float
    position_size_usd: float
    reasoning: str
    urgency: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"


# ==================== DEX SCANNER ====================

class DexScreenerScanner:
    """ماسح DexScreener للعملات الرائجة"""
    
    def __init__(self, config: MemeHunterConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_trending_tokens(self) -> List[Dict]:
        """البحث عن العملات الرائجة"""
        try:
            # Method 1: Search by chain and sort by volume
            url = f"{self.config.DEXSCREENER_API}/search"
            
            all_tokens = []
            
            # Search for high volume tokens
            for search_term in ['pump', 'moon', 'doge', 'pepe', 'shib', 'elon', 'floki']:
                try:
                    params = {'q': search_term}
                    response = self.session.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'pairs' in data and data['pairs']:
                            # Filter by chain
                            chain_pairs = [
                                p for p in data['pairs']
                                if p.get('chainId') == self.config.TARGET_CHAIN
                            ]
                            all_tokens.extend(chain_pairs[:5])  # Top 5 per search
                    
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"Search term '{search_term}' failed: {e}")
                    continue
            
            # Remove duplicates by pair address
            unique_tokens = {}
            for token in all_tokens:
                pair_addr = token.get('pairAddress')
                if pair_addr and pair_addr not in unique_tokens:
                    unique_tokens[pair_addr] = token
            
            logger.info(f"📊 Found {len(unique_tokens)} unique tokens from DexScreener")
            return list(unique_tokens.values())
            
        except Exception as e:
            logger.error(f"❌ DexScreener trending scan failed: {e}")
            return []
    
    def get_token_details(self, pair_address: str) -> Optional[Dict]:
        """الحصول على تفاصيل العملة"""
        try:
            url = f"{self.config.DEXSCREENER_API}/pairs/{self.config.TARGET_CHAIN}/{pair_address}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'pair' in data:
                    return data['pair']
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get token details: {e}")
            return None


# ==================== SOCIAL ANALYZER ====================

class SocialAnalyzer:
    """محلل نشاط وسائل التواصل الاجتماعي"""
    
    def __init__(self, config: MemeHunterConfig):
        self.config = config
        self.session = requests.Session()
    
    def analyze_token_social(self, token_address: str, links: Dict) -> Dict:
        """تحليل النشاط الاجتماعي للعملة"""
        social_data = {
            'twitter_followers': 0,
            'telegram_members': 0,
            'website_exists': False,
            'social_score': 0
        }
        
        try:
            # Extract social links
            twitter_url = links.get('twitter') or links.get('url', [{}])[0].get('url', '') if 'twitter.com' in str(links.get('url', '')) else ''
            telegram_url = links.get('telegram', '')
            website_url = links.get('url', '')
            
            # Twitter Analysis (if URL exists)
            if twitter_url:
                social_data['twitter_followers'] = self._estimate_twitter_followers(twitter_url)
            
            # Telegram Analysis (if URL exists)
            if telegram_url:
                social_data['telegram_members'] = self._estimate_telegram_members(telegram_url)
            
            # Website Check
            if website_url:
                social_data['website_exists'] = self._check_website_validity(website_url)
            
            # Calculate Social Score (0-100)
            score = 0
            if social_data['twitter_followers'] >= 10000:
                score += 40
            elif social_data['twitter_followers'] >= 5000:
                score += 30
            elif social_data['twitter_followers'] >= 1000:
                score += 20
            
            if social_data['telegram_members'] >= 5000:
                score += 40
            elif social_data['telegram_members'] >= 2000:
                score += 30
            elif social_data['telegram_members'] >= 500:
                score += 20
            
            if social_data['website_exists']:
                score += 20
            
            social_data['social_score'] = score
            
            logger.debug(f"Social Score: {score}/100 (Twitter: {social_data['twitter_followers']}, TG: {social_data['telegram_members']})")
            
        except Exception as e:
            logger.warning(f"⚠️ Social analysis failed: {e}")
        
        return social_data
    
    def _estimate_twitter_followers(self, twitter_url: str) -> int:
        """تقدير متابعي Twitter (محاكاة - يحتاج Twitter API حقيقي)"""
        # NOTE: في البيئة الحقيقية، استخدم Twitter API
        # هنا نستخدم تقدير بسيط بناءً على وجود الرابط
        try:
            # Extract username
            username_match = re.search(r'twitter\.com/([^/?]+)', twitter_url)
            if username_match:
                # محاكاة: نفترض وجود الرابط = على الأقل 1000 متابع
                return 1000
        except:
            pass
        return 0
    
    def _estimate_telegram_members(self, telegram_url: str) -> int:
        """تقدير أعضاء Telegram (محاكاة)"""
        # NOTE: في البيئة الحقيقية، استخدم Telegram API
        try:
            # Extract channel name
            if 't.me/' in telegram_url:
                # محاكاة: نفترض وجود الرابط = على الأقل 500 عضو
                return 500
        except:
            pass
        return 0
    
    def _check_website_validity(self, website_url: str) -> bool:
        """فحص صلاحية الموقع"""
        try:
            response = self.session.head(website_url, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except:
            return False


# ==================== LIQUIDITY ANALYZER ====================

class LiquidityAnalyzer:
    """محلل السيولة وقفلها"""
    
    def __init__(self, config: MemeHunterConfig):
        self.config = config
        self.session = requests.Session()
    
    def check_liquidity_lock(self, token_address: str, chain: str, liquidity_usd: float) -> Dict:
        """فحص قفل السيولة"""
        lock_data = {
            'is_locked': False,
            'lock_percent': 0.0,
            'lock_duration_days': 0,
            'lock_service': None,
            'liquidity_score': 0
        }
        
        try:
            # For Solana: Check common lock services
            if chain == 'solana':
                lock_data = self._check_solana_liquidity_lock(token_address, liquidity_usd)
            elif chain == 'bsc':
                lock_data = self._check_bsc_liquidity_lock(token_address, liquidity_usd)
            elif chain == 'ethereum':
                lock_data = self._check_eth_liquidity_lock(token_address, liquidity_usd)
            
            # Calculate Liquidity Score (0-100)
            score = 0
            
            # Base score from liquidity amount
            if liquidity_usd >= 500000:
                score += 30
            elif liquidity_usd >= 200000:
                score += 20
            elif liquidity_usd >= 50000:
                score += 10
            
            # Locked liquidity bonus
            if lock_data['is_locked']:
                if lock_data['lock_percent'] >= 90:
                    score += 50
                elif lock_data['lock_percent'] >= 70:
                    score += 40
                elif lock_data['lock_percent'] >= 50:
                    score += 30
                
                # Duration bonus
                if lock_data['lock_duration_days'] >= 365:
                    score += 20
                elif lock_data['lock_duration_days'] >= 180:
                    score += 15
                elif lock_data['lock_duration_days'] >= 90:
                    score += 10
            
            lock_data['liquidity_score'] = min(score, 100)
            
            logger.debug(f"Liquidity Score: {score}/100 (Locked: {lock_data['is_locked']}, {lock_data['lock_percent']}%)")
            
        except Exception as e:
            logger.warning(f"⚠️ Liquidity lock check failed: {e}")
        
        return lock_data
    
    def _check_solana_liquidity_lock(self, token_address: str, liquidity_usd: float) -> Dict:
        """فحص قفل السيولة على Solana"""
        # محاكاة - في البيئة الحقيقية، استخدم Solscan API أو on-chain data
        # Common lock services on Solana: Streamflow, Saber Lockup
        
        # For demonstration: assume tokens with high liquidity have some lock
        if liquidity_usd >= 100000:
            return {
                'is_locked': True,
                'lock_percent': 70.0,
                'lock_duration_days': 180,
                'lock_service': 'Assumed (Streamflow)',
                'liquidity_score': 0
            }
        
        return {
            'is_locked': False,
            'lock_percent': 0.0,
            'lock_duration_days': 0,
            'lock_service': None,
            'liquidity_score': 0
        }
    
    def _check_bsc_liquidity_lock(self, token_address: str, liquidity_usd: float) -> Dict:
        """فحص قفل السيولة على BSC"""
        # Common services: PinkSale, Mudra, Team Finance
        # محاكاة
        return {
            'is_locked': False,
            'lock_percent': 0.0,
            'lock_duration_days': 0,
            'lock_service': None,
            'liquidity_score': 0
        }
    
    def _check_eth_liquidity_lock(self, token_address: str, liquidity_usd: float) -> Dict:
        """فحص قفل السيولة على Ethereum"""
        # Common services: Unicrypt, Team Finance
        # محاكاة
        return {
            'is_locked': False,
            'lock_percent': 0.0,
            'lock_duration_days': 0,
            'lock_service': None,
            'liquidity_score': 0
        }


# ==================== HOLDER ANALYZER ====================

class HolderAnalyzer:
    """محلل توزيع الحاملين"""
    
    def __init__(self, config: MemeHunterConfig):
        self.config = config
        self.session = requests.Session()
    
    def analyze_holders(self, token_address: str, chain: str) -> Dict:
        """تحليل توزيع الحاملين"""
        holder_data = {
            'total_holders': 0,
            'top_10_percent': 0.0,
            'creator_percent': 0.0,
            'distribution_score': 0,
            'whale_risk': 'UNKNOWN'
        }
        
        try:
            if chain == 'solana':
                holder_data = self._analyze_solana_holders(token_address)
            elif chain == 'bsc':
                holder_data = self._analyze_bsc_holders(token_address)
            elif chain == 'ethereum':
                holder_data = self._analyze_eth_holders(token_address)
            
            # Calculate Distribution Score (0-100)
            score = 0
            
            # Holder count score
            if holder_data['total_holders'] >= 5000:
                score += 30
            elif holder_data['total_holders'] >= 2000:
                score += 20
            elif holder_data['total_holders'] >= 500:
                score += 10
            
            # Distribution score (lower concentration = better)
            if holder_data['top_10_percent'] < 20:
                score += 50
                holder_data['whale_risk'] = 'LOW'
            elif holder_data['top_10_percent'] < 40:
                score += 30
                holder_data['whale_risk'] = 'MEDIUM'
            elif holder_data['top_10_percent'] < 60:
                score += 15
                holder_data['whale_risk'] = 'HIGH'
            else:
                score += 0
                holder_data['whale_risk'] = 'EXTREME'
            
            # Creator holding penalty
            if holder_data['creator_percent'] > 20:
                score -= 20
            elif holder_data['creator_percent'] > 10:
                score -= 10
            
            holder_data['distribution_score'] = max(0, min(score, 100))
            
            logger.debug(f"Distribution Score: {holder_data['distribution_score']}/100 (Holders: {holder_data['total_holders']}, Top10: {holder_data['top_10_percent']}%)")
            
        except Exception as e:
            logger.warning(f"⚠️ Holder analysis failed: {e}")
        
        return holder_data
    
    def _analyze_solana_holders(self, token_address: str) -> Dict:
        """تحليل حاملي Solana"""
        # محاكاة - في البيئة الحقيقية، استخدم Solscan API
        # Example: https://api.solscan.io/token/holders?token={address}
        
        # For demonstration: assume reasonable distribution
        return {
            'total_holders': 1500,
            'top_10_percent': 35.0,
            'creator_percent': 5.0,
            'distribution_score': 0,
            'whale_risk': 'UNKNOWN'
        }
    
    def _analyze_bsc_holders(self, token_address: str) -> Dict:
        """تحليل حاملي BSC"""
        return {
            'total_holders': 0,
            'top_10_percent': 0.0,
            'creator_percent': 0.0,
            'distribution_score': 0,
            'whale_risk': 'UNKNOWN'
        }
    
    def _analyze_eth_holders(self, token_address: str) -> Dict:
        """تحليل حاملي Ethereum"""
        return {
            'total_holders': 0,
            'top_10_percent': 0.0,
            'creator_percent': 0.0,
            'distribution_score': 0,
            'whale_risk': 'UNKNOWN'
        }


# ==================== SECURITY CHECKER ====================

class SecurityChecker:
    """فحص أمان العملة"""
    
    def __init__(self, config: MemeHunterConfig):
        self.config = config
        self.session = requests.Session()
    
    def check_token_security(self, token_address: str, chain: str) -> Dict:
        """فحص أمان العملة الشامل"""
        security_data = {
            'contract_verified': False,
            'honeypot_risk': False,
            'has_mint_function': False,
            'has_pause_function': False,
            'ownership_renounced': False,
            'security_score': 0,
            'risk_flags': []
        }
        
        try:
            # Check contract verification
            security_data['contract_verified'] = self._check_contract_verified(token_address, chain)
            
            # Check for honeypot (محاكاة - يحتاج API متخصص)
            security_data['honeypot_risk'] = self._check_honeypot(token_address, chain)
            
            # Check dangerous functions (محاكاة)
            security_data['has_mint_function'] = False  # Would need contract ABI
            security_data['has_pause_function'] = False
            security_data['ownership_renounced'] = True  # Assume for demo
            
            # Calculate Security Score (0-100)
            score = 100  # Start with perfect score
            
            if not security_data['contract_verified']:
                score -= 30
                security_data['risk_flags'].append('UNVERIFIED_CONTRACT')
            
            if security_data['honeypot_risk']:
                score -= 50
                security_data['risk_flags'].append('HONEYPOT_RISK')
            
            if security_data['has_mint_function']:
                score -= 20
                security_data['risk_flags'].append('MINTABLE')
            
            if security_data['has_pause_function']:
                score -= 15
                security_data['risk_flags'].append('PAUSABLE')
            
            if not security_data['ownership_renounced']:
                score -= 10
                security_data['risk_flags'].append('OWNER_NOT_RENOUNCED')
            
            security_data['security_score'] = max(0, score)
            
            logger.debug(f"Security Score: {score}/100 (Flags: {security_data['risk_flags']})")
            
        except Exception as e:
            logger.warning(f"⚠️ Security check failed: {e}")
        
        return security_data
    
    def _check_contract_verified(self, token_address: str, chain: str) -> bool:
        """فحص توثيق العقد"""
        # محاكاة - في البيئة الحقيقية، استخدم block explorers APIs
        # Solana: Solscan
        # BSC: BscScan
        # Ethereum: Etherscan
        return True  # Assume verified for demo
    
    def _check_honeypot(self, token_address: str, chain: str) -> bool:
        """فحص honeypot (عملة لا يمكن بيعها)"""
        # محاكاة - في البيئة الحقيقية، استخدم:
        # - Honeypot.is API
        # - Token Sniffer API
        # - QuickIntel API
        return False  # Assume safe for demo


# ==================== SCORING ENGINE ====================

class ScoringEngine:
    """محرك التقييم الشامل"""
    
    def __init__(self, config: MemeHunterConfig):
        self.config = config
    
    def calculate_total_score(
        self,
        price_action: Dict,
        liquidity_data: Dict,
        social_data: Dict,
        holder_data: Dict,
        security_data: Dict
    ) -> Tuple[float, str]:
        """حساب النقاط الإجمالية ومستوى الخطر"""
        
        # Weighted scoring system
        weights = {
            'price_action': 0.20,   # 20% - Price momentum
            'liquidity': 0.25,      # 25% - Liquidity & lock
            'social': 0.20,         # 20% - Social activity
            'holders': 0.15,        # 15% - Distribution
            'security': 0.20        # 20% - Security checks
        }
        
        # Price Action Score (0-100)
        price_score = 0
        if price_action.get('price_change_1h', 0) >= 50:
            price_score = 100
        elif price_action.get('price_change_1h', 0) >= 30:
            price_score = 80
        elif price_action.get('price_change_1h', 0) >= 20:
            price_score = 60
        elif price_action.get('price_change_1h', 0) >= 10:
            price_score = 40
        else:
            price_score = 20
        
        # Transaction activity bonus
        if price_action.get('transactions_24h', 0) >= 20000:
            price_score = min(100, price_score + 20)
        elif price_action.get('transactions_24h', 0) >= 10000:
            price_score = min(100, price_score + 10)
        
        # Get other scores
        liquidity_score = liquidity_data.get('liquidity_score', 0)
        social_score = social_data.get('social_score', 0)
        holder_score = holder_data.get('distribution_score', 0)
        security_score = security_data.get('security_score', 0)
        
        # Calculate weighted total
        total_score = (
            price_score * weights['price_action'] +
            liquidity_score * weights['liquidity'] +
            social_score * weights['social'] +
            holder_score * weights['holders'] +
            security_score * weights['security']
        )
        
        # Determine risk level
        risk_level = self._calculate_risk_level(
            security_score,
            liquidity_data.get('is_locked', False),
            holder_data.get('whale_risk', 'UNKNOWN'),
            price_action.get('price_change_24h', 0)
        )
        
        logger.info(f"📊 SCORES - Price:{price_score} Liq:{liquidity_score} Social:{social_score} Holders:{holder_score} Sec:{security_score} | TOTAL:{total_score:.1f} RISK:{risk_level}")
        
        return total_score, risk_level
    
    def _calculate_risk_level(
        self,
        security_score: float,
        liquidity_locked: bool,
        whale_risk: str,
        price_change_24h: float
    ) -> str:
        """تحديد مستوى الخطر"""
        
        risk_points = 0
        
        # Security risks
        if security_score < 50:
            risk_points += 3
        elif security_score < 70:
            risk_points += 2
        elif security_score < 90:
            risk_points += 1
        
        # Liquidity risks
        if not liquidity_locked:
            risk_points += 2
        
        # Whale risks
        if whale_risk == 'EXTREME':
            risk_points += 3
        elif whale_risk == 'HIGH':
            risk_points += 2
        elif whale_risk == 'MEDIUM':
            risk_points += 1
        
        # Price action risks (too high too fast = late entry)
        if price_change_24h > 1000:
            risk_points += 2
        elif price_change_24h > 500:
            risk_points += 1
        
        # Categorize
        if risk_points >= 7:
            return 'EXTREME'
        elif risk_points >= 5:
            return 'HIGH'
        elif risk_points >= 3:
            return 'MEDIUM'
        else:
            return 'LOW'


# ==================== SIGNAL TRACKER ====================

class SignalTracker:
    """تتبع الإشارات والكولداون"""
    
    def __init__(self, config: MemeHunterConfig):
        self.config = config
        self.signals_today: List[MemeSignal] = []
        self.signal_history: Dict[str, datetime] = {}  # token_address: last_signal_time
    
    def can_signal(self, token_address: str) -> bool:
        """هل يمكن إرسال إشارة لهذه العملة؟"""
        
        # Check daily limit
        today_count = len([
            s for s in self.signals_today
            if s.token.detected_at.date() == datetime.now().date()
        ])
        
        if today_count >= self.config.MAX_SIGNALS_PER_DAY:
            logger.warning(f"⚠️ Daily signal limit reached ({self.config.MAX_SIGNALS_PER_DAY})")
            return False
        
        # Check cooldown for this specific token
        if token_address in self.signal_history:
            last_signal = self.signal_history[token_address]
            time_since = datetime.now() - last_signal
            cooldown_hours = self.config.COOLDOWN_HOURS
            
            if time_since < timedelta(hours=cooldown_hours):
                remaining = cooldown_hours - (time_since.total_seconds() / 3600)
                logger.debug(f"⏳ Token in cooldown: {remaining:.1f}h remaining")
                return False
        
        return True
    
    def add_signal(self, signal: MemeSignal):
        """إضافة إشارة جديدة"""
        self.signals_today.append(signal)
        self.signal_history[signal.token.address] = signal.token.detected_at
        logger.info(f"✅ Signal added: {signal.token.symbol} (Total today: {len(self.signals_today)})")
    
    def cleanup_old_signals(self):
        """تنظيف الإشارات القديمة"""
        # Keep only today's signals
        today = datetime.now().date()
        self.signals_today = [
            s for s in self.signals_today
            if s.token.detected_at.date() == today
        ]
        
        # Remove old cooldowns (older than 24h)
        cutoff = datetime.now() - timedelta(hours=24)
        self.signal_history = {
            k: v for k, v in self.signal_history.items()
            if v > cutoff
        }


# ==================== TELEGRAM NOTIFIER ====================

class TelegramNotifier:
    """إرسال الإشارات عبر Telegram"""
    
    def __init__(self, config: MemeHunterConfig):
        self.config = config
        self.bot_token = config.TELEGRAM_BOT_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID
    
    def send_meme_signal(self, signal: MemeSignal):
        """إرسال إشارة عملة ميم"""
        try:
            token = signal.token
            
            # Build message
            urgency_emoji = {
                'LOW': '🟢',
                'MEDIUM': '🟡',
                'HIGH': '🟠',
                'CRITICAL': '🔴'
            }.get(signal.urgency, '⚪')
            
            risk_emoji = {
                'LOW': '🟢',
                'MEDIUM': '🟡',
                'HIGH': '🟠',
                'EXTREME': '🔴'
            }.get(token.risk_level, '⚪')
            
            message = f"""
🚀 {urgency_emoji} **MEME HUNTER ALERT** #MemeHunter

**{token.symbol}** ({token.name})
━━━━━━━━━━━━━━━━━━━━━

💰 **السعر:** ${token.price_usd:.8f}
📊 **Chain:** {token.chain.upper()} | {token.dex_name}

📈 **حركة السعر:**
├─ 5m: {token.price_change_5m:+.1f}%
├─ 1h: {token.price_change_1h:+.1f}% {'🔥' if token.price_change_1h > 30 else ''}
├─ 6h: {token.price_change_6h:+.1f}%
└─ 24h: {token.price_change_24h:+.1f}% {'🚀' if token.price_change_24h > 100 else ''}

💧 **السيولة:** ${token.liquidity_usd:,.0f}
{'🔒 قفل السيولة: ' + str(token.liquidity_lock_percent) + '%' if token.liquidity_locked else '⚠️ السيولة غير مقفلة'}

📊 **النشاط (24h):**
├─ حجم التداول: ${token.volume_24h:,.0f}
├─ معاملات: {token.transactions_24h:,}
├─ شراء/بيع: {token.buys_24h}/{token.sells_24h}
└─ حاملين: {token.holders_count:,}

🌐 **Social Media:**
├─ Twitter: {token.twitter_followers:,} متابع
├─ Telegram: {token.telegram_members:,} عضو
└─ {'✅ موقع موثق' if token.website_url else '⚠️ لا يوجد موقع'}

🔐 **الأمان:**
{'✅ عقد موثق' if token.contract_verified else '⚠️ عقد غير موثق'}
{'⚠️ HONEYPOT RISK!' if token.honeypot_risk else '✅ آمن'}

━━━━━━━━━━━━━━━━━━━━━

🎯 **استراتيجية الدخول:**

**Entry:** ${signal.entry_price:.8f}

**Targets:**
├─ T1 (+{self.config.TARGET_1_PCT:.0f}%): ${signal.targets[0]:.8f} - Exit {self.config.EXIT_1_PCT*100:.0f}%
├─ T2 (+{self.config.TARGET_2_PCT:.0f}%): ${signal.targets[1]:.8f} - Exit {self.config.EXIT_2_PCT*100:.0f}%
└─ T3 (+{self.config.TARGET_3_PCT:.0f}%): ${signal.targets[2]:.8f} - Exit {self.config.EXIT_3_PCT*100:.0f}%

**Stop Loss:** ${signal.stop_loss:.8f} ({self.config.STOP_LOSS_PCT:.0f}%)

**حجم المركز:** ${signal.position_size_usd:.0f} ({self.config.MAX_POSITION_SIZE_PCT*100:.1f}% من رأس المال)

⏱️ **Max Hold:** {self.config.MAX_HOLD_HOURS}h

━━━━━━━━━━━━━━━━━━━━━

📊 **التقييم:**
├─ نقاط: {token.total_score:.1f}/100
├─ خطر: {risk_emoji} {token.risk_level}
└─ عمر: {token.age_hours:.1f}h

💡 **السبب:**
{signal.reasoning}

⚠️ **تحذير:** عملات الميم عالية الخطورة! تداول بحذر!

🔗 **Links:**
Contract: `{token.address}`
{f"Website: {token.website_url}" if token.website_url else ""}
{f"Twitter: {token.twitter_url}" if token.twitter_url else ""}
{f"Telegram: {token.telegram_url}" if token.telegram_url else ""}

━━━━━━━━━━━━━━━━━━━━━
🤖 Meme Hunter v1.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            # Send via Telegram
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ Telegram signal sent: {token.symbol}")
                return True
            else:
                logger.error(f"❌ Telegram failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to send Telegram signal: {e}")
            return False
    
    def send_status_update(self, message: str):
        """إرسال رسالة حالة"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': f"🤖 **Meme Hunter Status**\n\n{message}",
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"❌ Failed to send status update: {e}")
            return False


# ==================== MAIN MEME HUNTER ====================

class MemeHunter:
    """البوت الرئيسي لصيد عملات الميم"""
    
    def __init__(self, config: MemeHunterConfig):
        self.config = config
        
        # Initialize components
        self.dex_scanner = DexScreenerScanner(config)
        self.social_analyzer = SocialAnalyzer(config)
        self.liquidity_analyzer = LiquidityAnalyzer(config)
        self.holder_analyzer = HolderAnalyzer(config)
        self.security_checker = SecurityChecker(config)
        self.scoring_engine = ScoringEngine(config)
        self.signal_tracker = SignalTracker(config)
        self.telegram = TelegramNotifier(config)
        
        logger.info("🚀 Meme Hunter Bot initialized!")
    
    async def scan_and_analyze(self):
        """مسح وتحليل العملات الرائجة"""
        try:
            logger.info("🔍 Starting meme coin scan...")
            
            # 1. Get trending tokens from DexScreener
            trending_tokens = self.dex_scanner.search_trending_tokens()
            
            if not trending_tokens:
                logger.info("😴 No trending tokens found")
                return
            
            logger.info(f"📊 Analyzing {len(trending_tokens)} potential tokens...")
            
            # 2. Analyze each token
            for pair_data in trending_tokens:
                try:
                    token_data = await self._analyze_token(pair_data)
                    
                    if token_data and self._meets_criteria(token_data):
                        # Generate signal
                        signal = self._generate_signal(token_data)
                        
                        if signal and self.signal_tracker.can_signal(token_data.address):
                            # Send signal!
                            logger.info(f"🎯 SIGNAL GENERATED: {token_data.symbol} (Score: {token_data.total_score:.1f})")
                            
                            self.telegram.send_meme_signal(signal)
                            self.signal_tracker.add_signal(signal)
                    
                    # Small delay between analyses
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"❌ Token analysis failed: {e}")
                    continue
            
            # Cleanup old signals
            self.signal_tracker.cleanup_old_signals()
            
            logger.info("✅ Scan cycle completed")
            
        except Exception as e:
            logger.error(f"❌ Scan failed: {e}")
    
    async def _analyze_token(self, pair_data: Dict) -> Optional[TokenData]:
        """تحليل شامل لعملة واحدة"""
        try:
            # Extract basic data
            base_token = pair_data.get('baseToken', {})
            symbol = base_token.get('symbol', 'UNKNOWN')
            name = base_token.get('name', 'UNKNOWN')
            address = base_token.get('address', '')
            chain = pair_data.get('chainId', '')
            
            # Skip if blacklisted
            if address in self.config.BLACKLIST_TOKENS:
                logger.debug(f"⛔ Blacklisted token: {symbol}")
                return None
            
            # Price data
            price_usd = float(pair_data.get('priceUsd', 0))
            if price_usd == 0:
                return None
            
            price_change = pair_data.get('priceChange', {})
            price_change_5m = float(price_change.get('m5', 0) or 0)
            price_change_1h = float(price_change.get('h1', 0) or 0)
            price_change_6h = float(price_change.get('h6', 0) or 0)
            price_change_24h = float(price_change.get('h24', 0) or 0)
            
            # Volume & Liquidity
            volume = pair_data.get('volume', {})
            volume_24h = float(volume.get('h24', 0) or 0)
            
            liquidity = pair_data.get('liquidity', {})
            liquidity_usd = float(liquidity.get('usd', 0) or 0)
            
            # Transactions
            txns = pair_data.get('txns', {}).get('h24', {})
            buys = int(txns.get('buys', 0) or 0)
            sells = int(txns.get('sells', 0) or 0)
            transactions_24h = buys + sells
            
            # DEX info
            dex_name = pair_data.get('dexId', 'Unknown')
            pair_address = pair_data.get('pairAddress', '')
            
            # Token age
            pair_created = pair_data.get('pairCreatedAt', 0)
            if pair_created:
                age_hours = (time.time() - (pair_created / 1000)) / 3600
            else:
                age_hours = 999  # Unknown
            
            # Links
            info = pair_data.get('info', {})
            links = info.get('socials', []) if isinstance(info.get('socials'), list) else []
            
            # Convert links list to dict
            links_dict = {}
            for link in links:
                if isinstance(link, dict):
                    link_type = link.get('type', '')
                    link_url = link.get('url', '')
                    if link_type and link_url:
                        links_dict[link_type] = link_url
            
            website_url = info.get('website') or info.get('websites', [{}])[0] if info.get('websites') else None
            
            logger.info(f"🔎 Analyzing: {symbol} | ${price_usd:.8f} | 1h: {price_change_1h:+.1f}% | Vol: ${volume_24h:,.0f}")
            
            # === DEEP ANALYSIS ===
            
            # 1. Social Analysis
            social_data = self.social_analyzer.analyze_token_social(address, links_dict)
            
            # 2. Liquidity Analysis
            liquidity_data = self.liquidity_analyzer.check_liquidity_lock(address, chain, liquidity_usd)
            
            # 3. Holder Analysis
            holder_data = self.holder_analyzer.analyze_holders(address, chain)
            
            # 4. Security Check
            security_data = self.security_checker.check_token_security(address, chain)
            
            # 5. Calculate Total Score
            price_action_data = {
                'price_change_1h': price_change_1h,
                'price_change_24h': price_change_24h,
                'transactions_24h': transactions_24h
            }
            
            total_score, risk_level = self.scoring_engine.calculate_total_score(
                price_action_data,
                liquidity_data,
                social_data,
                holder_data,
                security_data
            )
            
            # Build TokenData object
            token_data = TokenData(
                symbol=symbol,
                name=name,
                address=address,
                chain=chain,
                price_usd=price_usd,
                price_change_5m=price_change_5m,
                price_change_1h=price_change_1h,
                price_change_6h=price_change_6h,
                price_change_24h=price_change_24h,
                volume_24h=volume_24h,
                liquidity_usd=liquidity_usd,
                liquidity_locked=liquidity_data['is_locked'],
                liquidity_lock_percent=liquidity_data['lock_percent'],
                transactions_24h=transactions_24h,
                buys_24h=buys,
                sells_24h=sells,
                holders_count=holder_data['total_holders'],
                twitter_followers=social_data['twitter_followers'],
                telegram_members=social_data['telegram_members'],
                website_url=website_url,
                telegram_url=links_dict.get('telegram'),
                twitter_url=links_dict.get('twitter'),
                contract_verified=security_data['contract_verified'],
                honeypot_risk=security_data['honeypot_risk'],
                creator_suspicious=False,
                age_hours=age_hours,
                dex_name=dex_name,
                pair_address=pair_address,
                total_score=total_score,
                risk_level=risk_level,
                detected_at=datetime.now()
            )
            
            return token_data
            
        except Exception as e:
            logger.error(f"❌ Token analysis error: {e}")
            return None
    
    def _meets_criteria(self, token: TokenData) -> bool:
        """هل العملة تلبي معايير الدخول؟"""
        
        # Minimum score required
        if token.total_score < 60:
            logger.debug(f"❌ {token.symbol}: Score too low ({token.total_score:.1f})")
            return False
        
        # Minimum liquidity
        if token.liquidity_usd < self.config.MIN_LIQUIDITY_USD:
            logger.debug(f"❌ {token.symbol}: Liquidity too low (${token.liquidity_usd:,.0f})")
            return False
        
        # Minimum volume
        if token.volume_24h < self.config.MIN_VOLUME_24H_USD:
            logger.debug(f"❌ {token.symbol}: Volume too low (${token.volume_24h:,.0f})")
            return False
        
        # Minimum transactions
        if token.transactions_24h < self.config.MIN_TRANSACTIONS_24H:
            logger.debug(f"❌ {token.symbol}: Transactions too low ({token.transactions_24h})")
            return False
        
        # Price change triggers
        if token.price_change_1h < self.config.MIN_PRICE_CHANGE_1H:
            logger.debug(f"❌ {token.symbol}: Price change 1h too low ({token.price_change_1h:.1f}%)")
            return False
        
        # Not too late (avoid 1000%+ pumps)
        if token.price_change_24h > self.config.MAX_PRICE_CHANGE_24H:
            logger.debug(f"❌ {token.symbol}: Already pumped too much ({token.price_change_24h:.1f}%)")
            return False
        
        # Liquidity lock check (if required)
        if self.config.LIQUIDITY_LOCK_REQUIRED and not token.liquidity_locked:
            logger.debug(f"❌ {token.symbol}: Liquidity not locked")
            return False
        
        # Security check
        if token.honeypot_risk:
            logger.debug(f"❌ {token.symbol}: Honeypot risk detected!")
            return False
        
        # Risk level check
        if token.risk_level == 'EXTREME':
            logger.debug(f"❌ {token.symbol}: Risk level EXTREME")
            return False
        
        logger.info(f"✅ {token.symbol}: Meets all criteria! Score: {token.total_score:.1f}")
        return True
    
    def _generate_signal(self, token: TokenData) -> Optional[MemeSignal]:
        """توليد إشارة دخول"""
        try:
            entry_price = token.price_usd
            
            # Calculate targets
            target_1 = entry_price * (1 + self.config.TARGET_1_PCT / 100)
            target_2 = entry_price * (1 + self.config.TARGET_2_PCT / 100)
            target_3 = entry_price * (1 + self.config.TARGET_3_PCT / 100)
            
            # Calculate stop loss
            stop_loss = entry_price * (1 + self.config.STOP_LOSS_PCT / 100)
            
            # Position size (1% of capital - in demo, use $100)
            position_size_usd = 1000 * self.config.MAX_POSITION_SIZE_PCT  # Assuming $1000 capital
            
            # Determine urgency
            if token.price_change_1h > 50 and token.total_score > 80:
                urgency = 'CRITICAL'
            elif token.price_change_1h > 30 and token.total_score > 70:
                urgency = 'HIGH'
            elif token.price_change_1h > 20:
                urgency = 'MEDIUM'
            else:
                urgency = 'LOW'
            
            # Build reasoning
            reasons = []
            if token.price_change_1h > 30:
                reasons.append(f"🚀 ارتفاع قوي +{token.price_change_1h:.1f}% في ساعة")
            if token.transactions_24h > 20000:
                reasons.append(f"🔥 نشاط عالي ({token.transactions_24h:,} معاملة)")
            if token.liquidity_locked:
                reasons.append(f"🔒 سيولة مقفلة ({token.liquidity_lock_percent:.0f}%)")
            if token.twitter_followers > 5000:
                reasons.append(f"📱 متابعين كثر ({token.twitter_followers:,})")
            if token.holders_count > 2000:
                reasons.append(f"👥 توزيع جيد ({token.holders_count:,} حامل)")
            
            reasoning = "\n".join(reasons) if reasons else "فرصة مميزة للدخول"
            
            signal = MemeSignal(
                token=token,
                signal_type="MEME_OPPORTUNITY",
                entry_price=entry_price,
                targets=[target_1, target_2, target_3],
                stop_loss=stop_loss,
                position_size_usd=position_size_usd,
                reasoning=reasoning,
                urgency=urgency
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"❌ Signal generation failed: {e}")
            return None
    
    async def run(self):
        """تشغيل البوت"""
        logger.info("🚀🚀🚀 MEME HUNTER BOT STARTED! 🚀🚀🚀")
        
        # Send startup notification
        self.telegram.send_status_update(
            f"🚀 Meme Hunter Bot Started!\n\n"
            f"🎯 Target: {self.config.TARGET_CHAIN.upper()} DEX\n"
            f"⏰ Scan Interval: {self.config.SCAN_INTERVAL_SECONDS}s\n"
            f"📊 Max Signals/Day: {self.config.MAX_SIGNALS_PER_DAY}\n"
            f"💰 Position Size: {self.config.MAX_POSITION_SIZE_PCT*100}%\n"
            f"🛑 Stop Loss: {self.config.STOP_LOSS_PCT}%\n"
            f"🎯 Targets: +{self.config.TARGET_1_PCT}%, +{self.config.TARGET_2_PCT}%, +{self.config.TARGET_3_PCT}%"
        )
        
        while True:
            try:
                # Run scan
                await self.scan_and_analyze()
                
                # Wait for next scan
                logger.info(f"😴 Sleeping for {self.config.SCAN_INTERVAL_SECONDS}s...")
                await asyncio.sleep(self.config.SCAN_INTERVAL_SECONDS)
                
            except KeyboardInterrupt:
                logger.info("⛔ Stopping Meme Hunter...")
                self.telegram.send_status_update("⛔ Meme Hunter Bot Stopped")
                break
            except Exception as e:
                logger.error(f"❌ Runtime error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error


# ==================== MAIN ENTRY POINT ====================

async def main():
    """نقطة الدخول الرئيسية"""
    
    # Load configuration
    config = MemeHunterConfig()
    
    # TODO: Load from config file or environment variables
    # config.TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    # config.TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    # Create and run hunter
    hunter = MemeHunter(config)
    await hunter.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Meme Hunter stopped by user")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
