# Cloudflare Tunnel Setup - Complete Guide Package

## Everything you need to get your APIs online with Cloudflare!

---

## 📚 **Documentation Files Created**

### 1. **CLOUDFLARE_TUNNEL_SETUP.md** (Detailed Guide)
Comprehensive guide with:
- Why Cloudflare Tunnel is the best option
- Complete installation instructions
- Configuration options
- Windows service setup
- Troubleshooting
- All features and options

### 2. **CLOUDFLARE_TUNNEL_QUICKSTART.md** (Fastest Method)
15-minute quick start:
- Install cloudflared
- Login to Cloudflare
- Start 3 backend APIs
- Create 3 tunnels (quick method)
- Copy URLs
- Test

### 3. **Start-Tunnels.ps1** (PowerShell Script)
Automated launcher:
- Checks installation
- Checks if APIs are running
- Starts all 3 tunnels
- Extracts URLs automatically
- Shows them clearly

### 4. **Stop-Tunnels.ps1** (Cleanup Script)
Simple script to stop all tunnels

---

## 🚀 **Quick Start (3 Options)**

### **Option A: Fully Automated (Recommended)** ⭐

```powershell
# 1. Install cloudflared (one time)
winget install cloudflare.cloudflared

# 2. Login to Cloudflare (one time)
cloudflared tunnel login

# 3. Start your 3 backend APIs (3 terminals)
python simple_r2_api.py
python simple_quiz_api.py
python simple_progress_api.py

# 4. Run the launcher script
.\Start-Tunnels.ps1

# That's it! URLs will be displayed automatically.
```

### **Option B: Semi-Automated**

```bash
# 1. Install & login
winget install cloudflare.cloudflared
cloudflared tunnel login

# 2. Start backends (3 terminals)
python simple_r2_api.py
python simple_quiz_api.py
python simple_progress_api.py

# 3. Create tunnels (3 new terminals)
cloudflared tunnel --url http://localhost:8000
cloudflared tunnel --url http://localhost:8001
cloudflared tunnel --url http://localhost:8002

# 4. Copy the URLs from output
```

### **Option C: Manual**

See: `CLOUDFLARE_TUNNEL_SETUP.md` for detailed instructions.

---

## 📋 **Step-by-Step Checklist**

### Prerequisites (One-time setup)

- [ ] Install Cloudflare Tunnel
  ```powershell
  winget install cloudflare.cloudflared
  ```

- [ ] Login to Cloudflare
  ```bash
  cloudflared tunnel login
  ```

- [ ] Verify installation
  ```bash
  cloudflared --version
  ```

### Start Your System (Each time)

- [ ] **Step 1: Start Backend APIs (3 terminals)**
  ```bash
  # Terminal 1
  cd backend
  python simple_r2_api.py

  # Terminal 2
  cd backend
  python simple_quiz_api.py

  # Terminal 3
  cd backend
  python simple_progress_api.py
  ```

- [ ] **Step 2: Start Tunnels**
  ```powershell
  # Run the PowerShell script
  .\Start-Tunnels.ps1
  ```

- [ ] **Step 3: Copy Your URLs**

  The script will display:
  ```
  Content API: https://abc123-def456.trycloudflare.com
  Quiz API:    https://xyz789-abc123.trycloudflare.com
  Progress API: https://def456-ghi789.trycloudflare.com
  ```

- [ ] **Step 4: Test in Browser**
  ```
  https://YOUR-CONTENT-URL.trycloudflare.com/chapters
  https://YOUR-QUIZ-URL.trycloudflare.com/quizzes
  https://YOUR-PROGRESS-URL.trycloudflare.com/progress/dashboard
  ```

- [ ] **Step 5: Use in ChatGPT App**
  - Open OpenAI dashboard
  - Configure your app
  - Add these URLs

---

## 🎯 **What You Get**

After completing these steps:

✅ **3 Persistent Public URLs**
- Content API: `https://xxx.trycloudflare.com`
- Quiz API: `https://yyy.trycloudflare.com`
- Progress API: `https://zzz.trycloudflare.com`

✅ **Features:**
- URLs never change on restart
- SSL certificates included
- DDoS protection
- Edge performance
- Professional domains
- Free forever

✅ **Perfect for:**
- ChatGPT App integration
- Production use
- Demo day presentation
- Long-term deployment

---

