'use client';

import { Chapter } from '@/types';
import { Clock, BookOpen, Lock, ArrowRight } from 'lucide-react';
import Link from 'next/link';
import { formatTime } from '@/lib/utils';
import { StaggerChildren, StaggerItem, HoverCard } from '@/components/animations';

interface ChapterGridProps {
  chapters: Chapter[];
}

export function ChapterGrid({ chapters }: ChapterGridProps) {
  return (
    <StaggerChildren staggerDelay={0.1}>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {chapters.map((chapter, index) => (
          <StaggerItem key={chapter.id}>
            <ChapterCard chapter={chapter} index={index} />
          </StaggerItem>
        ))}
      </div>
    </StaggerChildren>
  );
}

function ChapterCard({ chapter, index }: { chapter: Chapter; index: number }) {
  const isLocked = chapter.access_tier === 'premium';

  return (
    <HoverCard className="interactive-card group card-dark overflow-hidden">
      {/* Chapter Number Badge */}
      <div className="absolute top-4 right-4 flex h-8 w-8 items-center justify-center rounded-full bg-zinc-800 border border-cyan-700 group-hover:border-cyan-500/30 transition-all duration-300">
        <span className="text-sm font-bold text-zinc-300">{index + 1}</span>
      </div>

      <div className="p-6">
        {/* Icon */}
        <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-cyan-500/10 border border-cyan-500/20 group-hover:bg-cyan-500/20 group-hover:scale-110 transition-all duration-300">
          <BookOpen className="h-6 w-6 text-cyan-400" />
        </div>

        {/* Title */}
        <h3 className="mb-2 text-xl font-bold text-white group-hover:text-cyan-400 transition-colors duration-300">
          {chapter.title}
        </h3>

        {/* Description */}
        <p className="mb-4 text-sm text-zinc-400 line-clamp-2">{chapter.description}</p>

        {/* Meta Info */}
        <div className="mb-4 flex items-center gap-4 text-sm text-zinc-500">
          <div className="flex items-center gap-1.5 group-hover:text-zinc-400 transition-colors duration-300">
            <Clock className="h-4 w-4" />
            <span>{chapter.estimated_time}</span>
          </div>
          <div className="flex items-center gap-1.5 group-hover:text-zinc-400 transition-colors duration-300">
            <BookOpen className="h-4 w-4" />
            <span>
              {chapter.sections && Array.isArray(chapter.sections) && chapter.sections.length > 0
                ? `${chapter.sections.length} sections`
                : chapter.content
                ? 'Full chapter'
                : 'No content'}
            </span>
          </div>
        </div>

        {/* Difficulty Badge */}
        <div className="mb-4">
          <span
            className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-all duration-300
              ${chapter.difficulty === 'beginner' ? 'bg-cyan-500/10 text-cyan-400 hover:bg-cyan-500/20' : ''}
              ${chapter.difficulty === 'intermediate' ? 'bg-blue-500/10 text-blue-400 hover:bg-blue-500/20' : ''}
              ${chapter.difficulty === 'advanced' ? 'bg-purple-500/10 text-purple-400 hover:bg-purple-500/20' : ''}
            `}
          >
            {chapter.difficulty}
          </span>
        </div>

        {/* Action Button */}
        <div className="flex items-center justify-between">
          {isLocked ? (
            <button
              disabled
              className="flex items-center gap-2 text-zinc-500 cursor-not-allowed"
            >
              <Lock className="h-4 w-4" />
              <span className="text-sm font-medium">Premium</span>
            </button>
          ) : (
            <Link href={`/chapters/${chapter.id}`} className="flex items-center gap-2 text-cyan-400 font-medium text-sm hover:text-cyan-300 transition-all duration-300 group-hover:gap-3">
              <span>Start Learning</span>
              <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform duration-300" />
            </Link>
          )}
        </div>
      </div>

      {/* Hover Glow Effect */}
      <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-cyan-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
    </HoverCard>
  );
}
