'use client';

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Trophy, Target } from 'lucide-react';
import { getMilestones, getAchievableMilestones, Milestone, MilestoneCategory } from '@/lib/api';
import { MilestoneBadge, UpcomingMilestoneBadge } from './MilestoneBadge';
import { LoadingSpinner } from './LoadingSpinner';

interface MilestoneListProps {
  limit?: number;
  showUpcoming?: boolean;
  className?: string;
}

type TabType = 'achieved' | 'upcoming';

export function MilestoneList({
  limit,
  showUpcoming = true,
  className = '',
}: MilestoneListProps) {
  const [activeTab, setActiveTab] = useState<TabType>('achieved');

  const { data: achievedMilestones, isLoading: loadingAchieved } = useQuery({
    queryKey: ['milestones'],
    queryFn: getMilestones,
  });

  const { data: achievableMilestones, isLoading: loadingUpcoming } = useQuery({
    queryKey: ['achievable-milestones'],
    queryFn: getAchievableMilestones,
  });

  if (loadingAchieved || loadingUpcoming) {
    return (
      <div className={`flex items-center justify-center py-12 ${className}`}>
        <LoadingSpinner size="medium" />
      </div>
    );
  }

  // Flatten all upcoming milestones
  const allUpcoming: MilestoneCategory[] = achievableMilestones
    ? [
        ...achievableMilestones.chapters,
        ...achievableMilestones.quizzes,
        ...achievableMilestones.streaks,
        ...achievableMilestones.time,
        ...achievableMilestones.badges,
      ]
        .filter((m) => !m.achieved)
        .sort((a, b) => (b.progress_percent || 0) - (a.progress_percent || 0))
    : [];

  const displayedAchieved = limit
    ? (achievedMilestones || []).slice(0, limit)
    : (achievedMilestones || []);

  const displayedUpcoming = limit
    ? allUpcoming.slice(0, limit)
    : allUpcoming;

  return (
    <div className={className}>
      {/* Tabs */}
      {showUpcoming && (
        <div className="flex items-center gap-1 mb-6 bg-zinc-900/50 rounded-lg p-1 w-fit">
          <button
            onClick={() => setActiveTab('achieved')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
              activeTab === 'achieved'
                ? 'bg-cyan-600 text-white'
                : 'text-zinc-400 hover:text-white'
            }`}
          >
            <Trophy className="h-4 w-4" />
            Achieved ({displayedAchieved?.length || 0})
          </button>
          <button
            onClick={() => setActiveTab('upcoming')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
              activeTab === 'upcoming'
                ? 'bg-cyan-600 text-white'
                : 'text-zinc-400 hover:text-white'
            }`}
          >
            <Target className="h-4 w-4" />
            Upcoming ({displayedUpcoming?.length || 0})
          </button>
        </div>
      )}

      {/* Achieved Milestones */}
      {activeTab === 'achieved' && (
        <div className="space-y-3">
          {!displayedAchieved || displayedAchieved.length === 0 ? (
            <div className="text-center py-12">
              <Trophy className="h-12 w-12 text-zinc-400 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-white mb-2">
                No milestones yet
              </h3>
              <p className="text-zinc-400 text-sm">
                Complete chapters, pass quizzes, and maintain streaks to earn achievements!
              </p>
            </div>
          ) : (
            displayedAchieved?.map((milestone) => (
              <MilestoneBadge
                key={milestone.id}
                milestone={milestone}
                size="md"
              />
            ))
          )}
        </div>
      )}

      {/* Upcoming Milestones */}
      {activeTab === 'upcoming' && showUpcoming && (
        <div className="space-y-3">
          {!displayedUpcoming || displayedUpcoming.length === 0 ? (
            <div className="text-center py-12">
              <Target className="h-12 w-12 text-zinc-400 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-white mb-2">
                All milestones achieved!
              </h3>
              <p className="text-zinc-400 text-sm">
                You've unlocked every achievement. Incredible work!
              </p>
            </div>
          ) : (
            displayedUpcoming?.map((milestone, index) => (
              <UpcomingMilestoneBadge
                key={`${milestone.type}-${index}`}
                milestone={milestone}
                size="md"
              />
            ))
          )}
        </div>
      )}
    </div>
  );
}

// Compact horizontal list variant
export function MilestoneRow({ limit = 5 }: { limit?: number }) {
  const { data: milestones } = useQuery({
    queryKey: ['milestones'],
    queryFn: getMilestones,
  });

  const displayed = milestones?.slice(0, limit) || [];

  if (displayed.length === 0) {
    return null;
  }

  return (
    <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-hide">
      {displayed.map((milestone) => (
        <div
          key={milestone.id}
          className="flex-shrink-0 text-2xl hover:scale-110 transition-transform cursor-pointer"
          title={milestone.display_name}
        >
          {milestone.icon_emoji}
        </div>
      ))}
    </div>
  );
}
