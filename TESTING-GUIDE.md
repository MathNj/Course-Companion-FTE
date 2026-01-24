# ChatGPT Integration Testing Guide

Follow these steps to test the ChatGPT integration with ngrok.

## Step 1: Verify Backend is Running

Open a terminal and run:

```bash
# Check Docker containers
docker-compose ps

# Should show backend, postgres, and redis all healthy
```

Test the API:

```bash
# Health check
curl http://localhost:8001/health

# Get chapters list
curl http://localhost:8001/api/v1/chapters

# Get OpenAPI schema
curl http://localhost:8001/api/openapi.json > openapi-test.json
```

Expected results:
- Health check returns `{"status":"healthy"...}`
- Chapters returns array of 6 chapters
- OpenAPI returns full schema

## Step 2: Install and Start ngrok

### Download ngrok

1. Go to https://ngrok.com/download
2. Download for Windows
3. Extract to a folder (e.g., `C:\ngrok\`)
4. (Optional) Sign up for free account at https://dashboard.ngrok.com/signup
5. (Optional) Run: `ngrok config add-authtoken YOUR_TOKEN`

### Start ngrok Tunnel

Open a **new terminal** (keep backend running in the first one):

```bash
# Navigate to ngrok folder
cd C:\ngrok\

# Start tunnel to backend
ngrok http 8001
```

You'll see output like:
```
Session Status    online
Account           Your Name (Plan: Free)
Version           3.x.x
Region            United States (us)
Latency           -
Web Interface     http://127.0.0.1:4040
Forwarding        https://abc123xyz.ngrok-free.app -> http://localhost:8001

Connections       ttl     opn     rt1     rt5     p50     p90
                  0       0       0.00    0.00    0.00    0.00
```

**IMPORTANT**: Copy the `https://....ngrok-free.app` URL - you'll need it!

## Step 3: Test ngrok Tunnel

In a **third terminal**:

```bash
# Replace with your ngrok URL
curl https://your-ngrok-url.ngrok-free.app/health

# Should return: {"status":"healthy"...}
```

Test the API endpoints through ngrok:

```bash
# Get chapters
curl https://your-ngrok-url.ngrok-free.app/api/v1/chapters

# Get OpenAPI schema
curl https://your-ngrok-url.ngrok-free.app/api/openapi.json
```

All should work! ✅

## Step 4: Create Custom GPT

### 4a. Go to ChatGPT

1. Open https://chat.openai.com (requires ChatGPT Plus)
2. Click your profile icon (bottom left)
3. Select **"My GPTs"**
4. Click **"Create a GPT"**

### 4b. Configure Basic Info

In the "Configure" tab:

**Name**:
```
Course Companion FTE
```

**Description**:
```
Your AI-powered learning companion for mastering Generative AI fundamentals. Access structured lessons, take quizzes, and track your progress through 6 comprehensive chapters.
```

**Instructions**:
1. Open `chatgpt-app/instructions.md` in a text editor
2. **Copy the ENTIRE file** (Ctrl+A, Ctrl+C)
3. Paste into the "Instructions" field

**Conversation starters** (add these 4):
```
What chapters can I learn?
Start with Chapter 1
Quiz me on what I've learned
How's my progress?
```

### 4c. Add Actions

1. Scroll down to **"Actions"** section
2. Click **"Create new action"**
3. Click **"Import from URL"**
4. Enter your ngrok OpenAPI URL:
   ```
   https://your-ngrok-url.ngrok-free.app/api/openapi.json
   ```
5. Click **"Import"**

You should see 5 actions imported:
- ✅ get_chapters
- ✅ get_chapter
- ✅ get_quiz
- ✅ submit_quiz
- ✅ get_progress

**Authentication**: Select **"None"** (for testing)

**Privacy**: Select **"Only me"** (for testing)

### 4d. Save GPT

Click **"Create"** (top right)

## Step 5: Test the GPT!

Now test each feature:

### Test 1: List Chapters

In the GPT chat:
```
You: "What chapters can I learn?"
```

**Expected**:
- GPT calls `get_chapters()` (you'll see "Used get_chapters" above response)
- Lists all 6 chapters with descriptions
- Mentions free (1-3) vs premium (4-6) tiers

**Verify**: Click the action call to see the API response

### Test 2: Get Chapter Content

```
You: "Show me Chapter 1"
```

**Expected**:
- GPT calls `get_chapter("chapter-1")`
- Presents chapter title: "Introduction to Generative AI"
- Shows learning objectives
- Offers to walk through sections
- Uses content from the API response (not GPT's knowledge)

**Verify**:
- Click the action call
- Compare GPT's explanation to the API response
- Ensure GPT is using pre-authored content

### Test 3: Take a Quiz

```
You: "I want to take the Chapter 1 quiz"
```

**Expected**:
- GPT calls `get_quiz("chapter-1-quiz")`
- Shows quiz info (10 questions, 70% to pass)
- Starts presenting questions
- Questions match the quiz JSON file

**Verify**: Check that answer options match `backend/content/quizzes/chapter-1-quiz.json`

### Test 4: Submit Quiz

Answer all 10 questions, then:

```
You: "Submit my answers"
```

Or provide answers in this format:
```
You: "q1: option_a, q2: option_b, q3: false, q4: option_b, q5: option_b, q6: false, q7: code generation and debugging, q8: true, q9: option_b, q10: bias and privacy"
```

**Expected**:
- GPT calls `submit_quiz()` with your answers
- Shows your score (e.g., "86.67%")
- Lists correct answers ✓
- Shows explanations for incorrect answers
- Celebrates if you passed 🎉
- Mentions chapter completion

**Verify**:
- Score matches grading logic
- Explanations match the quiz JSON
- Chapter progress updated in backend

### Test 5: Check Progress

```
You: "How am I doing?"
```

**Expected**:
- GPT calls `get_progress()`
- Shows completion percentage
- Displays current streak (e.g., "7-day streak 🔥")
- Lists milestones achieved
- Shows quiz statistics
- Provides encouragement

**Verify**: Progress data matches backend state

### Test 6: Premium Content (Freemium Gating)

```
You: "Show me Chapter 4"
```

**Expected** (if not logged in as premium user):
- GPT calls `get_chapter("chapter-4")`
- Receives 403 Forbidden response
- Explains this is premium content
- Mentions what you'd learn in Chapter 4
- Suggests continuing with free chapters
- NOT pushy about upgrading

**Verify**: 403 response handled gracefully

## Step 6: Advanced Testing

### Content Accuracy Test

```
You: "According to this course, what is generative AI?"
```

**Expected**:
- GPT calls `get_chapter("chapter-1")`
- Quotes from Section 1-1
- Uses exact definitions from course material
- Does NOT use GPT's own training data

**How to verify**:
1. Click the action call to see API response
2. Find Section 1-1 in the response
3. Compare GPT's explanation to the section content
4. They should match closely!

### Zero-Hallucination Test

```
You: "Explain transformers in your own words"
```

**Watch for**:
- GPT should call `get_chapter("chapter-2")` first
- Should reference the course content
- Should NOT generate explanation from its training
- Might say "Let me get the course material on transformers..."

**Red flag**: If GPT explains without calling an action, the instructions need strengthening

### Error Handling Test

```
You: "Show me Chapter 10"
```

**Expected**:
- GPT recognizes invalid chapter
- Explains only 6 chapters exist
- Lists available chapters
- Suggests a valid chapter

```
You: "Quiz me on Chapter 100"
```

**Expected**:
- Similar graceful handling
- Redirects to valid quiz

## Troubleshooting

### GPT Not Calling Actions

**Symptom**: GPT answers questions from its own knowledge without calling API

**Fix**:
1. Check instructions were fully copied
2. Try explicit prompt: "Use the get_chapter action to show me Chapter 1"
3. Verify actions are properly configured in GPT settings
4. Check ngrok tunnel is still running

### 403/404 Errors

**Symptom**: GPT says "I can't access that"

**Check**:
1. Is ngrok still running? (tunnels expire on free tier)
2. Is backend still running? (`docker-compose ps`)
3. Test ngrok URL directly: `curl https://your-url.ngrok-free.app/health`
4. Check action configuration uses correct URL

### Timeout Errors

**Symptom**: "The action took too long"

**Fix**:
1. Check backend logs: `docker-compose logs backend`
2. Verify database is responding
3. Check network connectivity
4. Try action again (may be temporary)

### Content Doesn't Match Course

**Symptom**: GPT gives different explanations than course files

**Fix**:
1. Strengthen instructions with more "ALWAYS call get_chapter" emphasis
2. Test with explicit: "What does Chapter 1 say about AI?"
3. Verify API responses contain expected content
4. Compare GPT responses to `backend/content/chapters/chapter-1.json`

## Success Criteria

✅ All 5 actions callable by GPT
✅ Chapter content retrieved and presented accurately
✅ Quizzes work end-to-end (retrieve → answer → grade)
✅ Progress tracking shows streaks and milestones
✅ Freemium gating blocks premium content appropriately
✅ GPT uses API content, not its own knowledge
✅ Error handling is graceful
✅ Conversation flow is natural and helpful

## Next Steps After Testing

Once everything works:

1. **Deploy backend to production**:
   - Fly.io, Railway, or Render
   - Get permanent HTTPS URL

2. **Update GPT with production URL**:
   - Edit action configuration
   - Import from production OpenAPI URL

3. **Make GPT public** (optional):
   - Change privacy to "Anyone with a link"
   - Share with beta testers

4. **Gather feedback**:
   - How's the learning experience?
   - Are explanations clear?
   - Is navigation intuitive?

5. **Iterate**:
   - Update instructions based on usage
   - Improve content based on feedback
   - Add more teaching modes

## Monitoring

While testing, keep an eye on:

```bash
# Watch backend logs
docker-compose logs -f backend

# Check ngrok requests
# Visit http://127.0.0.1:4040 in browser for ngrok inspector
```

The ngrok web interface (http://127.0.0.1:4040) shows:
- All requests made to your tunnel
- Request/response details
- Timing information
- Errors

Very useful for debugging! 🔍

---

**Happy testing! 🚀**

If you encounter issues, check:
1. Backend logs
2. ngrok inspector
3. ChatGPT action responses (click on them)
4. Compare to `chatgpt-app/test-scenarios.md` for expected behaviors
