# Testing ChatGPT Integration - Complete Guide

## Overview

This guide walks you through testing the ChatGPT Custom GPT integration with your Course Companion FTE backend.

## Prerequisites Checklist

- [ ] Backend API is running and accessible
- [ ] You have a ChatGPT Plus account (required for Custom GPTs)
- [ ] ngrok installed (for local testing) OR backend deployed to production

## Option A: Test with Production Backend (Recommended if deployed)

### Step 1: Verify Backend is Accessible

```bash
# Check if backend is accessible from internet
curl https://your-production-url.com/health

# Check OpenAPI spec is available
curl https://your-production-url.com/api/openapi.json
```

**Expected Response**:
```json
{"status":"healthy","environment":"production","components":{"api":"operational","cache":"operational"}}
```

### Step 2: Create Custom GPT

1. Go to https://chat.openai.com
2. Click on **"Explore GPTs"** in the left sidebar
3. Click **"Create a GPT"**
4. Click **"Configure"** tab

### Step 3: Configure Your GPT

#### 3.1. Basic Settings
- **Name**: Course Companion FTE
- **Description**: AI tutor for learning Generative AI Fundamentals
- **Instructions**: Copy content from `chatgpt-app/instructions.md`

#### 3.2. Add Actions (API Integration)

1. Click **"Create new action"**
2. Choose **"Import from URL"**
3. Enter your OpenAPI URL:
   ```
   https://your-production-url.com/api/openapi.json
   ```
4. Click **"Import"**

#### 3.3. Configure Authentication

