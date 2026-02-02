/**
 * Bookmark Button Component
 * Quick bookmark button for chapters and sections
 */

'use client';

import { useState, useEffect } from 'react';
import { Bookmark, BookmarkCheck } from 'lucide-react';
import { createBookmark, deleteBookmark, getBookmarks } from '@/lib/advancedFeatures';
import { useToast } from '@/hooks/useToast';

interface BookmarkButtonProps {
  chapterId: string;
  sectionId?: string;
  title?: string;
  className?: string;
}

export default function BookmarkButton({
  chapterId,
  sectionId,
  title,
  className = ''
}: BookmarkButtonProps) {
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [bookmarkId, setBookmarkId] = useState<string | null>(null);
  const { showToast } = useToast();

  // Check if already bookmarked on mount
  useEffect(() => {
    const checkBookmarkStatus = async () => {
      try {
        const { bookmarks } = await getBookmarks();
        const existing = bookmarks.find(
          (b) => b.chapter_id === chapterId && b.section_id === (sectionId || null)
        );
        if (existing) {
          setIsBookmarked(true);
          setBookmarkId(existing.id);
        }
      } catch (error) {
        console.error('Failed to check bookmark status:', error);
      }
    };

    checkBookmarkStatus();
  }, [chapterId, sectionId]);

  const handleToggleBookmark = async () => {
    setIsLoading(true);

    try {
      if (isBookmarked && bookmarkId) {
        // Remove bookmark
        await deleteBookmark(bookmarkId);
        setIsBookmarked(false);
        setBookmarkId(null);
        showToast('Bookmark removed', 'success');
      } else {
        // Add bookmark
        const bookmark = await createBookmark({
          chapter_id: chapterId,
          section_id: sectionId,
          title: title || `Chapter ${chapterId}${sectionId ? ` - ${sectionId}` : ''}`
        });
        setIsBookmarked(true);
        setBookmarkId(bookmark.id);
        showToast('Bookmark added', 'success');
      }
    } catch (error) {
      console.error('Failed to toggle bookmark:', error);
      showToast('Failed to update bookmark', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      onClick={handleToggleBookmark}
      disabled={isLoading}
      className={`
        flex items-center gap-2 px-4 py-2 rounded-lg
        transition-all duration-200
        ${isBookmarked
          ? 'bg-blue-600 hover:bg-blue-700 text-white'
          : 'bg-zinc-800 hover:bg-zinc-700 text-zinc-300'
        }
        disabled:opacity-50 disabled:cursor-not-allowed
        ${className}
      `}
      title={isBookmarked ? 'Remove bookmark' : 'Add bookmark'}
    >
      {isBookmarked ? (
        <BookmarkCheck className="w-5 h-5" />
      ) : (
        <Bookmark className="w-5 h-5" />
      )}
      <span className="text-sm font-medium">
        {isBookmarked ? 'Bookmarked' : 'Bookmark'}
      </span>
    </button>
  );
}
