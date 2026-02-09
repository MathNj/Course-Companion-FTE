/**
 * Offline Page
 * Displayed when user is offline
 */

'use client';

import { WifiOff, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';

export default function OfflinePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-950 via-zinc-900 to-zinc-950 flex items-center justify-center p-4">
      <div className="max-w-md w-full text-center animate-fade-in-up">
        {/* Icon */}
        <div className="mb-8 flex justify-center">
          <div className="relative">
            <div className="absolute inset-0 bg-zinc-500/20 rounded-full blur-3xl animate-pulse"></div>
            <div className="relative p-8 bg-zinc-800/50 rounded-full border border-cyan-700">
              <WifiOff className="w-20 h-20 text-zinc-400" />
            </div>
          </div>
        </div>

        {/* Title */}
        <h1 className="text-4xl font-bold text-white mb-4">
          You&apos;re Offline
        </h1>

        {/* Message */}
        <p className="text-xl text-zinc-300 mb-8">
          Please check your internet connection and try again.
        </p>

        {/* Info Cards */}
        <div className="bg-zinc-900/50 rounded-xl p-6 border border-cyan-800 mb-8 text-left">
          <h2 className="text-lg font-bold text-white mb-4">While offline, you can:</h2>
          <ul className="space-y-3">
            <li className="flex items-start gap-3 text-zinc-300">
              <div className="w-6 h-6 rounded-full bg-cyan-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-cyan-400 text-sm">✓</span>
              </div>
              <span>View previously accessed chapters and notes</span>
            </li>
            <li className="flex items-start gap-3 text-zinc-300">
              <div className="w-6 h-6 rounded-full bg-cyan-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-cyan-400 text-sm">✓</span>
              </div>
              <span>Review your progress and bookmarks</span>
            </li>
            <li className="flex items-start gap-3 text-zinc-300">
              <div className="w-6 h-6 rounded-full bg-cyan-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-cyan-400 text-sm">✓</span>
              </div>
              <span>Access your library of saved content</span>
            </li>
          </ul>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button
            onClick={() => window.location.reload()}
            className="bg-cyan-500 hover:bg-cyan-400 text-white font-semibold py-3 px-8 rounded-lg transition-all hover:scale-105"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Try Again
          </Button>
          <Link href="/">
            <Button
              variant="outline"
              className="border-cyan-700 text-zinc-400 hover:text-white hover:border-cyan-600 py-3 px-8 rounded-lg transition-all"
            >
              Go to Home
            </Button>
          </Link>
        </div>

        {/* Auto-retry notice */}
        <p className="mt-8 text-sm text-zinc-500">
          The app will automatically reconnect when you&apos;re back online.
        </p>
      </div>
    </div>
  );
}