## 🔧 **Advanced Configuration (Optional)**

If you want custom domains (e.g., `api.yourdomain.com`):

1. Go to Cloudflare Dashboard
2. Add your domain to Cloudflare
3. Update tunnel configuration
4. Set up DNS records
5. Done!

See: `CLOUDFLARE_TUNNEL_SETUP.md` for details.

---

## 🛑 **How to Stop Tunnels**

### Method 1: Use the cleanup script
```powershell
.\Stop-Tunnels.ps1
```

### Method 2: Manual
- Press Ctrl+C in each tunnel window
- Or close the terminal windows

### Method 3: Kill process
```powershell
taskkill /F /IM cloudflared.exe
```

---

## 🔄 **Restarting Tunnels**

If you need to restart:

1. Stop existing tunnels (see above)
2. Start backend APIs again (if not running)
3. Run `.\Start-Tunnels.ps1` again
4. URLs will be the same!

---

## 📊 **Cloudflare Tunnel vs ngrok**

| Feature | Cloudflare Tunnel | ngrok |
|---------|-------------------|-------|
| Cost | Free | Free (limited) |
| URL Persistence | ✅ Permanent | ❌ Changes on restart |
| SSL | ✅ Included | ✅ Included |
| Speed | ✅ Fast (Edge) | ✅ Good |
| Custom Domain | ✅ Free | ❌ Paid only |
| Account | Cloudflare (free) | ngrok.com |
| Setup | ✅ Easy | ✅ Easy |
| Production Ready | ✅ Yes | ⚠️ Limited |
| Best For | **Production & Long-term** | Quick testing |

**Winner: Cloudflare Tunnel** ⭐

---

## 💡 **Tips & Tricks**

### Tip 1: Run as Windows Service
Tunnels start automatically when Windows boots!

```bash
cloudflared service install
cloudflared-service.exe configure --tunnel <TUNNEL_ID>
net start cloudflared
```

### Tip 2: Monitor Tunnel Status
```bash
cloudflared tunnel info <TUNNEL_ID>
```

### Tip 3: View Logs
```bash
# Logs are in the tunnel windows
# Or specify log file:
cloudflared tunnel --url http://localhost:8000 --loglevel debug
```

### Tip 4: Quick Health Check
```bash
# Test all APIs
curl https://YOUR-URL.trycloudflare.com/
```

---

## 🆘 **Troubleshooting**

### Problem: "cloudflared not recognized"

**Solution:**
```powershell
# Make sure it's in PATH
where cloudflared

# If not, install:
winget install cloudflare.cloudflared

# Or add to PATH manually
```

### Problem: "Tunnel not accessible"

**Solutions:**
1. Check firewall (allow port 80/443)
2. Verify APIs are running: `curl http://localhost:8000/`
3. Check Cloudflare dashboard
4. Make sure tunnel is running

### Problem: "Localhost connection refused"

**Solution:**
```powershell
# Check if APIs are running
Get-NetTCPConnection -LocalPort 8000,8001,8002 -State Listen

# Or test:
curl http://localhost:8000/
curl http://localhost:8001/
curl http://localhost:8002/
```

### Problem: "CORS errors"

**Solution:**
Your FastAPI apps need CORS enabled:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📝 **Summary**

**Time Investment:**
- One-time setup: 10 minutes
- Each session: 2 minutes

**What You Get:**
- 3 persistent public URLs
- Professional domains
- SSL certificates
- Production-ready deployment
- Perfect for ChatGPT App

**Next Steps:**
1. Install cloudflared
2. Login to Cloudflare
3. Start your backend APIs
4. Run `Start-Tunnels.ps1`
5. Copy URLs
6. Use in ChatGPT App configuration

---

## 🎉 **You're Ready!**

**Files Created:**
- `CLOUDFLARE_TUNNEL_SETUP.md` - Complete guide
- `CLOUDFLARE_TUNNEL_QUICKSTART.md` - Quick start
- `Start-Tunnels.ps1` - Launcher script
- `Stop-Tunnels.ps1` - Cleanup script

**What to Do:**
1. Install cloudflared (one time)
2. Login to Cloudflare (one time)
3. Start backends and run `Start-Tunnels.ps1`
4. Copy your URLs
5. Use them in ChatGPT App

**Time: 15 minutes**

**Result: 3 persistent, production-ready URLs for your APIs!** 🚀
