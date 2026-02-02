/**
 * Note Button Component
 * Quick note button for chapters and sections
 */

'use client';

import { useState } from 'react';
import { FileText, FileEdit } from 'lucide-react';
import { NoteEditor } from './NoteEditor';
import { getNotes } from '@/lib/advancedFeatures';
import { useToast } from '@/hooks/useToast';

interface NoteButtonProps {
  chapterId: string;
  sectionId?: string;
  className?: string;
}

export default function NoteButton({
  chapterId,
  sectionId,
  className = ''
}: NoteButtonProps) {
  const [showEditor, setShowEditor] = useState(false);
  const [hasNotes, setHasNotes] = useState(false);
  const { showToast } = useToast();

  const checkNotes = async () => {
    try {
      const { notes } = await getNotes({
        chapter_id: chapterId,
        section_id: sectionId
      });
      setHasNotes(notes.length > 0);
    } catch (error) {
      console.error('Failed to check notes:', error);
    }
  };

  const handleClick = () => {
    setShowEditor(true);
    checkNotes();
  };

  return (
    <>
      <button
        onClick={handleClick}
        className={`
          flex items-center gap-2 px-4 py-2 rounded-lg
          bg-zinc-800 hover:bg-zinc-700 text-zinc-300
          transition-all duration-200
          ${className}
        `}
        title={hasNotes ? 'Edit notes' : 'Add notes'}
      >
        {hasNotes ? (
          <FileEdit className="w-5 h-5 text-blue-400" />
        ) : (
          <FileText className="w-5 h-5" />
        )}
        <span className="text-sm font-medium">
          {hasNotes ? 'Notes' : 'Add Note'}
        </span>
      </button>

      {showEditor && (
        <NoteEditor
          chapterId={chapterId}
          sectionId={sectionId}
          onClose={() => {
            setShowEditor(false);
            checkNotes();
          }}
        />
      )}
    </>
  );
}
