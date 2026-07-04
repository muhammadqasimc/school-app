# Cloudflare Setup Guide for Kismet Reporting App

This guide will walk you through deploying your Flask application to your domain using Cloudflare.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Preparing Your Flask App for Production](#preparing-your-flask-app-for-production)
3. [Option 1: Cloudflare Tunnel (Recommended)](#option-1-cloudflare-tunnel-recommended)
4. [Option 2: Reverse Proxy with Nginx](#option-2-reverse-proxy-with-nginx)
5. [Cloudflare DNS Configuration](#cloudflare-dns-configuration)
6. [SSL/TLS Configuration](#ssltls-configuration)
7. [Security Settings](#security-settings)
8. [Performance Optimization](#performance-optimization)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:
- ✅ A domain name (e.g., `yourschool.com`)
- ✅ Cloudflare account (free tier works)
- ✅ A server/VPS to host your Flask app (Windows Server, Linux VPS, or local machine)
- ✅ Python 3.8+ installed on your server
- ✅ Your Flask app working locally

---

## Preparing Your Flask App for Production

### 1. Update Production Settings

Create a `.env` file for production (if not already exists):

```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here-change-this
MDB_FILE_PATH=path/to/your/database.mdb
MDB_PASSWORD=your-mdb-password
```

### 2. Install Production Dependencies

```bash
pip install gunicorn  # For Linux/Mac
# OR
pip install waitress  # For Windows
```

### 3. Update app.py for Production

Modify the `if __name__ == '__main__'` section:

**For Linux/Mac:**
```python
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables checked/created successfully")
    
    # Production: Use gunicorn instead
    # Run with: gunicorn -w 4 -b 0.0.0.0:5000 app:app
    app.run(debug=False, host='0.0.0.0', port=5000)
```

**For Windows:**
```python
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables checked/created successfully")
    
    # Production: Use waitress
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)
```

### 4. Create Production Startup Script

**Windows (start_production.bat):**
```batch
@echo off
cd /d "C:\Users\Muhammad Cassim\Documents\Reporting_app"
python -m waitress --host=0.0.0.0 --port=5000 app:app
```

**Linux/Mac (start_production.sh):**
```bash
#!/bin/bash
cd /path/to/your/app
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app
```

---

## Option 1: Cloudflare Tunnel (Recommended)

Cloudflare Tunnel (formerly Argo Tunnel) is the easiest way to expose your local app without opening ports.

### Step 1: Install cloudflared

**Windows:**
1. Download from: https://github.com/cloudflare/cloudflared/releases
2. Extract `cloudflared.exe` to your app directory
3. Or use Chocolatey: `choco install cloudflared`

**Linux:**
```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/
```

### Step 2: Login to Cloudflare

```bash
cloudflared tunnel login
```

This will open a browser window. Select your domain and authorize.

### Step 3: Create a Tunnel

```bash
cloudflared tunnel create kismet-app
```

Note the Tunnel ID that's displayed.

### Step 4: Create Configuration File

Create `config.yml` in `.cloudflared` folder:

**Windows:** `C:\Users\<YourUser>\.cloudflared\config.yml`
**Linux:** `~/.cloudflared/config.yml`

```yaml
tunnel: <your-tunnel-id>
credentials-file: C:\Users\<YourUser>\.cloudflared\<tunnel-id>.json

ingress:
  - hostname: app.yourschool.com
    service: http://localhost:5000
  - service: http_status:404
```

Replace:
- `<your-tunnel-id>` with the ID from Step 3
- `app.yourschool.com` with your subdomain
- Update the credentials-file path

### Step 5: Run the Tunnel

```bash
cloudflared tunnel run kismet-app
```

### Step 6: Run as Windows Service (Optional)

**Install as service:**
```bash
cloudflared tunnel service install
cloudflared service start
```

**Or create a scheduled task:**
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: "When the computer starts"
4. Action: Start a program
5. Program: `C:\path\to\cloudflared.exe`
6. Arguments: `tunnel run kismet-app`

---

## Option 2: Reverse Proxy with Nginx

If you prefer a traditional reverse proxy setup:

### Step 1: Install Nginx

**Windows:**
- Download from: http://nginx.org/en/download.html
- Or use: `choco install nginx`

**Linux:**
```bash
sudo apt update
sudo apt install nginx
```

### Step 2: Configure Nginx

Edit `/etc/nginx/sites-available/kismet-app` (Linux) or `nginx.conf` (Windows):

```nginx
server {
    listen 80;
    server_name app.yourschool.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**Linux:**
```bash
sudo ln -s /etc/nginx/sites-available/kismet-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 3: Configure Firewall

**Windows:**
- Allow port 80 and 443 in Windows Firewall

**Linux:**
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

---

## Cloudflare DNS Configuration

### Step 1: Add Your Domain to Cloudflare

1. Log in to Cloudflare dashboard
2. Click "Add a Site"
3. Enter your domain
4. Select plan (Free tier works)
5. Follow DNS setup instructions

### Step 2: Configure DNS Records

**For Cloudflare Tunnel:**
- Type: `CNAME`
- Name: `app` (or `@` for root domain)
- Target: `<your-tunnel-id>.cfargotunnel.com`
- Proxy status: Proxied (orange cloud)

**For Nginx/Reverse Proxy:**
- Type: `A`
- Name: `app` (or `@` for root domain)
- IPv4 address: Your server's public IP
- Proxy status: Proxied (orange cloud)

### Step 3: Verify DNS Propagation

Wait 5-10 minutes, then check:
```bash
nslookup app.yourschool.com
```

---

## SSL/TLS Configuration

### Automatic HTTPS (Recommended)

Cloudflare automatically provides SSL when:
- DNS records are proxied (orange cloud)
- SSL/TLS mode is set to "Full" or "Full (strict)"

### Configure SSL Mode

1. Go to Cloudflare Dashboard
2. Select your domain
3. Go to **SSL/TLS**
4. Set encryption mode to **Full**
5. Enable **Always Use HTTPS**

### SSL Certificate (For Full Strict Mode)

If using Full Strict, you need an SSL certificate on your server:

**Using Let's Encrypt (Linux):**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d app.yourschool.com
```

**Using Cloudflare Origin Certificate (Recommended):**
1. Cloudflare Dashboard → SSL/TLS → Origin Server
2. Click "Create Certificate"
3. Download certificate and key
4. Update Nginx config to use these certificates

---

## Security Settings

### 1. Firewall Rules

Create firewall rules in Cloudflare:
- **Dashboard → Security → WAF**
- Block known bad IPs
- Rate limiting for login attempts

### 2. Access Rules

**Dashboard → Security → WAF → Tools:**
- Rate Limiting: 100 requests per minute per IP
- Challenge: CAPTCHA for suspicious traffic

### 3. Application Security

Update your Flask app:

```python
# Add to app.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # Your login code
    pass
```

### 4. Environment Variables

Never commit `.env` file. Use environment variables:
- `SECRET_KEY` - Flask secret key
- `MDB_PASSWORD` - Database password
- `ADMIN_PASSWORD` - Change from default

---

## Performance Optimization

### 1. Caching

**Cloudflare Dashboard → Caching:**
- Caching Level: Standard
- Browser Cache TTL: 4 hours
- Enable Auto Minify (HTML, CSS, JS)

### 2. Speed Settings

**Dashboard → Speed:**
- Enable Auto Minify
- Enable Brotli compression
- Enable HTTP/2
- Enable HTTP/3 (with QUIC)

### 3. Flask App Optimization

```python
# Add caching headers
@app.after_request
def after_request(response):
    # Don't cache dynamic pages
    if request.path.startswith('/api/') or request.path.startswith('/dashboard'):
        response.cache_control.no_cache = True
    else:
        response.cache_control.max_age = 3600
    return response
```

### 4. Database Optimization

- Use connection pooling
- Index frequently queried fields
- Regular database maintenance

---

## Troubleshooting

### Issue: "502 Bad Gateway"

**Causes:**
- Flask app not running
- Wrong port number
- Firewall blocking connection

**Solutions:**
1. Check if Flask app is running: `netstat -an | findstr 5000`
2. Verify port in Cloudflare Tunnel config
3. Check firewall settings

### Issue: "SSL Certificate Error"

**Solutions:**
1. Set SSL mode to "Full" (not Full Strict) initially
2. Verify origin certificate is installed correctly
3. Check certificate expiration

### Issue: "Too Many Redirects"

**Solutions:**
1. Disable "Always Use HTTPS" temporarily
2. Check Nginx/Cloudflare Tunnel config
3. Verify proxy settings

### Issue: "Connection Timeout"

**Solutions:**
1. Check if server is accessible
2. Verify DNS records point to correct IP
3. Check Cloudflare Tunnel status: `cloudflared tunnel list`

### Debugging Commands

```bash
# Check Cloudflare Tunnel status
cloudflared tunnel list
cloudflared tunnel info kismet-app

# Test local Flask app
curl http://localhost:5000

# Check Nginx status
sudo systemctl status nginx
sudo nginx -t

# View logs
# Windows: Check Event Viewer
# Linux: sudo tail -f /var/log/nginx/error.log
```

---

## Quick Start Checklist

- [ ] Domain added to Cloudflare
- [ ] DNS records configured
- [ ] SSL/TLS mode set to "Full"
- [ ] Cloudflare Tunnel installed and configured (OR Nginx configured)
- [ ] Flask app running on localhost:5000
- [ ] Firewall ports opened (if using Nginx)
- [ ] Test access: `https://app.yourschool.com`
- [ ] Security settings configured
- [ ] Performance optimizations enabled
- [ ] Monitoring set up

---

## Additional Resources

- [Cloudflare Tunnel Documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Nginx Configuration Guide](https://nginx.org/en/docs/)

---

## Support

If you encounter issues:
1. Check Cloudflare Dashboard for errors
2. Review server logs
3. Verify DNS propagation
4. Test local Flask app independently

---

**Last Updated:** 2026-02-17
**App Version:** 1.0
