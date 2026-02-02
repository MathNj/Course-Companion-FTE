'use client';

import { Chapter, Section } from '@/types';
import { Clock, ArrowLeft, ArrowRight, CheckCircle } from 'lucide-react';
import { formatTime } from '@/lib/utils';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import { Button } from './ui/Button';
import Link from 'next/link';
import { FadeIn } from '@/components/animations';
import { BookmarkButton } from '@/components/bookmarks';
import { NoteButton } from '@/components/notes';
import { ChapterExportButton } from '@/components/PDFExportButton';

interface ChapterContentProps {
  chapter: Chapter;
  section: Section;
  onNext: () => void;
  onPrevious: () => void;
  hasQuiz: boolean;
}

export function ChapterContent({ chapter, section, onNext, onPrevious, hasQuiz }: ChapterContentProps) {
  const currentSectionIndex = chapter.sections.findIndex(s => s.id === section.id);
  const isFirstSection = currentSectionIndex === 0;
  const isLastSection = currentSectionIndex === chapter.sections.length - 1;

  return (
    <FadeIn>
      <div className="space-y-8">
        {/* Section Header */}
        <div className="space-y-4">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-sm text-zinc-500">
              <span className="animate-fade-in-up">Section {currentSectionIndex + 1} of {chapter.sections.length}</span>
              <span>•</span>
              <div className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                <span>{formatTime(Math.round(chapter.estimated_time_minutes / chapter.sections.length))}</span>
              </div>
            </div>

            {/* Bookmark, Note, and Export Buttons */}
            <div className="flex items-center gap-2">
              <BookmarkButton
                chapterId={chapter.id}
                sectionId={section.id}
                title={`${chapter.title} - ${section.title}`}
              />
              <NoteButton
                chapterId={chapter.id}
                sectionId={section.id}
              />
              <ChapterExportButton chapter={{
                title: chapter.title,
                content: section.content,
                sections: undefined
              }} />
            </div>
          </div>

          <h1 className="text-3xl font-bold text-white animate-fade-in-up delay-100">{section.title}</h1>

          {/* Learning Objectives */}
          {currentSectionIndex === 0 && chapter.learning_objectives.length > 0 && (
            <div className="p-4 rounded-lg bg-emerald-500/5 border border-emerald-500/10 animate-fade-in-up delay-200">
              <h3 className="text-sm font-semibold text-emerald-400 mb-2">Learning Objectives</h3>
              <ul className="space-y-1">
                {chapter.learning_objectives.map((objective, index) => (
                  <li key={index} className="text-sm text-zinc-300 flex items-start gap-2 animate-fade-in-up" style={{ animationDelay: `${200 + (index * 50)}ms` }}>
                    <CheckCircle className="h-4 w-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                    <span>{objective}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Markdown Content */}
        <div className="prose prose-invert prose-zinc max-w-none animate-fade-in-up delay-300">
          {section.content ? (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeHighlight]}
              components={{
                // Custom component wrappers to handle edge cases
                p: ({ children }) => <p className="mb-4 text-zinc-300">{children}</p>,
                h1: ({ children }) => <h1 className="text-2xl font-bold text-white mt-8 mb-4">{children}</h1>,
                h2: ({ children }) => <h2 className="text-xl font-bold text-white mt-6 mb-3">{children}</h2>,
                h3: ({ children }) => <h3 className="text-lg font-semibold text-white mt-4 mb-2">{children}</h3>,
                ul: ({ children }) => <ul className="list-disc list-inside mb-4 space-y-1 text-zinc-300">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal list-inside mb-4 space-y-1 text-zinc-300">{children}</ol>,
                li: ({ children }) => <li className="text-zinc-300">{children}</li>,
                code: ({ className, children, ...props }) => {
                  const match = /language-(\w+)/.exec(className || '');
                  return match ? (
                    <code className={className} {...props}>{children}</code>
                  ) : (
                    <code className="bg-zinc-800 text-emerald-400 px-1.5 py-0.5 rounded text-sm" {...props}>
                      {children}
                    </code>
                  );
                },
                pre: ({ children }) => (
                  <pre className="bg-zinc-950 border border-zinc-800 rounded-lg p-4 overflow-x-auto">
                    {children}
                  </pre>
                ),
                blockquote: ({ children }) => (
                  <blockquote className="border-l-4 border-emerald-500 pl-4 italic text-zinc-400 my-4">
                    {children}
                  </blockquote>
                ),
                a: ({ href, children }) => (
                  <a href={href} className="text-emerald-400 hover:text-emerald-300 underline" target="_blank" rel="noopener noreferrer">
                    {children}
                  </a>
                ),
                strong: ({ children }) => <strong className="font-bold text-white">{children}</strong>,
                em: ({ children }) => <em className="italic text-zinc-300">{children}</em>,
              }}
            >
              {section.content}
            </ReactMarkdown>
          ) : (
            <p className="text-zinc-400">No content available for this section.</p>
          )}
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between pt-6 border-t border-zinc-800 animate-fade-in-up delay-400">
          <Button
            variant="secondary"
            onClick={onPrevious}
            disabled={isFirstSection}
            className="gap-2 hover:scale-105 active:scale-95 transition-all duration-300"
          >
            <ArrowLeft className="h-4 w-4" />
            Previous
          </Button>

          {isLastSection && hasQuiz ? (
            <Link href={`/chapters/${chapter.id}/quiz`}>
              <Button className="gap-2 hover:scale-105 active:scale-95 transition-all duration-300">
                Take Quiz
                <CheckCircle className="h-4 w-4" />
              </Button>
            </Link>
          ) : (
            <Button onClick={onNext} disabled={isLastSection} className="gap-2 hover:scale-105 active:scale-95 transition-all duration-300">
              Next Section
              <ArrowRight className="h-4 w-4" />
            </Button>
          )}
        </div>

        {/* Progress Bar */}
        <div className="space-y-2 animate-fade-in-up delay-500">
          <div className="flex justify-between text-sm text-zinc-400">
            <span>Progress</span>
            <span>{Math.round(((currentSectionIndex + 1) / chapter.sections.length) * 100)}%</span>
          </div>
          <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 progress-bar-animated transition-all duration-700 ease-out"
              style={{ width: `${((currentSectionIndex + 1) / chapter.sections.length) * 100}%` }}
            />
          </div>
        </div>
      </div>
    </FadeIn>
  );
}
