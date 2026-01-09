import React, { useMemo, useState } from 'react';

export function ApproveModal({
  open,
  docName,
  onClose,
  onApprove,
}: {
  open: boolean;
  docName: string;
  onClose: () => void;
  onApprove: (payload: { name: string; comment?: string }) => void;
}) {
  const [name, setName] = useState('');
  const [comment, setComment] = useState('');

  const canSubmit = useMemo(() => name.trim().length > 1, [name]);

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 p-4">
      <div className="w-full max-w-lg rounded-lg bg-white shadow-xl border border-gray-200">
        <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
          <div className="text-sm font-semibold text-gray-900">Approve: {docName}</div>
          <button onClick={onClose} className="text-sm text-gray-600 hover:text-gray-900">
            Close
          </button>
        </div>
        <div className="p-4 space-y-3">
          <div>
            <label className="block text-xs font-semibold text-gray-700">Approver Name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
              placeholder="e.g. Jane Smith"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-700">Comment (optional)</label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
              rows={3}
              placeholder="Approval rationale, conditions, or notes..."
            />
          </div>
        </div>
        <div className="px-4 py-3 border-t border-gray-200 flex items-center justify-end gap-2">
          <button onClick={onClose} className="px-3 py-2 rounded-md text-sm border border-gray-300">
            Cancel
          </button>
          <button
            disabled={!canSubmit}
            onClick={() => {
              onApprove({ name: name.trim(), comment: comment.trim() || undefined });
              setName('');
              setComment('');
            }}
            className={`px-3 py-2 rounded-md text-sm text-white ${
              canSubmit ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-emerald-300 cursor-not-allowed'
            }`}
          >
            Approve
          </button>
        </div>
      </div>
    </div>
  );
}

