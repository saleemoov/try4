#!/bin/bash

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 💀 Crypto Killer - فحص حالة البوت
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💀 فحص حالة Crypto Killer Bot"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. حالة الخدمة
echo "1️⃣ حالة الخدمة:"
systemctl status crypto-killer --no-pager | head -15
echo ""

# 2. آخر 20 سطر من السجل
echo "2️⃣ آخر نشاط (آخر 20 سطر):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
tail -20 /root/crypto_killer/crypto_killer.log
echo ""

# 3. إحصائيات
echo "3️⃣ إحصائيات:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# عدد مرات المسح
SCANS=$(grep -c "Scanning market" /root/crypto_killer/crypto_killer.log 2>/dev/null || echo "0")
echo "   📊 عدد مرات المسح: $SCANS"

# عدد الإشارات المرسلة
SIGNALS=$(grep -c "💀 KILLER SIGNAL" /root/crypto_killer/crypto_killer.log 2>/dev/null || echo "0")
echo "   🎯 إشارات مُرسلة: $SIGNALS"

# عدد الأخطاء
ERRORS=$(grep -c "ERROR" /root/crypto_killer/crypto_killer.log 2>/dev/null || echo "0")
echo "   ⚠️  أخطاء: $ERRORS"

# وقت التشغيل
UPTIME=$(systemctl show crypto-killer -p ActiveEnterTimestamp --value 2>/dev/null)
echo "   ⏰ وقت البدء: $UPTIME"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ الفحص مكتمل!"
echo ""
echo "📱 للمراقبة المباشرة:"
echo "   tail -f /root/crypto_killer/crypto_killer.log"
echo ""
