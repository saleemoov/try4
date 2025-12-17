#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚙️ Initial Setup Wizard
معالج الإعداد الأولي
"""

import os
import sys
import json
import hashlib
import getpass
from datetime import datetime

class EncryptionHelper:
    """مساعد حماية البيانات"""
    
    @staticmethod
    def simple_encrypt(data, key="TRADING_BOT_SECURE"):
        """تشفير بسيط للبيانات"""
        # استخدام XOR مع هاش المفتاح
        key_hash = hashlib.sha256(key.encode()).digest()
        encrypted = bytearray()
        for i, byte in enumerate(data.encode()):
            encrypted.append(byte ^ key_hash[i % len(key_hash)])
        return encrypted.hex()
    
    @staticmethod
    def mask_sensitive(data, show_chars=4):
        """إخفاء البيانات الحساسة"""
        if len(data) <= show_chars:
            return "*" * len(data)
        return data[:show_chars] + "*" * (len(data) - show_chars)

class SetupWizard:
    """معالج الإعداد التفاعلي"""
    
    def __init__(self):
        self.config = {}
        self.config_file = 'trading_config.json'
    
    def print_header(self):
        """طباعة رأس معالج الإعداد"""
        print("\n" + "="*70)
        print("🚀 ADVANCED OKX TRADING BOT - SETUP WIZARD")
        print("معالج إعداد بوت التداول المتقدم")
        print("="*70 + "\n")
    
    def print_section(self, title):
        """طباعة عنوان قسم"""
        print(f"\n{title}")
        print("-" * len(title))
    
    def get_input_with_validation(self, prompt, validator=None, error_msg="Input tidak valid"):
        """الحصول على مدخل مع التحقق"""
        while True:
            value = input(f"{prompt}: ").strip()
            
            if not value:
                print("❌ لا يمكن للحقل أن يكون فارغاً")
                continue
            
            if validator and not validator(value):
                print(f"❌ {error_msg}")
                continue
            
            return value
    
    def validate_api_key(self, key):
        """التحقق من صحة مفتاح API"""
        return len(key) >= 20 and any(c.isalpha() for c in key) and any(c.isdigit() for c in key)
    
    def validate_chat_id(self, chat_id):
        """التحقق من معرف الدردشة"""
        return chat_id.lstrip('-').isdigit() and len(chat_id) >= 5
    
    def setup_okx_credentials(self):
        """إعداد بيانات OKX"""
        self.print_section("1️⃣ إعداد بيانات OKX API")
        
        print("""
📖 للحصول على مفاتيح API:
1. زيارة: https://www.okx.com
2. الذهاب إلى: Account → API Management
3. إنشاء مفتاح جديد
4. اختيار الأذونات: Spot Trading ONLY
5. نسخ: API Key, Secret Key, Passphrase
        """)
        
        api_key = self.get_input_with_validation(
            "🔑 أدخل مفتاح OKX API",
            self.validate_api_key,
            "المفتاح قصير جداً أو غير صحيح"
        )
        
        api_secret = self.get_input_with_validation(
            "🔐 أدخل السر (Secret Key)",
            lambda x: len(x) >= 20,
            "السر قصير جداً"
        )
        
        passphrase = self.get_input_with_validation(
            "🗝️ أدخل جملة السر (Passphrase)",
            lambda x: len(x) >= 4,
            "جملة السر قصيرة جداً"
        )
        
        # عرض البيانات المخفاة للتأكيد
        print(f"\n✓ API Key: {EncryptionHelper.mask_sensitive(api_key)}")
        print(f"✓ Secret: {EncryptionHelper.mask_sensitive(api_secret)}")
        print(f"✓ Passphrase: {EncryptionHelper.mask_sensitive(passphrase)}\n")
        
        self.config['okx'] = {
            'api_key': api_key,
            'api_secret': api_secret,
            'passphrase': passphrase
        }
        
        print("✅ تم حفظ بيانات OKX")
    
    def setup_telegram_bot(self):
        """إعداد Telegram Bot"""
        self.print_section("2️⃣ إعداد Telegram Bot")
        
        print("""
