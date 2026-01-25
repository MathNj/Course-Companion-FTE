# Phase 2 Implementation Plan

**Project:** Course Companion FTE - Hybrid Intelligence Features
**Current Status:** Phase 1 Complete ✅
**Phase:** 2 - Selective Hybrid Intelligence (Premium Features)
**Last Updated:** 2026-01-26

---

## Phase 2 Overview

### Goal

Add **selective backend intelligence** that:
- Delivers clear additional educational value
- Is cost-justified as a premium feature
- Cannot be implemented using zero-LLM design
- Is user-initiated and feature-scoped
- Has clear cost tracking

### Architecture Pattern

```
ChatGPT App
    ↓
Backend
    ├─ Deterministic APIs (Phase 1) - Free tier
    └─ Hybrid Intelligence APIs (Phase 2, gated) - Premium tier
        └─ LLM calls (OpenAI/Anthropic)
```

### Phase 2 Rules

✅ **Hybrid intelligence MUST be:**
- Feature-scoped (limited to specific features)
- User-initiated (user requests it)
- Premium-gated (paid users only)
- Isolated (separate API routes)
- Cost-tracked (monitor per-user cost)

❌ **You may NOT:**
- Convert entire app to hybrid
- Auto-trigger hybrid features
- Make hybrid required for core UX
- Hide hybrid costs from analysis

---

## Feature Selection

### Available Features (Choose Up to 2)

| Feature | What It Does | Why It Needs LLM | Est. Cost/Request |
|---------|--------------|------------------|-------------------|
| **A. Adaptive Learning Path** | Analyzes patterns, generates personalized recommendations | Requires reasoning over learning data | $0.018 (2K tokens) |
| **B. LLM-Graded Assessments** | Evaluates free-form written answers with detailed feedback | Rule-based can't evaluate reasoning | $0.014 (1.5K tokens) |
| **C. Cross-Chapter Synthesis** | Connects concepts across chapters, generates "big picture" | Requires multi-document reasoning | $0.025 (2.5K tokens) |
| **D. AI Mentor Agent** | Long-running agent for complex tutoring workflows | Multi-turn problem solving | $0.036 (4K tokens) |

### Recommended Selection

**Feature 1: B. LLM-Graded Assessments** ✅
- **Why:** Highest educational value, clear differentiation from Phase 1
- **Value:** Detailed feedback on written answers, not just multiple choice
- **Cost:** $0.014 per request (reasonable for premium)
- **Implementation:** Evaluate short answers, essays, code explanations

**Feature 2: C. Cross-Chapter Synthesis** ✅
- **Why:** Unique capability not possible with deterministic backend
- **Value:** Connect concepts across chapters, show "big picture"
- **Cost:** $0.025 per request (higher value for deeper insights)
- **Implementation:** Generate concept maps, explain relationships

**Alternative Options:**
- **A. Adaptive Learning Path** - Good, but can be approximated with rules
- **D. AI Mentor Agent** - Powerful but expensive and complex

---

## Implementation Plan

### Task 1: Database Schema Updates

**Add Premium User Tracking:**

```sql
-- Update users table
ALTER TABLE users ADD COLUMN subscription_type TEXT DEFAULT 'free';
ALTER TABLE users ADD COLUMN subscription_expires_at TIMESTAMP;

-- Add cost tracking table
CREATE TABLE llm_usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    feature_type TEXT NOT NULL,  -- 'graded_assessment', 'synthesis'
    tokens_used INTEGER NOT NULL,
    cost_usd REAL NOT NULL,
    model_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Task 2: Backend Architecture Updates

**File Structure:**
```
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py           # Add subscription status
│   │   │   ├── content.py        # Phase 1 (unchanged)
│   │   │   ├── quiz.py           # Phase 1 (unchanged)
│   │   │   ├── progress.py       # Phase 1 (unchanged)
│   │   │   ├── premium.py        # NEW: Hybrid features
│   │   │   └── admin.py          # NEW: Admin/monitoring
│   ├── services/
│   │   ├── llm_service.py        # NEW: LLM API integration
│   │   └── cost_tracker.py       # NEW: Cost tracking
│   └── models/
│       └── subscription.py        # NEW: Subscription models
├── config/
│   └── llm_config.py             # NEW: LLM API keys and config
```

### Task 3: LLM Service Integration

**Create `backend/app/services/llm_service.py`:**

```python
import os
from typing import Dict, Any
from openai import OpenAI
from anthropic import Anthropic

