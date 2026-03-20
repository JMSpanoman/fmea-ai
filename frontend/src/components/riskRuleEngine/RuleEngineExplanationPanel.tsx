import React from 'react';
import { Box, Typography, Divider } from '@mui/material';

export type EnginePhaseResult = {
  ok?: boolean;
  classification?: string | null;
  risk_score?: number | null;
  benefit_risk_required?: boolean;
  benefit_risk_formal_approval_required?: boolean;
  benefit_risk_structured_workflow_active?: boolean;
  benefit_risk_documentation_gates_active?: boolean;
  benefit_risk_multi_party_approval_required?: boolean;
  reviewer_justification_required?: boolean;
  cross_functional_review_required?: boolean;
  formal_release_approval_required?: boolean;
  residual_acceptable_rationale_required?: boolean;
  residual_alarp_feasibility_attestations_required?: boolean;
  approval_blocked?: boolean;
  acceptable_for_release?: boolean;
  release_status?: string;
  release_blockers?: string[];
  critical_function_flag?: boolean;
  critical_hazard_category_match?: boolean;
  system_level_verification_required?: boolean;
  input_fmea_severity?: number | null;
  evaluated_fmea_severity?: number | null;
  matched_rules?: string[];
  decision_path?: string[];
  validation_errors?: string[];
  matrix_indices?: { severity?: number; probability?: number };
};

function PhaseBlock({ title, data }: { title: string; data?: EnginePhaseResult | null }) {
  if (!data) {
    return (
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle2" fontWeight={600}>
          {title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Not evaluated yet.
        </Typography>
      </Box>
    );
  }
  if (data.ok === false) {
    return (
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle2" fontWeight={600} color="error">
          {title} — validation failed
        </Typography>
        <ul className="list-disc pl-5 text-sm text-red-800">
          {(data.validation_errors || []).map((e, i) => (
            <li key={i}>{e}</li>
          ))}
        </ul>
      </Box>
    );
  }
  return (
    <Box sx={{ mb: 2 }}>
      <Typography variant="subtitle2" fontWeight={600}>
        {title}
      </Typography>
      <Typography variant="body2" sx={{ mt: 0.5 }}>
        <strong>Classification:</strong> {data.classification ?? '—'}
      </Typography>
      <Typography variant="body2">
        <strong>Risk score (S×O×D path):</strong> {data.risk_score ?? '—'}
      </Typography>
      {data.input_fmea_severity != null || data.evaluated_fmea_severity != null ? (
        <Typography variant="body2" color="text.secondary">
          FMEA severity (input → evaluated): {data.input_fmea_severity ?? '—'} → {data.evaluated_fmea_severity ?? '—'}
        </Typography>
      ) : null}
      {data.matrix_indices ? (
        <Typography variant="body2" color="text.secondary">
          Matrix indices S{data.matrix_indices.severity ?? '—'} × P{data.matrix_indices.probability ?? '—'}
        </Typography>
      ) : null}
      <Typography variant="caption" display="block" sx={{ mt: 1, color: 'text.secondary' }}>
        Benefit-risk: {data.benefit_risk_required ? 'Yes' : 'No'} · Formal B-R approval required:{' '}
        {data.benefit_risk_formal_approval_required ? 'Yes' : 'No'} · B-R structured workflow:{' '}
        {data.benefit_risk_structured_workflow_active ? 'Yes' : 'No'} · B-R doc gates:{' '}
        {data.benefit_risk_documentation_gates_active ? 'Yes' : 'No'} · B-R multi-party approval:{' '}
        {data.benefit_risk_multi_party_approval_required ? 'Yes' : 'No'} · Reviewer justification:{' '}
        {data.reviewer_justification_required ? 'Yes' : 'No'} · Cross-functional review:{' '}
        {data.cross_functional_review_required ? 'Yes' : 'No'} · Formal release approval:{' '}
        {data.formal_release_approval_required ? 'Yes' : 'No'} · Residual acceptable rationale:{' '}
        {data.residual_acceptable_rationale_required ? 'Yes' : 'No'} · Residual ALARP feas. attest.:{' '}
        {data.residual_alarp_feasibility_attestations_required ? 'Yes' : 'No'} · Approval blocked:{' '}
        {data.approval_blocked ? 'Yes' : 'No'} · Acceptable for release:{' '}
        {data.acceptable_for_release ? 'Yes' : 'No'} · Critical function: {data.critical_function_flag ? 'Yes' : 'No'}{' '}
        · Critical hazard category: {data.critical_hazard_category_match ? 'Yes' : 'No'} · Sys-level V&V
        required: {data.system_level_verification_required ? 'Yes' : 'No'}
      </Typography>
      {(data.release_blockers || []).length > 0 ? (
        <>
          <Typography variant="caption" fontWeight={600} display="block" sx={{ mt: 1 }}>
            Release blockers
          </Typography>
          <ul className="list-disc pl-5 text-xs text-orange-900">
            {(data.release_blockers || []).map((b, i) => (
              <li key={i}>{b}</li>
            ))}
          </ul>
        </>
      ) : null}
      <Typography variant="caption" fontWeight={600} display="block" sx={{ mt: 1 }}>
        Rules matched
      </Typography>
      <ul className="list-disc pl-5 text-xs text-gray-700 max-h-24 overflow-y-auto">
        {(data.matched_rules || []).map((r, i) => (
          <li key={i} className="font-mono">
            {r}
          </li>
        ))}
      </ul>
      <Typography variant="caption" fontWeight={600} display="block" sx={{ mt: 1 }}>
        Decision path
      </Typography>
      <ol className="list-decimal pl-5 text-xs text-gray-700 max-h-40 overflow-y-auto space-y-0.5">
        {(data.decision_path || []).map((step, i) => (
          <li key={i}>{step}</li>
        ))}
      </ol>
    </Box>
  );
}

/**
 * Expandable audit-oriented panel — inputs come from persisted `rule_engine_result_json` on the FMEA row.
 */
export function RuleEngineExplanationPanel({
  ruleEngineResult,
}: {
  ruleEngineResult?: Record<string, unknown> | null;
}) {
  const initial = (ruleEngineResult?.initial ?? null) as EnginePhaseResult | null;
  const residual = (ruleEngineResult?.residual ?? null) as EnginePhaseResult | null;

  return (
    <Box
      sx={{
        p: 2,
        bgcolor: 'grey.50',
        borderRadius: 1,
        border: '1px solid',
        borderColor: 'grey.200',
      }}
    >
      <Typography variant="subtitle1" fontWeight={700} gutterBottom>
        Why? — Rule engine trace
      </Typography>
      <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1 }}>
        Deterministic evaluation from approved (or latest) project risk criteria. AI suggestions are not used in this
        path.
      </Typography>
      <Divider sx={{ my: 1 }} />
      <PhaseBlock title="Initial risk" data={initial} />
      <Divider sx={{ my: 1 }} />
      <PhaseBlock title="Residual risk" data={residual} />
    </Box>
  );
}
