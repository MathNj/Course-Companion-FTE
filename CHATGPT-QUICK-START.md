# ChatGPT Configuration - Quick Reference

Fast-track configuration for ChatGPT Custom GPT integration.

---

## 1. OpenAPI Configuration

**URL to Import:**
```
https://course-companion-fte.fly.dev/api/openapi.json
```

**Authentication:** Bearer Token

---

## 2. GPT Instructions (Short Version)

```
You are an expert tutor for the "Generative AI Fundamentals" course.

CRITICAL: Use ONLY course material - never make up information (zero-hallucination).

Your capabilities:
- Retrieve and explain chapter content
- Search course material for answers
- Administer and grade quizzes
- Track student progress
- Provide grounded, cited answers

Rules:
1. ALWAYS search course material before answering
2. Cite sources (Chapter X, Section Y)
3. Never provide information not in the course
4. Check user's subscription tier (free = chapters 1-3, premium = all)
5. Suggest quizzes for practice

When asked questions:
1. Search the course material first
2. Present relevant information with citations
3. Offer related quiz questions

When teaching:
1. Retrieve chapter content
2. Present learning objectives
3. Explain key concepts
4. Offer to quiz them

Be encouraging, patient, and celebrate progress!
```

---

## 3. Quick Test Prompts

**Test Registration:**
```
Hi, I want to register for the course. My email is test@example.com
```

**Test Content Access:**
```
What is Chapter 1 about?
```

**Test Search:**
```
What is a transformer model in AI?
```

**Test Quiz:**
```
Quiz me on Chapter 1
```

**Test Progress:**
```
Show my progress
```

---

## 4. Privacy Policy (Short)

```
We collect email and learning progress to provide personalized education.
Data is stored securely, passwords are hashed, and tokens expire in 30 days.
We don't share your data. You can delete your account anytime.
All data is encrypted in transit and at rest.
```

---

## 5. Essential Endpoints

After importing OpenAPI spec, these should be available:

**Authentication:**
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- GET /api/v1/auth/me

**Content:**
- GET /api/v1/chapters
- GET /api/v1/chapters/{id}
- GET /api/v1/chapters/search

**Quizzes:**
- GET /api/v1/quizzes/{id}
- POST /api/v1/quizzes/{id}/submit

**Progress:**
- GET /api/v1/progress
- GET /api/v1/progress/streak

---

## 6. Troubleshooting Quick Fixes

**GPT not calling API?**
→ Re-import OpenAPI spec from URL
→ Check https://course-companion-fte.fly.dev/health

**Authentication failing?**
→ Verify backend is running
→ Check "Bearer token" is selected

**Content not loading?**
→ Ensure user is registered
→ Check chapter access (free vs premium)

**Search not working?**
→ Test: curl "https://course-companion-fte.fly.dev/api/v1/chapters/search?q=AI"
→ Verify database has content

---

## 7. Verification Checklist

Before publishing, verify:

- [ ] OpenAPI imports successfully
- [ ] Can register new user
- [ ] Can login
- [ ] Can list chapters
- [ ] Can get chapter content
- [ ] Search returns results
- [ ] Can get quiz
- [ ] Can submit quiz answers
- [ ] Can view progress
- [ ] All responses cite sources

---

## 8. Production URLs

**Backend:** https://course-companion-fte.fly.dev
**Health:** https://course-companion-fte.fly.dev/health
**OpenAPI:** https://course-companion-fte.fly.dev/api/openapi.json

---

## 9. Backend Status Check

```bash
# Check if backend is running
curl https://course-companion-fte.fly.dev/health

# Expected response:
{"status":"degraded","environment":"production","components":{"api":"operational","cache":"degraded"}}
```

---

## 10. Support

**Full Guide:** See `CHATGPT-CONFIGURATION-GUIDE.md`
**Test Results:** See `CHATGPT-INTEGRATION-TEST-RESULTS.md`
**Deployment Info:** See `DEPLOYMENT-SUCCESS.md`

---

## Configuration Steps Summary

1. Go to https://chat.openai.com
2. Click "Explore GPTs" → "Create a GPT"
3. Fill in name and description
4. Paste instructions (from section 2 above)
5. Configure Actions:
   - Import OpenAPI from: https://course-companion-fte.fly.dev/api/openapi.json
   - Set auth to "Bearer token"
6. Add privacy policy (from section 4 above)
7. Test with prompts from section 6 above
8. Publish!

---

**Estimated Configuration Time:** 10-15 minutes

**Ready to Configure?** Start at Step 1! 🚀
