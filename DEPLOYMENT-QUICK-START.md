# Production Deployment - Quick Reference

## One-Command Deploy (Windows)

```powershell
# 1. Install flyctl (first time only)
iwr https://fly.io/install.ps1 -useb | iex

# 2. Login (first time only)
flyctl auth login

# 3. Deploy!
.\deploy-to-flyio.ps1
```

## What Happens

1. Creates Fly.io app (course-companion-fte)
2. Creates PostgreSQL database (1GB free)
3. Sets environment secrets
4. Deploys backend from Dockerfile
5. Runs database migrations
6. **Provides production URL**

## Your Production URLs

After deployment, you'll get:

```
Backend API:     https://course-companion-fte.fly.dev
Health Check:    https://course-companion-fte.fly.dev/health
OpenAPI Spec:    https://course-companion-fte.fly.dev/api/openapi.json
```

## Test Deployment

```powershell
# Health check
curl https://course-companion-fte.fly.dev/health

# Register test user
curl -X POST https://course-companion-fte.fly.dev/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{"email":"me@example.com","password":"Test123!","full_name":"Me"}'
```

## Connect ChatGPT

1. Go to https://chat.openai.com (Plus required)
2. Create Custom GPT → Configure
3. Import OpenAPI from: `https://course-companion-fte.fly.dev/api/openapi.json`
4. Copy instructions from `chatgpt-app/instructions.md`
5. Test!

## Common Commands

```powershell
flyctl status        # Check app status
flyctl logs          # View live logs
flyctl apps restart  # Restart app
flyctl open          # Open in browser
```

## Costs

**Free Tier** (what you get):
- ✅ Backend VM: FREE
- ✅ PostgreSQL 1GB: FREE
- ✅ Bandwidth: FREE
- ✅ Total: **$0/month**

## Troubleshooting

```powershell
# If deployment fails
flyctl logs --lines 100

# If migrations fail
flyctl ssh console -C "alembic upgrade head"

# Rollback to previous version
flyctl releases rollback -r 1
```

## Full Documentation

See `DEPLOYMENT-FLYIO-GUIDE.md` for complete guide.

---

**Ready to deploy? Run: `.\deploy-to-flyio.ps1`**
