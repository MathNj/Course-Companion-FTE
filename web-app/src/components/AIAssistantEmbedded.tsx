'use client';

import { useState, useEffect } from 'react';
import { ArrowRight, Send, Sparkles, X, Lightbulb, FileQuestion, Target, Trophy, Bot } from 'lucide-react';
import { SkillModeSelector } from '@/components/SkillModeSelector';
import { detectSkill, getSkillIcon, getSkillDisplayName, SkillType } from '@/lib/skills/skillDetector';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  skill?: SkillType;
}

export default function AIAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentSkill, setCurrentSkill] = useState<SkillType>('general');
  const [isClient, setIsClient] = useState(false);
  const [showSkillToast, setShowSkillToast] = useState(false);
  const [detectedSkill, setDetectedSkill] = useState<SkillType | null>(null);

  useEffect(() => {
    setIsClient(true);
  }, []);

  // Initialize with welcome message
  useEffect(() => {
    if (isOpen && messages.length === 0 && isClient) {
      setMessages([{
        role: 'assistant',
        content: `Hi! 👋 I'm your AI Learning Assistant with 4 intelligent modes:

💡 **Explainer** - Clear explanations at your level
📝 **Quiz Master** - Supportive practice quizzes
🎯 **Socratic Tutor** - Guides you to discover answers
🏆 **Progress** - Celebrates your achievements

Try saying:
• "Explain neural networks"
• "Test me on this chapter"
• "Help me think through this without giving the answer"
• "Show me my progress"

What would you like to explore?`,
        skill: 'general'
      }]);
    }
  }, [isOpen, messages.length, isClient]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userInput = input;

    // Detect skill from user input
    const detection = detectSkill(userInput);
    if (detection.confidence > 0.7) {
      setDetectedSkill(detection.skill);
      setCurrentSkill(detection.skill);
      setShowSkillToast(true);
      setTimeout(() => setShowSkillToast(false), 3000);
    }

    const userMessage: ChatMessage = {
      role: 'user',
      content: userInput,
      skill: currentSkill
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Generate skill-enhanced system prompt
      const systemPrompt = generateSkillPrompt(currentSkill);

      // Call backend API
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify({
          messages: [
            {
              role: 'system',
              content: systemPrompt,
            },
            ...messages.slice(-10).map(m => ({
              role: m.role,
              content: m.content,
            })),
            {
              role: 'user',
              content: userInput,
            }
          ],
          model: 'gpt-4o-mini',
          max_tokens: 800,
          temperature: 0.7,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get AI response');
      }

      const data = await response.json();
      const aiResponse = data.choices?.[0]?.message?.content || generateFallbackResponse(userInput, currentSkill);

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: aiResponse,
        skill: currentSkill
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      const fallbackResponse = generateFallbackResponse(userInput, currentSkill);

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: fallbackResponse,
        skill: currentSkill
      };

      setMessages(prev => [...prev, assistantMessage]);
    }

    setIsLoading(false);
  };

  // Generate skill-specific system prompt
  const generateSkillPrompt = (skill: SkillType): string => {
    const basePrompt = "You are a helpful AI learning assistant for a Generative AI course. Be friendly, encouraging, and educational. Keep responses concise but thorough.";

    switch (skill) {
      case 'concept-explainer':
        return `${basePrompt}

You are in CONCEPT-EXPLAINER mode 💡

Guidelines:
- Determine learner level (beginner/intermediate/advanced)
- Provide multi-layer explanations: Definition → Intuition → Example
- Use analogies and visual descriptions
- Start simple, add complexity gradually
- Check understanding frequently
- Ask: "Does this make sense? Want me to go deeper or simplify?"

Remember: Build intuition before technical details. Be encouraging.`;

      case 'quiz-master':
        return `${basePrompt}

You are in QUIZ-MASTER mode 📝

Guidelines:
- Frame as learning opportunity, not testing (no pressure)
- Show one question at a time from the chapter content
- Provide immediate feedback with explanations
- Celebrate correct answers
- Be supportive with incorrect answers (no shaming)
- Adapt difficulty based on performance
- Celebrate completion and progress

Remember: Mistakes are learning opportunities. Focus on growth, not grades.`;

      case 'socratic-tutor':
        return `${basePrompt}

You are in SOCRATIC-TUTOR mode 🎯

Guidelines:
- NEVER give direct answers first
- Start with questions: "What do you think...?" "How would you approach...?"
- Provide minimal, progressive hints only when truly stuck
- Celebrate the thinking process and insights
- Build on what they already know
- Use diagnostic → guiding → probing questions sequence
- Only reveal answer if explicitly requested or after multiple hints

Remember: Ask questions, don't give answers. Help them discover it themselves.`;

      case 'progress-motivator':
        return `${basePrompt}

You are in PROGRESS-MOTIVATOR mode 🏆

Guidelines:
- Start with enthusiasm and celebration
- Make progress visible (chapters, scores, streaks)
- Celebrate every win, big and small
- Frame setbacks positively (breaks are normal)
- Focus on growth and consistency
- Highlight milestones and achievements
- Encourage next steps

Remember: Every step forward is progress worth celebrating. You're doing great!`;

      default:
        return basePrompt;
    }
  };

  // Generate fallback response when API fails
  const generateFallbackResponse = (userInput: string, skill: SkillType): string => {
    const lowerInput = userInput.toLowerCase();

    switch (skill) {
      case 'concept-explainer':
        return `I'd be happy to explain that concept! However, I'm having trouble connecting to my AI backend right now.

While I reconnect, you can:
• Read through the chapter content above
• Check out the chapter quiz for practice
• Try rephrasing your question

What specifically would you like to know about this topic?`;

      case 'quiz-master':
        return `Great choice to practice! I'm setting up a quiz for you, but my connection is unstable.

You can take the chapter quiz from the Quiz tab above. The quiz is designed to be low-pressure and supportive - perfect for learning!

The quiz will:
• Test your understanding chapter by chapter
• Provide immediate feedback
• Help you identify areas to review

Ready when you are!`;

      case 'socratic-tutor':
        return `I'd love to guide you through this! Let me think...

I'm having connection issues, but I don't want to just give you the answer.

Can you tell me: What's your current understanding of this concept? We can work through it together step by step - I'll ask questions to help you discover the answer yourself.`;

      case 'progress-motivator':
        return `You're doing amazing! Let me check your progress stats...

I'm having trouble loading your detailed stats right now, but that doesn't change your achievement! Every chapter you complete, every quiz you take, every day you show up - that's real progress.

Your commitment to learning is what matters most. Keep showing up, keep learning, and you'll master this material!

Would you like me to help you plan your next learning session?`;

      default:
        return `I'm here to help you learn! I'm experiencing some connection issues at the moment.

In the meantime, you can:
• Read through the chapter content
• Try the chapter quiz
• Check your progress dashboard
• Review previous chapters

I'll be back shortly to answer your questions!`;
    }
  };

  // Get skill icon component
  const getSkillIconComponent = (skill: SkillType) => {
    switch (skill) {
      case 'concept-explainer': return <Lightbulb className="w-3 h-3" />;
      case 'quiz-master': return <FileQuestion className="w-3 h-3" />;
      case 'socratic-tutor': return <Target className="w-3 h-3" />;
      case 'progress-motivator': return <Trophy className="w-3 h-3" />;
      default: return <Bot className="w-3 h-3" />;
    }
  };

  const suggestions = [
    { text: "Explain neural networks", skill: 'concept-explainer' as SkillType },
    { text: "Quiz me on this chapter", skill: 'quiz-master' as SkillType },
    { text: "Show me my progress", skill: 'progress-motivator' as SkillType },
    { text: "Help me think through this", skill: 'socratic-tutor' as SkillType }
  ];

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 bg-gradient-to-r from-cyan-500 to-teal-500 text-white p-4 rounded-full shadow-2xl hover:scale-110 transition-all duration-300 group"
      >
        <div className="flex items-center gap-2">
          <Sparkles className="w-6 h-6" />
          <span className="font-semibold pr-2">Ask AI Assistant</span>
        </div>
      </button>
    );
  }

  return (
    <>
      {/* Skill Detection Toast */}
      {showSkillToast && detectedSkill && (
        <div className="fixed bottom-32 right-8 z-50 animate-fade-in-up">
          <div className="bg-gradient-to-r from-cyan-600 to-teal-600 text-white px-4 py-3 rounded-lg shadow-xl border border-white/20 flex items-center gap-3">
            {getSkillIconComponent(detectedSkill)}
            <div>
              <p className="text-sm font-semibold">Switched to {getSkillDisplayName(detectedSkill)}</p>
              <p className="text-xs opacity-90">AI adjusted to your request</p>
            </div>
          </div>
        </div>
      )}

      <div className="fixed bottom-6 right-6 z-50 w-96 h-[600px] bg-zinc-900 rounded-2xl shadow-2xl border border-cyan-700 flex flex-col overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-cyan-600 to-teal-600 p-4 flex items-center justify-between">
          <div className="flex items-center gap-2 text-white">
            <Sparkles className="w-5 h-5" />
            <div className="flex flex-col">
              <span className="font-semibold">AI Learning Assistant</span>
              <span className="text-xs opacity-90">{getSkillDisplayName(currentSkill)} mode</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <SkillModeSelector
              currentMode={currentSkill}
              onModeChange={setCurrentSkill}
              disabled={isLoading}
            />
            <button
              onClick={() => setIsOpen(false)}
              className="text-white hover:bg-white/20 rounded-lg p-1 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-zinc-800 text-zinc-100 border border-cyan-700'
              }`}
            >
              {/* Skill Badge for Assistant Messages */}
              {message.role === 'assistant' && message.skill && message.skill !== 'general' && (
                <div className="flex items-center gap-1 mb-2 pb-2 border-b border-cyan-700/50">
                  {getSkillIconComponent(message.skill)}
                  <span className="text-xs font-semibold text-zinc-400">
                    {getSkillDisplayName(message.skill)}
                  </span>
                </div>
              )}
              <p className="whitespace-pre-wrap text-sm">{message.content}</p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-zinc-800 rounded-2xl px-4 py-2 border border-cyan-700">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-cyan-500 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-cyan-500 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-cyan-500 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Suggestions */}
      {messages.length === 1 && (
        <div className="px-4 pb-2">
          <p className="text-zinc-400 text-xs mb-2">Try asking:</p>
          <div className="grid grid-cols-1 gap-2">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => {
                  setInput(suggestion.text);
                  setCurrentSkill(suggestion.skill);
                }}
                className="text-xs bg-zinc-800 hover:bg-zinc-700 text-zinc-300 px-3 py-2 rounded-lg border border-cyan-700 transition-colors text-left flex items-center gap-2"
              >
                {getSkillIconComponent(suggestion.skill)}
                <span>{suggestion.text}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-cyan-800 bg-zinc-900/50">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask me anything about the course..."
            className="flex-1 bg-zinc-800 text-white px-4 py-2 rounded-lg border border-cyan-700 focus:border-cyan-500 focus:outline-none transition-colors"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            className="bg-cyan-600 hover:bg-cyan-700 text-white p-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
    </>
  );
}