# ChatGPT Custom GPT Configuration Guide

Complete step-by-step guide to configure ChatGPT Custom GPT with the Course Companion FTE backend.

---

## Prerequisites

✅ Backend deployed to production
✅ OpenAPI specification available
✅ CORS configured for ChatGPT domains
✅ Authentication system operational

---

## Step-by-Step Configuration

### Step 1: Access ChatGPT Custom GPT Configuration

1. Go to https://chat.openai.com
2. Click on **"Explore GPTs"** in the left sidebar
3. Click **"Create a GPT"** button
4. You'll see the GPT configuration page

---

### Step 2: Basic Information

Fill in the basic GPT details:

**Name:**
```
Course Companion FTE - Generative AI
```

**Description (Short):**
```
Expert tutor for the Generative AI Fundamentals course. Provides grounded answers using only course material, tracks your progress, and administers quizzes.
```

**Instructions (Copy and paste):

```
You are an expert educational tutor for the "Generative AI Fundamentals" course. Your role is to help students learn using ONLY the course material - never make up information.

## Your Capabilities

1. **Access Course Content** - You can retrieve chapter content, sections, and learning objectives
2. **Search Content** - You can search the course material to find relevant information
3. **Answer Questions** - You provide grounded answers using only course material (zero-hallucination)
4. **Track Progress** - You can monitor student progress through the course
5. **Administer Quizzes** - You can present quiz questions and grade answers
6. **Provide Explanations** - You explain concepts using course content only

## Critical Rules

1. **NEVER HALLUCINATE** - Only use information from the course material
2. **Zero-Backend-LLM** - You don't generate your own content; you retrieve and present course content
3. **Grounded Q&A** - When asked questions, search the course material first
4. **Cite Sources** - Reference which chapter and section information comes from
5. **Progress Tracking** - Help students track their learning journey
6. **Quiz First** - For factual questions, consider using the quiz system

## How to Help Students

### When Students Ask Questions:
1. Search the course material using the search endpoint
2. Retrieve relevant chapters and sections
3. Present information with citations (Chapter X, Section Y)
4. Suggest related quizzes for practice

### When Students Want to Learn:
1. Ask which chapter or topic interests them
2. Retrieve that chapter's content
3. Present learning objectives and key concepts
4. Offer related quiz questions

### When Students Request Quizzes:
1. Ask which chapter they want to test on
2. Retrieve quiz questions for that chapter
3. Present questions one at a time
4. Grade answers and provide explanations

## Access Control

- Free users can access Chapters 1-3
- Premium users can access all chapters (1-6)
- Always check user's subscription tier before providing premium content

## Your Tone

- Encouraging and supportive
- Patient and thorough
- Focused on learning outcomes
- Celebrates student progress
- Provides constructive feedback

## Example Interactions

**Student:** "What is a transformer model?"

**You:** [Search course material for "transformer model"]
"Great question! According to Chapter 3 on 'Neural Network Architectures,' a transformer model is a neural network architecture that uses self-attention mechanisms to process sequential data. [Present detailed content from Chapter 3, Section 3.2]. Would you like to try a quiz question on this topic?"

**Student:** "Quiz me on Chapter 1"

**You:** [Retrieve quiz for Chapter 1]
"Excellent choice! Let's test your knowledge of Chapter 1. [Present first question]. Take your time - I'll wait for your answer!"

## Important Notes

- Always verify you have authentication before attempting to access content
- If authentication fails, guide the user to register/login
- Never provide premium content to free-tier users
- Always cite your sources (Chapter X, Section Y)
- When you don't find information in the course material, say so explicitly

Remember: Your strength is providing ACCURATE, GROUNDED answers from the course material, not generating new information.
```

---

### Step 3: Configure Actions (API Integration)

This is the critical part where ChatGPT connects to your backend.

#### 3.1 Enable Actions

1. Scroll down to the **"Actions"** section
2. Click **"Create new action"**
3. Select **"OpenAPI"** as the specification type

#### 3.2 Import OpenAPI Specification

You have two options:

**Option A: Automatic Import (Recommended)**

In the **"Import from URL"** field, paste:
```
https://course-companion-fte.fly.dev/api/openapi.json
```

Click **"Import"** or **"Fetch"**. ChatGPT will automatically load all API endpoints.

**Option B: Manual Import**

If automatic import doesn't work, click **"Import manually"** and paste the OpenAPI JSON from:
```
https://course-companion-fte.fly.dev/api/openapi.json
```

Visit that URL, copy all the JSON, and paste it into the editor.

#### 3.3 Configure Authentication

1. In the **"Authentication"** section, select **"Bearer token"**
2. Leave the **"Bearer token prefix"** as `Bearer`
3. Click **"Save"**

**Note:** ChatGPT will handle the authentication flow by:
- First calling the register or login endpoint to get a token
- Then using that token in subsequent requests

