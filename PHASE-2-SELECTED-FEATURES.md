# Phase 2 Selected Features

**Selected Features (2):**
1. ✅ **LLM-Graded Assessments** ($0.014/request)
   - Evaluate free-form written answers with detailed feedback
   - Provide specific suggestions for improvement
   - Score: 0-100 with rubric-based grading

2. ✅ **Adaptive Learning Path** ($0.018/request)
   - Analyze learning patterns and performance
   - Generate personalized recommendations
   - Suggest optimal learning sequence

**API Keys Status:** Need to obtain OpenAI/Anthropic keys
**Implementation Strategy:** Start with mock LLM calls, add real API integration later

---

## Feature 1: LLM-Graded Assessments

### Purpose
Grade free-form written answers (short answers, essays, explanations) with detailed, personalized feedback that rule-based systems cannot provide.

### API Endpoint
```
POST /api/v2/premium/assessments/grade
```

### Request Schema
```json
{
  "question": "Explain how backpropagation works in neural networks",
  "student_answer": "Backpropagation is...",
  "rubric": "Clarity: 30%, Accuracy: 40%, Depth: 30%",
  "question_type": "short_answer" // or "essay", "code_explanation"
}
```

### Response Schema
```json
{
  "score": 85,
  "feedback": {
    "strengths": [
      "Good understanding of gradient flow",
      "Clear explanation of chain rule application"
    ],
    "areas_for_improvement": [
      "Could elaborate on loss function computation",
      "Missing details about weight updates"
    ],
    "specific_suggestions": [
      "Add example with specific numbers",
      "Mention learning rate role in weight updates"
    ]
  },
  "rubric_scores": {
    "clarity": 28,
    "accuracy": 35,
    "depth": 22
  },
  "tokens_used": 1500,
  "cost_usd": 0.014
}
```

### LLM Prompt Template
```
Grade this student answer:

Question: {question}
Student Answer: {student_answer}

Rubric: {rubric}

Provide:
1. Overall score (0-100)
2. Strengths (what they did well)
3. Areas for improvement (what's missing or incorrect)
4. Specific suggestions for improvement
5. Score breakdown by rubric category

Format as JSON.
```

---

## Feature 2: Adaptive Learning Path

### Purpose
Analyze student's learning patterns, quiz performance, and progress to generate personalized recommendations for what to study next and optimal learning sequence.

### API Endpoint
```
POST /api/v2/premium/learning-path/generate
```

### Request Schema
```json
{
  "focus": "reinforce_weaknesses", // or "fastest_completion", "deepest_understanding"
  "current_chapter": 5,
  "include_completed": true,
  "learning_style": "visual" // optional: "visual", "textual", "mixed"
}
```

### Response Schema
```json
{
  "learning_path": {
    "current_status": "Chapter 5: Attention Mechanisms (75% complete)",
    "recommended_next": [
      {
        "chapter": 6,
        "title": "Large Language Models",
        "reason": "Builds directly on attention mechanisms from Chapter 5",
        "priority": "high",
        "estimated_difficulty": "medium"
      },
      {
        "chapter": 3,
        "title": "Transformer Architecture (Review)",
        "reason": "Your quiz scores here were lower than other chapters",
        "priority": "medium",
        "estimated_difficulty": "easy (review)"
      }
    ],
    "knowledge_gaps": [
      {
        "topic": "Multi-head attention",
        "gap_severity": "moderate",
        "recommended_resources": ["Chapter 5, Section 3", "Practice Quiz 5.3"]
      },
      {
        "topic": "Positional encoding",
        "gap_severity": "minor",
        "recommended_resources": ["Chapter 5, Section 2"]
      }
    ],
    "study_plan": {
      "this_week": [
        "Complete Chapter 5 (remaining 25%)",
        "Review Chapter 3, Section 4 (positional encoding)",
        "Take Chapter 5 quiz"
      ],
      "next_week": [
        "Start Chapter 6: Large Language Models",
        "Complete Chapter 6 quiz",
        "Review synthesis: Chapters 3-6"
      ]
    },
    "motivation": "You're making great progress! Focusing on multi-head attention will solidify your understanding before moving to LLMs."
  },
  "tokens_used": 2000,
  "cost_usd": 0.018
}
```

