#!/bin/bash

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 💀 Crypto Killer - تحديث سريع
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💀 تحديث Crypto Killer Bot"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. حالة قبل التحديث
echo "1️⃣ الحالة الحالية:"
systemctl status crypto-killer --no-pager | head -5
echo ""

# 2. تحديث الكود
echo "2️⃣ تحديث الكود من GitHub..."
cd /root/crypto_killer
git pull origin main

# 3. إعادة التشغيل
echo "3️⃣ إعادة تشغيل البوت..."
systemctl restart crypto-killer

sleep 3

# 4. التحقق
echo "4️⃣ التحقق من الحالة الجديدة:"
systemctl status crypto-killer --no-pager | head -10

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ التحديث مكتمل!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 آخر 10 أسطر من السجل:"
tail -10 /root/crypto_killer/crypto_killer.log
echo ""
echo "💀 البوت محدّث وجاهز!"
