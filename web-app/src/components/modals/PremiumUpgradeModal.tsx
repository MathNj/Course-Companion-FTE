'use client';

import { useState } from 'react';
import { X, Check, Zap, Star, Award, TrendingUp, Crown, Loader } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { createCheckoutSession, redirectToCheckout } from '@/lib/stripe';

interface PremiumUpgradeModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentPlan: 'free' | 'premium' | 'pro' | 'team';
}

export function PremiumUpgradeModal({
  isOpen,
  onClose,
  currentPlan,
}: PremiumUpgradeModalProps) {
  const [selectedPlan, setSelectedPlan] = useState<'free' | 'premium' | 'pro' | 'team'>('premium');
  const [isProcessing, setIsProcessing] = useState(false);

  if (!isOpen) return null;

  const handleUpgrade = async (plan: 'premium' | 'pro' | 'team') => {
    setIsProcessing(true);
    try {
      // Create Stripe checkout session
      const { checkout_url } = await createCheckoutSession({ plan });

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
      { icon: '🤖', name: 'ChatGPT Tutoring', description: 'AI-powered learning assistant' },
      { icon: '🔥', name: 'Streaks', description: 'Learning streak tracking' },
      { icon: '❌', name: 'AI Features', description: 'Not available' },
      { icon: '❌', name: 'Advanced Analytics', description: 'Not available' },
    ],
    premium: [
      { icon: '📚', name: 'All 6 Chapters', description: 'Full course access' },
      { icon: '✅', name: 'All Quizzes', description: 'Complete quiz access' },
      { icon: '🤖', name: 'ChatGPT Tutoring', description: 'AI-powered learning assistant' },
      { icon: '📊', name: 'Progress Tracking', description: 'Basic progress monitoring' },
      { icon: '❌', name: 'Adaptive Learning', description: 'Not available' },
      { icon: '❌', name: 'AI Assessments', description: 'Not available' },
    ],
    pro: [
      { icon: '📚', name: 'All 6 Chapters', description: 'Full course access' },
      { icon: '✅', name: 'All Quizzes', description: 'Complete quiz access' },
      { icon: '🤖', name: 'Adaptive Learning', description: 'AI-powered personalized paths' },
      { icon: '📝', name: 'AI Assessments', description: 'Open-ended answer grading' },
      { icon: '📊', name: 'Progress Tracking', description: 'Detailed progress monitoring' },
      { icon: '❌', name: 'Team Features', description: 'Not available' },
    ],
    team: [
      { icon: '📚', name: 'All 6 Chapters', description: 'Full course access' },
      { icon: '✅', name: 'All Quizzes', description: 'Complete quiz access' },
      { icon: '🤖', name: 'Adaptive Learning', description: 'AI-powered personalized paths' },
      { icon: '📝', name: 'AI Assessments', description: 'Open-ended answer grading' },
      { icon: '👥', name: 'Team Analytics', description: 'Multi-user performance insights' },
      { icon: '🎯', name: 'Priority Support', description: 'Dedicated support' },
    ],
  };

  const prices = {
    free: { monthly: 0, yearly: 0 },
    premium: { monthly: 9.99, yearly: 79.99 },
    pro: { monthly: 19.99, yearly: 159.99 },
    team: { monthly: 49.99, yearly: 499.99 },
  };

  const selectedPlanPrice = prices[selectedPlan as keyof typeof prices];
  const yearlyDiscount = selectedPlanPrice.monthly > 0
    ? Math.round(((selectedPlanPrice.monthly * 12 - selectedPlanPrice.yearly) / (selectedPlanPrice.monthly * 12)) * 100)
    : 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="relative bg-zinc-900 rounded-2xl border border-cyan-700/50 max-w-4xl w-full max-h-[90vh] overflow-y-auto animate-fade-in-up">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded-lg transition-all"
          aria-label="Close modal"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="p-8 pb-4 border-b border-cyan-700/50">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-xl">
              <Crown className="w-8 h-8 text-yellow-400" />
            </div>
            <div>
              <h2 className="text-3xl font-bold text-white">Choose Your Plan</h2>
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
          {/* Pricing Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {/* Free Plan */}
            <div className={`p-6 rounded-xl border-2 transition-all ${
              currentPlan === 'free' ? 'border-cyan-700 bg-zinc-800/50' : 'border-cyan-700'
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
              selectedPlan === 'premium' ? 'border-purple-500 bg-purple-500/5' : 'border-cyan-700'
            }`}>
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
                <span className="text-4xl font-bold text-white">${prices.premium.monthly}</span>
                <span className="text-zinc-400">/month</span>
              </div>
              <ul className="space-y-3">
                {features.premium.map((feature, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold text-white">{feature.name}</p>
                      <p className="text-sm text-zinc-400">{feature.description}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </div>

            {/* Pro Plan */}
            <div className={`p-6 rounded-xl border-2 transition-all relative ${
              selectedPlan === 'pro' ? 'border-blue-500 bg-blue-500/5' : 'border-cyan-700'
            }`}>
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-blue-500 to-cyan-500 text-white text-sm font-bold rounded-full">
                POPULAR
              </div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <h3 className="text-xl font-bold text-white">Pro</h3>
                  <TrendingUp className="w-5 h-5 text-blue-400" />
                </div>
                {currentPlan === 'pro' && (
                  <span className="px-3 py-1 bg-blue-500/20 text-blue-400 text-xs font-semibold rounded-full">
                    Current
                  </span>
                )}
              </div>
              <div className="mb-6">
                <span className="text-4xl font-bold text-white">${prices.pro.monthly}</span>
                <span className="text-zinc-400">/month</span>
              </div>
              <ul className="space-y-3">
                {features.pro.map((feature, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold text-white">{feature.name}</p>
                      <p className="text-sm text-zinc-400">{feature.description}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </div>

            {/* Team Plan */}
            <div className={`p-6 rounded-xl border-2 transition-all relative ${
              selectedPlan === 'team' ? 'border-cyan-500 bg-cyan-500/5' : 'border-cyan-700'
            }`}>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <h3 className="text-xl font-bold text-white">Team</h3>
                  <Award className="w-5 h-5 text-cyan-400" />
                </div>
                {currentPlan === 'team' && (
                  <span className="px-3 py-1 bg-cyan-500/20 text-cyan-400 text-xs font-semibold rounded-full">
                    Current
                  </span>
                )}
              </div>
              <div className="mb-6">
                <span className="text-4xl font-bold text-white">${prices.team.monthly}</span>
                <span className="text-zinc-400">/month</span>
              </div>
              <ul className="space-y-3">
                {features.team.map((feature, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
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
                <Award className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-white">Advanced Analytics</p>
                  <p className="text-sm text-zinc-400">Deep performance insights</p>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-4">
            {currentPlan === 'free' ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Button
                  onClick={() => handleUpgrade('premium')}
                  disabled={isProcessing}
                  className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold py-3 px-6 rounded-lg transition-all hover:scale-105 active:scale-95"
                >
                  {isProcessing && selectedPlan === 'premium' ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Star className="w-5 h-5 mr-2" />
                      Upgrade to Premium
                    </>
                  )}
                </Button>
                <Button
                  onClick={() => handleUpgrade('pro')}
                  disabled={isProcessing}
                  className="bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-semibold py-3 px-6 rounded-lg transition-all hover:scale-105 active:scale-95"
                >
                  {isProcessing && selectedPlan === 'pro' ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <TrendingUp className="w-5 h-5 mr-2" />
                      Upgrade to Pro
                    </>
                  )}
                </Button>
                <Button
                  onClick={() => handleUpgrade('team')}
                  disabled={isProcessing}
                  className="bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-600 hover:to-teal-600 text-white font-semibold py-3 px-6 rounded-lg transition-all hover:scale-105 active:scale-95"
                >
                  {isProcessing && selectedPlan === 'team' ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Award className="w-5 h-5 mr-2" />
                      Upgrade to Team
                    </>
                  )}
                </Button>
              </div>
            ) : (
              <div className="w-full p-4 bg-cyan-500/10 border border-cyan-500/30 rounded-lg text-center">
                <p className="text-cyan-400 font-semibold mb-2">
                  You&apos;re already a {currentPlan.charAt(0).toUpperCase() + currentPlan.slice(1)} member!
                </p>
                <p className="text-sm text-zinc-400">Manage your subscription in account settings.</p>
              </div>
            )}
          </div>

          {/* Trust Badges */}
          <div className="mt-8 flex flex-wrap justify-center gap-6 text-sm text-zinc-500">
            <div className="flex items-center gap-2">
              <Check className="w-4 h-4 text-cyan-400" />
              <span>Cancel anytime</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-4 h-4 text-cyan-400" />
              <span>Secure payment</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-4 h-4 text-cyan-400" />
              <span>30-day guarantee</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
