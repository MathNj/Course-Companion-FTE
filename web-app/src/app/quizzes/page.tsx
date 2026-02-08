'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { useStore } from '@/store/useStore';
import { getProgress, getQuiz } from '@/lib/api';
import { Header } from '@/components/Header';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { Button } from '@/components/ui/Button';
import {
  Clock,
  Target,
  Trophy,
  Lock,
  Play,
  RotateCcw,
  CheckCircle,
  BookOpen,
  Filter,
  Flame,
  TrendingUp,
} from 'lucide-react';
import { useState } from 'react';

const CHAPTERS = [
  { id: 'chapter-1', number: 1, title: 'Introduction to Generative AI', difficulty: 'Beginner', timeLimit: 15, questions: 10 },
  { id: 'chapter-2', number: 2, title: 'How LLMs Work', difficulty: 'Beginner', timeLimit: 20, questions: 12 },
  { id: 'chapter-3', number: 3, title: 'Prompt Engineering Basics', difficulty: 'Intermediate', timeLimit: 20, questions: 15 },
  { id: 'chapter-4', number: 4, title: 'Advanced Prompting Techniques', difficulty: 'Intermediate', timeLimit: 25, questions: 15 },
  { id: 'chapter-5', number: 5, title: 'AI Safety and Ethics', difficulty: 'Advanced', timeLimit: 20, questions: 12 },
  { id: 'chapter-6', number: 6, title: 'Real-World Applications', difficulty: 'Advanced', timeLimit: 25, questions: 15 },
];

type FilterType = 'all' | 'not-started' | 'in-progress' | 'passed';

