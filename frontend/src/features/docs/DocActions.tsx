import React from 'react';
import type { DocumentInstance, DocumentTypeDef } from './docsTypes';
import { canGenerate } from './DocumentsProvider';

export function DocActions({
  docType,
  instance,
  generating,
  onGenerate,
  onMarkDraft,
  onSubmitForReview,
  onApprove,
  onExport,
}: {
  docType: DocumentTypeDef;
  instance: DocumentInstance;
  generating: boolean;
  onGenerate: () => void;
  onMarkDraft: () => void;
  onSubmitForReview: () => void;
  onApprove: () => void;
  onExport: () => void;
}) {
  const showGenerate = canGenerate(docType.id);

  const primaryCta =
    instance.status === 'not_started'
      ? showGenerate
        ? { label: 'Start / Generate', onClick: onGenerate }
        : { label: 'Start (Draft)', onClick: onMarkDraft }
      : instance.status === 'draft'
        ? { label: 'Submit for Review', onClick: onSubmitForReview }
        : instance.status === 'in_review'
          ? { label: 'Approve', onClick: onApprove }
          : { label: 'Export', onClick: onExport };

  return (
    <div className="flex flex-wrap gap-2">
      {showGenerate ? (
        <button
          onClick={onGenerate}
          disabled={generating}
          className={`px-3 py-2 rounded-md text-sm text-white ${
            generating ? 'bg-primary/50 cursor-not-allowed' : 'bg-primary hover:bg-primary/90'
          }`}
        >
          {generating ? 'Generating…' : instance.status === 'not_started' ? 'Generate' : 'Regenerate'}
        </button>
      ) : null}

      <button
        onClick={primaryCta.onClick}
        className="px-3 py-2 rounded-md text-sm border border-gray-300 bg-white hover:bg-gray-50"
      >
        {primaryCta.label}
      </button>

      <button
        onClick={onExport}
        disabled={!docType.exportable}
        className={`px-3 py-2 rounded-md text-sm border border-gray-300 ${
          docType.exportable ? 'bg-white hover:bg-gray-50' : 'bg-gray-100 text-gray-500 cursor-not-allowed'
        }`}
      >
        Export (PDF/Docx)
      </button>
    </div>
  );
}

