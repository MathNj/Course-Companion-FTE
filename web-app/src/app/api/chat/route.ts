import { NextRequest, NextResponse } from 'next/server';

// Backend API configuration - uses OpenAI SDK, not custom fetch
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

/**
 * Chat API Route - Proxies to backend OpenAI SDK integration

 * This endpoint calls the backend which uses the official OpenAI SDK
 * (not custom fetch calls) for chat completions with proper error handling,
 * retries, and token management.
 */
export async function POST(request: NextRequest) {
  try {
    const { messages, max_tokens = 1000, temperature = 0.7 } = await request.json();

    // Validate input
    if (!messages || !Array.isArray(messages) || messages.length === 0) {
      return NextResponse.json(
        { error: 'Invalid messages format' },
        { status: 400 }
      );
    }

    // Call backend chat endpoint (uses OpenAI SDK)
    const response = await fetch(`${API_BASE}/api/v1/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages,
        max_tokens,
        temperature,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      console.error('Backend chat error:', error);

      return NextResponse.json(
        {
          message: `I'm having trouble connecting to the AI assistant. Please try again!\n\n(Error: ${response.status})`,
          error: error.detail || 'Backend error',
        },
        { status: response.status }
      );
    }

    const data = await response.json();

    return NextResponse.json({
      message: data.message,
      sources: data.sources || [],
    });

  } catch (error) {
    console.error('Chat API Error:', error);
    return NextResponse.json(
      {
        message: "I'm having trouble connecting right now. Please try again!",
        error: 'Failed to process chat message'
      },
      { status: 500 }
    );
  }
}

/**
 * GET endpoint to check chat configuration
 */
export async function GET() {
  try {
    const response = await fetch(`${API_BASE}/api/v1/chat/config`);

    if (!response.ok) {
      throw new Error('Failed to fetch chat config');
    }

    const config = await response.json();

    return NextResponse.json({
      status: 'connected',
      backend: API_BASE,
      model: config.model,
      features: config.features,
      mcp_tools: config.mcp_tools,
    });
  } catch (error) {
    return NextResponse.json({
      status: 'disconnected',
      error: 'Cannot connect to backend chat service',
    }, { status: 503 });
  }
}
