# Production Deployment Guide - Fly.io

## Quick Start (Windows PowerShell)

### Prerequisites

1. **Install Fly.io CLI** (if not installed):
   ```powershell
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. **Create Fly.io Account** (free):
   - Go to https://fly.io
   - Sign up (free tier includes 3 VMs + 1GB PostgreSQL)

3. **Login to Fly.io**:
   ```powershell
   flyctl auth login
   ```

### One-Command Deployment

```powershell
.\deploy-to-flyio.ps1
```

This script will:
- ✅ Create Fly.io app
- ✅ Create PostgreSQL database
- ✅ Set environment secrets
- ✅ Deploy backend
- ✅ Run database migrations
- ✅ Provide production URL

### What Gets Deployed

- **Backend API**: FastAPI application
- **PostgreSQL Database**: 1GB free tier
- **Content**: 6 chapters + 6 quizzes
- **All 6 API endpoints**: Operational

### Estimated Costs

**Free Tier** (what you'll use):
- ✅ Backend VM: FREE (up to 3 small VMs)
- ✅ PostgreSQL: FREE (1GB storage)
- ✅ Bandwidth: FREE (160GB/month)
- ✅ **Total: $0/month**

**If you exceed free tier**:
- Additional VMs: ~$5/month each
- More storage: ~$1/GB-month

## Manual Deployment Steps

If you prefer manual deployment or the script fails:

### Step 1: Create App

```powershell
cd backend
flyctl launch --name course-companion-fte --region iad --no-deploy --copy-config
```

### Step 2: Create Database

```powershell
flyctl postgres create --name course-companion-db --region iad --initial-cluster-size 1 --vm-size shared-cpu-1x --volume-size 1
flyctl postgres attach course-companion-db
```

### Step 3: Set Secrets

```powershell
# Generate JWT secret
$secret = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})

# Set secrets
flyctl secrets set JWT_SECRET_KEY="$secret" APP_ENV="production" CORS_ORIGINS="https://chat.openai.com,https://chatgpt.com" LOG_LEVEL="INFO"
```

### Step 4: Deploy

```powershell
flyctl deploy --dockerfile Dockerfile.production
```

### Step 5: Run Migrations

```powershell
flyctl ssh console -C "alembic upgrade head"
```

## Verify Deployment

### Test Health Endpoint

```powershell
curl https://course-companion-fte.fly.dev/health
```

**Expected response**:
```json
{"status":"healthy","environment":"production","components":{"api":"operational","cache":"operational"}}
```

### Test API Endpoint

```powershell
# Register a test user
curl -X POST https://course-companion-fte.fly.dev/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{"email":"test@example.com","password":"Test123!","full_name":"Test User"}'
```

### Check App Status

```powershell
flyctl status
```

## Configure ChatGPT Integration

### 1. Get Production URL

Your production URL will be:
```
https://course-companion-fte.fly.dev/api/v1
```

OpenAPI spec URL:
```
https://course-companion-fte.fly.dev/api/openapi.json
```

### 2. Create Custom GPT

1. Go to https://chat.openai.com (ChatGPT Plus required)
2. Click **"Explore GPTs"** → **"Create a GPT"**
3. Click **"Configure"** tab
4. **Name**: Course Companion FTE
5. **Description**: AI tutor for learning Generative AI Fundamentals
6. **Instructions**: Copy from `chatgpt-app/instructions.md`

### 3. Add Actions

1. Click **"Create new action"**
2. Choose **"Import from URL"**
3. Enter: `https://course-companion-fte.fly.dev/api/openapi.json`
4. Click **"Import"**
5. Configure authentication:
   - **Type**: HTTP Bearer
   - **How to provide**: User will input (for testing)

### 4. Test Your GPT

Try these conversations:
```
You: I want to learn about generative AI
You: What is a transformer model?
You: Quiz me on Chapter 1
You: How's my progress?
```

## Monitoring and Management

### View Logs

```powershell
# Live logs
flyctl logs

# Last 100 lines
flyctl logs --lines 100

# Filter by app instance
flyctl logs --instance <instance-id>
```

### Check App Status

```powershell
flyctl status
```

### SSH Into App

```powershell
flyctl ssh console
```

Inside the container:
```bash
# Check environment
env | grep FLY

# View logs
tail -f /app/logs/app.log

# Run migrations manually
alembic upgrade head

# Access database
flyctl postgres connect -a course-companion-db
```

### Restart App

```powershell
flyctl apps restart
```

### Scale Up (if needed)

```powershell
# Scale to 2 VMs
flyctl scale count 2

# Upgrade to larger VM
flyctl scale vm shared-cpu-2x
```

## Troubleshooting

### Issue: Deployment Fails

**Check logs**:
```powershell
flyctl logs --lines 50
```

