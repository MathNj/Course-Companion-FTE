# Agent Skills Test Plan

Comprehensive test plan for all 4 hackathon-required Agent Skills.

## Test Environment

**ChatGPT Custom GPT URL:** https://chatgpt.com/g/g-6976388081fc8191b24f585910d2b6ce-course-companion-fte-generative-ai

**Skills to Test:**
1. concept-explainer
2. quiz-master
3. socratic-tutor
4. progress-motivator

## Test Strategy

Since the Agent Skills are designed to be used by Claude (not ChatGPT), we'll test them in two ways:

### Part 1: Direct Skill Testing (Recommended)
Test the skills directly by reading the SKILL.md files and verifying they follow the skill-creator template correctly.

### Part 2: ChatGPT Custom GPT Testing (Optional)
Test if similar behaviors work in the ChatGPT Custom GPT (which uses backend APIs, not Agent Skills).

---

## Part 1: Direct Skill Verification

### Test 1: concept-explainer

**Verification Steps:**

1. **Check Frontmatter**
   - ✅ Contains `name: concept-explainer`
   - ✅ Contains comprehensive description with trigger keywords
   - ✅ Description explains when to use the skill

2. **Check Content Structure**
   - ✅ Core Principles section present
   - ✅ Explanation Levels (Beginner, Intermediate, Advanced)
   - ✅ Explanation Framework defined
   - ✅ Trigger Detection patterns
   - ✅ Quick prompts for different scenarios
   - ✅ Anti-patterns to avoid
   - ✅ Example interactions

3. **Check Quality**
   - ✅ Clear, actionable instructions
   - ✅ Specific examples for Generative AI course
   - ✅ Progressive complexity levels
   - ✅ Uses analogies and check-for-understanding
   - ✅ Under 500 lines (context efficient)

**Expected Trigger Behavior:**
- User: "Explain backpropagation"
- Skill: Gauges level → Explains appropriately → Checks understanding

---

### Test 2: quiz-master

**Verification Steps:**

1. **Check Frontmatter**
   - ✅ Contains `name: quiz-master`
   - ✅ Description includes trigger keywords
   - ✅ Mentions quiz facilitation and encouragement

2. **Check Content Structure**
   - ✅ Core Philosophy (Make quizzes engaging, immediate feedback, celebrate effort)
   - ✅ Quiz Flow (5 steps: understand → expect → present → feedback → encourage)
   - ✅ Question Presentation Strategies
   - ✅ Positive Reinforcement Techniques
   - ✅ Managing Quiz Flow (adaptive difficulty)
   - ✅ Encouragement Language
   - ✅ Dealing with Anxiety
   - ✅ Integration with Backend APIs

3. **Check Quality**
   - ✅ Multiple question types covered
   - ✅ Specific language templates for encouragement
   - ✅ Anxiety management strategies
   - ✅ Anti-patterns clearly defined
   - ✅ Backend integration documented

**Expected Trigger Behavior:**
- User: "Quiz me on Chapter 3"
- Skill: Understands context → Sets expectations → Presents questions one-by-one → Provides feedback

---

### Test 3: socratic-tutor

**Verification Steps:**

1. **Check Frontmatter**
   - ✅ Contains `name: socratic-tutor`
   - ✅ Description includes "questioning techniques" and trigger keywords
   - ✅ Emphasizes not giving direct answers

2. **Check Content Structure**
   - ✅ Core Philosophy (Never give answers, ask questions first, build on what they know)
   - ✅ The Socratic Method (Question sequencing)
   - ✅ Question Types (Diagnostic, Guiding, Probing, Reflective)
   - ✅ Hint Progression (3 levels, never reaches level 4)
   - ✅ Common Scenarios (lost, partial, wrong, asks for answer)
   - ✅ Domain-specific examples
   - ✅ Anti-patterns to avoid

3. **Check Quality**
   - ✅ Clear distinction from direct tutoring
   - ✅ Specific question templates
   - ✅ Progressive hint levels
   - ✅ Domain-specific examples (neural networks, transformers, backpropagation)
   - ✅ Never reaches direct answer

**Expected Trigger Behavior:**
- User: "Help me think through attention mechanism"
- Skill: Asks diagnostic questions → Guides with questions → Celebrates discovery

---

### Test 4: progress-motivator

**Verification Steps:**

1. **Check Frontmatter**
   - ✅ Contains `name: progress-motivator`
   - ✅ Description includes celebration, progress tracking, triggers
   - ✅ Mentions gamification

2. **Check Content Structure**
   - ✅ Core Philosophy (Celebrate wins, make progress visible, maintain momentum)
   - ✅ Progress Display structure
   - ✅ Celebration Templates (first milestones, streaks, scores, completions)
   - ✅ Progress Categories (content, quizzes, streak, time)
   - ✅ Handling Different Scenarios (strong, moderate, slowing, broken streak, return from break)
   - ✅ Achievement Unlocks (Bronze, Silver, Gold, Platinum)
   - ✅ Motivational Language Patterns
   - ✅ Integration with Backend APIs

