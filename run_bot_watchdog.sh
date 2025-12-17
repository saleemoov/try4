#!/usr/bin/env bash
# Watchdog script: keeps advanced_trading_bot.py running and restarts on exit
cd "$(dirname "$0")"

LOGFILE="watchdog.log"
BOT_LOG="bot.log"

send_telegram_restart() {
  # Read token/chat from trading_config.json (supporting both old/new schema)
  if [ ! -f trading_config.json ]; then
    echo "$(date -Iseconds) - watchdog: trading_config.json not found; cannot send telegram notification" >> "$LOGFILE"
    return 1
  fi

  token=$(python3 - <<'PY'
import json,sys
try:
    d=json.load(open('trading_config.json'))
    t = d.get('telegram',{}).get('bot_token') or d.get('telegram_token')
    print(t or '')
except Exception:
    print('')
PY
)

  chat_id=$(python3 - <<'PY'
import json,sys
try:
    d=json.load(open('trading_config.json'))
    c = d.get('telegram',{}).get('chat_id') or d.get('telegram_chat_id')
    print(c or '')
except Exception:
    print('')
PY
)

  if [ -z "$token" ] || [ -z "$chat_id" ]; then
    echo "$(date -Iseconds) - watchdog: telegram token/chat not found; skipping notification" >> "$LOGFILE"
    return 1
  fi

  # prepare a concise error snippet (prefer Traceback, else recent ERROR/Exception lines)
  err_snippet=$(tail -n 300 bot.log | sed -n '/Traceback\|Exception/,${p}' | tail -n 120)
  if [ -z "$err_snippet" ]; then
    err_snippet=$(grep -E "ERROR|Exception|Traceback" bot.log | tail -n 20)
  fi
  if [ -z "$err_snippet" ]; then
    err_snippet="(no recent error lines found in bot.log)"
  else
    # truncate to ~800 chars to keep message short
    err_snippet=$(printf "%s" "$err_snippet" | tail -c 800)
  fi

  text="Watchdog: advanced_trading_bot.py restarted at $(date -u +'%Y-%m-%d %H:%M:%SZ')\nExitCode: ${1:-?}\nRecentError:\n${err_snippet}"

  # send via curl (quiet). Use --data-urlencode for safety with newlines
  curl -s -X POST "https://api.telegram.org/bot${token}/sendMessage" \
    --data-urlencode "chat_id=${chat_id}" \
    --data-urlencode "text=${text}" >/dev/null 2>&1 || true

  echo "$(date -Iseconds) - watchdog: telegram restart notification sent (exit=${1:-?})" >> "$LOGFILE"
}

echo "$(date -Iseconds) - watchdog: started" >> "$LOGFILE"

while true; do
  echo "$(date -Iseconds) - watchdog: launching advanced_trading_bot.py" >> "$LOGFILE"
  python3 advanced_trading_bot.py >> "$BOT_LOG" 2>&1
  rc=$?
  echo "$(date -Iseconds) - watchdog: process exited with code $rc. restarting in 10s" >> "$LOGFILE"

  # small pause then attempt to notify user that we are restarting, include exit code
  sleep 1
  send_telegram_restart "$rc" || true

  sleep 10
done