**Common causes**:
- Docker build error: Check Dockerfile.production
- Out of memory: Check free tier limits
- Database connection failed: Verify database is attached

### Issue: Database Migrations Fail

**Run manually**:
```powershell
flyctl ssh console -C "cd /app && alembic upgrade head"
```

**Check database status**:
```powershell
flyctl postgres status -a course-companion-db
```

### Issue: API Returns 500 Errors

**Check logs**:
```powershell
flyctl logs --lines 100 | grep ERROR
```

**Common causes**:
- Missing secrets: `flyctl secrets list`
- Database not ready: `flyctl postgres status`
- Out of memory: `flyctl status`

### Issue: ChatGPT Can't Reach API

**Verify OpenAPI spec**:
```powershell
curl https://course-companion-fte.fly.dev/api/openapi.json
```

**Check CORS configuration**:
```powershell
flyctl secrets list
# Should include: CORS_ORIGINS=https://chat.openai.com,https://chatgpt.com
```

**Test from external source**:
- Use https://httpie.io/app or Postman
- Test: GET https://course-companion-fte.fly.dev/health

## Update Application

### Make Changes Locally

1. Edit code in `backend/`
2. Test locally: `docker-compose up`

### Deploy Updates

```powershell
cd backend
flyctl deploy
```

### Run Migrations (if needed)

```powershell
flyctl ssh console -C "alembic upgrade head"
```

## Database Management

### Backup Database

```powershell
# Create snapshot
flyctl postgres create-snapshot -a course-companion-db

# List snapshots
flyctl postgres list-snapshots -a course-companion-db
```

### Restore Database

```powershell
flyctl postgres restore-snapshot -a course-companion-db <snapshot-id>
```

### Access Database

```powershell
flyctl postgres connect -a course-companion-db
```

Inside psql:
```sql
\dt                    -- List tables
SELECT * FROM users;   -- Query users
\q                     -- Quit
```

## Cost Monitoring

### Check Usage

```powershell
flyctl orgs show
```

### View Metrics

```powershell
flyctl dashboard
```

### Free Tier Limits

- **3 VMs** (shared-cpu-1x: 256MB RAM, 1 CPU)
- **3GB volume storage**
- **160GB outbound bandwidth/month**

**What this means for Course Companion FTE**:
- ✅ 1 backend VM: Within free tier
- ✅ 1GB PostgreSQL: Within free tier
- ✅ API traffic: Well within 160GB limit
- ✅ **Total cost: $0/month**

## Security Hardening

### Secrets Management

```powershell
# List secrets (shows PRN, not values)
flyctl secrets list

# Set new secret
flyctl secrets set MY_SECRET="value"

# Remove secret
flyctl secrets remove MY_SECRET
```

### HTTPS/TLS

Fly.io automatically:
- ✅ Issues Let's Encrypt SSL certificate
- ✅ Enables HTTPS for all traffic
- ✅ Handles certificate renewal

### Firewall Rules

By default, only ports 80 and 443 are exposed.

### Database Security

- Database is in private VPC
- Only accessible from app VM
- Connection string includes auto-generated credentials

## Performance Optimization

### Enable Redis Cache (Optional)

For better performance, add Redis:

```powershell
flyctl redis create --name course-companion-redis --region iad
flyctl redis attach course-companion-redis
flyctl secrets set REDIS_URL=$(flyctl redis status -a course-companion-redis --json | ConvertFrom-Json).primaryConnectionString
```

### Monitoring

```powershell
# Enable metrics
flyctl metrics enable

# View metrics
flyctl metrics dashboard
```

## Rollback

### If Deployment Breaks Something

```powershell
# View deployment history
flyctl releases

# Rollback to previous version
flyctl releases rollback <version-number>

# Example: Rollback 2 versions
flyctl releases rollback -r 2
```

## Alternative: Railway Deployment

If Fly.io doesn't work, try Railway:

1. Go to https://railway.app
2. Click **"Deploy from GitHub repo"**
3. Select your repo
4. Railway detects it's a Python/FastAPI app
5. Add PostgreSQL database
6. Set environment variables
7. Deploy!

**Railway free tier**:
- $5 free credit/month
- Should be sufficient for testing

## Support

### Fly.io Docs
- https://fly.io/docs/getting-started/

### Common Issues
- https://fly.io/docs/about/faq/

### Community
- https://community.fly.io/

## Summary

After running the deployment script:

1. ✅ Backend deployed to Fly.io
2. ✅ PostgreSQL database created
3. ✅ All migrations run
4. ✅ Production URL available
5. ✅ Ready for ChatGPT integration

**Your production URL**: `https://course-companion-fte.fly.dev`

**Next**: Configure ChatGPT Custom GPT with this URL and test!
