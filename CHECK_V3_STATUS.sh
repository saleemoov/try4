#!/bin/bash

echo "📊 Crypto Adaptive Bot v3.0 - Status Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

SERVER="root@134.209.244.180"

# Check service status
echo "1️⃣ Service Status:"
ssh -o StrictHostKeyChecking=no $SERVER 'systemctl is-active adaptive-crypto.service && echo "✅ Running" || echo "❌ Stopped"'
echo ""

# Check process
echo "2️⃣ Process Info:"
ssh -o StrictHostKeyChecking=no $SERVER 'ps aux | grep crypto_adaptive_bot.py | grep -v grep | awk "{print \"PID: \"\$2\" | CPU: \"\$3\"% | MEM: \"\$4\"% | Started: \"\$9}"'
echo ""

# Count signals today
echo "3️⃣ Signals Today:"
ssh -o StrictHostKeyChecking=no $SERVER 'journalctl -u adaptive-crypto.service --since today --no-pager | grep -c "BUY!" && echo "total signals"'
echo ""

# Last 10 signals
echo "4️⃣ Last 10 Signals:"
ssh -o StrictHostKeyChecking=no $SERVER 'journalctl -u adaptive-crypto.service --no-pager | grep "BUY!" | tail -10'
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 View live logs:"
echo "   ssh root@134.209.244.180 'journalctl -u adaptive-crypto.service -f'"
echo ""
echo "🔄 Restart bot:"
echo "   ssh root@134.209.244.180 'systemctl restart adaptive-crypto.service'"
