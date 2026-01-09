#!/bin/bash

# 🚀 MEME HUNTER - Quick Setup Script
# الإعداد السريع لبوت صيد عملات الميم

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 MEME HUNTER BOT - Quick Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found! Installing..."
    sudo apt update
    sudo apt install -y python3 python3-pip
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install requests asyncio --quiet

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""

# Check if config file exists
if [ ! -f "meme_hunter_config.json" ]; then
    echo "⚠️ Config file not found!"
    echo "Creating default config..."
    
    cat > meme_hunter_config.json << 'EOF'
{
  "telegram": {
    "bot_token": "YOUR_TELEGRAM_BOT_TOKEN_HERE",
    "chat_id": "YOUR_TELEGRAM_CHAT_ID_HERE"
  },
  
  "detection_criteria": {
    "min_liquidity_usd": 50000,
    "min_volume_24h_usd": 200000,
    "min_transactions_24h": 5000,
    "min_holders": 500,
    "liquidity_lock_required": false,
    "min_price_change_1h": 20.0,
    "min_price_change_5m": 5.0,
    "max_price_change_24h": 2000.0
  },
  
  "social_requirements": {
    "min_twitter_followers": 1000,
    "min_telegram_members": 500,
    "require_verified_contract": false
  },
  
  "risk_management": {
    "max_position_size_pct": 0.01,
    "max_total_meme_exposure": 0.03,
    "stop_loss_pct": -15.0,
    "max_concurrent_positions": 3,
    "target_1_pct": 50.0,
    "target_2_pct": 150.0,
    "target_3_pct": 500.0,
    "exit_1_pct": 0.50,
    "exit_2_pct": 0.30,
    "exit_3_pct": 0.20
  },
  
  "timing": {
    "max_hold_hours": 12,
    "scan_interval_seconds": 60,
    "cooldown_hours": 4,
    "max_signals_per_day": 5
  },
  
  "target_platforms": {
    "primary_chain": "solana",
    "backup_chains": ["bsc", "ethereum", "base"]
  },
  
  "blacklist": {
    "tokens": [],
    "creators": []
  }
}
EOF
    
    echo "✅ Config file created: meme_hunter_config.json"
    echo ""
    echo "⚠️ IMPORTANT: Edit the config file and add your Telegram credentials!"
    echo ""
    read -p "Press Enter to open config file in nano editor..."
    nano meme_hunter_config.json
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup completed!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next steps:"
echo ""
echo "1️⃣ Edit config file:"
echo "   nano meme_hunter_config.json"
echo ""
echo "2️⃣ Add your Telegram bot token and chat ID"
echo ""
echo "3️⃣ Run the bot:"
echo "   python3 meme_hunter.py"
echo ""
echo "4️⃣ For background run:"
echo "   screen -S meme_hunter"
echo "   python3 meme_hunter.py"
echo "   # Press Ctrl+A then D to detach"
echo ""
echo "5️⃣ To check running bot:"
echo "   screen -r meme_hunter"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Ready to hunt meme coins!"
echo ""