3. **Check Quality**
   - ✅ Comprehensive scenario coverage
   - ✅ Tiered achievement system
   - ✅ Positive reframing of setbacks
   - ✅ Specific celebration templates
   - ✅ Backend data structure documented
   - ✅ Anti-patterns clearly defined

**Expected Trigger Behavior:**
- User: "Show me my progress"
- Skill: Fetches progress → Celebrates achievements → Shows metrics → Encourages next steps

---

## Part 2: ChatGPT Custom GPT Behavior Tests

These tests verify that the ChatGPT Custom GPT exhibits similar behaviors (even though it uses backend APIs, not Agent Skills).

### Test 1: Concept Explanation

**Prompt:** "Explain what a transformer model is"

**Expected Behavior:**
- GPT calls `search_content` or `get_chapter_content` API
- Provides clear explanation appropriate for the user's level
- Uses examples from the course content
- Checks if user understands

**Success Criteria:**
- ✅ Calls backend API (doesn't hallucinate)
- ✅ Uses course material (grounded Q&A)
- ✅ Explains clearly
- ✅ Offers to clarify or go deeper

---

### Test 2: Quiz Functionality

**Prompt:** "Quiz me on neural networks"

**Expected Behavior:**
- GPT calls `get_quiz` API for neural network questions
- Presents questions one at a time
- Provides feedback after each answer
- Encourages and celebrates correct answers
- Frames mistakes positively

**Success Criteria:**
- ✅ Calls backend API for quiz data
- ✅ Presents questions clearly
- ✅ Provides immediate feedback
- ✅ Uses encouraging language
- ✅ Tracks score

---

### Test 3: Learning Guidance (Socratic-like)

**Prompt:** "I'm stuck on backpropagation but don't tell me the answer"

**Expected Behavior:**
- GPT calls `search_content` to retrieve backpropagation material
- Guides learning through questions
- Doesn't provide direct answers immediately
- Builds understanding step-by-step

**Success Criteria:**
- ✅ Retrieves relevant content
- ✅ Asks guiding questions
- ✅ Doesn't just give the answer
- ✅ Builds on student's knowledge

---

### Test 4: Progress Tracking

**Prompt:** "Show me my progress"

**Expected Behavior:**
- GPT calls `get_user_progress` API
- Celebrates achievements
- Shows completion metrics
- Encourages continued learning
- Handles low progress positively

**Success Criteria:**
- ✅ Calls backend API for progress data
- ✅ Celebrates achievements
- ✅ Shows specific metrics
- ✅ Uses positive, encouraging language
- ✅ Suggests next steps

---

## Test Execution Checklist

### Skill Verification (Manual)

Run these commands to verify skill structure:

```bash
# Test concept-explainer
python backend/.skills/concept-explainer/scripts/validate.py

# Test quiz-master
python backend/.skills/quiz-master/scripts/validate.py

# Test socratic-tutor
python backend/.skills/socratic-tutor/scripts/validate.py

# Test progress-motivator
python backend/.skills/progress-motivator/scripts/validate.py
```

**Expected Output:** All should print `[SUCCESS]` messages.

---

### ChatGPT Custom GPT Testing (Manual)

1. Open ChatGPT Custom GPT: https://chatgpt.com/g/g-6976388081fc8191b24f585910d2b6ce-course-companion-fte-generative-ai

2. Run each test prompt from Part 2 above

3. Verify backend API calls are made (check Actions used)

4. Verify responses follow expected behavior

---

## Success Criteria

### Skill Creation
- ✅ All 4 skills have SKILL.md with proper frontmatter
- ✅ All skills have validation scripts
- ✅ All skills have README.md
- ✅ All skills validated successfully
- ✅ All skills committed to git
- ✅ All skills pushed to GitHub

### Skill Quality
- ✅ Clear trigger keywords in descriptions
- ✅ Comprehensive content covering all scenarios
- ✅ Specific examples and templates
- ✅ Anti-patterns documented
- ✅ Backend integration explained
- ✅ Under 500 lines each (context efficient)

### Hackathon Requirements
- ✅ concept-explainer skill created
- ✅ quiz-master skill created
- ✅ socratic-tutor skill created
- ✅ progress-motivator skill created
- ✅ All skills follow skill-creator template

---

## Next Steps After Testing

If tests pass:
- ✅ Agent Skills requirement is complete
- Consider creating demo video
- Write cost analysis document
- Create architecture diagram

If tests fail:
- Fix any validation errors
- Update SKILL.md content as needed
- Re-test and re-commit

---

## Notes

**Important:** Agent Skills are designed for Claude Code, not ChatGPT Custom GPTs. The ChatGPT Custom GPT uses backend APIs directly and implements similar behaviors through its instructions. The Agent Skills are a separate hackathon requirement that demonstrate the ability to create reusable, modular skill packages.