export default function QuizzesPage() {
  const { user } = useStore();
  const [filter, setFilter] = useState<FilterType>('all');

  const { data: progress, isLoading: loadingProgress } = useQuery({
    queryKey: ['progress'],
    queryFn: getProgress,
    enabled: !!user,
  });

  // Fetch quiz data for each chapter to get latest scores
  const { data: quizData, isLoading: loadingQuizzes } = useQuery({
    queryKey: ['all-quiz-scores'],
    queryFn: async () => {
      const scores: Record<string, number> = {};
      const attempts: Record<string, number> = {};

      for (const chapter of CHAPTERS) {
        try {
          const quiz = await getQuiz(`${chapter.id}-quiz`);
          // Get the best score from recent attempts if available
          const recentAttempt = quiz.user_attempts?.[0];
          if (recentAttempt) {
            scores[chapter.id] = parseFloat(recentAttempt.score_percentage) || 0;
            attempts[chapter.id] = recentAttempt.attempt_number || 1;
          }
        } catch (e) {
          // Quiz not accessible or no attempts
        }
      }

      return { scores, attempts };
    },
    enabled: !!user,
  });

  if (!user) {
    return (
      <div className="min-h-screen bg-[#0B0C10]">
        <Header />
        <main className="container mx-auto px-4 py-16 text-center">
          <h1 className="text-3xl font-bold text-white mb-4">All Quizzes</h1>
          <p className="text-zinc-400 mb-8">Sign in to access quizzes and track your progress</p>
          <Link href="/login">
            <Button size="lg">Sign In</Button>
          </Link>
        </main>
      </div>
    );
  }

  const isPremium = user?.subscription_tier === 'premium' || user?.subscription_tier === 'pro';

  // Get quiz status for each chapter
  const getQuizStatus = (chapterId: string) => {
    const score = quizData?.scores[chapterId];
    const chapterProgress = progress?.chapter_progress?.find(cp => cp.chapter_id === chapterId);

    if (score >= 70) return 'passed';
    if (score || chapterProgress?.started_at) return 'in-progress';
    return 'not-started';
  };

  // Filter chapters based on selected filter
  const filteredChapters = CHAPTERS.filter((chapter) => {
    if (filter === 'all') return true;
    return getQuizStatus(chapter.id) === filter;
  });

  // Calculate stats
  const stats = {
    total: CHAPTERS.length,
    notStarted: CHAPTERS.filter(ch => getQuizStatus(ch.id) === 'not-started').length,
    inProgress: CHAPTERS.filter(ch => getQuizStatus(ch.id) === 'in-progress').length,
    passed: CHAPTERS.filter(ch => getQuizStatus(ch.id) === 'passed').length,
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="min-h-screen bg-[#0B0C10]">
      <Header />

      {/* Hero Section */}
      <div className="border-b border-zinc-800 bg-[#0B0C10]/50 backdrop-blur">
        <div className="container px-4 py-12">
          {/* Breadcrumb */}
          <div className="flex items-center gap-2 text-sm text-zinc-400 mb-4">
            <Link href="/" className="hover:text-emerald-400 transition-colors">Home</Link>
            <span>/</span>
            <span className="text-white font-medium">All Quizzes</span>
          </div>

          {/* Title */}
          <div className="flex items-start justify-between mb-6">
            <div>
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-3">
                All Quizzes
              </h1>
              <p className="text-lg text-zinc-400">
                Test your knowledge with chapter quizzes and track your progress
              </p>
            </div>
          </div>

          {/* Stats Bar */}
          <div className="flex flex-wrap items-center gap-6">
            <div className="flex items-center gap-2 text-sm">
              <Target className="h-4 w-4 text-zinc-500" />
              <span className="text-zinc-400">{stats.total} total quizzes</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <Play className="h-4 w-4 text-blue-400" />
              <span className="text-zinc-400">{stats.inProgress} in progress</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <Trophy className="h-4 w-4 text-emerald-400" />
              <span className="text-zinc-400">{stats.passed} passed</span>
            </div>
            {!isPremium && (
              <div className="ml-auto">
                <Link href="/pricing">
                  <Button size="sm" className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700">
                    <Lock className="h-4 w-4 mr-2" />
                    Unlock All Quizzes
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
              All ({stats.total})
            </FilterButton>
            <FilterButton active={filter === 'not-started'} onClick={() => setFilter('not-started')}>
              Not Started ({stats.notStarted})
            </FilterButton>
            <FilterButton active={filter === 'in-progress'} onClick={() => setFilter('in-progress')}>
              In Progress ({stats.inProgress})
            </FilterButton>
            <FilterButton active={filter === 'passed'} onClick={() => setFilter('passed')}>
              Passed ({stats.passed})
            </FilterButton>
          </div>
        </div>

        {/* Quizzes Grid */}
        {loadingQuizzes ? (
          <div className="flex items-center justify-center py-20">
            <LoadingSpinner size="large" />
          </div>
        ) : filteredChapters.length === 0 ? (
          <div className="text-center py-20">
            <Target className="h-16 w-16 text-zinc-700 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">No quizzes found</h3>
            <p className="text-zinc-400">Try selecting a different filter</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredChapters.map((chapter) => {
              const score = quizData?.scores[chapter.id];
              const status = getQuizStatus(chapter.id);
              const isLocked = chapter.number >= 4 && !isPremium;

              return (
                <div
                  key={chapter.id}
                  className={`group relative ${
                    isLocked ? 'opacity-60' : ''
                  }`}
                >
                  <div className={`card-dark p-6 h-full transition-all duration-300 hover:scale-[1.02] hover:shadow-xl hover:shadow-emerald-500/10 ${
                    status === 'passed' ? 'border-emerald-500/30' : status === 'in-progress' ? 'border-blue-500/30' : ''
                  }`}>
                    {/* Lock Overlay */}
                    {isLocked && (
                      <div className="absolute inset-0 bg-zinc-900/80 backdrop-blur-sm rounded-lg flex items-center justify-center z-10">
                        <div className="text-center">
                          <Lock className="h-8 w-8 text-zinc-400 mx-auto mb-2" />
                          <p className="text-white font-medium">Premium</p>
                          <Link href="/pricing">
                            <Button size="sm" variant="outline" className="mt-3 border-purple-500 text-purple-400 hover:bg-purple-500/10">
                              Upgrade
                            </Button>
                          </Link>
                        </div>
                      </div>
                    )}

                    {/* Chapter Number */}
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-500/10 border border-emerald-500/20 group-hover:bg-emerald-500/20 group-hover:scale-110 transition-all duration-300">
                        <span className="text-lg font-bold text-emerald-400">{chapter.number}</span>
                      </div>
                      {status === 'passed' && <Trophy className="h-5 w-5 text-emerald-400" />}
                      {status === 'in-progress' && <Flame className="h-5 w-5 text-blue-400" />}
                    </div>

                    {/* Title */}
                    <h3 className="mb-2 text-lg font-bold text-white group-hover:text-emerald-400 transition-colors duration-300">
                      {chapter.title}
                    </h3>

                    {/* Difficulty */}
                    <div className="mb-4">
                      <span className={`text-xs font-medium px-2 py-1 rounded ${
                        chapter.difficulty === 'Beginner'
                          ? 'bg-emerald-500/20 text-emerald-400'
                          : chapter.difficulty === 'Intermediate'
                          ? 'bg-yellow-500/20 text-yellow-400'
                          : 'bg-red-500/20 text-red-400'
                      }`}>
                        {chapter.difficulty}
                      </span>
                    </div>

                    {/* Meta Info */}
                    <div className="mb-4 flex items-center gap-4 text-xs text-zinc-500">
                      <div className="flex items-center gap-1">
                        <Target className="h-3.5 w-3.5" />
                        <span>{chapter.questions} questions</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="h-3.5 w-3.5" />
                        <span>{chapter.timeLimit} min</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <CheckCircle className="h-3.5 w-3.5" />
                        <span>70% to pass</span>
                      </div>
                    </div>

                    {/* Score Display */}
                    {score !== undefined && (
                      <div className="mb-4 p-3 bg-zinc-900 rounded-lg border border-zinc-800">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs text-zinc-400">Best Score</span>
                          <span className={`text-lg font-bold ${getScoreColor(score)}`}>
                            {score}%
                          </span>
                        </div>
                        <div className="w-full bg-zinc-800 rounded-full h-2 overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all duration-500"
                            style={{
                              width: `${score}%`,
                              backgroundColor: score >= 80 ? '#10b981' : score >= 60 ? '#f59e0b' : '#ef4444'
                            }}
                          />
                        </div>
                      </div>
                    )}

                    {/* Status Badge */}
                    <div className="flex items-center justify-between mb-4">
                      {status === 'passed' ? (
                        <span className="flex items-center gap-1.5 text-xs font-medium text-emerald-400">
                          <CheckCircle className="h-3.5 w-3.5" />
                          Passed
                        </span>
                      ) : status === 'in-progress' ? (
                        <span className="flex items-center gap-1.5 text-xs font-medium text-blue-400">
                          <Flame className="h-3.5 w-3.5" />
                          In Progress
                        </span>
                      ) : (
                        <span className="text-xs text-zinc-500">Not Started</span>
                      )}
                    </div>

                    {/* CTA Button */}
                    <Link
                      href={isLocked ? '#' : `/chapters/${chapter.id}/quiz`}
                      onClick={(e) => isLocked && e.preventDefault()}
                    >
                      <Button
                        size="sm"
                        className="w-full"
                        disabled={isLocked}
                        variant={status === 'passed' ? 'outline' : 'default'}
                        className={status === 'passed' ? 'border-emerald-500 text-emerald-400 hover:bg-emerald-500/10' : ''}
                      >
                        {status === 'passed' ? (
                          <>
                            <RotateCcw className="h-4 w-4 mr-2" />
                            Retake Quiz
                          </>
                        ) : (
                          <>
                            <Play className="h-4 w-4 mr-2" />
                            {status === 'in-progress' ? 'Continue Quiz' : 'Start Quiz'}
                          </>
                        )}
                      </Button>
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

function FilterButton({
  active,
  onClick,
  children,
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
