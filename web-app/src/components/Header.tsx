'use client';

import Link from 'next/link';
import { useStore } from '@/store/useStore';
import { BookOpen, Flame, Trophy, LogOut, User, Menu, X, BarChart3, TrendingUp, Library } from 'lucide-react';
import { Button } from './ui/Button';
import { useState } from 'react';
import { FadeIn } from '@/components/animations';
import { SearchModal, SearchButton } from '@/components/search';
import { useSearch } from '@/hooks/useSearch';

export function Header() {
  const { user, progress, logout } = useStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { isOpen: isSearchOpen, openSearch, closeSearch } = useSearch();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-zinc-800 bg-[#0B0C10]/95 backdrop-blur supports-[backdrop-filter]:bg-[#0B0C10]/60">
      <div className="container flex h-16 items-center justify-between">
        <Link
          href="/"
          className="flex items-center space-x-2 group"
          onClick={() => setMobileMenuOpen(false)}
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-500/10 border border-emerald-500/20 group-hover:scale-110 group-hover:bg-emerald-500/20 transition-all duration-300">
            <BookOpen className="h-6 w-6 text-emerald-400" />
          </div>
          <span className="text-xl font-bold text-white group-hover:text-emerald-400 transition-colors duration-300">Course Companion</span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-6">
          {/* Search Button */}
          <SearchButton />

          {user ? (
            <>
              {/* Progress Stats */}
              {progress && (
                <div className="flex items-center gap-4 text-sm">
                  <div className="flex items-center gap-1.5 text-zinc-400 hover:text-white transition-colors duration-300 group cursor-default">
                    <Flame className="h-4 w-4 text-orange-400 group-hover:scale-110 transition-transform duration-300" />
                    <span>{progress.current_streak} day streak</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-zinc-400 hover:text-white transition-colors duration-300 group cursor-default">
                    <Trophy className="h-4 w-4 text-emerald-400 group-hover:scale-110 transition-transform duration-300" />
                    <span>{progress.completion_percentage}% complete</span>
                  </div>
                </div>
              )}

              {/* Student Dashboard Link */}
              <Link href="/dashboard">
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-zinc-400 hover:text-white hover:scale-105 active:scale-95 transition-all duration-300"
                >
                  <TrendingUp className="h-4 w-4 mr-2" />
                  Student
                </Button>
              </Link>

              {/* Library Link */}
              <Link href="/library">
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-zinc-400 hover:text-white hover:scale-105 active:scale-95 transition-all duration-300"
                >
                  <Library className="h-4 w-4 mr-2" />
                  Library
                </Button>
              </Link>

              {/* Milestones Link */}
              <Link href="/milestones">
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-zinc-400 hover:text-white hover:scale-105 active:scale-95 transition-all duration-300"
                >
                  <Trophy className="h-4 w-4 mr-2" />
                  Milestones
                </Button>
              </Link>

              {/* Teacher Dashboard Link */}
              <Link href="/teacher">
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-zinc-400 hover:text-white hover:scale-105 active:scale-95 transition-all duration-300"
                >
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Teacher
                </Button>
              </Link>

              {/* User Menu */}
              <div className="flex items-center gap-3">
                <div className="hidden sm:block text-right">
                  <p className="text-sm font-medium text-white">{user.email}</p>
                  <p className="text-xs text-zinc-400 capitalize">{user.subscription_tier}</p>
                </div>
                <div className="h-10 w-10 rounded-full bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center hover:scale-110 transition-transform duration-300 cursor-pointer ring-2 ring-transparent hover:ring-emerald-500/50">
                  <User className="h-5 w-5 text-white" />
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={logout}
                  className="text-zinc-400 hover:text-white hover:scale-110 active:scale-95 transition-all duration-300"
                >
                  <LogOut className="h-4 w-4" />
                </Button>
              </div>
            </>
          ) : (
            <div className="flex items-center gap-3">
              <Link href="/login">
                <Button variant="ghost" size="sm" className="hover:scale-105 active:scale-95 transition-all duration-300">
                  Log In
                </Button>
              </Link>
              <Link href="/register">
                <Button size="sm" className="hover:scale-105 active:scale-95 transition-all duration-300">
                  Sign Up
                </Button>
              </Link>
            </div>
          )}
        </nav>

        {/* Mobile Menu Button */}
        <div className="flex items-center gap-3 md:hidden">
          <SearchButton />
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 text-zinc-400 hover:text-white transition-colors duration-300"
          >
            {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </div>

      {/* Search Modal */}
      <SearchModal isOpen={isSearchOpen} onClose={closeSearch} />

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <FadeIn>
          <div className="md:hidden border-t border-zinc-800 bg-[#0B0C10] py-4">
            <nav className="container flex flex-col gap-4">
              {user ? (
                <>
                  {/* Progress Stats */}
                  {progress && (
                    <div className="flex items-center justify-between text-sm py-2 border-b border-zinc-800">
                      <div className="flex items-center gap-1.5 text-zinc-400">
                        <Flame className="h-4 w-4 text-orange-400" />
                        <span>{progress.current_streak} day streak</span>
                      </div>
                      <div className="flex items-center gap-1.5 text-zinc-400">
                        <Trophy className="h-4 w-4 text-emerald-400" />
                        <span>{progress.completion_percentage}% complete</span>
                      </div>
                    </div>
                  )}

                  {/* Student Dashboard Link */}
                  <Link href="/dashboard" onClick={() => setMobileMenuOpen(false)}>
                    <Button variant="ghost" size="sm" className="justify-start w-full">
                      <TrendingUp className="h-4 w-4 mr-2" />
                      Student
                    </Button>
                  </Link>

                  {/* Library Link */}
                  <Link href="/library" onClick={() => setMobileMenuOpen(false)}>
                    <Button variant="ghost" size="sm" className="justify-start w-full">
                      <Library className="h-4 w-4 mr-2" />
                      Library
                    </Button>
                  </Link>

                  {/* Milestones Link */}
                  <Link href="/milestones" onClick={() => setMobileMenuOpen(false)}>
                    <Button variant="ghost" size="sm" className="justify-start w-full">
                      <Trophy className="h-4 w-4 mr-2" />
                      Milestones
                    </Button>
                  </Link>

                  {/* Teacher Dashboard Link */}
                  <Link href="/teacher" onClick={() => setMobileMenuOpen(false)}>
                    <Button variant="ghost" size="sm" className="justify-start w-full">
                      <BarChart3 className="h-4 w-4 mr-2" />
                      Teacher
                    </Button>
                  </Link>

                  {/* User Info */}
                  <div className="flex items-center gap-3 py-2 border-b border-zinc-800">
                    <div className="h-10 w-10 rounded-full bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center">
                      <User className="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">{user.email}</p>
                      <p className="text-xs text-zinc-400 capitalize">{user.subscription_tier}</p>
                    </div>
                  </div>

                  {/* Logout Button */}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      logout();
                      setMobileMenuOpen(false);
                    }}
                    className="justify-start"
                  >
                    <LogOut className="h-4 w-4 mr-2" />
                    Logout
                  </Button>
                </>
              ) : (
                <div className="flex flex-col gap-2">
                  <Link href="/login" onClick={() => setMobileMenuOpen(false)}>
                    <Button variant="ghost" size="sm" className="justify-start w-full">
                      Log In
                    </Button>
                  </Link>
                  <Link href="/register" onClick={() => setMobileMenuOpen(false)}>
                    <Button size="sm" className="justify-start w-full">
                      Sign Up
                    </Button>
                  </Link>
                </div>
              )}
            </nav>
          </div>
        </FadeIn>
      )}
    </header>
  );
}