class LLMService:
    """Service for LLM API calls (Phase 2 hybrid features)"""

    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    async def grade_assessment(
        self,
        question: str,
        student_answer: str,
        rubric: str
    ) -> Dict[str, Any]:
        """Grade free-form assessment using LLM"""
        prompt = f"""
        Grade this student answer:

        Question: {question}
        Student Answer: {student_answer}

        Rubric: {rubric}

        Provide:
        1. Score (0-100)
        2. Detailed feedback (what they did well, what to improve)
        3. Specific suggestions for improvement
        """
        # Implementation...

    async def synthesize_concepts(
        self,
        topics: list[str],
        focus: str = "connections"
    ) -> Dict[str, Any]:
        """Synthesize concepts across chapters"""
        prompt = f"""
        Analyze these topics from the Generative AI course:
        {topics}

        Focus on: {focus}

        Provide:
        1. How these concepts connect
        2. Key relationships
        3. Practical implications
        4. Suggested learning sequence
        """
        # Implementation...

    def track_cost(
        self,
        user_id: int,
        feature_type: str,
        tokens_used: int,
        cost_usd: float,
        model_name: str
    ):
        """Track LLM usage costs"""
        # Log to database
        pass
```

### Task 4: Premium API Routes

**Create `backend/app/api/routes/premium.py`:**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from app.services.llm_service import LLMService
from app.services.cost_tracker import CostTracker
from app.api.dependencies import get_current_user, require_premium

router = APIRouter(prefix="/api/v2/premium", tags=["premium"])

@router.post("/assessments/grade")
async def grade_assessment(
    question: str,
    student_answer: str,
    rubric: str,
    current_user = Depends(require_premium),
    llm_service: LLMService = Depends()
):
    """Grade free-form assessment using LLM (Premium Feature)"""

    # Check premium subscription
    if current_user.subscription_type != 'premium':
        raise HTTPException(
            status_code=403,
            detail="This feature requires a premium subscription"
        )

    # Call LLM
    result = await llm_service.grade_assessment(
        question=question,
        student_answer=student_answer,
        rubric=rubric
    )

    # Track cost
    llm_service.track_cost(
        user_id=current_user.id,
        feature_type="graded_assessment",
        tokens_used=result["tokens_used"],
        cost_usd=result["cost"],
        model_name="claude-sonnet"
    )

    return result

@router.post("/synthesis/generate")
async def generate_synthesis(
    topics: list[str],
    focus: str = "connections",
    current_user = Depends(require_premium),
    llm_service: LLMService = Depends()
):
    """Generate cross-chapter synthesis (Premium Feature)"""

    # Check premium subscription
    if current_user.subscription_type != 'premium':
        raise HTTPException(
            status_code=403,
            detail="This feature requires a premium subscription"
        )

    # Call LLM
    result = await llm_service.synthesize_concepts(
        topics=topics,
        focus=focus
    )

    # Track cost
    llm_service.track_cost(
        user_id=current_user.id,
        feature_type="synthesis",
        tokens_used=result["tokens_used"],
        cost_usd=result["cost"],
        model_name="claude-sonnet"
    )

    return result
```

### Task 5: Premium Gate Dependency

**Create `backend/app/api/dependencies.py`:**

```python
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User

def require_premium(current_user: User = Depends(get_current_user)):
    """Dependency to require premium subscription"""
    if current_user.subscription_type != 'premium':
        raise HTTPException(
            status_code=403,
            detail="This feature requires a premium subscription. Upgrade at /pricing"
        )
    return current_user
```

### Task 6: ChatGPT Actions Updates

**Add Premium Actions to Custom GPT:**

1. **Grade Written Assessment**
   - Endpoint: `POST /api/v2/premium/assessments/grade`
   - Description: Grade free-form answers with detailed feedback
   - Authentication: JWT + Premium check

2. **Generate Concept Synthesis**
   - Endpoint: `POST /api/v2/premium/synthesis/generate`
   - Description: Connect concepts across chapters
   - Authentication: JWT + Premium check

### Task 7: Environment Configuration

**Add to `.env`:**

```env
# LLM API Keys (Phase 2)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# LLM Configuration
LLM_DEFAULT_MODEL=claude-sonnet
LLM_MAX_TOKENS=4000
LLM_TEMPERATURE=0.7

# Premium Pricing
PREMIUM_MONTHLY_COST=9.99
FREE_TIER_DAILY_LIMIT=10
```