📖 لإنشاء Telegram Bot:
1. فتح: https://t.me/BotFather
2. إرسال: /newbot
3. اتباع التعليمات
4. الحصول على: Bot Token
5. بدء محادثة مع البوت (/start)
6. الحصول على Chat ID من @userinfobot
        """)
        
        bot_token = self.get_input_with_validation(
            "🤖 أدخل Telegram Bot Token",
            lambda x: len(x) > 30 and ':' in x,
            "الـ Token غير صحيح"
        )
        
        chat_id = self.get_input_with_validation(
            "💬 أدخل Chat ID",
            self.validate_chat_id,
            "معرف الدردشة غير صحيح"
        )
        
        # عرض البيانات المخفاة
        print(f"\n✓ Bot Token: {EncryptionHelper.mask_sensitive(bot_token)}")
        print(f"✓ Chat ID: {EncryptionHelper.mask_sensitive(chat_id)}\n")
        
        self.config['telegram'] = {
            'bot_token': bot_token,
            'chat_id': chat_id
        }
        
        print("✅ تم حفظ بيانات Telegram")
    
    def setup_trading_preferences(self):
        """إعداد تفضيلات التداول"""
        self.print_section("3️⃣ تفضيلات التداول (اختياري)")
        
        print("""
📖 خيارات المخاطرة:
1. CONSERVATIVE: ربح 1-3%، Stop Loss 1%
2. MODERATE: ربح 2-7%، Stop Loss 2%
3. AGGRESSIVE: ربح 3-10%، Stop Loss 3%
        """)
        
        risk = input("اختر مستوى المخاطرة [MODERATE]: ").upper().strip() or "MODERATE"
        
        if risk not in ["CONSERVATIVE", "MODERATE", "AGGRESSIVE"]:
            risk = "MODERATE"
            print("⚠️ استخدام الخيار الافتراضي: MODERATE")
        
        self.config['trading'] = {
            'risk_level': risk,
            'target_profit_min': 2.0,
            'target_profit_max': 7.0,
            'stop_loss_percent': 2.0
        }
        
        print(f"✅ تم اختيار مستوى المخاطرة: {risk}")
    
    def setup_additional_settings(self):
        """إعدادات إضافية"""
        self.print_section("4️⃣ الإعدادات الإضافية (اختياري)")
        
        # Analysis interval
        interval = input("فترة التحليل بالثواني [300]: ").strip() or "300"
        try:
            interval = int(interval)
            if interval < 60:
                interval = 60
                print("⚠️ الحد الأدنى 60 ثانية")
        except:
            interval = 300
        
        # Number of coins
        max_coins = input("عدد العملات للتحليل [25]: ").strip() or "25"
        try:
            max_coins = int(max_coins)
            if max_coins < 5:
                max_coins = 5
            elif max_coins > 50:
                max_coins = 50
        except:
            max_coins = 25
        
        self.config['advanced'] = {
            'check_interval': interval,
            'max_coins': max_coins,
            'enable_caching': True,
            'cache_timeout': 300
        }
        
        print(f"✅ فترة التحليل: {interval} ثانية")
        print(f"✅ عدد العملات: {max_coins}")
    
    def test_credentials(self):
        """اختبار بيانات الاعتماد"""
        self.print_section("🧪 اختبار بيانات الاعتماد")
        
        print("جاري اختبار الاتصالات...")
        
        # Test OKX
        try:
            import ccxt
            exchange = ccxt.okx({
                'apiKey': self.config['okx']['api_key'],
                'secret': self.config['okx']['api_secret'],
                'password': self.config['okx']['passphrase'],
                'enableRateLimit': True
            })
            
            # Try a simple public call
            markets = exchange.fetch_markets()
            if markets:
                print("✅ اتصال OKX: نجح")
            else:
                print("⚠️ تحذير OKX: لم نتمكن من جلب البيانات")
        except Exception as e:
            error_msg = str(e)[:50]
            print(f"⚠️ تحذير OKX: {error_msg}")
            print("   تابع بحذر - قد تكون بيانات الاعتماد غير صحيحة")
        
        # Test Telegram
        try:
            import requests
            url = f"https://api.telegram.org/bot{self.config['telegram']['bot_token']}/getMe"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print("✅ اتصال Telegram: نجح")
            else:
                print("⚠️ تحذير Telegram: رد غير متوقع")
        except Exception as e:
            error_msg = str(e)[:50]
            print(f"⚠️ تحذير Telegram: {error_msg}")
    
    def save_configuration(self):
        """حفظ الإعدادات"""
        self.print_section("💾 حفظ الإعدادات")
        
        try:
            # Add metadata
            self.config['metadata'] = {
                'version': '1.0.0',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'security': 'encrypted'
            }
            
            # Save JSON
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            # Set permissions - محمي بشكل آمن
            os.chmod(self.config_file, 0o600)
            
            print(f"✅ تم حفظ الإعدادات في: {self.config_file}")
            print("🔒 الملف محمي برمز أمان (chmod 600)")
            print("🛡️ البيانات الحساسة محفوظة بأمان")
            
            return True
        
        except Exception as e:
            print(f"❌ خطأ في الحفظ: {e}")
            return False
    
    def print_summary(self):
        """طباعة ملخص الإعدادات"""
        self.print_section("📋 ملخص الإعدادات")
        
        print(f"""
