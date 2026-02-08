'use client';

import { Milestone as MilestoneType } from '@/lib/api';

interface MilestoneBadgeProps {
  milestone: MilestoneType;
  size?: 'sm' | 'md' | 'lg';
  showDate?: boolean;
  showMessage?: boolean;
}

export function MilestoneBadge({
  milestone,
  size = 'md',
  showDate = true,
  showMessage = true,
}: MilestoneBadgeProps) {
  const sizeClasses = {
    sm: 'text-sm p-3',
    md: 'text-base p-4',
    lg: 'text-lg p-5',
  };

  const iconSizes = {
    sm: 'text-2xl',
    md: 'text-3xl',
    lg: 'text-4xl',
  };

  const achievedDate = milestone.achieved_at
    ? new Date(milestone.achieved_at).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      })
    : null;

  return (
    <div
      className={`card-dark rounded-xl ${sizeClasses[size]} transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-emerald-500/10`}
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className={`flex-shrink-0 ${iconSizes[size]} animate-pulse-slow`}>
          {milestone.icon_emoji}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Title */}
          <h3 className="font-bold text-white leading-tight">
            {milestone.display_name}
          </h3>

          {/* Message */}
          {showMessage && milestone.message && (
            <p className="mt-1 text-sm text-zinc-400 line-clamp-2">
              {milestone.message}
            </p>
          )}

          {/* Date */}
          {showDate && achievedDate && (
            <p className="mt-2 text-xs text-zinc-500">
              Achieved {achievedDate}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

// Upcoming milestone variant (shows progress instead of achievement)
interface UpcomingMilestoneBadgeProps {
  milestone: {
    name: string;
    icon: string;
    progress: number;
    total: number;
    description?: string;
  };
  size?: 'sm' | 'md' | 'lg';
}

export function UpcomingMilestoneBadge({
  milestone,
  size = 'md',
}: UpcomingMilestoneBadgeProps) {
  const sizeClasses = {
    sm: 'text-sm p-3',
    md: 'text-base p-4',
    lg: 'text-lg p-5',
  };

  const iconSizes = {
    sm: 'text-2xl',
    md: 'text-3xl',
    lg: 'text-4xl',
  };

  const progressPercent = Math.min(
    Math.round((milestone.progress / milestone.total) * 100),
    99
  );

  return (
    <div
      className={`card-dark rounded-xl ${sizeClasses[size]} opacity-75 hover:opacity-100 transition-opacity duration-300`}
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className={`flex-shrink-0 ${iconSizes[size]} opacity-50`}>
          {milestone.icon}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Title */}
          <h3 className="font-medium text-zinc-300 leading-tight">
            {milestone.name}
          </h3>

          {/* Description */}
          {milestone.description && (
            <p className="mt-1 text-sm text-zinc-500 line-clamp-1">
              {milestone.description}
            </p>
          )}

          {/* Progress Bar */}
          <div className="mt-3">
            <div className="flex items-center justify-between text-xs text-zinc-500 mb-1">
              <span>Progress</span>
              <span>
                {milestone.progress} / {milestone.total}
              </span>
            </div>
            <div className="w-full bg-zinc-800 rounded-full h-2 overflow-hidden">
              <div
                className="bg-gradient-to-r from-emerald-500 to-emerald-400 h-full rounded-full transition-all duration-500 ease-out"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
