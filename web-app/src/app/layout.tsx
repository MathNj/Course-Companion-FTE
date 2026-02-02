import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';
import AIAssistant from '@/components/AIAssistantEmbedded';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Course Companion FTE - Generative AI Fundamentals',
  description: 'Master Generative AI with interactive lessons, quizzes, and personalized learning paths.',
  manifest: '/manifest.json',
  themeColor: '#10B981',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'Course Companion',
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
    userScalable: false,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
