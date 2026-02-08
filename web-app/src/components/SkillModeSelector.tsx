'use client';

import { SkillType } from '@/lib/skills/skillDetector';
import { Lightbulb, FileQuestion, Target, Trophy } from 'lucide-react';

interface SkillModeSelectorProps {
  currentMode: SkillType;
  onModeChange: (mode: SkillType) => void;
}

const skillModes = [
  { type: 'explainer' as SkillType, label: 'Explainer', icon: Lightbulb, color: 'text-yellow-400' },
  { type: 'quiz' as SkillType, label: 'Quiz', icon: FileQuestion, color: 'text-blue-400' },
  { type: 'socratic' as SkillType, label: 'Socratic', icon: Target, color: 'text-emerald-400' },
  { type: 'progress' as SkillType, label: 'Progress', icon: Trophy, color: 'text-purple-400' },
];

export function SkillModeSelector({ currentMode, onModeChange }: SkillModeSelectorProps) {
  return (
    <div className="flex gap-1">
      {skillModes.map((mode) => {
        const Icon = mode.icon;
        const isActive = currentMode === mode.type;
        return (
          <button
            key={mode.type}
            onClick={() => onModeChange(mode.type)}
            className={`p-2 rounded-lg transition-all duration-200 ${
              isActive
                ? 'bg-emerald-500/20 text-emerald-400'
                : 'text-zinc-400 hover:text-zinc-300 hover:bg-zinc-800'
            }`}
            title={mode.label}
          >
            <Icon className="h-4 w-4" />
          </button>
        );
      })}
    </div>
  );
}
