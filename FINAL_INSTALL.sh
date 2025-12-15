#!/bin/bash

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 💀 Crypto Killer - التثبيت النهائي (3 دقائق)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💀 بدء التثبيت..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. تحديث وتثبيت Python
echo "1️⃣ تثبيت Python..."
apt update -qq && apt install -y python3 python3-pip git >/dev/null 2>&1

# 2. استنساخ المشروع
echo "2️⃣ تنزيل الكود..."
cd /root
rm -rf try4
git clone -q https://github.com/saleemoov/try4.git
cd try4

# 3. إنشاء ملف الإعدادات
echo "3️⃣ إعداد الإعدادات..."
cat > trading_config.json << 'EOFCONFIG'
{
  "okx": {
    "api_key": "ae76e464-ceb1-41bb-a844-3472b1e44ddd",
    "api_secret": "96F1BADF796EE78293B8A0837AFABDD8",
    "passphrase": "Saleem@90"
  },
  "telegram": {
    "bot_token": "961646984:AAE3VnTFDsiwZsM0Tzs6xXjvzAcUv8e0glU",
    "chat_id": "6557926013"
  }
}
EOFCONFIG

# 4. تثبيت المكتبات
echo "4️⃣ تثبيت المكتبات..."
pip3 install -q ccxt pandas numpy requests python-dotenv

# 5. إنشاء systemd service
echo "5️⃣ إنشاء الخدمة..."
cat > /etc/systemd/system/crypto-killer.service << 'EOFSVC'
[Unit]
Description=Crypto Killer Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/try4
ExecStart=/usr/bin/python3 -u /root/try4/crypto_killer_bot.py
Restart=always
RestartSec=10
StandardOutput=append:/root/try4/crypto_killer.log
StandardError=append:/root/try4/crypto_killer.log

[Install]
WantedBy=multi-user.target
EOFSVC

# 6. تشغيل البوت
echo "6️⃣ تشغيل البوت..."
systemctl daemon-reload
systemctl enable crypto-killer
systemctl restart crypto-killer

sleep 3

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ تم التثبيت بنجاح!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# عرض الحالة
if systemctl is-active --quiet crypto-killer; then
    echo "✅ البوت يعمل الآن!"
    systemctl status crypto-killer --no-pager | head -10
else
    echo "⚠️  هناك مشكلة - تحقق من السجل:"
    tail -20 /root/try4/crypto_killer.log
fi

echo ""
echo "📊 أوامر مفيدة:"
echo "   tail -f /root/try4/crypto_killer.log    # مراقبة السجل"
echo "   systemctl status crypto-killer          # حالة البوت"
echo "   systemctl restart crypto-killer         # إعادة التشغيل"
echo ""
echo "💀 Crypto Killer جاهز للصيد!"
