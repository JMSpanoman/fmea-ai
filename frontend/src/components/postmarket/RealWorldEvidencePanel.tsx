import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { isAxiosError } from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import {
  type FailureModeScoreResponse,
  type PostmarketMissingRisksResponse,
  type PostmarketRunPipelineResponse,
  type ProjectRiskScoreItem,
  type ProjectRiskScoreResponse,
  type RecentTrend,
  type SuggestedMissingRisk,
  addMissingPostmarketRiskToFmea,
  getPostmarketMissingRisks,
  getProjectRiskScore,
  postFailureModeScore,
  runPostmarketPipeline,
} from '../../api/postmarketRiskScore';

export interface RealWorldEvidencePanelProps {
  /** Device type filter (MAUDE / project vocabulary); optional if `projectId` loads project profile. */
  deviceType?: string;
  /** Optional component context for focused scoring. */
  component?: string;
  /** Failure mode text for POST `/postmarket/risk-score/failure-mode`. */
  failureMode?: string;
  /** When set, loads project aggregates and missing-vs-FMEA themes via GET. */
  projectId?: string;
  className?: string;
  /** Called when user clicks “Add to FMEA” for a missing post-market theme. */
  onAddMissingRiskToFmea?: (risk: SuggestedMissingRisk) => void;
  /** When true (default), show orchestration controls if project + device type are set. */
  showPipelineControls?: boolean;
}

export type TrendDisplayFilter = 'all' | RecentTrend;

function cn(...parts: Array<string | false | undefined>): string {
  return parts.filter(Boolean).join(' ');
}

function formatApiError(e: unknown, fallback: string): string {
  if (isAxiosError(e)) {
    const d = e.response?.data as { detail?: unknown } | undefined;
    if (typeof d?.detail === 'string' && d.detail.trim()) return d.detail;
    if (Array.isArray(d?.detail)) {
      const parts = d.detail.map((x: { msg?: string }) => x?.msg).filter(Boolean);
      if (parts.length) return parts.join('; ');
    }
    if (e.response?.status === 403) {
      return 'This feature requires a Pro plan.';
    }
    if (e.message) return e.message;
  }
  if (e instanceof Error && e.message) return e.message;
  return fallback;
}

export function formatTrendLabel(trend: RecentTrend): string {
  switch (trend) {
    case 'increasing':
      return 'Increasing';
    case 'decreasing':
      return 'Decreasing';
    case 'stable':
      return 'Stable';
    default:
      return 'Insufficient data';
  }
}

export function trendBadgeClass(trend: RecentTrend): string {
  switch (trend) {
    case 'increasing':
      return 'bg-amber-50 text-amber-900 border-amber-200';
    case 'decreasing':
      return 'bg-emerald-50 text-emerald-900 border-emerald-200';
    case 'stable':
      return 'bg-slate-50 text-slate-800 border-slate-200';
    default:
      return 'bg-slate-50 text-slate-600 border-slate-200';
  }
}

export function confidenceBadgeClass(level: string): string {
  switch (level) {
    case 'high':
      return 'bg-blue-50 text-blue-900 border-blue-200';
    case 'medium':
      return 'bg-violet-50 text-violet-900 border-violet-200';
    default:
      return 'bg-slate-50 text-slate-700 border-slate-200';
  }
}

export function probabilityMeter(score: number): string {
  const s = Math.min(5, Math.max(1, Math.round(score)));
  return Array.from({ length: 5 }, (_, i) => (i < s ? '●' : '○')).join(' ');
}

