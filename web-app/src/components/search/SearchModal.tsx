'use client';

import { useState, useEffect, useCallback } from 'react';
import { Search, X, Filter, BookOpen, FileText, Hash, Clock, TrendingUp } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { useRouter } from 'next/navigation';
import debounce from 'lodash.debounce';

interface SearchResult {
  chapter_id: string;
  chapter_title: string;
  section_id: string;
  section_title: string;
  snippet: string;
  relevance_score: number;
  match_count: number;
}

interface SearchFilters {
  chapter_ids?: string[];
  min_relevance?: number;
  sort_by?: 'relevance' | 'chapter_order';
}

interface SearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function SearchModal({ isOpen, onClose }: SearchModalProps) {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<SearchFilters>({
    sort_by: 'relevance',
  });

  // Debounced search function
  const debouncedSearch = useCallback(
    debounce(async (searchQuery: string) => {
      if (!searchQuery.trim() || searchQuery.length < 2) {
        setResults([]);
        setIsSearching(false);
        return;
      }

      setIsSearching(true);
      try {
        const response = await api.get(`/api/v1/search?q=${encodeURIComponent(searchQuery)}`);
        const searchResults = response.data.results || [];

        // Apply filters
        let filteredResults = searchResults;

        // Apply minimum relevance filter
        if (filters.min_relevance) {
          filteredResults = filteredResults.filter(
            (r: SearchResult) => r.relevance_score >= filters.min_relevance!
          );
        }

        // Apply chapter filter
        if (filters.chapter_ids && filters.chapter_ids.length > 0) {
          filteredResults = filteredResults.filter((r: SearchResult) =>
            filters.chapter_ids!.includes(r.chapter_id)
          );
        }

        // Apply sorting
        if (filters.sort_by === 'chapter_order') {
          filteredResults.sort((a: SearchResult, b: SearchResult) => {
            const aNum = parseInt(a.chapter_id.replace('chapter-', ''));
            const bNum = parseInt(b.chapter_id.replace('chapter-', ''));
            return aNum - bNum;
          });
        }

        setResults(filteredResults.slice(0, 10)); // Top 10 results
      } catch (error) {
        console.error('Search failed:', error);
        setResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 300),
    [filters]
  );

  // Handle query change
  useEffect(() => {
    setSelectedIndex(-1);
    debouncedSearch(query);
  }, [query, debouncedSearch]);

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex(prev =>
            prev < results.length - 1 ? prev + 1 : prev
          );
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex(prev => (prev > 0 ? prev - 1 : -1));
          break;
        case 'Enter':
          e.preventDefault();
          if (selectedIndex >= 0 && results[selectedIndex]) {
            const result = results[selectedIndex];
            router.push(`/chapters/${result.chapter_id}`);
            onClose();
          }
          break;
        case 'Escape':
          e.preventDefault();
          onClose();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, results, selectedIndex, router, onClose]);

  const handleResultClick = (result: SearchResult) => {
    router.push(`/chapters/${result.chapter_id}`);
    onClose();
  };

  const highlightMatch = (text: string, query: string) => {
    if (!query) return text;

    const regex = new RegExp(`(${query.split(' ').join('|')})`, 'gi');
    return text.replace(regex, '<mark class="bg-yellow-500/30 text-yellow-300 px-0.5 rounded">$1</mark>');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-3xl mx-4 animate-fade-in-up">
        {/* Search Box */}
        <div className="bg-zinc-900 rounded-t-xl border border-cyan-700/50 p-4">
          <div className="flex items-center gap-3">
            <Search className="w-5 h-5 text-zinc-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search chapters, sections, concepts..."
              className="flex-1 bg-transparent text-white placeholder-zinc-500 outline-none text-lg"
              autoFocus
              autoComplete="off"
            />
            {query && (
              <button
                onClick={() => {
                  setQuery('');
                  setResults([]);
                }}
                className="p-1 hover:bg-zinc-800 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-zinc-400" />
              </button>
            )}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`p-2 rounded-lg transition-colors ${
                showFilters ? 'bg-purple-500/20 text-purple-400' : 'hover:bg-zinc-800 text-zinc-400'
              }`}
            >
              <Filter className="w-5 h-5" />
            </button>
          </div>

