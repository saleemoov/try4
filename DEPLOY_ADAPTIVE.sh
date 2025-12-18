#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
#  🚀 DEPLOY ADAPTIVE BOT v3.0
# ═══════════════════════════════════════════════════════════════════════════

echo "🔥 Deploying Crypto Adaptive Bot v3.0..."

# 1. حذف البوت القديم
echo "🗑️  Removing old bot..."
sudo systemctl stop crypto-killer.service 2>/dev/null
sudo systemctl disable crypto-killer.service 2>/dev/null
rm -f /root/crypto_killer_bot.py
rm -f /root/crypto_killer.log

# 2. رفع البوت الجديد
echo "📤 Uploading new bot..."
scp -o StrictHostKeyChecking=no crypto_adaptive_bot.py root@134.209.244.180:/root/
scp -o StrictHostKeyChecking=no trading_config.json root@134.209.244.180:/root/

# 3. إنشاء systemd service جديد
echo "⚙️  Creating service..."
ssh -o StrictHostKeyChecking=no root@134.209.244.180 << 'ENDSSH'

cat > /etc/systemd/system/crypto-adaptive.service << 'EOF'
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
EOF

# تفعيل وتشغيل
systemctl daemon-reload
systemctl enable crypto-adaptive.service
systemctl start crypto-adaptive.service

echo "✅ Service started!"
systemctl status crypto-adaptive.service --no-pager | head -15

ENDSSH

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Crypto Adaptive Bot v3.0 deployed!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Check logs:"
echo "   ssh root@134.209.244.180 'journalctl -u crypto-adaptive.service -f'"
echo ""
echo "📈 Check status:"
echo "   ssh root@134.209.244.180 'systemctl status crypto-adaptive.service'"
echo ""
