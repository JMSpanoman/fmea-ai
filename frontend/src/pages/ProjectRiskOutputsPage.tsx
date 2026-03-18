import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { DataTable } from '../components/ui/DataTable';
import {
  projectRiskOutputsApi,
  FmeaRow,
  HazardAnalysisRow,
  RiskAnalysisRow,
  RiskControlTraceabilityRow,
  VerificationTraceabilityRow,
  ResidualRiskRow,
  RiskManagementReportDraft,
} from '../services/projectRiskOutputsApi';

type TabId =
  | 'fmea'
  | 'hazard'
  | 'risk'
  | 'control-trace'
  | 'verification-trace'
  | 'residual'
  | 'rmr';

const TABS: { id: TabId; label: string }[] = [
  { id: 'fmea', label: 'FMEA Table' },
  { id: 'hazard', label: 'Hazard Analysis' },
  { id: 'risk', label: 'Risk Analysis' },
  { id: 'control-trace', label: 'Risk Control Traceability' },
  { id: 'verification-trace', label: 'Verification Traceability' },
  { id: 'residual', label: 'Residual Risk Evaluation' },
  { id: 'rmr', label: 'Risk Management Report (draft)' },
];

export default function ProjectRiskOutputsPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabId>('fmea');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fmeaRows, setFmeaRows] = useState<FmeaRow[]>([]);
  const [hazardRows, setHazardRows] = useState<HazardAnalysisRow[]>([]);
  const [riskRows, setRiskRows] = useState<RiskAnalysisRow[]>([]);
  const [controlTraceRows, setControlTraceRows] = useState<RiskControlTraceabilityRow[]>([]);
  const [verificationTraceRows, setVerificationTraceRows] = useState<VerificationTraceabilityRow[]>([]);
  const [residualRows, setResidualRows] = useState<ResidualRiskRow[]>([]);
  const [rmrDraft, setRmrDraft] = useState<RiskManagementReportDraft | null>(null);

  const loadAll = useCallback(async () => {
    if (!projectId) return;
    setLoading(true);
    setError(null);
    try {
      const [fmea, hazard, risk, controlTrace, verificationTrace, residual, rmr] = await Promise.all([
        projectRiskOutputsApi.getFmeaTable(projectId),
        projectRiskOutputsApi.getHazardAnalysisTable(projectId),
        projectRiskOutputsApi.getRiskAnalysisTable(projectId),
        projectRiskOutputsApi.getRiskControlTraceabilityTable(projectId),
        projectRiskOutputsApi.getVerificationTraceabilityTable(projectId),
        projectRiskOutputsApi.getResidualRiskEvaluationTable(projectId),
        projectRiskOutputsApi.getRiskManagementReportDraft(projectId),
      ]);
      setFmeaRows(fmea);
      setHazardRows(hazard);
      setRiskRows(risk);
      setControlTraceRows(controlTrace);
      setVerificationTraceRows(verificationTrace);
      setResidualRows(residual);
      setRmrDraft(rmr);
    } catch (e) {
      console.error(e);
      setError('Failed to load risk outputs. Ensure you have accepted component suggestions.');
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  if (!projectId) {
    return (
      <div className="p-4">
        <p>Missing project.</p>
        <Button onClick={() => navigate('/projects')}>Back to projects</Button>
      </div>
    );
  }

  return (
    <div className="p-4 max-w-7xl mx-auto">
      <PageHeader
        title="Risk outputs"
        subtitle="Structured tables and draft report from project risk items (Phase 4)"
      />
      <div className="flex gap-2 mb-4">
        <Button variant="secondary" onClick={() => navigate(`/projects/${projectId}/dashboard`)}>
          Back to project
        </Button>
        <Button variant="secondary" onClick={loadAll} disabled={loading}>
          {loading ? 'Loading…' : 'Refresh'}
        </Button>
      </div>

      {error && (
        <Card className="p-4 mb-4 bg-red-50 border-red-200 text-red-800">
          {error}
        </Card>
      )}

      <div className="flex flex-wrap gap-2 mb-4 border-b border-border pb-2">
        {TABS.map(({ id, label }) => (
          <button
            key={id}
            type="button"
            onClick={() => setActiveTab(id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              activeTab === id
                ? 'bg-primary text-white'
                : 'bg-surface-secondary text-text-secondary hover:bg-surface-secondary/80'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {loading && !fmeaRows.length && !rmrDraft ? (
        <Card className="p-8 text-center text-text-secondary">Loading risk outputs…</Card>
      ) : (
        <>
          {activeTab === 'fmea' && (
            <Card className="overflow-hidden">
              <h3 className="p-3 border-b border-border font-semibold">FMEA Table</h3>
              <div className="overflow-x-auto">
                <DataTable
                  data={fmeaRows}
                  columns={[
                    { key: 'row_number', header: '#' },
                    { key: 'component', header: 'Component' },
                    { key: 'failure_mode', header: 'Failure Mode' },
                    { key: 'effect', header: 'Effect' },
                    { key: 'cause', header: 'Cause' },
                    { key: 'severity', header: 'Severity' },
                    { key: 'probability', header: 'Probability' },
                    { key: 'detectability', header: 'Detectability' },
                    { key: 'risk_score', header: 'Risk Score' },
                    { key: 'risk_control', header: 'Risk Control' },
                    { key: 'verification', header: 'Verification' },
                    { key: 'residual_risk', header: 'Residual Risk' },
                  ]}
                  emptyMessage="No FMEA data. Accept component suggestions to generate."
                />
              </div>
            </Card>
          )}

          {activeTab === 'hazard' && (
            <Card className="overflow-hidden">
              <h3 className="p-3 border-b border-border font-semibold">Hazard Analysis Table</h3>
              <DataTable
                data={hazardRows}
                columns={[
                  { key: 'row_number', header: '#' },
                  { key: 'hazard', header: 'Hazard' },
                  { key: 'hazardous_situation', header: 'Hazardous Situation' },
                  { key: 'harm', header: 'Harm' },
                  { key: 'sequence_of_events', header: 'Sequence of Events' },
                  { key: 'severity', header: 'Severity' },
                  { key: 'probability', header: 'Probability' },
                ]}
                emptyMessage="No hazard analysis data yet."
              />
            </Card>
          )}

          {activeTab === 'risk' && (
            <Card className="overflow-hidden">
              <h3 className="p-3 border-b border-border font-semibold">Risk Analysis Table</h3>
              <DataTable
                data={riskRows}
                columns={[
                  { key: 'row_number', header: '#' },
                  { key: 'component', header: 'Component' },
                  { key: 'failure_mode', header: 'Failure mode' },
                  { key: 'hazard', header: 'Hazard' },
                  { key: 'harm', header: 'Harm' },
                  { key: 'severity', header: 'S' },
                  { key: 'probability', header: 'P' },
                  { key: 'detectability', header: 'D' },
                  { key: 'risk_score', header: 'Risk score' },
                  { key: 'risk_acceptability', header: 'Acceptability' },
                ]}
                emptyMessage="No risk analysis data yet."
              />
            </Card>
          )}

          {activeTab === 'control-trace' && (
            <Card className="overflow-hidden">
              <h3 className="p-3 border-b border-border font-semibold">Risk Control Traceability</h3>
              <DataTable
                data={controlTraceRows}
                columns={[
                  { key: 'risk_item', header: 'Risk Item' },
                  { key: 'hazard', header: 'Hazard' },
                  { key: 'control', header: 'Control' },
                  { key: 'implementation_reference', header: 'Implementation Reference' },
                  { key: 'verification', header: 'Verification' },
                  { key: 'evidence_reference', header: 'Evidence Reference' },
                ]}
                emptyMessage="No risk control traceability data yet."
              />
            </Card>
          )}

          {activeTab === 'verification-trace' && (
            <Card className="overflow-hidden">
              <h3 className="p-3 border-b border-border font-semibold">Verification Traceability</h3>
              <DataTable
                data={verificationTraceRows}
                columns={[
                  { key: 'component', header: 'Component' },
                  { key: 'control_text', header: 'Control' },
                  { key: 'verification_text', header: 'Verification' },
                  { key: 'evidence_reference', header: 'Evidence reference' },
                  { key: 'status', header: 'Status' },
                ]}
                emptyMessage="No verification traceability data yet."
              />
            </Card>
          )}

          {activeTab === 'residual' && (
            <Card className="overflow-hidden">
              <h3 className="p-3 border-b border-border font-semibold">Residual Risk Evaluation</h3>
              <DataTable
                data={residualRows}
                columns={[
                  { key: 'row_number', header: '#' },
                  { key: 'risk_item', header: 'Risk Item' },
                  { key: 'initial_risk', header: 'Initial Risk' },
                  { key: 'controls_applied', header: 'Controls Applied' },
                  { key: 'residual_severity', header: 'Residual Severity' },
                  { key: 'residual_probability', header: 'Residual Probability' },
                  { key: 'residual_risk_score', header: 'Residual Risk Score' },
                  { key: 'acceptable', header: 'Acceptable?' },
                ]}
                emptyMessage="No residual risk data yet."
              />
            </Card>
          )}

          {activeTab === 'rmr' && (
            <Card className="p-4">
              <h3 className="font-semibold mb-2">Draft Risk Management Report</h3>
              {rmrDraft?.stats && (
                <p className="text-sm text-text-secondary mb-3">
                  Risk items: {rmrDraft.stats.risk_items_count} · Hazard rows: {rmrDraft.stats.hazard_rows_count} ·
                  FMEA rows: {rmrDraft.stats.fmea_rows_count} · Residual rows: {rmrDraft.stats.residual_rows_count}
                </p>
              )}
              <pre className="whitespace-pre-wrap font-sans text-sm bg-surface-secondary p-4 rounded-lg overflow-x-auto max-h-[70vh] overflow-y-auto">
                {rmrDraft?.full_draft ?? 'No draft content. Accept component suggestions to generate.'}
              </pre>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
