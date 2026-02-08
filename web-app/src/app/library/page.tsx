'use client';

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { useStore } from '@/store/useStore';
import { getChapters, getProgress } from '@/lib/api';
import { Chapter as ChapterType } from '@/types';
import { ChapterGrid } from '@/components/ChapterGrid';
import { Header } from '@/components/Header';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { BookOpen, Trophy, Target, TrendingUp, Filter, Lock, Crown, Zap } from 'lucide-react';
import { Button } from '@/components/ui/Button';

type FilterType = 'all' | 'free' | 'premium' | 'completed' | 'in-progress';

export default function LibraryPage() {
  const { user, progress } = useStore();
  const [filter, setFilter] = useState<FilterType>('all');
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const { data: chapters, isLoading: chaptersLoading } = useQuery({
    queryKey: ['chapters'],
    queryFn: async () => {
      try {
        return await getChapters();
      } catch (err) {
        console.error('Failed to fetch chapters:', err);
        return [];
      }
    },
  });

  // Filter chapters based on selected filter
  const filteredChapters = chapters?.filter((chapter) => {
    if (filter === 'all') return true;
    if (filter === 'free') return chapter.access_tier === 'free';
    if (filter === 'premium') return chapter.access_tier === 'premium';
    if (filter === 'completed') {
      return progress?.chapter_progress?.some(cp => cp.chapter_id === chapter.id && cp.completed_at);
    }
    if (filter === 'in-progress') {
      const cp = progress?.chapter_progress?.find(cp => cp.chapter_id === chapter.id);
      return cp && !cp.completed_at;
    }
    return true;
  }) || [];

  // Calculate stats
  const totalChapters = chapters?.length || 0;
  const completedChapters = progress?.chapter_progress?.filter(cp => cp.completed_at).length || 0;
  const inProgressCount = progress?.chapter_progress?.filter(cp => !cp.completed_at && cp.started_at).length || 0;
  const completionPercentage = totalChapters > 0 ? Math.round((completedChapters / totalChapters) * 100) : 0;

  // Find next recommended chapter
  const nextChapter = chapters?.find(ch => {
    const cp = progress?.chapter_progress?.find(p => p.chapter_id === ch.id);
    return !cp || (!cp.completed_at && (cp.started_at || ch.access_tier === 'free'));
  });

  const isPremium = user?.subscription_tier === 'premium' || user?.subscription_tier === 'pro' || user?.subscription_tier === 'team';

  return (
    <div className="min-h-screen bg-[#0B0C10]">
      <Header />

      {/* Hero Section */}
      <div className="border-b border-zinc-800 bg-[#0B0C10]/50 backdrop-blur">
        <div className="container px-4 py-12">
          <div className="max-w-4xl">
            {/* Breadcrumb */}
            <div className="flex items-center gap-2 text-sm text-zinc-400 mb-4">
              <Link href="/" className="hover:text-emerald-400 transition-colors">Home</Link>
              <span>/</span>
              <span className="text-white font-medium">Course Library</span>
            </div>

            {/* Title */}
            <div className="flex items-start justify-between mb-6">
              <div>
                <h1 className="text-4xl md:text-5xl font-bold text-white mb-3">
                  Generative AI Fundamentals
                </h1>
                <p className="text-lg text-zinc-400">
                  Master the foundations of Generative AI through interactive lessons and hands-on exercises
                </p>
              </div>
              <div className="hidden md:flex flex-col items-end gap-2">
                <div className="text-right">
                  <p className="text-sm text-zinc-400">Your Progress</p>
                  <p className="text-3xl font-bold text-emerald-400">{completionPercentage}%</p>
                </div>
              </div>
            </div>

            {/* Stats Bar */}
            <div className="flex flex-wrap items-center gap-6">
              <div className="flex items-center gap-2 text-sm">
                <BookOpen className="h-4 w-4 text-zinc-500" />
                <span className="text-zinc-400">{completedChapters} of {totalChapters} chapters</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Zap className="h-4 w-4 text-orange-400" />
                <span className="text-zinc-400">{inProgressCount} in progress</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Trophy className="h-4 w-4 text-yellow-400" />
                <span className="text-zinc-400">{progress?.current_streak || 0} day streak</span>
              </div>
              {!isPremium && (
                <Link href="/pricing" className="ml-auto">
                  <Button size="sm" className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700">
                    <Crown className="h-4 w-4 mr-2" />
                    Upgrade for Full Access
                  </Button>
                </Link>
              )}
            </div>

            {/* Continue Learning Button */}
            {nextChapter && (
              <div className="mt-6">
                <Link href={`/chapters/${nextChapter.id}`}>
                  <Button size="lg" className="bg-emerald-600 hover:bg-emerald-700">
                    <Target className="h-5 w-5 mr-2" />
                    Continue Learning: {nextChapter.title}
                    <TrendingUp className="h-5 w-5 ml-2" />
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container px-4 py-8">
        {/* Filter Bar */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-2">
            <Filter className="h-5 w-5 text-zinc-400" />
            <span className="text-sm font-medium text-zinc-400">Filter:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            <FilterButton active={filter === 'all'} onClick={() => setFilter('all')}>
              All ({totalChapters})
            </FilterButton>
            <FilterButton active={filter === 'free'} onClick={() => setFilter('free')}>
              Free
            </FilterButton>
            <FilterButton active={filter === 'premium'} onClick={() => setFilter('premium')}>
              Premium
            </FilterButton>
            <FilterButton active={filter === 'in-progress'} onClick={() => setFilter('in-progress')}>
              In Progress ({inProgressCount})
            </FilterButton>
            <FilterButton active={filter === 'completed'} onClick={() => setFilter('completed')}>
              Completed ({completedChapters})
            </FilterButton>
          </div>
        </div>

        {/* Chapters Grid */}
        {chaptersLoading ? (
          <div className="flex items-center justify-center py-20">
            <LoadingSpinner size="large" />
          </div>
        ) : filteredChapters.length === 0 ? (
          <div className="text-center py-20">
            <BookOpen className="h-16 w-16 text-zinc-700 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">No chapters found</h3>
            <p className="text-zinc-400">Try selecting a different filter</p>
          </div>
        ) : (
          <ChapterGridWithProgress chapters={filteredChapters} progress={progress} />
        )}
      </div>
    </div>
  );
}

function FilterButton({
  active,
  onClick,
  children
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
        active
          ? 'bg-emerald-600 text-white'
          : 'bg-zinc-800 text-zinc-400 hover:text-white hover:bg-zinc-700'
      }`}
    >
      {children}
    </button>
  );
}

function ChapterGridWithProgress({
  chapters,
  progress
}: {
  chapters: ChapterType[];
  progress?: any;
}) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {chapters.map((chapter, index) => {
        const chapterProgress = progress?.chapter_progress?.find(cp => cp.chapter_id === chapter.id);
        const isCompleted = !!chapterProgress?.completed_at;
        const isInProgress = !!chapterProgress?.started_at && !chapterProgress?.completed_at;
        const isLocked = chapter.access_tier === 'premium';

        return (
          <Link
            key={chapter.id}
            href={`/chapters/${chapter.id}`}
            className="group"
          >
            <div className={`card-dark p-6 h-full transition-all duration-300 hover:scale-[1.02] hover:shadow-xl hover:shadow-emerald-500/10 ${
              isCompleted ? 'border-emerald-500/30' : isInProgress ? 'border-blue-500/30' : ''
            }`}>
              {/* Chapter Number */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-500/10 border border-emerald-500/20 group-hover:bg-emerald-500/20 group-hover:scale-110 transition-all duration-300">
                  <span className="text-lg font-bold text-emerald-400">{index + 1}</span>
                </div>
                {isLocked && <Lock className="h-4 w-4 text-zinc-500" />}
              </div>

              {/* Title */}
              <h3 className="mb-2 text-lg font-bold text-white group-hover:text-emerald-400 transition-colors duration-300">
                {chapter.title}
              </h3>

              {/* Description */}
              <p className="mb-4 text-sm text-zinc-400 line-clamp-2">{chapter.description}</p>

              {/* Meta Info */}
              <div className="mb-4 flex items-center gap-3 text-xs text-zinc-500">
                <span className="capitalize">{chapter.difficulty}</span>
                <span>•</span>
                <span>{chapter.estimated_time}</span>
              </div>

              {/* Status Badge */}
              <div className="flex items-center justify-between">
                {isCompleted ? (
                  <span className="flex items-center gap-1.5 text-xs font-medium text-emerald-400">
                    <Trophy className="h-3.5 w-3.5" />
                    Completed
                  </span>
                ) : isInProgress ? (
                  <span className="flex items-center gap-1.5 text-xs font-medium text-blue-400">
                    <Zap className="h-3.5 w-3.5" />
                    In Progress
                  </span>
                ) : isLocked ? (
                  <span className="flex items-center gap-1.5 text-xs font-medium text-purple-400">
                    <Crown className="h-3.5 w-3.5" />
                    Premium
                  </span>
                ) : (
                  <span className="text-xs text-zinc-500">Not started</span>
                )}
                <ArrowRight className="h-4 w-4 text-zinc-500 group-hover:text-emerald-400 group-hover:translate-x-1 transition-all duration-300" />
              </div>
            </div>
          </Link>
        );
      })}
    </div>
  );
}

function ArrowRight({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
    </svg>
  );
}
