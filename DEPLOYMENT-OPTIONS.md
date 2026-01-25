# 🚀 PRODUCTION DEPLOYMENT - Choose Your Platform

## Issue with Fly.io

Fly.io now requires a credit card on file even for free tier. Let's use alternatives!

## Option 1: Railway (Recommended - No Credit Card!) ⭐

**URL**: https://railway.app/new

### Steps:
1. Click "Deploy from GitHub repo"
2. Select: `MathNj/Course-Companion-FTE`
3. Click "Deploy"
4. Add PostgreSQL database
5. Add environment variables
6. Redeploy

**Free Tier**: $5 credit/month
**Docs**: See `DEPLOY-RAILWAY.md`

---

## Option 2: Render (Also No Credit Card!)

**URL**: https://render.com

### Steps:
1. Sign up with GitHub
2. Click "New" → "Web Service"
3. Connect your GitHub repo
4. Root dir: `backend`
5. Build: `pip install --no-cache-dir -e ".[dev]" && alembic upgrade head`
6. Start: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
7. Add PostgreSQL database
8. Add environment variables
9. Deploy!

**Free Tier**: 750 hours/month (24/7), 512MB RAM, 90MB PostgreSQL
**Docs**: See `DEPLOY-RENDER.md`

---

## Option 3: Fly.io (Requires Credit Card)

If you want to add a credit card to Fly.io:

1. Go to: https://fly.io/dashboard/math-nj/billing
2. Add payment method
3. Then run: `.\deploy-to-flyio.ps1`

---

## Quick Recommendation

**Use Railway** (easiest, no credit card, good free tier):
1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select `MathNj/Course-Companion-FTE`
4. Done!

## What About the Content?

All content files are already in the repository:
- ✅ 6 chapters in `backend/content/chapters/`
- ✅ 6 quizzes in `backend/content/quizzes/`
- ✅ All ready to deploy!

---

**Which platform do you want to use?** I recommend Railway for the easiest setup!
