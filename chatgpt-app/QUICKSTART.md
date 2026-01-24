# ChatGPT App Quick Start Guide

Get the Course Companion FTE ChatGPT app running in **under 10 minutes**.

## Prerequisites

- ✅ Backend running (`docker-compose up` in `backend/`)
- ✅ ChatGPT Plus subscription
- ✅ ngrok installed (for local testing)

## 5-Step Setup

### Step 1: Start Backend (2 min)

```bash
cd backend
docker-compose up -d
```

Verify it's running:
```bash
curl http://localhost:8001/health
# Should return: {"status":"healthy"...}
```

### Step 2: Expose with ngrok (1 min)

```bash
# Download ngrok: https://ngrok.com/download
ngrok http 8001
```

You'll see:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8001
```

Copy that `https://abc123.ngrok.io` URL - you'll need it!

### Step 3: Test API Access (1 min)

```bash
# Replace with your ngrok URL
curl https://your-ngrok-url.ngrok.io/api/v1/chapters
```

Should return a list of chapters!

### Step 4: Create Custom GPT (3 min)

1. Go to: https://chat.openai.com
2. Click your profile → **"My GPTs"** → **"Create a GPT"**
3. Fill in:
   - **Name**: Course Companion FTE
   - **Description**: AI learning companion for Generative AI fundamentals
4. **Instructions**: Copy ALL text from `instructions.md` and paste
5. **Actions**:
   - Click "Create new action"
   - Click "Import from URL"
   - Enter: `https://your-ngrok-url.ngrok.io/api/openapi.json`
   - Click "Import"
   - Authentication: **None** (for testing)

### Step 5: Test It! (3 min)

In the GPT conversation:

```
You: "What chapters can I learn?"
```

GPT should call `get_chapters()` and list the 6 chapters!

```
You: "Show me Chapter 1"
```

GPT should call `get_chapter("chapter-1")` and present the content!

```
You: "Quiz me on Chapter 1"
```

GPT should call `get_quiz("chapter-1-quiz")` and start asking questions!

## Test Conversation Script

Copy/paste these to quickly verify all features:

```
1. "What chapters are available?"
   → Should call get_chapters() and list 6 chapters

2. "I want to learn Chapter 1"
   → Should call get_chapter("chapter-1") and show content

3. "Give me a quiz"
   → Should call get_quiz("chapter-1-quiz") and present questions

4. "My answers: q1: option_a, q2: option_b, q3: false, q4: option_b, q5: option_b, q6: false, q7: code generation, q8: true, q9: option_b, q10: bias"
   → Should call submit_quiz() and show graded results

5. "How's my progress?"
   → Should call get_progress() and show stats
```

## Common Issues

### "I can't access your API"
- ❌ **Problem**: ngrok URL expired or wrong
- ✅ **Fix**: Restart ngrok, update action URL in GPT

### GPT doesn't call actions
- ❌ **Problem**: Instructions not clear enough
- ✅ **Fix**: Ensure you copied ALL of `instructions.md`

### 403 Forbidden
- ❌ **Problem**: CORS not configured
- ✅ **Fix**: Check `backend/app/config.py` CORS settings

### Backend not responding
- ❌ **Problem**: Docker containers not running
- ✅ **Fix**: `docker-compose ps` to check status

## Next Steps

Once it's working:

1. **Try all chapters**: Test access to free (1-3) and premium (4-6) chapters
2. **Take a full quiz**: Complete all 10 questions and submit
3. **Check progress**: Verify streak tracking and milestones
4. **Test edge cases**: Try invalid chapter IDs, incomplete quiz submissions
5. **Get feedback**: Have someone else test the learning experience

## Tips for Best Results

**Ask the GPT to be explicit**:
```
You: "Show me Chapter 1 using the get_chapter action"
```

**Test error handling**:
```
You: "Show me Chapter 99" (should handle gracefully)
```

**Verify content accuracy**:
- Compare GPT's explanations to `backend/content/chapters/chapter-1.json`
- Make sure GPT is using API content, not its own knowledge

## Stopping

When done testing:

```bash
# Stop ngrok
Ctrl+C in ngrok terminal

# Stop backend
cd backend
docker-compose down
```

---

**Ready to learn? Let's go! 🚀**
