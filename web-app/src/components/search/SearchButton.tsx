'use client';

import { Search } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useSearch } from '@/hooks/useSearch';

interface SearchButtonProps {
  className?: string;
}

export function SearchButton({ className }: SearchButtonProps) {
  const { openSearch } = useSearch();

  return (
    <button
      onClick={openSearch}
      className={`flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 hover:text-white rounded-lg transition-all duration-200 ${className || ''}`}
    >
      <Search className="w-4 h-4" />
      <span className="hidden sm:inline text-sm">Search...</span>
      <kbd className="hidden lg:inline-block px-2 py-0.5 text-xs bg-zinc-700 rounded border border-zinc-600">
        ⌘K
      </kbd>
    </button>
  );
}
