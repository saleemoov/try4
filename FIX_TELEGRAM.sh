#!/bin/bash

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 💀 Crypto Killer - تحديث Telegram وإصلاح شامل
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💀 إصلاح Telegram + تحديث كامل"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# بيانات Telegram الجديدة
NEW_BOT_TOKEN="8555966718:AAGPuLjEbDGDcuw5vEbpqG1E1DJdJ6nlCPA"
NEW_CHAT_ID="6557926013"

# 1. البحث عن ملف الإعدادات
echo "1️⃣ البحث عن ملف الإعدادات..."
CONFIG_PATH=$(find /root -name "trading_config.json" 2>/dev/null | head -1)

if [ -z "$CONFIG_PATH" ]; then
    echo "   ⚠️  لم نجد trading_config.json - سننشئه!"
    CONFIG_PATH="/root/crypto_killer/trading_config.json"
    mkdir -p /root/crypto_killer
fi

echo "   ✅ سنستخدم: $CONFIG_PATH"
echo ""

# 2. إنشاء ملف الإعدادات الجديد
echo "2️⃣ تحديث ملف الإعدادات..."
cat > "$CONFIG_PATH" << 'EOFCONFIG'
{
  "okx": {
    "api_key": "ae76e464-ceb1-41bb-a844-3472b1e44ddd",
    "api_secret": "96F1BADF796EE78293B8A0837AFABDD8",
    "passphrase": "Saleem@90"
  },
  "telegram": {
    "bot_token": "8555966718:AAGPuLjEbDGDcuw5vEbpqG1E1DJdJ6nlCPA",
    "chat_id": "6557926013"
  }
}
EOFCONFIG

echo "   ✅ ملف الإعدادات محدّث!"
echo ""

# 3. التأكد من وجود البوت
echo "3️⃣ التحقق من ملف البوت..."
BOT_FILE=$(find /root -name "crypto_killer_bot.py" 2>/dev/null | head -1)

if [ -z "$BOT_FILE" ]; then
    echo "   ⚠️  لم نجد البوت - سننزله!"
    cd $(dirname "$CONFIG_PATH")
    curl -sL https://raw.githubusercontent.com/saleemoov/try4/main/crypto_killer_bot.py -o crypto_killer_bot.py
    BOT_FILE="$(dirname "$CONFIG_PATH")/crypto_killer_bot.py"
fi

echo "   ✅ البوت موجود في: $BOT_FILE"
echo ""

# 4. تحديث systemd service
echo "4️⃣ تحديث خدمة systemd..."
BOT_DIR=$(dirname "$BOT_FILE")

cat > /etc/systemd/system/crypto-killer.service << EOFSVC
[Unit]
Description=Crypto Killer Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$BOT_DIR
ExecStart=/usr/bin/python3 -u $BOT_FILE
Restart=always
RestartSec=10
StandardOutput=append:$BOT_DIR/crypto_killer.log
StandardError=append:$BOT_DIR/crypto_killer.log

[Install]
WantedBy=multi-user.target
EOFSVC

echo "   ✅ الخدمة محدّثة!"
echo ""

# 5. إعادة تشغيل البوت
echo "5️⃣ إعادة تشغيل البوت..."
systemctl daemon-reload
systemctl restart crypto-killer
sleep 3

# 6. التحقق من الحالة
echo "6️⃣ حالة البوت:"
systemctl status crypto-killer --no-pager | head -10
echo ""

# 7. اختبار Telegram
echo "7️⃣ اختبار إشعارات Telegram..."
RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot$NEW_BOT_TOKEN/sendMessage" \
-H "Content-Type: application/json" \
-d "{\"chat_id\":\"$NEW_CHAT_ID\",\"text\":\"✅ نجح التحديث!\\n\\n💀 Crypto Killer Bot جاهز!\\nMIN_SCORE: 180\\n\\nانتظر الإشارات خلال ساعات...\"}")

if echo "$RESPONSE" | grep -q '"ok":true'; then
    echo "   ✅ إشعار Telegram مُرسل بنجاح!"
    echo "   📱 تحقق من تليجرام الآن!"
else
    echo "   ⚠️  فشل الإرسال. الرد:"
    echo "$RESPONSE"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ التحديث مكتمل 100%!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 آخر 10 أسطر من السجل:"
tail -10 "$BOT_DIR/crypto_killer.log" 2>/dev/null || echo "   (السجل فارغ - البوت بدأ لتوه)"
echo ""
echo "💀 الإعدادات النشطة:"
echo "   MIN_SCORE: 180 (45% من الحد الأقصى)"
echo "   Bot Token: محدّث ✅"
echo "   Chat ID: 6557926013 ✅"
echo ""
echo "🎯 توقع إشارات خلال 2-6 ساعات!"
echo ""
echo "📱 للمراقبة المباشرة:"
echo "   tail -f $BOT_DIR/crypto_killer.log"
