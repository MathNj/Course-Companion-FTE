'use client';

import { useState } from 'react';
import { X, Check, Zap, Star, Award, TrendingUp, Crown, Loader } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { createCheckoutSession, redirectToCheckout } from '@/lib/stripe';

interface PremiumUpgradeModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentPlan: 'free' | 'premium';
}

export function PremiumUpgradeModal({
  isOpen,
  onClose,
  currentPlan,
}: PremiumUpgradeModalProps) {
  const [selectedPlan, setSelectedPlan] = useState<'monthly' | 'yearly'>('yearly');
  const [isProcessing, setIsProcessing] = useState(false);

  if (!isOpen) return null;

  const handleUpgrade = async () => {
    setIsProcessing(true);
    try {
      // Create Stripe checkout session
      const { checkout_url } = await createCheckoutSession({ plan: selectedPlan });

      // Redirect to Stripe checkout
      redirectToCheckout(checkout_url);
    } catch (error) {
      console.error('Failed to create checkout session:', error);
      alert('Failed to create checkout session. Please try again.');
      setIsProcessing(false);
    }
  };

  const features = {
    free: [
      { icon: '📚', name: 'Chapters 1-3', description: 'Access to first 3 chapters' },
      { icon: '✅', name: 'Basic Quizzes', description: 'Standard quiz feedback' },
      { icon: '📊', name: 'Progress Tracking', description: 'Basic progress monitoring' },
      { icon: '🔥', name: 'Streaks', description: 'Learning streak tracking' },
      { icon: '❌', name: 'AI Features', description: 'Not available' },
      { icon: '❌', name: 'Advanced Analytics', description: 'Not available' },
    ],
    premium: [
      { icon: '📚', name: 'All 6 Chapters', description: 'Full course access' },
      { icon: '✅', name: 'Advanced Quizzes', description: 'Detailed explanations' },
      { icon: '🤖', name: 'Adaptive Learning', description: 'AI-powered personalized paths' },
      { icon: '📝', name: 'AI Assessments', description: 'Open-ended answer grading' },
      { icon: '📊', name: 'Advanced Analytics', description: 'Detailed performance insights' },
      { icon: '🎯', name: 'Priority Support', description: 'Fast response times' },
    ],
  };

  const monthlyPrice = 9.99;
  const yearlyPrice = 79.99;
  const yearlyDiscount = Math.round(((monthlyPrice * 12 - yearlyPrice) / (monthlyPrice * 12)) * 100);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="relative bg-zinc-900 rounded-2xl border border-zinc-800 max-w-4xl w-full max-h-[90vh] overflow-y-auto animate-fade-in-up">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded-lg transition-all"
          aria-label="Close modal"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="p-8 pb-4 border-b border-zinc-800">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-xl">
              <Crown className="w-8 h-8 text-yellow-400" />
            </div>
            <div>
              <h2 className="text-3xl font-bold text-white">Upgrade to Premium</h2>
              <p className="text-zinc-400 mt-1">
                {currentPlan === 'free'
                  ? 'Unlock your full learning potential'
                  : 'Change your subscription plan'}
              </p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-8">
          {/* Plan Toggle */}
          <div className="flex justify-center mb-8">
            <div className="inline-flex bg-zinc-800 rounded-lg p-1">
              <button
                onClick={() => setSelectedPlan('monthly')}
                className={`px-6 py-2 rounded-md font-semibold transition-all ${
                  selectedPlan === 'monthly'
                    ? 'bg-purple-500 text-white'
                    : 'text-zinc-400 hover:text-white'
                }`}
              >
                Monthly
              </button>
              <button
                onClick={() => setSelectedPlan('yearly')}
                className={`px-6 py-2 rounded-md font-semibold transition-all relative ${
                  selectedPlan === 'yearly'
                    ? 'bg-purple-500 text-white'
                    : 'text-zinc-400 hover:text-white'
                }`}
              >
                Yearly
                <span className="absolute -top-2 -right-2 px-2 py-0.5 bg-emerald-500 text-white text-xs font-bold rounded-full">
                  Save {yearlyDiscount}%
                </span>
              </button>
            </div>
          </div>

          {/* Pricing Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {/* Free Plan */}
            <div className={`p-6 rounded-xl border-2 transition-all ${
              currentPlan === 'free' ? 'border-zinc-700 bg-zinc-800/50' : 'border-zinc-700'
            }`}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-white">Free</h3>
                {currentPlan === 'free' && (
                  <span className="px-3 py-1 bg-zinc-700 text-zinc-300 text-xs font-semibold rounded-full">
                    Current
                  </span>
                )}
              </div>
              <div className="mb-6">
                <span className="text-4xl font-bold text-white">$0</span>
                <span className="text-zinc-400">/month</span>
              </div>
              <ul className="space-y-3">
                {features.free.map((feature, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <span className="text-lg">{feature.icon}</span>
                    <div>
                      <p className={`font-semibold ${feature.icon === '❌' ? 'text-zinc-500' : 'text-white'}`}>
                        {feature.name}
                      </p>
                      <p className="text-sm text-zinc-400">{feature.description}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </div>

            {/* Premium Plan */}
            <div className={`p-6 rounded-xl border-2 transition-all relative ${
              selectedPlan ? 'border-purple-500 bg-purple-500/5' : 'border-zinc-700'
            }`}>
              {yearlyDiscount > 0 && selectedPlan === 'yearly' && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-sm font-bold rounded-full">
                  BEST VALUE
                </div>
              )}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <h3 className="text-xl font-bold text-white">Premium</h3>
                  <Star className="w-5 h-5 text-yellow-400 fill-yellow-400" />
                </div>
                {currentPlan === 'premium' && (
                  <span className="px-3 py-1 bg-purple-500/20 text-purple-400 text-xs font-semibold rounded-full">
                    Current
                  </span>
                )}
              </div>
              <div className="mb-6">
                <span className="text-4xl font-bold text-white">
                  ${selectedPlan === 'monthly' ? monthlyPrice : yearlyPrice}
                </span>
                <span className="text-zinc-400">
                  /{selectedPlan === 'monthly' ? 'month' : 'year'}
                </span>
                {selectedPlan === 'yearly' && (
                  <p className="text-sm text-emerald-400 mt-1">
                    ${(yearlyPrice / 12).toFixed(2)}/month • Save ${yearlyDiscount}
                  </p>
                )}
              </div>
              <ul className="space-y-3">
                {features.premium.map((feature, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold text-white">{feature.name}</p>
                      <p className="text-sm text-zinc-400">{feature.description}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Feature Highlights */}
          <div className="bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/30 rounded-xl p-6 mb-8">
            <h4 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <Zap className="w-5 h-5 text-purple-400" />
              Premium Features
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-start gap-3">
                <TrendingUp className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-white">Adaptive Learning</p>
                  <p className="text-sm text-zinc-400">Personalized study paths</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Star className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-white">AI Assessments</p>
                  <p className="text-sm text-zinc-400">Detailed answer feedback</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Award className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-white">Advanced Analytics</p>
                  <p className="text-sm text-zinc-400">Deep performance insights</p>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4">
            {currentPlan === 'free' ? (
              <>
                <Button
                  onClick={handleUpgrade}
                  disabled={isProcessing}
                  className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-400 hover:to-pink-400 text-white font-semibold py-3 px-6 rounded-lg transition-all hover:scale-105 active:scale-95"
                >
                  {isProcessing ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Crown className="w-5 h-5 mr-2" />
                      Upgrade to Premium
                    </>
                  )}
                </Button>
                <Button
                  onClick={onClose}
                  variant="outline"
                  className="flex-1 border-zinc-700 text-zinc-400 hover:text-white hover:border-zinc-600 py-3 px-6 rounded-lg transition-all"
                >
                  Maybe Later
                </Button>
              </>
            ) : (
              <div className="w-full p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-center">
                <p className="text-emerald-400 font-semibold mb-2">You&apos;re already a Premium member!</p>
                <p className="text-sm text-zinc-400">Manage your subscription in account settings.</p>
              </div>
            )}
          </div>

          {/* Trust Badges */}
          <div className="mt-8 flex flex-wrap justify-center gap-6 text-sm text-zinc-500">
            <div className="flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-400" />
              <span>Cancel anytime</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-400" />
              <span>Secure payment</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-400" />
              <span>30-day guarantee</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
