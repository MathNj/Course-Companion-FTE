"""
Chat Completions API Router

Provides OpenAI-compatible chat completions endpoint for the AI chat component.
"""

import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from openai import AsyncOpenAI

from app.dependencies import get_current_user
from app.models.user import User
from app.database import get_db


# Request/Response Models
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = "gpt-4o-mini"
    max_tokens: Optional[int] = 2000
    temperature: Optional[float] = 0.7


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]


router = APIRouter()

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    openai_client = AsyncOpenAI(api_key=openai_api_key)
else:
    openai_client = None


@router.post("/completions", response_model=ChatCompletionResponse)
async def chat_completions(
    request: ChatCompletionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    OpenAI-compatible chat completions endpoint.

    Supports conversational AI interaction with course content context.
    """

    # Check if OpenAI API key is configured
    if not openai_client:
        # Fallback to mock response
        return await mock_completion(request)

    try:
        # Build system prompt with course context
        system_prompt = """You are an AI tutor for a course on Generative AI Fundamentals. You help students learn about:

1. Introduction to Generative AI
2. Large Language Models (LLMs)
3. Transformer Architecture
4. Attention Mechanisms
5. Prompt Engineering
6. Applications and Use Cases
7. Ethics and Safety

Your role is to:
- Provide clear, accurate explanations
- Use examples when helpful
- Encourage student understanding
- Ask follow-up questions to deepen learning
- Keep responses concise but thorough

Always be friendly, encouraging, and focused on helping the student learn."""

        # Add system message as first message
        messages_with_system = [
            {"role": "system", "content": system_prompt}
        ]

        # Add user messages
        for msg in request.messages:
            messages_with_system.append({
                "role": msg.role,
                "content": msg.content
            })

        # Call OpenAI API
        response = await openai_client.chat.completions.create(
            model=request.model,
            messages=messages_with_system,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )

        # Return OpenAI-compatible response
        return ChatCompletionResponse(
            id=f"chatcmpl-{response.id}",
            object="chat.completion",
            created=response.created,
            model=response.model,
            choices=[{
                "index": choice.index,
                "message": {
                    "role": choice.message.role,
                    "content": choice.message.content
                },
                "finish_reason": choice.finish_reason
            } for choice in response.choices],
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        )

    except Exception as e:
        print(f"Error in chat completion: {e}")
        # Fall back to mock response on error
        return await mock_completion(request)


async def mock_completion(request: ChatCompletionRequest) -> ChatCompletionResponse:
    """Mock chat completion for demo/testing when OpenAI API is unavailable"""

    import time
    import uuid

    # Get last user message
    last_user_message = ""
    for msg in reversed(request.messages):
        if msg.role == "user":
            last_user_message = msg.content
            break

    # Generate mock response
    mock_response = generate_mock_response(last_user_message)

    return ChatCompletionResponse(
        id=f"chatcmpl-{uuid.uuid4().hex[:24]}",
        object="chat.completion",
        created=int(time.time()),
        model=request.model,
        choices=[{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": mock_response
            },
            "finish_reason": "stop"
        }],
        usage={
            "prompt_tokens": sum(len(msg.content.split()) for msg in request.messages),
            "completion_tokens": len(mock_response.split()),
            "total_tokens": sum(len(msg.content.split()) for msg in request.messages) + len(mock_response.split())
        }
    )


def generate_mock_response(user_message: str) -> str:
    """Generate contextual mock responses"""

    user_lower = user_message.lower()

    # Greeting responses
    if any(word in user_lower for word in ["hello", "hi", "hey", "greetings"]):
        return "Hello! I'm your AI tutor for the Generative AI Fundamentals course. How can I help you today? Feel free to ask questions about any of the course topics!"

    # Questions about transformers
    if "transformer" in user_lower:
        return """Great question about Transformers! The Transformer architecture revolutionized AI by introducing:

**Self-Attention Mechanism**: Allows the model to weigh the importance of different words in a sentence relative to each other.

**Parallel Processing**: Unlike RNNs, Transformers can process all positions simultaneously, making them much faster to train.

**Positional Encoding**: Since there's no sequential processing, positional information is added to help the model understand word order.

**Multi-Head Attention**: Multiple attention heads operate in parallel, allowing the model to focus on different aspects of relationships between words.

Would you like me to explain any of these concepts in more detail?"""

    # Questions about attention
    if "attention" in user_lower:
        return """Attention mechanisms are fundamental to modern AI! Here's the key idea:

**Intuition**: Attention allows a model to focus on relevant parts of the input when producing each part of the output. Think of it like when you're reading - you pay more attention to important words.

**Self-Attention**: In Transformers, each word "attends" to all other words to understand context. For example, in "The cat sat on the mat", when processing "cat", attention helps understand it relates to "sat" (action) and "mat" (location).

**Weights**: Attention assigns weights that determine how much focus to give each word. These weights are learned during training.

**Visualization**: You can think of attention as a heatmap showing which words are most connected to each other.

Shall I explain how this is implemented mathematically, or would you prefer examples?"""

    # Questions about LLMs
    if any(word in user_lower for word in ["llm", "large language model", "gpt", "language model"]):
        return """Large Language Models (LLMs) are fascinating! Here's what makes them special:

**Scale**: LLMs are trained on massive amounts of text data (billions of words) and have billions of parameters.

**Training**: They learn by predicting the next word in sequences, which surprisingly teaches them grammar, facts, reasoning, and even some understanding of the world.

**Capabilities**: Modern LLMs can write, code, answer questions, translate, and more - emerging from simple next-word prediction at scale.

**Architecture**: Most LLMs use the Transformer architecture we discussed, which enables them to handle long-range dependencies in text.

**Emergence**: Interesting capabilities "emerge" at scale - abilities not explicitly trained for but arising from the model's size and training.

What aspect of LLMs interests you most?"""

    # Questions about prompt engineering
    if "prompt" in user_lower:
        return """Prompt Engineering is a crucial skill for working with AI! Here are some key principles:

**Be Specific**: Clear, detailed prompts get better results than vague ones.

**Provide Context**: Give relevant background information to help the AI understand what you need.

**Examples Matter**: Showing examples of what you want (few-shot prompting) dramatically improves performance.

**Chain of Thought**: Asking the model to "think step by step" improves reasoning on complex problems.

**Format Matters**: Specify how you want the output (bullet points, code blocks, etc.).

**Iterate**: Refine your prompt based on the results you get.

Would you like me to give you some specific examples of good prompts, or do you have a particular task in mind?"""

    # Questions about course content
    if "chapter" in user_lower or "what will i learn" in user_lower:
        return """Here's what you'll learn in this course:

**Chapter 1: Introduction to Generative AI**
- What is generative AI and how it differs from traditional AI
- Key concepts and terminology

**Chapter 2: Large Language Models**
- How LLMs work
- Training methods and architecture

**Chapter 3: Transformer Architecture**
- The revolutionary architecture behind modern AI
- Self-attention and other key components

**Chapter 4: Attention Mechanisms**
- Deep dive into how attention works
- Variants and applications

**Chapter 5: Prompt Engineering**
- How to effectively communicate with AI
- Best practices and techniques

**Chapter 6: Applications**
- Real-world uses of generative AI
- Building AI applications

**Chapter 7: Ethics and Safety**
- Responsible AI practices
- Safety considerations

Which chapter would you like to start with?"""

    # Questions about quizzes or assessment
    if any(word in user_lower for word in ["quiz", "test", "assessment"]):
        return """Quizzes are a great way to test your understanding! Here's how they work:

Each chapter includes a quiz that:
- Tests key concepts from the chapter
- Provides immediate feedback on your answers
- Helps identify areas you might want to review

**Tips for Success**:
1. Complete the chapter content first
2. Take your time with each question
3. Read the feedback carefully
4. Review areas where you score lower

If you're a premium subscriber, you also have access to AI-graded assessments where you can write free-form answers and get detailed, personalized feedback!

Ready to try a quiz, or do you have questions about a specific topic?"""

    # Default response
    return """That's a great question! As your AI tutor, I'm here to help you learn about Generative AI.

We cover topics like:
- Large Language Models (LLMs)
- Transformer architecture
- Attention mechanisms
- Prompt engineering
- Applications and use cases
- Ethics and safety

Could you tell me more specifically what you'd like to learn about? The more specific your question, the better I can help!"""
