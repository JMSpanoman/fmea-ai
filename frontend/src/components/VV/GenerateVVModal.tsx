/**
 * Modal that displays generated V&V test logic from an FMEA/risk row.
 * Supports copy-all and save-to-project. Displays verification, validation,
 * acceptance criteria, calculations (with formula/inputs/unit), worst-case,
 * sample size rationale, and full traceability.
 */
import React, { useState } from 'react';
import type { VVFromRiskGenerateResponse, VVFromRiskCalculationItem } from '../../types';
import { saveVVFromRisk } from '../../services/vvFromRiskApi';

interface GenerateVVModalProps {
  open: boolean;
  onClose: () => void;
  data: VVFromRiskGenerateResponse | null;
  loading: boolean;
  error: string | null;
  onRetry?: () => void;
  /** For save: project id and optional fmea_row_id */
  projectId?: string | null;
  fmeaRowId?: string | null;
  riskItemId?: string | null;
}

function section(title: string, content: React.ReactNode) {
  return (
    <div className="mb-4">
      <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5">{title}</h4>
      <div className="text-sm text-gray-900">{content}</div>
    </div>
  );
}

function safeList<T>(arr: T[] | undefined | null): T[] {
  return Array.isArray(arr) ? arr : [];
}

function safeStr(s: string | undefined | null): string {
  return typeof s === 'string' ? s : '';
}

