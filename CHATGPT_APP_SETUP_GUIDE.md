# ChatGPT App Setup Guide

## Step-by-Step Instructions

---

## Prerequisites

Before starting, ensure you have:
- ✅ OpenAI API account with access to ChatGPT
- ✅ Backend APIs running (ports 8000, 8001, 8002)
- ✅ Backend accessible from internet (or use ngrok for local testing)
- ✅ Skills defined in `.claude/skills/` directory

---

## Step 1: Access OpenAI Dashboard

1. Go to: https://platform.openai.com
2. Sign in with your OpenAI account
3. Navigate to: **Dashboard → Apps** (or use direct URL)
   - URL: https://platform.openai.com/apps

---

## Step 2: Create New App

1. Click **"Create new app"** or **"New App"**
2. Fill in app details:

### Basic Information

```
Name: Course Companion FTE - Generative AI
Description: Your AI-powered tutor for mastering Generative AI fundamentals. Learn LLMs, transformers, and prompt engineering through interactive quizzes, Socratic tutoring, and personalized progress tracking.
Category: Education
```

### App Configuration

```
Type: Custom ChatGPT
Visibility: Private (for testing) → Public (for production)
Model: GPT-4o (recommended)
```

3. Click **"Create"** or **"Save"**

---

## Step 3: Configure Capabilities

### 3.1 Add API Capabilities

In the app configuration:

1. **Add Action Capabilities** (for calling your backend APIs)

2. Configure API Specifications:

**Add these three API domains:**

#### API 1: Content API
```yaml
Name: Course Content
Base URL: http://localhost:8000  # Replace with your deployed URL
Description: Fetch course chapters and search content

Endpoints:
  GET /chapters
    - Description: List all available chapters
    - Returns: Array of chapter metadata

  GET /chapters/{chapter_id}
    - Description: Get full chapter content
    - Parameters:
      - chapter_id: string (e.g., "1", "chapter-1")
    - Returns: Chapter content with markdown

  GET /search
    - Description: Search course content
    - Parameters:
      - q: search query string
    - Returns: Matching chapters with previews
```

#### API 2: Quiz API
```yaml
Name: Quiz System
Base URL: http://localhost:8001  # Replace with your deployed URL
Description: Take quizzes and get graded feedback

Endpoints:
  GET /quizzes
    - Description: List all available quizzes
    - Returns: Array of quiz metadata

  GET /quizzes/{quiz_id}
    - Description: Get quiz questions
    - Parameters:
      - quiz_id: string (e.g., "chapter-1-quiz")
      - include_answers: boolean (optional)
    - Returns: Quiz questions

  POST /quizzes/{quiz_id}/submit
    - Description: Submit quiz answers for grading
    - Parameters:
      - quiz_id: string
      - answers: object {question_id: answer}
    - Returns: Graded results with explanations
```

#### API 3: Progress API
```yaml
Name: Progress Tracker
Base URL: http://localhost:8002  # Replace with your deployed URL
Description: Track learning progress and achievements

Endpoints:
  GET /progress/dashboard
    - Description: Get comprehensive progress summary
    - Returns: Overall completion, streaks, achievements

  GET /progress/chapters/{chapter_id}
    - Description: Get progress for specific chapter
    - Returns: Chapter progress data

  POST /progress/chapters/{chapter_id}/update
    - Description: Update chapter progress
    - Parameters:
      - chapter_id: string
      - time_spent_seconds: integer
      - completion_percentage: integer
      - mark_completed: boolean
    - Returns: Updated progress with milestones

  POST /progress/activity
    - Description: Record learning activity
    - Returns: Updated streak info

  GET /progress/achievements
    - Description: Get all achievements
    - Returns: Earned and locked achievements
```

---

## Step 4: Upload Skills

### 4.1 Prepare Skills for Upload

Your skills are already defined in:
- `.claude/skills/socratic-tutor/SKILL.md`
- `.claude/skills/concept-explainer/SKILL.md`
- `.claude/skills/quiz-master/SKILL.md`
- `.claude/skills/progress-motivator/SKILL.md`

### 4.2 Add Skills to ChatGPT App

For each skill:

1. In ChatGPT App dashboard, go to **"Skills"** section
2. Click **"Add Skill"**
3. Choose **"Create custom skill"**
4. For each skill:

