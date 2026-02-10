'use client';

import { useQuery } from '@tanstack/react-query';
import { Target, TrendingUp } from 'lucide-react';
import { getNextMilestones, MilestoneCategory } from '@/lib/api';
import { UpcomingMilestoneBadge } from './MilestoneBadge';
import { LoadingSpinner } from './LoadingSpinner';

interface NextMilestonesProps {
  count?: number;
  className?: string;
}

export function NextMilestones({
  count = 3,
  className = '',
}: NextMilestonesProps) {
  const { data: nextMilestonesData, isLoading } = useQuery({
    queryKey: ['next-milestones', count],
    queryFn: () => getNextMilestones(count),
  });

  const nextMilestones = nextMilestonesData?.next_milestones || [];

  if (isLoading) {
    return (
      <div className={`flex items-center justify-center py-8 ${className}`}>
        <LoadingSpinner size="small" />
      </div>
    );
  }

  if (nextMilestones.length === 0) {
    return null;
  }

  return (
    <div className={className}>
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <Target className="h-5 w-5 text-cyan-400" />
        <h3 className="text-lg font-semibold text-white">Next Milestones</h3>
      </div>

      {/* Milestones */}
      <div className="space-y-3">
        {nextMilestones.map((milestone, index) => (
          <UpcomingMilestoneBadge
            key={`${milestone.type}-${index}`}
            milestone={milestone}
            size="md"
          />
        ))}
      </div>

      {/* Motivation */}
      <div className="mt-4 flex items-center gap-2 text-sm text-zinc-400 bg-zinc-900/30 rounded-lg p-3">
        <TrendingUp className="h-4 w-4 text-cyan-400" />
        <span>
          {nextMilestones.length === 1
            ? 'You\'re close to your next achievement!'
            : `You're making progress toward ${nextMilestones.length} milestones!`}
        </span>
      </div>
    </div>
  );
}

// Compact card variant for dashboard
export function NextMilestonesCard({ className = '' }: { className?: string }) {
  const { data: nextMilestonesData, isLoading } = useQuery({
    queryKey: ['next-milestones', 2],
    queryFn: () => getNextMilestones(2),
  });

  const nextMilestones = nextMilestonesData?.next_milestones || [];

  if (isLoading) {
    return (
      <div className={`card-dark p-4 ${className}`}>
        <div className="flex items-center justify-center py-4">
          <LoadingSpinner size="small" />
        </div>
      </div>
    );
  }

  if (nextMilestones.length === 0) {
    return null;
  }

  return (
    <div className={`card-dark p-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Target className="h-4 w-4 text-cyan-400" />
          <h4 className="text-sm font-semibold text-white">Up Next</h4>
        </div>
        <span className="text-xs text-zinc-500">
          {nextMilestones[0].progress_percent || 0}%
        </span>
      </div>

      {/* Top milestone */}
      {nextMilestones[0] && (
        <div className="mb-3">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xl">{nextMilestones[0].icon}</span>
            <span className="text-sm font-medium text-white">
              {nextMilestones[0].name}
            </span>
          </div>
          <div className="w-full bg-zinc-800 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-gradient-to-r from-cyan-500 to-cyan-400 h-full rounded-full transition-all duration-500"
              style={{ width: `${nextMilestones[0].progress_percent || 0}%` }}
            />
          </div>
        </div>
      )}

      {/* Second milestone */}
      {nextMilestones[1] && (
        <div className="pt-3 border-t border-cyan-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-lg opacity-70">{nextMilestones[1].icon}</span>
              <span className="text-xs text-zinc-400">
                {nextMilestones[1].name}
              </span>
            </div>
            <span className="text-xs text-zinc-300">
              {nextMilestones[1].progress_percent || 0}%
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
