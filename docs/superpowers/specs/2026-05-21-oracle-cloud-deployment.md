# Oracle Cloud Free Tier Deployment Guide

## Goal
Deploy the ctracker interview analyzer (FastAPI + React + ML models) on Oracle Cloud's free ARM VM for public portfolio demo access.

## Architecture

```
User ──HTTPS──→ Caddy (port 443) ──proxy──→ Uvicorn (port 8000)
                                                │
                                          ┌─────┴─────┐
                                          │  SQLite DB │
                                          │ uploads/   │
                                          │ temp/      │
                                          └───────────┘
```

- **Caddy** handles TLS termination and reverse proxy (auto HTTPS via Let's Encrypt)
- **Uvicorn** runs the FastAPI app on 127.0.0.1:8000 (not exposed publicly)
- **SQLite** stores interview data in `database/app.db`
- **Uploads** stored on disk in `uploads/`, `temp/`, `reports/`

## Prerequisites
- Oracle Cloud Free Tier account (requires credit card for identity verification)
- A domain or DuckDNS subdomain (optional — can use IP directly)
- GitHub repo with the code pushed

## Step-by-Step

### 1. Provision Oracle Cloud VM

1. Log in to Oracle Cloud console → Compute → Instances → Create instance
2. Name: `ctracker`
3. Image: **Canonical Ubuntu 24.04** (ARM64)
4. Shape: **VM.Standard.A1.Flex** — set OCPU to **4**, Memory to **24 GB**
5. Add SSH key — generate one or paste your public key
6. Boot volume: **200 GB** (free tier includes up to 200 GB total)
7. Create → wait a few minutes for provisioning
8. Note the **Public IP Address** from the instance details

### 2. Configure Network Security

1. In the instance details, under "Resources" click **VNIC** → **Subnet** → **Security Lists**
2. Add ingress rules:
   - **Port 22** (SSH) — Source: `0.0.0.0/0` (or your IP only)
   - **Port 80** (HTTP) — Source: `0.0.0.0/0`
   - **Port 443** (HTTPS) — Source: `0.0.0.0/0`
3. Optionally restrict SSH to your home IP

### 3. Initial Server Setup

SSH into the VM:

```bash
ssh ubuntu@<PUBLIC_IP>
```

Update and install essentials:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip ffmpeg git curl
```

### 4. Deploy the Application

```bash
# Clone repo
cd ~
git clone https://github.com/<YOUR_USER>/ctracker.git
cd ctracker

# Create virtual environment (Python 3.11)
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Create data directories
mkdir -p uploads temp reports
```

### 5. Initial Model Cache (Optional but Recommended)

Run the app once to trigger model downloads (Whisper, DeepFace models):

```bash
# This will download ~2GB of model files on first run
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000
# Press Ctrl+C after models are downloaded and app starts
```

Models cache to `~/.cache/` — this prevents cold-start delays on service restart.

### 6. Install Caddy (Reverse Proxy)

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
```

Configure Caddy:

```bash
sudo nano /etc/caddy/Caddyfile
```

For a domain:
```
yourdomain.com {
    reverse_proxy 127.0.0.1:8000
}
```

For direct IP (will use HTTP only):
```
http://<PUBLIC_IP> {
    reverse_proxy 127.0.0.1:8000
}
```

```bash
sudo systemctl restart caddy
sudo systemctl enable caddy
```

### 7. Create systemd Service

```bash
sudo nano /etc/systemd/system/ctracker.service
```

```
[Unit]
Description=ctracker FastAPI server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ctracker
ExecStart=/home/ubuntu/ctracker/venv/bin/uvicorn api.server:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5
Environment="PATH=/home/ubuntu/ctracker/venv/bin:/usr/bin:/usr/local/bin"

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable ctracker
sudo systemctl start ctracker
sudo systemctl status ctracker  # Verify running
```

### 8. Verify

```bash
curl http://localhost:8000  # Should return HTML
curl http://<PUBLIC_IP>    # Should return HTML via Caddy
```

Open `http://<PUBLIC_IP>` (or your domain) in a browser.

### 9. Security Hardening

```bash
# Set up UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Install fail2ban to protect SSH
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 10. Auto-Deploy on Git Push

Set up a deploy script at `/home/ubuntu/ctracker/deploy.sh`:

```bash
#!/bin/bash
cd /home/ubuntu/ctracker
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --quiet
sudo systemctl restart ctracker
```

```bash
chmod +x deploy.sh
```

Then from your local machine:
```bash
ssh ubuntu@<PUBLIC_IP> 'bash /home/ubuntu/ctracker/deploy.sh'
```

Or set up a GitHub webhook + a lightweight listener for push-to-deploy.

### 11. Storage Cleanup (Cron)

Create a cleanup script at `/home/ubuntu/ctracker/cleanup.sh`:

```bash
#!/bin/bash
find /home/ubuntu/ctracker/uploads -type f -mtime +30 -delete
find /home/ubuntu/ctracker/temp -type f -mtime +7 -delete
```

```bash
chmod +x cleanup.sh
crontab -e
# Add:
0 3 * * 0 /home/ubuntu/ctracker/cleanup.sh
```

### 12. Database Backup (Cron)

```bash
crontab -e
# Add weekly backup:
0 4 * * 0 cp /home/ubuntu/ctracker/database/app.db /home/ubuntu/backups/app.db.$(date +\%Y\%m\%d)
```

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Cannot SSH | Security list missing port 22 | Check Oracle Cloud security list rules |
| `502 Bad Gateway` | Uvicorn not running | `sudo systemctl restart ctracker`; `journalctl -u ctracker -n 20` |
| Blank page in browser | `isLight` reference error | Ensure frontend builds cleanly; check browser console |
| Analysis fails mid-way | Out of memory | Monitor with `htop`. 24GB should suffice for base Whisper model |
| Upload fails (>500MB) | File too large | Reduce video duration or increase limit in server.py |
| Models re-downloading | Cache cleared | Verify `~/.cache/` exists and has correct permissions |
| Cannot install Python packages | ARM-specific wheel missing | Use `pip install --no-cache-dir` or build from source |

## Costs

- **Oracle Cloud Free Tier:** $0/mo (4 OCPU, 24GB RAM, 200GB storage)
- **DuckDNS (free domain):** $0/yr
- **Real domain:** ~$10-15/yr (optional)
- **Cloudflare (free DNS + DDoS protection):** $0/mo

## Known Limitations

- SQLite handles ~1 concurrent write well; multiple simultaneous users may experience contention
- Cold start after inactivity: ~30s for Uvicorn startup + model loading
- Oracle may reclaim idle free-tier instances after inactivity (uncommon but documented)
- 200GB disk fills up eventually — video cleanup cron is important
- DeepFace/TensorFlow has heavy dependency chain (~800MB pip install)
