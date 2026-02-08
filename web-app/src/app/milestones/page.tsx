'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { Trophy, Target, Flame, BookOpen, Clock, Award, Home } from 'lucide-react';
import { getMilestoneSummary, getAchievableMilestones } from '@/lib/api';
import { MilestoneBadge, UpcomingMilestoneBadge } from '@/components/MilestoneBadge';
import { Header } from '@/components/Header';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { useState } from 'react';

type CategoryType = 'all' | 'chapters' | 'quizzes' | 'streaks' | 'time' | 'badges';
type TabType = 'achieved' | 'upcoming';

export default function MilestonesPage() {
  const [activeTab, setActiveTab] = useState<TabType>('achieved');
  const [categoryFilter, setCategoryFilter] = useState<CategoryType>('all');

  const { data: summary, isLoading: loadingSummary } = useQuery({
    queryKey: ['milestone-summary'],
    queryFn: getMilestoneSummary,
  });

  const { data: achievable, isLoading: loadingAchievable } = useQuery({
    queryKey: ['achievable-milestones'],
    queryFn: getAchievableMilestones,
  });

  if (loadingSummary || loadingAchievable) {
    return (
      <div className="min-h-screen bg-[#0B0C10]">
        <Header />
        <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
          <LoadingSpinner size="large" />
        </div>
      </div>
    );
  }

  const recentMilestones = summary?.recent_milestones || [];
  const nextMilestones = summary?.next_milestones || [];

  // Filter milestones by category
  const categoryMap: Record<CategoryType, string[]> = {
    all: [],
    chapters: ['first_chapter', 'three_chapters', 'six_chapters'],
    quizzes: ['first_quiz', 'perfect_quiz', 'all_quizzes_passed'],
    streaks: ['streak_3', 'streak_7', 'streak_14', 'streak_30', 'streak_60', 'streak_100'],
    time: ['first_hour', 'ten_hours', 'hundred_hours'],
    badges: ['quick_learner', 'perfectionist', 'consistent_learner', 'knowledge_seeker'],
  };

  const filteredAchieved = categoryFilter === 'all'
    ? recentMilestones
    : recentMilestones.filter(m => categoryMap[categoryFilter].includes(m.milestone_type));

  // Get all upcoming milestones by category
  const allUpcoming = achievable ? [
    ...achievable.chapters,
    ...achievable.quizzes,
    ...achievable.streaks,
    ...achievable.time,
    ...achievable.badges,
  ].filter(m => !m.achieved) : [];

  const filteredUpcoming = categoryFilter === 'all'
    ? allUpcoming
    : allUpcoming.filter(m => {
        if (categoryFilter === 'chapters') return achievable.chapters.includes(m);
        if (categoryFilter === 'quizzes') return achievable.quizzes.includes(m);
        if (categoryFilter === 'streaks') return achievable.streaks.includes(m);
        if (categoryFilter === 'time') return achievable.time.includes(m);
        if (categoryFilter === 'badges') return achievable.badges.includes(m);
        return true;
      });

  const categories: { key: CategoryType; label: string; icon: any }[] = [
    { key: 'all', label: 'All', icon: Trophy },
    { key: 'chapters', label: 'Chapters', icon: BookOpen },
    { key: 'quizzes', label: 'Quizzes', icon: Target },
    { key: 'streaks', label: 'Streaks', icon: Flame },
    { key: 'time', label: 'Time', icon: Clock },
    { key: 'badges', label: 'Badges', icon: Award },
  ];

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
            <span className="text-white font-medium">Milestones</span>
          </div>

          {/* Title */}
          <div className="flex items-start justify-between mb-6">
            <div>
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-3">
                Achievements
              </h1>
              <p className="text-lg text-zinc-400">
                Track your learning journey and celebrate your progress
              </p>
            </div>
          </div>

          {/* Stats */}
          <div className="flex flex-wrap items-center gap-6">
            <div className="flex items-center gap-2 text-sm">
              <Trophy className="h-4 w-4 text-yellow-400" />
              <span className="text-zinc-400">{summary?.total_achieved || 0} of {summary?.total_possible || 18} milestones</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <Award className="h-4 w-4 text-emerald-400" />
              <span className="text-zinc-400">{summary?.completion_percentage || 0}% complete</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container px-4 py-8">
        {/* Tabs */}
        <div className="flex items-center gap-1 mb-6 bg-zinc-900/50 rounded-lg p-1 w-fit">
          <button
            onClick={() => setActiveTab('achieved')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
              activeTab === 'achieved'
                ? 'bg-emerald-600 text-white'
                : 'text-zinc-400 hover:text-white'
            }`}
          >
            <Trophy className="h-4 w-4" />
            Achieved ({summary?.total_achieved || 0})
          </button>
          <button
            onClick={() => setActiveTab('upcoming')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
              activeTab === 'upcoming'
                ? 'bg-emerald-600 text-white'
                : 'text-zinc-400 hover:text-white'
            }`}
          >
            <Target className="h-4 w-4" />
            Upcoming ({allUpcoming.length})
          </button>
        </div>

        {/* Category Filter */}
        <div className="flex flex-wrap items-center gap-2 mb-6">
          <span className="text-sm text-zinc-400 mr-2">Filter:</span>
          {categories.map((cat) => {
            const Icon = cat.icon;
            return (
              <button
                key={cat.key}
                onClick={() => setCategoryFilter(cat.key)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                  categoryFilter === cat.key
                    ? 'bg-emerald-600 text-white'
                    : 'bg-zinc-800 text-zinc-400 hover:text-white hover:bg-zinc-700'
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                {cat.label}
              </button>
            );
          })}
        </div>

        {/* Achieved Milestones */}
        {activeTab === 'achieved' && (
          <div>
            {filteredAchieved.length === 0 ? (
              <div className="text-center py-16">
                <Trophy className="h-16 w-16 text-zinc-700 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">
                  {categoryFilter === 'all' ? 'No milestones yet' : `No ${categoryFilter} milestones yet`}
                </h3>
                <p className="text-zinc-400 mb-6">
                  Complete chapters, pass quizzes, and maintain streaks to earn achievements!
                </p>
                <Link href="/library">
                  <button className="btn-primary">
                    <BookOpen className="h-4 w-4 mr-2" />
                    Start Learning
                  </button>
                </Link>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredAchieved.map((milestone) => (
                  <MilestoneBadge
                    key={milestone.id}
                    milestone={milestone}
                    size="md"
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Upcoming Milestones */}
        {activeTab === 'upcoming' && (
          <div>
            {filteredUpcoming.length === 0 ? (
              <div className="text-center py-16">
                <Trophy className="h-16 w-16 text-emerald-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">
                  {categoryFilter === 'all' ? 'All milestones achieved!' : `All ${categoryFilter} milestones achieved!`}
                </h3>
                <p className="text-zinc-400">
                  Incredible! You've unlocked every achievement in this category.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredUpcoming.map((milestone, index) => (
                  <UpcomingMilestoneBadge
                    key={`${milestone.type}-${index}`}
                    milestone={milestone}
                    size="md"
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Quick Actions */}
        {activeTab === 'achieved' && filteredAchieved.length > 0 && (
          <div className="mt-12 pt-8 border-t border-zinc-800">
            <h3 className="text-lg font-semibold text-white mb-4">Continue Your Journey</h3>
            <div className="flex flex-wrap gap-3">
              <Link href="/library">
                <button className="btn-primary">
                  <BookOpen className="h-4 w-4 mr-2" />
                  Continue Learning
                </button>
              </Link>
              <Link href="/dashboard">
                <button className="btn-secondary">
                  <Home className="h-4 w-4 mr-2" />
                  Dashboard
                </button>
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
