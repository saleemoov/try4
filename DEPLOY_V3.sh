#!/bin/bash

echo "🚀 Deploying Crypto Adaptive Bot v3.0..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

SERVER="root@134.209.244.180"

echo ""
echo "1️⃣ Stopping old bot..."
ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
    # إيقاف جميع البوتات القديمة
    systemctl stop crypto-killer.service 2>/dev/null || true
    pkill -f crypto_killer_bot.py 2>/dev/null || true
    pkill -f advanced_trading_bot.py 2>/dev/null || true
    sleep 2
    echo "✅ Old bots stopped"
EOF

echo ""
echo "2️⃣ Cleaning old files..."
ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
    # حذف الملفات القديمة
    rm -f /root/crypto_killer_bot.py
    rm -f /root/advanced_trading_bot.py
    rm -f /root/crypto_killer.log
    rm -f /root/bot*.log
    echo "✅ Old files removed"
EOF

echo ""
echo "3️⃣ Uploading new bot..."
scp -o StrictHostKeyChecking=no crypto_adaptive_bot.py $SERVER:/root/
scp -o StrictHostKeyChecking=no trading_config.json $SERVER:/root/
echo "✅ Files uploaded"

echo ""
echo "4️⃣ Creating systemd service..."
ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
cat > /etc/systemd/system/adaptive-crypto.service << 'UNIT'
[Unit]
Description=Crypto Adaptive Bot v3.0
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root
ExecStart=/usr/bin/python3 -u /root/crypto_adaptive_bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable adaptive-crypto.service
echo "✅ Service created"
EOF

echo ""
echo "5️⃣ Starting new bot..."
ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
    systemctl start adaptive-crypto.service
    sleep 3
    systemctl status adaptive-crypto.service --no-pager -l
EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Deployment complete!"
echo ""
echo "📊 Check status:"
echo "   ssh root@134.209.244.180 'systemctl status adaptive-crypto.service'"
echo ""
echo "📝 View logs:"
echo "   ssh root@134.209.244.180 'journalctl -u adaptive-crypto.service -f'"
echo ""
echo "🔥 Check signals:"
echo "   ssh root@134.209.244.180 'tail -f /root/adaptive_bot.log'"
