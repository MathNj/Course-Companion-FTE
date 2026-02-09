'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useStore } from '@/store/useStore';
import { Header } from '@/components/Header';
import { Button } from '@/components/ui/Button';
import {
  Check,
  X,
  Crown,
  Zap,
  Trophy,
  Star,
  BookOpen,
  Target,
  Brain,
  HeadphonesIcon,
  Award,
  ChevronRight,
  Sparkles,
  Flame,
} from 'lucide-react';

type BillingPeriod = 'monthly' | 'annual';

interface PricingTier {
  id: string;
  name: string;
  description: string;
  monthlyPrice: number;
  annualPrice: number;
  annualSavings: number;
  icon: any;
  color: string;
  gradient: string;
  features: {
    included: boolean;
    text: string;
    highlight?: boolean;
  }[];
  cta: string;
  popular?: boolean;
}

const PRICING_TIERS: PricingTier[] = [
  {
    id: 'free',
    name: 'Free',
    description: 'Perfect for getting started with Generative AI',
    monthlyPrice: 0,
    annualPrice: 0,
    annualSavings: 0,
    icon: BookOpen,
    color: 'text-zinc-400',
    gradient: 'from-zinc-500 to-zinc-600',
    features: [
      { included: true, text: 'First 3 chapters (Intro, LLMs, Prompting)' },
      { included: true, text: 'Basic quizzes for chapters 1-3' },
      { included: true, text: 'Progress tracking dashboard' },
      { included: true, text: 'Learning streak counter' },
      { included: true, text: 'Chapter bookmarks and notes' },
      { included: false, text: 'Chapters 4-6 (Advanced topics)' },
      { included: false, text: 'Adaptive learning paths' },
      { included: false, text: 'AI-graded open-ended assessments' },
      { included: false, text: 'Priority support' },
    ],
    cta: 'Get Started Free',
  },
  {
    id: 'premium',
    name: 'Premium',
    description: 'Unlock the complete Generative AI curriculum',
    monthlyPrice: 9.99,
    annualPrice: 99.99,
    annualSavings: 20,
    icon: Sparkles,
    color: 'text-purple-400',
    gradient: 'from-purple-500 to-pink-500',
    popular: true,
    features: [
      { included: true, text: 'All 6 chapters of content', highlight: true },
      { included: true, text: 'Advanced quizzes for all chapters', highlight: true },
      { included: true, text: 'Adaptive learning paths', highlight: true },
      { included: true, text: 'AI-graded open-ended assessments', highlight: true },
      { included: true, text: 'Personalized study recommendations' },
      { included: true, text: 'Progress tracking & streaks' },
      { included: true, text: 'Chapter bookmarks and notes' },
      { included: false, text: 'Priority email support' },
      { included: false, text: 'Course completion certificate' },
      { included: false, text: 'Early access to new features' },
    ],
    cta: 'Upgrade to Premium',
  },
  {
    id: 'pro',
    name: 'Pro',
    description: 'For serious learners who want the best',
    monthlyPrice: 19.99,
    annualPrice: 199.99,
    annualSavings: 40,
    icon: Crown,
    color: 'text-yellow-400',
    gradient: 'from-yellow-500 to-orange-500',
    features: [
      { included: true, text: 'Everything in Premium', highlight: true },
      { included: true, text: 'Priority email support', highlight: true },
      { included: true, text: 'Course completion certificate', highlight: true },
      { included: true, text: 'LinkedIn profile badge' },
      { included: true, text: 'Early access to new features' },
      { included: true, text: 'Exclusive workshops & webinars' },
      { included: true, text: '1-on-1 onboarding session' },
      { included: true, text: 'Private community access' },
      { included: true, text: 'Resume review & career coaching' },
    ],
    cta: 'Go Pro',
  },
];

const FAQ_ITEMS = [
  {
    question: 'What\'s the difference between Premium and Pro?',
    answer: 'Premium gives you full access to all course content and AI-powered features. Pro adds career-focused benefits like certificates, priority support, and exclusive access to our private community and workshops.',
  },
  {
    question: 'Can I switch between plans?',
    answer: 'Yes! You can upgrade or downgrade your plan at any time. When upgrading, you\'ll only be charged the prorated difference. When downgrading, you\'ll receive credit toward future billing cycles.',
  },
  {
    question: 'Is there a free trial?',
    answer: 'We offer 3 chapters completely free so you can experience the platform before committing. Plus, when you first upgrade, you get a 7-day free trial of Premium features.',
  },
  {
    question: 'What payment methods do you accept?',
    answer: 'We accept all major credit cards (Visa, Mastercard, American Express) and PayPal. All payments are processed securely through Stripe.',
  },
  {
    question: 'Can I cancel anytime?',
    answer: 'Absolutely! There are no long-term contracts. You can cancel your subscription at any time from your account settings, and you\'ll retain access until the end of your current billing period.',
  },
  {
    question: 'Do you offer discounts for students or teachers?',
    answer: 'Yes! We offer a 50% educational discount for verified students and teachers. Contact us at education@coursecompanion.ai to learn more.',
  },
];

