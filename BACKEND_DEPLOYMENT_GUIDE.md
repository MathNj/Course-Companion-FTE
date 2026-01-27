# Quick Backend Deployment Guide

## For ChatGPT App Integration

Your backend APIs need to be publicly accessible for the ChatGPT App to call them.

---

## Option 1: Quick Local Testing with ngrok ⭐ **FASTEST (5 min)**

### Step 1: Install ngrok

```bash
# Download from: https://ngrok.com/download
# Or use:
choco install ngrok  # Windows
brew install ngrok  # Mac
```

### Step 2: Start ngrok Tunnels

You'll need 3 separate terminals (or use background processes):

```bash
# Terminal 1: Content API
ngrok http 8000

# Terminal 2: Quiz API
ngrok http 8001

# Terminal 3: Progress API
ngrok http 8002
```

Each will give you a URL like:
```
https://abc123.ngrok.io  # Forwarding to localhost:8000
https://def456.ngrok.io  # Forwarding to localhost:8001
https://ghi789.ngrok.io  # Forwarding to localhost:8002
```

### Step 3: Update ChatGPT App Configuration

Use these ngrok URLs in your ChatGPT App:

```
Content API Base URL: https://abc123.ngrok.io
Quiz API Base URL: https://def456.ngrok.io
Progress API Base URL: https://ghi789.ngrok.io
```

### Pros & Cons
✅ Fastest (5 minutes)
✅ No deployment needed
✅ Works with localhost
❌ URLs change each restart (free tier)
❌ Not suitable for production

---

## Option 2: Deploy to Railway ⭐ **EASIEST (10 min)**

### Step 1: Create Railway Account

1. Go to: https://railway.app
2. Sign up (GitHub login works best)
3. Click **"New Project"**

### Step 2: Deploy Backend APIs

You'll need to deploy 3 separate services (or combine them):

#### Method A: Deploy All-in-One

1. Click **"Deploy from GitHub Repo"**
2. Select your repository
3. Railway will detect it's Python/FastAPI
4. Click **"Deploy"**

Railway will:
- Install dependencies from `requirements.txt`
- Start the server
- Give you a public URL like: `https://your-app.railway.app`

#### Method B: Deploy Each API Separately

Repeat for each API (content, quiz, progress) with different ports.

### Step 3: Configure Environment Variables

In Railway dashboard, add `.env` variables:

```env
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret
R2_BUCKET_NAME=generative-ai-fundamentals
R2_ENDPOINT=https://your-account.r2.cloudflarestorage.com
```

### Step 4: Update ChatGPT App

Use your Railway URL:
```
Content API: https://your-app.railway.app
Quiz API: https://your-app.railway.app/quizzes
Progress API: https://your-app.railway.app/progress
```

### Pros & Cons
✅ Easy deployment
✅ Free tier available
✅ Persistent URLs
✅ Auto-deploys on git push
❌ Cold starts on free tier
❌ Limited resources

---

## Option 3: Deploy to Render ⭐ **RECOMMENDED (15 min)**

### Step 1: Create Render Account

1. Go to: https://render.com
2. Sign up with GitHub
3. Click **"New +"** → **"Web Service"**

### Step 2: Connect Repository

1. Connect your GitHub repository
2. Select `Course-Companion-FTE`
3. Configure:

```yaml
Name: course-companion-backend
Environment: Python
Build Command: pip install -r requirements.txt
Start Command: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Step 3: Add Environment Variables

Scroll to **"Environment"** section:

```env
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret
R2_BUCKET_NAME=generative-ai-fundamentals
R2_ENDPOINT=https://e71c4388cef18b821a1ccbc73c3aa149.r2.cloudflarestorage.com
PYTHON_VERSION=3.9
```

### Step 4: Deploy

Click **"Create Web Service"**

Render will:
- Build your backend
- Deploy it
- Give you a URL: `https://course-companion-backend.onrender.com`

### Step 5: Update ChatGPT App

```
Content API: https://course-companion-backend.onrender.com
Quiz API: https://course-companion-backend.onrender.com/quizzes
Progress API: https://course-companion-backend.onrender.com/progress
```

### Pros & Cons
✅ Free tier available
✅ Persistent URLs
✅ Automatic SSL
✅ Good documentation
❌ Cold starts on free tier (15-30 sec)
❌ Limited bandwidth

---

## Option 4: Deploy to Fly.io ⭐ **BEST PERFORMANCE (20 min)**

### Step 1: Install Fly CLI

```bash
curl -L https://fly.io/install.sh | sh
```

### Step 2: Authenticate

```bash
fly auth login
```

### Step 3: Launch App

```bash
cd C:\Users\Najma-LP\Desktop\Course-Companion-FTE\backend

# Launch to Fly.io
fly launch

# Follow prompts:
# - App name: course-companion-fte
# - Region: Choose nearest
# - Deploy now: Yes
```

