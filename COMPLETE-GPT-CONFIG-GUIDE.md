# 🎯 Complete ChatGPT Custom GPT Configuration

Everything you need to configure your Course Companion FTE Custom GPT.

---

## 📝 BASIC INFORMATION

### Name (Copy Exactly):
```
Course Companion FTE - Generative AI
```

---

### Description (Copy Exactly):
```
Expert tutor for the Generative AI Fundamentals course. Provides grounded answers using only course material, tracks your progress, and administers quizzes.
```

---

## 📜 INSTRUCTIONS (Copy Everything Below)

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
1. Search the course material using the search action
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

---

## 🔧 ACTIONS (Create 4 Actions)

Go to the **Actions** section and click **"Create action"** for each:

---

### Action 1: User Login

**Authentication:** Bearer Token

**Configuration:**
- **Name:** `User Login`
- **Description:** `Authenticate user and get access token`
- **Method:** `POST`
- **URL:** `https://course-companion-fte.fly.dev/api/v1/auth/login`

**Request Body:**
```json
{
  "email": "{{USER_EMAIL}}",
  "password": "{{USER_PASSWORD}}"
}
```

---

### Action 2: Get Course Chapters

**Authentication:** Bearer Token

**Configuration:**
- **Name:** `Get Course Chapters`
- **Description:** `List all chapters in the course`
- **Method:** `GET`
- **URL:** `https://course-companion-fte.fly.dev/api/v1/chapters`

---

### Action 3: Get Chapter Details

**Authentication:** Bearer Token

**Configuration:**
- **Name:** `Get Chapter Details`
- **Description:** `Get full chapter content by ID`
- **Method:** `GET`
- **URL:** `https://course-companion-fte.fly.dev/api/v1/chapters/{{CHAPTER_ID}}`

---

### Action 4: Search Course Material

**Authentication:** Bearer Token

**Configuration:**
- **Name:** `Search Course Material`
- **Description:** `Search for content across all chapters`
- **Method:** `GET`
- **URL:** `https://course-companion-fte.fly.dev/api/v1/chapters/search?q={{QUERY}}&limit=5`

---

## 🔐 AUTHENTICATION (For All Actions)

**In each action, configure:**

- **Type:** Bearer Token (or API Key)
- **Token Prefix:** `Bearer`
- **Token:** Leave empty (ChatGPT will fill this after login)

---

## 🔒 PRIVACY POLICY (Copy Everything Below)

Go to the **Privacy** section and paste this:

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

---

## ⚙️ CAPABILITIES (DISABLE ALL)

**Go to the Capabilities section and make sure ALL are UNCHECKED:**

- ❌ **Web Search** - DISABLE (unchecked)
- ❌ **Canvas** - DISABLE (unchecked)
- ❌ **Image Generation** - DISABLE (unchecked)
- ❌ **Code Interpreter & Data Analysis** - DISABLE (unchecked)

**Leave them ALL disabled.**

---

## 📚 KNOWLEDGE (LEAVE EMPTY)

**Do NOT add any documents to Knowledge.**

**Leave it completely empty.**

---

## ✅ CONFIGURATION CHECKLIST

Before you publish, verify:

**Basic Info:**
- [ ] Name: "Course Companion FTE - Generative AI"
- [ ] Description: "Expert tutor for Generative AI course..."
- [ ] Instructions: Pasted completely (all sections)

**Actions (4 total):**
- [ ] User Login - POST /api/v1/auth/login
- [ ] Get Course Chapters - GET /api/v1/chapters
- [ ] Get Chapter Details - GET /api/v1/chapters/{chapter_id}
- [ ] Search Course Material - GET /api/v1/chapters/search

**Authentication:**
- [ ] All actions use Bearer Token
- [ ] Token prefix set to "Bearer"
- [ ] Token field left empty

**Privacy:**
- [ ] Privacy policy pasted completely

**Capabilities:**
- [ ] Web Search - DISABLED
- [ ] Canvas - DISABLED
- [ ] Image Generation - DISABLED
- [ ] Code Interpreter - DISABLED

**Knowledge:**
- [ ] Left EMPTY (no documents)

---

## 🧪 TESTING YOUR GPT

**After configuration, in the preview panel (left side), try:**

### Test 1: Login
```
Hi, I want to register. My email is test@example.com and password is TestPass123!
```

**Expected:** GPT should call the User Login action

### Test 2: Get Chapters
```
What chapters are available?
```

**Expected:** GPT should call Get Course Chapters action

### Test 3: Search
```
What is a transformer model?
```

**Expected:** GPT should call Search Course Material action

---

## 🚀 PUBLISHING

**Once everything is configured and tested:**

1. **Click "Create" or "Publish"** (top right button)

2. **Choose visibility:**
   - **"Only me"** - For your personal use only
   - **"Only people with a link"** - Share with specific people
   - **"Public"** - List in GPT store (requires review)

3. **Click "Confirm" or "Publish"**

4. **Your GPT is now live!** 🎉

---

## 📊 WHAT YOUR GPT WILL DO

**When students use it:**

✅ **Can:**
- List all course chapters
- Retrieve chapter content
- Search for specific topics
- Provide grounded, cited answers
- Administer quizzes
- Track progress
- Maintain zero-hallucination principle

❌ **Cannot:**
- Make up information
- Use external sources (Web Search disabled)
- Generate images
- Run code
- Access content outside the course material

---

## 🎯 KEY FEATURES

1. **Grounded Q&A** - All answers from course material only
2. **Source Citation** - Always cites Chapter X, Section Y
3. **Access Control** - Free tier (chapters 1-3), Premium (all)
4. **Progress Tracking** - Monitors learning journey
5. **Quiz System** - Tests knowledge with instant feedback
6. **Zero Hallucination** - Never makes up information

---

## 💡 TIPS FOR SUCCESS

**For Best Results:**

1. **Copy-paste everything exactly** - Don't modify the instructions
2. **Create all 4 actions** - Each one is essential
3. **Set authentication correctly** - Bearer Token for all actions
4. **Disable all capabilities** - Keeps focus on course content
5. **Leave Knowledge empty** - Backend has all the content
6. **Test thoroughly** - Try all the test prompts above
7. **Publish when ready** - Start with "Only me" to test privately

---

## 🆘 NEED HELP?

**If you get stuck:**

1. **Can't find "Create GPT"?** Look for "Explore GPTs" in left sidebar
2. **Actions not working?** Check the URL is exactly: `https://course-companion-fte.fly.dev`
3. **Authentication failing?** Make sure it says "Bearer Token" not "OAuth"
4. **GPT not responding?** Check the actions are created correctly

**Tell me what step you're on and what you see, and I'll help!**

---

## ✅ YOU'RE READY!

**Follow this guide step-by-step and you'll have a working Course Companion GPT!**

**Good luck! 🚀**
