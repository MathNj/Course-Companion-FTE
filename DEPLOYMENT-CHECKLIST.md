# Production Deployment Checklist

Use this checklist to ensure a smooth production deployment.

## Pre-Deployment

### Code Readiness
- [ ] All tests passing (`pytest backend/tests -v`)
- [ ] No TODO/FIXME comments in critical paths
- [ ] Code reviewed and merged to master branch
- [ ] Version tagged in git (`git tag v1.0.0`)

### Configuration
- [ ] `.env.production` created (don't commit!)
- [ ] JWT_SECRET_KEY generated (strong, 32+ characters)
- [ ] CORS_ORIGINS configured for ChatGPT domains
- [ ] Database credentials ready
- [ ] Redis URL ready (Upstash or platform)

### Security
- [ ] Secrets NOT in git
- [ ] `.gitignore` includes `.env*`
- [ ] Database uses SSL
- [ ] JWT secret is strong and unique
- [ ] HTTPS will be enforced

### Documentation
- [ ] README.md updated with production info
- [ ] API documentation complete
- [ ] Environment variables documented

## Platform Setup

### Choose Platform
- [ ] Fly.io account created
- [ ] OR Railway account created
- [ ] OR Render account created
- [ ] Payment method added (if needed)

### CLI Installation
- [ ] Fly CLI installed (`flyctl`) OR
- [ ] Railway CLI installed (`railway`) OR
- [ ] Using Render dashboard

### GitHub
- [ ] Repository pushed to GitHub
- [ ] Master branch protected
- [ ] Secrets configured (if using GitHub Actions)

## Database Setup

### PostgreSQL
- [ ] Database created on platform
- [ ] Database name: `course_companion`
- [ ] User created with permissions
- [ ] DATABASE_URL obtained
- [ ] SSL enabled
- [ ] Backups configured

### Initial Data
- [ ] Migrations ready (`alembic/versions/*.py`)
- [ ] Content files in `backend/content/`
- [ ] 6 chapters present
- [ ] 6 quizzes present

## Redis Setup

### Cache Configuration
- [ ] Upstash account created
- [ ] Redis database created
- [ ] Region selected (close to app)
- [ ] REDIS_URL obtained
- [ ] Connection tested

## Application Deployment

### Fly.io
- [ ] `fly launch` executed
- [ ] `fly.toml` configured
- [ ] PostgreSQL attached
- [ ] Secrets set (`fly secrets set`)
- [ ] `fly deploy` successful
- [ ] Logs checked (`fly logs`)

### Railway
- [ ] Project created
- [ ] GitHub connected
- [ ] PostgreSQL added
- [ ] Redis added
- [ ] Environment variables set
- [ ] Deployment successful
- [ ] Logs checked

### Render
- [ ] Blueprint created
- [ ] `render.yaml` configured
- [ ] GitHub connected
- [ ] PostgreSQL created
- [ ] Environment variables set
- [ ] Deployment successful
- [ ] Logs checked

## Post-Deployment

### Database Migrations
- [ ] SSH/Console access tested
- [ ] `alembic upgrade head` executed
- [ ] Tables created (6 tables)
- [ ] No migration errors

### API Testing
- [ ] Health check: `curl https://app.com/health`
- [ ] Returns `{"status":"healthy"}`
- [ ] List chapters: `curl https://app.com/api/v1/chapters`
- [ ] Returns 6 chapters
- [ ] OpenAPI schema: `curl https://app.com/api/openapi.json`
- [ ] Valid JSON returned

### Authentication Testing
- [ ] Register user works
- [ ] Login returns JWT token
- [ ] Token refresh works
- [ ] Protected endpoints require auth

### Content Testing
- [ ] Chapter 1 content loads
- [ ] Chapter content matches local files
- [ ] Quiz 1 loads (without answer keys)
- [ ] Quiz submission works
- [ ] Grading returns correct results

### Progress Tracking
- [ ] Get progress endpoint works
- [ ] Streak tracking functional
- [ ] Milestones calculated correctly

## ChatGPT Integration

### OpenAPI Update
- [ ] `chatgpt-app/openapi.yaml` updated with production URL
- [ ] Committed and pushed

### Custom GPT Update
- [ ] Logged into ChatGPT
- [ ] Opened Custom GPT settings
- [ ] Updated Actions import URL
- [ ] Re-imported OpenAPI schema
- [ ] All 5 actions present

### End-to-End Testing
- [ ] "List chapters" works
- [ ] "Show Chapter 1" returns content
- [ ] "Quiz me" presents questions
- [ ] Quiz submission and grading works
- [ ] "My progress" shows stats
- [ ] GPT uses API (not its own knowledge)

## Monitoring

### Logging
- [ ] Application logs visible
- [ ] Error logs being captured
- [ ] Log level set to INFO
- [ ] No sensitive data in logs

### Health Checks
- [ ] Platform health check configured
- [ ] `/health` endpoint monitored
- [ ] Alerts configured (optional)

### Performance
- [ ] Response times < 1s
- [ ] Cache hit rate > 80%
- [ ] Database queries optimized
- [ ] No memory leaks

## Documentation

### Update Documentation
- [ ] Production URL added to README.md
- [ ] Deployment process documented
- [ ] Troubleshooting guide updated
- [ ] API base URL updated in docs

### User Communication
- [ ] Beta testers notified (if any)
- [ ] Production URL shared
- [ ] Known issues documented
- [ ] Support channel established

## Backup & Recovery

### Database Backups
- [ ] Automatic backups enabled
- [ ] Backup frequency configured (daily)
- [ ] Backup retention set (7-30 days)
- [ ] Restore process tested

### Code Backups
- [ ] Git repository backed up
- [ ] All branches pushed to remote
- [ ] Tags created for releases
- [ ] GitHub Actions configured (optional)

## Security Hardening

### Application Security
- [ ] HTTPS enforced (automatic)
- [ ] CORS properly configured
- [ ] Rate limiting considered
- [ ] SQL injection prevention (using ORM)
- [ ] XSS prevention (API only)

### Dependency Security
- [ ] No known vulnerabilities (`pip audit`)
- [ ] Dependencies up to date
- [ ] Security updates scheduled

### Access Control
- [ ] Production secrets secured
- [ ] Limited access to production
- [ ] 2FA enabled on platform account
- [ ] API keys rotated regularly

## Performance Optimization

### Caching
- [ ] Redis caching enabled
- [ ] Cache TTL configured (24 hours)
- [ ] Cache hit rate monitored

### Database
- [ ] Indexes created
- [ ] Connection pooling configured
- [ ] Query performance monitored

### Scaling
- [ ] Auto-scaling configured (if available)
- [ ] Resource limits set
- [ ] Scale-up plan documented

## Cost Management

### Resource Usage
- [ ] Current usage monitored
- [ ] Within free tier limits (if applicable)
- [ ] Billing alerts set
- [ ] Cost optimization opportunities identified

### Estimated Costs
- [ ] Monthly cost estimated
- [ ] Budget allocated
- [ ] Cost tracking enabled

## Rollback Plan

### Rollback Preparation
- [ ] Previous version tagged
- [ ] Rollback command documented
- [ ] Database migration rollback tested
- [ ] Downtime estimated (if needed)

### Rollback Testing
- [ ] Can rollback to previous release
- [ ] Database migrations reversible
- [ ] Content versioning (if needed)

## Go-Live

### Final Checks
- [ ] All checklist items completed
- [ ] Team notified
- [ ] Support ready
- [ ] Monitoring active

### Launch
- [ ] Production deployed
- [ ] Health checks passing
- [ ] No errors in logs
- [ ] Users can access

### Post-Launch
- [ ] Monitor for 1 hour
- [ ] Check error rates
- [ ] Verify user activity
- [ ] Gather initial feedback

## Success Criteria

Deployment is successful when:
- ✅ Health check returns 200 OK
- ✅ All API endpoints functional
- ✅ ChatGPT integration working
- ✅ No errors in logs (first hour)
- ✅ Users can register and learn
- ✅ Quizzes can be taken and graded
- ✅ Progress tracking works
- ✅ Response times acceptable (< 1s)

## Support

### Issue Tracking
- [ ] Issue tracking system ready
- [ ] Bug report template created
- [ ] Support email configured

### Communication
- [ ] Status page (optional)
- [ ] User documentation published
- [ ] FAQ created
- [ ] Contact information visible

---

## Sign-off

- [ ] Technical lead approved
- [ ] Product owner approved
- [ ] Deployment completed by: ________________
- [ ] Date: ________________
- [ ] Production URL: ________________

---

**Ready for production! 🚀**

Keep this checklist for future deployments and updates!
