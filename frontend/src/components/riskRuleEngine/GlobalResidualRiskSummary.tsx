import React from 'react';
import type { GlobalResidualRiskSummary } from '../../services/riskRuleEngineApi';
import { Typography, Paper, Chip } from '@mui/material';

export function GlobalResidualRiskSummaryPanel({ data }: { data: GlobalResidualRiskSummary | null }) {
  if (!data) {
    return (
      <Paper sx={{ p: 2 }}>
        <Typography variant="body2" color="text.secondary">
          No summary loaded. Configure criteria and run “Evaluate all rows” on the FMEA page.
        </Typography>
      </Paper>
    );
  }

  const rs = data.residual_summary;
  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Global residual risk summary
      </Typography>
      <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
        Criteria version v{data.criteria_version} · {data.total_rows} FMEA rows
      </Typography>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div>
          <Typography variant="caption" color="text.secondary">
            Acceptable
          </Typography>
          <Typography variant="h5">{rs.acceptable}</Typography>
        </div>
        <div>
          <Typography variant="caption" color="text.secondary">
            ALARP
          </Typography>
          <Typography variant="h5">{rs.alarp}</Typography>
        </div>
        <div>
          <Typography variant="caption" color="text.secondary">
            Unacceptable
          </Typography>
          <Typography variant="h5" color="error">
            {rs.unacceptable}
          </Typography>
        </div>
        <div>
          <Typography variant="caption" color="text.secondary">
            Unknown / not evaluated
          </Typography>
          <Typography variant="h5">{rs.unknown}</Typography>
        </div>
      </div>
      <div className="flex flex-wrap gap-2 mt-3">
        <Chip label={`Benefit-risk: ${data.benefit_risk_required_count}`} size="small" />
        <Chip label={`Approval blocked: ${data.approval_blocked_count}`} size="small" color="warning" />
        <Chip label={`Critical function: ${data.critical_function_count}`} size="small" />
      </div>
      {data.global_residual_acceptability ? (
        <div className="mt-4 rounded-md border border-gray-200 bg-gray-50 p-3">
          <Typography variant="subtitle2" gutterBottom>
            Overall residual risk acceptability
            {data.global_residual_acceptability.policy_applied === false ? (
              <Typography component="span" variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                (aggregate policy off — configure criteria or enable in special_rules)
              </Typography>
            ) : null}
          </Typography>
          <Chip
            size="small"
            color={data.global_residual_acceptability.overall_acceptable ? 'success' : 'error'}
            label={data.global_residual_acceptability.overall_acceptable ? 'Acceptable (aggregate)' : 'Not acceptable (aggregate)'}
            sx={{ mb: 1 }}
          />
          {data.global_residual_acceptability.blockers?.length ? (
            <ul className="text-sm list-disc pl-5 space-y-1 text-red-900">
              {data.global_residual_acceptability.blockers.map((b, i) => (
                <li key={i}>{b}</li>
              ))}
            </ul>
          ) : null}
          {data.global_residual_acceptability.decision_path?.length ? (
            <div className="mt-2 text-xs text-gray-600 space-y-1">
              {data.global_residual_acceptability.decision_path.map((line, i) => (
                <div key={i}>{line}</div>
              ))}
            </div>
          ) : null}
        </div>
      ) : null}
      {data.top_unresolved_risks?.length ? (
        <div className="mt-4">
          <Typography variant="subtitle2" gutterBottom>
            Top unresolved / escalated
          </Typography>
          <ul className="text-sm list-disc pl-5 space-y-1">
            {data.top_unresolved_risks.slice(0, 8).map((r, i) => (
              <li key={i}>
                <span className="font-mono text-xs">{String(r.fmea_row_id).slice(0, 8)}…</span> —{' '}
                {String(r.residual_risk_classification)} — RPN {String(r.residual_rpn ?? '—')}{' '}
                {r.failure_mode ? `· ${String(r.failure_mode).slice(0, 80)}` : ''}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </Paper>
  );
}