function PhraseList({
  title,
  rows,
  empty,
}: {
  title: string;
  rows: { phrase: string; count: number }[];
  empty: string;
}) {
  if (!rows?.length) {
    return <p className="text-sm text-text-secondary">{empty}</p>;
  }
  return (
    <div>
      <p className="text-xs font-medium uppercase tracking-wide text-text-secondary mb-2">{title}</p>
      <ul className="space-y-1.5">
        {rows.slice(0, 8).map((r) => (
          <li
            key={`${title}-${r.phrase}-${r.count}`}
            className="flex justify-between gap-3 text-sm text-text-primary"
          >
            <span className="truncate" title={r.phrase}>
              {r.phrase}
            </span>
            <span className="shrink-0 tabular-nums text-text-secondary">{r.count}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function FocusedScoreBody({ data }: { data: FailureModeScoreResponse }) {
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end gap-4">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-text-secondary mb-1">
            Suggested probability (1–5)
          </p>
          <div className="flex items-baseline gap-3">
            <span className="text-3xl font-semibold tabular-nums text-text-primary">
              {data.suggested_probability_score}
            </span>
            <span
              className="text-lg font-mono text-text-secondary tracking-widest"
              aria-hidden
            >
              {probabilityMeter(data.suggested_probability_score)}
            </span>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <span
            className={cn(
              'inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium',
              trendBadgeClass(data.recent_trend)
            )}
          >
            Trend: {formatTrendLabel(data.recent_trend)}
          </span>
          <span
            className={cn(
              'inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium capitalize',
              confidenceBadgeClass(data.confidence_level)
            )}
          >
            Confidence: {data.confidence_level}
          </span>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="rounded-lg border border-border bg-surface-secondary/40 px-3 py-2">
          <p className="text-xs text-text-secondary">Supporting events</p>
          <p className="text-lg font-semibold tabular-nums text-text-primary">
            {data.supporting_event_count}
          </p>
        </div>
        <div className="rounded-lg border border-border bg-surface-secondary/40 px-3 py-2">
          <p className="text-xs text-text-secondary">Weighted total</p>
          <p className="text-lg font-semibold tabular-nums text-text-primary">
            {data.weighted_event_count.toFixed(1)}
          </p>
        </div>
        <div className="rounded-lg border border-border bg-surface-secondary/40 px-3 py-2 sm:col-span-2">
          <p className="text-xs text-text-secondary">Query window</p>
          <p className="text-sm text-text-primary">
            {[data.date_from ?? '—', data.date_to ?? '—'].join(' → ')}
          </p>
        </div>
      </div>
      <p className="text-sm leading-relaxed text-text-primary border-l-2 border-border pl-3">
        {data.rationale}
      </p>
      <div className="grid gap-6 sm:grid-cols-2">
        <PhraseList title="Top related causes" rows={data.top_related_causes} empty="No cause phrases." />
        <PhraseList title="Top related effects" rows={data.top_related_effects} empty="No effect phrases." />
      </div>
    </div>
  );
}

function filterTrendingItems(
  items: ProjectRiskScoreItem[],
  minScore: number,
  trendFilter: TrendDisplayFilter
): ProjectRiskScoreItem[] {
  return items.filter((it) => {
    if (it.suggested_probability_score < minScore) return false;
    if (trendFilter === 'all') return true;
    return it.recent_trend === trendFilter;
  });
}

export const RealWorldEvidencePanel: React.FC<RealWorldEvidencePanelProps> = ({
  deviceType,
  component,
  failureMode,
  projectId,
  className = '',
  onAddMissingRiskToFmea,
  showPipelineControls = true,
}) => {
  const [projectData, setProjectData] = useState<ProjectRiskScoreResponse | null>(null);
  const [matchReport, setMatchReport] = useState<PostmarketMissingRisksResponse | null>(null);
  const [matchError, setMatchError] = useState<string | null>(null);
  const [focusedScore, setFocusedScore] = useState<FailureModeScoreResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [projectError, setProjectError] = useState<string | null>(null);
  const [focusError, setFocusError] = useState<string | null>(null);

  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [minSuggestedProbability, setMinSuggestedProbability] = useState(1);
  const [trendFilter, setTrendFilter] = useState<TrendDisplayFilter>('all');

  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [pipelineResult, setPipelineResult] = useState<PostmarketRunPipelineResponse | null>(null);
  const [pipelineError, setPipelineError] = useState<string | null>(null);
  const [manufacturerName, setManufacturerName] = useState('');
  const [runIngestion, setRunIngestion] = useState(true);
  const [runExtraction, setRunExtraction] = useState(true);
  const [runScoring, setRunScoring] = useState(true);

  const [addFmeaBusyKey, setAddFmeaBusyKey] = useState<string | null>(null);
  const [addFmeaMessage, setAddFmeaMessage] = useState<string | null>(null);
  const [addFmeaError, setAddFmeaError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setProjectError(null);
    setFocusError(null);
    setMatchError(null);
    const hasProject = Boolean(projectId?.trim());
    const fm = failureMode?.trim();
    const dtProp = deviceType?.trim();

    if (!hasProject && (!fm || !dtProp)) {
      setProjectData(null);
      setMatchReport(null);
      setFocusedScore(null);
      return;
    }

    setLoading(true);
    let project: ProjectRiskScoreResponse | null = null;

    if (hasProject) {
      try {
        const proj = await getProjectRiskScore(projectId!.trim(), {
          deviceType: dtProp || undefined,
        });
        project = proj;
        setProjectData(proj);
        try {
          const m = await getPostmarketMissingRisks(projectId!.trim(), {
            deviceType: dtProp || proj.device_type_used || undefined,
          });
          setMatchReport(m);
        } catch (e: unknown) {
          setMatchReport(null);
          setMatchError(formatApiError(e, 'FMEA alignment report failed.'));
        }
      } catch (e: unknown) {
        setProjectData(null);
        setMatchReport(null);
        setProjectError(formatApiError(e, 'Project risk score request failed.'));
      }
    } else {
      setProjectData(null);
      setMatchReport(null);
    }

    const effectiveDevice = dtProp || project?.device_type_used?.trim() || '';
    if (fm && effectiveDevice) {
      try {
        const focused = await postFailureModeScore({
          device_type: effectiveDevice,
          failure_mode: fm,
          component: component?.trim() || undefined,
          date_from: dateFrom.trim() || undefined,
          date_to: dateTo.trim() || undefined,
        });
        setFocusedScore(focused);
      } catch (e: unknown) {
        setFocusedScore(null);
        setFocusError(formatApiError(e, 'Failure-mode score request failed.'));
      }
    } else {
      setFocusedScore(null);
      if (fm && !effectiveDevice) {
        setFocusError(
          'Device type is required for focused scoring (pass deviceType or load a project first).'
        );
      }
    }

    setLoading(false);
  }, [projectId, deviceType, component, failureMode, dateFrom, dateTo]);

  useEffect(() => {
    void load();
  }, [load]);

  const filteredTrending = useMemo(() => {
    if (!projectData?.items?.length) return [];
    const sorted = [...projectData.items].sort(
      (a, b) => b.weighted_event_count - a.weighted_event_count
    );
    return filterTrendingItems(sorted, minSuggestedProbability, trendFilter);
  }, [projectData, minSuggestedProbability, trendFilter]);

  const hasAnyContext = Boolean(projectId?.trim() || (deviceType?.trim() && failureMode?.trim()));

  const missingRisksList: SuggestedMissingRisk[] = matchReport
    ? matchReport.likely_missing_risks
    : projectData?.suggested_missing_risks ?? [];

  const canRunPipeline = Boolean(projectId?.trim() && deviceType?.trim());

  const handleRunPipeline = async () => {
    if (!canRunPipeline) return;
    setPipelineRunning(true);
    setPipelineError(null);
    setPipelineResult(null);
    try {
      const res = await runPostmarketPipeline({
        project_id: projectId!.trim(),
        device_type: deviceType!.trim(),
        manufacturer_name: manufacturerName.trim() || undefined,
        component: component?.trim() || undefined,
        failure_mode: failureMode?.trim() || undefined,
        date_from: dateFrom.trim() || undefined,
        date_to: dateTo.trim() || undefined,
        run_ingestion: runIngestion,
        run_extraction: runExtraction,
        run_scoring: runScoring,
      });
      setPipelineResult(res);
      await load();
    } catch (e: unknown) {
      setPipelineError(formatApiError(e, 'Pipeline run failed.'));
    } finally {
      setPipelineRunning(false);
    }
  };

  const handleAddToFmea = async (risk: SuggestedMissingRisk) => {
    if (onAddMissingRiskToFmea) {
      onAddMissingRiskToFmea(risk);
      return;
    }
    if (!projectId?.trim()) return;
    setAddFmeaBusyKey(risk.failure_mode_hint);
    setAddFmeaError(null);
    setAddFmeaMessage(null);
    try {
      const res = await addMissingPostmarketRiskToFmea({
        project_id: projectId.trim(),
        normalized_failure_mode: risk.failure_mode_hint,
        device_type: deviceType?.trim() || undefined,
        component: component?.trim() || undefined,
      });
      setAddFmeaMessage(res.message || `Draft FMEA row ${res.fmea_row_id} created.`);
    } catch (e: unknown) {
      setAddFmeaError(formatApiError(e, 'Could not create draft FMEA row.'));
    } finally {
      setAddFmeaBusyKey(null);
    }
  };

  return (
    <div className={cn('space-y-6', className)}>
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-h2 text-text-primary font-semibold">Real-world evidence (MAUDE)</h2>
          <p className="text-sm text-text-secondary mt-1 max-w-3xl">
            Post-market surveillance signals linked to NLP-extracted themes. Use alongside design and clinical
            inputs—not as standalone incidence estimates.
          </p>
        </div>
      </div>

      <div
        className="rounded-lg border border-amber-200 bg-amber-50/80 px-4 py-3 text-sm text-amber-950"
        role="note"
      >
        <strong className="font-semibold">Regulatory note:</strong> MAUDE-derived frequencies are supportive
        evidence only and reflect reporting biases. Probability suggestions require expert review in QMS /
        clinical context before updating FMEA rows.
      </div>

      {showPipelineControls && projectId?.trim() && (
        <Card>
          <CardHeader className="py-4">
            <CardTitle className="text-base">Post-market pipeline</CardTitle>
            <p className="text-xs text-text-secondary mt-1 font-normal">
              Ingest openFDA MAUDE rows, run narrative NLP, refresh scoring. Requires Pro plan,{' '}
              <code className="text-xs bg-surface-secondary px-1 rounded">deviceType</code>, and{' '}
              <code className="text-xs bg-surface-secondary px-1 rounded">OPENAI_API_KEY</code> for extraction.
            </p>
          </CardHeader>
          <CardContent className="pt-0 space-y-4">
            {!canRunPipeline && (
              <p className="text-sm text-amber-800 bg-amber-50 border border-amber-200 rounded-md px-3 py-2">
                Set <code className="text-xs">deviceType</code> to run the pipeline for this project.
              </p>
            )}
            <label className="flex flex-col gap-1 text-sm max-w-md">
              <span className="text-text-secondary">Manufacturer filter (ingest)</span>
              <input
                type="text"
                value={manufacturerName}
                onChange={(e) => setManufacturerName(e.target.value)}
                placeholder="Optional — openFDA manufacturer_d_name"
                className="rounded-md border border-border bg-surface-primary px-3 py-2 text-text-primary text-sm"
              />
            </label>
            <div className="flex flex-wrap gap-4 text-sm">
              <label className="inline-flex items-center gap-2 cursor-pointer">
                <input type="checkbox" checked={runIngestion} onChange={(e) => setRunIngestion(e.target.checked)} />
                Ingest MAUDE
              </label>
              <label className="inline-flex items-center gap-2 cursor-pointer">
                <input type="checkbox" checked={runExtraction} onChange={(e) => setRunExtraction(e.target.checked)} />
                NLP extract
              </label>
              <label className="inline-flex items-center gap-2 cursor-pointer">
                <input type="checkbox" checked={runScoring} onChange={(e) => setRunScoring(e.target.checked)} />
                Score / aggregate
              </label>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <button
                type="button"
                disabled={!canRunPipeline || pipelineRunning}
                onClick={() => void handleRunPipeline()}
                className="rounded-md bg-text-primary text-surface-primary px-4 py-2 text-sm font-medium hover:opacity-90 disabled:opacity-50"
              >
                {pipelineRunning ? 'Running pipeline…' : 'Run pipeline'}
              </button>
              {pipelineResult && (
                <span className="text-xs text-text-secondary">
                  Last run: {pipelineResult.status} · inserted {pipelineResult.records_inserted} · extracted{' '}
                  {pipelineResult.records_extracted}
                  {pipelineResult.pipeline_run_id ? ` · run ${pipelineResult.pipeline_run_id.slice(0, 8)}…` : ''}
                </span>
              )}
            </div>
            {pipelineError && (
              <div className="text-sm text-red-800 bg-red-50 border border-red-200 rounded-md px-3 py-2" role="alert">
                {pipelineError}
              </div>
            )}
            {pipelineResult?.warnings?.length ? (
              <div className="text-sm text-amber-950 bg-amber-50 border border-amber-200 rounded-md px-3 py-2">
                <p className="font-medium">Pipeline warnings</p>
                <ul className="list-disc pl-5 mt-1 space-y-0.5">
                  {pipelineResult.warnings.map((w, i) => (
                    <li key={i}>{w}</li>
                  ))}
                </ul>
              </div>
            ) : null}
            {pipelineResult?.disclaimer && (
              <p className="text-xs text-text-secondary border-l-2 border-border pl-3">{pipelineResult.disclaimer}</p>
            )}
          </CardContent>
        </Card>
      )}

      {(addFmeaMessage || addFmeaError) && (
        <div className="space-y-2">
          {addFmeaMessage && (
            <div className="text-sm text-emerald-900 bg-emerald-50 border border-emerald-200 rounded-md px-3 py-2">
              {addFmeaMessage}
            </div>
          )}
          {addFmeaError && (
            <div className="text-sm text-red-800 bg-red-50 border border-red-200 rounded-md px-3 py-2" role="alert">
              {addFmeaError}
            </div>
          )}
        </div>
      )}

      <Card>
        <CardHeader className="py-4">
          <CardTitle className="text-base">Filters</CardTitle>
          <p className="text-xs text-text-secondary mt-1 font-normal">
            Date range applies to the focused failure-mode score (POST). Project aggregates use the server
            lookback window.
          </p>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="flex flex-col gap-4 lg:flex-row lg:flex-wrap lg:items-end">
            <label className="flex flex-col gap-1 text-sm min-w-[140px]">
              <span className="text-text-secondary">Date from</span>
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="rounded-md border border-border bg-surface-primary px-3 py-2 text-text-primary text-sm"
              />
            </label>
            <label className="flex flex-col gap-1 text-sm min-w-[140px]">
              <span className="text-text-secondary">Date to</span>
              <input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                className="rounded-md border border-border bg-surface-primary px-3 py-2 text-text-primary text-sm"
              />
            </label>
            <label className="flex flex-col gap-1 text-sm min-w-[200px]">
              <span className="text-text-secondary">Trending — min. suggested P</span>
              <select
                value={minSuggestedProbability}
                onChange={(e) => setMinSuggestedProbability(Number(e.target.value))}
                className="rounded-md border border-border bg-surface-primary px-3 py-2 text-text-primary text-sm"
              >
                {[1, 2, 3, 4, 5].map((n) => (
                  <option key={n} value={n}>
                    {n}+ (severity filter)
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-sm min-w-[200px]">
              <span className="text-text-secondary">Trending — trend type</span>
              <select
                value={trendFilter}
                onChange={(e) => setTrendFilter(e.target.value as TrendDisplayFilter)}
                className="rounded-md border border-border bg-surface-primary px-3 py-2 text-text-primary text-sm"
              >
                <option value="all">All trends</option>
                <option value="increasing">Increasing only</option>
                <option value="stable">Stable only</option>
                <option value="decreasing">Decreasing only</option>
                <option value="insufficient_data">Insufficient data only</option>
              </select>
            </label>
            <button
              type="button"
              onClick={() => void load()}
              className="rounded-md bg-text-primary text-surface-primary px-4 py-2 text-sm font-medium hover:opacity-90"
            >
              Refresh
            </button>
          </div>
        </CardContent>
      </Card>

      {loading && (
        <div
          className="flex items-center gap-3 rounded-lg border border-border bg-surface-primary px-4 py-6"
          role="status"
          aria-live="polite"
        >
          <span className="inline-block h-5 w-5 animate-spin rounded-full border-2 border-border border-t-text-primary" />
          <span className="text-sm text-text-secondary">Loading MAUDE-linked evidence…</span>
        </div>
      )}

      {projectError && !loading && (
        <div
          className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-900"
          role="alert"
        >
          {projectError}
        </div>
      )}

      {focusError && !loading && (
        <div
          className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950"
          role="alert"
        >
          {focusError}
        </div>
      )}

      {matchError && !loading && projectId?.trim() && (
        <div
          className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950"
          role="alert"
        >
          {matchError}
        </div>
      )}

      {!loading && !hasAnyContext && (
        <Card>
          <CardContent className="py-10 text-center">
            <p className="text-text-primary font-medium">No scope selected</p>
            <p className="text-sm text-text-secondary mt-2 max-w-md mx-auto">
              Pass a <code className="text-xs bg-surface-secondary px-1 rounded">projectId</code> for project-wide
              aggregates and missing risks, and/or{' '}
              <code className="text-xs bg-surface-secondary px-1 rounded">deviceType</code> with{' '}
              <code className="text-xs bg-surface-secondary px-1 rounded">failureMode</code> for a focused
              probability suggestion.
            </p>
          </CardContent>
        </Card>
      )}

      {!loading && hasAnyContext && (
        <div className="grid gap-6 lg:grid-cols-2">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Probability suggestion</CardTitle>
              <p className="text-xs text-text-secondary mt-1 font-normal">
                Focused query:{' '}
                {failureMode?.trim()
                  ? `“${failureMode.trim()}”`
                  : 'Provide `failureMode` to run the failure-mode scorer.'}
              </p>
            </CardHeader>
            <CardContent>
              {focusedScore && <FocusedScoreBody data={focusedScore} />}
              {!focusedScore && failureMode?.trim() && !loading && (
                <p className="text-sm text-text-secondary">
                  {focusError
                    ? 'Focused score unavailable — see the alert above.'
                    : !(deviceType?.trim() || projectData?.device_type_used)
                      ? 'Waiting for device type (prop or loaded project) to score this failure mode.'
                      : 'No focused score returned for this query.'}
                </p>
              )}
              {!failureMode?.trim() && (
                <p className="text-sm text-text-secondary">
                  Embed this panel with a <code className="text-xs bg-surface-secondary px-1 rounded">failureMode</code>{' '}
                  prop (e.g. from an FMEA row) to populate this card.
                </p>
              )}
            </CardContent>
          </Card>

          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Evidence summary</CardTitle>
            </CardHeader>
            <CardContent>
              {projectData ? (
                <div className="grid gap-6 md:grid-cols-3">
                  <div>
                    <p className="text-xs font-medium uppercase text-text-secondary mb-2">Project window</p>
                    <p className="text-sm text-text-primary">
                      {[projectData.date_from ?? '—', projectData.date_to ?? '—'].join(' → ')}
                    </p>
                    <p className="text-xs text-text-secondary mt-2">
                      Device type used:{' '}
                      <span className="text-text-primary font-medium">{projectData.device_type_used}</span>
                    </p>
                  </div>
                  <div>
                    <p className="text-xs font-medium uppercase text-text-secondary mb-2">Failure-mode themes</p>
                    <p className="text-2xl font-semibold tabular-nums text-text-primary">
                      {projectData.items.length}
                    </p>
                    <p className="text-xs text-text-secondary">Returned in this response</p>
                  </div>
                  <div>
                    <p className="text-xs font-medium uppercase text-text-secondary mb-2">Gaps vs FMEA</p>
                    <p className="text-2xl font-semibold tabular-nums text-text-primary">
                      {missingRisksList.length}
                    </p>
                    <p className="text-xs text-text-secondary">Suggested missing real-world risks</p>
                  </div>
                </div>
              ) : focusedScore ? (
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <p className="text-xs font-medium uppercase text-text-secondary mb-2">Device type</p>
                    <p className="text-sm text-text-primary">{focusedScore.device_type}</p>
                  </div>
                  <div>
                    <p className="text-xs font-medium uppercase text-text-secondary mb-2">Component filter</p>
                    <p className="text-sm text-text-primary">{focusedScore.component_filter ?? '—'}</p>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-text-secondary">
                  Open from a project to see corpus-wide evidence summary, or run a focused query above.
                </p>
              )}
              {projectData && (
                <div className="mt-6 grid gap-6 md:grid-cols-2">
                  <div>
                    <p className="text-xs font-medium uppercase text-text-secondary mb-2">
                      Device family roll-up (MAUDE)
                    </p>
                    {projectData.device_family_aggregates.length === 0 ? (
                      <p className="text-sm text-text-secondary">No aggregates.</p>
                    ) : (
                      <ul className="space-y-1 text-sm">
                        {projectData.device_family_aggregates.slice(0, 6).map((d) => (
                          <li key={d.device_family} className="flex justify-between gap-2">
                            <span className="truncate text-text-primary" title={d.device_family}>
                              {d.device_family}
                            </span>
                            <span className="shrink-0 tabular-nums text-text-secondary">
                              {d.supporting_event_count} evt / {d.weighted_event_count.toFixed(1)} w
                            </span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                  <div>
                    <p className="text-xs font-medium uppercase text-text-secondary mb-2">
                      Component themes (NLP)
                    </p>
                    {projectData.component_aggregates.length === 0 ? (
                      <p className="text-sm text-text-secondary">No aggregates.</p>
                    ) : (
                      <ul className="space-y-1 text-sm">
                        {projectData.component_aggregates.slice(0, 6).map((c) => (
                          <li key={c.component_text} className="flex justify-between gap-2">
                            <span className="truncate text-text-primary" title={c.component_text}>
                              {c.component_text}
                            </span>
                            <span className="shrink-0 tabular-nums text-text-secondary">
                              {c.supporting_event_count} evt / {c.weighted_event_count.toFixed(1)} w
                            </span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {matchReport && projectData && (
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>FMEA alignment</CardTitle>
                <p className="text-xs text-text-secondary mt-1 font-normal">
                  Post-market themes matched to existing FMEA failure modes vs. themes with no strong FMEA match.
                </p>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-text-secondary mb-4 border-l-2 border-border pl-3">{matchReport.disclaimer}</p>
                <div className="grid gap-6 lg:grid-cols-2">
                  <div>
                    <p className="text-xs font-semibold uppercase text-text-secondary mb-2">Matched themes</p>
                    {matchReport.matched_themes.length === 0 ? (
                      <p className="text-sm text-text-secondary">No scored themes linked to FMEA rows.</p>
                    ) : (
                      <ul className="space-y-2 text-sm max-h-56 overflow-y-auto">
                        {matchReport.matched_themes.slice(0, 12).map((m) => (
                          <li key={m.normalized_failure_mode} className="border border-border rounded-md p-2">
                            <p className="font-medium text-text-primary truncate" title={m.normalized_failure_mode}>
                              {m.normalized_failure_mode}
                            </p>
                            <p className="text-xs text-text-secondary mt-1">
                              FMEA: {m.matched_fmea_failure_mode ?? m.matched_fmea_row_id}
                            </p>
                            <p className="text-xs text-text-secondary">
                              P̂ {m.suggested_probability_score} · {m.supporting_event_count} events
                            </p>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                  <div>
                    <p className="text-xs font-semibold uppercase text-text-secondary mb-2">Unmatched themes</p>
                    {matchReport.unmatched_themes.length === 0 ? (
                      <p className="text-sm text-text-secondary">All scored themes align with an FMEA row.</p>
                    ) : (
                      <ul className="space-y-2 text-sm max-h-56 overflow-y-auto">
                        {matchReport.unmatched_themes.slice(0, 12).map((u) => (
                          <li key={u.normalized_failure_mode} className="border border-border rounded-md p-2">
                            <p className="font-medium text-text-primary truncate" title={u.normalized_failure_mode}>
                              {u.normalized_failure_mode}
                            </p>
                            <p className="text-xs text-text-secondary">
                              P̂ {u.suggested_probability_score} · {u.supporting_event_count} events
                            </p>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {projectData && (
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Trending risks</CardTitle>
                <p className="text-xs text-text-secondary mt-1 font-normal">
                  Post-market themes ranked by weighted signal (filtered below).
                </p>
              </CardHeader>
              <CardContent>
                {filteredTrending.length === 0 ? (
                  <p className="text-sm text-text-secondary">
                    No themes match the current trend and minimum probability filters.
                  </p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                      <thead>
                        <tr className="border-b border-border text-xs uppercase text-text-secondary">
                          <th className="py-2 pr-4 font-medium">Failure mode</th>
                          <th className="py-2 pr-4 font-medium">P̂</th>
                          <th className="py-2 pr-4 font-medium">Events</th>
                          <th className="py-2 pr-4 font-medium">Weighted</th>
                          <th className="py-2 pr-4 font-medium">Trend</th>
                          <th className="py-2 font-medium">Confidence</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredTrending.map((row) => (
                          <tr key={row.normalized_failure_mode} className="border-b border-border/60">
                            <td className="py-2 pr-4 text-text-primary max-w-xs truncate" title={row.normalized_failure_mode}>
                              {row.normalized_failure_mode}
                            </td>
                            <td className="py-2 pr-4 tabular-nums">{row.suggested_probability_score}</td>
                            <td className="py-2 pr-4 tabular-nums">{row.supporting_event_count}</td>
                            <td className="py-2 pr-4 tabular-nums">{row.weighted_event_count.toFixed(1)}</td>
                            <td className="py-2 pr-4">
                              <span
                                className={cn(
                                  'inline-flex rounded border px-1.5 py-0.5 text-xs',
                                  trendBadgeClass(row.recent_trend)
                                )}
                              >
                                {formatTrendLabel(row.recent_trend)}
                              </span>
                            </td>
                            <td className="py-2 capitalize text-text-secondary">{row.confidence_level}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {projectData && (
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Missing real-world risks</CardTitle>
                <p className="text-xs text-text-secondary mt-1 font-normal">
                  Themes seen in post-market data with weak coverage in this project&apos;s FMEA / risk items.
                </p>
              </CardHeader>
              <CardContent>
                {missingRisksList.length === 0 ? (
                  <p className="text-sm text-text-secondary">
                    No additional gaps surfaced, or corpus is sparse for this device context.
                  </p>
                ) : (
                  <ul className="space-y-4">
                    {missingRisksList.map((risk, idx) => (
                      <li
                        key={`${risk.failure_mode_hint}-${idx}`}
                        className="rounded-lg border border-border bg-surface-secondary/30 p-4 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"
                      >
                        <div className="min-w-0 flex-1">
                          <p className="font-medium text-text-primary">{risk.failure_mode_hint}</p>
                          <p className="text-xs text-text-secondary mt-1">
                            {risk.supporting_event_count} events · weighted {risk.weighted_event_count.toFixed(1)}
                          </p>
                          <p className="text-sm text-text-primary mt-2 leading-relaxed">{risk.rationale}</p>
                        </div>
                        {(onAddMissingRiskToFmea || projectId?.trim()) && (
                          <button
                            type="button"
                            disabled={addFmeaBusyKey === risk.failure_mode_hint}
                            onClick={() => void handleAddToFmea(risk)}
                            className="shrink-0 rounded-md border border-border bg-surface-primary px-3 py-2 text-sm font-medium text-text-primary hover:bg-surface-secondary disabled:opacity-50"
                          >
                            {addFmeaBusyKey === risk.failure_mode_hint ? 'Adding…' : 'Add to FMEA'}
                          </button>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
};

export default RealWorldEvidencePanel;