#### Skill 1: socratic-tutor
```yaml
Name: Socratic Tutor
Description: Guides learners to discover answers through questioning rather than direct instruction. Builds critical thinking and confidence.

Instructions:
# Copy from: .claude/skills/socratic-tutor/SKILL.md

Key Points:
- Ask questions before explaining
- Guide, don't solve
- Build on prior knowledge
- Progressive hints
- Grounded in course content only
- Never give direct answers unless requested
```

**Trigger Phrases:**
- "help me think"
- "I'm stuck"
- "don't tell me the answer"
- "guide me"
- "walk me through it"

#### Skill 2: concept-explainer
```yaml
Name: Concept Explainer
Description: Explains concepts at learner's level using retrieved course content.

Instructions:
# Copy from: .claude/skills/concept-explainer/SKILL.md

Key Points:
- Explain at appropriate level
- Use analogies and examples
- Break down complex ideas
- Grounded in course content
- Check understanding
```

**Trigger Phrases:**
- "explain X"
- "what is Y"
- "help me understand"
- "tell me about"

#### Skill 3: quiz-master
```yaml
Name: Quiz Master
Description: Transforms quizzes into supportive learning experiences with immediate feedback and encouragement.

Instructions:
# Copy from: .claude/skills/quiz-master/SKILL.md

Key Points:
- Reduce anxiety
- Celebrate effort
- Provide immediate feedback
- Explain correct/incorrect answers
- Adapt difficulty
- Deterministic grading only
```

**Trigger Phrases:**
- "quiz me"
- "test my knowledge"
- "practice questions"
- "take a quiz"

#### Skill 4: progress-motivator
```yaml
Name: Progress Motivator
Description: Celebrates achievements, maintains motivation, and tracks learning streaks.

Instructions:
# Copy from: .claude/skills/progress-motivator/SKILL.md

Key Points:
- Celebrate progress
- Highlight streaks
- Unlock achievements
- Encourage consistency
- Motivate continued learning
```

**Trigger Phrases:**
- "how am I doing"
- "show my progress"
- "my achievements"
- "track my learning"

5. Click **"Save"** for each skill

---

## Step 5: Configure Authentication

### 5.1 OAuth Setup (Optional but Recommended)

For user authentication and progress tracking:

1. Go to **"Authentication"** in app settings
2. Enable **"OAuth"**
3. Configure:

```yaml
OAuth Provider: Custom (or your preferred provider)
Callback URL: https://chat.openai.com/a/YOUR_APP_ID
Scopes: email, profile
```

### 5.2 Alternative: User ID in ChatGPT Context

For Phase 1 testing, ChatGPT provides a user context:
- Use `user_id` from ChatGPT message context
- Pass to backend APIs
- Backend tracks progress per user

---

## Step 6: Instructions for ChatGPT

In the **"Instructions"** section of your app, add:

```markdown
# Course Companion FTE - Generative AI Fundamentals

You are an AI tutor helping students master Generative AI fundamentals through an interactive course on LLMs, Transformers, and Prompt Engineering.

## Your Capabilities

1. **Content Delivery**: Access 4 chapters of course material via Content API
2. **Socratic Tutoring**: Guide students to discover answers through questioning
3. **Concept Explanation**: Explain complex topics at learner's level
4. **Interactive Quizzes**: Administer quizzes with immediate, supportive feedback
5. **Progress Tracking**: Monitor student progress, streaks, and achievements

## Key Principles

- **Groundedness**: Always use retrieved course content - never invent information
- **Zero-Backend-LLM**: All explanation happens here (in ChatGPT), backend only serves content
- **Encouragement First**: Celebrate effort and progress, reduce anxiety
- **Discovery-Based**: Ask questions before explaining when appropriate

## Workflow

1. Understand what the student wants to learn
2. Use APIs to fetch relevant content
3. Guide them through the material (using appropriate skill)
4. Track their progress
5. Celebrate achievements and maintain motivation

## When to Use Skills

- **socratic-tutor**: When student says "I'm stuck" or "don't tell me the answer"
- **concept-explainer**: When student asks "explain X" or "what is Y"
- **quiz-master**: When student wants to test knowledge
- **progress-motivator**: When checking progress or celebrating achievements

## Important

- Always call APIs before answering content questions
- Never make up course content - fetch it first
- Use retrieved content as your source of truth
- Be encouraging and supportive
- Celebrate progress and achievements
```

