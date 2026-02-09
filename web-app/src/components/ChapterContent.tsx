'use client';

import { Chapter, Section } from '@/types';
import { Clock, ArrowLeft, ArrowRight, CheckCircle } from 'lucide-react';
import { formatTime, aggressiveCleanMarkdown, cleanTitle } from '@/lib/utils';
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
  // Safely access sections with fallback
  const sections = chapter.sections || [];
  const currentSectionIndex = sections.findIndex(s => s.id === section.id);
  const isFirstSection = currentSectionIndex === 0;
  const isLastSection = sections.length > 0 ? currentSectionIndex === sections.length - 1 : true;

  return (
    <FadeIn>
      <div className="space-y-8">
        {/* Section Header */}
        <div className="space-y-4">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-sm text-zinc-500">
              <span className="animate-fade-in-up">Section {currentSectionIndex + 1} of {sections.length}</span>
              <span>•</span>
              <div className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                <span>{formatTime(Math.round((parseInt(chapter.estimated_time || '45') || 45) / Math.max(sections.length, 1)))}</span>
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

          <h1 className="text-5xl font-bold text-white animate-fade-in-up delay-100 leading-tight tracking-tight">
            {cleanTitle(section.title)}
          </h1>

          {/* Learning Objectives */}
          {currentSectionIndex === 0 && chapter.learning_objectives && chapter.learning_objectives.length > 0 && (
            <div className="p-4 rounded-lg bg-cyan-500/5 border border-cyan-500/10 animate-fade-in-up delay-200">
              <h3 className="text-sm font-semibold text-cyan-400 mb-2">Learning Objectives</h3>
              <ul className="space-y-1">
                {chapter.learning_objectives.map((objective, index) => (
                  <li key={index} className="text-sm text-zinc-300 flex items-start gap-2 animate-fade-in-up" style={{ animationDelay: `${200 + (index * 50)}ms` }}>
                    <CheckCircle className="h-4 w-4 text-cyan-400 flex-shrink-0 mt-0.5" />
                    <span>{objective}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Markdown Content - Book-like typography */}
        <div className="prose prose-invert prose-lg prose-zinc max-w-none animate-fade-in-up delay-300 chapter-content">
          {section.content ? (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeHighlight]}
              skipHtml={false}
              unwrapDisallowed={false}
              components={{
                // Enhanced typography for book-like reading experience
                p: ({ children }) => (
                  <p className="mb-6 leading-relaxed text-zinc-300 text-base">
                    {children}
                  </p>
                ),
                h1: ({ children }) => (
                  <h1 className="text-4xl font-bold text-white mt-12 mb-6 leading-tight tracking-tight">
                    {children}
                  </h1>
                ),
                h2: ({ children }) => (
                  <h2 className="text-3xl font-bold text-white mt-10 mb-5 leading-tight tracking-tight">
                    {children}
                  </h2>
                ),
                h3: ({ children }) => (
                  <h3 className="text-2xl font-semibold text-white mt-8 mb-4 leading-snug">
                    {children}
                  </h3>
                ),
                h4: ({ children }) => (
                  <h4 className="text-xl font-semibold text-zinc-100 mt-6 mb-3">
                    {children}
                  </h4>
                ),
                h5: ({ children }) => (
                  <h5 className="text-lg font-semibold text-zinc-200 mt-5 mb-2">
                    {children}
                  </h5>
                ),
                h6: ({ children }) => (
                  <h6 className="text-base font-semibold text-zinc-300 mt-4 mb-2">
                    {children}
                  </h6>
                ),
                ul: ({ children }) => (
                  <ul className="list-disc list-outside ml-6 mb-6 space-y-2 text-zinc-300 text-base">
                    {children}
                  </ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal list-outside ml-6 mb-6 space-y-2 text-zinc-300 text-base">
                    {children}
                  </ol>
                ),
                li: ({ children }) => (
                  <li className="leading-relaxed text-zinc-300 text-base">
                    {children}
                  </li>
                ),
                code: ({ className, children, ...props }) => {
                  const match = /language-(\w+)/.exec(className || '');
                  return match ? (
                    <code className={className} {...props}>{children}</code>
                  ) : (
                    <code
                      className="bg-zinc-800/50 text-cyan-400 px-2 py-1 rounded-md text-sm font-mono border border-cyan-700/50"
                      {...props}
                    >
                      {children}
                    </code>
                  );
                },
                pre: ({ children }) => (
                  <pre className="bg-zinc-950 border border-cyan-800 rounded-lg p-5 overflow-x-auto my-6 shadow-lg text-sm">
                    {children}
                  </pre>
                ),
                blockquote: ({ children }) => (
                  <blockquote className="border-l-4 border-cyan-500/50 bg-zinc-900/30 pl-6 pr-4 py-4 rounded-r-lg my-6 text-zinc-300 italic leading-relaxed text-base">
                    {children}
                  </blockquote>
                ),
                a: ({ href, children }) => (
                  <a
                    href={href}
                    className="text-cyan-400 hover:text-cyan-300 underline underline-offset-2 decoration-cyan-400/30 hover:decoration-cyan-300 transition-colors"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {children}
                  </a>
                ),
                strong: ({ children }) => (
                  <strong className="font-bold text-white">
                    {children}
                  </strong>
                ),
                em: ({ children }) => (
                  <em className="italic text-zinc-200">
                    {children}
                  </em>
                ),
                hr: () => (
                  <hr className="my-8 border-cyan-700/50" />
                ),
                table: ({ children }) => (
                  <div className="my-6 overflow-x-auto">
                    <table className="min-w-full divide-y divide-zinc-700 text-sm">
                      {children}
                    </table>
                  </div>
                ),
                thead: ({ children }) => (
                  <thead className="bg-zinc-800/50">
                    {children}
                  </thead>
                ),
                tbody: ({ children }) => (
                  <tbody className="divide-y divide-zinc-800">
                    {children}
                  </tbody>
                ),
                tr: ({ children }) => (
                  <tr className="hover:bg-zinc-800/20 transition-colors">
                    {children}
                  </tr>
                ),
                th: ({ children }) => (
                  <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-300 uppercase tracking-wider">
                    {children}
                  </th>
                ),
                td: ({ children }) => (
                  <td className="px-4 py-3 text-sm text-zinc-300">
                    {children}
                  </td>
                ),
              }}
            >
              {aggressiveCleanMarkdown(section.content)}
            </ReactMarkdown>
          ) : (
            <p className="text-zinc-400 italic">No content available for this section.</p>
          )}
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between pt-6 border-t border-cyan-800 animate-fade-in-up delay-400">
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
        {sections.length > 0 && (
          <div className="space-y-2 animate-fade-in-up delay-500">
            <div className="flex justify-between text-sm text-zinc-400">
              <span>Progress</span>
              <span>{Math.round(((currentSectionIndex + 1) / sections.length) * 100)}%</span>
            </div>
            <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-cyan-500 to-cyan-400 progress-bar-animated transition-all duration-700 ease-out"
                style={{ width: `${((currentSectionIndex + 1) / sections.length) * 100}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </FadeIn>
  );
}
