# 🔴 LIVE CONFIGURATION WALKTHROUGH

Follow these steps IN ORDER while you're on chat.openai.com

---

## STEP 1: Open ChatGPT ✅

**Action:** Open https://chat.openai.com in your browser

**What you should see:**
- ChatGPT interface with your chat history
- Sidebar on the left

**When done:** Move to Step 2

---

## STEP 2: Access GPT Creation ✅

**Action:**
1. Look at the left sidebar
2. Click on **"Explore GPTs"** (sometimes labeled just "Explore")

**What you should see:**
- A page showing GPTs
- A button that says **"Create a GPT"** (usually top right)

**When done:** Move to Step 3

---

## STEP 3: Start Creating Your GPT ✅

**Action:** Click the **"Create a GPT"** button

**What you should see:**
- GPT configuration page
- Two-column layout
- Left side: Preview
- Right side: Configuration

**When done:** Move to Step 4

---

## STEP 4: Fill In Basic Information ✅

### Name Field:
```
Course Companion FTE - Generative AI
```

### Description (Short):
```
Expert tutor for the Generative AI Fundamentals course. Provides grounded answers using only course material, tracks your progress, and administers quizzes.
```

### Instructions (CRITICAL - COPY THIS EXACTLY):

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

## Important Notes

- Always verify you have authentication before attempting to access content
- If authentication fails, guide the user to register/login
- Never provide premium content to free-tier users
- Always cite your sources (Chapter X, Section Y)
- When you don't find information in the course material, say so explicitly

Remember: Your strength is providing ACCURATE, GROUNDED answers from the course material, not generating new information.
```

**When done:** Move to Step 5

---

## STEP 5: Configure Actions (API Integration) ✅

**This is CRITICAL - This connects your GPT to the backend**

### 5.1 Find the Actions Section

**Action:** Scroll down on the configuration page until you see **"Actions"**

**What you should see:**
- A section that says "Actions" or "Configure actions"
- A button that says **"Create new action"** or **"Add action"**

**When done:** Click that button and move to 5.2

---

### 5.2 Create New Action

**Action:** After clicking "Create new action", select **"OpenAPI"**

**What you should see:**
- Option to import from URL
- Option to import manually
- Option to paste OpenAPI JSON

**When done:** Move to 5.3

---

### 5.3 Import OpenAPI Specification

**IMPORTANT DECISION POINT:**

**Option A: Automatic Import (RECOMMENDED - Try This First)**

**Action:**
1. In the "Import from URL" field, paste this EXACT URL:
```
https://course-companion-fte.fly.dev/api/openapi.json
```

2. Click **"Import"** or **"Fetch"** button

**What should happen:**
- ChatGPT will load the OpenAPI specification
- All endpoints will appear
- You'll see a list of API endpoints

**If this works:** Skip to Step 5.4
**If this fails:** Use Option B below

---

**Option B: Manual Import (If Automatic Fails)**

**Action:**
1. Open a new browser tab
2. Go to: https://course-companion-fte.fly.dev/api/openapi.json
3. Select ALL the text (Ctrl+A or Cmd+A)
4. Copy ALL the text (Ctrl+C or Cmd+C)
5. Go back to ChatGPT
6. Click "Import manually" or "Paste"
7. Paste the OpenAPI JSON into the editor

**When done:** Move to 5.4

---

### 5.4 Configure Authentication

**Action:**
1. Look for the **"Authentication"** section in Actions
2. Click on it or expand it
3. Select **"Bearer token"** from the dropdown
4. Leave the **"Bearer token prefix"** as `Bearer` (it should be default)
5. Click **"Save"**

**Critical:** Make sure it says "Bearer token" NOT "Custom" or anything else

**When done:** Move to Step 6

---

### 5.5 Verify Endpoints Are Imported

**Action:** Look through the list of imported endpoints

**You should see these endpoints:**

**Authentication:**
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- POST /api/v1/auth/refresh
- GET /api/v1/auth/me

**Chapters:**
- GET /api/v1/chapters
- GET /api/v1/chapters/{chapter_id}
- GET /api/v1/chapters/search

**Quizzes:**
- GET /api/v1/quizzes/{quiz_id}
- POST /api/v1/quizzes/{quiz_id}/submit

**Progress:**
- GET /api/v1/progress
- GET /api/v1/progress/streak
- GET /api/v1/progress/chapters/{chapter_id}
- POST /api/v1/progress/activity

**If you see all these:** Great! Move to Step 6
**If some are missing:** The import may have failed - try again

**When done:** Move to Step 6

---

## STEP 6: Add Privacy Policy ✅

**Action:**
1. Scroll down to the **"Privacy"** section
2. You should see a text area for privacy policy
3. Copy and paste this EXACT text:

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

**When done:** Move to Step 7

---

## STEP 7: Configure Profile (Optional) ✅

**Action:** Scroll to the profile section

**Profile Image:**
- You can upload an image or let ChatGPT generate one
- Suggestion: Use something related to education/AI

**Description (for GPT store - if making public):**
```
Your personal tutor for the Generative AI Fundamentals course. Get grounded answers from course material, track your progress, take quizzes, and master AI concepts with zero hallucination.

