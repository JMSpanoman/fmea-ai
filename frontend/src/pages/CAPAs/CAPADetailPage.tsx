import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useProject } from '../../contexts/ProjectContext';
import { PageHeader } from '../../components/ui/PageHeader';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { UpstreamLinksPanel } from '../../components/Traceability/UpstreamLinksPanel';
import {
  getCAPA,
  updateCAPA,
  addCapaEvidence,
  deleteCapaEvidence,
  getCapaAiReviewHooks,
  CAPAFull,
  CapaWorkflowPayload,
  CorrectiveActionItem,
} from '../../api/capas';

const TRIGGER_TYPES = [
  { v: 'complaint', l: 'Complaint' },
  { v: 'nonconformance', l: 'Nonconformance' },
  { v: 'audit_finding', l: 'Audit Finding' },
  { v: 'trending_signal', l: 'Trending Signal' },
  { v: 'supplier_issue', l: 'Supplier Issue' },
  { v: 'other', l: 'Other' },
];

function deepClone<T>(x: T): T {
  return JSON.parse(JSON.stringify(x));
}

function intakeComplete(p: CapaWorkflowPayload): boolean {
  const t = p.trigger || {};
  const pr = p.problem || {};
  const c = p.containment || {};
  return !!(
    t.trigger_type &&
    String(t.source_reference || '').trim() &&
    String(pr.problem_statement || '').trim() &&
    pr.scope &&
    String(c.containment_actions || '').trim() &&
    c.containment_verified === true
  );
}

function newAction(): CorrectiveActionItem {
  return {
    id: crypto.randomUUID(),
    description: '',
    owner: '',
    status: 'planned',
    linked_root_cause_id: 'primary',
    action_type: 'process',
  };
}

