'use client';

import { useQuery } from '@tanstack/react-query';
import { useStore } from '@/store/useStore';
import { getProgress } from '@/lib/api';
import { Header } from '@/components/Header';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { Button } from '@/components/ui/Button';
import AIAssistant from '@/components/AIAssistantEmbedded';
import {
  Trophy,
  Flame,
  BookOpen,
  Target,
  TrendingUp,
  Calendar,
  Clock,
  Award,
  Star,
  CheckCircle2,
  ArrowRight,
  AlertCircle,
  Zap,
  BarChart3,
  RefreshCw
} from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { format } from 'date-fns';
import { useState, useEffect } from 'react';

export default function StudentDashboard() {
  const { user } = useStore();
  const router = useRouter();
  const [isClient, setIsClient] = useState(false);

  // Ensure dates are only formatted on client-side
  useEffect(() => {
    setIsClient(true);
  }, []);

  const { data: apiProgress, isLoading, error, refetch } = useQuery({
    queryKey: ['progress'],
    queryFn: async () => {
      const response = await getProgress();
      console.log('Dashboard - Progress API Response:', response);
      console.log('Dashboard - User:', user?.id);
      return response;
    },
    enabled: !!user,
    retry: false,
  });

  // Debug logging to track data source (MUST be before any early returns)
  const progress = apiProgress;

  useEffect(() => {
    console.log('=== DASHBOARD DEBUG ===');
    console.log('User ID:', user?.id);
    console.log('Raw API Response:', progress);
    console.log('Quiz Scores from API:', progress?.quiz_scores);
    console.log('Chapter Progress from API:', progress?.chapter_progress);
    console.log('=====================');
  }, [progress, user?.id]);

  // Show loading state or wait for client-side
  if (isLoading || !isClient) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0B0C10]">
        <LoadingSpinner />
      </div>
    );
  }

  // Show sign-in prompt if not authenticated
  if (!user) {
    return (
      <div className="min-h-screen bg-[#0B0C10]">
        <Header />
        <main className="container mx-auto px-4 py-16 text-center">
          <h1 className="text-4xl font-bold text-white mb-4">Student Dashboard</h1>
          <p className="text-zinc-400 mb-8">Sign in to track your learning progress</p>
          <Link href="/login">
            <Button size="lg">Sign In</Button>
          </Link>
        </main>
      </div>
    );
  }

  // Show error state
  if (error || !apiProgress) {
    return (
      <div className="min-h-screen bg-[#0B0C10]">
        <Header />
        <main className="container mx-auto px-4 py-16">
          <div className="max-w-md mx-auto text-center">
            <div className="bg-zinc-900 rounded-xl p-8 border border-zinc-800">
              <h2 className="text-2xl font-bold text-white mb-4">Unable to Load Progress</h2>
              <p className="text-zinc-400 mb-6">
                We couldn't load your progress data. This might be because you haven't started learning yet.
              </p>
              <div className="flex gap-3 justify-center">
                <Button onClick={() => refetch()}>Try Again</Button>
                <Link href="/chapters/chapter-1">
                  <Button variant="outline">Start Learning</Button>
                </Link>
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  const completionPercentage = progress.completion_percentage;
  const completedChapters = progress.chapters_completed;
  const totalChapters = progress.total_chapters;
  const currentStreak = progress.current_streak;
  const longestStreak = progress.longest_streak;
  const totalActiveDays = progress.total_active_days;
  // Only format date on client-side to prevent hydration errors
  const lastActivityDate = isClient && progress.last_activity_date
    ? format(new Date(progress.last_activity_date), 'MM/dd/yyyy')
    : 'No activity yet';

  // Calculate quiz statistics from recent attempts
  const recentAttempts = progress.recent_quiz_attempts || [];
  const quizScores = recentAttempts.length > 0
    ? recentAttempts.map(a => parseFloat(a.score_percentage) || 0)
    : Object.values(progress.quiz_scores || {}).map(s => parseFloat(s) || 0);
  const averageQuizScore = quizScores.length > 0
    ? quizScores.reduce((sum, score) => sum + score, 0) / quizScores.length
    : 0;

  // Identify weak areas (chapters with quiz scores below 70%)
  const weakAreas = Object.entries(progress.quiz_scores || {})
    .filter(([_, score]) => parseFloat(score) < 70)
    .map(([chapterId, score]) => ({
      chapterId,
      chapterNumber: chapterId.split('-')[1],
      score: parseFloat(score),
    }));

  // Calculate next recommended chapter
  const nextChapter = completedChapters < totalChapters ? completedChapters + 1 : null;

  // Milestones
  const milestones = [
    { achieved: completedChapters >= 1, icon: '🎯', title: 'First Chapter', description: 'Completed your first chapter' },
    { achieved: completedChapters >= 3, icon: '📚', title: 'Halfway There', description: 'Completed 3 chapters' },
    { achieved: completedChapters >= 6, icon: '🏆', title: 'Course Master', description: 'Completed all chapters' },
    { achieved: currentStreak >= 3, icon: '🔥', title: 'On Fire', description: '3-day learning streak' },
    { achieved: currentStreak >= 7, icon: '💎', title: 'Dedicated Learner', description: '7-day learning streak' },
    { achieved: longestStreak >= 10, icon: '⭐', title: 'Consistency King', description: '10-day longest streak' },
    { achieved: totalActiveDays >= 20, icon: '🎓', title: 'Knowledge Seeker', description: '20+ active learning days' },
    { achieved: completionPercentage >= 80, icon: '👑', title: 'Almost There', description: '80% course completion' },
  ];

  const earnedMilestones = milestones.filter(m => m.achieved).length;

  return (
    <div className="min-h-screen bg-[#0B0C10]">
      <Header />
      <main className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8 animate-fade-in">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Student Dashboard</h1>
            <p className="text-zinc-400">Track your learning journey and achieve your goals</p>
          </div>
          <div className="flex gap-3">
            <Link href="/progress">
              <Button
                variant="outline"
                size="sm"
                className="border-emerald-500 text-emerald-400 hover:bg-emerald-500 hover:text-white hover:scale-105 active:scale-95 transition-all duration-300"
              >
                <BarChart3 className="w-4 h-4 mr-2" />
                View Analytics
              </Button>
            </Link>
            <Button
              onClick={() => refetch()}
              variant="ghost"
              size="sm"
              className="hover:scale-105 active:scale-95 transition-all duration-300"
            >
              <RefreshCw className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Learning Progress Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-blue-400" />
            Learning Progress
          </h2>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Visual Progress Overview */}
            <div className="bg-zinc-900 rounded-xl p-8 border border-zinc-800 flex flex-col items-center justify-center animate-fade-in-up">
              <div className="relative w-48 h-48 mb-4">
                <svg className="w-full h-full transform -rotate-90">
                  <circle
                    cx="96"
                    cy="96"
                    r="88"
                    stroke="currentColor"
                    strokeWidth="12"
                    fill="transparent"
                    className="text-zinc-800"
                  />
                  <circle
                    cx="96"
                    cy="96"
                    r="88"
                    stroke="currentColor"
                    strokeWidth="12"
                    fill="transparent"
                    strokeDasharray={`${2 * Math.PI * 88}`}
                    strokeDashoffset={`${2 * Math.PI * 88 * (1 - completionPercentage / 100)}`}
                    strokeLinecap="round"
                    className="text-emerald-500 transition-all duration-1000"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-5xl font-bold text-white">{completionPercentage}%</span>
                  <span className="text-sm text-zinc-400">Complete</span>
                </div>
              </div>
              <div className="text-center">
                <p className="text-lg text-white font-semibold">{completedChapters} of {totalChapters} Chapters</p>
                <p className="text-sm text-zinc-400">{totalChapters - completedChapters} chapters remaining</p>
              </div>
            </div>

            {/* Current & Next Chapter */}
            <div className="bg-zinc-900 rounded-xl p-8 border border-zinc-800 animate-fade-in-up delay-100">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-emerald-400" />
                Current & Next
              </h3>
              <div className="space-y-4">
                {completedChapters < totalChapters ? (
                  <>
                    <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-lg">
                      <p className="text-sm text-zinc-400 mb-1">Continue Learning</p>
                      <p className="text-white font-semibold mb-2">Chapter {nextChapter}</p>
                      <Link href={`/chapters/chapter-${nextChapter}`}>
                        <Button size="sm" className="w-full hover:scale-105 active:scale-95 transition-all duration-300">
                          Continue
                          <ArrowRight className="ml-2 w-4 h-4" />
                        </Button>
                      </Link>
                    </div>
                    {completedChapters > 0 && (
                      <div className="p-4 bg-zinc-800 rounded-lg">
                        <p className="text-sm text-zinc-400 mb-1">Last Completed</p>
                        <p className="text-white font-semibold">Chapter {completedChapters}</p>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                    <p className="text-yellow-400 font-semibold flex items-center gap-2">
                      <Trophy className="w-5 h-5" />
                      Course Completed!
                    </p>
                    <p className="text-sm text-zinc-400 mt-2">Congratulations on finishing all chapters!</p>
                  </div>
                )}
              </div>
            </div>

            {/* Progress Stats */}
            <div className="bg-zinc-900 rounded-xl p-8 border border-zinc-800 animate-fade-in-up delay-200">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-purple-400" />
                Progress Stats
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-zinc-400">Completed</span>
                  <span className="text-white font-semibold">{completedChapters} chapters</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-zinc-400">Remaining</span>
                  <span className="text-white font-semibold">{totalChapters - completedChapters} chapters</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-zinc-400">Completion</span>
                  <span className="text-emerald-400 font-semibold">{completionPercentage}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-zinc-400">Total Study Time</span>
                  <span className="text-white font-semibold">
                    {progress.chapter_progress?.reduce((sum, ch) => sum + (ch.time_spent_minutes || 0), 0) || 0} min
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quizzes & Mastery Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            <Target className="w-6 h-6 text-purple-400" />
            Quizzes & Mastery
          </h2>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Quiz Scores */}
            <div className="bg-zinc-900 rounded-xl p-8 border border-zinc-800 animate-fade-in-up">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Star className="w-5 h-5 text-yellow-400" />
                Recent Quiz Scores
              </h3>
              {recentAttempts.length > 0 ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-zinc-800 rounded-lg">
                    <span className="text-zinc-400">Average Score</span>
                    <span className="text-xl font-bold text-white">{averageQuizScore.toFixed(1)}%</span>
                  </div>
                  {recentAttempts.map((attempt, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-zinc-800 rounded-lg">
                      <div className="flex-1">
                        <span className="text-zinc-400 text-sm">Chapter {attempt.chapter_id?.replace('chapter-', '')}</span>
                        <span className="text-zinc-500 text-xs ml-2">Attempt #{attempt.attempt_number}</span>
                      </div>
                      <span className={`font-bold ${
                        parseFloat(attempt.score_percentage) >= 80 ? 'text-emerald-400' : parseFloat(attempt.score_percentage) >= 60 ? 'text-yellow-400' : 'text-red-400'
                      }`}>
                        {attempt.score_percentage}%
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-zinc-400 text-center py-8">No quizzes taken yet</p>
              )}
            </div>

            {/* Weak Areas */}
            <div className="bg-zinc-900 rounded-xl p-8 border border-zinc-800 animate-fade-in-up delay-100">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-orange-400" />
                Areas to Improve
              </h3>
              {weakAreas.length > 0 ? (
                <div className="space-y-3">
                  {weakAreas.map((area) => (
                    <div key={area.chapterId} className="p-4 bg-orange-500/10 border border-orange-500/30 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-white font-semibold">Chapter {area.chapterNumber}</span>
                        <span className="text-orange-400 font-bold">{area.score}%</span>
                      </div>
                      <Link href={`/chapters/${area.chapterId}`}>
                        <Button size="sm" variant="secondary" className="w-full hover:scale-105 active:scale-95 transition-all duration-300">
                          <BookOpen className="mr-2 w-4 h-4" />
                          Review Chapter
                        </Button>
                      </Link>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
                  <p className="text-zinc-400">No weak areas identified!</p>
                  <p className="text-sm text-zinc-500">Great job on your quizzes!</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Streaks & Motivation Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            <Flame className="w-6 h-6 text-orange-400" />
            Streaks & Motivation
          </h2>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Current Streak */}
            <div className="bg-zinc-900 rounded-xl p-8 border border-zinc-800 animate-fade-in-up">
              <div className="flex items-center justify-between mb-4">
                <Flame className="w-10 h-10 text-orange-400" />
                <div className="text-right">
                  <p className="text-4xl font-bold text-orange-400">{currentStreak}</p>
                  <p className="text-sm text-zinc-400">days</p>
                </div>
              </div>
              <p className="text-white font-semibold">Current Streak</p>
              {currentStreak >= 3 && (
                <p className="text-sm text-zinc-400 mt-1">You&apos;re on fire! Keep it going!</p>
              )}
            </div>

            {/* Longest Streak */}
            <div className="bg-zinc-900 rounded-xl p-8 border border-zinc-800 animate-fade-in-up delay-100">
              <div className="flex items-center justify-between mb-4">
                <Award className="w-10 h-10 text-yellow-400" />
                <div className="text-right">
                  <p className="text-4xl font-bold text-yellow-400">{longestStreak}</p>
                  <p className="text-sm text-zinc-400">days</p>
                </div>
              </div>
              <p className="text-white font-semibold">Longest Streak</p>
              <p className="text-sm text-zinc-400 mt-1">Your personal best!</p>
            </div>

            {/* Last Active */}
            <div className="bg-zinc-900 rounded-xl p-8 border border-zinc-800 animate-fade-in-up delay-200">
              <div className="flex items-center justify-between mb-4">
                <Calendar className="w-10 h-10 text-blue-400" />
                <div className="text-right">
                  {isClient ? (
                    <p className="text-2xl font-bold text-white">{lastActivityDate}</p>
                  ) : (
                    <p className="text-2xl font-bold text-white">...</p>
                  )}
                  <p className="text-sm text-zinc-400">last active</p>
                </div>
              </div>
              <p className="text-white font-semibold">Last Activity</p>
              <p className="text-sm text-zinc-400 mt-1">
                {totalActiveDays} total active days
              </p>
            </div>
          </div>
        </div>

        {/* Milestones */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            <Trophy className="w-6 h-6 text-yellow-400" />
            Milestones ({earnedMilestones}/{milestones.length})
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {milestones.map((milestone, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border transition-all hover-lift ${
                  milestone.achieved
                    ? 'bg-yellow-500/10 border-yellow-500/30'
                    : 'bg-zinc-800/50 border-zinc-700/50 opacity-50'
                }`}
              >
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-2xl">{milestone.icon}</span>
                  {milestone.achieved && <CheckCircle2 className="w-5 h-5 text-yellow-400" />}
                </div>
                <p className={`font-semibold text-sm ${
                  milestone.achieved ? 'text-white' : 'text-zinc-500'
                }`}>
                  {milestone.title}
                </p>
                <p className="text-xs text-zinc-400">{milestone.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Premium Features Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            <Zap className="w-6 h-6 text-purple-400" />
            Premium Features
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Adaptive Learning Path */}
            <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-xl p-8 border border-purple-500/30 animate-fade-in-up">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-purple-500/20 rounded-lg">
                  <Target className="w-8 h-8 text-purple-400" />
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-white mb-2">Adaptive Learning Path</h3>
                  <p className="text-zinc-400 mb-4">
                    Get a personalized AI-powered study plan based on your progress and learning patterns.
                  </p>
                  <div className="flex flex-wrap gap-2 mb-4">
                    <span className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded text-xs">Personalized</span>
                    <span className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded text-xs">AI-Powered</span>
                    <span className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded text-xs">Smart Recommendations</span>
                  </div>
                  {nextChapter && (
                    <Link href={`/chapters/chapter-${nextChapter}/adaptive-path`}>
                      <Button className="hover:scale-105 active:scale-95 transition-all duration-300">
                        Generate Path
                        <ArrowRight className="ml-2 w-4 h-4" />
                      </Button>
                    </Link>
                  )}
                </div>
              </div>
            </div>

            {/* LLM-Graded Assessments */}
            <div className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10 rounded-xl p-8 border border-blue-500/30 animate-fade-in-up delay-100">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-blue-500/20 rounded-lg">
                  <Star className="w-8 h-8 text-blue-400" />
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-white mb-2">AI-Graded Assessments</h3>
                  <p className="text-zinc-400 mb-4">
                    Submit free-form answers and get detailed feedback with scores from AI.
                  </p>
                  <div className="flex flex-wrap gap-2 mb-4">
                    <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs">Detailed Feedback</span>
                    <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs">Instant Grading</span>
                    <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs">Actionable Tips</span>
                  </div>
                  {nextChapter && (
                    <Link href={`/assessments/chapter-${nextChapter}`}>
                      <Button className="hover:scale-105 active:scale-95 transition-all duration-300">
                        Try Assessment
                        <ArrowRight className="ml-2 w-4 h-4" />
                      </Button>
                    </Link>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div>
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            <Zap className="w-6 h-6 text-emerald-400" />
            Quick Actions
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Continue Learning */}
            {nextChapter && (
              <Link href={`/chapters/chapter-${nextChapter}`} className="block hover-lift">
                <div className="bg-zinc-900 rounded-xl p-6 border border-zinc-800 hover:border-emerald-500/50 transition-all">
                  <div className="flex items-center gap-4 mb-3">
                    <div className="p-3 bg-emerald-500/20 rounded-lg">
                      <BookOpen className="w-8 h-8 text-emerald-400" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-white">Continue Learning</h3>
                      <p className="text-sm text-zinc-400">Chapter {nextChapter}</p>
                    </div>
                  </div>
                  <p className="text-sm text-zinc-500">Pick up where you left off</p>
                </div>
              </Link>
            )}

            {/* Review Weak Areas */}
            {weakAreas.length > 0 ? (
              <Link href={`/chapters/${weakAreas[0].chapterId}`} className="block hover-lift">
                <div className="bg-zinc-900 rounded-xl p-6 border border-zinc-800 hover:border-orange-500/50 transition-all">
                  <div className="flex items-center gap-4 mb-3">
                    <div className="p-3 bg-orange-500/20 rounded-lg">
                      <AlertCircle className="w-8 h-8 text-orange-400" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-white">Review Weak Areas</h3>
                      <p className="text-sm text-zinc-400">{weakAreas.length} areas to improve</p>
                    </div>
                  </div>
                  <p className="text-sm text-zinc-500">Strengthen your understanding</p>
                </div>
              </Link>
            ) : (
              <div className="bg-zinc-900 rounded-xl p-6 border border-zinc-800 opacity-50">
                <div className="flex items-center gap-4 mb-3">
                  <div className="p-3 bg-zinc-800 rounded-lg">
                    <CheckCircle2 className="w-8 h-8 text-zinc-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-zinc-500">No Weak Areas</h3>
                    <p className="text-sm text-zinc-600">All quizzes passed!</p>
                  </div>
                </div>
                <p className="text-sm text-zinc-600">Great job!</p>
              </div>
            )}

            {/* Take a Quiz */}
            {nextChapter && (
              <Link href={`/chapters/chapter-${nextChapter}/quiz`} className="block hover-lift">
                <div className="bg-zinc-900 rounded-xl p-6 border border-zinc-800 hover:border-purple-500/50 transition-all">
                  <div className="flex items-center gap-4 mb-3">
                    <div className="p-3 bg-purple-500/20 rounded-lg">
                      <Target className="w-8 h-8 text-purple-400" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-white">Take a Quiz</h3>
                      <p className="text-sm text-zinc-400">Chapter {nextChapter}</p>
                    </div>
                  </div>
                  <p className="text-sm text-zinc-500">Test your knowledge</p>
                </div>
              </Link>
            )}
          </div>
        </div>
      </main>
      <AIAssistant />
    </div>
  );
}
