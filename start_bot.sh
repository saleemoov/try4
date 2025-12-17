#!/bin/bash

# 🚀 START TRADING BOT - شغّل البوت الآن
# تشغيل بوت التداول المتقدم

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║     🚀 Advanced OKX Trading Bot - Starting Up              ║"
echo "║     بوت التداول المتقدم - جاري التشغيل                    ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# التحقق من الملفات المطلوبة
echo "✅ التحقق من المتطلبات..."
echo ""

if [ ! -f "trading_config.json" ]; then
    echo "❌ ملف الإعدادات غير موجود!"
    echo "اشغل: python quick_setup.py"
    exit 1
fi

if [ ! -f "advanced_trading_bot.py" ]; then
    echo "❌ ملف البوت غير موجود!"
    exit 1
fi

echo "✅ جميع الملفات موجودة"
echo ""

# عرض معلومات الإعدادات
echo "📋 معلومات الإعدادات:"
echo "───────────────────────────────────────────────────────────"
python3 -c "
import json
with open('trading_config.json', 'r') as f:
    config = json.load(f)
    print(f'✓ Telegram Chat ID: {config[\"telegram\"][\"chat_id\"]}')
    print(f'✓ Risk Level: {config[\"trading\"][\"risk_level\"]}')
    print(f'✓ Check Interval: {config[\"advanced\"][\"check_interval\"]}s')
    print(f'✓ Max Coins: {config[\"advanced\"][\"max_coins\"]}')
"
echo "───────────────────────────────────────────────────────────"
echo ""

# شغّل البوت
echo "🚀 شغّل البوت..."
echo ""

python3 advanced_trading_bot.py

echo ""
echo "⏹️  تم إيقاف البوت"