#### 3.4 Verify Endpoints

After importing, you should see these endpoints:

**Authentication:**
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get user profile

**Chapters:**
- `GET /api/v1/chapters` - List all chapters
- `GET /api/v1/chapters/{chapter_id}` - Get chapter content
- `GET /api/v1/chapters/search` - Search content (Grounded Q&A)

**Quizzes:**
- `GET /api/v1/quizzes/{quiz_id}` - Get quiz
- `POST /api/v1/quizzes/{quiz_id}/submit` - Submit quiz

**Progress:**
- `GET /api/v1/progress` - Get user progress
- `GET /api/v1/progress/streak` - Get streak details
- `GET /api/v1/progress/chapters/{chapter_id}` - Get chapter progress
- `POST /api/v1/progress/activity` - Record activity

---

### Step 4: Privacy Policy

In the **"Privacy"** section, paste:

```
# Privacy Policy

## Data Collection
We collect the following information:
- Email address (for user account)
- Name (optional)
- Learning progress and quiz scores
- Activity timestamps

## Data Usage
Your data is used to:
- Provide personalized learning experience
- Track your course progress
- Administer and grade quizzes
- Maintain streak records

## Data Storage
- All data is stored securely in PostgreSQL database
- Passwords are hashed with bcrypt (never stored in plain text)
- JWT tokens expire after 30 days

## Data Sharing
We do NOT share your personal data with third parties.
Your learning progress is private to you.

## Data Retention
- Your data is retained as long as your account is active
- You can request account deletion at any time
- Upon deletion, all personal data is permanently removed

## Security
- All data is encrypted in transit (HTTPS/TLS)
- All data is encrypted at rest
- We follow industry best practices for data security

## Your Rights
- Right to access your data
- Right to correct your data
- Right to delete your data
- Right to export your data

## Contact
For privacy concerns, contact the course administrator.

Last updated: January 25, 2026
```

---

### Step 5: Configure Profile

Add an image and description for your GPT:

**Profile Image:**
You can use any educational AI-themed image or create one with:
- Background: Blue/purple gradient
- Icon: Neural network or book
- Text: "Course Companion"

**Description (for GPT store):**
```
Your personal tutor for the Generative AI Fundamentals course. Get grounded answers from course material, track your progress, take quizzes, and master AI concepts with zero hallucination.

Access to:
- 6 comprehensive chapters on Generative AI
- Interactive quizzes with instant feedback
- Progress tracking and streaks
- Grounded Q&A (no made-up answers)

Free tier includes Chapters 1-3. Premium unlocks all content.
```

---

### Step 6: Test Your GPT

Before publishing, test the integration:

#### Test 1: Registration Flow

**Prompt to GPT:**
```
Hi, I'm new here. I want to register for the course.
```

**Expected Behavior:**
- GPT should call the register endpoint
- Ask for your email and password
- Create an account
- Confirm registration was successful

#### Test 2: Access Content

**Prompt to GPT:**
```
What topics are covered in Chapter 1?
```

**Expected Behavior:**
- GPT should call `/api/v1/chapters` to list chapters
- Call `/api/v1/chapters/chapter-1` to get Chapter 1 content
- Present chapter title, objectives, and sections
- Should NOT make up any information

#### Test 3: Grounded Q&A

**Prompt to GPT:**
```
What is a Large Language Model?
```

**Expected Behavior:**
- GPT should call `/api/v1/chapters/search?q=Large+Language+Model`
- Present information from search results
- Cite which chapter/section it came from
- Say "I couldn't find that in the course material" if not found

#### Test 4: Quiz

**Prompt to GPT:**
```
Give me a quiz on Chapter 1.
```

**Expected Behavior:**
- GPT should call `/api/v1/quizzes/chapter-1-quiz`
- Present quiz questions
- Wait for your answers
- Submit your answers for grading
- Provide feedback and explanations

#### Test 5: Progress Check

**Prompt to GPT:**
```
How am I doing in the course?
```

**Expected Behavior:**
- GPT should call `/api/v1/progress`
- Present your completion statistics
- Show quiz scores
- Display streak information
- Provide encouragement

---

### Step 7: Publish Your GPT

Once testing is successful:

1. Click **"Publish"** or **"Update"** button
2. Choose visibility:
   - **"Only me"** - Private use only
   - **"Only people with a link"** - Share with specific people
   - **"Public"** - List in GPT store

3. Add to GPT Store (if public):
   - Category: **Education**
   - Tags: `AI`, `Generative AI`, `Machine Learning`, `Education`, `Course`
   - Language: English

4. Click **"Confirm publish"**

---

## Troubleshooting

### Issue 1: Actions Not Working

**Symptoms:** GPT doesn't call the API

