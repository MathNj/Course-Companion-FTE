# ChatGPT App Test Scenarios

Use these conversation scenarios to thoroughly test the ChatGPT app integration.

## Scenario 1: New Student Journey

**Goal**: Test complete onboarding and first chapter flow

```
Student: "Hi, I want to learn about AI"

Expected GPT Response:
- Welcomes student
- Calls get_chapters() or get_progress()
- Explains course structure (6 chapters, free vs premium)
- Suggests starting with Chapter 1

Student: "Yes, start with Chapter 1"

Expected GPT Response:
- Calls get_chapter("chapter-1")
- Presents chapter title, learning objectives, estimated time
- Asks how student wants to proceed (read all, section by section, etc.)

Student: "Show me the first section"

Expected GPT Response:
- Presents section 1-1: "What is Generative AI?"
- Shows the content from the API response
- Offers to continue to next section

Student: "Continue to next section"

Expected GPT Response:
- Presents section 1-2: "Types of Generative AI"
- Shows LLMs, image models, audio/video, code generation
- Continues guiding through chapter

Student: "I'm done with the chapter, quiz me"

Expected GPT Response:
- Calls get_quiz("chapter-1-quiz")
- Presents quiz info (10 questions, 70% to pass, 15 min)
- Asks if student wants questions one-by-one or all at once
```

## Scenario 2: Quiz Flow

**Goal**: Test quiz presentation and grading

```
Student: "I want to take the Chapter 1 quiz"

Expected GPT Response:
- Calls get_quiz("chapter-1-quiz")
- Shows quiz metadata
- Presents first question or all questions (based on preference)

Student: "Give me all questions at once"

Expected GPT Response:
- Lists all 10 questions with options
- Asks student to provide answers

Student: "q1: option_a, q2: option_b, q3: false, q4: option_b, q5: option_b, q6: false, q7: code generation and testing, q8: true, q9: option_b, q10: privacy and bias"

Expected GPT Response:
- Calls submit_quiz() with formatted answers
- Shows score (e.g., "You scored 86.67%")
- Lists correct answers
- Shows explanations for incorrect/partially correct answers
- Celebrates if passed (shows 🎉 or similar)
- Mentions chapter completion status
- Suggests next chapter

Student: "Show me the explanation for Q5 again"

Expected GPT Response:
- References the grading_details from submit_quiz response
- Shows explanation for Q5 specifically
- Offers to explain other questions too
```

## Scenario 3: Progress Tracking

**Goal**: Test streak and milestone features

```
Student: "How am I doing?"

Expected GPT Response:
- Calls get_progress()
- Shows overall completion percentage
- Lists completed chapters
- Shows current streak (e.g., "7-day streak 🔥")
- Mentions achieved milestones (e.g., "Week Warrior unlocked!")
- Shows progress to next milestone
- Displays quiz statistics
- Encourages continued learning

Student: "What's my streak?"

Expected GPT Response:
- Uses data from get_progress() response
- Highlights current streak
- Mentions longest streak
- Shows milestone progress
- Motivates to maintain streak

Student: "What milestones have I achieved?"

Expected GPT Response:
- Lists achieved_milestones from progress response
- Celebrates each one
- Shows what's next
```

## Scenario 4: Freemium Gating

**Goal**: Test access control for premium content

```
[Assuming student is on free tier]

Student: "Show me Chapter 4"

Expected GPT Response:
- Calls get_chapter("chapter-4")
- Receives 403 Forbidden response
- Explains this is premium content
- Lists what Chapter 4 covers (from error response)
- Mentions upgrade benefits
- Suggests continuing with free chapters first
- NOT pushy about upgrading

Student: "What do I get with premium?"

Expected GPT Response:
- Lists Chapters 4-6 content
- Advanced prompting techniques
- AI safety and ethics
- Real-world applications
- Possibly mentions certificate of completion
- Remains helpful and informative

Student: "OK, I'll continue with Chapter 2"

Expected GPT Response:
- Calls get_chapter("chapter-2")
- Successfully retrieves content (free tier)
- Proceeds with teaching
```

## Scenario 5: Resume Learning

**Goal**: Test continuation for returning students

