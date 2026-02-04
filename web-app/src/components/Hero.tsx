'use client';

import { Sparkles, Crown } from 'lucide-react';
import Link from 'next/link';
import { useStore } from '@/store/useStore';
import { FadeIn, CountUp, StaggerChildren, StaggerItem, Float } from '@/components/animations';

export function Hero() {
  const { isPremium, setShowUpgradeModal } = useStore();

  const handleUpgradeClick = () => {
    if (!isPremium) {
      setShowUpgradeModal(true);
    }
  };

  return (
    <section className="relative overflow-hidden py-24 sm:py-32">
      {/* Animated Background */}
      <div className="absolute inset-0">
        <div className="gradient-radial absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] animate-pulse-glow" />
        <div className="absolute inset-0 bg-[#0B0C10]/80" />
      </div>

      {/* Floating Orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <Float duration={4}>
          <div className="absolute top-20 left-[10%] w-4 h-4 rounded-full bg-emerald-500/20 blur-xl" />
        </Float>
        <Float duration={6}>
          <div className="absolute top-40 right-[15%] w-6 h-6 rounded-full bg-emerald-400/10 blur-xl" style={{ animationDelay: '1s' }} />
        </Float>
        <Float duration={5}>
          <div className="absolute bottom-40 left-[20%] w-3 h-3 rounded-full bg-emerald-300/15 blur-xl" style={{ animationDelay: '2s' }} />
        </Float>
        <Float duration={7}>
          <div className="absolute bottom-20 right-[10%] w-5 h-5 rounded-full bg-emerald-500/10 blur-xl" style={{ animationDelay: '1.5s' }} />
        </Float>
      </div>

      <div className="container relative z-10">
        <StaggerChildren staggerDelay={0.1}>
          <div className="mx-auto max-w-3xl text-center">
            {/* Badge */}
            <StaggerItem>
              <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 px-4 py-2 hover:bg-emerald-500/20 transition-all duration-300 hover:scale-105">
                <Sparkles className="h-4 w-4 text-emerald-400 animate-pulse" />
                <span className="text-sm font-medium text-emerald-400">Generative AI Fundamentals</span>
              </div>
            </StaggerItem>

            {/* Heading */}
            <StaggerItem>
              <h1 className="mb-6 text-5xl font-bold tracking-tight text-white sm:text-6xl lg:text-7xl">
                Master the Future of{' '}
                <span className="bg-gradient-to-r from-emerald-400 to-emerald-600 bg-clip-text text-transparent glow-text gradient-animate">
                  AI Learning
                </span>
              </h1>
            </StaggerItem>

            {/* Subheading */}
            <StaggerItem>
              <p className="mb-10 max-w-2xl text-lg text-zinc-400 sm:text-xl">
                Dive deep into Large Language Models, Prompt Engineering, RAG, Fine-tuning, and more.
                Interactive lessons, quizzes, and personalized learning paths await.
              </p>
            </StaggerItem>

            {/* CTA Buttons */}
            <StaggerItem>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/chapters/chapter-1">
                  <button className="btn-primary glow-box hover:scale-105 active:scale-95 transition-all duration-300 ripple">
                    Start Learning Free
                  </button>
                </Link>
                <button
                  onClick={handleUpgradeClick}
                  className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-400 hover:to-pink-400 text-white font-medium px-6 py-3 rounded-lg transition-all duration-200 hover:scale-105 active:scale-95"
                >
                  <Crown className="inline w-4 h-4 mr-2" />
                  View Plans
                </button>
              </div>
            </StaggerItem>

            {/* Stats */}
            <StaggerItem>
              <div className="mt-16 grid grid-cols-3 gap-8 sm:gap-12">
                <div className="group cursor-pointer">
                  <div className="text-3xl font-bold text-white group-hover:text-emerald-400 transition-colors duration-300">
                    <CountUp end={6} />
                  </div>
                  <div className="text-sm text-zinc-400">Comprehensive Chapters</div>
                </div>
                <div className="group cursor-pointer">
                  <div className="text-3xl font-bold text-white group-hover:text-emerald-400 transition-colors duration-300">
                    <CountUp end={60} suffix="+" />
                  </div>
                  <div className="text-sm text-zinc-400">Quiz Questions</div>
                </div>
                <div className="group cursor-pointer">
                  <div className="text-3xl font-bold text-white group-hover:text-emerald-400 transition-colors duration-300">
                    ∞
                  </div>
                  <div className="text-sm text-zinc-400">Learning Possibilities</div>
                </div>
              </div>
            </StaggerItem>
          </div>
        </StaggerChildren>
      </div>
    </section>
  );
}
// Force refresh
// Trigger recompile
