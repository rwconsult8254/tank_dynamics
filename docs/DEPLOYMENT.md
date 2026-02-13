# Tank Dynamics Simulator - Production Deployment Guide

## System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB (2GB for backend, 2GB for frontend)
- **Storage**: 500MB free space
- **OS**: Linux (Ubuntu 22.04+, Arch Linux) or macOS
- **Python**: 3.10 or higher
- **Node.js**: 18 or higher

### Recommended for Production
- **CPU**: 4+ cores
- **RAM**: 8GB or more
- **Storage**: 1GB (includes logs and temp files)
- **OS**: Ubuntu 22.04 LTS (long-term support, widely supported)
- **Network**: Stable connection, low latency

---

## Dependencies Installation

### Ubuntu 22.04 LTS

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Install build tools and libraries
sudo apt install -y \
  build-essential \
  cmake \
  git \
  libeigen3-dev \
  libgsl-dev \
  python3-dev \
  python3-venv \
  curl

# Install Node.js (v18 or later)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installations
cmake --version
python3 --version
node --version
~/.cargo/bin/uv --version
```

### Arch Linux

```bash
# Update system packages
sudo pacman -Syu

# Install dependencies
sudo pacman -S \
  base-devel \
  cmake \
  eigen \
  gsl \
  nodejs \
  npm

# Install uv
yay -S uv  # Or manually from AUR if yay not available

# Verify installations
cmake --version
python3 --version
node --version
uv --version
```

### macOS

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install \
  cmake \
  eigen \
  gsl \
  python@3.10 \
  node

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installations
cmake --version
python3 --version
node --version
uv --version
```

---

## Building the Application

### Clone Repository

```bash
# Clone the repository (replace with your actual repository URL)
# Example: git clone https://github.com/yourusername/tank_dynamics.git
git clone YOUR_REPOSITORY_URL
cd tank_dynamics

# Or if deploying from existing clone, ensure latest version
git pull origin main
```

### Build C++ Core

```bash
# Create build directory
cmake -B build -DCMAKE_BUILD_TYPE=Release

# Build with optimization flags
cmake --build build --parallel $(nproc)

# Run C++ tests (optional, verify build)
ctest --test-dir build --output-on-failure
```

### Install Python Dependencies

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# Or on Windows: .venv\Scripts\activate

# Install package in editable mode with dependencies
uv pip install -e .

# Verify Python bindings work
python3 -c "from tank_sim import Model; print('Python bindings OK')"
```

### Build Frontend

```bash
cd frontend

# Install Node dependencies
npm install

# Build for production (creates optimized bundle)
npm run build

# Verify build succeeded (should create .next directory)
ls -la .next/
```

---

## Production Configuration

### Backend Configuration

Create `/opt/tank_dynamics/api/config.py` (or update existing):

```python
import os

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
DEBUG = ENVIRONMENT != "production"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "json"  # Structured JSON logging for production

# CORS (Cross-Origin Resource Sharing)
# Set to your domain in production, not "*"
CORS_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]

# Security
SECURE_HEADERS = True
HSTS_ENABLED = True

# Performance
MAX_WEBSOCKET_CONNECTIONS = 50
MESSAGE_QUEUE_SIZE = 1000
```

Update `api/main.py` to use configuration:

```python
from fastapi.middleware.cors import CORSMiddleware
from api.config import CORS_ORIGINS, DEBUG

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend Configuration

Create `frontend/.env.production`:

```
# Backend API URL (must match your domain/server)
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com/ws

# Enable production optimizations
NEXT_PUBLIC_ANALYTICS=true
```

---

## Running in Production

### Option 1: Systemd Services (Recommended for Linux)

#### Create Backend Service File

```bash
sudo nano /etc/systemd/system/tank-simulator-backend.service
```

Paste the following:

```ini
[Unit]
Description=Tank Dynamics Simulator - Backend API
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=tank_simulator
Group=tank_simulator
WorkingDirectory=/opt/tank_dynamics
Environment="PATH=/opt/tank_dynamics/.venv/bin"
Environment="ENVIRONMENT=production"
Environment="LOG_LEVEL=INFO"
ExecStart=/opt/tank_dynamics/.venv/bin/uvicorn api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --access-log
Restart=always
RestartSec=10
StandardOutput=append:/var/log/tank-simulator/backend.log
StandardError=append:/var/log/tank-simulator/backend.log

[Install]
WantedBy=multi-user.target
```

#### Create Frontend Service File

