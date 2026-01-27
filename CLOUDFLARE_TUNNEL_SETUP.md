# Cloudflare Tunnel Setup Guide

## Best option for your Course Companion FTE (content already on R2!)

---

## Why Cloudflare Tunnel?

✅ **Perfect for R2 Integration**
- Same ecosystem (Cloudflare)
- No additional account needed
- Fast edge routing

✅ **Free & Fast**
- No bandwidth limits
- No cold starts
- Global edge network

✅ **Persistent URLs**
- URLs don't change on restart
- Professional domain names
- SSL certificates included

✅ **Easy Setup**
- No credit card required
- Quick configuration
- Works with localhost

---

## Step 1: Install Cloudflare Tunnel (cloudflared)

### Windows (Recommended for you)

```bash
# Option 1: Download directly
# Go to: https://github.com/cloudflare/cloudflared/releases
# Download: cloudflared-windows-amd64.exe
# Rename to: cloudflared.exe
# Place in: C:\Windows\System32

# Option 2: Using PowerShell (Admin)
# Run PowerShell as Administrator
winget install cloudflare.cloudflared

# Option 3: Using Chocolate Install
choco install cloudflared
```

### Verify Installation

```bash
# Check if installed
cloudflared --version

# You should see version info
```

---

## Step 2: Authenticate Cloudflare

```bash
# Login to Cloudflare
cloudflared tunnel login

# This will:
# 1. Open a browser
# 2. Ask you to login to Cloudflare
# 3. Ask you to grant permissions
# 4. Create a certificate file
```

**Expected output:**
```
Opening browser...
Please open the following URL and log in:
https://dash.cloudflare.com/argotunnel

Successfully authenticated!
```

---

## Step 3: Create Tunnels

You'll need 3 tunnels (one for each API). But first, let me show you a better approach...

### Better Approach: Single Tunnel with Multiple Routes

Instead of 3 separate tunnels, we'll use **one tunnel** that routes all 3 APIs!

```bash
# Create a tunnel for Course Companion FTE
cloudflared tunnel create course-companion-fte

# You'll get a tunnel UUID like:
# Your tunnel ID is: abc123-def456-ghi789
# Save this ID!
```

---

## Step 4: Configure Tunnel

Create a configuration file: `C:\Users\Najma-LP\Desktop\Course-Companion-FTE\backend\config.yml`

```yaml
# Cloudflare Tunnel Configuration for Course Companion FTE

tunnel: <YOUR_TUNNEL_ID>  # Replace with your tunnel ID from Step 3
credentials-file: C:\Users\<YOUR_USERNAME>\.cloudflared\<YOUR_TUNNEL_ID>.json

# Service configuration
ingress:
  # Content API (port 8000)
  - hostname: content.your-domain.com  # Optional: custom domain
    service: http://localhost:8000
  - hostname: api.your-domain.com
    path: /content/*
    service: http://localhost:8000

  # Quiz API (port 8001)
  - hostname: api.your-domain.com
    path: /quizzes/*
    service: http://localhost:8001

  # Progress API (port 8002)
  - hostname: api.your-domain.com
    path: /progress/*
    service: http://localhost:8002

  # Fallback for local testing
  - hostname: trycloudflare.com
    service: http://localhost:8000

  # Catch-all rule (must be last)
  - service: http_status:404

# Don't change this
originRequest:
  noTLSVerify: true
```

### Simpler Configuration (for quick start)

Create: `backend\cloudflare-tunnel-config.yml`

```yaml
tunnel: <YOUR_TUNNEL_ID>
credentials-file: C:\Users\<YOUR_USERNAME>\.cloudflared\<YOUR_TUNNEL_ID>.json

ingress:
  # Content API - Use trycloudflare.com subdomain
  - hostname: content-course-companion-fte.trycloudflare.com
    service: http://localhost:8000

  # Quiz API
  - hostname: quiz-course-companion-fte.trycloudflare.com
    service: http://localhost:8001

  # Progress API
  - hostname: progress-course-companion-fte.trycloudflare.com
    service: http://localhost:8002

  # Catch-all (must be last)
  - service: http_status:404

originRequest:
  noTLSVerify: true
```

---

## Step 5: Start Your Backend APIs

Open 3 separate terminals:

```bash
# Terminal 1: Content API
cd C:\Users\Najma-LP\Desktop\Course-Companion-FTE\backend
python simple_r2_api.py

# Terminal 2: Quiz API
cd C:\Users\Najma-LP\Desktop\Course-Companion-FTE\backend
python simple_quiz_api.py

# Terminal 3: Progress API
cd C:\Users\Najma-LP\Desktop\Course-Companion-FTE\backend
python simple_progress_api.py
```

---

## Step 6: Start Cloudflare Tunnel

```bash
# Navigate to backend directory
cd C:\Users\Najma-LP\Desktop\Course-Companion-FTE\backend

# Start tunnel with config
cloudflared tunnel --config cloudflare-tunnel-config.yml run

# Or simply (if no config):
cloudflared tunnel run <YOUR_TUNNEL_ID>
```

**Expected output:**
```
2026-01-27T00:00:00Z INF Starting tunnel tunnelID=<YOUR_TUNNEL_ID>
2026-01-27T00:00:00Z INF Version 2024.x.x
2026-01-27T00:00:00Z INF Generated https://content-course-companion-fte.trycloudflare.com
2026-01-27T00:00:01Z INF https://content-course-companion-fte.trycloudflare.com is running
```