The import will detect HTTP Bearer authentication. Configure:
- **Auth Type**: HTTP Bearer
- **How to provide it**: User input (you'll enter token when testing)

**IMPORTANT**: For production, you'll want a more secure auth flow. For testing, this is fine.

### Step 4: Test Your GPT

Try these test conversations:

#### Test 1: Guided Learning Mode
```
You: I want to learn about generative AI

Expected: GPT should call get_chapters() and offer to guide you through Chapter 1
```

#### Test 2: Grounded Q&A Mode
```
You: What is generative AI?

Expected: GPT should call search_chapters() and answer with cited content from Chapter 1
```

#### Test 3: Quiz Mode
```
You: Quiz me on Chapter 1

Expected: GPT should call get_quiz() and present questions
```

#### Test 4: Progress Tracking
```
You: How am I doing?

Expected: GPT should call get_progress() and show your stats
```

## Option B: Test with Local Backend (Requires ngrok)

### Step 1: Install ngrok

**Windows**:
```bash
# Using Chocolatey
choco install ngrok

# Or download from https://ngrok.com/download
```

**Verify installation**:
```bash
ngrok version
```

### Step 2: Start ngrok Tunnel

```bash
# Start tunnel to your backend
ngrok http 8001
```

**You'll see output like**:
```
Session Status                online
Forwarding                    https://abc123.ngrok.io -> http://localhost:8001
```

**Copy the https:// URL** (e.g., `https://abc123.ngrok.io`)

### Step 3: Update OpenAPI Spec Temporarily

The OpenAPI spec needs your ngrok URL. Edit `chatgpt-app/openapi.yaml`:

```yaml
servers:
  - url: https://abc123.ngrok.io/api/v1  # Replace with your ngrok URL
    description: ngrok tunnel to local backend
```

### Step 4: Host OpenAPI Spec

The OpenAPI spec must be accessible via HTTPS. Use a GitHub Gist or similar:

```bash
# Create a Gist with your openapi.yaml
# Or use a free hosting service like Netlify/Vercel
```

**Alternative**: Export as JSON and host it:
```bash
curl http://localhost:8001/api/openapi.json > openapi.json
# Upload openapi.json to a public URL
```

### Step 5: Create Custom GPT (Follow Option A, Step 2-4)

But use your ngrok URL instead of production URL.

### Step 6: Authenticate

When prompted for token, get one from your local backend:

```bash
# Register or login to get token
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'
```

Copy the `access_token` and paste it into ChatGPT when prompted.

## Common Issues and Solutions

### Issue 1: "Failed to fetch actions"

**Cause**: OpenAPI spec not accessible or invalid URL

**Solution**:
- Verify OpenAPI URL is accessible: `curl https://your-url/api/openapi.json`
- Check ngrok is still running (for local testing)
- Ensure URL uses HTTPS (required for ChatGPT)

### Issue 2: Authentication errors

**Cause**: Token expired or invalid

**Solution**:
- Get fresh token from `/api/v1/auth/login`
- For testing, tokens are valid for 30 days
- Check Authorization header format: `Bearer YOUR_TOKEN`

### Issue 3: "Cannot read properties of undefined"

**Cause**: API response format mismatch

**Solution**:
- Test endpoint directly: `curl -H "Authorization: Bearer TOKEN" https://your-url/api/v1/chapters`
- Check response matches OpenAPI schema
- Review backend logs for errors

### Issue 4: ngrok timeout

**Cause**: Free ngrok tier has connection limits

**Solution**:
- Restart ngrok tunnel
- Or upgrade ngrok account
- Or deploy to production (better option)

## Manual API Testing Script

Before testing in ChatGPT, verify your backend works:

```python
import requests
import json

BASE_URL = "https://your-backend-url.com/api/v1"  # or ngrok URL

# 1. Register/Login
print("1. Authenticating...")
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "test@example.com",
    "password": "Test123!"
})

if response.status_code != 200:
    print(f"Login failed: {response.status_code}")
    print(response.text)
    exit(1)

token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("✓ Authenticated")

# 2. Test get_chapters
print("\n2. Testing get_chapters...")
response = requests.get(f"{BASE_URL}/chapters", headers=headers)
print(f"✓ get_chapters: {response.status_code}")
print(f"  Chapters returned: {len(response.json())}")

# 3. Test get_chapter
print("\n3. Testing get_chapter...")
response = requests.get(f"{BASE_URL}/chapters/chapter-1", headers=headers)
print(f"✓ get_chapter: {response.status_code}")
if response.status_code == 200:
    chapter = response.json()
    print(f"  Chapter title: {chapter.get('title')}")

# 4. Test search
print("\n4. Testing search_chapters...")
response = requests.get(
    f"{BASE_URL}/chapters/search",
    params={"q": "generative AI"},
    headers=headers
)
print(f"✓ search_chapters: {response.status_code}")
if response.status_code == 200:
    results = response.json()
    print(f"  Results found: {len(results)}")
    if results:
        print(f"  Top result: {results[0].get('section_title')}")

# 5. Test get_progress
print("\n5. Testing get_progress...")
response = requests.get(f"{BASE_URL}/progress", headers=headers)
print(f"✓ get_progress: {response.status_code}")
if response.status_code == 200:
    progress = response.json()
    print(f"  Completion: {progress.get('overall_completion_percentage')}%")

# 6. Test get_quiz
print("\n6. Testing get_quiz...")
response = requests.get(f"{BASE_URL}/quizzes/chapter-1-quiz", headers=headers)
print(f"✓ get_quiz: {response.status_code}")
if response.status_code == 200:
    quiz = response.json()
    print(f"  Questions: {quiz.get('total_questions')}")

print("\n✓ All endpoints working! Ready for ChatGPT integration.")
```

## Verification Checklist

Before testing with ChatGPT, verify:

- [ ] Backend returns healthy status
- [ ] All 6 API endpoints work (chapters, search, quizzes, progress, auth)
- [ ] OpenAPI spec is accessible via HTTPS
- [ ] You have a valid JWT token
- [ ] CORS allows chat.openai.com and chatgpt.com

## Expected Test Results

### Successful Integration Looks Like:

1. **GPT retrieves chapters**:
   ```
   GPT: "I'll help you learn about Generative AI! Let me get the available chapters..."
   [Calls get_chapters()]
   GPT: "I found 6 chapters. You have access to chapters 1-3 (free tier).
        Would you like to start with Chapter 1: Introduction to Generative AI?"
   ```

2. **GPT searches before answering**:
   ```
   You: "What is a transformer model?"
   GPT: "Let me search the course material for you..."
   [Calls search_chapters(q="transformer model")]
   GPT: "According to Chapter 2: Large Language Models, Section 3:
        'The Transformer architecture revolutionized NLP by enabling
        parallel processing and handling long-range dependencies...'
        (Source: Chapter 2, Section 3)
   ```

3. **GPT facilitates quizzes**:
   ```
   You: "Quiz me"
   GPT: "I'll get a quiz for you. Which chapter would you like to test?"
   [After you choose]
   [Calls get_quiz()]
   GPT: "Here's your quiz on Chapter 1. I'll show you 10 questions..."
   ```

## Next Steps After Testing

If tests pass:
1. ✅ Integration is working
2. Consider deploying to production (if not already)
3. Add more sophisticated prompts to instructions.md
4. Test with real students
5. Iterate based on feedback

If tests fail:
1. Check backend logs
2. Verify OpenAPI schema matches actual API
3. Test endpoints manually with curl/Postman
4. Review ChatGPT's error messages
5. Check CORS configuration

## Production Deployment Notes

For production deployment:

1. **Use production URL** in OpenAPI servers list
2. **Implement OAuth 2.0** instead of manual token input
3. **Add rate limiting** to prevent abuse
4. **Monitor API usage** with analytics
5. **Set up alerts** for API failures

See `DEPLOYMENT.md` for detailed production deployment guide.
