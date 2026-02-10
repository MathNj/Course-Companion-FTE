'use client';

import { useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useStore } from '@/store/useStore';
import { CheckCircle2 } from 'lucide-react';
import { Header } from '@/components/Header';
import { Button } from '@/components/ui/Button';

function PaymentSuccessContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, setUser } = useStore();

  useEffect(() => {
    // Refresh user data to get premium status
    if (user) {
      // In production, this would fetch fresh user data from API
      // For now, we'll update the local state
      setUser({ ...user, subscription_tier: 'premium' });
    }

    // Redirect to dashboard after 3 seconds
    const timer = setTimeout(() => {
      router.push('/dashboard?premium=true');
    }, 3000);

    return () => clearTimeout(timer);
  }, [user, setUser, router]);

  return (
    <div className="min-h-screen bg-[#0B0C10]">
      <Header />
      <main className="flex items-center justify-center p-4">
        <div className="max-w-md w-full text-center animate-fade-in-up">
          {/* Success Icon */}
          <div className="mb-8 flex justify-center">
            <div className="relative">
              <div className="absolute inset-0 bg-cyan-500/20 rounded-full blur-3xl animate-pulse"></div>
              <div className="relative p-6 bg-cyan-500/10 rounded-full border border-cyan-500/30">
                <CheckCircle2 className="w-20 h-20 text-cyan-400" />
              </div>
            </div>
          </div>

          {/* Success Message */}
          <h1 className="text-4xl font-bold text-white mb-4">
            Welcome to Premium!
          </h1>
          <p className="text-xl text-zinc-300 mb-8">
            Your payment was successful. You now have access to all premium features!
          </p>

          {/* Features Unlocked */}
          <div className="bg-zinc-900 rounded-xl p-6 border border-cyan-800 mb-8">
            <h2 className="text-lg font-bold text-white mb-4">Premium Features Unlocked:</h2>
            <ul className="space-y-3 text-left">
              <li className="flex items-center gap-3 text-zinc-300">
                <CheckCircle2 className="w-5 h-5 text-cyan-400 flex-shrink-0" />
                <span>All 6 chapters of course content</span>
              </li>
              <li className="flex items-center gap-3 text-zinc-300">
                <CheckCircle2 className="w-5 h-5 text-cyan-400 flex-shrink-0" />
                <span>AI-powered adaptive learning paths</span>
              </li>
              <li className="flex items-center gap-3 text-zinc-300">
                <CheckCircle2 className="w-5 h-5 text-cyan-400 flex-shrink-0" />
                <span>LLM-graded assessments with detailed feedback</span>
              </li>
              <li className="flex items-center gap-3 text-zinc-300">
                <CheckCircle2 className="w-5 h-5 text-cyan-400 flex-shrink-0" />
                <span>Advanced analytics and insights</span>
              </li>
            </ul>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              onClick={() => router.push('/dashboard')}
              className="bg-cyan-500 hover:bg-cyan-600 text-white font-semibold py-3 px-8 rounded-lg transition-all hover:scale-105"
            >
              Go to Dashboard
            </Button>
            <Button
              onClick={() => router.push('/library')}
              variant="outline"
              className="border-cyan-700 text-zinc-400 hover:text-white hover:border-cyan-600 py-3 px-8 rounded-lg transition-all"
            >
              Start Learning
            </Button>
          </div>

          {/* Auto-redirect Notice */}
          <p className="mt-8 text-sm text-zinc-500">
            Redirecting to dashboard in a few seconds...
          </p>
        </div>
      </main>
    </div>
  );
}

export default function PaymentSuccessPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#0B0C10] flex items-center justify-center">
        <div className="text-zinc-400">Loading...</div>
      </div>
    }>
      <PaymentSuccessContent />
    </Suspense>
  );
}
