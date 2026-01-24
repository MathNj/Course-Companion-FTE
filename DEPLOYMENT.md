# Course Companion FTE - Production Deployment Guide

This guide covers deploying the Course Companion FTE backend to production using various platforms.

## Quick Start

Choose your deployment platform:
- **Fly.io** (Recommended) - Free tier available, good performance
- **Railway** - Simple, generous free tier
- **Render** - Easy setup, automatic deployments

## Option 1: Deploy to Fly.io (Recommended)

### Prerequisites

1. **Install Fly CLI**
   ```bash
   # Windows (PowerShell)
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

   # macOS
   brew install flyctl

   # Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Sign up and login**
   ```bash
   fly auth signup
   # OR if you have an account
   fly auth login
   ```

### Step 1: Create Fly App

```bash
cd backend

# Launch app (will create fly.toml)
fly launch --name course-companion-fte --region iad

# When prompted:
# - Use existing fly.toml? Yes
# - Create PostgreSQL database? Yes (select Development for free tier)
# - Create Redis? No (we'll use Upstash)
# - Deploy now? No (we need to set secrets first)
```

### Step 2: Create Database

If not created during launch:

```bash
# Create PostgreSQL database
fly postgres create \
  --name course-companion-db \
  --region iad \
  --initial-cluster-size 1 \
  --vm-size shared-cpu-1x \
  --volume-size 1

# Attach to app
fly postgres attach course-companion-db
```

### Step 3: Create Redis (Upstash)

Fly.io Redis is paid. Use Upstash Redis (free tier):

1. Go to https://upstash.com
2. Create account
3. Create Redis database
4. Select region close to your Fly.io app
5. Copy the Redis URL (format: `redis://...`)

### Step 4: Set Secrets

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set secrets
fly secrets set JWT_SECRET_KEY="your-generated-secret-key"
fly secrets set REDIS_URL="redis://your-upstash-url"

# Database URL is automatically set when you attach Postgres
# Verify with:
fly secrets list
```

### Step 5: Deploy

```bash
# Deploy the application
fly deploy

# Monitor deployment
fly logs

# Check status
fly status

# Open in browser
fly open
```

### Step 6: Run Migrations

```bash
# SSH into the VM
fly ssh console

# Run migrations
alembic upgrade head

# Exit
exit
```

### Step 7: Verify Deployment

```bash
# Get app URL
fly info

# Test endpoints
curl https://your-app.fly.dev/health
curl https://your-app.fly.dev/api/v1/chapters
curl https://your-app.fly.dev/api/openapi.json
```

### Fly.io Configuration

The `backend/fly.toml` file contains:
- **Region**: `iad` (US East - change as needed)
- **Resources**: 512MB RAM, 1 shared CPU
- **Auto-scaling**: Min 1 machine
- **Health checks**: Every 30s on `/health`
- **HTTPS**: Automatic with free SSL

### Monitoring

```bash
# View logs (real-time)
fly logs

# View metrics
fly dashboard

# SSH into machine
fly ssh console

# Check resource usage
fly status
```

### Updating

```bash
# After making code changes
git add .
git commit -m "Update feature"
git push

# Deploy new version
cd backend
fly deploy

# Rollback if needed
fly releases
fly rollback <version>
```

### Scaling

```bash
# Scale vertically (more resources)
fly scale vm shared-cpu-2x --memory 1024

# Scale horizontally (more machines)
fly scale count 2

# Auto-scaling
fly autoscale set min=1 max=3
```

## Option 2: Deploy to Railway

### Prerequisites

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli

   # OR use without installing
   npx @railway/cli
   ```

2. **Login**
   ```bash
   railway login
   ```

### Step 1: Create Project

```bash
cd backend

# Initialize Railway project
railway init

# Link to new project
railway link
```

### Step 2: Add Services

