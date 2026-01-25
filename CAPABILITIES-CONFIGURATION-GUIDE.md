# 🔧 Custom GPT Capabilities Configuration Guide

Which capabilities should you enable for Course Companion FTE?

---

## 📋 Quick Answer

**Recommended Configuration:**

- ❌ Web Search → **NO**
- ❌ Canvas → **NO**
- ❌ Image Generation → **NO**
- ❌ Code Interpreter & Data Analysis → **NO**

**Reason:** We want ChatGPT to use ONLY the course material from our backend API, not external sources.

---

## 🎯 Detailed Analysis of Each Capability

### 1. Web Search 🔍

**What it does:**
- ChatGPT can search the internet for information
- Gets real-time data from web sources
- Can access current events, latest news, etc.

**Should you enable it?** ❌ **NO**

**Why NOT to enable:**
- **Violates zero-hallucination principle:** We want ChatGPT to use ONLY course material
- **Undermines grounded Q&A:** Students should get answers from the course, not Google
- **Inconsistent information:** Web search might contradict course content
- **Defeats the purpose:** The whole point is to provide a focused, course-specific learning experience

**When might you want it:**
- If the course needs real-time information (e.g., current AI research papers)
- If you want ChatGPT to supplement course material with external sources
- If the course explicitly requires web research

**For our use case:** NO - keep it focused on course material only

---

### 2. Canvas 🎨

**What it does:**
- Allows ChatGPT to create and edit visual content
- Can generate diagrams, charts, visualizations
- Can save and reference images across conversations

**Should you enable it?** ❌ **NO**

**Why NOT to enable:**
- **Not needed:** Our backend provides all the content ChatGPT needs
- **Distraction:** Students are here to learn AI concepts, not create art
- **Cost:** Uses extra credits/tokens
- **Doesn't add educational value:** Course content is text-based (chapters, quizzes)

**When might you want it:**
- If you want ChatGPT to create visual explanations
- If students need to generate diagrams
- If the course includes visual assignments

**For our use case:** NO - text-based learning is sufficient

---

### 3. Image Generation 🖼️

**What it does:**
- ChatGPT can generate images using DALL-E
- Create visual content based on descriptions

**Should you enable it?** ❌ **NO**

**Why NOT to enable:**
- **Not relevant:** Generative AI course is about concepts, not creating images
- **Cost:** Uses extra credits
- **Distraction:** Takes focus away from learning
- **Not in course objectives:** Students are learning ABOUT AI, not USING AI to create art

**When might you want it:**
- If the course includes visual design components
- If students need to visualize concepts
- If assignments require image generation

**For our use case:** NO - not needed for educational content

---

### 4. Code Interpreter & Data Analysis 📊

**What it does:**
- ChatGPT can run Python code
- Can analyze data files
- Can perform calculations
- Can create charts and graphs

**Should you enable it?** ⚠️ **MAYBE - but probably NO**

**Why MIGHT be useful:**
- Students could run AI code examples
- Could analyze quiz results
- Could visualize learning progress

**Why probably NOT:**
- **Not in course scope:** Course is about learning AI concepts, not coding
- **Backend already handles everything:** Quizzes are graded by the backend, not ChatGPT
- **Unnecessary complexity:** Adds features that aren't part of the learning objectives
- **Cost:** Uses extra credits

**When might you want it:**
- If course includes hands-on coding exercises
- If students need to run ML models
- If you want data visualization features

**For our use case:** NO - the backend handles all the functionality

---

## 🎯 The Core Principle

### Grounded Q&A = Single Source of Truth

**Our architecture:**
```
Student Question
    ↓
ChatGPT
    ↓
Backend API (search/retrieve)
    ↓
Course Material (chapters, sections)
    ↓
Grounded Answer with Citation
```

**If you enable Web Search:**
```
Student Question
    ↓
ChatGPT
    ↓
?? Web Search OR Backend API ??
    ↓
Confusion / Inconsistent Sources
```

**Result:** Undermines the zero-hallucination principle

---

## ✅ Recommended Configuration

### Keep It Simple & Focused

**Enable:**
- ✅ **Actions** (API integration) ← This is critical!
- ✅ **Knowledge** (if adding hackathon document)

**Do NOT enable:**
- ❌ Web Search
- ❌ Canvas
- ❌ Image Generation
- ❌ Code Interpreter

---

## 🎓 Why This Approach?

### 1. Maintains Course Integrity

