# Deployment Guide - Soccer Timekeeper App

**Version:** 1.0  
**Last Updated:** February 25, 2026

---

## Table of Contents

1. [Deployment Options Overview](#deployment-options-overview)
2. [Quick Start - Streamlit Cloud (Recommended)](#quick-start---streamlit-cloud-recommended)
3. [Alternative Deployment Options](#alternative-deployment-options)
4. [Pre-Deployment Checklist](#pre-deployment-checklist)
5. [Production Configuration](#production-configuration)
6. [Security Considerations](#security-considerations)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Deployment Options Overview

### Comparison Matrix

| Platform | Difficulty | Cost | Best For | Scalability |
|----------|-----------|------|----------|-------------|
| **Streamlit Cloud** | ⭐ Easy | Free | Quick deployment, demos | Low-Medium |
| **Heroku** | ⭐⭐ Medium | $7-25/mo | Production apps | Medium |
| **AWS EC2** | ⭐⭐⭐ Hard | $10-50/mo | Full control | High |
| **Docker + Cloud Run** | ⭐⭐⭐ Hard | Pay-per-use | Containerized apps | High |
| **Railway** | ⭐⭐ Medium | $5-20/mo | Modern deployment | Medium |

### Recommended: Streamlit Cloud

**Why?**
- ✅ Free tier available
- ✅ Zero configuration needed
- ✅ Automatic HTTPS
- ✅ Built specifically for Streamlit apps
- ✅ GitHub integration
- ✅ Easy updates via git push

**Limitations:**
- Limited to 1GB RAM on free tier
- Public apps only (unless paid)
- Limited concurrent users (~50-100)

---

## Quick Start - Streamlit Cloud (Recommended)

### Prerequisites
- GitHub account
- Your code pushed to a GitHub repository

### Step 1: Prepare Your Repository

1. **Create `.streamlit/config.toml`** (optional but recommended):

```toml
[theme]
primaryColor = "#2e7d32"
backgroundColor = "#e8f5e9"
secondaryBackgroundColor = "#c8e6c9"
textColor = "#1b5e20"

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

2. **Update `requirements.txt`** for production:

```txt
# Web Framework
streamlit>=1.28.0

# QR Code Generation and Scanning
qrcode[pil]>=7.4.2
streamlit-qrcode-scanner>=0.1.0

# Production dependencies (optional)
watchdog>=3.0.0  # For better file watching
```

3. **Create `.gitignore`** (if not exists):

```gitignore
# Data files
data/storage.json
data/*.json

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.venv/
env/
ENV/

# Testing
.pytest_cache/
.hypothesis/
htmlcov/
.coverage

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

4. **Push to GitHub**:

```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### Step 2: Deploy to Streamlit Cloud

1. **Go to** [share.streamlit.io](https://share.streamlit.io)

2. **Sign in** with your GitHub account

3. **Click "New app"**

4. **Configure deployment**:
   - Repository: Select your repository
   - Branch: `main` (or your default branch)
   - Main file path: `app.py`
   - App URL: Choose a custom subdomain (e.g., `soccer-timekeeper`)

5. **Advanced settings** (click "Advanced settings"):
   - Python version: `3.9` or higher
   - Secrets: Add any environment variables (see below)

6. **Click "Deploy"**

7. **Wait 2-5 minutes** for deployment to complete

### Step 3: Configure Secrets (Optional)

If you need environment variables, add them in the Streamlit Cloud dashboard:

```toml
# .streamlit/secrets.toml (for local testing)
# DO NOT commit this file to git!

STORAGE_PATH = "data/storage.json"
STORAGE_TYPE = "json"
```

In Streamlit Cloud dashboard:
- Go to your app settings
- Click "Secrets"
- Paste the same content

### Step 4: Test Your Deployment

1. Visit your app URL (e.g., `https://soccer-timekeeper.streamlit.app`)
2. Test all features:
   - Create a match
   - Generate QR code
   - Scan QR code (on mobile)
   - View timer
   - Test admin controls
3. Check for any errors in the logs

---

## Alternative Deployment Options

### Option 2: Heroku

**Best for:** Production apps with custom domains

#### Prerequisites
- Heroku account
- Heroku CLI installed

#### Deployment Steps

1. **Create `Procfile`**:

```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

2. **Create `runtime.txt`**:

```
python-3.11.7
```

3. **Create `setup.sh`**:

```bash
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

4. **Update `Procfile`** to use setup script:

```
web: sh setup.sh && streamlit run app.py
```

5. **Deploy to Heroku**:

```bash
# Login to Heroku
heroku login

# Create new app
heroku create soccer-timekeeper-app

# Set buildpack
heroku buildpacks:set heroku/python

# Deploy
git push heroku main

# Open app
heroku open
```

6. **Configure environment variables**:

```bash
heroku config:set STORAGE_PATH=/tmp/storage.json
heroku config:set STORAGE_TYPE=json
```

**Cost:** $7/month (Eco dyno) or $25/month (Basic dyno)

---

### Option 3: AWS EC2

**Best for:** Full control, high scalability

#### Prerequisites
- AWS account
- Basic Linux knowledge

#### Deployment Steps

1. **Launch EC2 Instance**:
   - AMI: Ubuntu 22.04 LTS
   - Instance type: t2.micro (free tier) or t2.small
   - Security group: Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS)

2. **Connect to instance**:

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

3. **Install dependencies**:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3-pip python3-venv nginx -y

# Clone your repository
git clone https://github.com/yourusername/soccer-timekeeper.git
cd soccer-timekeeper

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

4. **Create systemd service** (`/etc/systemd/system/streamlit.service`):

```ini
[Unit]
Description=Streamlit Soccer Timekeeper App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/soccer-timekeeper
Environment="PATH=/home/ubuntu/soccer-timekeeper/venv/bin"
ExecStart=/home/ubuntu/soccer-timekeeper/venv/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0

[Install]
WantedBy=multi-user.target
```

5. **Configure Nginx** (`/etc/nginx/sites-available/streamlit`):

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

6. **Enable and start services**:

```bash
# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/streamlit /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Enable and start Streamlit service
sudo systemctl enable streamlit
sudo systemctl start streamlit

# Check status
sudo systemctl status streamlit
```

7. **Set up SSL with Let's Encrypt** (optional but recommended):

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

**Cost:** ~$10-50/month depending on instance size

---

### Option 4: Docker + Google Cloud Run

**Best for:** Containerized deployments, pay-per-use pricing

#### Prerequisites
- Docker installed
- Google Cloud account
- gcloud CLI installed

#### Deployment Steps

1. **Create `Dockerfile`**:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. **Create `.dockerignore`**:

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
venv/
.venv/
.git
.gitignore
.pytest_cache
.hypothesis
data/storage.json
tests/
*.md
```

3. **Build and test locally**:

```bash
# Build image
docker build -t soccer-timekeeper .

# Run locally
docker run -p 8501:8501 soccer-timekeeper

# Test at http://localhost:8501
```

4. **Deploy to Google Cloud Run**:

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and push to Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/soccer-timekeeper

# Deploy to Cloud Run
gcloud run deploy soccer-timekeeper \
  --image gcr.io/YOUR_PROJECT_ID/soccer-timekeeper \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1
```

**Cost:** Pay-per-use, typically $5-20/month for moderate traffic

---

### Option 5: Railway

**Best for:** Modern, simple deployment with good developer experience

#### Deployment Steps

1. **Go to** [railway.app](https://railway.app)

2. **Sign in** with GitHub

3. **Click "New Project"** → "Deploy from GitHub repo"

4. **Select your repository**

5. **Railway auto-detects** Python and Streamlit

6. **Add environment variables** (if needed):
   - `STORAGE_PATH=/app/data/storage.json`
   - `STORAGE_TYPE=json`

7. **Deploy** - Railway handles everything automatically

8. **Get your URL** from the deployment dashboard

**Cost:** $5/month (Hobby plan) or $20/month (Pro plan)

---

## Pre-Deployment Checklist

### Code Preparation

- [ ] All tests pass (`pytest tests/`)
- [ ] Code coverage meets threshold (92%+)
- [ ] No hardcoded secrets or credentials
- [ ] Environment variables configured
- [ ] `.gitignore` properly configured
- [ ] `requirements.txt` up to date
- [ ] README.md updated with deployment info

### Configuration

- [ ] `config.py` uses environment variables
- [ ] Storage path configured for production
- [ ] CORS settings configured (if needed)
- [ ] Session management configured
- [ ] Error logging enabled

### Security

- [ ] No sensitive data in repository
- [ ] HTTPS enabled (for production)
- [ ] Input validation implemented
- [ ] File upload restrictions (if applicable)
- [ ] Rate limiting considered

### Testing

- [ ] Manual testing completed
- [ ] QR code scanning tested on mobile
- [ ] Multi-user synchronization tested
- [ ] Performance tested with multiple matches
- [ ] Browser compatibility tested

---

## Production Configuration

### Environment Variables

Create a `.env` file for local development (DO NOT commit):

```bash
# Storage Configuration
STORAGE_PATH=data/storage.json
STORAGE_TYPE=json

# Application Settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true

# Security (optional)
STREAMLIT_SERVER_ENABLE_CORS=false
STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true
```

### Update `config.py` for Production

```python
import os
from pathlib import Path

class Config:
    """Application configuration constants."""
    
    # Determine if running in production
    IS_PRODUCTION = os.getenv('ENVIRONMENT', 'development') == 'production'
    
    # Storage Configuration
    if IS_PRODUCTION:
        # Use absolute path in production
        STORAGE_PATH = os.getenv('STORAGE_PATH', '/app/data/storage.json')
    else:
        # Use relative path in development
        STORAGE_PATH = os.getenv('STORAGE_PATH', 'data/storage.json')
    
    STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'json')
    
    # Ensure storage directory exists
    storage_dir = Path(STORAGE_PATH).parent
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    # Timer Configuration
    MATCH_DURATION_SECONDS = 5400
    TIMER_UPDATE_INTERVAL = 1.0
    TIMER_ACCURACY_THRESHOLD = 2
    
    # UI Theme
    PRIMARY_COLOR = '#2e7d32'
    SECONDARY_COLOR = '#c8e6c9'
    BACKGROUND_COLOR = '#e8f5e9'
    TEXT_COLOR = '#1b5e20'
    
    # QR Code Configuration
    QR_BOX_SIZE = 10
    QR_BORDER = 4
    QR_ERROR_CORRECTION = 'L'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
```

### Add Logging

Create `src/logger.py`:

```python
import logging
import sys
from config import Config

def setup_logger(name: str) -> logging.Logger:
    """Set up logger with appropriate configuration."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    return logger
```

---

## Security Considerations

### 1. Data Storage

**Current:** JSON file storage  
**Recommendation for Production:**

- Use PostgreSQL or MongoDB for multi-instance deployments
- Implement database backups
- Use connection pooling
- Encrypt sensitive data at rest

### 2. Session Management

**Current:** Streamlit session state  
**Considerations:**

- Sessions are per-browser
- No authentication required (by design)
- User IDs are generated client-side

**Recommendations:**
- For production, consider adding optional authentication
- Implement session timeout
- Add rate limiting to prevent abuse

### 3. Input Validation

**Already Implemented:**
- ✅ UUID format validation
- ✅ Match description length limits
- ✅ QR code validation

**Additional Recommendations:**
- Add rate limiting on match creation
- Implement CAPTCHA for public deployments
- Monitor for abuse patterns

### 4. HTTPS

**Critical for Production:**
- Always use HTTPS in production
- QR code scanning requires HTTPS on most mobile browsers
- Use Let's Encrypt for free SSL certificates

### 5. CORS Configuration

For production, configure CORS properly:

```python
# In .streamlit/config.toml
[server]
enableCORS = false
enableXsrfProtection = true
```

---

## Monitoring and Maintenance

### Health Checks

Add a health check endpoint (for platforms that support it):

```python
# Add to app.py
def health_check():
    """Simple health check for monitoring."""
    try:
        # Check storage is accessible
        storage_manager = StorageManager()
        storage_manager.list_all_matches()
        return True
    except Exception:
        return False
```

### Logging

Monitor these key metrics:
- Match creation rate
- Active matches count
- Storage file size
- Error rates
- Response times

### Backup Strategy

**For JSON storage:**

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
cp data/storage.json backups/storage_$DATE.json

# Keep only last 30 days
find backups/ -name "storage_*.json" -mtime +30 -delete
```

**For database storage:**
- Use automated database backups
- Test restore procedures regularly
- Keep backups in different region/zone

### Updates and Maintenance

1. **Monitor dependencies:**
   ```bash
   pip list --outdated
   ```

2. **Update regularly:**
   ```bash
   pip install --upgrade streamlit qrcode
   ```

3. **Test after updates:**
   ```bash
   pytest tests/
   ```

4. **Deploy updates:**
   - For Streamlit Cloud: `git push` (auto-deploys)
   - For Heroku: `git push heroku main`
   - For others: Follow platform-specific process

---

## Troubleshooting

### Common Issues

#### 1. QR Scanner Not Working

**Symptoms:** Camera doesn't open, scanner shows error

**Solutions:**
- Ensure HTTPS is enabled (required for camera access)
- Check browser permissions for camera
- Test on different browsers (Chrome, Safari)
- Verify `streamlit-qrcode-scanner` is installed
- Fallback to manual UUID entry

#### 2. Timer Not Synchronizing

**Symptoms:** Different users see different times

**Solutions:**
- Check storage is being updated correctly
- Verify `update_timer_display()` is called
- Check system time on server
- Ensure `st.rerun()` is working
- Check for storage file locking issues

#### 3. Storage File Errors

**Symptoms:** "Permission denied", "File not found"

**Solutions:**
- Check file permissions: `chmod 644 data/storage.json`
- Ensure directory exists: `mkdir -p data`
- Check disk space: `df -h`
- Verify STORAGE_PATH environment variable
- Check for file locking conflicts

#### 4. High Memory Usage

**Symptoms:** App crashes, slow performance

**Solutions:**
- Limit number of active matches
- Implement match cleanup (delete old matches)
- Optimize storage queries
- Increase server memory
- Consider database instead of JSON

#### 5. Deployment Fails

**Symptoms:** Build errors, deployment errors

**Solutions:**
- Check `requirements.txt` is complete
- Verify Python version compatibility
- Check logs for specific errors
- Ensure all files are committed
- Test locally with Docker first

### Debug Mode

Enable debug logging:

```python
# In config.py
LOG_LEVEL = 'DEBUG'

# In app.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

- **Streamlit Community:** [discuss.streamlit.io](https://discuss.streamlit.io)
- **GitHub Issues:** Create issue in your repository
- **Stack Overflow:** Tag with `streamlit` and `python`

---

## Performance Optimization

### For High Traffic

1. **Use Database Instead of JSON:**
   - PostgreSQL for relational data
   - Redis for session management
   - MongoDB for document storage

2. **Implement Caching:**
   ```python
   @st.cache_data(ttl=60)
   def get_active_matches(user_id):
       # Cache for 60 seconds
       pass
   ```

3. **Optimize Timer Updates:**
   - Reduce update frequency for spectators
   - Use WebSocket for real-time updates
   - Implement server-side timer calculation

4. **Load Balancing:**
   - Deploy multiple instances
   - Use load balancer (AWS ALB, Nginx)
   - Implement sticky sessions

---

## Cost Estimates

### Monthly Costs by Platform

| Platform | Free Tier | Paid Tier | High Traffic |
|----------|-----------|-----------|--------------|
| Streamlit Cloud | Free | $20/mo | $200/mo |
| Heroku | $0 (limited) | $7-25/mo | $50-250/mo |
| AWS EC2 | $0 (12 months) | $10-30/mo | $100-500/mo |
| Google Cloud Run | $0 (limited) | $5-20/mo | $50-200/mo |
| Railway | $0 (limited) | $5-20/mo | $50-150/mo |

### Cost Optimization Tips

- Start with free tier
- Monitor usage and scale as needed
- Use auto-scaling to handle traffic spikes
- Implement caching to reduce compute
- Clean up old/inactive matches

---

## Recommended Deployment Path

### For Development/Demo
1. **Start with Streamlit Cloud** (free, easy)
2. Test all features
3. Share with stakeholders

### For Production (Small Scale)
1. **Use Railway or Heroku** ($5-25/mo)
2. Add custom domain
3. Enable HTTPS
4. Set up monitoring

### For Production (Large Scale)
1. **Use AWS EC2 or Google Cloud Run**
2. Implement database (PostgreSQL)
3. Add load balancing
4. Set up CI/CD pipeline
5. Implement comprehensive monitoring

---

## Next Steps

1. ✅ Choose deployment platform
2. ✅ Complete pre-deployment checklist
3. ✅ Configure production settings
4. ✅ Deploy to staging environment
5. ✅ Complete manual testing
6. ✅ Deploy to production
7. ✅ Monitor and maintain

---

## Support and Resources

### Documentation
- [Streamlit Deployment Docs](https://docs.streamlit.io/streamlit-community-cloud/get-started)
- [Heroku Python Guide](https://devcenter.heroku.com/articles/getting-started-with-python)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [Google Cloud Run Docs](https://cloud.google.com/run/docs)

### Community
- [Streamlit Forum](https://discuss.streamlit.io)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/streamlit)
- [GitHub Discussions](https://github.com/streamlit/streamlit/discussions)

---

**Document Version:** 1.0  
**Last Updated:** February 25, 2026  
**Maintained By:** Development Team