export default function PricingPage() {
  const { user } = useStore();
  const [billingPeriod, setBillingPeriod] = useState<BillingPeriod>('annual');
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const handleUpgrade = (tierId: string) => {
    if (!user) {
      router.push('/register');
      return;
    }
    // Redirect to checkout page with tier parameter
    router.push(`/payment/checkout?tier=${tierId}&period=${billingPeriod}`);
  };

  return (
    <div className="min-h-screen bg-[#0B0C10]">
      <Header />

      {/* Hero Section */}
      <div className="border-b border-zinc-800 bg-[#0B0C10]/50 backdrop-blur">
        <div className="container px-4 py-16">
          {/* Breadcrumb */}
          <div className="flex items-center gap-2 text-sm text-zinc-400 mb-6">
            <Link href="/" className="hover:text-emerald-400 transition-colors">Home</Link>
            <span>/</span>
            <span className="text-white font-medium">Pricing</span>
          </div>

          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-4">
              Choose Your Learning Path
            </h1>
            <p className="text-xl text-zinc-400 mb-8">
              Invest in your future with our comprehensive Generative AI curriculum
            </p>

            {/* Billing Toggle */}
            <div className="flex items-center justify-center gap-4">
              <button
                onClick={() => setBillingPeriod('monthly')}
                className={`text-sm font-medium transition-colors ${
                  billingPeriod === 'monthly'
                    ? 'text-white'
                    : 'text-zinc-400 hover:text-white'
                }`}
              >
                Monthly
              </button>
              <button
                onClick={() => setBillingPeriod('annual')}
                className={`relative px-6 py-2 rounded-full text-sm font-medium transition-all ${
                  billingPeriod === 'annual'
                    ? 'bg-emerald-600 text-white'
                    : 'bg-zinc-800 text-zinc-400 hover:text-white'
                }`}
              >
                Annual
                {billingPeriod === 'annual' && (
                  <span className="absolute -top-3 -right-2 bg-yellow-500 text-white text-xs px-2 py-0.5 rounded-full font-bold">
                    Save 20%
                  </span>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Pricing Cards */}
      <div className="container px-4 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {PRICING_TIERS.map((tier) => {
            const Icon = tier.icon;
            const price = billingPeriod === 'annual' ? tier.annualPrice / 12 : tier.monthlyPrice;
            const savings = billingPeriod === 'annual' && tier.annualSavings > 0;

            return (
              <div
                key={tier.id}
                className={`relative rounded-2xl p-8 transition-all duration-300 ${
                  tier.popular
                    ? 'bg-gradient-to-b from-purple-900/50 to-zinc-900 border-2 border-purple-500/50 shadow-xl shadow-purple-500/10 scale-105'
                    : 'bg-zinc-900 border border-zinc-800 hover:border-zinc-700'
                }`}
              >
                {tier.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <span className="bg-gradient-to-r from-purple-600 to-pink-600 text-white text-sm font-semibold px-4 py-1 rounded-full flex items-center gap-1">
                      <Flame className="h-4 w-4" />
                      Most Popular
                    </span>
                  </div>
                )}

                {/* Header */}
                <div className="text-center mb-6">
                  <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${tier.gradient} mb-4`}>
                    <Icon className={`h-8 w-8 text-white`} />
                  </div>
                  <h3 className={`text-2xl font-bold text-white mb-2`}>
                    {tier.name}
                  </h3>
                  <p className="text-sm text-zinc-400">{tier.description}</p>
                </div>

                {/* Price */}
                <div className="text-center mb-6">
                  <div className="flex items-baseline justify-center gap-1">
                    <span className="text-4xl font-bold text-white">
                      ${price.toFixed(0)}
                    </span>
                    <span className="text-zinc-400">/month</span>
                  </div>
                  {savings && (
                    <p className="text-sm text-emerald-400 mt-1">
                      Save ${tier.annualSavings}/year with annual billing
                    </p>
                  )}
                </div>

                {/* Features */}
                <ul className="space-y-3 mb-8">
                  {tier.features.map((feature, index) => (
                    <li key={index} className="flex items-start gap-3">
                      {feature.included ? (
                        <Check className="h-5 w-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                      ) : (
                        <X className="h-5 w-5 text-zinc-600 flex-shrink-0 mt-0.5" />
                      )}
                      <span
                        className={`text-sm ${
                          feature.highlight
                            ? 'text-white font-medium'
                            : feature.included
                            ? 'text-zinc-300'
                            : 'text-zinc-600'
                        }`}
                      >
                        {feature.text}
                      </span>
                    </li>
                  ))}
                </ul>

                {/* CTA */}
                <button
                  onClick={() => handleUpgrade(tier.id)}
                  className={`w-full py-3 rounded-lg font-semibold transition-all ${
                    tier.popular
                      ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white'
                      : tier.id === 'free'
                      ? 'bg-zinc-800 hover:bg-zinc-700 text-white'
                      : 'bg-emerald-600 hover:bg-emerald-700 text-white'
                  }`}
                >
                  {tier.cta}
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Feature Comparison */}
      <div className="bg-zinc-900/50 border-y border-zinc-800">
        <div className="container px-4 py-16">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            Feature Comparison
          </h2>

          <div className="overflow-x-auto">
            <table className="w-full max-w-4xl mx-auto">
              <thead>
                <tr className="border-b border-zinc-800">
                  <th className="text-left py-4 px-4 text-zinc-400 font-medium">Feature</th>
                  <th className="py-4 px-4 text-zinc-400 font-medium">Free</th>
                  <th className="py-4 px-4 text-purple-400 font-medium">Premium</th>
                  <th className="py-4 px-4 text-yellow-400 font-medium">Pro</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800">
                {[
                  { feature: 'Chapters 1-3 (Foundational)', free: true, premium: true, pro: true },
                  { feature: 'Chapters 4-6 (Advanced)', free: false, premium: true, pro: true },
                  { feature: 'Basic Quizzes', free: true, premium: true, pro: true },
                  { feature: 'Advanced Quizzes', free: false, premium: true, pro: true },
                  { feature: 'Progress Tracking', free: true, premium: true, pro: true },
                  { feature: 'Learning Streaks', free: true, premium: true, pro: true },
                  { feature: 'Adaptive Learning', free: false, premium: true, pro: true },
                  { feature: 'AI-Graded Assessments', free: false, premium: true, pro: true },
                  { feature: 'Priority Support', free: false, premium: false, pro: true },
                  { feature: 'Completion Certificate', free: false, premium: false, pro: true },
                  { feature: 'Early Access', free: false, premium: false, pro: true },
                ].map((row, index) => (
                  <tr key={index} className="hover:bg-zinc-800/50">
                    <td className="py-4 px-4 text-white">{row.feature}</td>
                    <td className="py-4 px-4 text-center">
                      {row.free ? <Check className="h-5 w-5 text-emerald-400 mx-auto" /> : <X className="h-5 w-5 text-zinc-600 mx-auto" />}
                    </td>
                    <td className="py-4 px-4 text-center">
                      {row.premium ? <Check className="h-5 w-5 text-emerald-400 mx-auto" /> : <X className="h-5 w-5 text-zinc-600 mx-auto" />}
                    </td>
                    <td className="py-4 px-4 text-center">
                      {row.pro ? <Check className="h-5 w-5 text-emerald-400 mx-auto" /> : <X className="h-5 w-5 text-zinc-600 mx-auto" />}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* FAQ Section */}
      <div className="container px-4 py-16">
        <h2 className="text-3xl font-bold text-white text-center mb-12">
          Frequently Asked Questions
        </h2>

        <div className="max-w-3xl mx-auto space-y-4">
          {FAQ_ITEMS.map((item, index) => (
            <div
              key={index}
              className="bg-zinc-900 rounded-xl border border-zinc-800 overflow-hidden"
            >
              <button
                onClick={() => setOpenFaq(openFaq === index ? null : index)}
                className="w-full flex items-center justify-between p-6 text-left"
              >
                <span className="text-lg font-semibold text-white">{item.question}</span>
                <ChevronRight
                  className={`h-5 w-5 text-zinc-400 transition-transform ${
                    openFaq === index ? 'rotate-90' : ''
                  }`}
                />
              </button>
              {openFaq === index && (
                <div className="px-6 pb-6">
                  <p className="text-zinc-400">{item.answer}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Educational Discount */}
      <div className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 border-y border-zinc-800">
        <div className="container px-4 py-12">
          <div className="max-w-3xl mx-auto text-center">
            <div className="inline-flex p-3 bg-blue-500/20 rounded-xl mb-4">
              <GraduationCap className="h-8 w-8 text-blue-400" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-3">
              Educational Discount Available
            </h3>
            <p className="text-zinc-400 mb-6">
              Students and teachers get 50% off all plans. Verified .edu email address
              or school ID required.
            </p>
            <Button className="bg-blue-600 hover:bg-blue-700">
              Request Educational Discount
            </Button>
          </div>
        </div>
      </div>

      {/* Bottom CTA */}
      <div className="container px-4 py-16">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Master Generative AI?
          </h2>
          <p className="text-zinc-400 mb-8">
            Join thousands of learners who are already building their AI skills
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link href="/library">
              <Button size="lg" className="hover:scale-105 active:scale-95 transition-all">
                <BookOpen className="h-5 w-5 mr-2" />
                Start Learning Free
              </Button>
            </Link>
            <Link href="/register">
              <Button size="lg" variant="outline" className="border-emerald-500 text-emerald-400 hover:bg-emerald-500 hover:text-white hover:scale-105 active:scale-95 transition-all">
                Create Account
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

function GraduationCap(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M22 10v6M2 10l10-5 10-10-5" />
      <path d="M12 12v9" />
      <path d="M12 22l4-4" />
      <path d="M12 22l-4-4" />
    </svg>
  );
}
