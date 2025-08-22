# 🔧 Installation Guide

**Blueprint Generator Pro - Professional Setup Instructions**

This guide will walk you through installing and configuring Blueprint Generator Pro for your environment.

## 📋 **Prerequisites**

### **System Requirements**
- **Operating System**: Linux, macOS, or Windows 10/11
- **Python**: 3.9 or higher (3.11+ recommended)
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 2GB free space minimum (10GB recommended)
- **Network**: Internet connection for initial setup

### **Required Software**
- **Docker** (recommended) - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** - [Install Docker Compose](https://docs.docker.com/compose/install/)
- **Git** - [Install Git](https://git-scm.com/downloads)

### **Optional but Recommended**
- **Reverse Proxy** (nginx, Traefik, or Caddy)
- **SSL Certificate** for HTTPS
- **Domain Name** for production deployment

## 🚀 **Quick Start (Docker - Recommended)**

### **1. Clone the Repository**
```bash
# Requires valid commercial license
git clone https://github.com/yourusername/BlueprintGeneratorPro.git
cd BlueprintGeneratorPro
```

### **2. Configure Environment**
```bash
# Copy environment template
cp .env.example .env

# Edit configuration (see Configuration section below)
nano .env
```

### **3. Start Services**
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### **4. Access the Application**
- **Web Interface**: http://localhost:8001
- **Validation Service**: http://localhost:8002
- **Health Check**: http://localhost:8001/api/health

### **5. Verify Installation**
```bash
# Test web interface
curl http://localhost:8001/api/health

# Test validation service
curl http://localhost:8002/

# Run system tests
docker-compose exec web python -m pytest tests/
```

## 🐍 **Manual Installation (Python)**

### **1. Clone and Setup**
```bash
git clone https://github.com/yourusername/BlueprintGeneratorPro.git
cd BlueprintGeneratorPro
```

### **2. Create Virtual Environment**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### **3. Install Dependencies**
```bash
# Install web app dependencies
cd web_app
pip install -r requirements.txt

# Install validation service dependencies
cd ../validation_service
pip install -r requirements.txt

# Install testing dependencies
cd ../tests
pip install -r requirements.txt
```

### **4. Configure Services**
```bash
# Copy configuration files
cp web_app/.env.example web_app/.env
cp validation_service/.env.example validation_service/.env

# Edit configurations
nano web_app/.env
nano validation_service/.env
```

### **5. Start Services**
```bash
# Terminal 1: Start web application
cd web_app
python main.py

# Terminal 2: Start validation service
cd validation_service
python main.py
```

## ⚙️ **Configuration**

### **Environment Variables**

Create `.env` files in both `web_app/` and `validation_service/` directories:

#### **Web App Configuration (`web_app/.env`)**
```bash
# Application Settings
APP_NAME="Blueprint Generator Pro"
APP_VERSION="1.0.0"
DEBUG=false
SECRET_KEY="your-secret-key-here"

# Server Configuration
HOST=0.0.0.0
PORT=8001
WORKERS=4

# Security Settings
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
CORS_ORIGINS=http://localhost:8001,https://yourdomain.com
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_PERIOD=60

# Validation Service
VALIDATION_SERVICE_URL=http://localhost:8002

# Monitoring
ENABLE_METRICS=true
LOG_LEVEL=INFO
LOG_FORMAT=json

# File Storage
UPLOAD_MAX_SIZE=100MB
STORAGE_PATH=/app/storage
```

#### **Validation Service Configuration (`validation_service/.env`)**
```bash
# Service Settings
SERVICE_NAME="Blueprint Validation Service"
SERVICE_VERSION="1.0.0"
DEBUG=false

# Server Configuration
HOST=0.0.0.0
PORT=8002
WORKERS=2

# Analysis Settings
MAX_FILE_SIZE=100MB
ANALYSIS_TIMEOUT=300
CACHE_TTL=3600

# Security
API_KEY_REQUIRED=false
ALLOWED_IPS=127.0.0.1,localhost

# Performance
ENABLE_CACHING=true
CACHE_SIZE=1000
```

### **Docker Compose Configuration**

The `docker-compose.yml` file includes:

```yaml
version: '3.8'

services:
  web:
    build: ./web_app
    ports:
      - "8001:8001"
    environment:
      - VALIDATION_SERVICE_URL=http://validation:8002
    volumes:
      - ./storage:/app/storage
    depends_on:
      - validation
    restart: unless-stopped

  validation:
    build: ./validation_service
    ports:
      - "8002:8002"
    volumes:
      - ./temp:/app/temp
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped
```

## 🔒 **Security Configuration**

### **SSL/TLS Setup**
```bash
# Generate self-signed certificate (development)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/private.key -out ssl/certificate.crt

# Or use Let's Encrypt (production)
certbot --nginx -d yourdomain.com
```

### **Firewall Configuration**
```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow SSH (if needed)
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

### **Security Headers**
The application automatically includes security headers:
- Content Security Policy (CSP)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Strict-Transport-Security

## 📊 **Monitoring Setup**

### **Health Checks**
```bash
# Basic health check
curl http://localhost:8001/api/health

# Detailed health check
curl http://localhost:8001/api/health/detailed

# Performance metrics
curl http://localhost:8001/api/metrics
```

### **Log Configuration**
```bash
# View application logs
docker-compose logs -f web

# View validation service logs
docker-compose logs -f validation

# Export logs
docker-compose logs --no-color > application.log
```

## 🧪 **Testing Installation**

### **Run Test Suite**
```bash
# Run all tests
cd tests
python -m pytest -v

# Run specific test categories
python -m pytest test_simple.py -v
python -m pytest test_integration.py -v

# Run with coverage
python -m pytest --cov=../web_app --cov-report=html
```

### **Performance Testing**
```bash
# Install performance testing tools
pip install locust

# Run load tests
locust -f tests/locustfile.py --host http://localhost:8001
```

### **Security Testing**
```bash
# Install security tools
pip install bandit safety

# Run security scans
bandit -r web_app/ validation_service/
safety check
```

## 🚀 **Production Deployment**

### **Docker Swarm**
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.prod.yml blueprint-pro
```

### **Kubernetes**
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n blueprint-pro
```

### **Systemd Service**
```bash
# Create systemd service
sudo cp blueprint-pro.service /etc/systemd/system/
sudo systemctl enable blueprint-pro
sudo systemctl start blueprint-pro
```

## 🔧 **Troubleshooting**

### **Common Issues**

#### **Port Already in Use**
```bash
# Find process using port
lsof -i :8001
sudo kill -9 <PID>

# Or change port in configuration
export PORT=8003
```

#### **Permission Denied**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x web_app/start.sh
```

#### **Docker Issues**
```bash
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Clean Docker system
docker system prune -a
```

#### **Memory Issues**
```bash
# Increase Docker memory limit
# Docker Desktop: Settings > Resources > Memory

# Monitor memory usage
docker stats
```

### **Log Analysis**
```bash
# Check application logs
tail -f web_app/app.log

# Check system logs
journalctl -u blueprint-pro -f

# Check Docker logs
docker-compose logs --tail=100 -f
```

## 📞 **Support**

If you encounter issues during installation:

1. **Check the logs** for error messages
2. **Review the troubleshooting** section above
3. **Search existing issues** on GitHub
4. **Contact support** with detailed error information

**Support Channels:**
- **Email**: Bentleywinstonco@outlook.com
- **Documentation**: [View Documentation](../docs/)
- **GitHub Issues**: [Report Issues](https://github.com/MissyMedina/BlueprintGeneratorPro/issues)
- **Support Development**: [Buy Me a Coffee](https://buymeacoffee.com/bentleywinston)

## ✅ **Next Steps**

After successful installation:

1. **Read the [User Guide](USER_GUIDE.md)** to learn how to use the platform
2. **Configure your [API settings](API.md)** for integrations
3. **Review [security best practices](SECURITY.md)**
4. **Support the project** by [buying me a coffee](https://buymeacoffee.com/bentleywinston)

---

**🎉 Congratulations! Blueprint Generator Pro is now installed and ready to use.**
