# How to Integrate ChatGPT in Your Frontend Dashboard

## Quick Overview

You have **3 options** for integrating ChatGPT into your dashboard:

---

## ✅ Option 1: Floating AI Assistant Button (EASIEST - RECOMMENDED)

**What it looks like:**
- A floating button in the bottom-right corner
- Click to open a chat panel
- Available on every page
- Non-intrusive, always accessible

### Add it in 2 simple steps:

#### Step 1: Add to your main layout

Open `web-app/src/app/layout.tsx`:

```tsx
import AIAssistant from '@/components/AIAssistantEmbedded';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="__className_f367f3">
        {children}

        {/* Add this line - that's it! */}
        <AIAssistant />

      </body>
    </html>
  );
}
```

#### Step 2: Done! 🎉

Now you'll see a floating "Ask AI Assistant" button on every page!

**Preview:**
```
┌─────────────────────────────────┐
│  Your Dashboard                 │
│                                 │
│  [Chapters] [Progress] [Quiz]    │
│                                 │
│                                 │
│                    ┌───────────┐│
│                    │ 🤖 Ask AI ││ ← Floating button
│                    └───────────┘│
└─────────────────────────────────┘
```

---

## ✅ Option 2: Add to Navigation Menu

**What it looks like:**
- A link in your top navigation bar
- Opens chat in the same page or modal

### Add to Header component:

Open `web-app/src/components/Header.tsx` and add the menu item:

```tsx
import { Sparkles } from 'lucide-react';
import Link from 'next/link';

// In your nav items section, add:
<Link href="/ai-assistant">
  <button className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg transition-all">
    <Sparkles className="w-4 h-4" />
    <span>AI Assistant</span>
  </button>
</Link>
```

---

## ✅ Option 3: Dedicated Page Section

**What it looks like:**
- A full-width chat section on your dashboard
- More prominent, always visible

### Add to your dashboard page:

Open `web-app/src/app/dashboard/page.tsx` and add the section:

```tsx
import AIAssistant from '@/components/AIAssistantEmbedded';

export default function StudentDashboard() {
  // ... existing code ...

  return (
    <div className="min-h-screen bg-[#0B0C10]">
      <Header />

      {/* Existing dashboard content */}
      <div className="container mx-auto px-4 py-8">
        {/* Your existing stats and charts */}
      </div>

      {/* Add AI Assistant section */}
      <div className="container mx-auto px-4 pb-8">
        <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">
                🤖 AI Learning Assistant
              </h2>
              <p className="text-zinc-400">
                Get instant help with course content, quizzes, and more
              </p>
            </div>
            <Sparkles className="w-12 h-12 text-emerald-500" />
          </div>

          {/* Embedded chat interface */}
          <AIAssistant />
        </div>
      </div>
    </div>
  );
}
```

But wait! The `AIAssistant` component uses state for open/close. We need a version that's always visible. Let me create that:

---

## Full-Page Chat Component (Always Visible)

Create `web-app/src/components/AIAssistantFull.tsx`:

```tsx
'use client';

import { useState } from 'react';
import { Send, Sparkles } from 'lucide-react';

export default function AIAssistantFull() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hi! 👋 I'm your AI learning assistant. How can I help you learn today?"
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user' as const, content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: [...messages, userMessage] })
      });

      const data = await res.json();

      setMessages(prev => [...prev, {
        role: 'assistant' as const,
        content: data.message
      }]);
    } catch (error) {
      console.error('Error:', error);
    }

    setIsLoading(false);
  };

  return (
    <div className="bg-zinc-900 rounded-xl border border-zinc-800 overflow-hidden">
      {/* Messages */}
      <div className="h-[500px] overflow-y-auto p-6 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
              msg.role === 'user'
                ? 'bg-emerald-600 text-white'
                : 'bg-zinc-800 text-zinc-100 border border-zinc-700'
            }`}>
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-zinc-800 rounded-2xl px-4 py-3 border border-zinc-700">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="p-4 border-t border-zinc-800">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask me anything about the course..."
            className="flex-1 bg-zinc-800 text-white px-4 py-3 rounded-lg border border-zinc-700 focus:border-emerald-500 focus:outline-none"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            className="bg-emerald-600 hover:bg-emerald-700 text-white p-3 rounded-lg transition-colors disabled:opacity-50"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

## Which Option Should You Choose?

### For a Hackathon: **Option 1 (Floating Button)** ⭐

**Why?**
- ✅ Quickest to implement (2 minutes)
- ✅ Always accessible but not intrusive
- ✅ Works on all pages automatically
- ✅ Doesn't clutter the UI
- ✅ Users can open it when they need help

### For a Production App: **Option 3 (Dashboard Section)**

**Why?**
- ✅ More prominent
- ✅ Shows AI assistant as a key feature
- ✅ Always visible on dashboard
- ✅ Can show alongside progress stats

---

## Quick Start (Right Now!)

### Add the floating button in 2 minutes:

1. Open `web-app/src/app/layout.tsx`

2. Add these 2 lines:

```tsx
import AIAssistant from '@/components/AIAssistantEmbedded';

// ... inside the body tag ...
<AIAssistant />
```

3. Refresh your browser!

4. You'll see the floating button in the bottom-right corner!

---

## How It Works

### Architecture:

```
┌─────────────────────┐
│  Your Frontend      │
│  localhost:3000     │
│                     │
│  ┌──────────────┐   │
│  │ Chat Panel   │   │
│  └──────┬───────┘   │
│         │           │
│         ▼           │
│  /api/chat (Route)  │
│         │           │
│         ▼           │
│  [ ChatGPT API ]    │  ← Future: Add OpenAI API
│  [ Your Backend ]   │  ← Current: Simple responses
└─────────────────────┘
```

### Current Behavior:

1. User types message in chat panel
2. Frontend sends to `/api/chat`
3. API returns simple pattern-matched responses
4. Chat displays response

### To Connect Real ChatGPT:

You'll need to:

1. **Get OpenAI API Key**
2. **Add to your `.env.local`:**
   ```
   OPENAI_API_KEY=your-key-here
   ```
3. **Update `/api/chat/route.ts`** to call OpenAI API with your MCP tools

---

## What Users Can Do Right Now:

✅ Ask about available chapters
✅ Check their progress
✅ Get quiz questions
✅ Request help with topics
✅ Search for information

All from within your dashboard! 🎉

---

## Next Steps

1. ✅ **Add floating button** (Option 1) - 2 minutes
2. ✅ **Test with users** - Get feedback
3. ✅ **Connect real OpenAI API** (if needed)
4. ✅ **Add to Gadget MCP tools** for live data

---

## Troubleshooting

**Button not showing?**
- Check browser console for errors
- Make sure `AIAssistantEmbedded.tsx` exists
- Verify import path is correct

**Chat not responding?**
- Check `/api/chat` route exists
- Look at browser Network tab for API errors
- Check backend logs

**Want real ChatGPT responses?**
- You'll need to add OpenAI API integration
- Or use the ChatGPT App directly (separate from frontend)

---

**Recommendation:** Start with Option 1 (floating button) for your hackathon. It's the quickest way to add AI assistance to your dashboard! 🚀
