'use client';

import { useEffect, useState, Suspense, use } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useStore } from '@/store/useStore';
import { Header } from '@/components/Header';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { CreditCard, Lock, Shield, Check, Crown, Zap, Sparkles } from 'lucide-react';
import { loadStripe } from '@stripe/stripe-js';

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || '');

const PLAN_DETAILS = {
  premium: {
    name: 'Premium',
    priceId: process.env.NEXT_PUBLIC_STRIPE_PREMIUM_PRICE_ID || 'price_premium',
    monthlyPrice: 9.99,
    annualPrice: 99.99,
    features: [
      'All 6 chapters of content',
      'Advanced quizzes for all chapters',
      'Adaptive learning paths',
      'AI-graded open-ended assessments',
      'Personalized study recommendations',
    ],
    icon: Sparkles,
    color: 'purple',
    gradient: 'from-purple-500 to-pink-500',
  },
  pro: {
    name: 'Pro',
    priceId: process.env.NEXT_PUBLIC_STRIPE_PRO_PRICE_ID || 'price_pro',
    monthlyPrice: 19.99,
    annualPrice: 199.99,
    features: [
      'Everything in Premium',
      'Priority email support',
      'Course completion certificate',
      'LinkedIn profile badge',
      'Early access to new features',
      'Exclusive workshops & webinars',
    ],
    icon: Crown,
    color: 'yellow',
    gradient: 'from-yellow-500 to-orange-500',
  },
};

function CheckoutContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user } = useStore();
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'annual'>(
    (searchParams.get('period') as 'monthly' | 'annual') || 'annual'
  );
  const [tier] = useState<'premium' | 'pro'>(
    (searchParams.get('tier') as 'premium' | 'pro') || 'premium'
  );

  const plan = PLAN_DETAILS[tier];
  const price = billingPeriod === 'annual' ? plan.annualPrice / 12 : plan.monthlyPrice;
  const totalPrice = billingPeriod === 'annual' ? plan.annualPrice : plan.monthlyPrice;

  useEffect(() => {
    if (!user) {
      router.push('/login?redirect=' + encodeURIComponent('/payment/checkout?' + searchParams.toString()));
      return;
    }

    // If already premium, redirect to dashboard
    if (user.subscription_tier === 'premium' || user.subscription_tier === 'pro') {
      router.push('/dashboard');
      return;
    }

    setLoading(false);
  }, [user, router, searchParams]);

  const handleCheckout = async () => {
    if (!user) {
      router.push('/login');
      return;
    }

    setProcessing(true);

    try {
      // Create checkout session
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_URL}/api/v1/payments/create-checkout-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          success_url: `${window.location.origin}/payment/success?tier=${tier}`,
          cancel_url: `${window.location.origin}/payment/cancelled?tier=${tier}`,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create checkout session');
      }

      const { checkout_url } = await response.json();

      // Redirect to Stripe Checkout
      window.location.href = checkout_url;
    } catch (error: any) {
      console.error('Checkout error:', error);
      alert(error.message || 'Failed to initiate checkout. Please try again.');
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0B0C10]">
        <Header />
        <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
          <LoadingSpinner size="large" />
        </div>
      </div>
    );
  }

  const PlanIcon = plan.icon;

  return (
    <div className="min-h-screen bg-[#0B0C10]">
      <Header />

      <main className="container px-4 py-12">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-sm text-zinc-400 mb-8">
          <button onClick={() => router.push('/pricing')} className="hover:text-emerald-400 transition-colors">
            Pricing
          </button>
          <span>/</span>
          <span className="text-white font-medium">Checkout</span>
        </div>

        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Order Summary */}
            <div>
              <h2 className="text-2xl font-bold text-white mb-6">Order Summary</h2>

              {/* Plan Card */}
              <div className={`card-dark p-6 mb-6 border-2 ${
                tier === 'premium' ? 'border-purple-500/50' : 'border-yellow-500/50'
              }`}>
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`p-3 rounded-xl bg-gradient-to-br ${plan.gradient}`}>
                      <PlanIcon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white">{plan.name} Plan</h3>
                      <p className="text-sm text-zinc-400">
                        {billingPeriod === 'annual' ? 'Billed annually' : 'Billed monthly'}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-white">
                      ${totalPrice}
                    </p>
                    {billingPeriod === 'annual' && (
                      <p className="text-xs text-zinc-500">
                        ${plan.monthlyPrice}/mo × 12 months
                      </p>
                    )}
                  </div>
                </div>

                {/* Billing Toggle */}
                <div className="flex items-center justify-center gap-4 p-4 bg-zinc-900 rounded-lg">
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

                {/* Features */}
                <div className="mt-6">
                  <h4 className="text-sm font-medium text-zinc-400 mb-3">Included Features:</h4>
                  <ul className="space-y-2">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm text-zinc-300">
                        <Check className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* User Info */}
              <div className="card-dark p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Account</h3>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center">
                    <span className="text-white font-medium">
                      {user?.email?.[0]?.toUpperCase() || 'U'}
                    </span>
                  </div>
                  <div>
                    <p className="text-white font-medium">{user?.email}</p>
                    <p className="text-sm text-zinc-400 capitalize">{user?.subscription_tier} Plan</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Payment Details */}
            <div>
              <h2 className="text-2xl font-bold text-white mb-6">Payment Details</h2>

              <div className="card-dark p-6">
                {/* Stripe Security Notice */}
                <div className="flex items-center gap-2 mb-6 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
                  <Lock className="w-5 h-5 text-emerald-400" />
                  <p className="text-sm text-emerald-400">
                    Secure payment powered by Stripe
                  </p>
                </div>

                {/* Security Badges */}
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="text-center p-4 bg-zinc-900 rounded-lg">
                    <Shield className="w-8 h-8 text-zinc-400 mx-auto mb-2" />
                    <p className="text-xs text-zinc-500">SSL Secure</p>
                  </div>
                  <div className="text-center p-4 bg-zinc-900 rounded-lg">
                    <CreditCard className="w-8 h-8 text-zinc-400 mx-auto mb-2" />
                    <p className="text-xs text-zinc-500">Card Safe</p>
                  </div>
                  <div className="text-center p-4 bg-zinc-900 rounded-lg">
                    <Zap className="w-8 h-8 text-zinc-400 mx-auto mb-2" />
                    <p className="text-xs text-zinc-500">Instant Access</p>
                  </div>
                </div>

                {/* Price Summary */}
                <div className="border-t border-zinc-800 pt-6 space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-zinc-400">Subtotal</span>
                    <span className="text-white">${totalPrice}</span>
                  </div>
                  {billingPeriod === 'annual' && (
                    <div className="flex justify-between text-sm">
                      <span className="text-zinc-400">Annual Savings</span>
                      <span className="text-emerald-400">-${(plan.monthlyPrice * 12 - plan.annualPrice).toFixed(2)}</span>
                    </div>
                  )}
                  <div className="flex justify-between text-sm">
                    <span className="text-zinc-400">Tax</span>
                    <span className="text-zinc-400">Calculated at checkout</span>
                  </div>
                  <div className="border-t border-zinc-800 pt-3">
                    <div className="flex justify-between">
                      <span className="text-lg font-semibold text-white">Total Due</span>
                      <span className="text-lg font-bold text-white">${totalPrice}</span>
                    </div>
                  </div>
                </div>

                {/* Checkout Button */}
                <Button
                  onClick={handleCheckout}
                  disabled={processing}
                  className={`w-full mt-6 py-4 text-lg font-semibold bg-gradient-to-r ${plan.gradient} hover:scale-105 transition-all`}
                >
                  {processing ? (
                    <>
                      <LoadingSpinner size="small" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <CreditCard className="w-5 h-5 mr-2" />
                      Pay ${totalPrice}
                    </>
                  )}
                </Button>

                {/* Cancel */}
                <button
                  onClick={() => router.push('/pricing')}
                  className="w-full mt-4 text-sm text-zinc-400 hover:text-white transition-colors"
                >
                  Cancel and return to pricing
                </button>

                {/* Guarantee */}
                <div className="mt-6 p-4 bg-zinc-900 rounded-lg border border-zinc-800">
                  <p className="text-sm text-zinc-400 text-center">
                    🛡️ 30-day money-back guarantee. Cancel anytime.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default function CheckoutPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#0B0C10] flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    }>
      <CheckoutContent />
    </Suspense>
  );
}