---

## Step 7: Test Configuration

### 7.1 Test API Connectivity

Before publishing, test that your backend APIs are accessible:

**Option A: Local Testing with ngrok**
```bash
# Install ngrok
# Then for each API:
ngrok http 8000  # Content API
ngrok http 8001  # Quiz API
ngrok http 8002  # Progress API

# Use the ngrok URLs in ChatGPT App configuration
```

**Option B: Deploy to Cloud**

Deploy your backend to:
- Cloudflare Workers
- Railway
- Fly.io
- Render

Get public URLs and update ChatGPT App configuration.

### 7.2 Test in ChatGPT Interface

1. Open your app in ChatGPT
2. Test queries:

**Test 1: Content Retrieval**
```
User: "What chapters are available?"
→ Should call GET /chapters
→ Should list all 4 chapters
```

**Test 2: Quiz Taking**
```
User: "Give me a quiz on Chapter 1"
→ Should call GET /quizzes/chapter-1-quiz
→ Should present questions
→ Should grade when answered
```

**Test 3: Progress Check**
```
User: "How am I doing?"
→ Should call GET /progress/dashboard
→ Should show completion, streak, achievements
```

**Test 4: Socratic Tutoring**
```
User: "I'm stuck on understanding emergence. Don't tell me the answer."
→ Should activate socratic-tutor skill
→ Should fetch Chapter 1 content
→ Should ask guiding questions
```

---

## Step 8: Publish App

Once testing is successful:

1. Go to **"Publishing"** section
2. Review app details
3. Set visibility:
   - **Private**: Only you can access (for testing)
   - **Unlisted**: Anyone with link can access
   - **Public**: Discoverable in ChatGPT store

4. Click **"Publish"**

---

## Step 9: Share App

### For Private Testing

Share the direct URL:
```
https://chat.openai.com/g/YOUR_APP_ID
```

### For Public Access

Provide the app name and URL to users.

---

## Troubleshooting

### Issue 1: APIs Not Accessible

**Problem**: ChatGPT can't reach your backend

**Solutions**:
- Use ngrok for local testing: `ngrok http 8000`
- Deploy backend to cloud (Railway, Fly.io, Render)
- Check CORS settings in backend
- Verify firewall rules

### Issue 2: Skills Not Triggering

**Problem**: Skills don't activate on trigger phrases

**Solutions**:
- Check trigger phrases in skill configuration
- Verify skill instructions are clear
- Test with exact trigger phrases
- Check ChatGPT app logs

### Issue 3: Authentication Errors

**Problem**: APIs returning 401/403

**Solutions**:
- For Phase 1: Use user_id from ChatGPT context
- For Phase 2: Implement full OAuth
- Check API keys if using OpenAI API
- Verify CORS configuration

---

## Configuration Files

### Update Backend URLs

Once deployed, update your skills with production URLs:

```yaml
# Local (development)
Content API: http://localhost:8000
Quiz API: http://localhost:8001
Progress API: http://localhost:8002

# Production (deployed)
Content API: https://your-backend.com/content
Quiz API: https://your-backend.com/quizzes
Progress API: https://your-backend.com/progress
```

---

## Summary Checklist

- [ ] OpenAI account created
- [ ] ChatGPT App created in dashboard
- [ ] App name and description set
- [ ] Capabilities configured (3 API domains)
- [ ] Skills uploaded (4 skills)
- [ ] Instructions added to app
- [ ] Backend APIs accessible (ngrok or deployed)
- [ ] API endpoints tested
- [ ] OAuth configured (optional)
- [ ] App tested in ChatGPT interface
- [ ] App published (private/public)

---

## Next Steps After App Creation

1. **Test End-to-End Flow**
   - User starts course
   - Takes Chapter 1 quiz
   - Progress is tracked
   - Achievements unlocked

2. **Implement User Auth** (if not done)
   - User registration
   - JWT tokens
   - Subscription tiers

3. **Complete Freemium**
   - Enforce access control
   - Premium upgrade flow

4. **Polish & Deploy**
   - Bug fixes
   - Performance optimization
   - Documentation

---

**Estimated Setup Time: 1-2 hours**

**Your ChatGPT App will be ready to use for the Phase 1 hackathon!**