```
[Assuming student has completed Chapter 1, started Chapter 2]

Student: "I'm back, where did I leave off?"

Expected GPT Response:
- Calls get_progress()
- Identifies last activity (Chapter 2 in progress)
- Suggests continuing where left off
- Shows recent achievements (if any)

Student: "Yes, continue Chapter 2"

Expected GPT Response:
- Calls get_chapter("chapter-2")
- Can reference progress to suggest specific section
- Continues teaching

Student: "Actually, can I review Chapter 1?"

Expected GPT Response:
- Calls get_chapter("chapter-1")
- Retrieves content
- Mentions student already completed this
- Offers to focus on specific sections
```

## Scenario 6: Adaptive Teaching

**Goal**: Test personalization and difficulty adjustment

```
Student: "I don't understand transformers, can you explain simply?"

Expected GPT Response:
- Calls get_chapter("chapter-2") to get the section on transformers
- Presents the pre-authored content
- Uses beginner-friendly language to introduce the concept
- Offers to break it down further
- DOES NOT generate its own transformer explanation from training data

Student: "I need a more advanced explanation"

Expected GPT Response:
- References the same chapter content
- Highlights more technical details from the sections
- Discusses nuances mentioned in the course material
- Still uses pre-authored content, just presents it differently

Student: "Give me an analogy"

Expected GPT Response:
- Checks if chapter content includes analogies
- Uses analogies from the course if available
- If not in course, may create simple analogy but clearly labels it as supplementary
- Encourages reading the chapter section for full understanding
```

## Scenario 7: Error Handling

**Goal**: Test graceful error handling

```
Student: "Show me Chapter 10"

Expected GPT Response:
- Recognizes invalid chapter ID
- Explains there are only 6 chapters
- Lists available chapters
- Suggests a valid chapter

Student: "Quiz me on Chapter 7"

Expected GPT Response:
- Recognizes invalid quiz
- Lists available quizzes (chapter-1-quiz through chapter-6-quiz)
- Suggests taking a quiz on completed chapters

Student: "I want to submit my quiz but I forgot my answers"

Expected GPT Response:
- Explains submit_quiz needs answers
- Offers to retrieve the quiz questions again
- Explains the format for submitting (question_id: answer)
```

## Scenario 8: Content Verification

**Goal**: Verify GPT uses API content, not its own knowledge

```
Student: "What is the difference between generative AI and traditional AI according to this course?"

Expected GPT Response:
- Calls get_chapter("chapter-1")
- Quotes or paraphrases from Section 1-1
- Specifically mentions: "Creation Over Classification"
- Uses the exact examples from the course (cat image example)
- Attributes information to the chapter

Student: "Tell me about prompt engineering"

Expected GPT Response:
- Calls get_chapter("chapter-3")
- Presents the principles from the course
- Clear, specific prompts
- Providing context
- Specifying format
- Does NOT add its own prompt engineering tips outside course content

Student: "What does GPT stand for?"

Expected GPT Response:
- Should call get_chapter("chapter-2") even for this simple question
- References Chapter 2 content: "Generative Pre-trained Transformer"
- Explains the 'T' is for Transformer architecture
- Uses course material as source
```

## Verification Checklist

After testing each scenario, verify:

### ✅ API Usage
- [ ] GPT called appropriate API action
- [ ] Response used data from API, not GPT's training
- [ ] Error responses handled gracefully

### ✅ Content Accuracy
- [ ] Explanations match course material in `backend/content/`
- [ ] No hallucinations or made-up facts
- [ ] Quiz answers match answer keys in quiz JSON

### ✅ User Experience
- [ ] Responses are encouraging and supportive
- [ ] Clear next steps provided
- [ ] Progress celebrated appropriately
- [ ] Adaptive to student level

### ✅ Technical Correctness
- [ ] Chapter IDs formatted correctly (chapter-1, chapter-2, etc.)
- [ ] Quiz submissions formatted correctly
- [ ] Score calculations accurate
- [ ] Streak logic works correctly

## Performance Test

Test with rapid-fire questions:

```
1. "List all chapters"
2. "Show Chapter 1"
3. "Quiz me"
4. [Submit answers]
5. "My progress"
```

All within 2 minutes - verify:
- Actions complete successfully
- No timeouts
- Responses are coherent
- Data is consistent across calls

## Stress Test

Test error scenarios:

```
1. Submit quiz with missing answers → Should request missing answers
2. Request Chapter 10 → Should explain only 6 chapters exist
3. Submit quiz without taking it first → Should offer to get quiz first
4. Request premium content as free user → Should explain upgrade path
5. Rapid repeated calls → Should handle without breaking
```

---

**Testing complete?** Compare GPT behavior to expected responses. If gaps exist, update `instructions.md` and re-import!
