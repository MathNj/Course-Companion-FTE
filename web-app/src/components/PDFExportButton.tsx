/**
 * PDF Export Button Component
 * Provides quick PDF export for various content types
 */

'use client';

import { Download, Loader2 } from 'lucide-react';
import { useState } from 'react';
import { Button } from './ui/Button';
import {
  exportElementToPDF,
  generateChapterPDF,
  generateNotesPDF,
  generateProgressPDF,
  type ChapterPDFData,
  type NotePDFData,
  type ProgressPDFData
} from '@/lib/pdfExport';
import { useToast } from '@/hooks/useToast';

interface PDFExportButtonProps {
  type: 'chapter' | 'notes' | 'progress' | 'element';
  data?: ChapterPDFData | NotePDFData | ProgressPDFData;
  elementId?: string;
  filename?: string;
  disabled?: boolean;
  className?: string;
}

export function PDFExportButton({
  type,
  data,
  elementId,
  filename,
  disabled = false,
  className = ''
}: PDFExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);
  const { showToast } = useToast();

  const handleExport = async () => {
    setIsExporting(true);

    try {
      switch (type) {
        case 'element':
          if (!elementId) {
            throw new Error('elementId is required for element export');
          }
          await exportElementToPDF(elementId, filename);
          showToast('PDF exported successfully', 'success');
          break;

        case 'chapter':
          if (!data) {
            throw new Error('data is required for chapter export');
          }
          await generateChapterPDF(data as ChapterPDFData, { filename });
          showToast('Chapter PDF exported successfully', 'success');
          break;

        case 'notes':
          if (!data) {
            throw new Error('data is required for notes export');
          }
          await generateNotesPDF(data as NotePDFData, { filename });
          showToast('Notes PDF exported successfully', 'success');
          break;

        case 'progress':
          if (!data) {
            throw new Error('data is required for progress export');
          }
          await generateProgressPDF(data as ProgressPDFData, { filename });
          showToast('Progress report exported successfully', 'success');
          break;

        default:
          throw new Error(`Unknown export type: ${type}`);
      }
    } catch (error) {
      console.error('PDF export failed:', error);
      showToast('Failed to export PDF', 'error');
    } finally {
      setIsExporting(false);
    }
  };

  const getTooltip = () => {
    if (isExporting) return 'Exporting...';
    if (type === 'element') return 'Export as PDF';
    if (type === 'chapter') return 'Export chapter as PDF';
    if (type === 'notes') return 'Export notes as PDF';
    if (type === 'progress') return 'Export progress report';
    return 'Export as PDF';
  };

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={handleExport}
      disabled={disabled || isExporting}
      className={`${className} hover:scale-105 active:scale-95 transition-all duration-300`}
      title={getTooltip()}
    >
      {isExporting ? (
        <>
          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          Exporting...
        </>
      ) : (
        <>
          <Download className="w-4 h-4 mr-2" />
          Export PDF
        </>
      )}
    </Button>
  );
}

/**
 * Quick export button for specific chapter content
 */
export function ChapterExportButton({
  chapter,
  className = ''
}: {
  chapter: {
    title: string;
    content: string;
    sections?: Array<{ title: string; content: string }>;
  };
  className?: string;
}) {
  const data: ChapterPDFData = {
    title: chapter.title,
    chapters: [chapter]
  };

  return (
    <PDFExportButton
      type="chapter"
      data={data}
      filename={`${chapter.title.replace(/\s+/g, '-').toLowerCase()}.pdf`}
      className={className}
    />
  );
}

/**
 * Quick export button for notes
 */
export function NotesExportButton({
  notes,
  className = ''
}: {
  notes: Array<{
    chapter: string;
    section?: string;
    content: string;
    createdAt: string;
    tags?: string[];
  }>;
  className?: string;
}) {
  const data: NotePDFData = {
    title: 'My Notes',
    notes
  };

  return (
    <PDFExportButton
      type="notes"
      data={data}
      filename={`notes-${new Date().toISOString().split('T')[0]}.pdf`}
      className={className}
    />
  );
}

/**
 * Quick export button for progress report
 */
export function ProgressExportButton({
  progress,
  className = ''
}: {
  progress: ProgressPDFData;
  className?: string;
}) {
  return (
    <PDFExportButton
      type="progress"
      data={progress}
      filename={`progress-report-${new Date().toISOString().split('T')[0]}.pdf`}
      className={className}
    />
  );
}