```bash
sudo nano /etc/systemd/system/tank-simulator-frontend.service
```

Paste the following:

```ini
[Unit]
Description=Tank Dynamics Simulator - Frontend
After=network.target
Wants=tank-simulator-backend.service

[Service]
Type=simple
User=tank_simulator
Group=tank_simulator
WorkingDirectory=/opt/tank_dynamics/frontend
Environment="PATH=/usr/bin:/bin:/usr/local/bin"
Environment="NODE_ENV=production"
Environment="PORT=3000"
ExecStart=/usr/bin/npm run start
Restart=always
RestartSec=10
StandardOutput=append:/var/log/tank-simulator/frontend.log
StandardError=append:/var/log/tank-simulator/frontend.log

[Install]
WantedBy=multi-user.target
```

#### Setup User and Directories

```bash
# Create dedicated user
sudo useradd -r -s /bin/false tank_simulator

# Create log directory
sudo mkdir -p /var/log/tank-simulator
sudo chown tank_simulator:tank_simulator /var/log/tank-simulator
sudo chmod 755 /var/log/tank-simulator

# Copy application to /opt
sudo cp -r /home/youruser/tank_dynamics /opt/
sudo chown -R tank_simulator:tank_simulator /opt/tank_dynamics
```

#### Enable and Start Services

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable services to start on boot
sudo systemctl enable tank-simulator-backend
sudo systemctl enable tank-simulator-frontend

# Start services
sudo systemctl start tank-simulator-backend
sudo systemctl start tank-simulator-frontend

# Check status
sudo systemctl status tank-simulator-backend
sudo systemctl status tank-simulator-frontend

# View logs
sudo journalctl -u tank-simulator-backend -f
sudo journalctl -u tank-simulator-frontend -f
```

### Option 2: Docker Containers

Create `Dockerfile.backend`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
  build-essential \
  cmake \
  libeigen3-dev \
  libgsl-dev \
  && rm -rf /var/lib/apt/lists/*

# Copy application
COPY . .

# Install uv using official installer
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Set PATH to include uv
ENV PATH="/root/.cargo/bin:$PATH"

# Create virtual environment and install dependencies
RUN uv venv --python 3.10 && \
    uv pip install -e .

# Set PATH to use venv by default
ENV PATH="/app/.venv/bin:$PATH"

# Expose port
EXPOSE 8000

# Start backend
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `Dockerfile.frontend`:

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy application
COPY frontend .

# Install and build
RUN npm install && npm run build

# Start production server
EXPOSE 3000
CMD ["npm", "run", "start"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      ENVIRONMENT: production
      LOG_LEVEL: INFO
    restart: always
    volumes:
      - ./logs/backend:/var/log/tank-simulator

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
      NEXT_PUBLIC_WS_URL: ws://localhost:8000/ws
    restart: always
    depends_on:
      - backend
    volumes:
      - ./logs/frontend:/var/log/tank-simulator

volumes:
  logs:
```

Start with Docker:

```bash
docker-compose up -d
```

---

## Reverse Proxy Setup (Nginx)

### Install Nginx

```bash
# Ubuntu
sudo apt install nginx

# Arch
sudo pacman -S nginx
```

### Configure Nginx

