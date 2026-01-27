# Course Companion FTE - R2 Content API

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- R2 credentials already configured in `.env`

### Installation

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Or install minimal dependencies for testing
pip install fastapi uvicorn boto3 python-dotenv pydantic
```

### Run the API

**Option 1: Simple R2 API (Recommended for testing)**
```bash
cd backend
python simple_r2_api.py
```

**Option 2: Full Backend**
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

---

## 📡 API Endpoints

### 1. Health Check
```bash
GET http://localhost:8000/
GET http://localhost:8000/health
```

**Response:**
```json
{
  "status": "operational",
  "service": "Course Companion FTE - R2 Content API",
  "course": "Generative AI Fundamentals",
  "r2_configured": true
}
```

---

### 2. List All Chapters
```bash
GET http://localhost:8000/chapters
```

**Response:**
```json
{
  "total": 4,
  "chapters": [
    {
      "name": "Chapter 1 — The Age of Synthesis_ An Introduction to Generative AI",
      "key": "Generative AI Fundamentals/Chapter 1 — The Age of Synthesis_ An Introduction to Generative AI.md",
      "size": 1289000,
      "last_modified": "2026-01-27T00:24:09Z"
    }
  ]
}
```

---

### 3. Get Chapter Content

**Supported formats:**
- Full name: `Chapter 1 — The Age of Synthesis_ An Introduction to Generative AI`
- Short name: `chapter-1`
- Number: `1`

```bash
# By number
GET http://localhost:8000/chapters/1

# By short name
GET http://localhost:8000/chapters/chapter-1

# By full name (URL encoded)
GET http://localhost:8000/chapters/Chapter%201%20%E2%80%94%20The%20Age%20of%20Synthesis_
```

**Response:**
```json
{
  "chapter_name": "Chapter 1 — The Age of Synthesis_ An Introduction to Generative AI",
  "content": "# Chapter 1\n\nFull markdown content...",
  "size_bytes": 1289000,
  "content_type": "text/markdown"
}
```

---

### 4. Search Content

```bash
GET http://localhost:8000/search?q=transformer&limit=5
```

**Response:**
```json
{
  "query": "transformer",
  "results": [
    {
      "chapter": "Chapter 3 — Transformer Architecture",
      "preview": "...The transformer architecture revolutionized the field...",
      "match_count": 42,
      "size": 1624000
    }
  ],
  "total": 2
}
```

---

## 🧪 Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/

# List chapters
curl http://localhost:8000/chapters

# Get chapter 1
curl http://localhost:8000/chapters/1

# Search for "transformer"
curl http://localhost:8000/search?q=transformer
```

### Using Python

```python
import requests

base_url = "http://localhost:8000"

# List chapters
response = requests.get(f"{base_url}/chapters")
chapters = response.json()
print(f"Found {chapters['total']} chapters")

# Get first chapter
response = requests.get(f"{base_url}/chapters/1")
chapter = response.json()
print(f"Chapter: {chapter['chapter_name']}")
print(f"Content length: {chapter['size_bytes']} bytes")

# Search
response = requests.get(f"{base_url}/search?q=llm")
results = response.json()
print(f"Found {results['total']} matches for 'llm'")
```

### Using Browser

Open in your browser:
- http://localhost:8000/
- http://localhost:8000/chapters
- http://localhost:8000/chapters/1

---

## 🔧 Configuration

The `.env` file should contain:

```env
R2_ACCOUNT_ID=e71c4388cef18b821a1ccbc73c3aa149
R2_ACCESS_KEY_ID=2db4761fdeb45d1611849c9e21897a65
R2_SECRET_ACCESS_KEY=8c096bec15fc1ad48a0fb8121df28ed9e803bda21d4f907110d94d0e2db57c6b
R2_BUCKET_NAME=generative-ai-fundamentals
R2_ENDPOINT=https://e71c4388cef18b821a1ccbc73c3aa149.r2.cloudflarestorage.com
```

---

## 🔒 Security Warning

⚠️ **IMPORTANT:** The R2 credentials in `.env` are now in a public repository.

**Immediate Actions Required:**

1. **Revoke the exposed API token:**
   - Go to Cloudflare Dashboard → R2 → Manage R2 API Tokens
   - Delete the compromised token

2. **Create a new token:**
   - Generate a new R2 API token
   - Update `.env` with new credentials

3. **Add `.env` to `.gitignore`:**
   ```gitignore
   # Environment variables
   .env
   .env.local
   .env.*.local
   ```

4. **Remove from git history:**
   ```bash
   git rm --cached backend/.env
   git commit -m "Remove sensitive .env file"
   ```

---

## 📚 Your Course Content

The API is configured to serve:

```
Generative AI Fundamentals/
├── Chapter 1 — The Age of Synthesis_ An Introduction to Generative AI.md (1.23 MB)
├── Chapter 2 — What are LLMs_.md (397 KB)
├── Chapter 3 — Transformer Architecture.md (1.55 MB)
└── Chapter 4 — Prompt Engineering Basics.md (13.5 KB)
```

---

## 🎯 Next Steps

1. **Test the API:**
   ```bash
   python simple_r2_api.py
   curl http://localhost:8000/chapters
   ```

2. **Update Skills to use the API:**
   - Modify `socratic-tutor` to call `/chapters/{id}`
   - Modify `concept-explainer` to call `/search?q={topic}`
   - Modify `quiz-master` to fetch quiz content

3. **Deploy for production:**
   - Use environment variables for secrets
   - Enable HTTPS
   - Add authentication
   - Restrict CORS origins

---

## 🐛 Troubleshooting

### "R2 client not configured"
- Check that all R2 credentials are in `.env`
- Verify the `.env` file is being loaded
- Check for typos in variable names

### "Chapter not found"
- Use `/chapters` to list available chapters
- Try different formats (number, short name, full name)
- Check if the chapter file exists in R2

### Connection errors
- Verify R2 endpoint is correct
- Check firewall/network settings
- Ensure R2 bucket exists and credentials are valid

---

## ✅ Phase 1 Compliance

This API meets Phase 1 requirements:

- ✅ **Zero-Backend-LLM**: No LLM calls in backend
- ✅ **Content Delivery**: Serves content verbatim from R2
- ✅ **Search API**: Keyword search across all chapters
- ✅ **Deterministic**: Same input = same output
- ✅ **Cost Efficient**: Near-zero marginal cost per user

---

**Generated for Course Companion FTE - Generative AI Fundamentals**
