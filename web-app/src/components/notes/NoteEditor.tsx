/**
 * Note Editor Component
 * Modal editor for creating and editing notes
 */

'use client';

import { useState, useEffect } from 'react';
import { X, Tag, Lock, Unlock, Save, Trash2 } from 'lucide-react';
import {
  createNote,
  getNotes,
  updateNote,
  deleteNote,
  getAllTags
} from '@/lib/advancedFeatures';
import type { Note } from '@/lib/advancedFeatures';
import { useToast } from '@/hooks/useToast';

interface NoteEditorProps {
  chapterId: string;
  sectionId?: string;
  onClose: () => void;
}

export function NoteEditor({ chapterId, sectionId, onClose }: NoteEditorProps) {
  const [content, setContent] = useState('');
  const [isPublic, setIsPublic] = useState(false);
  const [tags, setTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState('');
  const [existingNote, setExistingNote] = useState<Note | null>(null);
  const [allTags, setAllTags] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { showToast } = useToast();

  useEffect(() => {
    loadExistingNote();
    loadTags();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadExistingNote = async () => {
    try {
      const { notes } = await getNotes({
        chapter_id: chapterId,
        section_id: sectionId
      });

      if (notes.length > 0) {
        const note = notes[0];
        setExistingNote(note);
        setContent(note.content);
        setIsPublic(note.is_public);
        setTags(note.tags.map((t) => t.name));
      }
    } catch (error) {
      console.error('Failed to load existing note:', error);
    }
  };

  const loadTags = async () => {
    try {
      const tagsList = await getAllTags();
      setAllTags(tagsList);
    } catch (error) {
      console.error('Failed to load tags:', error);
    }
  };

  const handleSave = async () => {
    if (!content.trim()) {
      showToast('Please enter note content', 'error');
      return;
    }

    setIsLoading(true);

    try {
      if (existingNote) {
        await updateNote(existingNote.id, {
          content,
          is_public: isPublic
        });
        showToast('Note updated', 'success');
      } else {
        await createNote({
          chapter_id: chapterId,
          section_id: sectionId,
          content,
          is_public: isPublic,
          tags: tags.length > 0 ? tags : undefined
        });
        showToast('Note created', 'success');
      }
      onClose();
    } catch (error) {
      console.error('Failed to save note:', error);
      showToast('Failed to save note', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!existingNote) return;
    if (!confirm('Are you sure you want to delete this note?')) return;

    setIsLoading(true);

    try {
      await deleteNote(existingNote.id);
      showToast('Note deleted', 'success');
      onClose();
    } catch (error) {
      console.error('Failed to delete note:', error);
      showToast('Failed to delete note', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddTag = () => {
    const tag = tagInput.trim().toLowerCase();
    if (tag && !tags.includes(tag)) {
      setTags([...tags, tag]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter((t) => t !== tagToRemove));
  };

  const handleToggleTag = (tag: string) => {
    if (tags.includes(tag)) {
      handleRemoveTag(tag);
    } else {
      setTags([...tags, tag]);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-zinc-800">
          <h2 className="text-xl font-bold text-white">
            {existingNote ? 'Edit Note' : 'New Note'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 text-zinc-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {/* Context */}
          <div className="text-sm text-zinc-500">
            Chapter {chapterId}
            {sectionId && ` • Section ${sectionId}`}
          </div>

          {/* Textarea */}
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Start writing your note..."
            className="w-full h-64 px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-blue-500 resize-none"
          />

          {/* Tags */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-zinc-400 mb-2">
              <Tag className="w-4 h-4" />
              Tags
            </label>

            {/* Tag Input */}
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                placeholder="Add tag..."
                className="flex-1 px-3 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white text-sm focus:outline-none focus:border-blue-500"
              />
              <button
                onClick={handleAddTag}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg"
              >
                Add
              </button>
            </div>

            {/* Selected Tags */}
            {tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-2">
                {tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center gap-1 px-3 py-1 bg-blue-600/20 text-blue-400 rounded-full text-sm"
                  >
                    #{tag}
                    <button
                      onClick={() => handleRemoveTag(tag)}
                      className="hover:text-white"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}

            {/* All Tags */}
            {allTags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {allTags.map((tag) => (
                  <button
                    key={tag}
                    onClick={() => handleToggleTag(tag)}
                    className={`
                      px-2 py-1 rounded-full text-xs transition-all
                      ${tags.includes(tag)
                        ? 'bg-blue-600 text-white'
                        : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                      }
                    `}
                  >
                    #{tag}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Visibility */}
          <div className="flex items-center justify-between p-4 bg-zinc-800 rounded-lg">
            <div className="flex items-center gap-3">
              {isPublic ? (
                <Unlock className="w-5 h-5 text-green-400" />
              ) : (
                <Lock className="w-5 h-5 text-zinc-400" />
              )}
              <div>
                <div className="text-white font-medium">
                  {isPublic ? 'Public Note' : 'Private Note'}
                </div>
                <div className="text-sm text-zinc-500">
                  {isPublic
                    ? 'Anyone can see this note'
                    : 'Only you can see this note'}
                </div>
              </div>
            </div>
            <button
              onClick={() => setIsPublic(!isPublic)}
              className={`
                px-4 py-2 rounded-lg text-sm font-medium transition-all
                ${isPublic
                  ? 'bg-green-600 hover:bg-green-700 text-white'
                  : 'bg-zinc-700 hover:bg-zinc-600 text-zinc-300'
                }
              `}
            >
              {isPublic ? 'Make Private' : 'Make Public'}
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-zinc-800">
          {existingNote && (
            <button
              onClick={handleDelete}
              disabled={isLoading}
              className="flex items-center gap-2 px-4 py-2 text-red-400 hover:text-red-300 transition-colors disabled:opacity-50"
            >
              <Trash2 className="w-4 h-4" />
              Delete
            </button>
          )}

          <div className="flex items-center gap-3 ml-auto">
            <button
              onClick={onClose}
              disabled={isLoading}
              className="px-6 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={isLoading || !content.trim()}
              className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save className="w-4 h-4" />
              {isLoading ? 'Saving...' : 'Save'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