Create `/etc/nginx/sites-available/tank-simulator`:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Certificate (obtain from Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Frontend proxy
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/tank-simulator /etc/nginx/sites-enabled/
sudo nginx -t  # Verify configuration
sudo systemctl restart nginx
```

### Install SSL Certificates (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is automatic with certbot
```

---

## Monitoring and Maintenance

### Check Service Status

```bash
# Systemd services
sudo systemctl status tank-simulator-backend
sudo systemctl status tank-simulator-frontend

# Docker containers
docker-compose ps
docker-compose logs -f
```

### View Logs

```bash
# Backend logs (systemd)
sudo journalctl -u tank-simulator-backend -f
sudo tail -f /var/log/tank-simulator/backend.log

# Frontend logs (systemd)
sudo journalctl -u tank-simulator-frontend -f
sudo tail -f /var/log/tank-simulator/frontend.log

# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Health Checks

```bash
# Test backend health
curl http://localhost:8000/api/health

# Test frontend
curl http://localhost:3000

# Check WebSocket
wscat -c ws://localhost:8000/ws
```

### Regular Maintenance

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Python dependencies
cd /opt/tank_dynamics
source .venv/bin/activate
uv pip list --outdated  # Check for outdated packages
uv lock --upgrade       # Update lock file

# Update Node dependencies
cd /opt/tank_dynamics/frontend
npm audit fix  # Fix security vulnerabilities
npm update     # Update packages

# Clear logs (keep last 7 days)
sudo journalctl --vacuum-time=7d

# Restart services
sudo systemctl restart tank-simulator-backend tank-simulator-frontend
```

### Performance Monitoring

```bash
# CPU and memory usage
top -b -n 1 | grep python
top -b -n 1 | grep node

# Network connections
netstat -tuln | grep :8000  # Backend
netstat -tuln | grep :3000  # Frontend

# Disk usage
df -h
du -sh /opt/tank_dynamics
du -sh /var/log/tank-simulator
```

---

## Backup and Recovery

### What to Backup

1. **Application code** (if modified):
   ```bash
   tar -czf tank-dynamics-backup.tar.gz /opt/tank_dynamics
   ```

2. **Configuration files**:
   ```bash
   tar -czf config-backup.tar.gz \
     /etc/systemd/system/tank-simulator-*.service \
     /etc/nginx/sites-available/tank-simulator
   ```

3. **Logs** (if needed for compliance):
   ```bash
   tar -czf logs-backup.tar.gz /var/log/tank-simulator
   ```

### Recovery Procedure

```bash
# 1. Stop services
sudo systemctl stop tank-simulator-backend tank-simulator-frontend

# 2. Restore code
sudo tar -xzf tank-dynamics-backup.tar.gz -C /

# 3. Verify permissions
sudo chown -R tank_simulator:tank_simulator /opt/tank_dynamics

# 4. Rebuild if needed
cd /opt/tank_dynamics
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build

# 5. Start services
sudo systemctl start tank-simulator-backend tank-simulator-frontend

# 6. Verify
sudo systemctl status tank-simulator-backend
curl http://localhost:8000/api/health
```

---

## Security Considerations

- ✅ Run services as non-root user (tank_simulator)
- ✅ Use firewall to restrict access:
  ```bash
  sudo ufw default deny incoming
  sudo ufw allow 22/tcp    # SSH
  sudo ufw allow 80/tcp    # HTTP
  sudo ufw allow 443/tcp   # HTTPS
  sudo ufw enable
  ```
- ✅ Use HTTPS with valid SSL certificates
- ✅ Set appropriate CORS origins (not "*")
- ✅ Keep dependencies updated
- ✅ Monitor for unusual access patterns
- ✅ Configure firewall for internal-only access if on private network

---

## Troubleshooting

### Backend won't start

**Error**: `Address already in use`
```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>
# Start service again
sudo systemctl start tank-simulator-backend
```

**Error**: `ModuleNotFoundError: No module named 'tank_sim'`
```bash
# Rebuild Python bindings
cd /opt/tank_dynamics
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
source .venv/bin/activate
uv pip install -e .
```

### Frontend won't start

**Error**: `port 3000 already in use`
```bash
lsof -i :3000
kill -9 <PID>
```

**Error**: `npm: command not found`
```bash
# Check Node.js installation
which node
npm --version

# If missing, reinstall
sudo apt install nodejs npm
```

### WebSocket connection fails

**Check**:
- Backend is running: `curl http://localhost:8000/api/health`
- Firewall allows WebSocket: `sudo ufw status`
- Nginx WebSocket configured correctly (see config above)
- Client is using correct URL (wss:// for HTTPS, ws:// for HTTP)

### High CPU/Memory usage

1. Check active connections: `netstat -tuln | grep ESTABLISHED`
2. Reduce worker processes if using gunicorn
3. Check for long-running operations in logs
4. Restart services to clear state: `sudo systemctl restart tank-simulator-*`

---

## Production Checklist

- [ ] Dependencies installed
- [ ] Application built successfully
- [ ] Tests passing (optional but recommended)
- [ ] Systemd service files created and enabled
- [ ] Nginx reverse proxy configured
- [ ] SSL certificates installed
- [ ] Firewall rules configured
- [ ] Log directory created with correct permissions
- [ ] Health checks responding correctly
- [ ] WebSocket connection working
- [ ] Backup strategy documented
- [ ] Monitoring in place
- [ ] Documentation updated for your environment

---

## Support

For deployment issues:
1. Check `/var/log/tank-simulator/` for detailed error messages
2. Review systemd journal: `journalctl -u tank-simulator-backend -n 50`
3. Test individual components (backend API, frontend build)
4. Verify all dependencies are installed

For technical support, contact your development team with:
- OS version
- Error messages from logs
- Steps to reproduce the issue
