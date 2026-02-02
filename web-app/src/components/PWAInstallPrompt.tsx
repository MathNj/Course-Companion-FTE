/**
 * PWA Install Prompt Component
 * Shows a prompt to install the app as a PWA
 */

'use client';

import { useState, useEffect } from 'react';
import { Download, X } from 'lucide-react';
import { Button } from './ui/Button';
import { useStore } from '@/store/useStore';

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

export function PWAInstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [showPrompt, setShowPrompt] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const { user } = useStore();

  useEffect(() => {
    // Check if app is already installed
    const checkInstalled = () => {
      const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
      const isInApp = (window.navigator as any).standalone === true;
      setIsInstalled(isStandalone || isInApp);
    };

    checkInstalled();

    // Listen for beforeinstallprompt event
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      const promptEvent = e as BeforeInstallPromptEvent;
      setDeferredPrompt(promptEvent);

      // Show prompt after a delay (only show to logged-in users)
      if (user && !isInstalled) {
        setTimeout(() => {
          setShowPrompt(true);
        }, 30000); // Show after 30 seconds
      }
    };

    // Listen for app installed event
    const handleAppInstalled = () => {
      setIsInstalled(true);
      setShowPrompt(false);
      setDeferredPrompt(null);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    // Check if prompt was previously dismissed
    const dismissed = localStorage.getItem('pwa-prompt-dismissed');
    if (dismissed) {
      const dismissedTime = parseInt(dismissed);
      const daysSinceDismissed = (Date.now() - dismissedTime) / (1000 * 60 * 60 * 24);
      if (daysSinceDismissed < 30) {
        setShowPrompt(false);
      }
    }

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, [user, isInstalled]);

  const handleInstall = async () => {
    if (!deferredPrompt) {
      return;
    }

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;

    if (outcome === 'accepted') {
      console.log('[PWA] App installed');
    } else {
      console.log('[PWA] Install dismissed');
      // Remember dismissal for 30 days
      localStorage.setItem('pwa-prompt-dismissed', Date.now().toString());
    }

    setShowPrompt(false);
    setDeferredPrompt(null);
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    localStorage.setItem('pwa-prompt-dismissed', Date.now().toString());
  };

  // Don't show if already installed, no prompt available, or user not logged in
  if (isInstalled || !showPrompt || !deferredPrompt || !user) {
    return null;
  }

  return (
    <div className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-96 z-50 animate-fade-in-up">
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 shadow-2xl">
        {/* Close Button */}
        <button
          onClick={handleDismiss}
          className="absolute top-2 right-2 text-zinc-500 hover:text-white transition-colors"
          aria-label="Close"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Content */}
        <div className="flex items-start gap-4">
          {/* Icon */}
          <div className="flex-shrink-0">
            <div className="w-12 h-12 bg-emerald-500/20 rounded-lg flex items-center justify-center">
              <Download className="w-6 h-6 text-emerald-400" />
            </div>
          </div>

          {/* Message */}
          <div className="flex-1 min-w-0">
            <h3 className="text-white font-semibold mb-1">Install Course Companion</h3>
            <p className="text-sm text-zinc-400 mb-3">
              Install our app for faster access and offline support
            </p>

            {/* Install Button */}
            <div className="flex gap-2">
              <Button
                onClick={handleInstall}
                size="sm"
                className="bg-emerald-500 hover:bg-emerald-400 text-white text-sm"
              >
                Install
              </Button>
              <Button
                onClick={handleDismiss}
                variant="ghost"
                size="sm"
                className="text-zinc-400 hover:text-white text-sm"
              >
                Not now
              </Button>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="mt-4 pt-4 border-t border-zinc-800">
          <div className="grid grid-cols-3 gap-2 text-center">
            <div>
              <div className="text-emerald-400 font-semibold">Fast</div>
              <div className="text-xs text-zinc-500">Instant load</div>
            </div>
            <div>
              <div className="text-emerald-400 font-semibold">Offline</div>
              <div className="text-xs text-zinc-500">Works offline</div>
            </div>
            <div>
              <div className="text-emerald-400 font-semibold">Native</div>
              <div className="text-xs text-zinc-500">App-like feel</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Online/Offline Status Indicator
 */
export function NetworkStatus() {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Check initial status
    setIsOnline(navigator.onLine);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (isOnline) {
    return null;
  }

  return (
    <div className="fixed top-20 left-1/2 transform -translate-x-1/2 z-50 animate-fade-in">
      <div className="bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 flex items-center gap-2 shadow-lg">
        <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
        <span className="text-sm text-white">You&apos;re offline</span>
      </div>
    </div>
  );
}