export function GenerateVVModal({
  open,
  onClose,
  data,
  loading,
  error,
  onRetry,
  projectId,
  fmeaRowId,
  riskItemId,
}: GenerateVVModalProps) {
  const [copyDone, setCopyDone] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveDone, setSaveDone] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const handleCopy = async () => {
    if (!data) return;
    const ac = safeList(data.acceptance_criteria);
    const calcs = safeList(data.calculations);
    const wcc = safeList(data.worst_case_conditions);
    const trace = data.traceability || {} as any;
    const validationName = safeStr(data.validation_test_name);
    const validationObj = safeStr(data.validation_objective);
    const validationMethod = safeStr(data.validation_method_or_scenario || data.validation_scenario);

    const lines: string[] = [
      '=== Verification Test Case ===',
      `Name: ${data.verification_test_name}`,
      `Objective: ${data.verification_objective}`,
      `Method: ${data.verification_method}`,
      '',
      '=== Validation Test Case ===',
      validationName ? `Name: ${validationName}` : '',
      validationObj ? `Objective: ${validationObj}` : '',
      validationMethod ? `Method/Scenario: ${validationMethod}` : '',
      '',
      '=== Acceptance Criteria ===',
      ...ac.map((c) => `- ${c}`),
      '',
      '=== Calculations ===',
      ...calcs.map((c: VVFromRiskCalculationItem) => {
        const parts = [`${c.name}: ${c.formula}`];
        if (c.description) parts.push(`  Description: ${c.description}`);
        if (c.inputs?.length) parts.push(`  Inputs: ${c.inputs.join(', ')}`);
        if (c.unit_or_threshold) parts.push(`  Unit/Threshold: ${c.unit_or_threshold}`);
        return parts.join('\n');
      }),
      '',
      '=== Worst-Case Conditions ===',
      ...wcc.map((w) => `- ${w}`),
      '',
      data.sample_size_rationale ? `Sample Size Rationale: ${data.sample_size_rationale}` : '',
      '',
      '=== Traceability ===',
      `Component: ${trace.source_component ?? ''}`,
      `Failure Mode: ${trace.source_failure_mode ?? ''}`,
      `Effect: ${trace.source_effect ?? ''}`,
      `Cause: ${trace.source_cause ?? ''}`,
      `Mitigation: ${trace.source_mitigation ?? ''}`,
      `Severity: ${trace.source_severity ?? ''}`,
      `Occurrence: ${trace.source_occurrence ?? ''}`,
      `Detection: ${trace.source_detection ?? ''}`,
      `RPN: ${trace.source_rpn ?? ''}`,
      `Residual severity: ${trace.source_residual_severity ?? ''}`,
      `Residual occurrence: ${trace.source_residual_occurrence ?? ''}`,
      `Residual detection: ${trace.source_residual_detection ?? ''}`,
      `Residual RPN: ${trace.source_residual_rpn ?? ''}`,
    ];
    const text = lines.filter(Boolean).join('\n');
    try {
      await navigator.clipboard.writeText(text);
      setCopyDone(true);
      setTimeout(() => setCopyDone(false), 2000);
    } catch {
      setCopyDone(false);
    }
  };

  const handleSave = async () => {
    if (!data || !projectId) return;
    setSaving(true);
    setSaveError(null);
    try {
      await saveVVFromRisk({
        project_id: projectId,
        fmea_row_id: fmeaRowId ?? undefined,
        risk_item_id: riskItemId ?? undefined,
        verification_test_name: data.verification_test_name,
        verification_objective: data.verification_objective,
        verification_method: data.verification_method,
        validation_test_name: data.validation_test_name ?? undefined,
        validation_objective: data.validation_objective ?? undefined,
        validation_method_or_scenario: data.validation_method_or_scenario ?? data.validation_scenario ?? undefined,
        validation_scenario: data.validation_scenario ?? data.validation_method_or_scenario ?? '',
        acceptance_criteria: safeList(data.acceptance_criteria),
        calculations: safeList(data.calculations),
        worst_case_conditions: safeList(data.worst_case_conditions),
        sample_size_rationale: data.sample_size_rationale ?? undefined,
        traceability: data.traceability,
      });
      setSaveDone(true);
      setTimeout(() => setSaveDone(false), 3000);
    } catch (e: any) {
      setSaveError(e?.message || 'Failed to save');
    } finally {
      setSaving(false);
    }
  };

  if (!open) return null;

  const ac = safeList(data?.acceptance_criteria);
  const calcs = safeList(data?.calculations);
  const wcc = safeList(data?.worst_case_conditions);
  const trace = data?.traceability;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" onClick={onClose}>
      <div
        className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Generate V&V from Risk</h2>
          <button
            type="button"
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 p-1"
            aria-label="Close"
          >
            ×
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-4">
          {loading && (
            <div className="flex flex-col items-center justify-center py-12 text-gray-500">
              <div className="animate-spin rounded-full h-10 w-10 border-2 border-primary border-t-transparent mb-3" />
              <p>Generating V&V test logic…</p>
            </div>
          )}

          {error && (
            <div className="py-6">
              <p className="text-red-600 mb-3">{error}</p>
              {onRetry && (
                <button
                  type="button"
                  onClick={onRetry}
                  className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90"
                >
                  Retry
                </button>
              )}
            </div>
          )}

          {!loading && !error && data && (
            <>
              {section('1. Verification Test Case', (
                <div className="space-y-1">
                  <p className="font-medium">{data.verification_test_name}</p>
                  <p><span className="text-gray-600">Objective:</span> {data.verification_objective}</p>
                  <p><span className="text-gray-600">Method:</span> {data.verification_method}</p>
                </div>
              ))}

              {(data.validation_test_name || data.validation_objective || data.validation_method_or_scenario || data.validation_scenario) && section('2. Validation Test Case', (
                <div className="space-y-1">
                  {data.validation_test_name && <p className="font-medium">{data.validation_test_name}</p>}
                  {data.validation_objective && <p><span className="text-gray-600">Objective:</span> {data.validation_objective}</p>}
                  <p><span className="text-gray-600">Method/Scenario:</span> {data.validation_method_or_scenario || data.validation_scenario || '—'}</p>
                </div>
              ))}

              {section('3. Acceptance Criteria', (
                <ul className="list-disc list-inside space-y-1">
                  {ac.length > 0 ? ac.map((c, i) => <li key={i}>{c}</li>) : <li className="text-gray-500">None specified</li>}
                </ul>
              ))}

              {section('4. Calculations', (
                <div className="space-y-4">
                  {calcs.length > 0 ? (
                    calcs.map((c, i) => (
                      <div key={i} className="rounded-lg border border-amber-200 bg-amber-50/60 p-3">
                        <p className="font-semibold text-amber-900">{c.name}</p>
                        <p className="font-mono text-sm bg-white border border-amber-100 rounded px-2 py-1 my-1">{c.formula}</p>
                        {c.description && <p className="text-gray-700 text-xs mt-1">{c.description}</p>}
                        {c.inputs?.length ? <p className="text-gray-600 text-xs mt-1">Inputs: {c.inputs.join(', ')}</p> : null}
                        {c.unit_or_threshold && <p className="text-gray-600 text-xs mt-1">Unit/Threshold: {c.unit_or_threshold}</p>}
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500 text-sm">None specified</p>
                  )}
                </div>
              ))}

              {section('5. Worst-Case Conditions', (
                <ul className="list-disc list-inside space-y-1">
                  {wcc.length > 0 ? wcc.map((w, i) => <li key={i}>{w}</li>) : <li className="text-gray-500">None specified</li>}
                </ul>
              ))}

              {data.sample_size_rationale && section('6. Sample Size Rationale', <p>{data.sample_size_rationale}</p>)}

              {section('7. Traceability', (
                <div className="text-xs space-y-1 grid grid-cols-2 gap-x-4">
                  <p><span className="text-gray-500">Component:</span> {trace?.source_component ?? '—'}</p>
                  <p><span className="text-gray-500">Failure mode:</span> {trace?.source_failure_mode ?? '—'}</p>
                  <p><span className="text-gray-500">Effect:</span> {trace?.source_effect ?? '—'}</p>
                  <p><span className="text-gray-500">Cause:</span> {trace?.source_cause ?? '—'}</p>
                  <p><span className="text-gray-500">Mitigation:</span> {trace?.source_mitigation ?? '—'}</p>
                  <p><span className="text-gray-500">Severity:</span> {trace?.source_severity ?? '—'}</p>
                  <p><span className="text-gray-500">Occurrence:</span> {trace?.source_occurrence ?? '—'}</p>
                  <p><span className="text-gray-500">Detection:</span> {trace?.source_detection ?? '—'}</p>
                  <p><span className="text-gray-500">RPN:</span> {trace?.source_rpn ?? '—'}</p>
                  <p><span className="text-gray-500">Residual severity:</span> {trace?.source_residual_severity ?? '—'}</p>
                  <p><span className="text-gray-500">Residual occurrence:</span> {trace?.source_residual_occurrence ?? '—'}</p>
                  <p><span className="text-gray-500">Residual detection:</span> {trace?.source_residual_detection ?? '—'}</p>
                  <p><span className="text-gray-500">Residual RPN:</span> {trace?.source_residual_rpn ?? '—'}</p>
                </div>
              ))}
            </>
          )}
        </div>

        {!loading && !error && data && (
          <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between gap-3">
            <button
              type="button"
              onClick={handleCopy}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm hover:bg-gray-50"
            >
              {copyDone ? 'Copied' : 'Copy all'}
            </button>
            <div className="flex items-center gap-2">
              {projectId && (
                <button
                  type="button"
                  onClick={handleSave}
                  disabled={saving}
                  className="px-4 py-2 bg-green-600 text-white rounded-md text-sm hover:bg-green-700 disabled:opacity-50"
                >
                  {saving ? 'Saving…' : saveDone ? 'Saved' : 'Save to project'}
                </button>
              )}
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 bg-primary text-white rounded-md text-sm hover:bg-primary/90"
              >
                Close
              </button>
            </div>
          </div>
        )}
        {saveError && (
          <div className="px-6 py-2 text-sm text-red-600">{saveError}</div>
        )}
      </div>
    </div>
  );
}