### Step 4: Add Secrets

```bash
fly secrets set R2_ACCOUNT_ID=e71c4388cef18b821a1ccbc73c3aa149
fly secrets set R2_ACCESS_KEY_ID=your_access_key
fly secrets set R2_SECRET_ACCESS_KEY=your_secret
fly secrets set R2_BUCKET_NAME=generative-ai-fundamentals
fly secrets set R2_ENDPOINT=https://e71c4388cef18b821a1ccbc73c3aa149.r2.cloudflarestorage.com
```

### Step 5: Deploy

```bash
fly deploy
```

### Step 6: Get URL

Your app will be at:
```
https://course-companion-fte.fly.dev
```

### Pros & Cons
✅ No cold starts (always on)
✅ Fast performance
✅ Generous free tier
✅ Global deployment
❌ Requires CLI setup
❌ Credit card required (even for free tier)

---

## Option 5: Cloudflare Workers ⭐ **BEST FOR R2 (15 min)**

Since your content is already on R2, Cloudflare Workers is ideal.

### Step 1: Install Wrangler CLI

```bash
npm install -g wrangler
```

### Step 2: Authenticate

```bash
wrangler login
```

### Step 3: Create Worker

```bash
cd backend
wrangler init course-companion-api
```

### Step 4: Configure wrangler.toml

```toml
name = "course-companion-api"
main = "worker.js"
compatibility_date = "2024-01-01"

[vars]
R2_ACCOUNT_ID = "e71c4388cef18b821a1ccbc73c3aa149"
R2_BUCKET = "generative-ai-fundamentals"

[[r2_buckets]]
binding = "R2_BUCKET"
bucket_name = "generative-ai-fundamentals"
```

### Step 5: Deploy

```bash
wrangler deploy
```

### Pros & Cons
✅ Perfect for R2 integration
✅ Edge computing (fast worldwide)
✅ Generous free tier
✅ No cold starts
❌ Need to adapt code for Workers runtime

---

## Comparison Table

| Option | Setup Time | Free Tier | Performance | Best For |
|--------|------------|-----------|-------------|----------|
| ngrok | 5 min | Free | Good | Quick testing |
| Railway | 10 min | Yes | Medium | Easy deployment |
| Render | 15 min | Yes | Medium | Production ready |
| Fly.io | 20 min | Yes | Excellent | No cold starts |
| Cloudflare | 15 min | Yes | Excellent | R2 integration |

---

## Recommended Approach

### For Phase 1 Hackathon (Next 24-48 hours):

**Use ngrok** ⭐
- Fastest to set up
- Test with ChatGPT App immediately
- Get everything working

### For Production (After Hackathon):

**Use Fly.io or Cloudflare** ⭐
- Best performance
- No cold starts
- Scales well
- Cost-effective

---

## Deployment Steps Summary

### Choose Your Path:

**Path A: Quick Test (Today)**
```bash
1. Install ngrok
2. Run: ngrok http 8000
3. Copy URL to ChatGPT App
4. Test integration
```

**Path B: Production Deploy (This Week)**
```bash
1. Create Render/Railway account
2. Connect GitHub repo
3. Add environment variables
4. Deploy
5. Update ChatGPT App with production URL
```

---

## Testing Your Deployed Backend

Once deployed, test each endpoint:

```bash
# Test Content API
curl https://your-url.com/chapters

# Test Quiz API
curl https://your-url.com/quizzes

# Test Progress API
curl https://your-url.com/progress/dashboard
```

All should return JSON responses.

---

## Updating ChatGPT App with Deployed URLs

After deployment, update your ChatGPT App:

1. Go to: https://platform.openai.com/apps
2. Select your app
3. Go to **"Configuration"** → **"Actions"**
4. Update Base URLs:

```yaml
Content API: https://your-deployed-url.com
Quiz API: https://your-deployed-url.com
Progress API: https://your-deployed-url.com
```

5. Save changes
6. Test in ChatGPT interface

---

## Firewall Considerations

If deploying to cloud:

1. **Ensure CORS is enabled** in your FastAPI apps:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify ["https://chat.openai.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. **Check security group rules** (AWS/GCP/Azure)
3. **Allow HTTPS traffic** (port 443)
4. **Restrict API keys** in environment variables

---

## Monitoring

Once deployed, monitor:

- **Uptime**: Use UptimeRobot or Pingdom
- **Logs**: Check platform logs (Render/Railway/Fly)
- **Errors**: Set up error tracking (Sentry)
- **Performance**: Monitor response times

---

## Summary

**For Hackathon Demo (Next 24h):**
- Use ngrok for quick testing
- Get ChatGPT App working
- Demonstrate full flow

**For Production (After Hackathon):**
- Deploy to Fly.io or Cloudflare Workers
- Set up custom domain
- Enable monitoring
- Scale as needed

**Choose based on your timeline and requirements!**
