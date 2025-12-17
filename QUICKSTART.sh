#!/bin/bash

# 🚀 QUICK START GUIDE
# دليل البدء السريع

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   🚀 Advanced OKX Trading Bot - Quick Start                ║"
echo "║   بوت التداول المتقدم - دليل البدء السريع               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check Python
echo "📋 فحص المتطلبات..."
echo ""

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 غير مثبت"
    echo "يرجى تثبيت Python 3.8+ من https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION موجود"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo "⚠️ pip غير موجود، محاولة تثبيت..."
    python3 -m ensurepip --default-pip
fi

echo ""
echo "📦 تثبيت المكتبات المطلوبة..."
echo ""

pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ فشل تثبيت المكتبات"
    exit 1
fi

echo ""
echo "✅ تم تثبيت جميع المكتبات بنجاح"
echo ""

# Run tests
echo "🧪 تشغيل الاختبارات..."
echo ""

python3 test_bot.py

if [ $? -ne 0 ]; then
    echo "⚠️ بعض الاختبارات قد تكون فشلت"
    echo "لكن البوت قد يعمل بشكل صحيح"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                 الخطوة التالية                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "اختر واحداً من الخيارات التالية:"
echo ""
echo "1️⃣  إعداد البوت بشكل تفاعلي:"
echo "    python3 setup_wizard.py"
echo ""
echo "2️⃣  قراءة التوثيق الكامل بالعربية:"
echo "    cat DOCUMENTATION_AR.md"
echo ""
echo "3️⃣  قراءة ملخص المشروع:"
echo "    cat PROJECT_SUMMARY_AR.md"
echo ""
echo "4️⃣  تشغيل البوت (بعد الإعداد):"
echo "    python3 advanced_trading_bot.py"
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              معلومات مهمة - Important Notes               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "⚠️  تحذيرات حتمية:"
echo "   • التداول ينطوي على مخاطر عالية"
echo "   • ابدأ برأس مال صغير جداً"
echo "   • استخدم Stop Loss دائماً"
echo "   • نظام Spot فقط - بدون رافعة"
echo ""
echo "✅ نصائح مهمة:"
echo "   • فعّل 2FA على حسابك في OKX"
echo "   • استخدم VPN للأمان الإضافي"
echo "   • راقب السجلات يومياً"
echo "   • سجل نتائجك لقياس الأداء"
echo ""
echo "📞 للمساعدة:"
echo "   • قراءة DOCUMENTATION_AR.md"
echo "   • فحص trading_bot.log للأخطاء"
echo "   • التحقق من الإعدادات في trading_config.json"
echo ""
echo "🚀 نتمنى لك أرباح وفيرة! 💰"
echo ""
