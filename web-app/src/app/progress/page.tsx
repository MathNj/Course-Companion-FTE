'use client';

import { useQuery } from '@tanstack/react-query';
import { useStore } from '@/store/useStore';
import { getProgress } from '@/lib/api';
import { Header } from '@/components/Header';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { Button } from '@/components/ui/Button';
import { LineChart, BarChart, DoughnutChart, ProgressRing } from '@/components/charts';
import { ProgressExportButton } from '@/components/PDFExportButton';
import type { ProgressPDFData } from '@/lib/pdfExport';
import {
  BarChart3,
  TrendingUp,
  Clock,
  Target,
  Award,
  BookOpen,
  CheckCircle2,
  Calendar,
  Trophy,
  Flame,
  ArrowRight,
  AlertCircle,
  RefreshCw,
  Download,
  Filter,
  Zap
} from 'lucide-react';
import Link from 'next/link';
import { format, subDays, startOfDay } from 'date-fns';

export default function ProgressPage() {
  const { user } = useStore();

  const { data: apiProgress, isLoading, refetch } = useQuery({
    queryKey: ['progress'],
    queryFn: getProgress,
    enabled: !!user,
  });

  // Prepare progress data for PDF export
  const prepareProgressData = (): ProgressPDFData => {
    const progress = apiProgress || mockProgress;

    return {
      user: {
        email: user?.email || 'user@example.com',
        subscriptionType: user?.subscription_type || 'free'
      },
      progress: {
        completionPercentage: progress.completion_percentage || 0,
        currentStreak: progress.current_streak || 0,
        totalQuizzesTaken: Object.keys(progress.quiz_scores || {}).length,
        averageQuizScore: Object.values(progress.quiz_scores || {}).reduce((a, b) => a + b, 0) / (Object.keys(progress.quiz_scores || {}).length || 1),
        chaptersCompleted: progress.chapters_completed || 0,
        totalChapters: progress.total_chapters || 6
      },
      quizHistory: Object.entries(progress.quiz_scores || {}).map(([chapterId, score]) => ({
        chapterTitle: `Chapter ${chapterId.replace('chapter-', '')}`,
        score: score as number,
        completedAt: progress.last_activity_date || new Date().toISOString()
      })),
      generatedAt: new Date().toISOString()
    };
  };

  // Enhanced mock progress data for demonstration
  const mockProgress = {
    completion_percentage: 65,
    chapters_completed: 4,
    total_chapters: 6,
    current_streak: 7,
    longest_streak: 12,
    total_active_days: 18,
    last_activity_date: new Date().toISOString(),
    quiz_scores: {
      'chapter-1': 85,
      'chapter-2': 92,
      'chapter-3': 65,
      'chapter-4': 88,
    },
    chapter_progress: [
      {
        chapter_id: 'chapter-1',
        completion_status: 'completed',
        completion_percent: 100,
        quiz_score: 85,
        time_spent_minutes: 45,
        last_accessed: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        chapter_id: 'chapter-2',
        completion_status: 'completed',
        completion_percent: 100,
        quiz_score: 92,
        time_spent_minutes: 52,
        last_accessed: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        chapter_id: 'chapter-3',
        completion_status: 'completed',
        completion_percent: 100,
        quiz_score: 65,
        time_spent_minutes: 38,
        last_accessed: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        chapter_id: 'chapter-4',
        completion_status: 'completed',
        completion_percent: 100,
        quiz_score: 88,
        time_spent_minutes: 48,
        last_accessed: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        chapter_id: 'chapter-5',
        completion_status: 'in_progress',
        completion_percent: 50,
        quiz_score: undefined,
        time_spent_minutes: 25,
        last_accessed: new Date().toISOString(),
      },
      {
        chapter_id: 'chapter-6',
        completion_status: 'not_started',
        completion_percent: 0,
        quiz_score: undefined,
        time_spent_minutes: 0,
        last_accessed: new Date().toISOString(),
      },
    ],
  };

  const progress = apiProgress || mockProgress;

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0B0C10]">
        <LoadingSpinner />
      </div>
    );
  }

  // Calculate performance metrics
  const quizScores = Object.values(progress.quiz_scores || {});
  const averageQuizScore = quizScores.length > 0
    ? quizScores.reduce((sum, score) => sum + score, 0) / quizScores.length
    : 0;
  const highestQuizScore = quizScores.length > 0 ? Math.max(...quizScores) : 0;
  const lowestQuizScore = quizScores.length > 0 ? Math.min(...quizScores) : 0;
  const passedQuizzes = quizScores.filter(score => score >= 80).length;
  const totalQuizzes = quizScores.length;

  // Calculate study time estimates
  const totalStudyMinutes = progress.chapter_progress?.reduce(
    (sum, chapter) => sum + (chapter.time_spent_minutes || 0),
    0
  ) || 0;
  const studyHours = Math.floor(totalStudyMinutes / 60);
  const studyMinutes = totalStudyMinutes % 60;

  // Identify weak areas (chapters with quiz scores below 70%)
  const weakAreas = Object.entries(progress.quiz_scores || {})
    .filter(([_, score]) => score < 70)
    .map(([chapterId, score]) => ({
      chapterId,
      chapterNumber: chapterId.split('-')[1],
      score,
    }));

  // Generate quiz trend data (last 7 quizzes with simulated trend)
  const quizTrendData = quizScores.length > 0
    ? [...quizScores, ...(quizScores.length < 7 ? Array(7 - quizScores.length).fill(0) : [])].slice(0, 7)
    : [0, 0, 0, 0, 0, 0, 0];

  const quizTrendLabels = quizScores.length > 0
    ? quizScores.map((_, i) => `Quiz ${i + 1}`)
    : ['Quiz 1', 'Quiz 2', 'Quiz 3', 'Quiz 4', 'Quiz 5', 'Quiz 6', 'Quiz 7'];

  // Chapter completion data for doughnut chart
  const completionDistribution = [
    progress.chapters_completed || 0, // Completed
    progress.chapter_progress?.filter(ch => ch.completion_status === 'in_progress').length || 0, // In Progress
    progress.total_chapters - progress.chapters_completed - (progress.chapter_progress?.filter(ch => ch.completion_status === 'in_progress').length || 0), // Not Started
  ];

  // Calculate next recommended chapter
  const nextChapter = (progress.chapters_completed || 0) < (progress.total_chapters || 6)
    ? (progress.chapters_completed || 0) + 1
    : null;

  // Generate study activity data (simulated last 7 days)
  const studyActivityData = [45, 60, 30, 75, 90, 45, 60]; // Minutes studied per day
  const activityLabels = Array.from({ length: 7 }, (_, i) =>
    format(subDays(new Date(), 6 - i), 'MMM dd')
  );

  return (
    <div className="min-h-screen bg-[#0B0C10]">
      <Header />
      <main className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8 animate-fade-in">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Progress Dashboard</h1>
            <p className="text-zinc-400">Visual analytics and performance insights</p>
          </div>
          <div className="flex gap-3">
            <ProgressExportButton progress={prepareProgressData()} />
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

        {/* Overview Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-zinc-900 rounded-xl p-6 border border-zinc-800 hover-lift animate-fade-in-up">
            <div className="flex items-center justify-between mb-4">
              <BookOpen className="w-8 h-8 text-blue-400" />
              <span className="text-xs text-zinc-500">Completion</span>
            </div>
            <h3 className="text-3xl font-bold text-white mb-2">{progress.completion_percentage}%</h3>
            <p className="text-sm text-zinc-400">{progress.chapters_completed}/{progress.total_chapters} chapters</p>
            <div className="mt-3 w-full bg-zinc-800 rounded-full h-2">
              <div
                className="h-2 rounded-full bg-blue-500 transition-all duration-500"
                style={{ width: `${progress.completion_percentage}%` }}
              />
            </div>
          </div>

          <div className="bg-zinc-900 rounded-xl p-6 border border-zinc-800 hover-lift animate-fade-in-up delay-100">
            <div className="flex items-center justify-between mb-4">
              <Target className="w-8 h-8 text-purple-400" />
              <span className="text-xs text-zinc-500">Avg Quiz Score</span>
            </div>
            <h3 className="text-3xl font-bold text-white mb-2">{averageQuizScore.toFixed(1)}%</h3>
            <p className="text-sm text-zinc-400">{passedQuizzes}/{totalQuizzes} passed</p>
            <div className="mt-3 flex gap-1">
              {quizScores.slice(0, 5).map((score, i) => (
                <div
                  key={i}
                  className="flex-1 h-2 rounded-full"
                  style={{
                    backgroundColor: score >= 80 ? '#10b981' : score >= 60 ? '#f59e0b' : '#ef4444'
                  }}
                />
              ))}
            </div>
          </div>

          <div className="bg-zinc-900 rounded-xl p-6 border border-zinc-800 hover-lift animate-fade-in-up delay-200">
            <div className="flex items-center justify-between mb-4">
              <Clock className="w-8 h-8 text-emerald-400" />
              <span className="text-xs text-zinc-500">Study Time</span>
            </div>
            <h3 className="text-3xl font-bold text-white mb-2">
              {studyHours > 0 ? `${studyHours}h ${studyMinutes}m` : `${studyMinutes}m`}
            </h3>
            <p className="text-sm text-zinc-400">{totalStudyMinutes} minutes total</p>
            <div className="mt-3 flex items-center gap-2">
              <Flame className="w-4 h-4 text-orange-400" />
              <span className="text-xs text-zinc-400">{progress.total_active_days} active days</span>
            </div>
          </div>

          <div className="bg-zinc-900 rounded-xl p-6 border border-zinc-800 hover-lift animate-fade-in-up delay-300">
            <div className="flex items-center justify-between mb-4">
              <Award className="w-8 h-8 text-yellow-400" />
              <span className="text-xs text-zinc-500">Streak</span>
            </div>
            <h3 className="text-3xl font-bold text-white mb-2">{progress.current_streak} days</h3>
            <p className="text-sm text-zinc-400">Best: {progress.longest_streak} days</p>
            <div className="mt-3 flex items-center gap-2">
              {progress.current_streak >= 3 && (
                <>
                  <Zap className="w-4 h-4 text-yellow-400" />
                  <span className="text-xs text-zinc-400">On fire!</span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Visual Analytics Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-blue-400" />
            Visual Analytics
          </h2>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* Quiz Scores Trend - Line Chart */}
            <div className="bg-zinc-900 rounded-xl p-6 border border-zinc-800 animate-fade-in-up">
              <h3 className="text-lg font-bold text-white mb-4">Quiz Scores Trend</h3>
              {quizScores.length > 0 ? (
                <LineChart
                  data={quizTrendData}
                  labels={quizTrendLabels}
                  label="Score (%)"
                  color="#8b5cf6"
                />
              ) : (
                <div className="h-64 flex items-center justify-center text-zinc-500">
                  No quiz data available yet
                </div>
              )}
            </div>

            {/* Chapter Accuracy - Bar Chart */}
            <div className="bg-zinc-900 rounded-xl p-6 border border-zinc-800 animate-fade-in-up delay-100">
              <h3 className="text-lg font-bold text-white mb-4">Accuracy by Chapter</h3>
              {quizScores.length > 0 ? (
                <BarChart
                  data={quizScores}
                  labels={quizScores.map((_, i) => `Ch ${i + 1}`)}
                  label="Score (%)"
                />
              ) : (
                <div className="h-64 flex items-center justify-center text-zinc-500">
                  No quiz data available yet
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Completion Distribution - Doughnut Chart */}
            <div className="bg-zinc-900 rounded-xl p-6 border border-zinc-800 animate-fade-in-up">
              <h3 className="text-lg font-bold text-white mb-4">Completion Status</h3>
              <DoughnutChart
                data={completionDistribution}
                labels={['Completed', 'In Progress', 'Not Started']}
                colors={['#10b981', '#3b82f6', '#3f3f46']}
              />
            </div>

            {/* Study Activity - Bar Chart */}
            <div className="bg-zinc-900 rounded-xl p-6 border border-zinc-800 animate-fade-in-up delay-100 lg:col-span-2">
              <h3 className="text-lg font-bold text-white mb-4">Study Activity (Last 7 Days)</h3>
              <BarChart
                data={studyActivityData}
                labels={activityLabels}
                label="Minutes"
              />
            </div>
          </div>
        </div>

        {/* Performance Insights */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-emerald-400" />
            Performance Insights
          </h2>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Quiz Performance Analysis */}
            <div className="bg-zinc-900 rounded-xl p-8 border border-zinc-800 animate-fade-in-up">
              <h3 className="text-xl font-bold text-white mb-6">Quiz Statistics</h3>
              {totalQuizzes > 0 ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-zinc-800 rounded-lg">
                    <span className="text-zinc-300">Average Score</span>
                    <span className="text-2xl font-bold text-white">{averageQuizScore.toFixed(1)}%</span>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-zinc-800 rounded-lg">
                    <span className="text-zinc-300">Highest Score</span>
                    <span className="text-2xl font-bold text-emerald-400">{highestQuizScore}%</span>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-zinc-800 rounded-lg">
                    <span className="text-zinc-300">Lowest Score</span>
                    <span className={`text-2xl font-bold ${
                      lowestQuizScore >= 60 ? 'text-yellow-400' : 'text-red-400'
                    }`}>
                      {lowestQuizScore}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-zinc-800 rounded-lg">
                    <span className="text-zinc-300">Pass Rate</span>
                    <span className="text-2xl font-bold text-blue-400">
                      {totalQuizzes > 0 ? ((passedQuizzes / totalQuizzes) * 100).toFixed(0) : 0}%
                    </span>
                  </div>
                </div>
              ) : (
                <p className="text-zinc-400 text-center py-8">No quizzes taken yet</p>
              )}
            </div>

            {/* Study Statistics */}
            <div className="bg-zinc-900 rounded-xl p-8 border border-zinc-800 animate-fade-in-up delay-100">
              <h3 className="text-xl font-bold text-white mb-6">Study Statistics</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-zinc-800 rounded-lg">
                  <span className="text-zinc-300">Total Study Time</span>
                  <span className="text-xl font-bold text-white">
                    {studyHours > 0 ? `${studyHours}h ${studyMinutes}m` : `${studyMinutes}m`}
                  </span>
                </div>
                <div className="flex items-center justify-between p-4 bg-zinc-800 rounded-lg">
                  <span className="text-zinc-300">Active Days</span>
                  <span className="text-xl font-bold text-white">{progress.total_active_days} days</span>
                </div>
                <div className="flex items-center justify-between p-4 bg-zinc-800 rounded-lg">
                  <span className="text-zinc-300">Current Streak</span>
                  <span className="text-xl font-bold text-orange-400">{progress.current_streak} days</span>
                </div>
                <div className="flex items-center justify-between p-4 bg-zinc-800 rounded-lg">
                  <span className="text-zinc-300">Longest Streak</span>
                  <span className="text-xl font-bold text-yellow-400">{progress.longest_streak} days</span>
                </div>
                <div className="flex items-center justify-between p-4 bg-zinc-800 rounded-lg">
                  <span className="text-zinc-300">Last Activity</span>
                  <span className="text-sm font-bold text-white">
                    {new Date(progress.last_activity_date).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Chapter Progress */}
        <div className="bg-zinc-900 rounded-xl p-8 border border-zinc-800 mb-8 animate-fade-in-up">
          <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <CheckCircle2 className="w-6 h-6 text-emerald-400" />
            Chapter-by-Chapter Progress
          </h2>
          <div className="space-y-6">
            {progress.chapter_progress?.map((chapter) => (
              <div key={chapter.chapter_id} className="border border-zinc-800 rounded-lg p-6 hover:border-zinc-700 transition-all">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-white mb-1">
                      Chapter {chapter.chapter_id.split('-')[1]}
                    </h3>
                    <p className="text-sm text-zinc-400">
                      {chapter.completion_status === 'completed' && '✓ Completed'}
                      {chapter.completion_status === 'in_progress' && '→ In Progress'}
                      {chapter.completion_status === 'not_started' && '○ Not Started'}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    {chapter.quiz_score !== undefined && (
                      <div className="text-right">
                        <p className="text-xs text-zinc-400 mb-1">Quiz Score</p>
                        <p className={`text-lg font-bold ${
                          chapter.quiz_score >= 80
                            ? 'text-emerald-400'
                            : chapter.quiz_score >= 60
                            ? 'text-yellow-400'
                            : 'text-red-400'
                        }`}>
                          {chapter.quiz_score}%
                        </p>
                      </div>
                    )}
                    <div className="w-16 h-16 rounded-full border-4 flex items-center justify-center bg-zinc-800" style={{
                      borderColor: chapter.completion_status === 'completed'
                        ? '#10b981'
                        : chapter.completion_status === 'in_progress'
                        ? '#3b82f6'
                        : '#3f3f46'
                    }}>
                      <span className={`text-lg font-bold ${
                        chapter.completion_status === 'completed'
                          ? 'text-emerald-400'
                          : chapter.completion_status === 'in_progress'
                          ? 'text-blue-400'
                          : 'text-zinc-500'
                      }`}>
                        {chapter.completion_status === 'completed'
                          ? '✓'
                          : chapter.completion_status === 'in_progress'
                          ? '→'
                          : '—'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="w-full bg-zinc-800 rounded-full h-3 mb-3">
                  <div
                    className="h-3 rounded-full transition-all duration-500"
                    style={{
                      width: `${chapter.completion_percent || chapter.completion_status === 'completed' ? 100 : chapter.completion_status === 'in_progress' ? 50 : 0}%`,
                      backgroundColor: chapter.completion_percent === 100 || chapter.completion_status === 'completed'
                        ? '#10b981'
                        : chapter.completion_percent === 50 || chapter.completion_status === 'in_progress'
                        ? '#3b82f6'
                        : '#3f3f46'
                    }}
                  />
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-zinc-500">Time Spent</p>
                    <p className="text-white font-semibold">
                      {chapter.time_spent_minutes || 0} min
                    </p>
                  </div>
                  <div>
                    <p className="text-zinc-500">Last Accessed</p>
                    <p className="text-white font-semibold">
                      {new Date(chapter.last_accessed).toLocaleDateString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-zinc-500">Progress</p>
                    <p className="text-white font-semibold">
                      {chapter.completion_percent || (chapter.completion_status === 'completed' ? 100 : chapter.completion_status === 'in_progress' ? 50 : 0)}%
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Actionable Insights */}
        <div className="bg-zinc-900 rounded-xl p-8 border border-zinc-800 animate-fade-in-up delay-100">
          <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <Target className="w-6 h-6 text-blue-400" />
            Personalized Recommendations
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Continue Learning */}
            {nextChapter && (
              <Link href={`/chapters/chapter-${nextChapter}`} className="block">
                <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-lg hover-lift cursor-pointer">
                  <div className="flex items-center gap-3 mb-2">
                    <BookOpen className="w-5 h-5 text-emerald-400" />
                    <p className="text-white font-semibold">Continue Learning</p>
                  </div>
                  <p className="text-sm text-zinc-400 mb-3">
                    Pick up where you left off in Chapter {nextChapter}
                  </p>
                  <Button size="sm" className="w-full">
                    Continue
                    <ArrowRight className="ml-2 w-4 h-4" />
                  </Button>
                </div>
              </Link>
            )}

            {/* Review Weak Areas */}
            {weakAreas.length > 0 && (
              <Link href={`/chapters/${weakAreas[0].chapterId}`} className="block">
                <div className="p-4 bg-orange-500/10 border border-orange-500/30 rounded-lg hover-lift cursor-pointer">
                  <div className="flex items-center gap-3 mb-2">
                    <AlertCircle className="w-5 h-5 text-orange-400" />
                    <p className="text-white font-semibold">Review Weak Areas</p>
                  </div>
                  <p className="text-sm text-zinc-400 mb-3">
                    {weakAreas.length} chapter{weakAreas.length > 1 ? 's' : ''} need improvement
                  </p>
                  <Button size="sm" variant="secondary" className="w-full">
                    Review Now
                    <ArrowRight className="ml-2 w-4 h-4" />
                  </Button>
                </div>
              </Link>
            )}

            {/* Retake Quiz */}
            {nextChapter && (
              <Link href={`/chapters/chapter-${nextChapter}/quiz`} className="block">
                <div className="p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg hover-lift cursor-pointer">
                  <div className="flex items-center gap-3 mb-2">
                    <Target className="w-5 h-5 text-purple-400" />
                    <p className="text-white font-semibold">Take a Quiz</p>
                  </div>
                  <p className="text-sm text-zinc-400 mb-3">
                    Test your knowledge of Chapter {nextChapter}
                  </p>
                  <Button size="sm" className="w-full">
                    Start Quiz
                    <ArrowRight className="ml-2 w-4 h-4" />
                  </Button>
                </div>
              </Link>
            )}

            {/* Maintain Streak */}
            {progress.current_streak >= 3 && (
              <div className="p-4 bg-orange-500/10 border border-orange-500/30 rounded-lg">
                <div className="flex items-center gap-3 mb-2">
                  <Flame className="w-5 h-5 text-orange-400" />
                  <p className="text-white font-semibold">Maintain Your Streak</p>
                </div>
                <p className="text-sm text-zinc-400">
                  You&apos;re on a {progress.current_streak}-day streak! Learn today to keep it going.
                </p>
              </div>
            )}

            {/* Halfway Milestone */}
            {progress.completion_percentage >= 50 && progress.completion_percentage < 100 && (
              <div className="p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                <div className="flex items-center gap-3 mb-2">
                  <Trophy className="w-5 h-5 text-yellow-400" />
                  <p className="text-white font-semibold">Halfway There!</p>
                </div>
                <p className="text-sm text-zinc-400">
                  You&apos;ve completed {progress.completion_percentage}% of the course. Keep going!
                </p>
              </div>
            )}

            {/* Course Complete */}
            {progress.completion_percentage >= 100 && (
              <div className="p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                <div className="flex items-center gap-3 mb-2">
                  <Trophy className="w-5 h-5 text-yellow-400" />
                  <p className="text-white font-semibold">Course Completed!</p>
                </div>
                <p className="text-sm text-zinc-400">
                  Congratulations! You&apos;ve mastered all chapters.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
