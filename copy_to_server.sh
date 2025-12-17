#!/bin/bash

# اطلب IP من المستخدم
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💀 نسخ Crypto Killer إلى DigitalOcean"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "🌐 أدخل IP السيرفر: " SERVER_IP

if [ -z "$SERVER_IP" ]; then
    echo "❌ IP مطلوب!"
    exit 1
fi

echo ""
echo "📝 أدخل بيانات الاتصال (ستُحفظ في السيرفر):"
echo ""
read -p "🔑 OKX API Key: " OKX_KEY
read -p "🔐 OKX Secret: " OKX_SECRET
read -p "🔒 OKX Passphrase: " OKX_PASS
echo ""
read -p "🤖 Telegram Bot Token: " TG_TOKEN
read -p "💬 Telegram Chat ID: " TG_CHAT

echo ""
echo "🚀 جاري النسخ والتثبيت..."
echo ""

# إنشاء trading_config.json محلياً
cat > /tmp/trading_config.json << EOF
{
  "okx": {
    "api_key": "$OKX_KEY",
    "api_secret": "$OKX_SECRET",
    "passphrase": "$OKX_PASS"
  },
  "telegram": {
    "bot_token": "$TG_TOKEN",
    "chat_id": "$TG_CHAT"
  }
}
EOF

# نسخ الملفات
echo "1️⃣ نسخ ملفات البوت..."
ssh root@$SERVER_IP "mkdir -p /root/crypto_killer"
scp crypto_killer_bot.py root@$SERVER_IP:/root/crypto_killer/
scp /tmp/trading_config.json root@$SERVER_IP:/root/crypto_killer/

# تثبيت وتشغيل
echo "2️⃣ تثبيت المكتبات..."
ssh root@$SERVER_IP << 'ENDSSH'
cd /root/crypto_killer
pip3 install -q ccxt pandas numpy requests python-dotenv

# إنشاء systemd service
cat > /etc/systemd/system/crypto-killer.service << 'EOFSERVICE'
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
EOFSERVICE

# تفعيل وتشغيل
systemctl daemon-reload
systemctl enable crypto-killer
systemctl restart crypto-killer

sleep 3
systemctl status crypto-killer --no-pager
ENDSSH

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ تم! البوت يعمل الآن على $SERVER_IP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 لمراقبة السجل:"
echo "   ssh root@$SERVER_IP 'tail -f /root/crypto_killer/crypto_killer.log'"
echo ""

rm /tmp/trading_config.json
