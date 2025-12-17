#!/usr/bin/env bash
# deploy_to_droplet.sh
# Usage: edit variables below and run from your local machine where your project is.
# It rsyncs the workspace to the droplet, installs dependencies, creates a venv,
# writes a systemd service and starts it.

set -euo pipefail

# ----- Edit these -----
DROPLET_IP="1.2.3.4"            # <-- replace with your droplet IP
DROPLET_USER="youruser"         # <-- replace (e.g., ubuntu or yourusername)
REMOTE_BASE="/home/$DROPLET_USER/try4"  # remote path where repo will live
SSH_OPTS="-o StrictHostKeyChecking=no"
# ----------------------

if [ "$DROPLET_IP" = "1.2.3.4" ]; then
  echo "Please edit deploy_to_droplet.sh and set DROPLET_IP and DROPLET_USER"
  exit 1
fi

echo "Syncing project to $DROPLET_USER@$DROPLET_IP:$REMOTE_BASE"
rsync -av --exclude __pycache__ --exclude ".git" --exclude "*.pyc" ./ $DROPLET_USER@$DROPLET_IP:$REMOTE_BASE

echo "Running remote provisioning on $DROPLET_IP"
ssh $SSH_OPTS $DROPLET_USER@$DROPLET_IP bash -s <<'REMOTE'
set -euo pipefail
USER="${DROPLET_USER}"
REMOTE_BASE="${REMOTE_BASE}"

# Install system packages
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git rsync

# Create venv and install requirements
cd "$REMOTE_BASE"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi

# Create systemd service (system-level)
SERVICE_PATH="/etc/systemd/system/advanced_trading_bot.service"
cat <<EOF | sudo tee "$SERVICE_PATH"
[Unit]
Description=Advanced Trading Bot
After=network.target

[Service]
Type=simple
User=${DROPLET_USER}
WorkingDirectory=${REMOTE_BASE}
Environment=PYTHONUNBUFFERED=1
ExecStart=${REMOTE_BASE}/venv/bin/python3 ${REMOTE_BASE}/advanced_trading_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl enable --now advanced_trading_bot.service
sudo systemctl restart advanced_trading_bot.service || true

# Show status
sudo systemctl status advanced_trading_bot.service --no-pager || true

REMOTE

echo "Deployment finished. Check the service with: ssh $DROPLET_USER@$DROPLET_IP 'sudo systemctl status advanced_trading_bot'"

echo "If you want logs: ssh $DROPLET_USER@$DROPLET_IP 'journalctl -u advanced_trading_bot -f'"
chmod +x deploy_to_droplet.sh
