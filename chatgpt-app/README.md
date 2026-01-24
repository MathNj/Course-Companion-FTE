# Course Companion FTE - ChatGPT App

This directory contains the ChatGPT App configuration for Course Companion FTE, enabling students to learn Generative AI fundamentals through conversational interaction with ChatGPT.

## Overview

The ChatGPT App provides a natural language interface to the Course Companion FTE backend, allowing students to:
- **Learn**: Access structured course content through conversation
- **Practice**: Take interactive quizzes with immediate feedback
- **Track**: Monitor progress, streaks, and achievements
- **Engage**: Get personalized encouragement and adaptive teaching

## Architecture

```
Student ← Conversation → ChatGPT ← API Calls → Backend API
                         (GPT-4)              (FastAPI)
```

**Zero-Backend-LLM Design**: ChatGPT acts as a facilitator, retrieving pre-authored content from the backend rather than generating its own explanations. This ensures accuracy and consistency.

## Files

- **`instructions.md`** - Main instructions for ChatGPT on how to be a teaching assistant
- **`openapi.yaml`** - OpenAPI specification defining available backend actions
- **`gpt-config.json`** - ChatGPT app configuration metadata
- **`prompts/`** - Optional additional prompt files for specific teaching modes

## Setup Instructions

### Prerequisites

1. Backend API running (see `backend/README.md`)
2. ChatGPT Plus subscription (required for custom GPTs)
3. (Optional) Public URL for your backend API

### Local Development Setup

#### Step 1: Start the Backend

```bash
# In the project root
cd backend
docker-compose up
```

Backend will be available at `http://localhost:8001`

#### Step 2: Test API Endpoints

```bash
# List chapters
curl http://localhost:8001/api/v1/chapters

# Get OpenAPI spec
curl http://localhost:8001/api/openapi.json
```

#### Step 3: Configure ChatGPT for Local Testing

Since ChatGPT cannot directly access `localhost`, you have two options:

**Option A: Use ngrok (Recommended for Testing)**

```bash
# Install ngrok: https://ngrok.com/download
# Start tunnel to your local backend
ngrok http 8001
```

This gives you a public URL like `https://abc123.ngrok.io`

**Option B: Deploy to Production** (see Deployment section)

### Creating the Custom GPT

1. **Go to ChatGPT**: https://chat.openai.com
2. **Click your profile** → "My GPTs" → "Create a GPT"
3. **Configure the GPT**:

   **Name**: Course Companion FTE

   **Description**:
   ```
   Your AI-powered learning companion for mastering Generative AI fundamentals.
   Access structured lessons, take quizzes, and track your progress through 6 comprehensive chapters.
   ```

   **Instructions**: Copy the entire content of `instructions.md`

   **Conversation starters** (optional):
   - "What chapters are available?"
   - "Start with Chapter 1"
   - "Quiz me on what I've learned"
   - "How's my progress?"

4. **Add Actions**:
   - Click "Create new action"
   - Click "Import from URL"
   - Enter your OpenAPI URL:
     - For ngrok: `https://your-ngrok-url.ngrok.io/api/openapi.json`
     - For production: `https://your-domain.com/api/openapi.json`
   - Alternatively, copy/paste the content of `openapi.yaml`

5. **Configure Authentication**:
   - If using public testing: Set to "None"
   - If using authentication: Set to "API Key" or "OAuth"
   - For production: Configure bearer token authentication

6. **Test the GPT**:
   ```
   You: "What chapters can I learn?"
   GPT: [Calls get_chapters() action]
   GPT: "I can teach you about 6 chapters covering Generative AI..."
   ```

## Testing Checklist

Test each major function:

### ✅ Chapter Access
```
You: "Show me Chapter 1"
Expected: GPT calls get_chapter("chapter-1") and presents content
```

### ✅ Quiz Taking
```
You: "I want to take the Chapter 1 quiz"
Expected: GPT calls get_quiz("chapter-1-quiz") and presents questions
```

### ✅ Quiz Grading
```
You: [After answering questions] "Submit my answers"
Expected: GPT calls submit_quiz() and shows score + explanations
```

### ✅ Progress Tracking
```
You: "How am I doing?"
Expected: GPT calls get_progress() and shows completion stats, streak, milestones
```

### ✅ Freemium Gating
```
You: "Show me Chapter 4"
Expected: If free tier, GPT shows upgrade message. If premium, shows content.
```

## API Actions Reference

The GPT has access to 5 backend actions:

| Action | Purpose | Example Trigger |
|--------|---------|----------------|
| `get_chapters()` | List all chapters with access status | "What can I learn?" |
| `get_chapter(id)` | Retrieve full chapter content | "Show me Chapter 1" |
| `get_quiz(id)` | Get quiz questions (no answers) | "Quiz me on Chapter 1" |
| `submit_quiz(id, answers)` | Grade quiz submission | "Submit my quiz answers" |
| `get_progress()` | Get progress summary | "How's my progress?" |

## Prompt Engineering Tips

### For Better Student Experience

