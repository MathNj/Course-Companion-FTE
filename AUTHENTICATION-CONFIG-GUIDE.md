# 🔐 Authentication Configuration for Custom GPT

What to fill in the Authentication section when configuring Actions.

---

## 🎯 Short Answer

**For your Course Companion FTE backend:**

❌ **Do NOT use** the authentication form you're seeing

✅ **Instead**, use the simpler **"Bearer Token"** authentication

---

## 🔴 Problem: Wrong Authentication Interface

**The fields you're seeing:**
- Client ID
- Client Secret
- Authorization URL
- Token URL
- Scope

**These are for:** **OAuth** authentication (complex setup)

**Your backend uses:** **Bearer Token** (JWT) authentication (simpler)

---

## ✅ What You Should See Instead

**In the Actions section, you should see:**

### Option A: Bearer Token (Correct) ⭐

**Fields:**
- **Token** (or **API Key**)
- **Token Prefix** (sometimes)

**Configuration:**
- Leave **Token** field EMPTY
- Set **Prefix** to: `Bearer`

**This is what your backend needs!**

---

### Option B: HTTP Headers (Alternative)

**If you don't see "Bearer Token":**

Look for:
- **"HTTP Headers"** option
- **"Custom Headers"** option

**Then configure:**
- Header Name: `Authorization`
- Header Value: `Bearer <token>`

---

## 🔍 How to Find the Right Option

### Step 1: Check Actions Section

**Look for authentication options like:**

1. **"Bearer Token"** or **"API Key"** ← **Choose this**
2. **"OAuth"** ← Don't use this
3. **"HTTP Headers"** ← Alternative to option 1
4. **"None"** ← Don't use this

### Step 2: Select Bearer Token/API Key

**Click on "Bearer Token" or "API Key"**

### Step 3: Configure Bearer Token

**If you see:**
```
Token Prefix: [        ]
Token:        [        ]
```

**Set:**
- **Token Prefix:** `Bearer`
- **Token:** Leave EMPTY

**Why empty?** The token will be provided by the login/register flow, not configured here.

---

## 🎯 Complete Configuration

### Actions Section:

**1. Import OpenAPI:**
```
URL: https://course-companion-fte.fly.dev/api/openapi.json
```

**2. Authentication:**
```
Type: Bearer Token
Prefix: Bearer
Token: [leave empty]
```

**3. Save**

---

## ⚠️ What If You ONLY See OAuth?

### Scenario: OAuth is the Only Option

**If you don't see "Bearer Token" anywhere:**

### Option A: Use HTTP Headers (If Available)

**Look for "HTTP Headers" or "Custom Headers"**

**Configure:**
```
Header Name: Authorization
Header Value: Bearer {{token}}
```

**Note:** The `{{token}}` syntax means ChatGPT will substitute the actual token value.

---

### Option B: Use OAuth (Advanced, Not Recommended)

**Only if OAuth is the ONLY option:**

You would need to:
1. Create an OAuth provider (complex)
2. Run an OAuth server (more infrastructure)
3. Add OAuth endpoints to your backend (extra code)

**This is OVERKILL for your use case.**

**Don't do this unless absolutely necessary.**

---

## 🔧 Troubleshooting

### Problem 1: I don't see "Bearer Token"

**Solutions:**
1. Look for **"API Key"** instead (sometimes it's called this)
2. Look for **"HTTP Headers"** option
3. Check if there's a dropdown for authentication types
4. Read the authentication section header carefully

### Problem 2: The form shows OAuth fields

**This means you're in the wrong authentication type.**

**Solutions:**
1. Go back to the Actions section
2. Look for a dropdown or selector
3. Choose "Bearer Token" or "API Key" instead of "OAuth"
4. Then configure as described above

### Problem 3: I only see "None" and "OAuth"

**Then:**

**Option 1: Use HTTP Headers**
- Some Custom GPT interfaces allow custom headers
- Configure: `Authorization: Bearer {{token}}`

**Option 2: Configure in OpenAPI Spec**
- The OpenAPI spec already defines Bearer auth
- ChatGPT should recognize it automatically
- You might not need to configure anything in this form

---

## 📋 Quick Decision Guide

**What authentication fields do you see?**

### A) Token / API Key / Bearer Token
→ **✅ Perfect! Use this**
→ Set prefix to: `Bearer`
→ Leave token field empty

### B) HTTP Headers / Custom Headers
→ **✅ Good alternative**
→ Configure: `Authorization: Bearer {{token}}`

### C) Only OAuth
→ **⚠️ Complex**
→ Don't use unless absolutely necessary
→ Consider HTTP Headers instead

### D) None
→ **❌ Won't work**
→ Your backend requires authentication

---

## 🎯 How Your Authentication Actually Works

### With Bearer Token configured:

**1. User chats with GPT:**
```
User: "Hi, I want to register"
```

**2. GPT calls register endpoint:**
```
POST https://course-companion-fte.fly.dev/api/v1/auth/register
Headers: Authorization: Bearer [will be filled during conversation]
Body: {"email":"user@example.com","password":"pass123"}
```

**3. Backend responds:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**4. GPT uses token for subsequent calls:**
```
GET https://course-companion-fte.fly.dev/api/v1/chapters
Headers: Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**5. User gets content**

---

## ✅ Verification

**After configuration, test with:**

**Test prompt in GPT preview:**
```
"Hi, register me with email test@example.com and password TestPass123!"
```

**Expected behavior:**
- GPT calls the register API
- Uses Bearer authentication
- Successfully registers user

**If this works:** Authentication is configured correctly! ✅

---

## 🎯 Bottom Line

### The fields you're seeing (Client ID, Client Secret, OAuth):

**❌ These are NOT for your backend**

**Your backend uses:**
- ✅ JWT Bearer Token authentication
- ✅ Simple token-based auth
- ✅ No OAuth needed

### What You Need:

**Find and select:**
- **"Bearer Token"** or **"API Key"**
- NOT "OAuth"
- NOT "Client ID/Secret"

**Configure:**
- Prefix: `Bearer`
- Token: Leave empty

---

## 💡 Need Help?

**Tell me exactly what authentication options you see:**

1. What's the section header? (e.g., "Authentication Type")
2. What options are in the dropdown?
3. What fields do you see?

**I'll give you specific instructions for your exact interface!**

---

## 🚀 Quick Summary

**For Course Companion FTE:**

❌ **Don't use:** OAuth, Client ID, Client Secret

✅ **Use:** Bearer Token or API Key
- Prefix: `Bearer`
- Token: Leave empty

**That's it!** 🎯
