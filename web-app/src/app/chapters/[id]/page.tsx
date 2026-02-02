'use client';

import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useParams, useRouter } from 'next/navigation';
import { useStore } from '@/store/useStore';
import { getChapter, getQuiz, recordActivity } from '@/lib/api';
import { mockChapters } from '@/lib/mockData';
import { Chapter as ChapterType, Quiz as QuizType, Section } from '@/types';
import { Header } from '@/components/Header';
import { ChapterSidebar } from '@/components/ChapterSidebar';
import { ChapterContent } from '@/components/ChapterContent';
import { AIAssistant } from '@/components/AIAssistant';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { Lock } from 'lucide-react';

export default function ChapterPage() {
  const params = useParams();
  const router = useRouter();
  const { currentChapter, setCurrentChapter, user } = useStore();
  const [selectedSection, setSelectedSection] = useState<Section | null>(null);

  const chapterId = params.id as string;

  const { data: chapter, isLoading } = useQuery({
    queryKey: ['chapter', chapterId],
    queryFn: async () => {
      try {
        return await getChapter(chapterId);
      } catch (err) {
        // Use mock data if API fails
        console.log('Using mock data for chapter');
        return mockChapters.find(c => c.id === chapterId) || mockChapters[0];
      }
    },
  });

  const { data: quiz } = useQuery({
    queryKey: ['quiz', chapterId],
    queryFn: () => getQuiz(chapterId),
    enabled: !!chapter,
  });

  useEffect(() => {
    if (chapter) {
      setCurrentChapter(chapter);
      setSelectedSection(chapter.sections[0] || null);
      // Try to record activity (don't fail if it errors)
      recordActivity(chapter.id).catch(() => {});
    }
  }, [chapter, setCurrentChapter]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0B0C10]">
        <Header />
        <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
          <LoadingSpinner size="large" />
        </div>
      </div>
    );
  }

  if (!chapter) {
    return (
      <div className="min-h-screen bg-[#0B0C10]">
        <Header />
        <div className="container mx-auto px-4 py-16 text-center">
          <h1 className="text-2xl font-bold text-white mb-4">Chapter Not Found</h1>
          <button onClick={() => router.push('/')} className="btn-primary">
            Go Home
          </button>
        </div>
      </div>
    );
  }

  // Check if premium content and user is free tier
  if (chapter.access_tier === 'premium' && user?.subscription_type !== 'premium') {
    return (
      <div className="min-h-screen bg-[#0B0C10]">
        <Header />
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-2xl mx-auto text-center">
            <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-zinc-800 border border-zinc-700">
              <Lock className="h-10 w-10 text-zinc-500" />
            </div>
            <h1 className="text-3xl font-bold text-white mb-4">Premium Content</h1>
            <p className="text-zinc-400 mb-8">
              This chapter is part of our premium curriculum. Upgrade to access all 6 chapters and unlock
              advanced features like AI-powered assessments and adaptive learning paths.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="btn-primary">Upgrade to Premium</button>
              <button onClick={() => router.push('/')} className="btn-secondary">
                Back to Free Chapters
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0B0C10]">
      <Header />

      {/* Breadcrumb */}
      <div className="border-b border-zinc-800 bg-[#0B0C10]/50 backdrop-blur">
        <div className="container px-4 py-3">
          <div className="flex items-center gap-2 text-sm text-zinc-400">
            <button onClick={() => router.push('/')} className="hover:text-emerald-400 transition-colors">
              Home
            </button>
            <span>/</span>
            <button onClick={() => router.push('/chapters')} className="hover:text-emerald-400 transition-colors">
              Chapters
            </button>
            <span>/</span>
            <span className="text-white font-medium">{chapter.title}</span>
          </div>
        </div>
      </div>

      {/* Main Content - 3 Column Layout */}
      <div className="container">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Sidebar - Chapter Navigation */}
          <div className="lg:col-span-3 xl:col-span-2">
            <div className="sticky top-20">
              <ChapterSidebar
                chapter={chapter}
                selectedSection={selectedSection}
                onSectionSelect={setSelectedSection}
              />
            </div>
          </div>

          {/* Center - Main Content Area */}
          <div className="lg:col-span-6 xl:col-span-7">
            <div className="py-8">
              {selectedSection && (
                <ChapterContent
                  chapter={chapter}
                  section={selectedSection}
                  onNext={() => {
                    const currentIndex = chapter.sections.findIndex(s => s.id === selectedSection.id);
                    if (currentIndex < chapter.sections.length - 1) {
                      setSelectedSection(chapter.sections[currentIndex + 1]);
                    }
                  }}
                  onPrevious={() => {
                    const currentIndex = chapter.sections.findIndex(s => s.id === selectedSection.id);
                    if (currentIndex > 0) {
                      setSelectedSection(chapter.sections[currentIndex - 1]);
                    }
                  }}
                  hasQuiz={!!quiz}
                />
              )}
            </div>
          </div>

          {/* Right - AI Assistant */}
          <div className="lg:col-span-3 xl:col-span-3">
            <div className="sticky top-20">
              <AIAssistant chapter={chapter} quiz={quiz} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
