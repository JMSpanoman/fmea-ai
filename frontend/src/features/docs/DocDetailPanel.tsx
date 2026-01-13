import React, { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { docTypeById } from './docsRegistry';
import { canGenerate, useDocs } from './DocumentsProvider';
import { AuthorityBadge } from './AuthorityBadge';
import { StatusBadge } from './StatusBadge';
import { ImpactBanner } from './ImpactBanner';
import { DocActions } from './DocActions';
import { ApproveModal } from './ApproveModal';
import { htmlToText, isProbablyHtml } from './htmlUtils';

export function DocDetailPanel({
  onNavigate,
}: {
  onNavigate: (groupId: string, docTypeId?: string) => void;
}) {
  const { state, actions, derived } = useDocs();
  const [approveOpen, setApproveOpen] = useState(false);
  const [contentMode, setContentMode] = useState<'preview' | 'text'>('preview');
  const navigate = useNavigate();

  const docTypeId = state.selectedDocTypeId;
  const docType = docTypeId ? docTypeById[docTypeId] : undefined;
  const inst = docTypeId ? state.instancesByTypeId[docTypeId] : undefined;

  // IMPORTANT: keep hooks unconditional (no early returns before these)
  const isHtml = useMemo(() => isProbablyHtml(inst?.content), [inst?.content]);
  const textView = useMemo(() => {
    const c = inst?.content || '';
    return isHtml ? htmlToText(c) : c;
  }, [isHtml, inst?.content]);

  const dependencyStatus = useMemo(() => {
    if (!docType) return { blocking: false, message: '' };
    // MVP governance example (as requested): Residual Risk depends on Acceptability Criteria being completed
    if (docType.id === 'residual_risk') {
      const rac = state.instancesByTypeId['risk_acceptability_criteria'];
      if (!rac || rac.status !== 'approved') {
        return {
          blocking: true,
          message: 'Complete and approve Risk Acceptability Criteria to enable Residual Risk Evaluation.',
        };
      }
    }
    return { blocking: false, message: '' };
  }, [docType, state.instancesByTypeId]);

  if (!docTypeId || !docType || !inst) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6 text-sm text-gray-700">
        Select a document to view details. Use the left list to pick one.
      </div>
    );
  }

  const generating = state.generate.status === 'loading' && state.generate.docTypeId === docTypeId;
  const showGenerate = canGenerate(docTypeId);

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden flex flex-col h-[calc(100vh-220px)]">
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="text-lg font-semibold text-gray-900">{docType.name}</div>
            <div className="text-sm text-gray-600 mt-1">{docType.description}</div>
            <div className="mt-2 flex items-center gap-2">
              <AuthorityBadge authority={docType.authority} />
              <StatusBadge status={inst.status} />
              {inst.impacted ? (
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
                  Impacted by upstream changes
                </span>
              ) : null}
            </div>
            <div className="mt-2 text-xs text-gray-600">
              <div>
                <b>Version:</b> {inst.version || 'v0'} • <b>Updated:</b>{' '}
                {inst.updatedAt ? new Date(inst.updatedAt).toLocaleString() : '—'} • <b>Last generated:</b>{' '}
                {inst.lastGeneratedAt ? new Date(inst.lastGeneratedAt).toLocaleString() : '—'}
              </div>
            </div>
          </div>
          <DocActions
            docType={docType}
            instance={inst}
            generating={generating}
            onOpenEditor={
              inst.backendDocId
                ? () => navigate(`/projects/${state.projectId}/documents/${inst.backendDocId}`)
                : undefined
            }
            onGenerate={() => actions.generate(docTypeId)}
            onMarkDraft={() => actions.updateStatus(docTypeId, 'draft')}
            onSubmitForReview={() => actions.updateStatus(docTypeId, 'in_review')}
            onApprove={() => setApproveOpen(true)}
            onExport={() => {
              // Placeholder: later wire to backend export endpoints
              const blob = new Blob([inst.content || ''], { type: 'text/plain;charset=utf-8' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `${docType.id}_${state.projectId}_${inst.version || 'v0'}.txt`;
              a.click();
              URL.revokeObjectURL(url);
            }}
          />
        </div>

        {/* Registry explanation + "where it lives" link (for key doc types) */}
        {['rmp', 'hazard_analysis', 'fmea', 'rmf', 'traceability_matrix'].includes(docType.id) ? (
          <div className="mt-3 rounded-lg border border-gray-200 bg-gray-50 p-3">
            <div className="text-sm font-semibold text-gray-900">What this is</div>
            <div className="text-sm text-gray-700 mt-1">
              This page is a <b>Documentation</b> lens (registry definition). Your project-specific instance lives under
              Project Documents and is versioned for audit.
            </div>
            <div className="mt-2 flex flex-wrap items-center gap-2">
              <div className="text-xs text-gray-700">
                <b>Where it lives:</b>{' '}
                {inst.backendDocId ? 'Project Document instance exists.' : 'No project instance found.'}
              </div>
              <button
                onClick={() => {
                  if (inst.backendDocId) navigate(`/projects/${state.projectId}/documents/${inst.backendDocId}`);
                  else navigate(`/projects/${state.projectId}/documents`);
                }}
                className="px-3 py-2 rounded-md text-sm bg-primary text-white hover:bg-primary/90"
                type="button"
              >
                {inst.backendDocId ? 'Open in Project' : 'Create in Project'}
              </button>
            </div>
          </div>
        ) : null}

        {dependencyStatus.blocking ? (
          <div className="mt-3">
            <ImpactBanner title="Dependency required" message={dependencyStatus.message} />
          </div>
        ) : null}

        {inst.impacted ? (
          <div className="mt-3">
            <ImpactBanner
              title="Change impact detected"
              message="One or more dependencies changed after this document was last generated/reviewed. Consider regenerating or re-reviewing before approval."
              actions={
                showGenerate ? (
                  <button
                    onClick={() => actions.generate(docTypeId)}
                    className="px-3 py-2 rounded-md text-sm bg-amber-600 text-white hover:bg-amber-700"
                  >
                    Regenerate
                  </button>
                ) : null
              }
            />
          </div>
        ) : null}
      </div>

      <div className="p-4 flex-1 overflow-y-auto">
        <div className="grid grid-cols-1 gap-4">
          {['rmp', 'hazard_analysis', 'fmea', 'rmf', 'traceability_matrix'].includes(docType.id) ? (
            <div className="rounded-lg border border-gray-200 bg-white p-4">
              <div className="text-xs font-semibold text-gray-700 uppercase tracking-wider">What it includes</div>
              <div className="mt-2">
                {(docType.includes || []).length ? (
                  <ul className="list-disc pl-5 text-sm text-gray-700 space-y-1">
                    {(docType.includes || []).slice(0, 6).map((x) => (
                      <li key={x}>{x}</li>
                    ))}
                  </ul>
                ) : (
                  <div className="text-sm text-gray-600">—</div>
                )}
              </div>

              <div className="mt-4 text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Common auditor questions
              </div>
              <div className="mt-2">
                {(docType.auditorQuestions || []).length ? (
                  <ul className="list-disc pl-5 text-sm text-gray-700 space-y-1">
                    {(docType.auditorQuestions || []).slice(0, 6).map((x) => (
                      <li key={x}>{x}</li>
                    ))}
                  </ul>
                ) : (
                  <div className="text-sm text-gray-600">—</div>
                )}
              </div>

              <div className="mt-4">
                <button
                  onClick={() => {
                    if (inst.backendDocId) navigate(`/projects/${state.projectId}/documents/${inst.backendDocId}`);
                    else navigate(`/projects/${state.projectId}/documents`);
                  }}
                  className="px-4 py-2 rounded-md text-sm bg-primary text-white hover:bg-primary/90"
                  type="button"
                >
                  {inst.backendDocId ? 'Open in Project' : 'Create in Project'}
                </button>
              </div>
            </div>
          ) : null}

          <div>
            <div className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Dependencies</div>
            <div className="mt-2 flex flex-wrap gap-2">
              {(docType.dependencies || []).length ? (
                (docType.dependencies || []).map((depId) => {
                  const dep = derived.docTypeById[depId];
                  const depInst = state.instancesByTypeId[depId];
                  return (
                    <button
                      key={depId}
                      onClick={() => onNavigate(dep.groupId, depId)}
                      className="px-2 py-1 rounded-md text-xs border border-gray-200 hover:bg-gray-50"
                      title={dep?.description || depId}
                    >
                      {dep?.name || depId} • {depInst?.status || 'not_started'}
                    </button>
                  );
                })
              ) : (
                <div className="text-sm text-gray-600">No dependencies</div>
              )}
            </div>
          </div>

          <div>
            <div className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Content</div>
            <div className="mt-2">
              {inst.backendDocId && isHtml ? (
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setContentMode('preview')}
                      className={`px-2 py-1 text-xs rounded-md border ${
                        contentMode === 'preview' ? 'bg-primary/10 border-primary text-primary' : 'bg-white border-gray-200'
                      }`}
                    >
                      Preview
                    </button>
                    <button
                      onClick={() => setContentMode('text')}
                      className={`px-2 py-1 text-xs rounded-md border ${
                        contentMode === 'text' ? 'bg-primary/10 border-primary text-primary' : 'bg-white border-gray-200'
                      }`}
                    >
                      Text
                    </button>
                    <div className="text-xs text-gray-600">
                      This document is generated as HTML. Use <b>Open/Edit</b> for full editing/versioning.
                    </div>
                  </div>

                  {contentMode === 'preview' ? (
                    <div className="rounded-md border border-gray-200 p-3 overflow-auto max-h-[520px]">
                      <div
                        className="prose prose-sm max-w-none"
                        // Backend content is generated HTML; render it for readability.
                        dangerouslySetInnerHTML={{ __html: inst.content || '' }}
                      />
                    </div>
                  ) : (
                    <textarea
                      value={textView}
                      readOnly
                      className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm font-mono bg-gray-50"
                      rows={16}
                    />
                  )}
                </div>
              ) : (
                <textarea
                  value={inst.content || ''}
                  onChange={(e) => actions.updateContent(docTypeId, e.target.value)}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm font-mono"
                  rows={16}
                  placeholder={
                    showGenerate
                      ? 'Generate to create an initial draft, then edit here.'
                      : 'Start as Draft and edit content here.'
                  }
                />
              )}
            </div>
          </div>

          <div>
            <div className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Approvals</div>
            <div className="mt-2 space-y-2">
              {(inst.approvals || []).length ? (
                (inst.approvals || []).slice().reverse().map((a, idx) => (
                  <div key={idx} className="rounded-md border border-gray-200 p-3 text-sm">
                    <div className="flex items-center justify-between">
                      <div className="font-medium text-gray-900">{a.name}</div>
                      <div className="text-xs text-gray-600">{new Date(a.date).toLocaleString()}</div>
                    </div>
                    {a.comment ? <div className="text-sm text-gray-700 mt-2">{a.comment}</div> : null}
                  </div>
                ))
              ) : (
                <div className="text-sm text-gray-600">No approvals recorded.</div>
              )}
            </div>
          </div>
        </div>
      </div>

      <ApproveModal
        open={approveOpen}
        docName={docType.name}
        onClose={() => setApproveOpen(false)}
        onApprove={({ name, comment }) => {
          actions.approve(docTypeId, { name, comment, date: new Date().toISOString() });
          setApproveOpen(false);
        }}
      />
    </div>
  );
}

