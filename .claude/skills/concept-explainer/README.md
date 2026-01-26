# Concept Explainer Skill

**Skill Type:** Educational / Runtime Prompt Enhancement

---

## 📋 What This Skill Does

The concept-explainer skill enhances your Course Companion GPT by:

1. **Assessing learner level** - Beginner, intermediate, or advanced
2. **Adapting explanations** - Match complexity to learner's background
3. **Using analogies** - Connect new concepts to familiar things
4. **Checking understanding** - Verify the learner grasped the concept
5. **Building progressively** - Start simple, add complexity gradually

---

## 🎯 When It Triggers

**Trigger Keywords:**
- "explain"
- "what is"
- "how does"
- "define"
- "tell me about"
- "I don't understand"

**Context Clues:**
- User seems confused
- User asks follow-up questions
- User repeatedly asks "what" or "how"
- User requests simplification

---

## 🚀 How to Use

### With Your Course Companion GPT:

The skill is automatically activated when students ask questions about concepts. It works seamlessly with your backend's content retrieval to provide accurate, grounded explanations.

### Example Interactions:

**Beginner:**
> "What is a neural network?"

**Skill Response:** "Think of a neural network like a digital brain. Just like your brain has neurons connected, a neural network has artificial neurons called 'nodes' that pass information to each other. When shown many examples, it learns patterns. It can recognize images, translate languages, or make decisions. Would you like me to explain how the learning works?"

**Intermediate:**
> "How does backpropagation work?"

**Skill Response:** "Backpropagation is how neural networks learn from mistakes. Imagine you take a quiz and get an answer wrong. You work backwards to see which question you missed. Neural networks do something similar: they calculate how wrong their output was, then go backward through the layers adjusting connection strengths to reduce the error. Over many examples, they get better at predicting. Want me to explain the mathematics?"

**Advanced:**
> "What is attention?"

**Skill Response:** "Attention is a mechanism for focusing on relevant context. It computes three vectors (Query, Key, Value) for each token. The Query represents what's being looked for, Key represents available context, and the output token determines what's important. This allows the model to prioritize different parts of the input when producing each output. Should I show you the formal formulation?"

---

## 📚 Course Content Integration

This skill works hand-in-hand with your Course Companion backend:

1. **Search** the course material for the concept
2. **Retrieve** relevant chapters and sections
3. **Explain** using appropriate complexity level
4. **Cite** sources (Chapter X, Section Y)

---

## ✅ Skill Features

- **3 Complexity Levels** - Beginner, Intermediate, Advanced
- **Assessment-first** - Always checks learner's level
- **Analogies and Examples** - Makes concepts relatable
- **Understanding Checks** - Verifies learner comprehension
- **Progressive Building** - Starts simple, adds depth
- **Source Citation** - Always references course material

---

## 🎓 Benefits for Students

- **Personalized Learning** - Explanations match their level
- **Better Retention** - Analogies make concepts stick
- **Increased Confidence** - Checking understanding prevents confusion
- **Deeper Learning** - Progressive building reveals layers
- **Accessible** - Complex topics become approachable

---

## 🎯 For Hackathon Scoring

This skill satisfies **Required Runtime Skills** (Section 8.1):

- ✅ **concept-explainer** - Explains concepts at various levels
- ✅ **quiz-master** - (you'll create this)
- ✅ **socratic-tutor** - (you'll create this)
- ✅ **progress-motivator** - (you'll create this)

---

## 📝 Next Steps

After creating this skill, you should:

1. **Test it** - Try it with sample questions
2. **Package it** - Create .skill file for distribution
3. **Integrate** - Ensure your GPT can use it
4. **Create remaining 3 skills** - quiz-master, socratic-tutor, progress-motivator

---

## 🚀 Quick Start

The skill is ready to use! Your Course Companion GPT will automatically leverage it when explaining concepts to students.

**Status:** ✅ Created and validated
**Location:** `backend/.skills/concept-explainer/`

**Ready for:** Integration with your GPT instructions
