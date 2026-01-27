# ChatGPT App Creation - Action Checklist

## Step-by-Step Instructions

---

## Phase 1: Backend Deployment (30 minutes)

### Option A: Quick Testing with ngrok ⭐ **RECOMMENDED FOR TODAY**

- [ ] **Step 1.1: Install ngrok**
  ```bash
  # Download from https://ngrok.com/download
  # Or: choco install ngrok (Windows)
  ```

- [ ] **Step 1.2: Start your backend APIs**
  ```bash
  # Terminal 1
  cd backend
  python simple_r2_api.py

  # Terminal 2
  cd backend
  python simple_quiz_api.py

  # Terminal 3
  cd backend
  python simple_progress_api.py
  ```

- [ ] **Step 1.3: Create ngrok tunnels**
  ```bash
  # Terminal 4
  ngrok http 8000  # Content API

  # Terminal 5
  ngrok http 8001  # Quiz API

  # Terminal 6
  ngrok http 8002  # Progress API
  ```

- [ ] **Step 1.4: Copy the ngrok URLs**
  ```
  You'll get URLs like:
  - https://abc123.ngrok.io (Content)
  - https://def456.ngrok.io (Quiz)
  - https://ghi789.ngrok.io (Progress)
  ```

---

### Option B: Deploy to Railway (10 minutes) ⭐ **ALTERNATIVE**

- [ ] **Step 1.1: Create Railway account**
  - Go to: https://railway.app
  - Sign up with GitHub

- [ ] **Step 1.2: Create new project**
  - Click "New Project"
  - Click "Deploy from GitHub"
  - Select your repository

- [ ] **Step 1.3: Configure deployment**
  - Root directory: `backend`
  - Start command: `python simple_r2_api.py`
  - Click "Deploy"

- [ ] **Step 1.4: Add environment variables**
  - In Railway dashboard, add R2 credentials from `.env`

- [ ] **Step 1.5: Get public URL**
  - Railway will give you: `https://your-app.railway.app`

---

## Phase 2: Create ChatGPT App (20 minutes)

- [ ] **Step 2.1: Access OpenAI Dashboard**
  - Go to: https://platform.openai.com
  - Click "Apps" in left sidebar
  - URL: https://platform.openai.com/apps

- [ ] **Step 2.2: Create new app**
  - Click "Create new app" or "New App"
  - Fill in details:
    ```
    Name: Course Companion FTE - Generative AI
    Description: AI-powered tutor for mastering Generative AI fundamentals
    Category: Education
    ```

- [ ] **Step 2.3: Configure model**
  - Model: GPT-4o (recommended)
  - Click "Create"

---

## Phase 3: Configure Capabilities (15 minutes)

- [ ] **Step 3.1: Add Action APIs**

  In app configuration, go to "Capabilities" → "Actions" → "Add Action"

  **API 1: Content API**
  - Name: Course Content
  - Base URL: [Your ngrok/Railway URL for port 8000]
  - Description: Fetch course chapters and search content
  - Add endpoints:
    - GET /chapters
    - GET /chapters/{chapter_id}
    - GET /search?q={query}

  **API 2: Quiz API**
  - Name: Quiz System
  - Base URL: [Your ngrok/Railway URL for port 8001]
  - Description: Take quizzes and get graded feedback
  - Add endpoints:
    - GET /quizzes
    - GET /quizzes/{quiz_id}
    - POST /quizzes/{quiz_id}/submit

  **API 3: Progress API**
  - Name: Progress Tracker
  - Base URL: [Your ngrok/Railway URL for port 8002]
  - Description: Track learning progress and achievements
  - Add endpoints:
    - GET /progress/dashboard
    - POST /progress/chapters/{chapter_id}/update
    - POST /progress/activity

- [ ] **Step 3.2: Test API connectivity**
  - Open each endpoint URL in browser
  - Should return JSON (not error)
  - Example: `https://your-url.com/chapters`

---

## Phase 4: Add Skills (20 minutes)

- [ ] **Step 4.1: Go to Skills section**
  - In app dashboard, click "Skills"

- [ ] **Step 4.2: Add socratic-tutor skill**
  - Click "Add skill"
  - Name: Socratic Tutor
  - Description: Guides students to discover answers through questioning
  - Instructions: Copy from `.claude/skills/socratic-tutor/SKILL.md`
  - Trigger phrases: "I'm stuck", "don't tell me the answer", "guide me"
  - Click "Save"

- [ ] **Step 4.3: Add concept-explainer skill**
  - Name: Concept Explainer
  - Description: Explains concepts at learner's level using retrieved course content
  - Instructions: Copy from `.claude/skills/concept-explainer/SKILL.md`
  - Trigger phrases: "explain X", "what is Y", "help me understand"
  - Click "Save"

- [ ] **Step 4.4: Add quiz-master skill**
  - Name: Quiz Master
  - Description: Transforms quizzes into supportive learning experiences
  - Instructions: Copy from `.claude/skills/quiz-master/SKILL.md`
  - Trigger phrases: "quiz me", "test my knowledge", "practice"
  - Click "Save"