---

## Cost Analysis

### Phase 2 Cost Structure

| Feature | Model | Tokens/Request | Cost/Request | Est. Requests/User/Month | Monthly Cost/User |
|---------|-------|----------------|--------------|--------------------------|-------------------|
| LLM-Graded Assessments | Claude Sonnet | 1,500 | $0.014 | 20 | $0.28 |
| Cross-Chapter Synthesis | Claude Sonnet | 2,500 | $0.025 | 5 | $0.125 |
| **Total per User** | | | | | **$0.405/month** |

### Revenue Model

| Tier | Price | Features | Margin |
|------|-------|----------|--------|
| Free | $0/month | Phase 1 features only | N/A |
| Premium | $9.99/month | Phase 1 + 2 premium features | $9.59 (96%) |

### Breakeven Analysis

- **Cost per premium user:** $0.405/month
- **Revenue per premium user:** $9.99/month
- **Gross margin:** 96%
- **Breakeven users:** ~1 user covers LLM costs

### Scalability

| Users | LLM Costs | Revenue | Margin |
|-------|-----------|---------|--------|
| 10 | $4.05 | $99.90 | $95.85 (96%) |
| 100 | $40.50 | $999.00 | $958.50 (96%) |
| 1,000 | $405.00 | $9,990.00 | $9,585.00 (96%) |

---

## Testing Plan

### Unit Tests
1. Test premium gate dependency
2. Test LLM service integration
3. Test cost tracking
4. Test subscription validation

### Integration Tests
1. Test grading endpoint with real LLM
2. Test synthesis endpoint with real LLM
3. Test premium subscription flow
4. Test cost tracking accuracy

### Manual Tests
1. Test as free user (should get 403)
2. Test as premium user (should succeed)
3. Verify cost logging
4. Verify ChatGPT Actions integration

---

## Documentation Updates

### New Documentation Files
1. **PHASE-2-IMPLEMENTATION-GUIDE.md** - Implementation details
2. **PHASE-2-COST-ANALYSIS.md** - Detailed cost breakdown
3. **PREMIUM-FEATURES-GUIDE.md** - User-facing guide
4. **API-DOCUMENTATION-PHASE-2.md** - Updated API docs

### Update Existing Files
1. **README.md** - Add Phase 2 features
2. **ARCHITECTURE-DIAGRAM.md** - Add hybrid architecture
3. **CHATGPT-CONFIGURATION-GUIDE.md** - Add premium Actions

---

## Implementation Timeline

### Week 1: Foundation
- [ ] Database schema updates
- [ ] LLM service integration
- [ ] Cost tracking system
- [ ] Premium gate dependency

### Week 2: Features
- [ ] Implement LLM-Graded Assessments
- [ ] Implement Cross-Chapter Synthesis
- [ ] Add premium API routes
- [ ] Update authentication

### Week 3: Integration
- [ ] Update ChatGPT Actions
- [ ] Test premium features
- [ ] Cost tracking validation
- [ ] Performance testing

### Week 4: Documentation & Polish
- [ ] Write documentation
- [ ] Create cost analysis
- [ ] User guide for premium features
- [ ] Final testing

---

## Success Criteria

### Functional Requirements
- ✅ 2 hybrid features implemented
- ✅ Features are premium-gated
- ✅ Features are user-initiated
- ✅ Architecture clearly separated
- ✅ Cost tracking functional
- ✅ ChatGPT Actions updated

### Non-Functional Requirements
- ✅ Response time < 5 seconds for LLM calls
- ✅ 99.9% uptime for premium features
- ✅ Cost accuracy within 5%
- ✅ Clear error messages for free users

### Hackathon Scoring (20 points)
- ✅ Hybrid Feature Value (5 points)
- ✅ Cost Justification (5 points)
- ✅ Architecture Clarity (5 points)
- ✅ Implementation Quality (5 points)

---

## Next Steps

1. **Review and approve this plan** - Confirm feature selection
2. **Set up LLM API keys** - OpenAI and/or Anthropic
3. **Start implementation** - Begin with database updates
4. **Test incrementally** - Test each feature as built
5. **Document thoroughly** - Keep docs updated

---

**Status:** Planning Complete
**Ready to Start:** Pending approval
**Estimated Completion:** 4 weeks
