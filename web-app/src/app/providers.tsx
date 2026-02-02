'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useEffect, useState } from 'react';
import { useStore } from '@/store/useStore';
import { getCurrentUser } from '@/lib/api';
import { ToastContainer } from '@/hooks/useToast';
import { PWAInstallPrompt, NetworkStatus } from '@/components/PWAInstallPrompt';
import * as serviceWorkerRegistration from '@/lib/serviceWorkerRegistration';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>{children}</AuthProvider>
      <ToastContainer />
      <PWAInstallPrompt />
      <NetworkStatus />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

function AuthProvider({ children }: { children: React.ReactNode }) {
  const { setUser, user } = useStore();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token && !user) {
      getCurrentUser()
        .then(setUser)
        .catch(() => {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        });
    }
  }, [user, setUser]);

  // Register service worker
  useEffect(() => {
    if (typeof window !== 'undefined') {
      serviceWorkerRegistration.register({
        onSuccess: (registration) => {
          console.log('[PWA] Service worker registered successfully');
        },
        onUpdate: (registration) => {
          console.log('[PWA] New content available, refreshing...');
          // Auto-update when new version available
          if (registration.waiting) {
            registration.waiting.postMessage({ type: 'SKIP_WAITING' });
          }
        },
        onOffline: () => {
          console.log('[PWA] App went offline');
        },
        onOnline: () => {
          console.log('[PWA] App back online');
        }
      });
    }
  }, []);

  return <>{children}</>;
}