- [ ] **Step 4.5: Add progress-motivator skill**
  - Name: Progress Motivator
  - Description: Celebrates achievements and maintains motivation
  - Instructions: Copy from `.claude/skills/progress-motivator/SKILL.md`
  - Trigger phrases: "how am I doing", "show my progress", "my achievements"
  - Click "Save"

---

## Phase 5: Configure App Instructions (10 minutes)

- [ ] **Step 5.1: Add system instructions**
  - Go to "Instructions" section
  - Add instructions from `CHATGPT_APP_SETUP_GUIDE.md` (Step 6)
  - Or use this summary:

  ```markdown
  You are an AI tutor for Generative AI Fundamentals course.

  Your capabilities:
  1. Deliver course content via Content API
  2. Guide students through Socratic tutoring
  3. Explain concepts at learner's level
  4. Administer quizzes with immediate feedback
  5. Track progress and celebrate achievements

  Key principles:
  - Always fetch content before answering (groundedness)
  - Ask questions before explaining (Socratic method)
  - Be encouraging and supportive
  - Celebrate progress and achievements

  Use APIs to retrieve content, never make it up.
  ```

- [ ] **Step 5.2: Save instructions**

---

## Phase 6: Test Your App (15 minutes)

- [ ] **Step 6.1: Open your app in ChatGPT**
  - Go to: https://chat.openai.com/g/[YOUR_APP_ID]
  - Or find it in "Explore" → "Your Apps"

- [ ] **Step 6.2: Test content retrieval**
  ```
  User prompt: "What chapters are available?"
  Expected: Should list all 4 chapters
  ```

- [ ] **Step 6.3: Test Socratic tutoring**
  ```
  User prompt: "I'm stuck on understanding emergence. Don't tell me the answer."
  Expected: Should ask guiding questions, not give answer
  ```

- [ ] **Step 6.4: Test quiz functionality**
  ```
  User prompt: "Give me a quiz on Chapter 1.
  Expected: Should present quiz questions
  ```

- [ ] **Step 6.5: Test progress tracking**
  ```
  User prompt: "How am I doing?"
  Expected: Should show dashboard with completion, streak, achievements
  ```

- [ ] **Step 6.6: Test concept explanation**
  ```
  User prompt: "Explain what an LLM is."
  Expected: Should fetch Chapter 2 and explain at appropriate level
  ```

---

## Phase 7: Publish App (5 minutes)

- [ ] **Step 7.1: Go to Publishing section**
  - In app dashboard

- [ ] **Step 7.2: Choose visibility**
  - **Private** - Only you (for testing)
  - **Unlisted** - Anyone with link (for sharing with judges)
  - **Public** - Discoverable (for production)

- [ ] **Step 7.3: Click "Publish"**

- [ ] **Step 7.4: Copy share URL**
  ```
  URL: https://chat.openai.com/g/[YOUR_APP_ID]
  ```

---

## Troubleshooting Quick Guide

### Problem: APIs not accessible

**Solution:**
- Check ngrok is running
- Verify backend servers are running
- Test API URLs directly in browser
- Check CORS settings

### Problem: Skills not triggering

**Solution:**
- Use exact trigger phrases
- Check skill instructions are clear
- Test in fresh chat context
- Verify skills are saved

### Problem: App not creating

**Solution:**
- Check OpenAI account permissions
- Verify you have ChatGPT Plus/Team access
- Try different browser
- Contact OpenAI support

---

## Documentation Files Created

- ✅ `CHATGPT_APP_SETUP_GUIDE.md` - Detailed setup instructions
- ✅ `BACKEND_DEPLOYMENT_GUIDE.md` - Deployment options
- ✅ `CHATGPT_APP_ACTION_CHECKLIST.md` - This checklist

---

## Time Estimates

| Phase | Task | Time |
|-------|------|------|
| 1 | Deploy backend (ngrok) | 30 min |
| 2 | Create ChatGPT App | 20 min |
| 3 | Configure capabilities | 15 min |
| 4 | Add skills | 20 min |
| 5 | Add instructions | 10 min |
| 6 | Test functionality | 15 min |
| 7 | Publish app | 5 min |
| **Total** | | **~2 hours** |

---

## Success Criteria

Your ChatGPT App is working when:

✅ App responds to user messages
✅ Can list available chapters
✅ Can fetch chapter content
✅ Can administer quizzes
✅ Can track progress
✅ Skills activate on trigger phrases
✅ All API calls succeed
✅ End-to-end flow works

---

## Next Steps After Creation

1. **Test thoroughly** - Try all features
2. **Get feedback** - Share with team members
3. **Document issues** - Note any bugs
4. **Iterate** - Fix problems and improve
5. **Prepare demo** - For hackathon presentation

---

**Estimated Time to Complete: 2-3 hours**

**Your ChatGPT App will be ready for Phase 1 hackathon demo!**
