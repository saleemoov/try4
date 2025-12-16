#!/bin/bash

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 💀 Crypto Killer - تحديث ذكي (يكتشف المسار تلقائياً)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💀 تحديث Crypto Killer Bot (ذكي)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. اكتشاف مسار البوت
echo "1️⃣ البحث عن البوت..."
BOT_PATH=$(find /root -name "crypto_killer_bot.py" 2>/dev/null | head -1)

if [ -z "$BOT_PATH" ]; then
    echo "❌ لم يتم العثور على crypto_killer_bot.py"
    echo "📥 سيتم تنزيله في /root..."
    BOT_DIR="/root"
else
    BOT_DIR=$(dirname "$BOT_PATH")
    echo "✅ عثرنا على البوت في: $BOT_DIR"
fi

echo ""

# 2. تحديث الكود
echo "2️⃣ تحديث الكود..."
cd "$BOT_DIR"

# محاولة git pull أولاً
if [ -d .git ]; then
    echo "   استخدام git pull..."
    git pull origin main 2>/dev/null || {
        echo "   ⚠️  git pull فشل، سنستخدم التنزيل المباشر..."
        curl -sL https://raw.githubusercontent.com/saleemoov/try4/main/crypto_killer_bot.py -o crypto_killer_bot.py
    }
else
    echo "   التنزيل المباشر..."
    curl -sL https://raw.githubusercontent.com/saleemoov/try4/main/crypto_killer_bot.py -o crypto_killer_bot.py
fi

echo "   ✅ الكود محدّث!"
echo ""

# 3. إعادة التشغيل
echo "3️⃣ إعادة تشغيل البوت..."
systemctl restart crypto-killer
sleep 3

# 4. التحقق
echo "4️⃣ حالة البوت:"
systemctl status crypto-killer --no-pager | head -10

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ التحديث مكتمل!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 5. عرض السجل
if [ -f "$BOT_DIR/crypto_killer.log" ]; then
    echo "📊 آخر 15 سطر من السجل:"
    tail -15 "$BOT_DIR/crypto_killer.log"
elif [ -f /root/crypto_killer/crypto_killer.log ]; then
    echo "📊 آخر 15 سطر من السجل:"
    tail -15 /root/crypto_killer/crypto_killer.log
fi

echo ""
echo "💀 الإعدادات الجديدة:"
echo "   MIN_SCORE: 180 (بدلاً من 250)"
echo "   HIGH: 230 (بدلاً من 280)"
echo "   EXTREME: 280 (بدلاً من 320)"
echo ""
echo "🎯 توقع إشارات خلال 2-6 ساعات!"
