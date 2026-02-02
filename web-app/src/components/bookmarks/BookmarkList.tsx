/**
 * Bookmark List Component
 * Displays user bookmarks with filtering and organization
 */

'use client';

import { useState, useEffect } from 'react';
import { Bookmark, Folder, Trash2, Edit2, Plus } from 'lucide-react';
import {
  getBookmarks,
  getFolders,
  deleteBookmark,
  updateBookmark,
  createFolder,
  deleteFolder
} from '@/lib/advancedFeatures';
import type { Bookmark as BookmarkType, Folder as FolderType } from '@/lib/advancedFeatures';
import { useToast } from '@/hooks/useToast';

interface BookmarkListProps {
  className?: string;
}

export default function BookmarkList({ className = '' }: BookmarkListProps) {
  const [bookmarks, setBookmarks] = useState<BookmarkType[]>([]);
  const [folders, setFolders] = useState<FolderType[]>([]);
  const [selectedFolder, setSelectedFolder] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [showNewFolder, setShowNewFolder] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const { showToast } = useToast();

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedFolder]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const { bookmarks: b } = await getBookmarks(selectedFolder || undefined);
      const { folders: f } = await getFolders();
      setBookmarks(b);
      setFolders(f);
    } catch (error) {
      console.error('Failed to load bookmarks:', error);
      showToast('Failed to load bookmarks', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (bookmarkId: string) => {
    if (!confirm('Are you sure you want to delete this bookmark?')) return;

    try {
      await deleteBookmark(bookmarkId);
      setBookmarks(bookmarks.filter((b) => b.id !== bookmarkId));
      showToast('Bookmark deleted', 'success');
    } catch (error) {
      console.error('Failed to delete bookmark:', error);
      showToast('Failed to delete bookmark', 'error');
    }
  };

  const handleUpdate = async (bookmarkId: string) => {
    try {
      await updateBookmark(bookmarkId, { title: editTitle });
      setBookmarks(
        bookmarks.map((b) =>
          b.id === bookmarkId ? { ...b, title: editTitle } : b
        )
      );
      setEditingId(null);
      showToast('Bookmark updated', 'success');
    } catch (error) {
      console.error('Failed to update bookmark:', error);
      showToast('Failed to update bookmark', 'error');
    }
  };

  const handleCreateFolder = async () => {
    if (!newFolderName.trim()) return;

    try {
      await createFolder({ name: newFolderName });
      setShowNewFolder(false);
      setNewFolderName('');
      loadData();
      showToast('Folder created', 'success');
    } catch (error) {
      console.error('Failed to create folder:', error);
      showToast('Failed to create folder', 'error');
    }
  };

  const handleDeleteFolder = async (folderId: string, folderName: string) => {
    if (!confirm(`Delete folder "${folderName}" and all its bookmarks?`)) return;

    try {
      await deleteFolder(folderId);
      if (selectedFolder === folderId) {
        setSelectedFolder(null);
      }
      loadData();
      showToast('Folder deleted', 'success');
    } catch (error) {
      console.error('Failed to delete folder:', error);
      showToast('Failed to delete folder', 'error');
    }
  };

  if (isLoading) {
    return (
      <div className={`animate-pulse ${className}`}>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 bg-zinc-800 rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      {/* Folders */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-white">Folders</h3>
          <button
            onClick={() => setShowNewFolder(true)}
            className="flex items-center gap-2 text-sm text-blue-400 hover:text-blue-300"
          >
            <Plus className="w-4 h-4" />
            New Folder
          </button>
        </div>

        {showNewFolder && (
          <div className="mb-3 p-3 bg-zinc-800 rounded-lg">
            <input
              type="text"
              value={newFolderName}
              onChange={(e) => setNewFolderName(e.target.value)}
              placeholder="Folder name"
              className="w-full px-3 py-2 bg-zinc-900 border border-zinc-700 rounded-lg text-white text-sm focus:outline-none focus:border-blue-500"
              autoFocus
              onKeyPress={(e) => e.key === 'Enter' && handleCreateFolder()}
            />
            <div className="flex gap-2 mt-2">
              <button
                onClick={handleCreateFolder}
                className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg"
              >
                Create
              </button>
              <button
                onClick={() => {
                  setShowNewFolder(false);
                  setNewFolderName('');
                }}
                className="px-3 py-1 bg-zinc-700 hover:bg-zinc-600 text-white text-sm rounded-lg"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedFolder(null)}
            className={`
              px-3 py-1.5 rounded-lg text-sm font-medium transition-all
              ${selectedFolder === null
                ? 'bg-blue-600 text-white'
                : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
              }
            `}
          >
            All Bookmarks
          </button>
          {folders.map((folder) => (
            <div key={folder.id} className="flex items-center gap-1">
              <button
                onClick={() => setSelectedFolder(folder.id)}
                className={`
                  px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                  ${selectedFolder === folder.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                  }
                `}
              >
                <Folder className="w-3 h-3 inline mr-1" />
                {folder.name} ({folder.bookmark_count})
              </button>
              <button
                onClick={() => handleDeleteFolder(folder.id, folder.name)}
                className="p-1 text-zinc-500 hover:text-red-400"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Bookmarks */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-3">
          Bookmarks {bookmarks.length > 0 && `(${bookmarks.length})`}
        </h3>

        {bookmarks.length === 0 ? (
          <div className="text-center py-12 text-zinc-500">
            <Bookmark className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>No bookmarks yet</p>
            <p className="text-sm">Bookmark chapters and sections to find them easily</p>
          </div>
        ) : (
          <div className="space-y-2">
            {bookmarks.map((bookmark) => (
              <div
                key={bookmark.id}
                className="p-4 bg-zinc-900 border border-zinc-800 rounded-lg hover:border-zinc-700 transition-all"
              >
                {editingId === bookmark.id ? (
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      className="flex-1 px-3 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white text-sm focus:outline-none focus:border-blue-500"
                      onKeyPress={(e) => e.key === 'Enter' && handleUpdate(bookmark.id)}
                    />
                    <button
                      onClick={() => handleUpdate(bookmark.id)}
                      className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg"
                    >
                      Save
                    </button>
                    <button
                      onClick={() => setEditingId(null)}
                      className="px-3 py-2 bg-zinc-700 hover:bg-zinc-600 text-white text-sm rounded-lg"
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="text-white font-medium mb-1">{bookmark.title}</h4>
                      <p className="text-sm text-zinc-500">
                        Chapter {bookmark.chapter_id}
                        {bookmark.section_id && ` • Section ${bookmark.section_id}`}
                      </p>
                      {bookmark.notes && (
                        <p className="text-sm text-zinc-400 mt-2">{bookmark.notes}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => {
                          setEditingId(bookmark.id);
                          setEditTitle(bookmark.title);
                        }}
                        className="p-2 text-zinc-500 hover:text-blue-400 transition-colors"
                        title="Edit bookmark"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(bookmark.id)}
                        className="p-2 text-zinc-500 hover:text-red-400 transition-colors"
                        title="Delete bookmark"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
