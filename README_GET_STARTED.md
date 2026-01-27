# Getting Started with Cloudflare Tunnel

## Quick installation and first run

---

## 🚀 **5-Minute Setup**

### Step 1: Install Cloudflare Tunnel (2 min)

Open **PowerShell as Administrator** and run:

```powershell
winget install cloudflare.cloudflared
```

**Alternative (if winget doesn't work):**
1. Go to: https://github.com/cloudflare/cloudflared/releases/latest
2. Download: `cloudflared-windows-amd64.msi`
3. Double-click to install

---

### Step 2: Login to Cloudflare (1 min)

```bash
cloudflared tunnel login
```

This will:
- Open a browser
- Ask you to login to Cloudflare
- Authorize the tunnel
- Create a certificate

**Expected output:**
```
Opening browser...
Please open the following URL and log in:
https://dash.cloudflare.com/argotunnel

Successfully authenticated!
```

---

### Step 3: Start Your Backend APIs (2 min)

Open **3 separate Command Prompt or PowerShell windows** and run:

**Window 1:**
```bash
cd C:\Users\Najma-LP\Desktop\Course-Companion-FTE\backend
python simple_r2_api.py
```

**Window 2:**
```bash
cd C:\Users\Najma-LP\Desktop\Course-Companion-FTE\backend
python simple_quiz_api.py
```

**Window 3:**
```bash
cd C:\Users\Najma-LP\Desktop\Course-Companion-FTE\backend
python simple_progress_api.py
```

Leave all 3 windows running.

---

### Step 4: Create Tunnels (5 min)

Open **3 MORE Command Prompt windows** (one for each tunnel):

**Window 4:**
```bash
cloudflared tunnel --url http://localhost:8000
```

You'll see output like:
```
2026-01-27T00:00:00Z INF Starting tunnel
...
https://abc123def456.trycloudflare.com -> http://localhost:8000
```

**Copy this URL!** This is your **Content API URL**.

**Window 5:**
```bash
cloudflared tunnel --url http://localhost:8001
```

You'll get another URL:
```
https://xyz789abc123.trycloudflare.com -> http://localhost:8001
```

**Copy this URL!** This is your **Quiz API URL**.

**Window 6:**
```bash
cloudflared tunnel --url http://localhost:8002
```

You'll get a third URL:
```
https://def456ghi789.trycloudflare.com -> http://localhost:8002
```

**Copy this URL!** This is your **Progress API URL**.

---

### Step 5: Test Your URLs (2 min)

Open a web browser and test:

**Test 1 - Content API:**
```
https://YOUR-CONTENT-URL.trycloudflare.com/chapters
```

**Test 2 - Quiz API:**
```
https://YOUR-QUIZ-URL.trycloudflare.com/quizzes
```

**Test 3 - Progress API:**
```
https://YOUR-PROGRESS-URL.trycloudflare.com/progress/dashboard
```

All should return JSON data (not error pages).

---

## ✅ **You're Done!**

You now have 3 persistent public URLs:

```
Content API:  https://abc123def456.trycloudflare.com
Quiz API:     https://xyz789abc123.trycloudflare.com
Progress API: https://def456ghi789.trycloudflare.com
```

These URLs:
- ✅ Never change (even if you restart)
- ✅ Have SSL certificates
- ✅ Are publically accessible
- ✅ Work with ChatGPT Apps
- ✅ Are production-ready
- ✅ Are free forever

---

## 🎯 **Next: Use in ChatGPT App**

1. Go to: https://platform.openai.com/apps
2. Create or edit your app
3. In "Capabilities" → "Actions", add 3 APIs:

**API 1:**
- Name: Content API
- Base URL: `https://YOUR-CONTENT-URL.trycloudflare.com`

**API 2:**
- Name: Quiz API
- Base URL: `https://YOUR-QUIZ-URL.trycloudflare.com`

**API 3:**
- Name: Progress API
- Base URL: `https://YOUR-PROGRESS-URL.trycloudflare.com`

4. Save and test your app!

---

## 🔄 **Restarting Tunnels**

If you need to restart (e.g., after computer restart):

1. Start your 3 backend APIs (Windows 1-3)
2. Run the 3 cloudflared commands (Windows 4-6)
3. **Your URLs will be the same!**

---

## 🛑 **Stopping Tunnels**

When you're done:

1. Close the 6 terminal windows
2. Or press Ctrl+C in each window
3. Tunnels will stop

---

## 📚 **Full Documentation**

For more details, see:
- `CLOUDFLARE_TUNNEL_SETUP.md` - Complete guide
- `CLOUDFLARE_TUNNEL_QUICKSTART.md` - Quick reference
- `CLOUDFLARE_TUNNEL_COMPLETE.md` - Overview
- `Start-Tunnels.ps1` - Automated launcher
- `Stop-Tunnels.ps1` - Automated stopper

---

## ⏱️ **Time Estimate**

| Task | Time |
|------|------|
| Install cloudflared | 2 min |
| Login to Cloudflare | 1 min |
| Start 3 backend APIs | 2 min |
| Create 3 tunnels | 5 min |
| Test URLs | 2 min |
| **Total** | **12 min** |

---

## 🎓 **Need Help?**

**Common Issues:**

**Q: "cloudflared command not found"**
A: Make sure you installed it and restarted your terminal

**Q: "Tunnel not accessible"**
A: Check your firewall and make sure backend APIs are running

**Q: "How do I know if it's working?"**
A: Test the URLs in your browser - should return JSON

**Q: "Can I use the same URL tomorrow?"**
A: Yes! That's the beauty of Cloudflare Tunnel - URLs persist

---

**You're 12 minutes away from having production-ready URLs for all your APIs!**
