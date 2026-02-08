import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, Progress, Chapter } from '@/types';

interface AppState {
  user: User | null;
  progress: Progress | null;
  currentChapter: Chapter | null;
  isLoading: boolean;
  isPremium: boolean;
  showUpgradeModal: boolean;
  setUser: (user: User | null) => void;
  setProgress: (progress: Progress | null) => void;
  setCurrentChapter: (chapter: Chapter | null) => void;
  setLoading: (loading: boolean) => void;
  setIsPremium: (isPremium: boolean) => void;
  setShowUpgradeModal: (show: boolean) => void;
  logout: () => void;
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      user: null,
      progress: null,
      currentChapter: null,
      isLoading: false,
      isPremium: false,
      showUpgradeModal: false,
      setUser: (user) => set({ user, isPremium: user?.subscription_tier === 'premium' || user?.subscription_tier === 'pro' || user?.subscription_tier === 'team' }),
      setProgress: (progress) => set({ progress }),
      setCurrentChapter: (chapter) => set({ currentChapter: chapter }),
      setLoading: (isLoading) => set({ isLoading }),
      setIsPremium: (isPremium) => set({ isPremium }),
      setShowUpgradeModal: (showUpgradeModal) => set({ showUpgradeModal }),
      logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        set({ user: null, progress: null, currentChapter: null, isPremium: false });
      },
    }),
    {
      name: 'course-companion-storage',
      partialize: (state) => ({ user: state.user, progress: state.progress, isPremium: state.isPremium }),
    }
  )
);
