import React, { useCallback, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Button, MenuItem, Select, FormControl, InputLabel, Typography, Alert, Paper } from '@mui/material';
import {
  riskRuleEngineApi,
  type GlobalResidualRiskSummary,
  type ProjectRiskCriteria,
} from '../services/riskRuleEngineApi';
import { RiskCriteriaEditor } from '../components/riskRuleEngine/RiskCriteriaEditor';
import { GlobalResidualRiskSummaryPanel } from '../components/riskRuleEngine/GlobalResidualRiskSummary';

export default function ProjectRiskRuleCriteriaPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const [list, setList] = useState<ProjectRiskCriteria[]>([]);
  const [selectedId, setSelectedId] = useState<string>('');
  const [summary, setSummary] = useState<GlobalResidualRiskSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [approveMsg, setApproveMsg] = useState<string | null>(null);

  const selected = list.find((c) => c.id === selectedId) || null;

  const refresh = useCallback(async () => {
    if (!projectId) return;
    setLoading(true);
    setError(null);
    try {
      const [rows, sum] = await Promise.all([
        riskRuleEngineApi.listCriteria(projectId),
        riskRuleEngineApi.globalSummary(projectId).catch(() => null),
      ]);
      setList(rows);
      setSummary(sum);
      setSelectedId((prev) => {
        if (rows.find((r) => r.id === prev)) return prev;
        return rows[0]?.id || '';
      });
    } catch (e: any) {
      setError(e?.message || 'Failed to load risk criteria');
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleSeed = async () => {
    if (!projectId) return;
    setLoading(true);
    setError(null);
    try {
      const created = await riskRuleEngineApi.seedCriteria(projectId, 'iso14971_default_pacemaker');
      await refresh();
      setSelectedId(created.id);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Seed failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (patch: Partial<ProjectRiskCriteria>) => {
    if (!projectId || !selected) return;
    await riskRuleEngineApi.updateCriteria(projectId, selected.id, patch);
    await refresh();
  };

  const handleApprove = async () => {
    if (!projectId || !selected) return;
    setApproveMsg(null);
    setLoading(true);
    try {
      await riskRuleEngineApi.approveCriteria(projectId, selected.id, {
        approved_via: 'risk_rule_criteria_ui',
        at: new Date().toISOString(),
      });
      setApproveMsg('Criteria approved. Older approved versions were archived.');
      await refresh();
    } catch (e: any) {
      const d = e?.response?.data?.detail;
      if (d?.errors) {
        setError(`Approval blocked: ${d.message || 'validation'} — ${(d.errors as string[]).join('; ')}`);
      } else {
        setError(typeof d === 'string' ? d : e?.message || 'Approve failed');
      }
    } finally {
      setLoading(false);
    }
  };

  if (!projectId) {
    return <Alert severity="info">Missing project</Alert>;
  }

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Typography variant="h5" fontWeight={700}>
            Risk acceptability rule engine
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Versioned matrix + special rules for deterministic FMEA classification (no AI in the decision path).
          </Typography>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button component={Link} to={`/projects/${projectId}/fmea`} variant="outlined" size="small">
            Back to FMEA
          </Button>
          <Button variant="outlined" size="small" onClick={() => refresh()} disabled={loading}>
            Refresh
          </Button>
          <Button variant="contained" size="small" onClick={handleSeed} disabled={loading}>
            Seed ISO + pacemaker template
          </Button>
        </div>
      </div>

      {error ? (
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      ) : null}
      {approveMsg ? <Alert severity="success">{approveMsg}</Alert> : null}

      <GlobalResidualRiskSummaryPanel data={summary} />

      <Paper sx={{ p: 2 }}>
        <Typography variant="subtitle1" fontWeight={600} gutterBottom>
          Criteria versions
        </Typography>
        {list.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            No criteria yet. Click <strong>Seed ISO + pacemaker template</strong> to create a draft v1.
          </Typography>
        ) : (
          <FormControl size="small" sx={{ minWidth: 320 }}>
            <InputLabel>Version</InputLabel>
            <Select
              label="Version"
              value={selectedId}
              onChange={(e) => setSelectedId(String(e.target.value))}
            >
              {list.map((c) => (
                <MenuItem key={c.id} value={c.id}>
                  v{c.version} — {c.status}
                  {c.evaluation_method ? ` (${c.evaluation_method})` : ''}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}

        {selected ? (
          <div className="mt-4 space-y-3">
            <div className="flex flex-wrap gap-2">
              {selected.status === 'draft' ? (
                <Button variant="contained" color="secondary" onClick={handleApprove} disabled={loading}>
                  Approve criteria
                </Button>
              ) : (
                <Typography variant="caption" color="text.secondary">
                  Approved/archived versions are read-only in this editor. Create a new draft via API or future “new
                  version” action.
                </Typography>
              )}
            </div>
            <RiskCriteriaEditor
              criteria={selected}
              readOnly={selected.status !== 'draft'}
              onSave={handleSave}
            />
          </div>
        ) : null}
      </Paper>
    </div>
  );
}