const CAPADetailPage: React.FC = () => {
  const { projectId, id } = useParams<{ projectId?: string; id: string }>();
  const { currentProject } = useProject();
  const navigate = useNavigate();
  const [capa, setCapa] = useState<CAPAFull | null>(null);
  const [payload, setPayload] = useState<CapaWorkflowPayload | null>(null);
  const [workflowState, setWorkflowState] = useState('draft');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [aiHooks, setAiHooks] = useState<{ id: string; title: string; prompt: string }[]>([]);
  const [evTitle, setEvTitle] = useState('');
  const [evCat, setEvCat] = useState('general');

  const finalProjectId = projectId || currentProject?.id || '';

  const canRca = useMemo(() => intakeComplete(payload || ({} as CapaWorkflowPayload)), [payload]);
  const evidenceCount = capa?.evidences?.length ?? 0;
  const canEffectivenessResults = evidenceCount > 0;

  const loadCAPA = useCallback(async () => {
    if (!finalProjectId || !id) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getCAPA(finalProjectId, id);
      setCapa(data);
      setPayload(deepClone(data.payload));
      setWorkflowState(data.workflow_state || 'draft');
      const hooks = await getCapaAiReviewHooks(finalProjectId).catch(() => ({ hooks: [] }));
      setAiHooks(hooks.hooks || []);
    } catch (err: any) {
      console.error(err);
      setError(err?.response?.data?.detail || err?.message || 'Failed to load CAPA');
    } finally {
      setLoading(false);
    }
  }, [finalProjectId, id]);

  useEffect(() => {
    loadCAPA();
  }, [loadCAPA]);

  const save = async (nextState?: string) => {
    if (!finalProjectId || !id || !payload) return;
    setSaving(true);
    setError(null);
    try {
      const data = await updateCAPA(finalProjectId, id, {
        payload,
        workflow_state: nextState ?? workflowState,
      });
      setCapa(data);
      setPayload(deepClone(data.payload));
      setWorkflowState(data.workflow_state);
    } catch (err: any) {
      const d = err?.response?.data?.detail;
      const msg = typeof d === 'object' && d?.message ? d.message : d || err?.message || 'Save failed';
      setError(String(msg));
    } finally {
      setSaving(false);
    }
  };

  const addEvidence = async () => {
    if (!finalProjectId || !id || !evTitle.trim()) return;
    try {
      await addCapaEvidence(finalProjectId, id, { category: evCat, title: evTitle.trim() });
      setEvTitle('');
      await loadCAPA();
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to add evidence');
    }
  };

  const removeEv = async (evid: string) => {
    if (!finalProjectId || !id) return;
    try {
      await deleteCapaEvidence(finalProjectId, id, evid);
      await loadCAPA();
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to delete evidence');
    }
  };

  const patchPayload = (fn: (p: CapaWorkflowPayload) => void) => {
    if (!payload) return;
    const next = deepClone(payload);
    fn(next);
    setPayload(next);
  };

  if (!finalProjectId) {
    return (
      <div className="p-6">
        <div className="text-error">Project ID required. Please select a project first.</div>
      </div>
    );
  }

  if (loading || !payload) {
    return (
      <div className="p-6">
        <div className="text-text-secondary">Loading CAPA…</div>
      </div>
    );
  }

  if (error && !capa) {
    return (
      <div className="p-6">
        <div className="text-error mb-4">{error}</div>
        <Button onClick={() => loadCAPA()}>Retry</Button>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-5xl">
      <PageHeader
        title={`CAPA workflow`}
        breadcrumbs={[
          { label: 'Projects', path: '/projects' },
          { label: 'CAPAs', path: `/capa` },
          { label: id!.slice(0, 8), path: '#' },
        ]}
        actions={
          <>
            <span className="text-sm rounded-full bg-surface-secondary px-3 py-1 mr-2">
              State: <strong>{workflowState}</strong>
            </span>
            <Button variant="secondary" onClick={() => navigate('/capa')}>
              Back
            </Button>
            <Button onClick={() => save()} disabled={saving}>
              {saving ? 'Saving…' : 'Save'}
            </Button>
          </>
        }
      />

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-900">{error}</div>
      )}

      {finalProjectId && id && (
        <UpstreamLinksPanel
          projectId={finalProjectId}
          artifactType="capa"
          artifactId={id}
          onNavigate={(route) => navigate(route)}
        />
      )}

      <Card>
        <h3 className="text-lg font-semibold mb-2">A. Trigger & classification</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
          <label className="block">
            <span className="text-text-secondary">Trigger type *</span>
            <select
              className="mt-1 w-full border rounded px-2 py-1"
              value={String((payload.trigger as any).trigger_type || '')}
              onChange={(e) =>
                patchPayload((p) => {
                  p.trigger = { ...p.trigger, trigger_type: e.target.value || undefined };
                })
              }
            >
              <option value="">—</option>
              {TRIGGER_TYPES.map((t) => (
                <option key={t.v} value={t.v}>
                  {t.l}
                </option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="text-text-secondary">Source reference *</span>
            <input
              className="mt-1 w-full border rounded px-2 py-1"
              value={String((payload.trigger as any).source_reference || '')}
              onChange={(e) =>
                patchPayload((p) => {
                  p.trigger = { ...p.trigger, source_reference: e.target.value };
                })
              }
            />
          </label>
          <label className="block md:col-span-2">
            <span className="text-text-secondary">Detection method</span>
            <input
              className="mt-1 w-full border rounded px-2 py-1"
              value={String((payload.trigger as any).detection_method || '')}
              onChange={(e) =>
                patchPayload((p) => {
                  p.trigger = { ...p.trigger, detection_method: e.target.value };
                })
              }
            />
          </label>
        </div>
      </Card>

      <Card>
        <h3 className="text-lg font-semibold mb-2">B. Problem definition</h3>
        <label className="block text-sm mb-2">
          <span className="text-text-secondary">Problem statement *</span>
          <textarea
            className="mt-1 w-full border rounded px-2 py-1 min-h-[80px]"
            value={String((payload.problem as any).problem_statement || '')}
            onChange={(e) =>
              patchPayload((p) => {
                p.problem = { ...p.problem, problem_statement: e.target.value };
              })
            }
          />
        </label>
        <label className="block text-sm mb-2">
          <span className="text-text-secondary">Scope *</span>
          <select
            className="mt-1 w-full border rounded px-2 py-1"
            value={String((payload.problem as any).scope || '')}
            onChange={(e) =>
              patchPayload((p) => {
                p.problem = { ...p.problem, scope: e.target.value || undefined };
              })
            }
          >
            <option value="">—</option>
            <option value="local">Local</option>
            <option value="systemic">Systemic</option>
          </select>
        </label>
      </Card>

      <Card>
        <h3 className="text-lg font-semibold mb-2">C. Immediate containment</h3>
        <label className="block text-sm mb-2">
          <span className="text-text-secondary">Containment actions *</span>
          <textarea
            className="mt-1 w-full border rounded px-2 py-1"
            value={String((payload.containment as any).containment_actions || '')}
            onChange={(e) =>
              patchPayload((p) => {
                p.containment = { ...p.containment, containment_actions: e.target.value };
              })
            }
          />
        </label>
        <label className="inline-flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={!!(payload.containment as any).containment_verified}
            onChange={(e) =>
              patchPayload((p) => {
                p.containment = { ...p.containment, containment_verified: e.target.checked };
              })
            }
          />
          Containment verified *
        </label>
      </Card>

      <Card className={!canRca ? 'opacity-60' : ''}>
        <h3 className="text-lg font-semibold mb-2">D. Root cause analysis {!canRca && '(complete A–C first)'}</h3>
        <textarea
          disabled={!canRca}
          className="w-full border rounded px-2 py-1 text-sm min-h-[100px]"
          placeholder="Root cause summary"
          value={String((payload.rca as any).root_cause_summary || '')}
          onChange={(e) =>
            patchPayload((p) => {
              p.rca = { ...p.rca, root_cause_summary: e.target.value };
            })
          }
        />
        <label className="block text-sm mt-2">
          Status
          <select
            disabled={!canRca}
            className="mt-1 w-full border rounded px-2 py-1"
            value={String((payload.rca as any).root_cause_status || 'hypothesis')}
            onChange={(e) =>
              patchPayload((p) => {
                p.rca = { ...p.rca, root_cause_status: e.target.value };
              })
            }
          >
            <option value="hypothesis">Hypothesis (evidence may be pending)</option>
            <option value="confirmed">Confirmed (requires objective evidence)</option>
          </select>
        </label>
        <label className="block text-sm mt-2">
          Objective evidence
          <textarea
            disabled={!canRca}
            className="mt-1 w-full border rounded px-2 py-1 min-h-[60px]"
            value={String((payload.rca as any).objective_evidence || '')}
            onChange={(e) =>
              patchPayload((p) => {
                p.rca = { ...p.rca, objective_evidence: e.target.value };
              })
            }
          />
        </label>
      </Card>

      <Card>
        <h3 className="text-lg font-semibold mb-2">E. Corrective actions</h3>
        <p className="text-xs text-text-secondary mb-2">Each action must reference a root cause id (e.g. primary).</p>
        {(payload.corrective_actions || []).map((a, idx) => (
          <div key={a.id || idx} className="border rounded p-3 mb-2 space-y-2">
            <input
              className="w-full border rounded px-2 py-1 text-sm"
              placeholder="Description"
              value={a.description}
              onChange={(e) =>
                patchPayload((p) => {
                  p.corrective_actions[idx].description = e.target.value;
                })
              }
            />
            <div className="flex gap-2 flex-wrap">
              <input
                className="border rounded px-2 py-1 text-sm flex-1 min-w-[120px]"
                placeholder="Owner"
                value={a.owner}
                onChange={(e) =>
                  patchPayload((p) => {
                    p.corrective_actions[idx].owner = e.target.value;
                  })
                }
              />
              <input
                className="border rounded px-2 py-1 text-sm w-36"
                placeholder="linked_root_cause_id"
                value={a.linked_root_cause_id}
                onChange={(e) =>
                  patchPayload((p) => {
                    p.corrective_actions[idx].linked_root_cause_id = e.target.value;
                  })
                }
              />
              <select
                className="border rounded px-2 py-1 text-sm"
                value={a.status}
                onChange={(e) =>
                  patchPayload((p) => {
                    p.corrective_actions[idx].status = e.target.value;
                  })
                }
              >
                <option value="planned">planned</option>
                <option value="in_progress">in_progress</option>
                <option value="complete">complete</option>
                <option value="cancelled">cancelled</option>
              </select>
            </div>
          </div>
        ))}
        <Button
          variant="secondary"
          onClick={() =>
            patchPayload((p) => {
              p.corrective_actions = [...(p.corrective_actions || []), newAction()];
            })
          }
        >
          Add corrective action
        </Button>
      </Card>

      <Card>
        <h3 className="text-lg font-semibold mb-2">G. Verification of effectiveness (plan)</h3>
        <textarea
          className="w-full border rounded px-2 py-1 text-sm min-h-[80px]"
          placeholder="Success criteria"
          value={String((payload.voe_plan as any).success_criteria || '')}
          onChange={(e) =>
            patchPayload((p) => {
              p.voe_plan = { ...p.voe_plan, success_criteria: e.target.value };
            })
          }
        />
      </Card>

      <Card>
        <h3 className="text-lg font-semibold mb-2">Objective evidence records</h3>
        <p className="text-xs text-text-secondary mb-2">
          Effectiveness results are disabled until at least one evidence record exists (server-enforced).
        </p>
        <div className="flex flex-wrap gap-2 mb-3">
          <select
            className="border rounded px-2 py-1 text-sm"
            value={evCat}
            onChange={(e) => setEvCat(e.target.value)}
          >
            <option value="general">general</option>
            <option value="rca">rca</option>
            <option value="containment">containment</option>
            <option value="effectiveness">effectiveness</option>
          </select>
          <input
            className="border rounded px-2 py-1 text-sm flex-1 min-w-[200px]"
            placeholder="Evidence title"
            value={evTitle}
            onChange={(e) => setEvTitle(e.target.value)}
          />
          <Button variant="secondary" onClick={addEvidence}>
            Add evidence
          </Button>
        </div>
        <ul className="text-sm space-y-1">
          {(capa?.evidences || []).map((ev) => (
            <li key={ev.id} className="flex justify-between gap-2 border-b py-1">
              <span>
                <span className="font-mono text-xs">{ev.id.slice(0, 8)}</span> [{ev.category}] {ev.title}
              </span>
              <button type="button" className="text-red-600 text-xs" onClick={() => removeEv(ev.id)}>
                Remove
              </button>
            </li>
          ))}
        </ul>
      </Card>

      <Card>
        <h3 className="text-lg font-semibold mb-2">H. Effectiveness results</h3>
        {!canEffectivenessResults && (
          <p className="text-sm text-amber-800 bg-amber-50 border border-amber-200 rounded px-3 py-2">
            Add objective evidence above before recording effectiveness results.
          </p>
        )}
        {canEffectivenessResults && (
          <div className="space-y-2 text-sm">
            <textarea
              className="w-full border rounded px-2 py-1 min-h-[60px]"
              placeholder="Evidence summary"
              value={String((payload.effectiveness_results as any)?.evidence_summary || '')}
              onChange={(e) =>
                patchPayload((p) => {
                  p.effectiveness_results = {
                    ...(p.effectiveness_results || {}),
                    evidence_summary: e.target.value,
                    referenced_evidence_ids: (capa?.evidences || []).map((x) => x.id),
                    result: String((p.effectiveness_results as any)?.result || ''),
                    reviewer: String((p.effectiveness_results as any)?.reviewer || ''),
                  } as any;
                })
              }
            />
            <input
              className="w-full border rounded px-2 py-1"
              placeholder="Reviewer"
              value={String((payload.effectiveness_results as any)?.reviewer || '')}
              onChange={(e) =>
                patchPayload((p) => {
                  p.effectiveness_results = {
                    ...(p.effectiveness_results || {}),
                    reviewer: e.target.value,
                    evidence_summary: String((p.effectiveness_results as any)?.evidence_summary || ''),
                    referenced_evidence_ids: (capa?.evidences || []).map((x) => x.id),
                    result: String((p.effectiveness_results as any)?.result || ''),
                  } as any;
                })
              }
            />
            <select
              className="w-full border rounded px-2 py-1"
              value={String((payload.effectiveness_results as any)?.conclusion || '')}
              onChange={(e) =>
                patchPayload((p) => {
                  p.effectiveness_results = {
                    ...(p.effectiveness_results || {}),
                    conclusion: e.target.value || null,
                    evidence_summary: String((p.effectiveness_results as any)?.evidence_summary || ''),
                    referenced_evidence_ids: (capa?.evidences || []).map((x) => x.id),
                    result: String((p.effectiveness_results as any)?.result || ''),
                    reviewer: String((p.effectiveness_results as any)?.reviewer || ''),
                  } as any;
                })
              }
            >
              <option value="">Conclusion —</option>
              <option value="effective">effective</option>
              <option value="ineffective">ineffective</option>
              <option value="needs_more_monitoring">needs_more_monitoring</option>
            </select>
          </div>
        )}
      </Card>

      <Card>
        <h3 className="text-lg font-semibold mb-2">K. Approvals</h3>
        <div className="space-y-2">
          {(payload.approvals || []).map((ap, i) => (
            <div key={ap.id || i} className="flex flex-wrap items-center gap-2 text-sm border rounded px-2 py-1">
              <span className="font-medium">{ap.kind}</span>
              <select
                value={ap.status}
                onChange={(e) =>
                  patchPayload((p) => {
                    p.approvals[i].status = e.target.value;
                  })
                }
              >
                <option value="pending">pending</option>
                <option value="approved">approved</option>
                <option value="rejected">rejected</option>
              </select>
              <input
                className="border rounded px-2 py-1 flex-1 min-w-[120px]"
                placeholder="Approver name"
                value={ap.approver_name}
                onChange={(e) =>
                  patchPayload((p) => {
                    p.approvals[i].approver_name = e.target.value;
                  })
                }
              />
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <h3 className="text-lg font-semibold mb-2">L. Closure checklist</h3>
        {(['root_cause_verified', 'actions_implemented', 'effectiveness_supported_by_evidence', 'risk_documentation_updated', 'required_approvals_complete', 'documentation_complete'] as const).map((key) => (
          <label key={key} className="flex items-center gap-2 text-sm py-1">
            <input
              type="checkbox"
              checked={!!((payload.closure as any)?.checklist?.[key])}
              onChange={(e) =>
                patchPayload((p) => {
                  const cl = { ...((p.closure as any)?.checklist || {}) };
                  cl[key] = e.target.checked;
                  p.closure = { ...(p.closure || {}), checklist: cl };
                })
              }
            />
            {key.replace(/_/g, ' ')}
          </label>
        ))}
      </Card>

      <Card>
        <h3 className="text-lg font-semibold mb-2">AI review hooks (prompts only)</h3>
        <ul className="text-sm space-y-2">
          {aiHooks.map((h) => (
            <li key={h.id} className="border rounded p-2">
              <div className="font-medium">{h.title}</div>
              <div className="text-text-secondary text-xs mt-1">{h.prompt}</div>
            </li>
          ))}
        </ul>
      </Card>

      <Card>
        <h3 className="text-lg font-semibold mb-2">Workflow transition</h3>
        <div className="flex flex-wrap gap-2 items-center">
          <select
            className="border rounded px-2 py-1 text-sm"
            value={workflowState}
            onChange={(e) => setWorkflowState(e.target.value)}
          >
            {[
              'draft',
              'intake',
              'intake_complete',
              'rca_in_progress',
              'rca_pending_approval',
              'actions_defined',
              'implementation',
              'effectiveness_planned',
              'effectiveness_pending',
              'pending_closure',
              'closed',
              'cancelled',
            ].map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
          <Button variant="secondary" onClick={() => save(workflowState)}>
            Save with state
          </Button>
        </div>
        <p className="text-xs text-text-secondary mt-2">
          Server validates gates (e.g. cannot close without evidence, approvals, checklist).
        </p>
      </Card>
    </div>
  );
};

export default CAPADetailPage;
