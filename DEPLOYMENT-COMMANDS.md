# 🚀 DEPLOY TO PRODUCTION NOW

## Quick Start - Copy and Paste These Commands

Open **PowerShell as Administrator** and run:

### 1. Install flyctl
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

### 2. Login to Fly.io
```powershell
flyctl auth login
```
(Opens browser - create free account if needed)

### 3. Go to backend directory
```powershell
cd C:\Users\Najma-LP\Desktop\Course-Companion-FTE\backend
```

### 4. Create the app
```powershell
flyctl launch --name course-companion-fte --region iad --no-deploy --copy-config
```
(Press Enter for all defaults)

### 5. Create database
```powershell
flyctl postgres create --name course-companion-db --region iad --initial-cluster-size 1 --vm-size shared-cpu-1x --volume-size 1
```

### 6. Attach database
```powershell
flyctl postgres attach course-companion-db
```

### 7. Set secrets
```powershell
flyctl secrets set JWT_SECRET_KEY="nFpDpFougSl6BkqqXwzsDmKHA6keETfSytpB8nPQlfw" APP_ENV="production" CORS_ORIGINS="https://chat.openai.com,https://chatgpt.com" LOG_LEVEL="INFO"
```

### 8. Deploy!
```powershell
flyctl deploy --dockerfile Dockerfile.production
```
(Wait 3-5 minutes for deployment)

### 9. Run migrations
```powershell
flyctl ssh console -C "alembic upgrade head"
```

### 10. Verify deployment
```powershell
curl https://course-companion-fte.fly.dev/health
```

## ✅ Success!

Your production URLs:
- **API**: https://course-companion-fte.fly.dev
- **Health**: https://course-companion-fte.fly.dev/health
- **OpenAPI**: https://course-companion-fte.fly.dev/api/openapi.json

## 🤖 Configure ChatGPT

1. Go to https://chat.openai.com (Plus required)
2. Create Custom GPT → Configure
3. Import OpenAPI from: `https://course-companion-fte.fly.dev/api/openapi.json`
4. Copy instructions from: `chatgpt-app/instructions.md`
5. Test!

## 📊 Monitor Your App

```powershell
flyctl status        # Check status
flyctl logs          # View logs
flyctl apps restart  # Restart if needed
```

## 💰 Cost: FREE

- Backend VM: FREE
- PostgreSQL 1GB: FREE
- Bandwidth: FREE
- **Total: $0/month**

---

**Need help?** Check `DEPLOYMENT-FLYIO-GUIDE.md` for detailed troubleshooting.
