'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useStore } from '@/store/useStore';
import { register } from '@/lib/api';
import { Header } from '@/components/Header';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { BookOpen, Loader2 } from 'lucide-react';

export default function RegisterPage() {
  const router = useRouter();
  const { setUser } = useStore();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // Check if email is already registered
      const checkResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/auth/check-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
        }),
      });

      const data = await checkResponse.json();

      if (data.exists) {
        setError('This email is already registered. Please log in instead.');
        return;
      }

      // Register the user
      const response = await register(email, password);

      const userData = response.data;

      // Store auth tokens
      localStorage.setItem('access_token', userData.access_token);
      localStorage.setItem('refresh_token', userData.refresh_token);

      // Store user email for potential teacher verification
      localStorage.setItem('user_email', email);

      // Set user in store
      setUser(userData);

      // Navigate to library after registration
      router.push('/library');

    } catch (err: any) {
      console.error('Registration error:', err);
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const isValidForm = () => {
    return email.length > 0 &&
           password.length >= 8 &&
           password === confirmPassword &&
           !isLoading;
  };

  return (
    <div className="min-h-screen bg-[#0B0C10]">
      <Header />

      <div className="flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          <Card>
            <CardHeader>
              <CardTitle>Create Your Account</CardTitle>
              <CardDescription>
                Start your learning journey today by creating your free account
              </CardDescription>
            </CardHeader>

            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                {error && (
                  <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                    <p className="text-sm text-red-400">{error}</p>
                  </div>
                )}

                <div className="space-y-4">
                  <label htmlFor="email" className="text-sm font-medium text-zinc-400">
                    Email
                  </label>
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full px-4 py-2.5 rounded-lg border border-cyan-500/30 bg-white placeholder:text-zinc-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                    placeholder="your.email@example.com"
                  />

                  <label htmlFor="password" className="text-sm font-medium text-zinc-400 mt-3">
                    Password
                  </label>
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="w-full px-4 py-2.5 rounded-lg border border-cyan-500/30 bg-white placeholder:text-zinc-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                    placeholder="•••••••••••••••••••••••••••••"
                  />

                  <label htmlFor="confirmPassword" className="text-sm font-medium text-zinc-400 mt-3">
                    Confirm Password
                  </label>
                  <input
                    id="confirmPassword"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    className="w-full px-4 py-2.5 rounded-lg border border-cyan-500/30 bg-white placeholder:text-zinc-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                    placeholder="••••••••••••••••••••••••••••"
                  />

                  <Button
                    type="submit"
                    disabled={!isValidForm() || isLoading}
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Creating account...
                      </>
                    ) : (
                      <>
                        <BookOpen className="h-6 w-6 text-cyan-400" />
                        Create Your Account
                      </>
                    )}
                  </Button>
                </div>
              </form>

              <div className="mt-4 text-center text-sm text-zinc-400">
                  <span className="text-zinc-500">Already have an account? </span>
                  <Link href="/login" className="text-cyan-400 hover:text-cyan-300 font-medium">
                    Sign in instead
                  </Link>
                </div>
              </CardContent>
            </Card>
          </div>

        <div className="mt-8 text-center">
          <p className="text-sm text-zinc-400">
            Or explore our <Link href="/library" className="text-cyan-400 hover:text-cyan-300">free course library</Link> to see what you can learn as a guest.
          </p>
        </div>
      </div>
    </div>
  );
}
