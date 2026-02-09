'use client';

import { useRouter } from 'next/navigation';
import { XCircle } from 'lucide-react';
import { Header } from '@/components/Header';
import { Button } from '@/components/ui/Button';

export default function PaymentCancelledPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-[#0B0C10]">
      <Header />
      <main className="flex items-center justify-center p-4">
        <div className="max-w-md w-full text-center animate-fade-in-up">
          {/* Cancelled Icon */}
          <div className="mb-8 flex justify-center">
            <div className="p-6 bg-red-500/10 rounded-full border border-red-500/30">
              <XCircle className="w-20 h-20 text-red-400" />
            </div>
          </div>

          {/* Message */}
          <h1 className="text-4xl font-bold text-white mb-4">
            Payment Cancelled
          </h1>
          <p className="text-xl text-zinc-300 mb-8">
            No worries! Your payment was cancelled. You can upgrade anytime.
          </p>

          {/* Why Upgrade? */}
          <div className="bg-zinc-900 rounded-xl p-6 border border-cyan-800 mb-8 text-left">
            <h2 className="text-lg font-bold text-white mb-4">Why Go Premium?</h2>
            <ul className="space-y-3">
              <li className="flex items-center gap-3 text-zinc-300">
                <span>📚</span>
                <span>Access all 6 chapters of content</span>
              </li>
              <li className="flex items-center gap-3 text-zinc-300">
                <span>🤖</span>
                <span>AI-powered personalized learning paths</span>
              </li>
              <li className="flex items-center gap-3 text-zinc-300">
                <span>📝</span>
                <span>Detailed AI feedback on your assessments</span>
              </li>
              <li className="flex items-center gap-3 text-zinc-300">
                <span>📊</span>
                <span>Advanced analytics and progress insights</span>
              </li>
            </ul>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              onClick={() => router.push('/pricing')}
              className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-400 hover:to-pink-400 text-white font-semibold py-3 px-8 rounded-lg transition-all hover:scale-105"
            >
              Try Again
            </Button>
            <Button
              onClick={() => router.push('/library')}
              variant="outline"
              className="border-cyan-700 text-zinc-400 hover:text-white hover:border-cyan-600 py-3 px-8 rounded-lg transition-all"
            >
              Continue Free
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
}
