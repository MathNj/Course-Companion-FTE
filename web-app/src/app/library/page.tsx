/**
 * Library Page
 * User's personal library with bookmarks and notes
 */

'use client';

import { useState } from 'react';
import { Bookmark, FileText, Library, Download } from 'lucide-react';
import { BookmarkList } from '@/components/bookmarks';
import { NoteList } from '@/components/notes';
import { NotesExportButton } from '@/components/PDFExportButton';

export default function LibraryPage() {
  const [activeTab, setActiveTab] = useState<'bookmarks' | 'notes'>('bookmarks');

  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-950 via-zinc-900 to-zinc-950">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Library className="w-8 h-8 text-blue-400" />
            <h1 className="text-3xl font-bold text-white">My Library</h1>
          </div>
          <p className="text-zinc-400">
            Your personal collection of bookmarks and notes
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-8 bg-zinc-900/50 p-1 rounded-lg border border-zinc-800">
          <button
            onClick={() => setActiveTab('bookmarks')}
            className={`
              flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-md font-medium transition-all
              ${activeTab === 'bookmarks'
                ? 'bg-blue-600 text-white'
                : 'text-zinc-400 hover:text-white hover:bg-zinc-800'
              }
            `}
          >
            <Bookmark className="w-5 h-5" />
            Bookmarks
          </button>
          <button
            onClick={() => setActiveTab('notes')}
            className={`
              flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-md font-medium transition-all
              ${activeTab === 'notes'
                ? 'bg-blue-600 text-white'
                : 'text-zinc-400 hover:text-white hover:bg-zinc-800'
              }
            `}
          >
            <FileText className="w-5 h-5" />
            Notes
          </button>
        </div>

        {/* Content */}
        <div className="bg-zinc-900/30 border border-zinc-800 rounded-xl p-6">
          {activeTab === 'bookmarks' ? (
            <BookmarkList />
          ) : (
            <NoteList />
          )}
        </div>
      </div>
    </div>
  );
}
