#!/bin/bash

SERVER_IP="134.209.244.180"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💀 Crypto Killer - نشر تلقائي كامل"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 السيرفر: $SERVER_IP"
echo ""

# نسخ الملفات
echo "1️⃣ نسخ الملفات إلى السيرفر..."
ssh root@$SERVER_IP "rm -rf /root/crypto_killer && mkdir -p /root/crypto_killer"
scp crypto_killer_bot.py root@$SERVER_IP:/root/crypto_killer/
scp trading_config_ready.json root@$SERVER_IP:/root/crypto_killer/trading_config.json

# التثبيت والتشغيل
echo ""
echo "2️⃣ تثبيت المكتبات وتشغيل البوت..."
ssh root@$SERVER_IP << 'REMOTE_COMMANDS'
cd /root/crypto_killer

# تثبيت المكتبات
pip3 install -q ccxt pandas numpy requests python-dotenv

# اختبار سريع
echo "3️⃣ اختبار البوت..."
timeout 5 python3 crypto_killer_bot.py || true

# إنشاء systemd service
echo "4️⃣ إنشاء خدمة التشغيل الدائم..."
cat > /etc/systemd/system/crypto-killer.service << 'SERVICE'
[Unit]
Description=Crypto Killer Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/crypto_killer
ExecStart=/usr/bin/python3 -u /root/crypto_killer/crypto_killer_bot.py
Restart=always
RestartSec=10
StandardOutput=append:/root/crypto_killer/crypto_killer.log
StandardError=append:/root/crypto_killer/crypto_killer.log

[Install]
WantedBy=multi-user.target
SERVICE

# تفعيل وتشغيل
systemctl daemon-reload
systemctl enable crypto-killer
systemctl restart crypto-killer

sleep 3

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ التثبيت مكتمل!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

systemctl status crypto-killer --no-pager

echo ""
echo "📊 لمراقبة السجل:"
echo "   tail -f /root/crypto_killer/crypto_killer.log"
echo ""
REMOTE_COMMANDS

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 تم! البوت يعمل الآن 24/7"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
