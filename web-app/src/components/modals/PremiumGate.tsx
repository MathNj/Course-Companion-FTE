'use client';

import { useState } from 'react';
import { Lock, Crown, Zap } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { PremiumUpgradeModal } from './PremiumUpgradeModal';

interface PremiumGateProps {
  feature?: string;
}

export function PremiumGate({ feature = 'this feature' }: PremiumGateProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <>
      <div className="flex flex-col items-center justify-center p-12 text-center animate-fade-in-up">
        <div className="relative mb-6">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-full blur-3xl"></div>
          <div className="relative p-6 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-full border border-purple-500/30">
            <Lock className="w-12 h-12 text-purple-400" />
          </div>
        </div>

        <h2 className="text-3xl font-bold text-white mb-3">Premium Feature</h2>
        <p className="text-zinc-400 mb-8 max-w-md">
          This feature is available exclusively for paid members. Choose a plan that works for you!
        </p>

        {/* Premium Benefits */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8 max-w-2xl">
          <div className="p-4 bg-zinc-800/50 rounded-lg border border-zinc-700">
            <div className="p-2 bg-purple-500/20 rounded-lg w-fit mb-3">
              <Zap className="w-5 h-5 text-purple-400" />
            </div>
            <p className="font-semibold text-white mb-1">Adaptive Learning</p>
            <p className="text-sm text-zinc-400">Personalized study paths</p>
          </div>

          <div className="p-4 bg-zinc-800/50 rounded-lg border border-zinc-700">
            <div className="p-2 bg-blue-500/20 rounded-lg w-fit mb-3">
              <Crown className="w-5 h-5 text-blue-400" />
            </div>
            <p className="font-semibold text-white mb-1">All 6 Chapters</p>
            <p className="text-sm text-zinc-400">Full course access</p>
          </div>

          <div className="p-4 bg-zinc-800/50 rounded-lg border border-zinc-700">
            <div className="p-2 bg-emerald-500/20 rounded-lg w-fit mb-3">
              <Crown className="w-5 h-5 text-emerald-400" />
            </div>
            <p className="font-semibold text-white mb-1">AI Assessments</p>
            <p className="text-sm text-zinc-400">Detailed answer feedback</p>
          </div>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4">
          <Button
            onClick={() => setIsModalOpen(true)}
            className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-400 hover:to-pink-400 text-white font-semibold py-3 px-8 rounded-lg transition-all hover:scale-105 active:scale-95"
          >
            <Crown className="w-5 h-5 mr-2" />
            View Plans
          </Button>
          <Button
            variant="outline"
            className="border-zinc-700 text-zinc-400 hover:text-white hover:border-zinc-600 py-3 px-8 rounded-lg transition-all"
          >
            Learn More
          </Button>
        </div>

        {/* Trust Indicators */}
        <div className="mt-8 flex flex-wrap justify-center gap-6 text-sm text-zinc-500">
          <div className="flex items-center gap-2">
            <span>✓</span>
            <span>Cancel anytime</span>
          </div>
          <div className="flex items-center gap-2">
            <span>✓</span>
            <span>30-day guarantee</span>
          </div>
          <div className="flex items-center gap-2">
            <span>✓</span>
            <span>Secure payment</span>
          </div>
        </div>
      </div>

      {/* Premium Upgrade Modal */}
      <PremiumUpgradeModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        currentPlan="free"
      />
    </>
  );
}
