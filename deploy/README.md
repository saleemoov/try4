Deploy README — Advanced Trading Bot

Goal
--
Provide a simple way to deploy the bot to a DigitalOcean droplet (or any Ubuntu server).

Before you start
--
- You have a droplet (Ubuntu 22.04/24.04 recommended) and its public IP.
- You have SSH access to the droplet (key or password). The deploy script uses rsync+ssh.
- Your local repo contains the bot and `requirements.txt`.

Recommended droplet spec
--
- 1 vCPU, 1 GB RAM (512 MB can work but 1 GB is safer)
- 10–25 GB SSD
- 1 TB transfer (DigitalOcean plans normally include this)

Quick deploy (local machine)
--
1. Edit `deploy/deploy_to_droplet.sh` and set `DROPLET_IP` and `DROPLET_USER`.
2. From your project root run:

```bash
chmod +x deploy/deploy_to_droplet.sh
./deploy/deploy_to_droplet.sh
```

What the script does
--
- rsync project files to the droplet
- installs Python and required system packages
- creates a virtualenv and installs `requirements.txt`
- writes a systemd service file `/etc/systemd/system/advanced_trading_bot.service`
- enables and starts the service

Manual server setup
--
If you prefer to provision manually, here are the commands to run on the droplet:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git rsync
# as deploy user
cd ~
git clone <your-repo> try4
cd try4
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# create systemd service (edit paths and user)
sudo tee /etc/systemd/system/advanced_trading_bot.service <<'EOF'
[Unit]
Description=Advanced Trading Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/try4
Environment=PYTHONUNBUFFERED=1
ExecStart=/home/youruser/try4/venv/bin/python3 /home/youruser/try4/advanced_trading_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now advanced_trading_bot.service
sudo journalctl -u advanced_trading_bot -f
```

Next steps I can help with
--
- If you provide droplet IP and username I can provide exact commands to run or a one-liner for you to copy.
- If you want, I can generate a small `.env.example` and help secure API keys before deployment.
- I can also prepare a Dockerfile + `docker-compose.yml` if you prefer container deployment.

Security note
--
- Prefer SSH keys over password
- Do not share private SSH keys publicly. If you want me to run remote commands, share only the droplet IP and run the deploy script locally (recommended).  
