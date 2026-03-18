import React from 'react';
import type { DocumentInstance, DocumentTypeDef } from './docsTypes';
import { canGenerate } from './DocumentsProvider';

export function DocActions({
  docType,
  instance,
  generating,
  onOpenEditor,
  onGenerate,
  onMarkDraft,
  onSubmitForReview,
  onApprove,
  onExport,
}: {
  docType: DocumentTypeDef;
  instance: DocumentInstance;
  generating: boolean;
  onOpenEditor?: () => void;
  onGenerate: () => void;
  onMarkDraft: () => void;
  onSubmitForReview: () => void;
  onApprove: () => void;
  onExport: () => void;
}) {
  const showGenerate = canGenerate(docType.id);
  const isRmf = docType.id === 'rmf';
  const isCompileOnly = ['essential_requirements_checklist', 'submission_index', 'audit_package'].includes(docType.id);

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
      {onOpenEditor ? (
        <button
          onClick={onOpenEditor}
          className="px-3 py-2 rounded-md text-sm border border-gray-300 bg-white hover:bg-gray-50"
        >
          {isRmf ? 'Open' : 'Open/Edit'}
        </button>
      ) : null}
      {showGenerate ? (
        <button
          onClick={onGenerate}
          disabled={generating}
          className={`px-3 py-2 rounded-md text-sm text-gray-900 ${
            generating ? 'bg-primary/50 cursor-not-allowed' : 'bg-primary hover:bg-primary/90'
          }`}
        >
          {generating
            ? isRmf || isCompileOnly
              ? 'Compiling…'
              : 'Generating…'
            : instance.status === 'not_started'
              ? isRmf
                ? 'Compile Risk Management File'
                : isCompileOnly
                  ? docType.id === 'essential_requirements_checklist'
                    ? 'Compile Essential Requirements Checklist'
                    : docType.id === 'submission_index'
                      ? 'Compile Submission Index'
                      : 'Compile Audit Package'
                  : 'Generate'
              : isRmf
                ? 'Recompile Risk Management File'
                : isCompileOnly
                  ? 'Recompile'
                  : 'Regenerate'}
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

