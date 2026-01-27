# Cloudflare Tunnel - Quick Start

## Fastest path to get your APIs online (15 minutes)

---

## Step 1: Install cloudflared (2 min)

```powershell
# Run PowerShell as Administrator
winget install cloudflare.cloudflared
```

**Or download directly:**
- Go to: https://github.com/cloudflare/cloudflared/releases/latest
- Download: `cloudflared-windows-amd64.msi`
- Install with default options

---

## Step 2: Login to Cloudflare (1 min)

```bash
cloudflared tunnel login
```

This opens a browser window. Login to Cloudflare and authorize.

---

## Step 3: Start Your Backend APIs (3 min)

Open 3 separate terminals and run:

```bash
# Terminal 1
cd C:\Users\Najma-LP\Desktop\Course-Companion-FTE\backend
python simple_r2_api.py

# Terminal 2
cd C:\Users\Najma-LP\Desktop\Course-Companion-FTE\backend
python simple_quiz_api.py

# Terminal 3
cd C:\Users\Najma-LP\Desktop\Course-Companion-FTE\backend
python simple_progress_api.py
```

---

## Step 4: Create Tunnels - Quick Method (5 min)

For each API, open a NEW terminal and run:

### Tunnel 1: Content API
```bash
cloudflared tunnel --url http://localhost:8000
```

**Output:**
```
https://abc123-def456-ghi789.trycloudflare.com -> http://localhost:8000
```

**Copy this URL!** This is your Content API URL.

### Tunnel 2: Quiz API
```bash
cloudflared tunnel --url http://localhost:8001
```

**Output:**
```
https://xyz789-abc123-def456.trycloudflare.com -> http://localhost:8001
```

**Copy this URL!** This is your Quiz API URL.

### Tunnel 3: Progress API
```bash
cloudflared tunnel --url http://localhost:8002
```

**Output:**
```
https://def456-ghi789-abc123.trycloudflare.com -> http://localhost:8002
```

**Copy this URL!** This is your Progress API URL.

---

## Step 5: Test Your URLs (2 min)

Open a browser and test:

```bash
# Test Content API
https://YOUR-CONTENT-URL.trycloudflare.com/chapters

# Test Quiz API
https://YOUR-QUIZ-URL.trycloudflare.com/quizzes

# Test Progress API
https://YOUR-PROGRESS-URL.trycloudflare.com/progress/dashboard
```

All should return JSON responses.

---

## Step 6: Use in ChatGPT App (2 min)

In OpenAI dashboard, when configuring your app:

**API 1: Content API**
```
Name: Course Content
Base URL: https://YOUR-CONTENT-URL.trycloudflare.com
```

**API 2: Quiz API**
```
Name: Quiz System
Base URL: https://YOUR-QUIZ-URL.trycloudflare.com
```

**API 3: Progress API**
```
Name: Progress Tracker
Base URL: https://YOUR-PROGRESS-URL.trycloudflare.com
```

---

## That's It!

✅ Your 3 APIs are now publicly accessible
✅ URLs are persistent (won't change on restart)
✅ SSL included automatically
✅ Professional `.trycloudflare.com` domains
✅ Perfect for ChatGPT App integration

---

## Want Better URLs? (Optional)

If you want custom subdomains like:
- `content.yourdomain.com`
- `quiz.yourdomain.com`
- `progress.yourdomain.com`

See: `CLOUDFLARE_TUNNEL_SETUP.md` (Advanced Configuration)

---

## Summary

**Time: 15 minutes**

**Result:** 3 persistent, production-ready URLs

**Next:** Use these URLs in your ChatGPT App configuration!
