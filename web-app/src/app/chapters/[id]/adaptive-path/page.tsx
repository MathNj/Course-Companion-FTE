'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useStore } from '@/store/useStore';
import { useParams, useRouter } from 'next/navigation';
import api from '@/lib/api';
import { Header } from '@/components/Header';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { Button } from '@/components/ui/Button';
import {
  Route,
  CheckCircle2,
  Circle,
  ArrowRight,
  BookOpen,
  Target,
  TrendingUp,
  Clock,
  Zap,
  Award,
  AlertCircle,
  Calendar
} from 'lucide-react';

interface AdaptivePathResponse {
  learning_path: {
    current_status: string;
    recommended_next: Array<{
      chapter: number;
      title: string;
      reason: string;
      priority: 'high' | 'medium' | 'low';
      estimated_difficulty: string;
    }>;
    knowledge_gaps: Array<{
      topic: string;
      gap_severity: 'minor' | 'moderate' | 'significant';
      recommended_resources: string[];
    }>;
    study_plan: {
      this_week: string[];
      next_week: string[];
    };
    motivation: string;
  };
  tokens_used: number;
  cost_usd: number;
  generated_at: string;
}

export default function AdaptivePathPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useStore();
  const chapterId = params.id as string;

  const [selectedView, setSelectedView] = useState<'roadmap' | 'gaps' | 'plan'>('roadmap');

  const { data: adaptivePath, isLoading, isError } = useQuery<AdaptivePathResponse>({
    queryKey: ['adaptive-path', chapterId],
    queryFn: async () => {
      const response = await api.post('/api/v2/premium/learning-path/generate', {
        current_chapter_id: parseInt(chapterId.split('-')[1]),
        focus: 'comprehensive',
        include_completed: true,
        learning_style: 'mixed',
      });
      return response.data;
    },
    enabled: !!user && !!chapterId,
    retry: false,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0B0C10]">
        <LoadingSpinner />
      </div>
    );
  }

  if (isError || !adaptivePath) {
    return (
      <div className="min-h-screen bg-[#0B0C10]">
        <Header />
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-2xl mx-auto">
            <div className="bg-zinc-900 rounded-xl p-8 border border-cyan-800">
              <div className="flex items-center gap-3 mb-4">
                <AlertCircle className="w-8 h-8 text-yellow-400" />
                <h1 className="text-2xl font-bold text-white">Adaptive Learning Feature</h1>
              </div>
              <p className="text-zinc-400 mb-6">
                This premium feature uses AI to generate personalized learning paths based on your progress.
              </p>
              <div className="bg-zinc-800 rounded-lg p-6 mb-6">
                <h3 className="text-lg font-semibold text-white mb-3">What it does:</h3>
                <ul className="space-y-2 text-zinc-300">
                  <li>• Analyzes your learning patterns</li>
                  <li>• Identifies knowledge gaps</li>
                  <li>• Creates personalized study plans</li>
                  <li>• Recommends optimal learning order</li>
                </ul>
              </div>
              <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4 mb-6">
                <p className="text-sm text-yellow-400">
                  ⚠️ This feature requires an active premium subscription and backend API connection.
                </p>
              </div>
              <Button onClick={() => router.back()} className="w-full">
                Go Back
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const learningPath = adaptivePath.learning_path;

  return (
    <div className="min-h-screen bg-[#0B0C10]">
      <Header />
      <main className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 animate-fade-in">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">Adaptive Learning Path</h1>
              <p className="text-zinc-400">Personalized learning journey powered by AI</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-zinc-500">Cost</p>
              <p className="text-lg font-bold text-cyan-400">${adaptivePath.cost_usd.toFixed(4)}</p>
              <p className="text-xs text-zinc-500">{adaptivePath.tokens_used} tokens</p>
            </div>
          </div>

          {/* View Tabs */}
          <div className="flex gap-2 border-b border-cyan-800">
            <button
              onClick={() => setSelectedView('roadmap')}
              className={`px-4 py-2 font-semibold transition-colors ${
                selectedView === 'roadmap'
                  ? 'text-cyan-400 border-b-2 border-cyan-400'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              <Route className="w-4 h-4 inline mr-2" />
              Roadmap
            </button>
            <button
              onClick={() => setSelectedView('gaps')}
              className={`px-4 py-2 font-semibold transition-colors ${
                selectedView === 'gaps'
                  ? 'text-cyan-400 border-b-2 border-cyan-400'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              <Target className="w-4 h-4 inline mr-2" />
              Knowledge Gaps
            </button>
            <button
              onClick={() => setSelectedView('plan')}
              className={`px-4 py-2 font-semibold transition-colors ${
                selectedView === 'plan'
                  ? 'text-cyan-400 border-b-2 border-cyan-400'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              <Calendar className="w-4 h-4 inline mr-2" />
              Study Plan
            </button>
          </div>
        </div>

        {/* Motivation Message */}
        <div className="bg-gradient-to-r from-cyan-500/10 to-blue-500/10 rounded-xl p-6 border border-cyan-500/30 mb-8 animate-fade-in-up">
          <div className="flex items-start gap-4">
            <Zap className="w-8 h-8 text-yellow-400 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-bold text-white mb-2">AI Insight</h3>
              <p className="text-zinc-300">{learningPath.motivation}</p>
            </div>
          </div>
        </div>

        {/* Roadmap View */}
        {selectedView === 'roadmap' && (
          <div className="space-y-6 animate-fade-in-up">
            <div className="bg-zinc-900 rounded-xl p-8 border border-cyan-800">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                <Route className="w-6 h-6 text-blue-400" />
                Your Personalized Learning Roadmap
              </h2>
              <p className="text-zinc-400 mb-6">Follow this optimal path based on your progress and learning patterns</p>

              <div className="space-y-4">
                {learningPath.recommended_next.map((item, index) => (
                  <div
                    key={index}
                    className={`flex items-start gap-4 p-6 rounded-lg border transition-all hover-lift ${
                      item.priority === 'high'
                        ? 'bg-cyan-500/10 border-cyan-500/30'
                        : item.priority === 'medium'
                        ? 'bg-blue-500/10 border-blue-500/30'
                        : 'bg-zinc-800 border-cyan-700'
                    }`}
                  >
                    <div className="flex-shrink-0">
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                        item.priority === 'high'
                          ? 'bg-cyan-500/20'
                          : item.priority === 'medium'
                          ? 'bg-blue-500/20'
                          : 'bg-zinc-700'
                      }`}>
                        <span className={`text-2xl font-bold ${
                          item.priority === 'high'
                            ? 'text-cyan-400'
                            : item.priority === 'medium'
                            ? 'text-blue-400'
                            : 'text-zinc-400'
                        }`}>
                          {item.chapter}
                        </span>
                      </div>
                    </div>

                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="text-lg font-bold text-white">{item.title}</h3>
                        <span className={`px-2 py-1 rounded text-xs font-semibold ${
                          item.priority === 'high'
                            ? 'bg-cyan-500/20 text-cyan-400'
                            : item.priority === 'medium'
                            ? 'bg-blue-500/20 text-blue-400'
                            : 'bg-zinc-700 text-zinc-400'
                        }`}>
                          {item.priority} priority
                        </span>
                      </div>
                      <p className="text-zinc-400 mb-3">{item.reason}</p>
                      <div className="flex items-center gap-4 text-sm">
                        <div className="flex items-center gap-1 text-zinc-500">
                          <TrendingUp className="w-4 h-4" />
                          <span>Difficulty: {item.estimated_difficulty}</span>
                        </div>
                        <div className="flex items-center gap-1 text-zinc-500">
                          <Clock className="w-4 h-4" />
                          <span>Est. 30-45 min</span>
                        </div>
                      </div>
                    </div>

                    <Button
                      size="sm"
                      onClick={() => router.push(`/chapters/chapter-${item.chapter}`)}
                      className="flex-shrink-0"
                    >
                      Start
                      <ArrowRight className="ml-2 w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Knowledge Gaps View */}
        {selectedView === 'gaps' && (
          <div className="space-y-6 animate-fade-in-up">
            <div className="bg-zinc-900 rounded-xl p-8 border border-cyan-800">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                <Target className="w-6 h-6 text-purple-400" />
                Knowledge Gap Analysis
              </h2>
              <p className="text-zinc-400 mb-6">Areas where you can strengthen your understanding</p>

              <div className="space-y-4">
                {learningPath.knowledge_gaps.map((gap, index) => (
                  <div
                    key={index}
                    className={`p-6 rounded-lg border ${
                      gap.gap_severity === 'significant'
                        ? 'bg-red-500/10 border-red-500/30'
                        : gap.gap_severity === 'moderate'
                        ? 'bg-yellow-500/10 border-yellow-500/30'
                        : 'bg-blue-500/10 border-blue-500/30'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="text-lg font-bold text-white mb-1">{gap.topic}</h3>
                        <span className={`px-2 py-1 rounded text-xs font-semibold ${
                          gap.gap_severity === 'significant'
                            ? 'bg-red-500/20 text-red-400'
                            : gap.gap_severity === 'moderate'
                            ? 'bg-yellow-500/20 text-yellow-400'
                            : 'bg-blue-500/20 text-blue-400'
                        }`}>
                          {gap.gap_severity} gap
                        </span>
                      </div>
                      <Award className="w-6 h-6 text-zinc-500" />
                    </div>

                    <div className="mb-3">
                      <p className="text-sm text-zinc-400 mb-2">Recommended Resources:</p>
                      <div className="flex flex-wrap gap-2">
                        {gap.recommended_resources.map((resource, i) => (
                          <span
                            key={i}
                            className="px-3 py-1 bg-zinc-800 border border-cyan-700 rounded-full text-sm text-zinc-300"
                          >
                            {resource}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Study Plan View */}
        {selectedView === 'plan' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-fade-in-up">
            {/* This Week */}
            <div className="bg-zinc-900 rounded-xl p-8 border border-cyan-800">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Calendar className="w-5 h-5 text-blue-400" />
                This Week
              </h3>
              <div className="space-y-3">
                {learningPath.study_plan.this_week.map((task, index) => (
                  <div key={index} className="flex items-start gap-3">
                    <CheckCircle2 className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
                    <p className="text-zinc-300">{task}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Next Week */}
            <div className="bg-zinc-900 rounded-xl p-8 border border-cyan-800">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Calendar className="w-5 h-5 text-purple-400" />
                Next Week
              </h3>
              <div className="space-y-3">
                {learningPath.study_plan.next_week.map((task, index) => (
                  <div key={index} className="flex items-start gap-3">
                    <Circle className="w-5 h-5 text-zinc-600 flex-shrink-0 mt-0.5" />
                    <p className="text-zinc-300">{task}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Usage Stats */}
            <div className="md:col-span-2 bg-zinc-900 rounded-xl p-8 border border-cyan-800">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Zap className="w-5 h-5 text-yellow-400" />
                Usage Statistics
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <p className="text-sm text-zinc-500 mb-1">Tokens Used</p>
                  <p className="text-2xl font-bold text-white">{adaptivePath.tokens_used}</p>
                </div>
                <div>
                  <p className="text-sm text-zinc-500 mb-1">Cost</p>
                  <p className="text-2xl font-bold text-cyan-400">${adaptivePath.cost_usd.toFixed(4)}</p>
                </div>
                <div>
                  <p className="text-sm text-zinc-500 mb-1">Generated</p>
                  <p className="text-sm text-white">
                    {new Date(adaptivePath.generated_at).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Regenerate Button */}
        <div className="mt-8 flex justify-center">
          <Button
            onClick={() => window.location.reload()}
            className="hover:scale-105 active:scale-95 transition-all duration-300"
          >
            <Zap className="mr-2 w-4 h-4" />
            Regenerate Path
          </Button>
        </div>
      </main>
    </div>
  );
}