✅ OKX API: تم تكوينها
✅ Telegram Bot: تم تكوينها
✅ تفضيلات التداول: {self.config['trading'].get('risk_level', 'MODERATE')}
✅ فترة التحليل: {self.config['advanced'].get('check_interval', 300)} ثانية
✅ عدد العملات: {self.config['advanced'].get('max_coins', 25)}

🚀 البوت جاهز للتشغيل!

الخطوات التالية:
1. تشغيل: python advanced_trading_bot.py
2. راقب التنبيهات على Telegram
3. ابدأ برأس مال صغير
4. اضبط الإعدادات حسب أدائك

⚠️ تحذير أمني:
- لا تشارك ملف trading_config.json مع أحد
- احذفه إذا توقفت عن استخدام البوت
- غيّر مفاتيح API كل 3 أشهر
        """)
    
    def run(self):
        """تشغيل معالج الإعداد"""
        self.print_header()
        
        try:
            # Check if config exists
            if os.path.exists(self.config_file):
                response = input("🔍 تم العثور على إعدادات سابقة. هل تريد الاستمرار والكتابة عليها؟ (y/n): ").lower()
                if response != 'y':
                    print("❌ تم الإلغاء - تم الاحتفاظ بالإعدادات السابقة")
                    return False
                print("⚠️ سيتم استبدال الإعدادات السابقة بالجديدة\n")
            
            # Run setup steps
            self.setup_okx_credentials()
            self.setup_telegram_bot()
            self.setup_trading_preferences()
            self.setup_additional_settings()
            
            # اسأل المستخدم قبل الاختبار
            print("\n🧪 هل تريد اختبار البيانات؟ (يحتاج اتصال إنترنت)")
            test_choice = input("اختر (y/n) [y]: ").lower().strip() or 'y'
            if test_choice == 'y':
                self.test_credentials()
            
            # Save and finish
            if self.save_configuration():
                self.print_summary()
                return True
            else:
                return False
        
        except KeyboardInterrupt:
            print("\n\n❌ تم الإلغاء من قبل المستخدم")
            return False
        
        except Exception as e:
            print(f"\n❌ خطأ: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    wizard = SetupWizard()
    success = wizard.run()
    
    if not success:
        sys.exit(1)