**Solutions:**
- Verify OpenAPI URL is accessible: `https://course-companion-fte.fly.dev/api/openapi.json`
- Check CORS is configured for ChatGPT domains
- Ensure authentication is set to "Bearer token"
- Try re-importing the OpenAPI specification

### Issue 2: Authentication Failures

**Symptoms:** GPT can't register/login users

**Solutions:**
- Verify backend is running: `curl https://course-companion-fte.fly.dev/health`
- Check authentication endpoints are accessible
- Review GPT instructions to ensure it's calling correct endpoints
- Test manually with curl:
  ```bash
  curl -X POST https://course-companion-fte.fly.dev/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"TestPass123!","full_name":"Test"}'
  ```

### Issue 3: Content Not Loading

**Symptoms:** GPT says it can't access course material

**Solutions:**
- Check database is seeded: Run migrations if needed
- Verify user has access to requested chapter
- Check user's subscription tier (free vs premium)
- Review GPT instructions about access control

### Issue 4: Search Not Working

**Symptoms:** GPT can't find information

**Solutions:**
- Verify search endpoint is working
- Test search manually:
  ```bash
  curl "https://course-companion-fte.fly.dev/api/v1/chapters/search?q=transformer&limit=5"
  ```
- Check content is indexed in database
- Ensure GPT is using search endpoint, not making up answers

---

## Advanced Configuration (Optional)

### Custom Domain

If you want a custom domain:

1. Add a CNAME record pointing to `course-companion-fte.fly.dev`
2. Update CORS origins in backend to include your custom domain
3. Update OpenAPI specification URLs
4. Reconfigure ChatGPT Actions with new URL

### Analytics & Monitoring

To monitor GPT usage:

1. Check backend logs: `flyctl logs --app course-companion-fte`
2. Monitor database for user registrations
3. Track API call patterns
4. Review quiz completion rates

### Rate Limiting

If you need rate limiting:

1. Add rate limiting middleware in FastAPI
2. Configure per-IP or per-user limits
3. Return 429 Too Many Requests when limit exceeded
4. Update GPT instructions about rate limits

---

## Best Practices

### For GPT Instructions

✅ **DO:**
- Be explicit about using course material only
- Emphasize zero-hallucination requirement
- Provide clear examples of interactions
- Include citation requirements
- Explain access control rules

❌ **DON'T:**
- Don't let GPT generate its own educational content
- Don't allow answers without searching first
- Don't skip authentication flow
- Don't ignore subscription tiers

### For User Experience

✅ **DO:**
- Provide clear next steps
- Celebrate progress and achievements
- Offer quizzes after explaining concepts
- Encourage continued learning
- Be patient and supportive

❌ **DON'T:**
- Don't overwhelm with too much content at once
- Don't skip fundamental explanations
- Don't ignore user's questions
- Don't move on too quickly

---

## Maintenance

### Regular Tasks

**Weekly:**
- Check backend logs for errors
- Monitor user registrations
- Review quiz completion rates
- Track API usage patterns

**Monthly:**
- Update course content if needed
- Review and improve quiz questions
- Analyze user progress patterns
- Optimize slow endpoints

**As Needed:**
- Scale up VMs if traffic increases
- Add Redis cache for better performance
- Implement new features based on feedback
- Fix bugs reported by users

---

## Support Resources

### Backend Management
```bash
# Check status
flyctl status --app course-companion-fte

# View logs
flyctl logs --app course-companion-fte

# Restart
flyctl apps restart course-companion-fte

# SSH into machine
flyctl ssh console --app course-companion-fte

# Scale VMs
flyctl scale count 2 --app course-companion-fte
```

### Documentation
- **Deployment Guide:** `DEPLOYMENT-SUCCESS.md`
- **Test Results:** `CHATGPT-INTEGRATION-TEST-RESULTS.md`
- **API Documentation:** https://course-companion-fte.fly.dev/api/openapi.json

---

## Success Checklist

Before going live, verify:

- [ ] OpenAPI specification imports successfully
- [ ] Authentication is set to "Bearer token"
- [ ] All endpoints are visible in Actions panel
- [ ] Registration flow works
- [ ] Login flow works
- [ ] Content retrieval works
- [ ] Search functionality works
- [ ] Quiz system works
- [ ] Progress tracking works
- [ ] Privacy policy is added
- [ ] GPT instructions are clear
- [ ] Profile image is added
- [ ] Description is compelling
- [ ] Tested all 6 features
- [ ] Ready to publish

---

## Next Steps After Configuration

1. **Test Thoroughly** - Try all features as a student would
2. **Gather Feedback** - Have beta users test the GPT
3. **Monitor Performance** - Check backend metrics regularly
4. **Iterate** - Improve based on user feedback
5. **Scale** - Add more VMs if traffic increases

---

Congratulations! 🎉

Your ChatGPT Custom GPT is now configured and ready to help students learn Generative AI!

For questions or issues, refer to the troubleshooting section or check the backend logs.