### LLM Prompt Template
```
Analyze this student's learning data and generate personalized recommendations:

Current Progress:
- Chapter completed: {current_chapter}
- Quiz scores by chapter: {quiz_scores}
- Time spent per chapter: {time_data}
- Learning style: {learning_style}

Focus: {focus}

Provide:
1. Current status summary
2. Recommended next chapters (prioritized)
3. Knowledge gaps identified
4. Study plan for this week and next week
5. Motivational message

Consider:
- Prerequisite relationships between chapters
- Weak areas that need reinforcement
- Learning speed and preferences
- Optimal sequence for deep understanding

Format as JSON.
```

---

## Implementation Approach

### Phase 2A: Mock Implementation (Current)

**Files to Create:**
1. `backend/app/services/llm_service.py` - Mock LLM service
2. `backend/app/api/routes/premium.py` - Premium API routes
3. `backend/app/api/dependencies.py` - Premium gate dependency
4. `backend/app/models/subscription.py` - Subscription models
5. `backend/app/services/cost_tracker.py` - Cost tracking

**Database Updates:**
```sql
-- Add to users table
ALTER TABLE users ADD COLUMN subscription_type TEXT DEFAULT 'free';
ALTER TABLE users ADD COLUMN subscription_expires_at TIMESTAMP;

-- Create llm_usage_logs table
CREATE TABLE llm_usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    feature_type TEXT NOT NULL,
    tokens_used INTEGER NOT NULL,
    cost_usd REAL NOT NULL,
    model_name TEXT NOT NULL,
    mock_call BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Phase 2B: Real LLM Integration (After API Keys Obtained)

**Updates Needed:**
1. Add real API keys to `.env`
2. Update `llm_service.py` with real OpenAI/Anthropic clients
3. Replace mock responses with real LLM calls
4. Add error handling for LLM API failures
5. Add retry logic for failed requests

**Required API Keys:**
```
OPENAI_API_KEY=sk-...
# or
ANTHROPIC_API_KEY=sk-ant-...
```

---

## Cost Tracking

### Per-User Cost Limits

**Free Tier:**
- 0 premium requests per day
- Upsell prompt on premium feature access

**Premium Tier:**
- Up to 30 graded assessments/month ($0.42 cost)
- Up to 10 learning paths/month ($0.18 cost)
- Total LLM cost per user: $0.60/month
- Premium subscription: $9.99/month
- Gross margin: 94%

### Database Schema for Cost Tracking

```sql
CREATE TABLE llm_usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    feature_type TEXT NOT NULL,  -- 'graded_assessment', 'learning_path'
    tokens_used INTEGER NOT NULL,
    cost_usd REAL NOT NULL,
    model_name TEXT NOT NULL,
    request_details TEXT,  -- JSON metadata
    mock_call BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_llm_usage_user_date ON llm_usage_logs(user_id, created_at);
CREATE INDEX idx_llm_usage_feature ON llm_usage_logs(feature_type);
```

---

## Next Steps

### Immediate (Today)
1. ✅ Create database migration scripts
2. ✅ Implement mock LLM service
3. ✅ Create premium API routes
4. ✅ Add premium gate dependency
5. ✅ Update authentication to include subscription status

### Short-term (This Week)
1. Test premium features with mock LLM
2. Create ChatGPT Actions for premium features
3. Add cost tracking UI/logging
4. Write documentation

### Medium-term (After API Keys)
1. Replace mock with real LLM calls
2. Add error handling and retries
3. Performance optimization
4. Cost monitoring and alerts

---

**Status:** Ready to implement with mock LLM
**API Keys Needed:** OpenAI or Anthropic
**Estimated Timeline:** 2 weeks for mock implementation, 1 week for real LLM integration
