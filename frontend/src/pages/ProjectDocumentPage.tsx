import React, { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import api from '../axios';
import authService from '../services/authService';
import { documentsApi } from '../services/apiPhase3';
import { componentsApi, projectInitializeApi, projectsApi } from '../services/apiPhase1';
import type { Document } from '../types';
import DocumentGuidanceHeader from '../components/documents/DocumentGuidanceHeader';
import { ReportHeader } from '../components/reports/ReportHeader';
import { SummaryCards } from '../components/reports/SummaryCards';
import { ReportSection } from '../components/reports/ReportSection';
import { TopRisksPanel, type TopRiskItem } from '../components/reports/TopRisksPanel';
import { RiskSummaryChart } from '../components/reports/RiskSummaryChart';
import { RiskMatrix, buildFmeaSoGrid } from '../components/reports/RiskMatrix';
import { AuditTrail } from '../components/reports/AuditTrail';
import { RiskBadge, rpnToLevel } from '../components/reports/RiskBadge';
import { buildReportPreviewTableCss } from '../components/reports/reportPreviewTableStyles';
import { parseTopRisksFromPreviewHtml, parseQualitativeRiskBands } from '../utils/parseReportPreviewTopRisks';
import {
  analyzeFmeaCompliance,
  rowMatchesFilter,
  SAVED_VIEW_PRESETS,
  type RiskRowFilter,
  type SavedReportView,
} from '../components/reports/reportFmeaCompliance';
import { ReportViewToolbar } from '../components/reports/ReportViewToolbar';
import { ComplianceChecklistPanel } from '../components/reports/ComplianceChecklistPanel';
import { ReportDiffView } from '../components/reports/ReportDiffView';
import { VersionSelector } from '../components/reports/VersionSelector';
import { parseFmeaTableFromHtml } from '../utils/parseFmeaTableFromHtml';

type Tab = 'edit' | 'preview';
type VersionScope = 'approved_only' | 'current' | 'all';

type ComponentDraft = {
  name: string;
  description?: string;
};

type ParsedFmeaRow = {
  failureMode: string;
  effect: string;
  cause: string;
  mitigation: string;
  rpn: number;
  residualRpn: number;
  /** Severity / occurrence / detection (export columns S, O, D) */
  s: number;
  o: number;
  d: number;
  hazard?: string;
};

type PreviewTableStats = {
  rowCount: number;
  columnCount: number;
};

export default function ProjectDocumentPage() {
  const { projectId, docId } = useParams<{ projectId: string; docId: string }>();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string>('');
  // Default to Preview when opening documents (users can switch to Edit when needed).
  const [tab, setTab] = useState<Tab>('preview');
  const [doc, setDoc] = useState<Document | null>(null);
  const [name, setName] = useState('');
  const [status, setStatus] = useState<Document['status']>('draft');
  const [content, setContent] = useState('');
  const [previewHtml, setPreviewHtml] = useState<string>('');
  const [didInitFmea, setDidInitFmea] = useState(false);
  const [projectName, setProjectName] = useState<string>('');

  // Add Component modal state (FMEA docs)
  const [showAddComponent, setShowAddComponent] = useState(false);
  const [componentDrafts, setComponentDrafts] = useState<ComponentDraft[]>([{ name: '', description: '' }]);
  const [addComponentBulk, setAddComponentBulk] = useState('');
  const [addComponentInfo, setAddComponentInfo] = useState<string>('');

  // Generate New modal state
  const [showGenerate, setShowGenerate] = useState(false);
  const [genComponentInput, setGenComponentInput] = useState('');
  const [genComponents, setGenComponents] = useState<string[]>([]);
  const [versionScope, setVersionScope] = useState<VersionScope>('approved_only');
  const [rmpScope, setRmpScope] = useState('');
  const [rmpIntendedUse, setRmpIntendedUse] = useState('');
  const [rmpReviewRoles, setRmpReviewRoles] = useState<Record<string, string>>({
    risk_manager: 'required',
    design_lead: 'required',
    quality_lead: 'required',
    approver: 'required',
  });
  const [genOptions, setGenOptions] = useState<Record<string, any>>({
    include_traceability: true,
    include_ai_events: false,
    include_audit_log: false,
    include_unapproved: false,
    active_controls_only: true,
    acceptability_profile: 'default_med_device',
  });
  const [benefitRiskDecision, setBenefitRiskDecision] = useState('Not fully evaluable');
  const [benefitRiskRationale, setBenefitRiskRationale] = useState('');
  const [approvalAuthor, setApprovalAuthor] = useState('');
  const [approvalReviewer, setApprovalReviewer] = useState('');
  const [approvalApprover, setApprovalApprover] = useState('');
  const [approvalDate, setApprovalDate] = useState('');
  const [approvalVersion, setApprovalVersion] = useState('');
  const [approvalIssuanceState, setApprovalIssuanceState] = useState('Draft');

  /** Report preview: saved layout presets + FMEA row filter + compliance overlay (defaults match prior “show all” behavior). */
  const [savedView, setSavedView] = useState<SavedReportView>('engineering');
  const [riskFilter, setRiskFilter] = useState<RiskRowFilter>('all');
  const [complianceMode, setComplianceMode] = useState(false);

  // Versions (optional)
  const [showVersions, setShowVersions] = useState(false);
  const [versionsLoading, setVersionsLoading] = useState(false);
  const [versionsError, setVersionsError] = useState<string>('');
  const [versions, setVersions] = useState<any[]>([]);
  const [selectedVersionNo, setSelectedVersionNo] = useState<number | null>(null);

  /** FMEA version comparison (HTML snapshots — see ReportDiffView / parseFmeaTableFromHtml integration notes). */
  const [showCompare, setShowCompare] = useState(false);
  const [compareLeft, setCompareLeft] = useState<number | 'current'>('current');
  const [compareRight, setCompareRight] = useState<number | 'current'>('current');
  const [compareLoading, setCompareLoading] = useState(false);
  const [compareError, setCompareError] = useState('');
  const [compareHideUnchanged, setCompareHideUnchanged] = useState(false);
  const [diffResult, setDiffResult] = useState<{
    leftHtml: string;
    rightHtml: string;
    leftLabel: string;
    rightLabel: string;
  } | null>(null);

  /** Host for post-render FMEA RPN cell classes (preview HTML is not React-controlled). */
  const previewHostRef = useRef<HTMLDivElement | null>(null);

  const finalProjectId = projectId || '';
  const finalDocId = docId || '';

  const title = useMemo(() => doc?.name || 'Document', [doc]);
  const docType = (doc?.type || '').toLowerCase();
  const isCapa = docType === 'capa';
  const isRmf = docType === 'rmf';
  const isFmea = docType === 'fmea';
  const isHazardAnalysis = docType === 'hazard_analysis';
  const isRiskReportDoc = ['fmea', 'hazard_analysis', 'residual_risk', 'benefit_risk_analysis', 'risk_controls_doc'].includes(docType);
  /** Human-readable type for the executive header — keep in sync with docs registry labels. */
  const documentTypeLabel = useMemo(() => {
    const map: Record<string, string> = {
      fmea: 'Failure Mode and Effects Analysis (FMEA)',
      hazard_analysis: 'Hazard Analysis',
      residual_risk: 'Residual Risk Evaluation',
      benefit_risk_analysis: 'Benefit–Risk Analysis',
      risk_controls_doc: 'Risk Control Measures',
    };
    return map[docType] || (docType ? docType.replace(/_/g, ' ') : '');
  }, [docType]);
  const hasAiSample = Boolean((doc as any)?.ai_metadata?.ai_sample_generated || (doc as any)?.ai_metadata?.default_sample_provided);
  const missingSetupMessage = 'Project setup information is missing. Complete Project Setup to generate better examples.';

  function normalize(s: string | null | undefined) {
    return (s || '').trim();
  }

  const populationSources = useMemo(() => {
    // Optional, friendly chips in the header. Keep conservative and deterministic.
    const t = docType;
    const sources: string[] = [];
    if (!t) return sources;
    if (['rmp', 'hazard_analysis', 'design_inputs_doc', 'design_outputs_doc', 'vv_plan', 'vv_evidence', 'traceability_matrix', 'fmea', 'capa'].includes(t)) {
      sources.push('Project Setup');
      sources.push('Components');
    }
    if (['fmea', 'risk_controls_doc', 'traceability_matrix', 'residual_risk'].includes(t)) {
      sources.push('FMEA rows');
    }
    if (['risk_controls_doc', 'residual_risk'].includes(t)) {
      sources.push('Risk Controls');
      sources.push('Risk Items');
    }
    if (t === 'rmf') {
      sources.push('Compiled from other docs');
    }
    return Array.from(new Set(sources));
  }, [docType]);

  const parsedFmeaRows = useMemo<ParsedFmeaRow[]>(() => {
    if (!isFmea || !previewHtml) return [];
    try {
      return parseFmeaTableFromHtml(previewHtml).map((r) => ({
        failureMode: r.failureMode,
        effect: r.effect,
        cause: r.cause,
        mitigation: r.mitigation,
        rpn: r.rpn,
        residualRpn: r.residualRpn ?? 0,
        s: r.s,
        o: r.o,
        d: r.d,
        hazard: r.hazard,
      }));
    } catch {
      return [];
    }
  }, [isFmea, previewHtml]);

  const previewTableStats = useMemo<PreviewTableStats>(() => {
    if (!previewHtml) return { rowCount: 0, columnCount: 0 };
    try {
      // TODO: replace heuristic table stats with structured report metadata from backend export payload.
      const parser = new DOMParser();
      const html = parser.parseFromString(previewHtml, 'text/html');
      const firstTable = html.querySelector('table');
      const rowCount = firstTable ? firstTable.querySelectorAll('tbody tr').length : html.querySelectorAll('tbody tr').length;
      const columnCount = firstTable
        ? firstTable.querySelectorAll('thead tr th').length || firstTable.querySelectorAll('tbody tr:first-child td').length
        : 0;
      return { rowCount, columnCount };
    } catch {
      return { rowCount: 0, columnCount: 0 };
    }
  }, [previewHtml]);

  const riskSummary = useMemo(() => {
    const rows = parsedFmeaRows;
    const high = rows.filter((r) => r.rpn >= 100).length;
    const medium = rows.filter((r) => r.rpn >= 50 && r.rpn < 100).length;
    const low = rows.filter((r) => r.rpn > 0 && r.rpn < 50).length;
    const highest = rows.reduce((m, r) => Math.max(m, r.rpn || 0), 0);
    const highestResidual = rows.reduce((m, r) => Math.max(m, r.residualRpn || 0), 0);
    const averageRpn = rows.length
      ? Math.round(rows.reduce((sum, r) => sum + (r.rpn || 0), 0) / rows.length)
      : 0;
    const mitigationDone = rows.filter((r) => !!r.mitigation).length;
    const completion = rows.length ? Math.round((mitigationDone / rows.length) * 100) : 0;
    const topRisks: TopRiskItem[] = [...rows]
      .sort((a, b) => b.rpn - a.rpn)
      .slice(0, 6)
      .map((r) => ({
        failureMode: r.failureMode,
        effect: r.effect,
        cause: r.cause,
        rpn: r.rpn,
        mitigation: r.mitigation,
        status: r.rpn >= 100 ? 'Needs Action' : r.rpn >= 50 ? 'In Review' : 'Monitored',
        headline: r.hazard && r.hazard !== r.failureMode ? r.hazard : undefined,
      }));

    return {
      total: rows.length,
      high,
      medium,
      low,
      highest,
      highestResidual,
      averageRpn,
      completion,
      topRisks,
    };
  }, [parsedFmeaRows]);

  /** Severity × Occurrence concentration for FMEA (5×5 buckets). */
  const fmeaSoMatrixGrid = useMemo(() => {
    return buildFmeaSoGrid(parsedFmeaRows.map((r) => ({ s: r.s, o: r.o })));
  }, [parsedFmeaRows]);

  const qualitativeBands = useMemo(
    () => parseQualitativeRiskBands(previewHtml, docType),
    [previewHtml, docType]
  );

  const displayTopRisks = useMemo(() => {
    if (isFmea) return riskSummary.topRisks;
    if (!isRiskReportDoc || !previewHtml) return [];
    return parseTopRisksFromPreviewHtml(previewHtml, docType, 6);
  }, [docType, isFmea, isRiskReportDoc, previewHtml, riskSummary.topRisks]);

  const fmeaComplianceSummary = useMemo(
    () => analyzeFmeaCompliance(parsedFmeaRows, previewTableStats.columnCount),
    [parsedFmeaRows, previewTableStats.columnCount]
  );

  const fmeaFilteredRowCount = useMemo(() => {
    return parsedFmeaRows.filter((r) => rowMatchesFilter(r, riskFilter)).length;
  }, [parsedFmeaRows, riskFilter]);

  const riskFilterSummaryLabel = useMemo(() => {
    const labels: Record<RiskRowFilter, string> = {
      all: 'all rows',
      high: 'high RPN only',
      medium: 'medium RPN only',
      low: 'low RPN only',
      unmitigated: 'unmitigated only',
      needs_review: 'needs review',
      closed: 'closed / complete',
    };
    return labels[riskFilter];
  }, [riskFilter]);

  const applySavedView = useCallback((v: SavedReportView) => {
    setSavedView(v);
    const p = SAVED_VIEW_PRESETS[v];
    setComplianceMode(p.complianceMode);
    setRiskFilter(p.riskFilter);
  }, []);

  const executiveSummaryMetrics = useMemo(() => {
    if (isFmea) {
      return [
        { label: 'Total risks (rows)', value: riskSummary.total },
        {
          label: 'High (RPN ≥ 100)',
          value: riskSummary.high,
          tone: 'high' as const,
        },
        {
          label: 'Medium (50–99)',
          value: riskSummary.medium,
          tone: 'medium' as const,
        },
        {
          label: 'Low (1–49)',
          value: riskSummary.low,
          tone: 'low' as const,
        },
        { label: 'Highest RPN', value: riskSummary.highest || '—', tone: 'high' as const },
        { label: 'Average RPN', value: riskSummary.averageRpn || '—' },
        { label: 'Highest residual RPN', value: riskSummary.highestResidual || '—', tone: 'medium' as const },
        {
          label: 'Mitigation completion',
          value: `${riskSummary.completion}%`,
          tone: 'low' as const,
          hint: 'Share of rows with mitigation text in the preview table.',
        },
      ];
    }

    return [
      {
        label: 'Table rows (detected)',
        value: previewTableStats.rowCount || '—',
        hint: 'Heuristic count from exported HTML; replace with API metadata when available.',
      },
      {
        label: 'Columns (detected)',
        value: previewTableStats.columnCount || '—',
        hint: 'Derived from first table in preview.',
      },
      { label: 'Document status', value: String(status || 'draft') },
      { label: 'Document version', value: `v${selectedVersionNo || doc?.version || 1}` },
    ];
  }, [
    doc?.version,
    isFmea,
    previewTableStats.columnCount,
    previewTableStats.rowCount,
    riskSummary.averageRpn,
    riskSummary.completion,
    riskSummary.high,
    riskSummary.highest,
    riskSummary.highestResidual,
    riskSummary.low,
    riskSummary.medium,
    riskSummary.total,
    selectedVersionNo,
    status,
  ]);

  const auditTrailEntries = useMemo(() => {
    return (versions || []).slice(0, 12).map((v: any) => ({
      version: v.version,
      date: v.created_at ? new Date(v.created_at).toLocaleString() : 'Unknown',
      user: (v?.changes?.user || v?.changes?.generated_by || v?.changes?.author || 'System') as string,
      summary:
        (typeof v?.changes?.summary === 'string' && v.changes.summary) ||
        (v?.changes?.generated ? 'Regenerated report from project data.' : 'Content or metadata update.'),
      changeType: v?.changes?.generated ? 'Regeneration' : v?.changes?.change_type || 'Update',
      recordId: typeof v?.id === 'string' ? v.id : v?.id != null ? String(v.id) : undefined,
    }));
  }, [versions]);

  /**
   * FMEA preview DOM: RPN cell tint, row filter visibility, compliance row + cell highlights.
   * TODO: Backend should emit data-* on rows/cells so this does not depend on column indices.
   */
  useLayoutEffect(() => {
    if (!isFmea || !previewHostRef.current) return;
    const root = previewHostRef.current;
    root.querySelectorAll('td.compliance-mit-empty, td.compliance-res-empty').forEach((cell) => {
      cell.classList.remove('compliance-mit-empty', 'compliance-res-empty');
    });

    const selectors = ['tbody tr td:nth-child(10)', 'tbody tr td:nth-child(15)'];
    for (const sel of selectors) {
      root.querySelectorAll(sel).forEach((cell) => {
        const el = cell as HTMLTableCellElement;
        el.classList.remove('rpn-high', 'rpn-medium', 'rpn-low', 'rpn-neutral');
        const raw = (el.textContent || '').replace(/\D/g, '');
        const n = parseInt(raw, 10);
        if (!Number.isFinite(n) || n <= 0) {
          el.classList.add('rpn-neutral');
          return;
        }
        const level = rpnToLevel(n);
        if (level === 'high') el.classList.add('rpn-high');
        else if (level === 'medium') el.classList.add('rpn-medium');
        else if (level === 'low') el.classList.add('rpn-low');
        else el.classList.add('rpn-neutral');
      });
    }

    const hasResidualCol = previewTableStats.columnCount >= 15;
    const tbodyRows = root.querySelectorAll('tbody tr');

    tbodyRows.forEach((tr, i) => {
      const el = tr as HTMLTableRowElement;
      el.classList.remove('report-row-filtered-out', 'report-compliance-issue', 'report-compliance-critical');
      const row = parsedFmeaRows[i];
      if (!row) return;

      if (!rowMatchesFilter(row, riskFilter)) {
        el.classList.add('report-row-filtered-out');
      }

      if (complianceMode) {
        const mit = row.mitigation.trim();
        const sodIncomplete =
          row.s < 1 ||
          row.s > 10 ||
          row.o < 1 ||
          row.o > 10 ||
          row.d < 1 ||
          row.d > 10 ||
          row.rpn < 1;
        const resMissing = hasResidualCol && (!row.residualRpn || row.residualRpn < 1);
        if (!mit || sodIncomplete || resMissing) {
          el.classList.add('report-compliance-issue');
        }
        if (!mit && row.rpn >= 100) {
          el.classList.add('report-compliance-critical');
        }

        const cells = el.querySelectorAll('td');
        if (cells[10] && !mit) {
          cells[10].classList.add('compliance-mit-empty');
        }
        if (hasResidualCol && cells[14] && (!row.residualRpn || row.residualRpn < 1)) {
          cells[14].classList.add('compliance-res-empty');
        }
      }
    });
  }, [
    complianceMode,
    isFmea,
    parsedFmeaRows,
    previewHtml,
    previewTableStats.columnCount,
    riskFilter,
  ]);

  const load = async () => {
    if (!finalProjectId || !finalDocId) return;
    setLoading(true);
    setError('');
    try {
      if (!authService.isAuthenticated()) {
        await authService.authenticate();
      }
      const d = await documentsApi.getById(finalProjectId, finalDocId);
      setDoc(d);
      setName(d.name || '');
      setStatus((d.status as any) || 'draft');
      setContent(d.content || '');
    } catch (e: any) {
      setError(e?.message || 'Failed to load document');
    } finally {
      setLoading(false);
    }
  };

  const loadPreview = async () => {
    if (!finalProjectId || !finalDocId) return;
    try {
      if (!authService.isAuthenticated()) {
        await authService.authenticate();
      }
      // FMEA preview/export is rendered from persisted FMEA rows. Ensure baseline
      // rows exist for all wizard components before exporting HTML.
      if (isFmea && !didInitFmea) {
        try {
          await projectInitializeApi.run(finalProjectId);
        } finally {
          setDidInitFmea(true);
        }
      }
      const res = await api.get(
        `/projects/${finalProjectId}/documents/${finalDocId}/export/html`,
        { responseType: 'blob', params: selectedVersionNo ? { version: selectedVersionNo } : undefined }
      );
      const blob = new Blob([res.data], { type: 'text/html' });
      const text = await blob.text();
      setPreviewHtml(text);
    } catch (e: any) {
      setPreviewHtml('');
      setError(e?.message || 'Failed to load preview');
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [finalProjectId, finalDocId]);

  // Fetch project name for display (so the header matches the wizard project name).
  useEffect(() => {
    let cancelled = false;
    async function loadProjectName() {
      setProjectName('');
      if (!finalProjectId) return;
      try {
        const p = await projectsApi.getById(finalProjectId);
        if (!cancelled) setProjectName(String((p as any)?.name || ''));
      } catch {
        // non-blocking: keep showing the ID if name can't be loaded
      }
    }
    loadProjectName();
    return () => {
      cancelled = true;
    };
  }, [finalProjectId]);

  // When navigating between documents, reset the UI to Preview by default.
  useEffect(() => {
    setTab('preview');
    setPreviewHtml('');
    setDidInitFmea(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [finalProjectId, finalDocId]);

  useEffect(() => {
    if (tab === 'preview' && finalProjectId && finalDocId) {
      loadPreview();
    }
  }, [tab, selectedVersionNo, finalProjectId, finalDocId]);

  useEffect(() => {
    let cancelled = false;
    async function loadCompactVersions() {
      if (!isRiskReportDoc || !finalProjectId || !finalDocId) return;
      try {
        const list = await documentsApi.getVersions(finalProjectId, finalDocId);
        if (!cancelled) setVersions(Array.isArray(list) ? list : []);
      } catch {
        // non-blocking on dashboard/report view
      }
    }
    loadCompactVersions();
    return () => {
      cancelled = true;
    };
  }, [isRiskReportDoc, finalProjectId, finalDocId]);

  const save = async () => {
    if (!finalProjectId || !finalDocId) return;
    if (isRmf) {
      setError("RMF is compiled and cannot be edited manually. Use 'Compile Risk Management File'.");
      return;
    }
    setSaving(true);
    setError('');
    try {
      const updated = await documentsApi.update(finalProjectId, finalDocId, {
        name,
        status,
        content,
      } as any);
      setDoc(updated);
      if (tab === 'preview') {
        await loadPreview();
      }
    } catch (e: any) {
      setError(e?.message || 'Failed to save document');
    } finally {
      setSaving(false);
    }
  };

  const downloadHtml = async () => {
    try {
      const res = await api.get(
        `/projects/${finalProjectId}/documents/${finalDocId}/export/html`,
        { responseType: 'blob', params: selectedVersionNo ? { version: selectedVersionNo } : undefined }
      );
      const blob = new Blob([res.data], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const v = selectedVersionNo || doc?.version || 1;
      a.download = `${title}_v${v}.html`.replace(/\s+/g, '_');
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e: any) {
      setError(e?.message || 'Failed to download HTML');
    }
  };

  const downloadCsv = async () => {
    try {
      const res = await api.get(`/projects/${finalProjectId}/documents/${finalDocId}/export/csv`, { responseType: 'blob' });
      const blob = new Blob([res.data], { type: 'text/csv;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const v = selectedVersionNo || doc?.version || 1;
      a.download = `${title}_v${v}.csv`.replace(/\s+/g, '_');
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e: any) {
      setError(e?.message || 'Failed to download CSV');
    }
  };

  const addGenComponentsFromInput = () => {
    const parts = genComponentInput
      .split(',')
      .map((x) => x.trim())
      .filter(Boolean);
    if (parts.length === 0) return;
    setGenComponents((prev) => Array.from(new Set([...prev, ...parts])));
    setGenComponentInput('');
  };

  const generateNew = async () => {
    if (!finalProjectId || !finalDocId) return;
    setSaving(true);
    setError('');
    try {
      if (!authService.isAuthenticated()) {
        await authService.authenticate();
      }
      if (isFmea) {
        await projectInitializeApi.run(finalProjectId);
        setDidInitFmea(true);
      }
      const payload = {
        components: genComponents.map((name) => ({ name })),
        version_scope: versionScope,
        options:
          docType === 'rmp'
            ? {
                ...genOptions,
                scope: rmpScope,
                intended_use: rmpIntendedUse,
                review_roles: rmpReviewRoles,
              }
            : docType === 'benefit_risk_analysis'
              ? {
                  ...genOptions,
                  use_ai: false,
                  approved_mode: !!genOptions.approved_mode,
                  overall_decision: benefitRiskDecision,
                  decision_rationale: benefitRiskRationale,
                  approval_metadata: {
                    author: approvalAuthor,
                    reviewer: approvalReviewer,
                    approver: approvalApprover,
                    date: approvalDate,
                    version: approvalVersion,
                    issuance_state: approvalIssuanceState,
                  },
                }
              : genOptions,
      };
      const res = await api.post(
        `/projects/${finalProjectId}/documents/${finalDocId}/generate`,
        payload
      );
      const newVersionNo = res.data?.new_version_no;
      const html = res.data?.rendered_html || '';
      setSelectedVersionNo(null);
      setPreviewHtml(html);
      setTab('preview');
      setShowGenerate(false);
      await load(); // refresh doc metadata/version
      alert(`Generated version v${newVersionNo}`);
    } catch (e: any) {
      const detail = e?.response?.data?.detail;
      if (detail?.blockers && Array.isArray(detail.blockers)) {
        setError(`${detail?.message || 'Approved-mode generation blocked.'}\n- ${detail.blockers.join('\n- ')}`);
      } else {
        setError(detail || e?.message || 'Failed to generate new version');
      }
    } finally {
      setSaving(false);
    }
  };

  const addComponentRow = () => {
    setComponentDrafts((prev) => [...prev, { name: '', description: '' }]);
  };

  const removeComponentRow = (idx: number) => {
    setComponentDrafts((prev) => {
      const next = prev.filter((_, i) => i !== idx);
      return next.length ? next : [{ name: '', description: '' }];
    });
  };

  const applyAddComponentBulk = () => {
    const lines = addComponentBulk
      .split('\n')
      .map((l) => l.trim())
      .filter(Boolean);
    if (!lines.length) return;
    setComponentDrafts((prev) => {
      const existing = new Set(prev.map((c) => normalize(c.name).toLowerCase()).filter(Boolean));
      const additions: ComponentDraft[] = [];
      for (const name of lines) {
        const key = name.toLowerCase();
        if (existing.has(key)) continue;
        existing.add(key);
        additions.push({ name, description: '' });
      }
      const cleanedPrev = prev.filter((c) => normalize(c.name) || normalize(c.description));
      const base = cleanedPrev.length ? cleanedPrev : [];
      return [...base, ...additions, ...(base.length || additions.length ? [] : [{ name: '', description: '' }])];
    });
    setAddComponentBulk('');
  };

  const addComponentsToProject = async () => {
    if (!finalProjectId) return;
    setSaving(true);
    setError('');
    setAddComponentInfo('');
    try {
      if (!authService.isAuthenticated()) {
        await authService.authenticate();
      }

      const toCreate = componentDrafts
        .map((c) => ({ name: normalize(c.name), description: normalize(c.description) }))
        .filter((c) => c.name);

      if (toCreate.length === 0) {
        setError('Please enter at least one component name.');
        return;
      }

      // Create components
      for (const c of toCreate) {
        await componentsApi.create(finalProjectId, { name: c.name, description: c.description || undefined });
      }

      // Seed baseline FMEA rows (>= 5 rows per component)
      await projectInitializeApi.run(finalProjectId);

      // For FMEA docs, regenerate so the preview table reflects the newly seeded rows.
      if (isFmea && finalDocId) {
        const payload = {
          components: [],
          version_scope: versionScope,
          options: genOptions,
        };
        const res = await api.post(`/projects/${finalProjectId}/documents/${finalDocId}/generate`, payload);
        const html = res.data?.rendered_html || '';
        setSelectedVersionNo(null);
        setPreviewHtml(html);
        setTab('preview');
        await load(); // refresh doc metadata/version
      }

      setAddComponentInfo(`Added ${toCreate.length} component${toCreate.length === 1 ? '' : 's'} and seeded FMEA rows.`);
      setShowAddComponent(false);
      setComponentDrafts([{ name: '', description: '' }]);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to add component(s)');
    } finally {
      setSaving(false);
    }
  };

  const generateAiSample = async () => {
    if (!finalProjectId || !docType) return;
    if (!doc) return;
    setSaving(true);
    setError('');
    try {
      if (!authService.isAuthenticated()) {
        await authService.authenticate();
      }
      if (isFmea) {
        await projectInitializeApi.run(finalProjectId);
        setDidInitFmea(true);
      }
      const updated = await documentsApi.generateAiSampleForType(finalProjectId, docType);
      setDoc(updated);
      setName(updated.name || '');
      setStatus((updated.status as any) || 'draft');
      setContent(updated.content || '');
      setSelectedVersionNo(null);
      setTab('preview');
      await loadPreview();
      alert('AI sample added as a new draft version.');
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to generate AI sample');
    } finally {
      setSaving(false);
    }
  };

  const generateWithAi = async () => {
    if (!finalProjectId || !docType) return;
    if (!doc) return;
    setSaving(true);
    setError('');
    try {
      if (!authService.isAuthenticated()) {
        await authService.authenticate();
      }
      if (isFmea) {
        await projectInitializeApi.run(finalProjectId);
        setDidInitFmea(true);
      }
      if (isHazardAnalysis && finalDocId) {
        // Hazard Analysis: "Generate with AI" enriches risk chain fields, then regenerates the deterministic table.
        const enrichRes = await api.post(`/projects/${finalProjectId}/hazard-analysis/enrich-ai`, {
          max_items: 50,
          only_if_missing: true,
        });
        const stats = enrichRes?.data?.stats;

        // Ensure the regenerated table actually shows the versions we just created.
        // (Newly enriched versions are not "approved", so approved_only would look like "nothing happened".)
        const nextVersionScope = versionScope === 'approved_only' ? 'current' : versionScope;
        const payload = {
          components: [],
          version_scope: nextVersionScope,
          options: { ...genOptions, include_unapproved: true },
        };
        const res = await api.post(`/projects/${finalProjectId}/documents/${finalDocId}/generate`, payload);
        const html = res.data?.rendered_html || '';
        setSelectedVersionNo(null);
        setPreviewHtml(html);
        setTab('preview');
        await load(); // refresh doc metadata/version
        if (stats && typeof stats.updated === 'number') {
          alert(
            `Hazard Analysis enrichment complete: updated ${stats.updated} item(s) (scanned ${stats.scanned || 0}). Regenerated table.`
          );
        } else {
          alert('Filled missing hazard chain fields and regenerated Hazard Analysis.');
        }
      } else if (docType === 'benefit_risk_analysis' && finalDocId) {
        // Formal benefit–risk report: structured project evidence only (no AI addendum in stored content).
        const payload = {
          components: [],
          version_scope: versionScope || 'approved_only',
          options: {
            ...genOptions,
            use_ai: false,
            approved_mode: !!genOptions.approved_mode,
            overall_decision: benefitRiskDecision,
            decision_rationale: benefitRiskRationale,
            approval_metadata: {
              author: approvalAuthor,
              reviewer: approvalReviewer,
              approver: approvalApprover,
              date: approvalDate,
              version: approvalVersion,
              issuance_state: approvalIssuanceState,
            },
          },
        };
        const res = await api.post(`/projects/${finalProjectId}/documents/${finalDocId}/generate`, payload);
        const html = res.data?.rendered_html || '';
        const newVersionNo = res.data?.new_version_no;
        setSelectedVersionNo(null);
        setPreviewHtml(html);
        setTab('preview');
        await load();
        alert(`Benefit–risk report regenerated (v${newVersionNo}).`);
      } else {
        const updated = await documentsApi.generateWithAiForType(finalProjectId, docType);
        setDoc(updated);
        setName(updated.name || '');
        setStatus((updated.status as any) || 'draft');
        setContent(updated.content || '');
        setSelectedVersionNo(null);
        setTab('preview');
        await loadPreview();
        const meta = (updated as any)?.ai_metadata;
        if (docType === 'rmf' && meta?.rmf_deterministic_compile) {
          alert(
            'Risk Management File refreshed from linked authoritative documents (deterministic compilation; no LLM).'
          );
        } else {
          alert('AI populated draft created as a new version.');
        }
      }
    } catch (e: any) {
      const detail = e?.response?.data?.detail;
      if (detail?.blockers && Array.isArray(detail.blockers)) {
        setError(`${detail?.message || 'Approved-mode generation blocked.'}\n- ${detail.blockers.join('\n- ')}`);
      } else {
        setError(detail || e?.message || 'Failed to generate with AI');
      }
    } finally {
      setSaving(false);
    }
  };

  const openVersions = async () => {
    if (!finalProjectId || !finalDocId) return;
    setShowVersions(true);
    setVersionsError('');
    setVersionsLoading(true);
    try {
      const list = await documentsApi.getVersions(finalProjectId, finalDocId);
      setVersions(Array.isArray(list) ? list : []);
    } catch (e: any) {
      setVersionsError(e?.message || 'Failed to load versions');
    } finally {
      setVersionsLoading(false);
    }
  };

  const viewVersion = (v: any) => {
    setSelectedVersionNo(v.version);
    setTab('preview');
    // Prefer content if it looks like full HTML
    if (typeof v.content === 'string' && v.content.trim().startsWith('<')) {
      setPreviewHtml(v.content);
    } else {
      setPreviewHtml('');
    }
    setShowVersions(false);
  };

  const compareVersionOptions = useMemo(() => {
    const previewV = selectedVersionNo ?? doc?.version ?? 1;
    const base = [
      {
        value: 'current' as const,
        label: `Live preview (as shown — v${previewV})`,
      },
    ];
    const sorted = [...versions].sort((a, b) => (a.version as number) - (b.version as number));
    for (const v of sorted) {
      base.push({
        value: v.version as number,
        label: `Stored v${v.version} · ${new Date(v.created_at).toLocaleString()}`,
      });
    }
    return base;
  }, [versions, selectedVersionNo, doc?.version]);

  const openCompare = () => {
    setCompareError('');
    setDiffResult(null);
    const sorted = [...versions].sort((a, b) => (b.version as number) - (a.version as number));
    if (sorted.length >= 2) {
      setCompareRight(sorted[0].version);
      setCompareLeft(sorted[1].version);
    } else if (sorted.length === 1) {
      setCompareLeft('current');
      setCompareRight(sorted[0].version);
    } else {
      setCompareLeft('current');
      setCompareRight('current');
    }
    setShowCompare(true);
  };

  const resolveCompareHtml = async (side: number | 'current'): Promise<string> => {
    if (side === 'current') {
      return previewHtml || '';
    }
    const ver = await documentsApi.getVersion(finalProjectId, finalDocId, side);
    const c = ver?.content;
    return typeof c === 'string' && c.trim().startsWith('<') ? c : '';
  };

  const runFmeaCompare = async () => {
    if (!finalProjectId || !finalDocId) return;
    setCompareLoading(true);
    setCompareError('');
    try {
      const [leftHtml, rightHtml] = await Promise.all([resolveCompareHtml(compareLeft), resolveCompareHtml(compareRight)]);
      const leftLabel =
        compareLeft === 'current'
          ? `Live preview (v${selectedVersionNo ?? doc?.version ?? 1})`
          : `Stored v${compareLeft}`;
      const rightLabel =
        compareRight === 'current'
          ? `Live preview (v${selectedVersionNo ?? doc?.version ?? 1})`
          : `Stored v${compareRight}`;
      setDiffResult({ leftHtml, rightHtml, leftLabel, rightLabel });
    } catch (e: any) {
      setCompareError(e?.message || 'Failed to load versions for comparison');
    } finally {
      setCompareLoading(false);
    }
  };

  if (!finalProjectId || !finalDocId) {
    return (
      <div className="p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">Project and document id are required.</p>
          <button
            className="mt-3 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            onClick={() => navigate('/projects')}
          >
            Go to Projects
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return <div className="p-6 text-gray-600">Loading document…</div>;
  }

  const auditTrailSection = isRiskReportDoc ? (
    <ReportSection
      id="section-version-history"
      title="Version history & audit trail"
      subtitle="Chronological record of stored document versions (controlled artifact)"
    >
      <AuditTrail entries={auditTrailEntries} documentTitle={title} />
    </ReportSection>
  ) : null;

  return (
    <div className="min-h-screen bg-neutral-50 px-4 py-6 sm:px-6 lg:px-8 print:bg-white print:px-4 print:py-4">
      <div className="print:hidden">
        <DocumentGuidanceHeader
          documentType={docType || 'document'}
          hasAiSample={hasAiSample}
          onGenerateAiSample={generateAiSample}
          onGenerateWithAi={generateWithAi}
          isGeneratingAi={saving}
          populationSources={populationSources}
        />
      </div>
      <div className="mb-6 overflow-hidden rounded-lg border border-neutral-200 bg-white shadow-sm print:rounded-none print:border-neutral-300 print:shadow-none">
        <div className="flex flex-col gap-4 border-b border-neutral-200 p-5 sm:flex-row sm:items-start sm:justify-between sm:gap-6 print:border-neutral-300">
          <div className="min-w-0">
            <h1 className="text-xl font-semibold tracking-tight text-neutral-900 sm:text-2xl">{title}</h1>
            <p className="mt-1 text-sm text-neutral-600">
              Project:{' '}
              <span className="font-medium text-neutral-800">{projectName || '—'}</span>
              {documentTypeLabel ? (
                <>
                  <span className="text-neutral-400"> · </span>
                  <span className="text-neutral-600">{documentTypeLabel}</span>
                </>
              ) : null}
            </p>
          </div>
          <div className="flex flex-shrink-0 flex-wrap gap-2">
            <button
              type="button"
              className="rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-neutral-800 disabled:opacity-50 print:hidden"
              onClick={() => setShowGenerate(true)}
              disabled={saving}
            >
              {isRmf ? 'Compile RMF' : 'Generate new'}
            </button>
            <button
              type="button"
              className="rounded-md border border-neutral-200 bg-white px-4 py-2 text-sm font-medium text-neutral-800 transition hover:bg-neutral-50 disabled:opacity-50 print:hidden"
              onClick={save}
              disabled={saving || isRmf}
              title="Save draft"
            >
              {saving ? 'Saving…' : 'Save draft'}
            </button>
            <button
              type="button"
              className="rounded-md border border-neutral-200 bg-white px-4 py-2 text-sm font-medium text-neutral-800 transition hover:bg-neutral-50 print:hidden"
              onClick={() => navigate(`/projects/${finalProjectId}/dashboard`)}
            >
              Back
            </button>
            <button
              type="button"
              className="rounded-md border border-neutral-200 bg-white px-4 py-2 text-sm font-medium text-neutral-800 transition hover:bg-neutral-50 print:hidden"
              onClick={openVersions}
            >
              Versions
            </button>
            {isFmea ? (
              <button
                type="button"
                className="rounded-md border border-neutral-200 bg-white px-4 py-2 text-sm font-medium text-neutral-800 transition hover:bg-neutral-50 print:hidden"
                onClick={openCompare}
                title="Compare two FMEA report snapshots (Git-style field highlights)"
              >
                Compare versions
              </button>
            ) : null}
            <button
              type="button"
              className="rounded-md border border-neutral-300 bg-white px-4 py-2 text-sm font-medium text-neutral-900 transition hover:bg-neutral-50 print:hidden"
              onClick={isFmea ? downloadCsv : downloadHtml}
            >
              {isFmea ? 'Download CSV' : 'Download HTML'}
            </button>
          </div>
        </div>

        {error && (
          <div className="mx-5 mb-5 rounded-lg border border-red-200 bg-red-50 p-4">
            <p className="text-red-800">{error}</p>
            {String(error).includes(missingSetupMessage) ? (
              <div className="mt-2">
                <Link
                  to={`/projects/${finalProjectId}/setup`}
                  className="text-sm font-medium text-blue-700 underline"
                >
                  Complete Project Setup
                </Link>
              </div>
            ) : null}
          </div>
        )}
      </div>

      <div
        id="controlled-document-report"
        className="min-w-0 overflow-hidden rounded-lg border border-neutral-200 bg-white p-4 shadow-sm sm:p-6 print:rounded-none print:border-neutral-300 print:p-4 print:shadow-none"
      >
        <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between print:mb-4">
          <div className="flex flex-wrap gap-2 print:hidden">
            <button
              type="button"
              className={`rounded-md px-4 py-2 text-sm font-medium transition ${
                tab === 'edit'
                  ? 'bg-neutral-900 text-white'
                  : 'border border-neutral-200 bg-white text-neutral-800 hover:bg-neutral-50'
              }`}
              onClick={() => setTab('edit')}
              disabled={isRmf}
            >
              Edit
            </button>
            <button
              type="button"
              className={`rounded-md px-4 py-2 text-sm font-medium transition ${
                tab === 'preview'
                  ? 'bg-neutral-900 text-white'
                  : 'border border-neutral-200 bg-white text-neutral-800 hover:bg-neutral-50'
              }`}
              onClick={() => setTab('preview')}
            >
              Preview
            </button>
            {isFmea ? (
              <button
                type="button"
                className="rounded-md border border-neutral-200 bg-white px-4 py-2 text-sm font-medium text-neutral-800 transition hover:bg-neutral-50"
                onClick={() => {
                  setAddComponentInfo('');
                  setShowAddComponent(true);
                }}
              >
                Add component
              </button>
            ) : null}
          </div>
          <div className="text-sm font-medium text-neutral-600 print:text-xs">
            {selectedVersionNo ? `Viewing v${selectedVersionNo}` : `Current v${doc?.version || 1}`}
          </div>
        </div>

        {addComponentInfo ? (
          <div className="mb-4 rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-800">
            {addComponentInfo}
          </div>
        ) : null}

        {tab === 'edit' && !isRmf ? (
          <div className="space-y-4">
            {isCapa ? (
              <div className="rounded-md border border-sky-200 bg-sky-50 p-3 text-sm text-sky-900">
                This CAPA is stored as <strong>structured JSON</strong> (single object). Edit the JSON directly, or use{' '}
                <strong>Generate with AI</strong> to refresh only the <code className="rounded bg-sky-100 px-1">ai_assist</code>{' '}
                reviewer block — the system scaffold is not duplicated.
              </div>
            ) : null}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <input
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  value={status}
                  onChange={(e) => setStatus(e.target.value as any)}
                >
                  <option value="draft">Draft</option>
                  <option value="in_review">In Review</option>
                  <option value="approved">Approved</option>
                  <option value="obsolete">Obsolete</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
              <textarea
                className="w-full px-3 py-2 border border-gray-300 rounded-md font-mono text-sm"
                rows={18}
                value={content}
                onChange={(e) => setContent(e.target.value)}
              />
            </div>
          </div>
        ) : (
          <>
            {isRiskReportDoc && (
              <div className="mb-6 space-y-5 print:space-y-4">
                <ReportHeader
                  projectName={projectName || 'Project'}
                  documentTitle={title}
                  documentTypeLabel={documentTypeLabel}
                  subject={
                    isFmea
                      ? 'Project-scoped failure modes, effects, and risk scoring (preview)'
                      : `${doc?.name || 'Risk report'} — structured regulatory output (preview)`
                  }
                  version={`v${selectedVersionNo || doc?.version || 1}`}
                  reportDate={new Date().toLocaleDateString()}
                  owner={(doc as any)?.updated_by || 'Unassigned'}
                  status={status}
                />

                <SummaryCards
                  title="Key metrics"
                  metrics={executiveSummaryMetrics}
                />

                <div className="print:hidden">
                  <ReportViewToolbar
                    fmeaActive={isFmea}
                    savedView={savedView}
                    onSavedView={applySavedView}
                    riskFilter={riskFilter}
                    onRiskFilter={setRiskFilter}
                    complianceMode={complianceMode}
                    onComplianceMode={setComplianceMode}
                  />
                </div>

                {isFmea && complianceMode ? (
                  <ComplianceChecklistPanel
                    summary={fmeaComplianceSummary}
                    totalRows={parsedFmeaRows.length}
                    filteredVisibleCount={fmeaFilteredRowCount}
                    riskFilterLabel={riskFilterSummaryLabel}
                  />
                ) : null}
              </div>
            )}

            <div className="space-y-5">
              {isRiskReportDoc && (
                <>
                  {savedView === 'audit' ? auditTrailSection : null}

                  <ReportSection
                    id="section-scope"
                    variant="muted"
                    title="Scope"
                    subtitle="Report context and controlled scope for this version"
                  >
                    <p className="text-sm leading-relaxed text-neutral-700">
                      This view reflects the selected document version and export scope. Use{' '}
                      <span className="font-medium text-neutral-800">Download HTML</span> for the official artifact; the
                      layout below is optimized for on-screen review.
                      {/* TODO: Surface project setup fields (intended use, device description) from API when linked to this doc. */}
                    </p>
                  </ReportSection>

                  <ReportSection
                    id="section-risk-profile"
                    title="Risk profile"
                    subtitle="Distribution and concentration — for executive review; confirm details in the report table"
                  >
                    <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 lg:items-start">
                      {isFmea ? (
                        <RiskSummaryChart
                          variant="fmea"
                          high={riskSummary.high}
                          medium={riskSummary.medium}
                          low={riskSummary.low}
                        />
                      ) : (
                        <RiskSummaryChart
                          variant="generic"
                          high={qualitativeBands.high}
                          medium={qualitativeBands.medium}
                          low={qualitativeBands.low}
                        />
                      )}
                      {isFmea && parsedFmeaRows.length > 0 ? (
                        <RiskMatrix grid={fmeaSoMatrixGrid} docTypeLabel={documentTypeLabel} />
                      ) : (
                        <RiskMatrix
                          grid={[]}
                          empty
                          docTypeLabel={documentTypeLabel || undefined}
                        />
                      )}
                    </div>
                  </ReportSection>

                  <ReportSection
                    id="section-top-risks"
                    title="Top risks"
                    subtitle="Highest-priority items for this preview — align with the controlled risk register before decisions"
                  >
                    <TopRisksPanel
                      items={displayTopRisks}
                      docTypeLabel={documentTypeLabel || undefined}
                      limit={6}
                    />
                  </ReportSection>
                </>
              )}

              <ReportSection
                id={isFmea ? 'section-fmea-table' : 'section-report-table'}
                title={isFmea ? 'FMEA Table' : 'Report Table'}
                subtitle={
                  isFmea
                    ? 'Structured risk analysis table with scoring and mitigation actions'
                    : isCapa
                      ? 'Structured CAPA (HTML export) — AI assist is separated in the preview when present'
                      : 'Structured report output rendered from the selected document version'
                }
              >
                {isCapa ? (
                  <div className="mb-3 rounded-md border border-sky-200 bg-sky-50 p-3 text-sm text-sky-900 print:hidden">
                    Preview loads the server HTML export. Sections and workflow gates come from the JSON record;{' '}
                    <strong>AI assist</strong> appears in the highlighted panel when populated.
                  </div>
                ) : null}
                <div className="min-w-0 max-h-[min(72vh,56rem)] overflow-auto rounded-lg border border-neutral-200 bg-white [scrollbar-gutter:stable] print:max-h-none print:overflow-visible print:border-neutral-300 print:shadow-none">
                  {previewHtml ? (
                    <div ref={previewHostRef} className="report-preview report-preview-inner min-w-0 p-3 sm:p-4 print:p-2">
                      <style>{buildReportPreviewTableCss(isFmea)}</style>
                      <div dangerouslySetInnerHTML={{ __html: previewHtml }} />
                    </div>
                  ) : (
                    <div className="p-6 text-sm text-neutral-600">No preview available.</div>
                  )}
                </div>
              </ReportSection>

              {isFmea && (
                <>
                  <ReportSection
                    id="section-residual-summary"
                    title="Residual risk summary"
                    subtitle="RPN bands from visible FMEA rows (preview)"
                  >
                    <div className="text-sm text-neutral-700 space-y-2">
                      <div className="flex flex-wrap gap-2">
                        <RiskBadge level="high" label={`High: ${riskSummary.high}`} compact />
                        <RiskBadge level="medium" label={`Medium: ${riskSummary.medium}`} compact />
                        <RiskBadge level="low" label={`Low: ${riskSummary.low}`} compact />
                      </div>
                      <p>Highest RPN: {riskSummary.highest || '-'}</p>
                      <p>Highest Residual RPN: {riskSummary.highestResidual || '-'}</p>
                    </div>
                  </ReportSection>
                </>
              )}

              {isRiskReportDoc && savedView !== 'audit' ? auditTrailSection : null}
            </div>
          </>
        )}
      </div>

      {/* Add Component Modal (FMEA) */}
      {showAddComponent && isFmea && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg w-full max-w-3xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-gray-900">Add Component(s) to Project</h3>
              <button
                className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
                onClick={() => setShowAddComponent(false)}
                type="button"
              >
                Close
              </button>
            </div>

            <div className="text-sm text-gray-700 mb-4">
              This will add component(s) to your project and seed <b>at least 5 FMEA rows per component</b>.
              {isFmea ? ' The FMEA document preview will be regenerated to include the new rows.' : null}
            </div>

            <div className="space-y-4">
              <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
                <div className="text-sm font-semibold text-gray-900 mb-2">Bulk add</div>
                <div className="text-sm text-gray-600 mb-2">Paste one component name per line.</div>
                <textarea
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                  rows={4}
                  value={addComponentBulk}
                  onChange={(e) => setAddComponentBulk(e.target.value)}
                  placeholder="e.g.\nBattery pack\nCharging port\nSensor assembly"
                />
                <div className="mt-2 flex justify-end">
                  <button
                    type="button"
                    onClick={applyAddComponentBulk}
                    className="px-3 py-2 rounded-md text-sm border border-gray-300 bg-white hover:bg-gray-50"
                    disabled={!addComponentBulk.trim()}
                  >
                    Add lines
                  </button>
                </div>
              </div>

              <div className="rounded-lg border border-gray-200 p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="text-sm font-semibold text-gray-900">Components to add</div>
                  <button
                    type="button"
                    onClick={addComponentRow}
                    className="px-3 py-2 rounded-md text-sm border border-gray-300 bg-white hover:bg-gray-50"
                  >
                    + Add row
                  </button>
                </div>

                <div className="space-y-3">
                  {componentDrafts.map((c, idx) => (
                    <div key={idx} className="grid grid-cols-1 md:grid-cols-12 gap-2 items-start">
                      <div className="md:col-span-4">
                        <label className="block text-xs font-medium text-gray-600 mb-1">Name</label>
                        <input
                          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                          value={c.name}
                          onChange={(e) => {
                            const v = e.target.value;
                            setComponentDrafts((prev) => prev.map((x, i) => (i === idx ? { ...x, name: v } : x)));
                          }}
                          placeholder="Component name"
                        />
                      </div>
                      <div className="md:col-span-7">
                        <label className="block text-xs font-medium text-gray-600 mb-1">Description (optional)</label>
                        <input
                          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                          value={c.description || ''}
                          onChange={(e) => {
                            const v = e.target.value;
                            setComponentDrafts((prev) =>
                              prev.map((x, i) => (i === idx ? { ...x, description: v } : x))
                            );
                          }}
                          placeholder="Short description"
                        />
                      </div>
                      <div className="md:col-span-1 flex md:justify-end pt-6">
                        <button
                          type="button"
                          className="px-3 py-2 rounded-md text-sm border border-gray-300 bg-white hover:bg-gray-50"
                          onClick={() => removeComponentRow(idx)}
                          title="Remove"
                        >
                          ×
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-end gap-2">
                <button
                  type="button"
                  className="px-4 py-2 rounded-md text-sm border border-gray-300 bg-white hover:bg-gray-50"
                  onClick={() => setShowAddComponent(false)}
                  disabled={saving}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  className="px-4 py-2 rounded-md text-sm bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
                  onClick={addComponentsToProject}
                  disabled={saving}
                >
                  {saving ? 'Adding…' : 'Add component(s)'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Generate New Modal */}
      {showGenerate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg w-full max-w-2xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-gray-900">Generate New Version</h3>
              <button
                className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
                onClick={() => setShowGenerate(false)}
              >
                Close
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Components</label>
                <div className="flex gap-2">
                  <input
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="Add components (comma-separated)…"
                    value={genComponentInput}
                    onChange={(e) => setGenComponentInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        addGenComponentsFromInput();
                      }
                    }}
                  />
                  <button
                    className="bg-gray-200 px-4 py-2 rounded-md hover:bg-gray-300"
                    onClick={addGenComponentsFromInput}
                  >
                    Add
                  </button>
                </div>
                {genComponents.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {genComponents.map((c) => (
                      <span key={c} className="inline-flex items-center gap-2 px-2 py-1 bg-gray-100 rounded-full text-sm">
                        {c}
                        <button
                          className="text-gray-500 hover:text-gray-800"
                          onClick={() => setGenComponents((prev) => prev.filter((x) => x !== c))}
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {(docType === 'hazard_analysis' || docType === 'residual_risk' || docType === 'benefit_risk_analysis') && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Version scope</label>
                    <select
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      value={versionScope}
                      onChange={(e) => setVersionScope(e.target.value as any)}
                    >
                      <option value="approved_only">Approved only</option>
                      <option value="current">Current</option>
                      <option value="all">All</option>
                    </select>
                  </div>
                  <label className="flex items-center gap-2 text-sm text-gray-700 mt-6">
                    <input
                      type="checkbox"
                      checked={!!genOptions.include_unapproved}
                      onChange={(e) => setGenOptions((o) => ({ ...o, include_unapproved: e.target.checked }))}
                    />
                    Include unapproved
                  </label>
                </div>
              )}

              {docType === 'benefit_risk_analysis' && (
                <div className="space-y-4 border-t border-gray-200 pt-4">
                  <label className="flex items-center gap-2 text-sm text-gray-700">
                    <input
                      type="checkbox"
                      checked={!!genOptions.approved_mode}
                      onChange={(e) => setGenOptions((o) => ({ ...o, approved_mode: e.target.checked }))}
                    />
                    Generate in approved mode
                  </label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Overall decision</label>
                      <select
                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                        value={benefitRiskDecision}
                        onChange={(e) => setBenefitRiskDecision(e.target.value)}
                      >
                        <option>Acceptable</option>
                        <option>Acceptable with Conditions</option>
                        <option>Not Acceptable</option>
                        <option>Not fully evaluable</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Issuance state</label>
                      <select
                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                        value={approvalIssuanceState}
                        onChange={(e) => setApprovalIssuanceState(e.target.value)}
                      >
                        <option>Draft</option>
                        <option>Approved</option>
                        <option>Issued</option>
                      </select>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Decision rationale</label>
                    <textarea
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      rows={3}
                      value={benefitRiskRationale}
                      onChange={(e) => setBenefitRiskRationale(e.target.value)}
                    />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <input className="px-3 py-2 border border-gray-300 rounded-md" placeholder="Author" value={approvalAuthor} onChange={(e) => setApprovalAuthor(e.target.value)} />
                    <input className="px-3 py-2 border border-gray-300 rounded-md" placeholder="Reviewer" value={approvalReviewer} onChange={(e) => setApprovalReviewer(e.target.value)} />
                    <input className="px-3 py-2 border border-gray-300 rounded-md" placeholder="Approver" value={approvalApprover} onChange={(e) => setApprovalApprover(e.target.value)} />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <input className="px-3 py-2 border border-gray-300 rounded-md" placeholder="Date (YYYY-MM-DD)" value={approvalDate} onChange={(e) => setApprovalDate(e.target.value)} />
                    <input className="px-3 py-2 border border-gray-300 rounded-md" placeholder="Version (e.g. 1.0)" value={approvalVersion} onChange={(e) => setApprovalVersion(e.target.value)} />
                  </div>
                </div>
              )}

              {docType === 'rmf' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <label className="flex items-center gap-2 text-sm text-gray-700">
                    <input
                      type="checkbox"
                      checked={!!genOptions.include_traceability}
                      onChange={(e) => setGenOptions((o) => ({ ...o, include_traceability: e.target.checked }))}
                    />
                    Include traceability
                  </label>
                  <label className="flex items-center gap-2 text-sm text-gray-700">
                    <input
                      type="checkbox"
                      checked={!!genOptions.include_ai_events}
                      onChange={(e) => setGenOptions((o) => ({ ...o, include_ai_events: e.target.checked }))}
                    />
                    Include AI events
                  </label>
                  <label className="flex items-center gap-2 text-sm text-gray-700">
                    <input
                      type="checkbox"
                      checked={!!genOptions.include_audit_log}
                      onChange={(e) => setGenOptions((o) => ({ ...o, include_audit_log: e.target.checked }))}
                    />
                    Include audit log
                  </label>
                </div>
              )}

              {docType === 'risk_controls_doc' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <label className="flex items-center gap-2 text-sm text-gray-700">
                    <input
                      type="checkbox"
                      checked={!!genOptions.active_controls_only}
                      onChange={(e) => setGenOptions((o) => ({ ...o, active_controls_only: e.target.checked }))}
                    />
                    Active controls only
                  </label>
                  <label className="flex items-center gap-2 text-sm text-gray-700">
                    <input
                      type="checkbox"
                      checked={!!genOptions.include_traceability}
                      onChange={(e) => setGenOptions((o) => ({ ...o, include_traceability: e.target.checked }))}
                    />
                    Include traceability details
                  </label>
                </div>
              )}

              {docType === 'residual_risk' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Acceptability profile</label>
                    <select
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      value={genOptions.acceptability_profile}
                      onChange={(e) => setGenOptions((o) => ({ ...o, acceptability_profile: e.target.value }))}
                    >
                      <option value="default_med_device">Default medical device</option>
                      <option value="custom">Custom</option>
                    </select>
                  </div>
                </div>
              )}

              {docType === 'rmp' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Scope</label>
                    <textarea
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      rows={3}
                      placeholder="Define the scope of the Risk Management Plan…"
                      value={rmpScope}
                      onChange={(e) => setRmpScope(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Intended Use</label>
                    <textarea
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      rows={3}
                      placeholder="Describe intended use, users, environment, and lifecycle…"
                      value={rmpIntendedUse}
                      onChange={(e) => setRmpIntendedUse(e.target.value)}
                    />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Acceptability profile</label>
                      <select
                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                        value={genOptions.acceptability_profile}
                        onChange={(e) => setGenOptions((o) => ({ ...o, acceptability_profile: e.target.value }))}
                      >
                        <option value="default_med_device">Default medical device</option>
                        <option value="custom">Custom</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <div className="block text-sm font-medium text-gray-700 mb-2">Review roles</div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {Object.entries(rmpReviewRoles).map(([role, requirement]) => (
                        <label key={role} className="text-sm text-gray-700">
                          <div className="mb-1 font-medium">{role.replace(/_/g, ' ')}</div>
                          <select
                            className="w-full px-3 py-2 border border-gray-300 rounded-md"
                            value={requirement}
                            onChange={(e) =>
                              setRmpReviewRoles((prev) => ({ ...prev, [role]: e.target.value }))
                            }
                          >
                            <option value="required">required</option>
                            <option value="optional">optional</option>
                          </select>
                        </label>
                      ))}
                    </div>
                    <div className="text-xs text-gray-500 mt-2">
                      Tip: leave Scope/Intended Use blank to generate with placeholders and edit later.
                    </div>
                  </div>
                </div>
              )}

              <div className="flex justify-end gap-2 pt-2">
                <button
                  className="bg-gray-200 px-4 py-2 rounded-md hover:bg-gray-300"
                  onClick={() => setShowGenerate(false)}
                  disabled={saving}
                >
                  Cancel
                </button>
                <button
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
                  onClick={generateNew}
                  disabled={saving}
                >
                  {saving ? 'Generating…' : 'Generate'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* FMEA version diff (controlled artifact comparison) */}
      {showCompare && isFmea && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-neutral-900/40 p-3 backdrop-blur-[1px] sm:p-4 print:hidden">
          <div
            className="flex max-h-[92vh] w-full max-w-[min(120rem,100%)] min-w-0 flex-col overflow-hidden rounded-lg border border-neutral-200 bg-white shadow-lg"
            role="dialog"
            aria-labelledby="fmea-compare-title"
          >
            <div className="flex flex-shrink-0 flex-wrap items-start justify-between gap-4 border-b border-neutral-200 bg-neutral-50 px-4 py-3 sm:px-5 sm:py-4">
              <div className="min-w-0">
                <h3 id="fmea-compare-title" className="text-lg font-semibold text-neutral-900">
                  FMEA report comparison
                </h3>
                <p className="mt-1 max-w-2xl text-xs leading-relaxed text-neutral-600">
                  Row-aligned diff across stored document versions or the live preview. Risk scores: green indicates
                  reduction, red indicates increase. Text edits use amber. For audit-grade lineage, plan backend
                  snapshots keyed by stable risk-item IDs (see code comments in{' '}
                  <code className="rounded border border-neutral-200 bg-neutral-100 px-1 font-mono text-[11px] text-neutral-800">
                    parseFmeaTableFromHtml
                  </code>
                  ).
                </p>
              </div>
              <button
                type="button"
                className="rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium text-neutral-800 hover:bg-neutral-50"
                onClick={() => setShowCompare(false)}
              >
                Close
              </button>
            </div>

            <div className="flex-shrink-0 border-b border-neutral-200 bg-white px-4 py-3 sm:px-5 sm:py-4">
              <div className="flex flex-wrap items-end gap-4">
                <VersionSelector
                  id="fmea-compare-baseline"
                  label="Baseline (older)"
                  value={compareLeft}
                  options={compareVersionOptions}
                  onChange={setCompareLeft}
                  disabled={compareLoading}
                />
                <VersionSelector
                  id="fmea-compare-target"
                  label="Target (newer)"
                  value={compareRight}
                  options={compareVersionOptions}
                  onChange={setCompareRight}
                  disabled={compareLoading}
                />
                <div className="flex flex-col gap-1">
                  <span className="text-[11px] font-semibold uppercase tracking-[0.12em] text-neutral-500">View</span>
                  <label className="flex cursor-pointer items-center gap-2 text-sm text-neutral-800">
                    <input
                      type="checkbox"
                      className="rounded border-neutral-300"
                      checked={compareHideUnchanged}
                      onChange={(e) => setCompareHideUnchanged(e.target.checked)}
                    />
                    Hide unchanged rows
                  </label>
                </div>
                <button
                  type="button"
                  className="rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800 disabled:opacity-50"
                  onClick={runFmeaCompare}
                  disabled={compareLoading}
                >
                  {compareLoading ? 'Loading…' : 'Run comparison'}
                </button>
              </div>
              {compareError ? <p className="mt-3 text-sm text-red-700">{compareError}</p> : null}
            </div>

            <div className="min-h-0 min-w-0 flex-1 overflow-y-auto px-4 py-4 sm:px-5">
              {diffResult ? (
                <ReportDiffView
                  leftHtml={diffResult.leftHtml}
                  rightHtml={diffResult.rightHtml}
                  leftLabel={diffResult.leftLabel}
                  rightLabel={diffResult.rightLabel}
                  hideUnchanged={compareHideUnchanged}
                />
              ) : (
                <p className="text-sm leading-relaxed text-neutral-600">
                  Select a baseline and target, then run the comparison. Use <strong>Live preview</strong> for the HTML
                  currently shown in Preview; use <strong>Stored v…</strong> for an immutable snapshot from the version
                  history.
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Versions Modal */}
      {showVersions && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg w-full max-w-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-gray-900">Document Versions</h3>
              <button
                className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
                onClick={() => setShowVersions(false)}
              >
                Close
              </button>
            </div>
            {versionsLoading ? (
              <div className="text-gray-600">Loading…</div>
            ) : versionsError ? (
              <div className="text-red-700">{versionsError}</div>
            ) : versions.length === 0 ? (
              <div className="text-gray-600">No versions found.</div>
            ) : (
              <div className="space-y-2">
                {versions.map((v) => (
                  <div key={v.id} className="border border-gray-200 rounded-md p-3 flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900">v{v.version}</div>
                      <div className="text-xs text-gray-500">{new Date(v.created_at).toLocaleString()}</div>
                      {v?.changes?.generated && (
                        <div className="text-xs text-blue-600 mt-1">Generated</div>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <button
                        className="bg-blue-600 text-white px-3 py-1 rounded-md hover:bg-blue-700"
                        onClick={() => viewVersion(v)}
                      >
                        View
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}


