'use client';

import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useParams, useRouter } from 'next/navigation';
import { useStore } from '@/store/useStore';
import { getChapter, getQuiz, recordActivity } from '@/lib/api';
import { cleanTitle, parseTitle } from '@/lib/utils';
import { Chapter as ChapterType, Quiz as QuizType, Section } from '@/types';
import { Header } from '@/components/Header';
import { ChapterSidebar } from '@/components/ChapterSidebar';
import { ChapterContent } from '@/components/ChapterContent';
import { AIAssistant } from '@/components/AIAssistant';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { Lock } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';

export default function ChapterPage() {
  const params = useParams();
  const router = useRouter();
  const { currentChapter, setCurrentChapter, user, setShowUpgradeModal } = useStore();
  const [selectedSection, setSelectedSection] = useState<Section | null>(null);

  // Function to unescape markdown content
  const unescapeMarkdown = (text: string) => {
    return text
      .replace(/\\\*/g, '*')      // \*\* → ** (bold)
      .replace(/\\#/g, '#')        // \# → # (headings)
      .replace(/\\-/g, '-')        // \- → - (dashes)
      .replace(/\\_/g, '_')        // \_ → _ (italics)
      .replace(/\\`/g, '`')        // \` → ` (code)
      .replace(/\\\./g, '.');      // \. → . (escapes)
  };

  const chapterId = params.id as string;

  const { data: chapter, isLoading } = useQuery({
    queryKey: ['chapter', chapterId],
    queryFn: () => getChapter(chapterId),
  });

  const { data: quiz } = useQuery({
    queryKey: ['quiz', chapterId],
    queryFn: () => getQuiz(chapterId),
    enabled: !!chapter,
  });

  useEffect(() => {
    if (chapter) {
      setCurrentChapter(chapter);
      // Only set selected section if structured sections exist
      if (chapter.sections && chapter.sections.length > 0) {
        setSelectedSection(chapter.sections[0] || null);
      }
      // Try to record activity (don't fail if it errors)
      recordActivity(chapter.id).catch(() => {});
    }
  }, [chapter, setCurrentChapter]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0B0C10]">
        <Header />
        <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
          <LoadingSpinner size="large" />
        </div>
      </div>
    );
  }

  if (!chapter) {
    return (
      <div className="min-h-screen bg-[#0B0C10]">
        <Header />
        <div className="container mx-auto px-4 py-16 text-center">
          <h1 className="text-2xl font-bold text-white mb-4">Chapter Not Found</h1>
          <button onClick={() => router.push('/')} className="btn-primary">
            Go Home
          </button>
        </div>
      </div>
    );
  }

  // Check if premium content and user is free tier
  if (chapter.access_tier === 'premium' && user?.subscription_tier !== 'premium') {
    return (
      <div className="min-h-screen bg-[#0B0C10]">
        <Header />
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-2xl mx-auto text-center">
            <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-zinc-800 border border-zinc-700">
              <Lock className="h-10 w-10 text-zinc-500" />
            </div>
            <h1 className="text-3xl font-bold text-white mb-4">Premium Content</h1>
            <p className="text-zinc-400 mb-8">
              This chapter is part of our premium curriculum. Choose a plan to access all 6 chapters and unlock
              advanced features like AI-powered assessments and adaptive learning paths.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button onClick={() => setShowUpgradeModal(true)} className="btn-primary">View Plans</button>
              <button onClick={() => router.push('/')} className="btn-secondary">
                Back to Free Chapters
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0B0C10]">
      <Header />

      {/* Breadcrumb */}
      <div className="border-b border-zinc-800 bg-[#0B0C10]/50 backdrop-blur">
        <div className="container px-4 py-3">
          <div className="flex items-center gap-2 text-sm text-zinc-400">
            <button onClick={() => router.push('/')} className="hover:text-emerald-400 transition-colors">
              Home
            </button>
            <span>/</span>
            <button onClick={() => router.push('/library')} className="hover:text-emerald-400 transition-colors">
              Chapters
            </button>
            <span>/</span>
            <span className="text-white font-medium">{cleanTitle(chapter.title)}</span>
          </div>
        </div>
      </div>

      {/* Main Content - 3 Column Layout */}
      <div className="container">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Sidebar - Chapter Navigation */}
          <div className="lg:col-span-3 xl:col-span-2">
            <div className="sticky top-20">
              <ChapterSidebar
                chapter={chapter}
                selectedSection={selectedSection}
                onSectionSelect={setSelectedSection}
              />
            </div>
          </div>

          {/* Center - Main Content Area */}
          <div className="lg:col-span-6 xl:col-span-7">
            <div className="py-8">
              {selectedSection && chapter.sections && chapter.sections.length > 0 ? (
                // Structured sections - render section by section
                <ChapterContent
                  chapter={chapter}
                  section={selectedSection}
                  onNext={() => {
                    const currentIndex = chapter.sections!.findIndex(s => s.id === selectedSection.id);
                    if (currentIndex < chapter.sections!.length - 1) {
                      setSelectedSection(chapter.sections![currentIndex + 1]);
                    }
                  }}
                  onPrevious={() => {
                    const currentIndex = chapter.sections!.findIndex(s => s.id === selectedSection.id);
                    if (currentIndex > 0) {
                      setSelectedSection(chapter.sections![currentIndex - 1]);
                    }
                  }}
                  hasQuiz={!!quiz}
                />
              ) : chapter.content ? (
                // Markdown content - render full chapter with beautiful typography
                <div className="max-w-none">
                  <div className="card-dark p-8 md:p-12">
                    {/* Chapter Title */}
                    <div className="mb-8 pb-6 border-b border-zinc-800">
                      {(() => {
                        const { main: titleMain, subtitle: titleSubtitle } = parseTitle(chapter.title);
                        return (
                          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight">
                            {titleMain}
                            {titleSubtitle && (
                              <>
                                <br />
                                <span className="text-3xl md:text-4xl">{titleSubtitle}</span>
                              </>
                            )}
                          </h1>
                        );
                      })()}
                      <div className="flex flex-wrap items-center gap-4 text-sm text-zinc-400">
                        <span className="capitalize">{chapter.difficulty}</span>
                        <span>•</span>
                        <span>{chapter.estimated_time}</span>
                        <span>•</span>
                        <span className="text-emerald-400">{chapter.access_tier} tier</span>
                      </div>
                    </div>

                    {/* Markdown Content with Book-Like Typography */}
                    <div className="prose prose-lg prose-invert prose-emerald max-w-none">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        rehypePlugins={[rehypeHighlight]}
                        components={{
                          // Headings
                          h1: ({ children }) => (
                            <h1 className="text-3xl font-bold text-white mt-12 mb-6 leading-tight">
                              {children}
                            </h1>
                          ),
                          h2: ({ children }) => (
                            <h2 className="text-2xl font-bold text-white mt-10 mb-5 leading-tight">
                              {children}
                            </h2>
                          ),
                          h3: ({ children }) => (
                            <h3 className="text-xl font-semibold text-white mt-8 mb-4 leading-tight">
                              {children}
                            </h3>
                          ),
                          h4: ({ children }) => (
                            <h4 className="text-lg font-semibold text-zinc-200 mt-6 mb-3">
                              {children}
                            </h4>
                          ),

                          // Paragraphs with book-like line height and spacing
                          p: ({ children }) => (
                            <p className="text-base md:text-lg text-zinc-300 leading-relaxed mb-6">
                              {children}
                            </p>
                          ),

                          // Lists
                          ul: ({ children }) => (
                            <ul className="space-y-3 mb-6 ml-6 list-disc text-zinc-300">
                              {children}
                            </ul>
                          ),
                          ol: ({ children }) => (
                            <ol className="space-y-3 mb-6 ml-6 list-decimal text-zinc-300">
                              {children}
                            </ol>
                          ),
                          li: ({ children }) => (
                            <li className="leading-relaxed text-base md:text-lg">
                              {children}
                            </li>
                          ),

                          // Code blocks with syntax highlighting
                          code: ({ className, children, ...props }) => {
                            const match = /language-(\w+)/.exec(className || '');
                            return match ? (
                              <code className={className} {...props}>
                                {children}
                              </code>
                            ) : (
                              <code className="bg-zinc-800 text-emerald-400 px-2 py-1 rounded text-sm font-mono" {...props}>
                                {children}
                              </code>
                            );
                          },
                          pre: ({ children }) => (
                            <pre className="bg-zinc-950 border border-zinc-800 rounded-lg p-6 mb-6 overflow-x-auto">
                              {children}
                            </pre>
                          ),

                          // Blockquotes
                          blockquote: ({ children }) => (
                            <blockquote className="border-l-4 border-emerald-500 pl-6 py-2 my-6 italic text-zinc-400 bg-zinc-900/50 rounded-r">
                              {children}
                            </blockquote>
                          ),

                          // Links
                          a: ({ href, children }) => (
                            <a
                              href={href}
                              className="text-emerald-400 hover:text-emerald-300 underline transition-colors"
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              {children}
                            </a>
                          ),

                          // Strong and emphasis
                          strong: ({ children }) => (
                            <strong className="font-bold text-white">{children}</strong>
                          ),
                          em: ({ children }) => (
                            <em className="italic text-zinc-200">{children}</em>
                          ),

                          // Horizontal rule
                          hr: () => <hr className="my-10 border-zinc-800" />,

                          // Tables
                          table: ({ children }) => (
                            <div className="overflow-x-auto mb-6">
                              <table className="min-w-full border border-zinc-800 rounded-lg overflow-hidden">
                                {children}
                              </table>
                            </div>
                          ),
                          thead: ({ children }) => (
                            <thead className="bg-zinc-900">{children}</thead>
                          ),
                          tbody: ({ children }) => (
                            <tbody className="divide-y divide-zinc-800">{children}</tbody>
                          ),
                          tr: ({ children }) => <tr>{children}</tr>,
                          th: ({ children }) => (
                            <th className="px-6 py-3 text-left text-sm font-semibold text-white">
                              {children}
                            </th>
                          ),
                          td: ({ children }) => (
                            <td className="px-6 py-4 text-sm text-zinc-300">{children}</td>
                          ),
                        }}
                      >
                        {unescapeMarkdown(chapter.content)}
                      </ReactMarkdown>
                    </div>
                  </div>
                </div>
              ) : (
                // No content
                <div className="text-center py-12">
                  <p className="text-zinc-400">No content available for this chapter.</p>
                </div>
              )}
            </div>
          </div>

          {/* Right - AI Assistant */}
          <div className="lg:col-span-3 xl:col-span-3">
            <div className="sticky top-20">
              <AIAssistant chapter={chapter} quiz={quiz} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
