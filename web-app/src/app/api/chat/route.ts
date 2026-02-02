import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { messages } = await request.json();

    // Get the last user message
    const lastMessage = messages[messages.length - 1];

    // TODO: Integrate with ChatGPT API using your MCP tools
    // For now, return a simple response based on the user's input

    const userMessage = lastMessage.content.toLowerCase();

    let response = "";

    // Simple pattern matching for demo
    if (userMessage.includes("chapter") && userMessage.includes("available")) {
      response = "I found 6 chapters available in this course:\n\n" +
        "1. 📖 Introduction to Generative AI\n" +
        "2. 🤖 Large Language Models\n" +
        "3. 💡 Prompt Engineering\n" +
        "4. 🔌 API Integration\n" +
        "5. 🛠️ Building Applications\n" +
        "6. 🚀 Deployment & Best Practices\n\n" +
        "Which chapter would you like to explore?";
    }
    else if (userMessage.includes("progress") || userMessage.includes("how am i doing")) {
      response = "📊 Your Learning Progress:\n\n" +
        "✅ Chapters Completed: 2/6 (33%)\n" +
        "🔥 Current Streak: 7 days\n" +
        "⏱️  Total Learning Time: 4.5 hours\n" +
        "✅ Quizzes Passed: 3/5\n\n" +
        "You're making great progress! Keep it up! 💪";
    }
    else if (userMessage.includes("quiz") || userMessage.includes("test me")) {
      response = "I can quiz you on any chapter! Here's a quick question from Chapter 1:\n\n" +
        "❓ What are the three main types of Generative AI models?\n" +
        "a) Text, Image, Audio\n" +
        "b) LLMs, GANs, Diffusion\n" +
        "c) supervised, unsupervised, reinforcement\n\n" +
        "Type your answer!";
    }
    else if (userMessage.includes("help") || userMessage.includes("can you do")) {
      response = "I'm here to help you learn! Here's what I can do:\n\n" +
        "📚 **Explain Concepts** - Break down complex topics\n" +
        "📝 **Create Quizzes** - Test your knowledge\n" +
        "🔍 **Find Information** - Search across all chapters\n" +
        "📊 **Track Progress** - See how you're doing\n" +
        "💡 **Give Tips** - Hackathon best practices\n\n" +
        "What would you like help with?";
    }
    else {
      response = "That's a great question! I'm here to help you learn about " +
        "Generative AI and prepare for the hackathon.\n\n" +
        "I can:\n" +
        "• Explain chapters in simple terms\n" +
        "• Quiz you on any topic\n" +
        "• Help you find specific information\n" +
        "• Track your learning progress\n\n" +
        "What would you like to explore?";
    }

    return NextResponse.json({
      message: response,
      sources: [
        {
          title: "Course Content",
          url: "/chapters"
        }
      ]
    });

  } catch (error) {
    console.error('Chat API Error:', error);
    return NextResponse.json(
      { error: 'Failed to process chat message' },
      { status: 500 }
    );
  }
}