---

## Step 7: Get Your Public URLs

Cloudflare will generate URLs like:

```
Content API: https://content-course-companion-fte.trycloudflare.com
Quiz API: https://quiz-course-companion-fte.trycloudflare.com
Progress API: https://progress-course-companion-fte.trycloudflare.com
```

Or if using subdomain paths:

```
All APIs: https://api-course-companion-fte.trycloudflare.com
- /content/* → localhost:8000
- /quizzes/* → localhost:8001
- /progress/* → localhost:8002
```

---

## Step 8: Test Your Tunnels

Open a browser and test each:

```bash
# Test Content API
https://content-course-companion-fte.trycloudflare.com/chapters

# Test Quiz API
https://quiz-course-companion-fte.trycloudflare.com/quizzes

# Test Progress API
https://progress-course-companion-fte.trycloudflare.com/progress/dashboard
```

All should return JSON responses.

---

## Alternative: Quick Quickstart (No Config File)

If you want to skip the config file:

### For Individual APIs (3 separate tunnels)

```bash
# Tunnel 1: Content API
cloudflared tunnel --url http://localhost:8000

# Tunnel 2: Quiz API
cloudflared tunnel --url http://localhost:8001

# Tunnel 3: Progress API
cloudflared tunnel --url http://localhost:8002
```

Each will give you a temporary `.trycloudflare.com` URL.

**Example output:**
```
https://random-words.trycloudflare.com → http://localhost:8000
```

Copy these URLs for your ChatGPT App configuration.

---

## Step 9: Update ChatGPT App Configuration

Once you have your Cloudflare URLs, update your ChatGPT App:

### Option A: Separate URLs

```
Content API Base URL: https://content-course-companion-fte.trycloudflare.com
Quiz API Base URL: https://quiz-course-companion-fte.trycloudflare.com
Progress API Base URL: https://progress-course-companion-fte.trycloudflare.com
```

### Option B: Single Domain with Paths

```
API Base URL: https://api-course-companion-fte.trycloudflare.com

Content endpoints: /content/*
Quiz endpoints: /quizzes/*
Progress endpoints: /progress/*
```

---

## Step 10: Make Tunnel Persistent (Optional but Recommended)

### Install as Windows Service (runs on startup)

```bash
# Run as Administrator
cloudflared service install

# Configure service
cloudflared-service.exe configure --tunnel <YOUR_TUNNEL_ID> --config cloudflare-tunnel-config.yml

# Start service
net start cloudflared

# Check status
sc query cloudflared
```

Now your tunnel starts automatically when Windows boots!

---

## Troubleshooting

### Problem: "cloudflared not recognized"

**Solution:**
```bash
# Make sure it's in your PATH
where cloudflared

# Or use full path
C:\Program Files\cloudflared\cloudflared.exe --version
```

### Problem: "Tunnel not accessible"

**Solutions:**
1. Check firewall settings (allow port 80/443)
2. Verify Cloudflare DNS is propagating
3. Check tunnel is running: `cloudflared tunnel info <YOUR_TUNNEL_ID>`

### Problem: "Localhost connection refused"

**Solutions:**
1. Make sure your backend APIs are running
2. Check they're listening on the right ports (8000, 8001, 8002)
3. Try `127.0.0.1` instead of `localhost`

### Problem: "CORS errors"

**Solution:**
Your FastAPI apps should have CORS enabled:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify "https://chat.openai.com"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Quick Reference Commands

```bash
# Login
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create course-companion-fte

# List tunnels
cloudflared tunnel list

# Start tunnel
cloudflared tunnel run <TUNNEL_ID>

# Start with config
cloudflared tunnel --config cloudflare-tunnel-config.yml run

# Stop tunnel
Ctrl+C

# Delete tunnel
cloudflared tunnel delete <TUNNEL_ID>

# Tunnel info
cloudflared tunnel info <TUNNEL_ID>
```

---

## Benefits of Cloudflare Tunnel

| Feature | Cloudflare Tunnel | ngrok |
|---------|-------------------|-------|
| Cost | Free | Free (limited) |
| URL Stability | Persistent | Changes on restart |
| SSL | Included | Included |
| Performance | Fast (Edge) | Good |
| Setup | Easy | Easy |
| Custom Domain | Yes | Paid only |
| Account Required | Cloudflare | ngrok.com |
| Best For | Production | Quick Testing |

---

## Summary

**What you'll have:**

✅ **3 Public URLs** (persistent)
```
https://content-course-companion-fte.trycloudflare.com
https://quiz-course-companion-fte.trycloudflare.com
https://progress-course-companion-fte.trycloudflare.com
```

✅ **Persistent connection**
- URLs never change
- Runs continuously
- Auto-starts (if installed as service)

✅ **Production ready**
- Professional domains
- SSL certificates
- Edge performance
- DDoS protection

✅ **Perfect for R2**
- Same Cloudflare ecosystem
- Fast R2 access
- Optimized routing

---

## Next Steps

1. ✅ Install cloudflared
2. ✅ Authenticate: `cloudflared tunnel login`
3. ✅ Create tunnel: `cloudflared tunnel create course-companion-fte`
4. ✅ Start backends (3 terminals)
5. ✅ Start tunnel: `cloudflared tunnel run <TUNNEL_ID>`
6. ✅ Copy the generated URLs
7. ✅ Use in ChatGPT App configuration

---

**Time to complete: 15 minutes**

**You'll get persistent, production-ready URLs for all your APIs!**
