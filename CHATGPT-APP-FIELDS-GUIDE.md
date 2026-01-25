# 🔧 ChatGPT App Configuration Guide

Filling in the fields for your ChatGPT App with the Course Companion backend.

---

## FIELD 1: Name ✅

**What to enter:**
```
Course Companion FTE
```

**Or alternatively:**
```
Generative AI Course Tutor
```

**Why:** This identifies your app in ChatGPT

**Click "Next" when done**

---

## FIELD 2: Custom Tool ✅

**What to enter:** Leave this **EMPTY** (blank)

**Why:** This is for custom code/tools. We're using the API via MCP instead.

**Just skip this field and click "Next"**

---

## FIELD 3: Description (optional) ✅

**What to enter:**
```
Expert tutor for the Generative AI Fundamentals course. Provides grounded answers using only course material, tracks progress, and administers quizzes.
```

**Why:** Short description of what your app does

**Click "Next" when done**

---

## FIELD 4: MCP Server URL ⭐ CRITICAL ✅

**What to enter:**
```
https://course-companion-fte.fly.dev/api/openapi.json
```

**WAIT!** That's OpenAPI, not MCP. Let me explain:

**IMPORTANT:** ChatGPT Apps can use **either**:
1. **MCP (Model Context Protocol)** - For direct server connections
2. **OpenAPI** - For REST APIs (which we have)

**The interface you're seeing is for MCP servers, but we have a REST API with OpenAPI spec.**

**You have TWO options:**

### OPTION A: Use OpenAPI Instead (RECOMMENDED)

1. **Cancel** this MCP configuration
2. Look for a button or link that says **"OpenAPI"** or **"REST API"**
3. Choose that option instead
4. Then enter: `https://course-companion-fte.fly.dev/api/openapi.json`

### OPTION B: Continue with MCP (ADVANCED)

If you MUST use MCP (Model Context Protocol), the URL would be different.

**But our backend is set up for REST API with OpenAPI, not MCP.**

---

## 🎯 RECOMMENDATION: Switch to OpenAPI/REST API

**Our backend is a REST API with OpenAPI specification. It's NOT an MCP server.**

**Here's what to do:**

### Step 1: Look for Alternative Options

On the configuration page, look for:
- **"OpenAPI"** button/tab
- **"REST API"** option
- **"API Specification"**
- Or a link that says **"Configure with OpenAPI"**

**The interface might show:**
- "MCP Server" (what you're seeing now)
- "OpenAPI" ← **Choose this instead**
- "Files" (for other purposes)

### Step 2: Select OpenAPI/REST API

Click on **"OpenAPI"** or **"REST API"**

### Step 3: Enter OpenAPI URL

**Then enter:**
```
https://course-companion-fte.fly.dev/api/openapi.json
```

---

## FIELD 5: Authentication ✅

**What to select:** **OAuth** is probably NOT what we want

**Our backend uses:** **Bearer Token** (JWT)

**Look for these options instead:**
- **"Bearer Token"** or **"API Key"** ← **Choose this**
- **"No Authentication"** (if available)

**If OAuth is the only option:**

You might need to select OAuth, but then our backend won't work correctly with it.

**Better approach:** See if there's a way to specify custom authentication headers.

---

## 🔴 PROBLEM: Interface Mismatch

**The interface you're seeing (MCP Server URL, OAuth) suggests:**

You're creating a **ChatGPT App** that connects to an MCP server.

**But our backend is:**
- A **REST API**
- With **OpenAPI specification**
- Using **Bearer Token** authentication

**These are different architectures!**

---

## ✅ SOLUTION: Create a Custom GPT Instead

**ChatGPT has TWO different platforms:**

### 1. ChatGPT Apps (What you're doing now)
- For MCP servers
- For custom tools
- Different authentication model

### 2. ChatGPT Custom GPTs (What we need)
- For REST APIs
- OpenAPI specification
- Bearer token authentication ← **This matches our backend!**

---

## 🎯 CORRECT APPROACH: Create a Custom GPT

**Here's what to do instead:**

### Step 1: Cancel Current Configuration

Click **"Cancel"** or go back

### Step 2: Navigate to Custom GPTs

1. Look at the left sidebar in ChatGPT
2. Find **"Explore GPTs"** or **"My GPTs"**
3. Click on it
4. Look for **"Create a GPT"** button

### Step 3: Create Custom GPT (Not App)

The Custom GPT interface has:
- Name
- Description
- Instructions ← **Critical!**
- Actions (with OpenAPI import) ← **This is what we need!**
- Knowledge (optional)
- Privacy (optional)

---

## 📋 Quick Decision Guide

**Are you seeing:**

### A) MCP Server URL, OAuth, Client ID?
→ **You're in the wrong place!**
→ Go back and choose "Create a GPT" instead of "Create an App"
→ Or look for "Explore GPTs" → "Create a GPT"

### B) Actions, OpenAPI, Bearer Token?
→ **You're in the RIGHT place!**
→ This is the Custom GPT interface
→ Follow the configuration guide

---

## 🚀 Next Steps

### If you can switch to Custom GPT:

1. **Cancel** the current App configuration
2. Go to **"Explore GPTs"** in left sidebar
3. Click **"Create a GPT"**
4. Follow the guide: **LIVE-CONFIGURATION-WALKTHROUGH.md**

### If you must use ChatGPT Apps:

We would need to:
1. Create an MCP server wrapper around our REST API
2. This is complex and not recommended
3. Custom GPT is much simpler

---

## 💡 My Recommendation

**Switch to creating a Custom GPT instead of an App.**

**Why?**
- ✅ Our backend is designed for Custom GPTs
- ✅ OpenAPI specification ready
- ✅ Bearer token authentication
- ✅ Simple configuration
- ✅ Perfect match for our architecture

**Apps with MCP are for:**
- ❌ Different use cases
- ❌ More complex setup
- ❌ Doesn't match our backend

---

## 🎯 What to Do Right Now

1. **Cancel** the current App configuration
2. Find **"Explore GPTs"** or **"My GPTs"** in the left sidebar
3. Click **"Create a GPT"** (NOT "Create an App")
4. Then I'll guide you through the correct fields!

---

**Questions?** Tell me what you see on your screen and I'll help you navigate to the right place!
