import sys
sys.path.insert(0, '/workspaces/try4')
from crypto_adaptive_bot import *
import json, time

with open('trading_config.json') as f:
    config = json.load(f)

bot = CryptoAdaptiveBot(
    config['okx']['api_key'],
    config['okx']['api_secret'], 
    config['okx']['passphrase'],
    config['telegram']['bot_token'],
    config['telegram']['chat_id']
)

print('\n===== SCAN 1 =====')
symbols = bot._get_top_symbols()[:3]
for sym in symbols:
    bot._analyze_symbol(sym)

print('\n===== SCAN 2 (بعد ثانية) =====')
time.sleep(1)
for sym in symbols:
    bot._analyze_symbol(sym)

print('\n✅ Test complete!')
