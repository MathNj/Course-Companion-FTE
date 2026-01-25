# Quick Deploy to Render (Free Tier, No Credit Card!)

## Option 1: Manual Deploy to Render (Recommended - No CLI needed)

### Step 1: Go to Render

Visit: https://render.com

### Step 2: Sign Up

- Click "Sign Up"
- Use GitHub account (easiest)
- No credit card required for free tier

### Step 3: Create New Web Service

1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Select: `MathNj/Course-Companion-FTE`

### Step 4: Configure Service

**Name**: `course-companion-fte`

**Root Directory**: `backend`

**Build Command**:
```
pip install --no-cache-dir -e ".[dev]" && alembic upgrade head
```

**Start Command**:
```
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Step 5: Add PostgreSQL Database

1. In Render dashboard, click "New" → "PostgreSQL"
2. Name: `course-companion-db`
3. Database: `PostgreSQL 15` (free tier)
4. Region: Choose closest to you

### Step 6: Connect Database to App

1. Go to your web service
2. Click "Environment"
3. Add internal database URL: `DATABASE_URL`
   - Value: Click "Connect" → "Internal Database URL"
   - Copy from database service

### Step 7: Add Environment Variables

In your web service → "Environment", add:

```
JWT_SECRET_KEY=nFpDpFougSl6BkqqXwzsDmKHA6keETfSytpB8nPQlfw
APP_ENV=production
CORS_ORIGINS=https://chat.openai.com,https://chatgpt.com
LOG_LEVEL=INFO
```

### Step 8: Deploy!

Click "Create Web Service"

Render will:
- Build your Docker image
- Deploy to production
- Provide a URL like: `https://course-companion-fte.onrender.com`

### Step 9: Verify Deployment

```bash
curl https://course-companion-fte.onrender.com/health
```

## Cost: FREE

Render free tier includes:
- ✅ 750 hours/month (enough for 24/7 operation)
- ✅ 512MB RAM
- ✅ PostgreSQL 90MB free tier
- ✅ SSL/TLS certificate
- ✅ **Total: $0/month**

## Your Production URLs

After deployment:
```
API: https://course-companion-fte.onrender.com
Health: https://course-companion-fte.onrender.com/health
OpenAPI: https://course-companion-fte.onrender.com/api/openapi.json
```

## Configure ChatGPT

1. Go to https://chat.openai.com
2. Create Custom GPT
3. Import from: `https://course-companion-fte.onrender.com/api/openapi.json`
4. Copy instructions from `chatgpt-app/instructions.md`
5. Test!

---

**Ready to deploy? Go to https://render.com and follow the steps above!**