Access to:
- 6 comprehensive chapters on Generative AI
- Interactive quizzes with instant feedback
- Progress tracking and streaks
- Grounded Q&A (no made-up answers)

Free tier includes Chapters 1-3. Premium unlocks all content.
```

**When done:** Move to Step 8

---

## STEP 8: TEST YOUR GPT ✅

**CRITICAL STEP - Test before publishing!**

### Test 1: Registration

**In the ChatGPT preview (left side), type:**
```
Hi, I'm new here. I want to register for the course. My email is test@example.com and password is TestPass123!
```

**Expected Result:**
- GPT should call the register API
- Should say something like "I'll register you with email test@example.com"
- Should confirm registration successful
- Should welcome you to the course

**If this works:** ✅ Great! Move to Test 2
**If this fails:** Check Actions configuration

---

### Test 2: Access Content

**Type:**
```
What topics are covered in Chapter 1?
```

**Expected Result:**
- GPT should call the chapters API
- Should retrieve Chapter 1 content
- Should describe what Chapter 1 is about
- Should list main topics

**If this works:** ✅ Great! Move to Test 3
**If this fails:** Check if GPT can access the API

---

### Test 3: Grounded Q&A (Search)

**Type:**
```
What is a Large Language Model?
```

**Expected Result:**
- GPT should call the SEARCH API first
- Should search for "Large Language Model"
- Should provide information from the course
- Should cite which chapter/section it came from
- Should NOT make up information

**If this works:** ✅ Great! Move to Test 4
**If this fails:** Check if search endpoint is working

---

### Test 4: Quiz

**Type:**
```
Give me a quiz on Chapter 1.
```

**Expected Result:**
- GPT should call the quiz API
- Should get Chapter 1 quiz
- Should present quiz questions
- Should wait for your answers
- Should grade your answers when you provide them

**If this works:** ✅ Great! Move to Test 5
**If this fails:** Check quiz endpoints

---

### Test 5: Progress

**Type:**
```
Show my learning progress.
```

**Expected Result:**
- GPT should call the progress API
- Should show your completion stats
- Should display quiz scores if any
- Should show streak information

**If this works:** ✅ All tests passed!
**If this fails:** Check progress endpoint

---

## STEP 9: Publish Your GPT ✅

**Action:**
1. Look for the **"Publish"** or **"Create"** button (usually top right)
2. Click on it
3. Choose visibility:
   - **"Only me"** - For your personal use
   - **"Only people with a link"** - Share with specific people
   - **"Public"** - List in GPT store (requires review)
4. Click **"Confirm"** or **"Publish"**

**What happens:**
- Your GPT is saved and published
- You can now use it in ChatGPT
- If public, it goes to the GPT store

**When done:** Congratulations! 🎉

---

## TROUBLESHOOTING

### Problem: Can't find "Explore GPTs"

**Solution:**
- Make sure you're logged in
- Look for "Explore" in the left sidebar
- Or go directly to: https://chat.openai.com/gpts

### Problem: OpenAPI import fails

**Solution:**
1. Check if backend is running: Visit https://course-companion-fte.fly.dev/health
2. You should see: `{"status":"degraded","environment":"production"...}`
3. If not, the backend is down - check deployment

### Problem: GPT doesn't call the API

**Solution:**
1. Verify Actions are configured
2. Check that "Bearer token" authentication is selected
3. Make sure endpoints are visible in Actions panel
4. Try re-importing the OpenAPI spec

### Problem: Authentication fails

**Solution:**
1. Check backend is operational
2. Verify you're using the correct API URL
3. Make sure "Bearer token" is selected
4. Try the test prompts again

### Problem: Content not loading

**Solution:**
1. Make sure you completed registration first
2. Check if GPT is calling the right endpoint
3. Verify user has access to requested chapter
4. Check subscription tier (free vs premium)

---

## CHECKLIST

Before you finish, verify:

- [ ] OpenAPI spec imported successfully
- [ ] Authentication set to "Bearer token"
- [ ] GPT instructions pasted correctly
- [ ] Privacy policy added
- [ ] All 5 tests passed
- [ ] GPT provides cited answers
- [ ] GPT doesn't make up information
- [ ] Search functionality works
- [ ] Quiz system works
- [ ] Progress tracking works

---

## SUCCESS CRITERIA

Your GPT is successfully configured when:

✅ You can register new users
✅ You can access chapter content
✅ Search returns relevant, cited results
✅ Quizzes can be taken and graded
✅ Progress displays correctly
✅ GPT says "I found this in Chapter X, Section Y"
✅ GPT says "I couldn't find that in the course" when appropriate
✅ NO made-up information or hallucination

---

## NEED HELP?

If you get stuck:

1. **Check this guide** - Make sure you followed all steps
2. **Read the detailed guide** - CHATGPT-CONFIGURATION-GUIDE.md
3. **Verify backend** - https://course-companion-fte.fly.dev/health
4. **Test manually** - Use curl to test endpoints
5. **Check logs** - Fly.io logs may show errors

---

## YOU'RE READY! 🚀

Follow this guide step-by-step and you'll have your ChatGPT Custom GPT configured in about 10-15 minutes!

**Good luck!** 🎓