          {/* Filters */}
          {showFilters && (
            <div className="mt-4 pt-4 border-t border-cyan-700/50 animate-fade-in">
              <div className="flex gap-4 mb-4">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-zinc-400 mb-2">Sort By</label>
                  <select
                    value={filters.sort_by}
                    onChange={(e) => setFilters({ ...filters, sort_by: e.target.value as any })}
                    className="w-full bg-zinc-800 border border-cyan-700 rounded-lg px-3 py-2 text-white outline-none focus:border-cyan-500"
                  >
                    <option value="relevance">Relevance</option>
                    <option value="chapter_order">Chapter Order</option>
                  </select>
                </div>

                <div className="flex-1">
                  <label className="block text-sm font-medium text-zinc-400 mb-2">Min Relevance</label>
                  <select
                    value={filters.min_relevance || ''}
                    onChange={(e) => setFilters({ ...filters, min_relevance: e.target.value ? parseFloat(e.target.value) : undefined })}
                    className="w-full bg-zinc-800 border border-cyan-700 rounded-lg px-3 py-2 text-white outline-none focus:border-cyan-500"
                  >
                    <option value="">All</option>
                    <option value="50">High (50+)</option>
                    <option value="20">Medium (20+)</option>
                    <option value="10">Low (10+)</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Stats */}
          {query && (
            <div className="mt-3 flex items-center gap-4 text-sm text-zinc-500">
              {isSearching ? (
                <span>Searching...</span>
              ) : (
                <>
                  <span>{results.length} results</span>
                  {results.length > 0 && (
                    <>
                      <span>•</span>
                      <span>Best match: {results[0].relevance_score.toFixed(1)}%</span>
                    </>
                  )}
                </>
              )}
            </div>
          )}
        </div>

        {/* Results */}
        <div className="bg-zinc-900 rounded-b-xl border border-t-0 border-cyan-700/50 max-h-[60vh] overflow-y-auto">
          {isSearching ? (
            <div className="p-8 text-center text-zinc-400">
              <div className="inline-block w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin mb-3"></div>
              <p>Searching...</p>
            </div>
          ) : query && query.length >= 2 && results.length === 0 ? (
            <div className="p-8 text-center">
              <FileText className="w-12 h-12 text-zinc-400 mx-auto mb-4" />
              <p className="text-zinc-400 mb-2">No results found</p>
              <p className="text-sm text-zinc-500">
                Try different keywords or check your spelling
              </p>
            </div>
          ) : !query || query.length < 2 ? (
            <div className="p-8 text-center">
              <Search className="w-12 h-12 text-zinc-400 mx-auto mb-4" />
              <p className="text-zinc-400 mb-2">Search Course Content</p>
              <p className="text-sm text-zinc-500 max-w-md mx-auto">
                Type to search through chapters, sections, and concepts across all course material.
              </p>
              <div className="mt-6 grid grid-cols-2 gap-3 max-w-sm mx-auto text-left">
                <div className="p-3 bg-zinc-800/50 rounded-lg border border-cyan-700">
                  <p className="text-xs text-zinc-500 mb-1">💡 Tip</p>
                  <p className="text-sm text-zinc-400">Use specific terms for better results</p>
                </div>
                <div className="p-3 bg-zinc-800/50 rounded-lg border border-cyan-700">
                  <p className="text-xs text-zinc-500 mb-1">⌨️ Keyboard</p>
                  <p className="text-sm text-zinc-400">↑↓ to navigate, Enter to open</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="divide-y divide-zinc-800">
              {results.map((result, index) => (
                <div
                  key={`${result.chapter_id}-${result.section_id}-${index}`}
                  onClick={() => handleResultClick(result)}
                  className={`p-4 cursor-pointer transition-all ${
                    index === selectedIndex
                      ? 'bg-purple-500/10 border-l-2 border-purple-500'
                      : 'hover:bg-zinc-800 border-l-2 border-transparent'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <BookOpen className="w-5 h-5 text-purple-400 flex-shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="text-sm font-semibold text-white truncate">
                          {result.section_title || 'Untitled Section'}
                        </h4>
                        <span className="px-2 py-0.5 bg-zinc-800 text-xs text-zinc-400 rounded">
                          {result.chapter_title}
                        </span>
                        {result.match_count > 1 && (
                          <span className="px-2 py-0.5 bg-purple-500/20 text-xs text-purple-400 rounded">
                            {result.match_count} matches
                          </span>
                        )}
                      </div>
                      <p
                        className="text-sm text-zinc-400 line-clamp-2"
                        dangerouslySetInnerHTML={{
                          __html: highlightMatch(result.snippet, query),
                        }}
                      />
                      <div className="flex items-center gap-3 mt-2 text-xs text-zinc-500">
                        <span className="flex items-center gap-1">
                          <TrendingUp className="w-3 h-3" />
                          {(result.relevance_score * 100).toFixed(0)}% relevant
                        </span>
                        <Hash className="w-3 h-3" />
                        <span>{result.section_id}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-zinc-900/95 backdrop-blur-sm rounded-b-xl border border-t-0 border-cyan-700/50 p-2 flex items-center justify-between text-xs text-zinc-500">
          <div className="flex items-center gap-3">
            <span>Esc to close</span>
            <span>•</span>
            <span>↑↓ to navigate</span>
            <span>•</span>
            <span>Enter to open</span>
          </div>
          <div className="flex items-center gap-2">
            {query && results.length > 0 && (
              <span>⌘K to search again</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