In Railway dashboard (https://railway.app):

1. **Add PostgreSQL**:
   - Click "New" → "Database" → "PostgreSQL"
   - Database URL is automatically set as `DATABASE_URL`

2. **Add Redis**:
   - Click "New" → "Database" → "Redis"
   - Redis URL is automatically set as `REDIS_URL`

### Step 3: Set Environment Variables

In Railway dashboard or via CLI:

```bash
# Via CLI
railway variables set JWT_SECRET_KEY="your-secret-key"
railway variables set APP_ENV="production"
railway variables set CORS_ORIGINS="https://chat.openai.com,https://chatgpt.com"

# Verify
railway variables
```

### Step 4: Deploy

Railway auto-deploys from GitHub:

1. Connect GitHub repository
2. Railway detects Dockerfile
3. Automatic deployments on push to main

Or deploy manually:

```bash
railway up
```

### Step 5: Get URL

```bash
# Generate domain
railway domain

# Or use custom domain
railway domain add yourdomain.com
```

## Option 3: Deploy to Render

### Prerequisites

1. GitHub account with repository
2. Render account (https://render.com)

### Step 1: Create Web Service

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Configure:
   - **Name**: course-companion-fte
   - **Environment**: Docker
   - **Region**: Oregon (US West)
   - **Branch**: master
   - **Dockerfile Path**: backend/Dockerfile

### Step 2: Add PostgreSQL

1. Click "New +" → "PostgreSQL"
2. Configure:
   - **Name**: course-companion-db
   - **Database**: course_companion
   - **User**: course_companion
   - **Region**: Same as web service
   - **Plan**: Free
3. Copy Internal Database URL

### Step 3: Add Redis

Render Redis is paid. Use Upstash:

1. Go to https://upstash.com
2. Create Redis database
3. Copy Redis URL

### Step 4: Set Environment Variables

In Web Service settings → Environment:

```bash
JWT_SECRET_KEY=your-secret-key
DATABASE_URL=your-postgres-url-from-render
REDIS_URL=your-upstash-redis-url
APP_ENV=production
CORS_ORIGINS=https://chat.openai.com,https://chatgpt.com
LOG_LEVEL=INFO
```

### Step 5: Deploy

1. Click "Manual Deploy" → "Deploy latest commit"
2. Monitor logs in dashboard
3. Wait for deployment to complete

### Step 6: Run Migrations

In Render Shell (or during first deploy):

```bash
# Add to Dockerfile CMD before uvicorn:
alembic upgrade head && uvicorn app.main:app
```

## Post-Deployment Setup

### 1. Update ChatGPT App

Update `chatgpt-app/openapi.yaml`:

```yaml
servers:
  - url: https://your-app.fly.dev/api/v1  # Or Railway/Render URL
    description: Production server
```

### 2. Update Custom GPT

In ChatGPT Custom GPT settings:
1. Edit Actions
2. Change import URL to: `https://your-app.fly.dev/api/openapi.json`
3. Re-import schema
4. Test actions

### 3. Test Production API

```bash
# Health check
curl https://your-app.fly.dev/health

# List chapters
curl https://your-app.fly.dev/api/v1/chapters

# OpenAPI schema
curl https://your-app.fly.dev/api/openapi.json

# Register user (optional - test auth)
curl -X POST https://your-app.fly.dev/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","full_name":"Test User"}'
```

### 4. Enable CORS for ChatGPT

Verify in `backend/app/config.py`:

```python
cors_origins: str = "https://chat.openai.com,https://chatgpt.com"
```

Already configured in `backend/.env.example`

### 5. Monitor Production

**Fly.io**:
```bash
fly logs
fly status
fly dashboard
```

**Railway**:
```bash
railway logs
railway status
```

**Render**:
- Dashboard → Logs
- Dashboard → Metrics

## Database Migrations

### Initial Setup

```bash
# SSH into production
fly ssh console  # Fly.io
railway run bash  # Railway

# Run migrations
alembic upgrade head

# Verify tables
psql $DATABASE_URL -c "\dt"
```

### Future Migrations

```bash
# Create migration locally
alembic revision --autogenerate -m "Add new column"

# Test locally
alembic upgrade head

# Commit and push
git add alembic/versions/*.py
git commit -m "Add migration"
git push

# Deploy
fly deploy  # Will run migrations automatically via Dockerfile CMD
```

## Secrets Management

### Fly.io

```bash
# Set secret
fly secrets set KEY=value

# List secrets (names only)
fly secrets list

# Remove secret
fly secrets unset KEY
```

### Railway

```bash
# Set variable
railway variables set KEY=value

# List variables
railway variables

# Delete variable
railway variables delete KEY
```

### Render

- Dashboard → Environment
- Add/Edit/Delete variables
- Auto-redeploys on changes

## SSL/HTTPS

All platforms provide free SSL:

- **Fly.io**: Automatic SSL with fly.dev domain
- **Railway**: Automatic SSL with railway.app domain
- **Render**: Automatic SSL with onrender.com domain

### Custom Domain

**Fly.io**:
```bash
fly certs create yourdomain.com
fly certs show yourdomain.com
# Add DNS records as shown
```

**Railway**:
- Dashboard → Settings → Domains → Add Custom Domain
- Add CNAME record to your DNS

**Render**:
- Dashboard → Settings → Custom Domain
- Add CNAME record to your DNS

## Performance Optimization

### 1. Enable Caching

Already configured in the app:
- Redis caching with 24-hour TTL
- Chapter and quiz content cached

### 2. Database Connection Pooling

In `backend/app/database.py`:
```python
engine = create_async_engine(
    settings.database_url,
    pool_size=5,  # Adjust based on traffic
    max_overflow=10,
    pool_pre_ping=True,
)
```

### 3. Static File Serving

For production, consider:
- Cloudflare R2 for chapter/quiz content
- CDN for static assets

## Monitoring & Logging

### Application Logs

```bash
# Fly.io
fly logs --app course-companion-fte

# Railway
railway logs

# Render
# Use dashboard
```

### Error Tracking

Consider adding:
- **Sentry** for error tracking
- **LogDNA** or **Papertrail** for log aggregation
- **UptimeRobot** for uptime monitoring

### Health Checks

All platforms auto-configured to check `/health` endpoint.

Endpoint returns:
```json
{
  "status": "healthy",
  "environment": "production",
  "components": {
    "api": "operational",
    "cache": "operational"
  }
}
```

## Cost Estimates

### Fly.io (Free Tier)
- **App**: 3 shared-cpu-1x VMs, 256MB RAM each - FREE
- **PostgreSQL**: Development instance - FREE
- **Redis**: Use Upstash (external) - FREE
- **Bandwidth**: 100GB/month - FREE
- **Total**: $0/month

### Railway (Free Tier)
- **$5 credit/month** (no credit card required)
- App + PostgreSQL + Redis fits in free tier
- **Total**: $0/month (within free credit)

### Render (Free Tier)
- **Web Service**: Free tier available
- **PostgreSQL**: 90-day free trial, then $7/month
- **Redis**: Not available (use external Upstash)
- **Total**: $0/month (first 90 days)

## Troubleshooting

### Build Failures

```bash
# Check build logs
fly logs

# Verify Dockerfile
docker build -f backend/Dockerfile.production -t test .

# Test locally
docker run -p 8000:8000 test
```

### Database Connection Issues

```bash
# Verify DATABASE_URL secret
fly secrets list

# Test connection
fly ssh console
psql $DATABASE_URL -c "SELECT 1"
```

### Redis Connection Issues

```bash
# Test Redis connection
fly ssh console
python -c "import redis; r=redis.from_url('$REDIS_URL'); print(r.ping())"
```

### Application Errors

```bash
# Check logs
fly logs

# Increase log verbosity
fly secrets set LOG_LEVEL=DEBUG

# SSH and debug
fly ssh console
python -c "from app.main import app; print(app)"
```

## Rollback

### Fly.io

```bash
# List releases
fly releases

# Rollback to previous
fly rollback <version>

# Or specify version
fly deploy --image <image-tag>
```

### Railway

- Dashboard → Deployments
- Click previous deployment → Redeploy

### Render

- Dashboard → Deploys
- Click previous deploy → "Rollback to this version"

## Security Checklist

- [ ] JWT_SECRET_KEY is strong and secret
- [ ] DATABASE_URL uses SSL
- [ ] CORS_ORIGINS limits to trusted domains
- [ ] No .env files in git
- [ ] Secrets stored in platform secret manager
- [ ] HTTPS enforced
- [ ] Database backups enabled
- [ ] Rate limiting configured (if needed)

## Next Steps

After successful deployment:

1. **Test production API** with all endpoints
2. **Update Custom GPT** with production URL
3. **Test ChatGPT integration** end-to-end
4. **Set up monitoring** (error tracking, uptime)
5. **Configure backups** (database)
6. **Add custom domain** (optional)
7. **Enable auto-scaling** (for growth)

---

**Deployment complete! Your Course Companion FTE is now live! 🚀**

For support, check platform documentation:
- Fly.io: https://fly.io/docs
- Railway: https://docs.railway.app
- Render: https://render.com/docs
