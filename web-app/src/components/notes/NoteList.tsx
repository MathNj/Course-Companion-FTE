/**
 * Note List Component
 * Displays user notes with filtering by chapter and tags
 */

'use client';

import { useState, useEffect } from 'react';
import { FileText, Tag, ChevronDown, ChevronUp, Lock, Unlock, Download } from 'lucide-react';
import {
  getNotes,
  getAllTags,
  deleteNote,
  updateNote
} from '@/lib/advancedFeatures';
import type { Note } from '@/lib/advancedFeatures';
import { useToast } from '@/hooks/useToast';
import { NotesExportButton } from '@/components/PDFExportButton';

interface NoteListProps {
  className?: string;
}

export default function NoteList({ className = '' }: NoteListProps) {
  const [notes, setNotes] = useState<Note[]>([]);
  const [allTags, setAllTags] = useState<string[]>([]);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [selectedChapter, setSelectedChapter] = useState<string | null>(null);
  const [expandedNote, setExpandedNote] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isClient, setIsClient] = useState(false);
  const { showToast } = useToast();

  useEffect(() => {
    setIsClient(true);
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedTag, selectedChapter]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const filters: any = {};
      if (selectedTag) filters.tag = selectedTag;
      if (selectedChapter) filters.chapter_id = selectedChapter;

      const { notes: n } = await getNotes(filters);
      const tags = await getAllTags();

      setNotes(n);
      setAllTags(tags);
    } catch (error) {
      console.error('Failed to load notes:', error);
      showToast('Failed to load notes', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (noteId: string) => {
    if (!confirm('Are you sure you want to delete this note?')) return;

    try {
      await deleteNote(noteId);
      setNotes(notes.filter((n) => n.id !== noteId));
      showToast('Note deleted', 'success');
    } catch (error) {
      console.error('Failed to delete note:', error);
      showToast('Failed to delete note', 'error');
    }
  };

  const handleTogglePublic = async (note: Note) => {
    try {
      const updated = await updateNote(note.id, {
        is_public: !note.is_public
      });
      setNotes(notes.map((n) => (n.id === note.id ? updated : n)));
      showToast(`Note is now ${note.is_public ? 'private' : 'public'}`, 'success');
    } catch (error) {
      console.error('Failed to update note:', error);
      showToast('Failed to update note', 'error');
    }
  };

  const chapters = Array.from(new Set(notes.map((n) => n.chapter_id))).sort();

  if (isLoading) {
    return (
      <div className={`animate-pulse ${className}`}>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-32 bg-zinc-800 rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      {/* Header with Export */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-white">My Notes</h2>
        {notes.length > 0 && (
          <NotesExportButton
            notes={notes.map(n => ({
              chapter: n.chapter_id,
              section: n.section_id || undefined,
              content: n.content,
              createdAt: n.created_at,
              tags: n.tags?.map(t => t.name)
            }))}
          />
        )}
      </div>

      {/* Filters */}
      <div className="mb-6 space-y-3">
        {/* Chapter Filter */}
        {chapters.length > 0 && (
          <div>
            <label className="text-sm font-medium text-zinc-400 mb-2 block">
              Filter by Chapter
            </label>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setSelectedChapter(null)}
                className={`
                  px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                  ${selectedChapter === null
                    ? 'bg-blue-600 text-white'
                    : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                  }
                `}
              >
                All Chapters
              </button>
              {chapters.map((chapter) => (
                <button
                  key={chapter}
                  onClick={() => setSelectedChapter(chapter)}
                  className={`
                    px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                    ${selectedChapter === chapter
                      ? 'bg-blue-600 text-white'
                      : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                    }
                  `}
                >
                  Chapter {chapter}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Tag Filter */}
        {allTags.length > 0 && (
          <div>
            <label className="text-sm font-medium text-zinc-400 mb-2 block flex items-center gap-2">
              <Tag className="w-4 h-4" />
              Filter by Tag
            </label>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setSelectedTag(null)}
                className={`
                  px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                  ${selectedTag === null
                    ? 'bg-blue-600 text-white'
                    : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                  }
                `}
              >
                All Tags
              </button>
              {allTags.map((tag) => (
                <button
                  key={tag}
                  onClick={() => setSelectedTag(tag)}
                  className={`
                    px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                    ${selectedTag === tag
                      ? 'bg-blue-600 text-white'
                      : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                    }
                  `}
                >
                  #{tag}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Notes */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-3">
          Notes {notes.length > 0 && `(${notes.length})`}
        </h3>

        {notes.length === 0 ? (
          <div className="text-center py-12 text-zinc-500">
            <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>No notes yet</p>
            <p className="text-sm">Take notes while studying to remember key points</p>
          </div>
        ) : (
          <div className="space-y-3">
            {notes.map((note) => (
              <div
                key={note.id}
                className="p-5 bg-zinc-900 border border-zinc-800 rounded-lg hover:border-zinc-700 transition-all"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="text-white font-medium">
                        Chapter {note.chapter_id}
                        {note.section_id && ` • Section ${note.section_id}`}
                      </h4>
                      {note.is_public ? (
                        <Unlock className="w-4 h-4 text-green-400" />
                      ) : (
                        <Lock className="w-4 h-4 text-zinc-500" />
                      )}
                    </div>
                    <p className="text-xs text-zinc-500">
                      {isClient ? new Date(note.created_at).toLocaleDateString() : '...'}
                      {note.updated_at !== note.created_at && ' • Edited'}
                    </p>
                  </div>
                  <button
                    onClick={() => setExpandedNote(expandedNote === note.id ? null : note.id)}
                    className="p-2 text-zinc-400 hover:text-white transition-colors"
                  >
                    {expandedNote === note.id ? (
                      <ChevronUp className="w-5 h-5" />
                    ) : (
                      <ChevronDown className="w-5 h-5" />
                    )}
                  </button>
                </div>

                {/* Tags */}
                {note.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-3">
                    {note.tags.map((tag) => (
                      <span
                        key={tag.name}
                        className="inline-flex items-center px-2 py-0.5 bg-zinc-800 text-zinc-400 rounded-full text-xs"
                        style={{ borderLeft: `3px solid ${tag.color}` }}
                      >
                        #{tag.name}
                      </span>
                    ))}
                  </div>
                )}

                {/* Content */}
                {expandedNote === note.id && (
                  <div className="mb-4">
                    <p className="text-zinc-300 whitespace-pre-wrap leading-relaxed">
                      {note.content}
                    </p>
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center gap-2 pt-3 border-t border-zinc-800">
                  <button
                    onClick={() => handleTogglePublic(note)}
                    className="text-sm text-zinc-400 hover:text-white transition-colors"
                  >
                    {note.is_public ? 'Make Private' : 'Make Public'}
                  </button>
                  <span className="text-zinc-700">•</span>
                  <button
                    onClick={() => handleDelete(note.id)}
                    className="text-sm text-red-400 hover:text-red-300 transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
