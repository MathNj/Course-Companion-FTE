'use client';

import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { MessageSquare, Send, X, Loader2, Sparkles, Mic, MicOff, Volume2, VolumeX, Languages, Trash2 } from 'lucide-react';
import { useStore } from '@/store/useStore';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  contentUrdu?: string;
  timestamp: Date;
}

interface AIChatProps {
  chapter: any;
  isOpen?: boolean;
  onClose?: () => void;
}

type Language = 'en' | 'ur';

// Storage keys
const STORAGE_KEYS = {
  MESSAGES: 'chat_messages',
  LANGUAGE: 'chat_language',
  SOUND_ENABLED: 'chat_sound_enabled',
};

export function AIChat({ chapter, isOpen = true, onClose }: AIChatProps) {
  const { user } = useStore();
  const [isClient, setIsClient] = useState(false);
  const [messages, setMessages] = useState<Message[]>(() => {
    // Load messages from localStorage on mount
    if (typeof window !== 'undefined') {
      try {
        const saved = localStorage.getItem(STORAGE_KEYS.MESSAGES);
        if (saved) {
          const parsed = JSON.parse(saved);
          // Convert timestamps back to Date objects
          return parsed.map((m: any) => ({
            ...m,
            timestamp: new Date(m.timestamp),
          }));
        }
      } catch (error) {
        console.error('Failed to load chat history:', error);
      }
    }
    // Default welcome message
    return [{
      role: 'assistant',
      content: `Hi! I'm your AI learning assistant for "${chapter.title}". I can help you understand concepts, explain examples, answer questions, and provide additional insights.

You can:
💬 Type your questions
🎤 Click the microphone to speak
🔊 Click the speaker to hear my responses
🌐 English or Urdu - اردو
💾 Your conversation is saved automatically

What would you like to learn about?`,
      contentUrdu: `سلام! میں آپ کا ایآئی لرننگ اسسٹنٹ ہوں "${chapter.title}" کے لیے۔ میں آپ کے سوالات کے جوابات دے سکتا ہوں، تصورات سمجھا سکتا ہوں، اور تعلیمی مدد کر سکتا ہوں۔

آپ:
💬 اپنے سوالات لکھیں
🎤 مائکروفون بٹن دبائیں بات کرنے کے لیے
🔊 اسپیکر بٹن دبائیں جوابات سننے کے لیے
🌐 انگلش یا اردو
💾 آپ کی بات چیت خود بخود محفوظ ہو جاتی ہے

آپ کیا سیکھنا چاہتے ہیں؟`,
      timestamp: new Date(),
    }];
  });

  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(() => {
    // Load sound preference from localStorage
    if (typeof window !== 'undefined') {
      try {
        const saved = localStorage.getItem(STORAGE_KEYS.SOUND_ENABLED);
        return saved !== 'false'; // Default to true if not set
      } catch {
        return true;
      }
    }
    return true;
  });
  const [language, setLanguage] = useState<Language>(() => {
    // Load language preference from localStorage
    if (typeof window !== 'undefined') {
      try {
        const saved = localStorage.getItem(STORAGE_KEYS.LANGUAGE);
        return (saved === 'ur' || saved === 'en') ? saved : 'en';
      } catch {
        return 'en';
      }
    }
    return 'en';
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Set isClient to true after mount
  useEffect(() => {
    setIsClient(true);
  }, []);

  const recognitionRef = useRef<any>(null);
  const speechRef = useRef<SpeechSynthesisUtterance | null>(null);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (typeof window !== 'undefined' && messages.length > 0) {
      try {
        localStorage.setItem(STORAGE_KEYS.MESSAGES, JSON.stringify(messages));
      } catch (error) {
        console.error('Failed to save chat history:', error);
      }
    }
  }, [messages]);

  // Save language preference
  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem(STORAGE_KEYS.LANGUAGE, language);
      } catch (error) {
        console.error('Failed to save language preference:', error);
      }
    }
  }, [language]);

  // Save sound preference
  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem(STORAGE_KEYS.SOUND_ENABLED, String(soundEnabled));
      } catch (error) {
        console.error('Failed to save sound preference:', error);
      }
    }
  }, [soundEnabled]);

  // Language configurations
  const languageConfig = {
    en: {
      code: 'en-US',
      name: 'English',
      flag: '🇺🇸',
      direction: 'ltr',
    },
    ur: {
      code: 'ur-PK',
      name: 'اردو',
      flag: '🇵🇰',
      direction: 'rtl',
    },
  };

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = languageConfig[language].code;

      recognitionRef.current.onresult = (event: any) => {
        const transcript = Array.from(event.results)
          .map((result: any) => result[0])
          .map((result) => result.transcript)
          .join('');

        setInput(transcript);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      if (speechRef.current) {
        window.speechSynthesis.cancel();
      }
    };
  }, [language]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const speak = (text: string, lang: Language = 'en') => {
    if (!soundEnabled || typeof window === 'undefined') return;

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = lang === 'ur' ? 0.9 : 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    utterance.lang = languageConfig[lang].code;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    // Try to get a good voice for the language
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(voice =>
      lang === 'ur'
        ? voice.lang.startsWith('ur')
        : (voice.name.includes('Google') || voice.name.includes('Natural') || voice.name.includes('Premium'))
    ) || voices.find(voice => voice.lang.startsWith(lang === 'ur' ? 'ur' : 'en')) || voices[0];

    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    speechRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  };

  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition is not supported in your browser. Please try Chrome or Edge.');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.lang = languageConfig[language].code;
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  // Handle mouse/touch events for hold-to-talk
  const startListening = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition is not supported in your browser. Please try Chrome or Edge.');
      return;
    }
    if (!isListening) {
      recognitionRef.current.lang = languageConfig[language].code;
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const stopListeningHandler = () => {
    if (isListening && recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  const stopSpeaking = () => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  };

  const toggleLanguage = () => {
    setLanguage(prev => prev === 'en' ? 'ur' : 'en');
  };

  const clearHistory = () => {
    if (confirm(language === 'ur'
      ? 'کیا آپ واقعی بات چیت کی تاریخ صرف کرنا چاہتے ہیں؟'
      : 'Are you sure you want to clear chat history?')) {
      setMessages([{
        role: 'assistant',
        content: language === 'ur'
          ? 'آپ کی بات چیت کی تاریخ صرف کر دی گئی ہے۔ نیا سوال پوچھیں!'
          : 'Chat history cleared. Feel free to ask a new question!',
        timestamp: new Date(),
      }]);
      localStorage.removeItem(STORAGE_KEYS.MESSAGES);
    }
  };

  const exportHistory = () => {
    const text = messages.map(m => {
      const time = m.timestamp.toLocaleString();
      const role = m.role === 'user' ? 'You' : 'AI';
      let content = `[${time}] ${role}:\n${m.content}\n`;
      if (m.contentUrdu) {
        content += `${m.contentUrdu}\n`;
      }
      return content;
    }).join('\n---\n\n');

    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-history-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const translateToUrdu = (text: string): string => {
    // Simple translation mappings for common phrases
    const translations: Record<string, string> = {
      'Great question!': 'بہت اچھا سوال!',
      'Let me explain': 'مجھے وضاحت کرنے دیں',
      'Here are': 'یہاں ہیں',
      'First': 'پہلے',
      'Second': 'دوسرے',
      'Third': 'تیسرے',
      'Finally': 'آخر میں',
      'Does this help?': 'کیا یہ مدد کرتا ہے؟',
      'Would you like': 'کیا آپ چاہیں گے',
      'For example': 'مثال کے طور پر',
      'In summary': 'خلاصہ یہ ہے کہ',
      'I hope this helps': 'امید ہے یہ مدد کرے گا',
      'Let me know': 'مجھے بتائیں',
      'Chat history cleared': 'بات چیت کی تاریخ صرف کر دی گئی',
    };

    let translated = text;
    Object.entries(translations).forEach(([en, ur]) => {
      translated = translated.replace(new RegExp(en, 'gi'), ur);
    });

    return translated;
  };

  const generateMockResponse = (question: string, chapter: any, lang: Language): { en: string; ur: string } => {
    const lowerQuestion = question.toLowerCase();

    const chapterContexts: Record<string, { en: string; ur: string }> = {
      'chapter-1': { en: 'Generative AI', ur: 'جنریٹو ای آئی' },
      'chapter-2': { en: 'Large Language Models', ur: 'بڑے لینگوئج ماڈلز' },
      'chapter-3': { en: 'Prompt Engineering', ur: 'پرمپٹ انجینئرنگ' },
      'chapter-4': { en: 'Advanced Prompting', ur: 'ایڈوانسڈ پرامپٹنگ' },
      'chapter-5': { en: 'AI Safety and Ethics', ur: 'ای آئی سیفٹی اینڈیتھکس' },
      'chapter-6': { en: 'AI Applications', ur: 'ای آئی ایپلی کیشنز' },
    };

    const context = chapterContexts[chapter.id] || { en: 'this topic', ur: 'اس موضوع' };

    if (lowerQuestion.includes('what is') || lowerQuestion.includes('define') || lowerQuestion.includes('explain') || lowerQuestion.includes('کیا ہے') || lowerQuestion.includes('وضاحت')) {
      return {
        en: `Great question! ${context.en} is a fascinating topic. Let me explain.

First, the core concept involves understanding the fundamental principles and how they work together.

Second, in practical applications, this is used to solve specific problems and improve outcomes in real-world scenarios.

Understanding ${context.en} helps you build a solid foundation for more advanced topics. Would you like me to go deeper into any specific aspect?`,
        ur: `بہت اچھا سوال! ${context.ur} ایک دلچسپ موضوع ہے۔ مجھے وضاحت کرنے دیں۔

پہلے، بنیادی تصور کو سمجھنا شامل ہے کہ بنیادی اصول کیا ہیں اور وہ ایک ساتھ کیسے کام کرتے ہیں۔

دوسرے، عملی استعمال میں، یہ حقیقی دنیا کے مناظر میں مخصوص مسائل کو حل کرنے اور نتائج بہتر بنانے کے لیے استعمال ہوتا ہے۔

${context.ur} کو سمجھنا آپ کے لیے زیادہ ترقی یافتہ موضوعات کی مضبوط بنیاد رکھنے میں مدد کرتا ہے۔ کیا آپ چاہیں گے کہ میں کسی مخصوص پہلو میں گہرا جاؤں؟`,
      };
    }

    if (lowerQuestion.includes('how') || lowerQuestion.includes('work') || lowerQuestion.includes('کیسے') || lowerQuestion.includes('کام')) {
      return {
        en: `Let me break down how this works.

The process has three main steps. First, the system receives information or data as input.

Then, through advanced algorithms, the information is analyzed and patterns are identified. This is where the magic happens.

Finally, based on the analysis, the system generates a response or result. The key innovation is in the processing step, where modern techniques enable sophisticated understanding.

Does this help clarify the process?`,
        ur: `مجھے وضاحت کرنے دیں کہ یہ کیسے کام کرتا ہے۔

اس عمل میں تین اہم مراحل ہیں۔ پہلے، سسٹم معلومات یا ڈیٹا انپٹ کے طور پر وصول کرتا ہے۔

پھر، اعلی درجے کے الگوریدم کے ذریعے، معلومات کا تجزیہ کیا جاتا ہے اور پیٹرنز کی شناخت کی جاتی ہے۔ یہیں جادو ہوتا ہے۔

آخر میں، تجزیے کی بنیاد پر، سسٹم جواب یا نتیجہ تیار کرتا ہے۔ اہم جدیدیت پروسیسنگ کے مرحلے میں ہے، جہاں جدید تکنیکیں پیچیدہ سمجھ کو ممکن بناتی ہیں۔

کیا یہ عمل کو واضح کرتا ہے؟`,
      };
    }

    if (lowerQuestion.includes('example') || lowerQuestion.includes('real world') || lowerQuestion.includes('مثال') || lowerQuestion.includes('دنیا')) {
      return {
        en: `Here are some real-world examples.

In content creation, this technology helps writers draft articles, create marketing copy, and generate ideas quickly.

In education, it provides personalized tutoring, explains complex concepts, and creates practice problems tailored to each student.

In software development, it assists with code generation, debugging, and documentation, making developers more productive.

These examples show how versatile and practical ${context.en} can be. Want more examples in a specific industry?`,
        ur: `یہاں کچھ حقیقی دنیا کے مثالات ہیں۔

مواد کی تخلیق میں، یہ ٹیکنالوجی مصنفین کو مضامین کا مسودہ تیار کرنے، مارکیٹنگ کاپی بنانے، اور تیزی سے خیالات پیدا کرنے میں مدد کرتی ہے۔

تعلیم میں، یہ ذاتی کوچنگ فراہم کرتی ہے، پیچیدہ تصورات کی وضاحت کرتی ہے، اور ہر طالب علم کے لیے مشق کے مسائل بناتی ہے۔

سافٹ ویئر ڈویلپمنٹ میں، یہ کوڈ جنریشن، ڈیبگنگ، اور دستاویزکاری میں مدد کرتی ہے، جس سے ڈویلپرز زیادہ پیدا کار بن جاتے ہیں۔

ان مثالات سے پتا چلتا ہے کہ ${context.ur} کتنا لچکدار اور عملی ہو سکتا ہے۔ کیا آپ کسی مخصوص صنعت میں مزید مثالات چاہتے ہیں؟`,
      };
    }

    // Default response
    return {
      en: `That's a great question about ${context.en}!

Here's the main idea. This concept focuses on understanding how modern AI systems can assist with learning, creating, and problem-solving.

The key takeaway is that the goal is to work alongside AI tools to enhance your capabilities, not replace them. Think of it as having a super-powered assistant.

For next steps, I'd recommend reviewing the chapter content again, and feel free to ask me more specific questions as you read through the material.

Is there anything specific about ${context.en} you'd like to explore further?`,
      ur: `یہ ${context.ur} کے بارے میں ایک بہت اچھا سوال ہے!

یہاں مرکزی خیال ہے۔ یہ تصور اس بات پر توجہ مرکوز کرتا ہے کہ جدید AI سسٹمز سیکھنے، تخلیق کرنے، اور مسائل حل کرنے میں کیسے مدد کر سکتے ہیں۔

اہم بات یہ ہے کہ مقصد AI ٹولز کے ساتھ کام کرنا ہے تاکہ آپ کی صلاحیتوں میں اضافہ ہو، نہ کہ انہیں تبدیل کرنا۔ اسے ایک سپر پاورڈ اسسٹنٹ کے طور پر سوچیں۔

اگلے مراحل کے لیے، میں سفارش کروں گا کہ آپ چپٹر کے مواد کو دوبارہ دیکھیں، اور جب آپ مواد کے ذریعے پڑھیں تو میرے پاس مزید مخصوص سوالات پوچھنے میں ہچکچاہت نہ کریں۔

کیا آپ ${context.ur} کے بارے میں کوئی خاص بات مزید探索 کرنا چاہیں گے؟`,
    };
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    const userInput = input;
    setInput('');
    setIsLoading(true);

    try {
      // Call the backend API for AI response
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
              content: `You are a helpful AI learning assistant for a course on "${chapter.title}". The user is communicating in ${language === 'ur' ? 'Urdu (اردو)' : 'English'}. Provide clear, educational responses in the same language. Be friendly and encouraging. Keep responses concise. Use conversational language that works well when read aloud by text-to-speech.`,
            },
            ...messages.slice(-10).map(m => ({  // Only include last 10 messages for context
              role: m.role,
              content: m.content,
            })),
            {
              role: 'user',
              content: userInput,
            }
          ],
          model: 'gpt-4o-mini',
          max_tokens: 500,
          temperature: 0.7,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const aiResponse = data.choices[0].message.content;
        const assistantMessage: Message = {
          role: 'assistant',
          content: aiResponse,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, assistantMessage]);

        // Speak the response
        speak(aiResponse, language);
      } else {
        throw new Error('API request failed');
      }
    } catch (error) {
      console.error('AI chat error:', error);
      // Fallback to mock response
      const mockResponse = generateMockResponse(userInput, chapter, language);
      const assistantMessage: Message = {
        role: 'assistant',
        content: mockResponse.en,
        contentUrdu: mockResponse.ur,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);

      // Speak the appropriate language
      speak(language === 'ur' ? mockResponse.ur : mockResponse.en, language);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  const currentLang = languageConfig[language];
  const messageCount = messages.length - 1; // Exclude initial welcome message

  return (
    <Card className="glow-box flex flex-col h-[600px]">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-cyan-500/10 border border-cyan-500/20">
              <Sparkles className="h-4 w-4 text-cyan-400" />
            </div>
            <div>
              <CardTitle className="text-lg">AI Assistant</CardTitle>
              <CardDescription className="text-xs">
                {messageCount > 0 ? `${messageCount} messages saved` : 'Type or speak your questions'} • English / اردو
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={exportHistory}
              className="h-8 w-8 p-0"
              title={language === 'ur' ? 'تاریخ محفوظ کریں' : 'Export chat history'}
            >
              <MessageSquare className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={clearHistory}
              className="h-8 w-8 p-0"
              title={language === 'ur' ? 'تاریخ صرف کریں' : 'Clear chat history'}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleLanguage}
              className="h-8 px-2 gap-1"
              title={`Switch to ${language === 'en' ? 'Urdu' : 'English'}`}
            >
              <Languages className="h-4 w-4" />
              <span className="text-sm">{currentLang.flag}</span>
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSoundEnabled(!soundEnabled)}
              className="h-8 w-8 p-0"
              title={soundEnabled ? 'Mute responses' : 'Unmute responses'}
            >
              {soundEnabled ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
            </Button>
            {onClose && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onClose}
                className="h-8 w-8 p-0"
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 space-y-4">
          <AnimatePresence initial={false}>
            {messages.map((message, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-lg px-4 py-2 ${
                    message.role === 'user'
                      ? 'bg-cyan-500/20 border border-cyan-500/20 text-white'
                      : 'bg-zinc-800 border border-cyan-700 text-zinc-200'
                  }`}
                  dir={message.role === 'assistant' ? 'auto' : 'ltr'}
                >
                  <div className="flex items-start gap-2">
                    <div className="flex-1 space-y-2">
                      {message.role === 'assistant' && message.contentUrdu && (
                        <p className="text-sm whitespace-pre-wrap text-cyan-400" dir="rtl">
                          {message.contentUrdu}
                        </p>
                      )}
                      <p className={`text-sm whitespace-pre-wrap ${message.contentUrdu ? 'border-t border-cyan-700 pt-2' : ''}`} dir={message.contentUrdu ? 'ltr' : 'auto'}>
                        {message.content}
                      </p>
                    </div>
                    {message.role === 'assistant' && soundEnabled && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => speak(message.content, language)}
                        className="h-6 w-6 p-0 flex-shrink-0 opacity-50 hover:opacity-100"
                        title="Read aloud"
                      >
                        <Volume2 className="h-3 w-3" />
                      </Button>
                    )}
                  </div>
                  <span className="text-xs text-zinc-500 mt-1 block">
                    {isClient ? message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                  </span>
                </div>
              </motion.div>
            ))}
            {isLoading && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex justify-start"
              >
                <div className="bg-zinc-800 border border-cyan-700 rounded-lg px-4 py-2">
                  <Loader2 className="h-4 w-4 animate-spin text-cyan-400" />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-cyan-800 p-4">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={language === 'ur' ? 'اپنا سوال لکھیں یا بولیں...' : 'Type or speak your question...'}
              disabled={isLoading}
              dir={language === 'ur' ? 'rtl' : 'ltr'}
              className={`flex-1 px-4 py-2 rounded-lg border bg-zinc-900 text-white placeholder:text-zinc-500 focus:outline-none focus:ring-1 text-sm ${
                isListening
                  ? 'border-red-500 ring-1 ring-red-500'
                  : 'border-cyan-700 focus:border-cyan-500 focus:ring-cyan-500'
              }`}
              style={{ fontFamily: language === 'ur' ? 'Noto Nastaliq Urdu, serif' : 'inherit' }}
            />
            <Button
              type="button"
              variant={isListening ? "secondary" : "outline"}
              size="sm"
              onClick={toggleListening}
              onMouseDown={startListening}
              onMouseUp={stopListeningHandler}
              onMouseLeave={stopListeningHandler}
              onTouchStart={startListening}
              onTouchEnd={stopListeningHandler}
              disabled={isLoading}
              className={`px-3 select-none ${isListening ? 'bg-red-500/20 border-red-500/50 text-red-400 hover:bg-red-500/30' : ''}`}
              title={isListening ? 'Release to stop' : 'Hold to record, click to toggle'}
            >
              {isListening ? <MicOff className="h-4 w-4 animate-pulse" /> : <Mic className="h-4 w-4" />}
            </Button>
            {isSpeaking && (
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={stopSpeaking}
                className="px-3"
                title="Stop speaking"
              >
                <VolumeX className="h-4 w-4" />
              </Button>
            )}
            <Button
              type="submit"
              disabled={isLoading || !input.trim()}
              size="sm"
              className="px-4"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
          <div className="flex items-center justify-between mt-2">
            <p className="text-xs text-zinc-500">
              {isListening ? (
                <span className="text-red-400 animate-pulse">🎤 Listening... (Release to stop)</span>
              ) : isSpeaking ? (
                <span className="text-cyan-400">🔊 Speaking... ({currentLang.name})</span>
              ) : (
                <>
                  {currentLang.flag} {currentLang.name} • 💾 Auto-saved
                </>
              )}
            </p>
            <p className="text-xs text-zinc-300">
              {soundEnabled ? '🔊 Sound on' : '🔇 Sound off'}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
