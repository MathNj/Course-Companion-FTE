'use client';

import { Chapter, Section } from '@/types';
import { Check, ChevronRight, Lock } from 'lucide-react';
import { cn, parseTitle } from '@/lib/utils';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import { getChapterProgress, markSectionComplete } from '@/lib/api';
import { useStore } from '@/store/useStore';

interface ChapterSidebarProps {
  chapter: Chapter;
  selectedSection: Section | null;
  onSectionSelect: (section: Section) => void;
}

export function ChapterSidebar({ chapter, selectedSection, onSectionSelect }: ChapterSidebarProps) {
  const [hoveredSection, setHoveredSection] = useState<string | null>(null);
  const [completedSections, setCompletedSections] = useState<Record<string, string>>({});
  const { user } = useStore();

  // Fetch chapter progress to get completed sections
  useEffect(() => {
    if (user) {
      getChapterProgress(chapter.id)
        .then((progress) => {
          if (progress.completed_sections) {
            setCompletedSections(progress.completed_sections);
          }
        })
        .catch(() => {
          // Silently fail - user might not have progress yet
        });
    }
  }, [chapter.id, user]);

  const handleSectionSelect = (section: Section) => {
    onSectionSelect(section);

    // Mark section as complete if user is logged in
    if (user && !completedSections[section.id]) {
      markSectionComplete(chapter.id, section.id, chapter.id).then(() => {
        setCompletedSections((prev) => ({
          ...prev,
          [section.id]: new Date().toISOString(),
        }));
      }).catch(() => {
        // Silently fail - section will be marked on next load
      });
    }
  };

  // Parse title for multi-line display
  const { main: titleMain, subtitle: titleSubtitle } = parseTitle(chapter.title);

  // Check if chapter has structured sections or markdown content
  const hasStructuredSections = chapter.sections && Array.isArray(chapter.sections) && chapter.sections.length > 0;
  const hasMarkdownContent = chapter.content && typeof chapter.content === 'string';

  return (
    <div className="card-dark p-4">
      {/* Chapter Info */}
      <div className="mb-4 pb-4 border-b border-cyan-700/50">
        <h3 className="font-bold text-white mb-1">
          {titleMain}
          {titleSubtitle && (
            <>
              <br />
              <span className="text-base">{titleSubtitle}</span>
            </>
          )}
        </h3>
        {hasStructuredSections ? (
          <p className="text-xs text-zinc-500">{chapter.sections.length} sections</p>
        ) : hasMarkdownContent ? (
          <p className="text-xs text-zinc-500">Full chapter content</p>
        ) : (
          <p className="text-xs text-zinc-500">No content available</p>
        )}
      </div>

      {/* Section List - Only show if structured sections exist */}
      {hasStructuredSections ? (
        <nav className="space-y-1">
          {chapter.sections.map((section, index) => {
            const isSelected = selectedSection?.id === section.id;
            const isHovered = hoveredSection === section.id;
            const isCompleted = !!completedSections[section.id];

            return (
              <button
                key={section.id}
                onClick={() => handleSectionSelect(section)}
                onMouseEnter={() => setHoveredSection(section.id)}
                onMouseLeave={() => setHoveredSection(null)}
                className={cn(
                  'w-full flex items-start gap-3 px-3 py-2.5 rounded-lg text-left transition-all duration-300',
                  isSelected
                    ? 'bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 scale-105'
                    : 'text-zinc-400 hover:bg-zinc-800 hover:text-white hover:scale-[1.02]'
                )}
              >
                <div className="flex-shrink-0 mt-0.5">
                  {isCompleted ? (
                    <Check className="h-4 w-4 text-cyan-400" />
                  ) : (
                    <ChevronRight
                      className={cn(
                        'h-4 w-4 transition-all duration-300',
                        isSelected || isHovered ? 'text-cyan-400 translate-x-1' : 'text-zinc-400'
                      )}
                    />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="text-xs font-medium text-zinc-500">{index + 1}</span>
                    {isSelected && (
                      <span className="text-xs px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-400 animate-pulse">
                        Reading
                      </span>
                    )}
                  </div>
                  <p className="text-sm font-medium line-clamp-2">{section.title}</p>
                </div>
              </button>
            );
          })}
        </nav>
      ) : hasMarkdownContent ? (
        <div className="text-center py-6">
          <p className="text-sm text-zinc-400 mb-2">This chapter contains markdown content</p>
          <p className="text-xs text-zinc-500">Scroll down to read the full chapter</p>
        </div>
      ) : (
        <div className="text-center py-6">
          <p className="text-sm text-zinc-500">No sections available</p>
        </div>
      )}

      {/* Quiz Link */}
      <div className="mt-4 pt-4 border-t border-cyan-700/50">
        <Link
          href={`/chapters/${chapter.id}/quiz`}
          className="flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm font-medium text-zinc-300 hover:bg-zinc-800 hover:text-cyan-400 hover:scale-105 transition-all duration-300 group"
        >
          <div className="h-8 w-8 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
            <Check className="h-4 w-4 text-cyan-400" />
          </div>
          <div>
            <p className="group-hover:translate-x-1 transition-transform duration-300">Take Quiz</p>
            <p className="text-xs text-zinc-500">Test your knowledge</p>
          </div>
        </Link>
      </div>
    </div>
  );
}
