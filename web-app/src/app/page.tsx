'use client';

import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useStore } from '@/store/useStore';
import { getChapters, getProgress } from '@/lib/api';
import { mockChapters } from '@/lib/mockData';
import { Header } from '@/components/Header';
import { Hero } from '@/components/Hero';
import { ChapterGrid } from '@/components/ChapterGrid';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { PremiumUpgradeModal } from '@/components/modals';

export default function HomePage() {
  const { user, setProgress, setLoading, showUpgradeModal, setShowUpgradeModal } = useStore();

  const { data: chapters, isLoading: chaptersLoading } = useQuery({
    queryKey: ['chapters'],
    queryFn: async () => {
      try {
        return await getChapters();
      } catch (err) {
        // Use mock data if API fails
        console.log('Using mock data due to API error');
        return mockChapters;
      }
    },
  });

  const { data: progress } = useQuery({
    queryKey: ['progress'],
    queryFn: getProgress,
    enabled: !!user,
  });

  useEffect(() => {
    if (progress) {
      setProgress(progress);
    }
  }, [progress, setProgress]);

  useEffect(() => {
    setLoading(false);
  }, [setLoading]);

  if (chaptersLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0B0C10]">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0B0C10]">
      <Header />
      <main>
        <Hero />
        <div id="chapters" className="container mx-auto px-4 py-16">
          <div className="mb-12 text-center">
            <h2 className="text-3xl font-bold text-white mb-4 animate-fade-in-up">Course Chapters</h2>
            <p className="text-zinc-400 animate-fade-in-up delay-100">
              Master Generative AI through our comprehensive curriculum
            </p>
          </div>
          <ChapterGrid chapters={chapters || mockChapters} />
        </div>
      </main>

      {/* Premium Upgrade Modal */}
      <PremiumUpgradeModal
        isOpen={showUpgradeModal}
        onClose={() => setShowUpgradeModal(false)}
        currentPlan={user?.subscription_tier || 'free'}
      />
    </div>
  );
}