**Be Specific About Actions**:
```
✅ Good: "Let me get Chapter 1 for you" [calls get_chapter]
❌ Avoid: Explaining AI concepts from GPT's training data
```

**Encourage Structured Learning**:
```
✅ Good: "Great! You've completed Chapter 1. Ready for Chapter 2?"
❌ Avoid: Jumping randomly between topics
```

**Celebrate Progress**:
```
✅ Good: "You're on a 7-day streak! 🔥 Just 7 more days to Two Week Champion!"
❌ Avoid: Just reporting numbers without encouragement
```

### For Better Accuracy

**Always Use API Content**:
The instructions explicitly tell GPT to:
1. Call `get_chapter()` for all explanations
2. Never generate its own AI explanations
3. Reference exact content from API responses

**Verify in Testing**:
- Check that GPT actually calls the action (you'll see "Used [action]" in the response)
- Verify explanations match the course content, not general AI knowledge

## Deployment

### Production Backend

1. **Deploy Backend**: Follow `backend/README.md` deployment guide
   - Options: Fly.io, Railway, Render, AWS, etc.
   - Ensure HTTPS enabled
   - Note your production URL

2. **Update OpenAPI**:
   - Edit `openapi.yaml`
   - Update the `servers` section with your production URL:
     ```yaml
     servers:
       - url: https://your-production-url.com/api/v1
         description: Production server
     ```

3. **Update GPT Actions**:
   - In your Custom GPT settings
   - Edit the action import URL to your production OpenAPI endpoint
   - Re-import the schema

### Authentication (Optional)

For production, you may want to add authentication:

**Option 1: No Auth** (Current setup)
- Simplest for MVP
- Anyone can use the GPT
- Consider rate limiting

**Option 2: API Key**
- Generate API keys for users
- Users enter key when starting GPT conversation
- Update `openapi.yaml` to require API key header

**Option 3: OAuth** (Most secure)
- Implement OAuth flow in backend
- Configure in GPT action settings
- Users log in through OAuth

## Monitoring

Track GPT usage:
- Monitor backend API logs for action calls
- Check which endpoints are most used
- Identify error patterns

Useful queries:
```bash
# Count API calls by endpoint
grep "GET /api/v1" backend/logs/*.log | wc -l

# Find errors
grep "ERROR" backend/logs/*.log | tail -20
```

## Troubleshooting

### GPT Not Calling Actions

**Symptom**: GPT answers from its own knowledge instead of calling API

**Solutions**:
1. Check instructions emphasize "ALWAYS call get_chapter"
2. Verify action schema is properly imported
3. Test action directly in GPT action tester
4. Make sure server URL is accessible (not localhost without ngrok)

### 403 Forbidden Errors

**Symptom**: GPT says "I can't access that chapter"

**Solutions**:
1. Check CORS settings in backend (`settings.cors_origins`)
2. Verify URL in openapi.yaml is correct
3. Check authentication configuration

### Timeout Errors

**Symptom**: "The action took too long to respond"

**Solutions**:
1. Check backend server is running
2. Verify network connectivity
3. Check for slow database queries
4. Increase timeout in GPT action settings (default 45s)

### Content Not Matching Course Material

**Symptom**: GPT gives different explanations than course content

**Solutions**:
1. Strengthen instructions to "NEVER generate your own explanations"
2. Add examples in instructions of calling get_chapter first
3. Test with specific questions like "What does Chapter 1 say about...?"

## Best Practices

### For GPT Configuration

1. **Keep Instructions Updated**: As you improve the course, update the GPT instructions
2. **Test Regularly**: Test all actions after any backend changes
3. **Monitor Feedback**: Pay attention to how students interact with the GPT
4. **Iterate on Prompts**: Refine instructions based on actual usage patterns

### For Content Quality

1. **Audit API Calls**: Verify GPT always uses API, never its own knowledge for course content
2. **Check Explanations**: Compare GPT responses to source material in backend
3. **Test Edge Cases**: Try confusing questions to ensure GPT stays on track
4. **Update Backend Content**: Improve course material in backend, not GPT instructions

### For Student Experience

1. **Personalization**: Use student's name if available
2. **Adaptive Pacing**: Match student's comprehension level
3. **Celebrate Wins**: Acknowledge progress, streaks, quiz passes
4. **Clear Navigation**: Always suggest next steps after completing a section

## Support

For issues or questions:
- **Backend API**: See `backend/README.md`
- **Course Content**: Check `backend/content/`
- **GPT Behavior**: Review and update `instructions.md`

## Next Steps

After setting up the ChatGPT app:

1. **Test with Real Users**: Get feedback on the teaching experience
2. **Analyze Usage**: See which chapters and features are most used
3. **Iterate on Instructions**: Improve GPT behavior based on interactions
4. **Expand Features**: Add more teaching modes (Socratic tutor, concept explainer)
5. **Scale**: Consider deployment to ChatGPT Plugin Store (if available)

## License

[Your License]

---

**Built with ❤️ for AI Education**