**Without extra capabilities:**
- All answers come from course material
- Consistent with learning objectives
- Focused learning experience

**With extra capabilities:**
- ChatGPT might use external sources
- Inconsistent with course content
- Distracts from learning goals

---

### 2. Ensures Grounded Q&A

**Our promise to students:**
- "All answers are from the course material"
- "No hallucination or made-up information"
- "Cited sources (Chapter X, Section Y)"

**Extra capabilities break this promise:**
- Web Search: "I found this on Google" ❌
- Image Generation: "Here's a picture I created" ❌
- Code Interpreter: "I ran some code to figure this out" ❌

---

### 3. Simplifies Testing & Validation

**With only Actions (API):**
- Easy to test: "Did ChatGPT call the API?"
- Clear behavior: "Search → Retrieve → Cite"
- Predictable responses

**With extra capabilities:**
- Hard to predict which source ChatGPT uses
- Testing becomes complex
- Behavior varies

---

### 4. Reduces Cost

**Extra capabilities consume:**
- More tokens
- External API calls (web search, DALL-E, code execution)
- Higher per-conversation cost

**Minimal configuration:**
- Only API calls (which we already have)
- Predictable token usage
- Cost-effective

---

## ⚠️ What If You REALLY Want to Enable Something?

### Scenario 1: You Want Web Search for "Current AI Developments"

**Consider:**
- Is this in the course scope?
- Could you add a "Latest News" chapter to the backend instead?
- Does it align with learning objectives?

**If yes:**
- Enable Web Search
- Update instructions: "For course concepts, use API. For latest AI news, use Web Search and cite sources."
- Accept that students get external information

---

### Scenario 2: You Want Code Interpreter for "Hands-On Practice"

**Consider:**
- Does the backend already support this? (quizzes, progress tracking)
- Could code exercises be added to the backend?
- Is it essential for learning?

**If yes:**
- Enable Code Interpreter
- Update instructions to clarify when to use it
- Test thoroughly to ensure it doesn't interfere with API calls

---

### Scenario 3: You Want Canvas for "Visual Learning"

**Consider:**
- Are visual diagrams in the course content?
- Could they be added to the backend as images?
- Is DALL-E generation better than prepared visuals?

**If yes:**
- Enable Canvas
- Use it for creating study aids, not content generation
- Update instructions accordingly

---

## 📋 Configuration Checklist

Before publishing, verify:

- [ ] Actions configured (API integration) ← **CRITICAL**
- [ ] Web Search: DISABLED
- [ ] Canvas: DISABLED
- [ ] Image Generation: DISABLED
- [ ] Code Interpreter: DISABLED
- [ ] Knowledge: Optional (if adding hackathon document)
- [ ] Instructions updated (emphasize API usage)
- [ ] Tested: ChatGPT uses API, not external sources

---

## 🧪 Testing Without Capabilities

**Test that ChatGPT uses ONLY the API:**

**Prompt:**
```
"What is the latest development in large language models?"
```

**Expected WITHOUT Web Search:**
- "I searched the course material but couldn't find information about the latest developments. The course covers LLM fundamentals, but may not have the most recent news."

**Expected WITH Web Search:**
- "According to recent news..." ← This violates grounded Q&A

**Which do you want?** For our use case, the first response is correct!

---

## 🎯 Bottom Line

### For Course Companion FTE:

**DO NOT enable any extra capabilities**

**Rationale:**
1. ✅ Backend API provides everything needed
2. ✅ Maintains grounded Q&A principle
3. ✅ Ensures consistent, focused learning
4. ✅ Reduces cost and complexity
5. ✅ Easier to test and validate

**The only capability you need is:**
- ✅ **Actions** (to connect to the backend API)

**Optional:**
- 📚 **Knowledge** (if adding hackathon document)

---

## 🚀 Configuration Summary

**Enable:**
- ✅ Actions (required for API integration)

**Optional:**
- 📚 Knowledge (only if adding hackathon document)

**Disable:**
- ❌ Web Search
- ❌ Canvas
- ❌ Image Generation
- ❌ Code Interpreter & Data Analysis

**Result:** A focused, grounded Q&A tutor that uses only course material!

---

## 💡 Need Help?

**If you have a specific use case for a capability:**

Tell me:
1. Which capability do you want to enable?
2. What's the specific use case?
3. Why do you think it's needed?

I'll help you decide and configure it properly if it makes sense!

---

**For now: Keep it simple and focused on the API!** 🎯
