/**
 * Post-market (MAUDE) structured report for quality / regulatory review.
 *
 * FUTURE_PDF_EXPORT:
 *   - Add @media print rules on `.postmarket-report-root` (hide buttons, force background white).
 *   - Or reuse `PostmarketReportResponsePayload` with jspdf + jspdf-autotable (already in package.json).
 *   - Or call a future POST /postmarket/report/pdf that returns application/pdf from the backend.
 */
import React, { useCallback, useState } from 'react';
import { isAxiosError } from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import {
  type PostmarketReportResponsePayload,
  addMissingPostmarketRiskToFmea,
  postPostmarketReport,
} from '../../api/postmarketRiskScore';

function cn(...parts: Array<string | false | undefined>): string {
  return parts.filter(Boolean).join(' ');
}

function formatApiError(e: unknown, fallback: string): string {
  if (isAxiosError(e)) {
    const d = e.response?.data as { detail?: unknown } | undefined;
    if (typeof d?.detail === 'string' && d.detail.trim()) return d.detail;
    if (e.response?.status === 403) return 'This feature requires a Pro plan.';
    if (e.message) return e.message;
  }
  if (e instanceof Error && e.message) return e.message;
  return fallback;
}

function formatDateLabel(iso?: string | null): string {
  if (!iso) return '—';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleDateString();
}

function outcomeBarClass(outcome: string): string {
  switch (outcome) {
    case 'death':
      return 'bg-red-500';
    case 'injury':
      return 'bg-amber-500';
    case 'malfunction':
      return 'bg-slate-500';
    case 'other':
      return 'bg-violet-500';
    default:
      return 'bg-zinc-400';
  }
}

function HorizontalBarRow({ label, value, max }: { label: string; value: number; max: number }) {
  const pct = max > 0 ? Math.min(100, Math.round((value / max) * 100)) : 0;
  return (
    <div className="mb-2">
      <div className="flex justify-between text-xs text-text-secondary mb-0.5">
        <span className="truncate pr-2" title={label}>
          {label}
        </span>
        <span className="shrink-0 tabular-nums">{value}</span>
      </div>
      <div className="h-2 rounded-full bg-surface-secondary overflow-hidden">
        <div className="h-full rounded-full bg-text-primary/70 transition-all" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export interface PostMarketReportProps {
  projectId: string;
  className?: string;
  initialDeviceType?: string;
  initialDeviceName?: string;
  initialComponent?: string;
  initialFailureMode?: string;
  /** Override default “Add to FMEA” API call. */
  onAddRiskToFmea?: (normalizedFailureMode: string, component?: string) => void | Promise<void>;
}

export const PostMarketReport: React.FC<PostMarketReportProps> = ({
  projectId,
  className = '',
  initialDeviceType = '',
  initialDeviceName = '',
  initialComponent = '',
  initialFailureMode = '',
  onAddRiskToFmea,
}) => {
  const [deviceType, setDeviceType] = useState(initialDeviceType);
  const [deviceName, setDeviceName] = useState(initialDeviceName);
  const [component, setComponent] = useState(initialComponent);
  const [failureMode, setFailureMode] = useState(initialFailureMode);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [includeMissing, setIncludeMissing] = useState(true);
  const [includeTrend, setIncludeTrend] = useState(true);
  const [includeOutcomes, setIncludeOutcomes] = useState(true);

  const [report, setReport] = useState<PostmarketReportResponsePayload | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [addBusy, setAddBusy] = useState<string | null>(null);
  const [addNotice, setAddNotice] = useState<string | null>(null);
  const [docSyncNotice, setDocSyncNotice] = useState<string | null>(null);

  const runReport = useCallback(async () => {
    setLoading(true);
    setError(null);
    setAddNotice(null);
    setDocSyncNotice(null);
    try {
      const data = await postPostmarketReport({
        project_id: projectId,
        device_type: deviceType.trim() || undefined,
        device_name: deviceName.trim() || undefined,
        component: component.trim() || undefined,
        failure_mode: failureMode.trim() || undefined,
        date_from: dateFrom.trim() || undefined,
        date_to: dateTo.trim() || undefined,
        include_missing_risks: includeMissing,
        include_trend_summary: includeTrend,
        include_outcome_breakdown: includeOutcomes,
      });
      setReport(data);
      const mode =
        data.report_mode ??
        (data.evidence_summary.total_maude_records_analyzed > 0 ? 'populated' : 'draft');
      if (mode === 'populated') {
        setDocSyncNotice(
          'The stored PMS Report project document (Documentation / Document Control) was refreshed from this run so it matches the populated report.'
        );
      }
    } catch (e: unknown) {
      setReport(null);
      setError(formatApiError(e, 'Report generation failed.'));
    } finally {
      setLoading(false);
    }
  }, [
    projectId,
    deviceType,
    deviceName,
    component,
    failureMode,
    dateFrom,
    dateTo,
    includeMissing,
    includeTrend,
    includeOutcomes,
  ]);

  const handleAdd = async (normalizedFailureMode: string, comp?: string | null) => {
    if (onAddRiskToFmea) {
      await onAddRiskToFmea(normalizedFailureMode, comp || undefined);
      return;
    }
    setAddBusy(normalizedFailureMode);
    setAddNotice(null);
    try {
      const compArg = (comp && comp.trim()) || (component.trim() ? component.trim() : undefined);
      const res = await addMissingPostmarketRiskToFmea({
        project_id: projectId,
        normalized_failure_mode: normalizedFailureMode,
        device_type: deviceType.trim() || undefined,
        component: compArg,
      });
      setAddNotice(res.message || `Draft row ${res.fmea_row_id} — expert review required.`);
    } catch (e: unknown) {
      setAddNotice(formatApiError(e, 'Add to FMEA failed.'));
    } finally {
      setAddBusy(null);
    }
  };

  const maxFm =
    report?.top_failure_modes?.length > 0
      ? Math.max(...report.top_failure_modes.map((f) => f.supporting_event_count), 1)
      : 1;
  const maxTrend =
    report?.trend_summary?.periods?.length > 0
      ? Math.max(...report.trend_summary.periods.map((p) => p.event_count), 1)
      : 1;

  const reportModeResolved =
    report == null
      ? 'draft'
      : report.report_mode ??
        (report.evidence_summary.total_maude_records_analyzed > 0 ? 'populated' : 'draft');

  return (
    <div className={cn('space-y-6', 'postmarket-report-root', className)}>
      <div>
        <h1 className="text-h2 font-semibold text-text-primary">Post-market report</h1>
        <p className="text-sm text-text-secondary mt-1 max-w-3xl">
          Structured summary from MAUDE-linked extractions. Wording is intentionally non-causal; use for expert
          review alongside design history and clinical evidence.
        </p>
      </div>

      <Card>
        <CardHeader className="py-4">
          <CardTitle className="text-base">Scope & filters</CardTitle>
        </CardHeader>
        <CardContent className="pt-0 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-text-secondary">Device type (MAUDE filter)</span>
            <input
              value={deviceType}
              onChange={(e) => setDeviceType(e.target.value)}
              placeholder="e.g. infusion pump — optional; else from project"
              className="rounded-md border border-border bg-surface-primary px-3 py-2 text-sm"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-text-secondary">Device name (report label)</span>
            <input
              value={deviceName}
              onChange={(e) => setDeviceName(e.target.value)}
              placeholder="Optional display label"
              className="rounded-md border border-border bg-surface-primary px-3 py-2 text-sm"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-text-secondary">Component contains</span>
            <input
              value={component}
              onChange={(e) => setComponent(e.target.value)}
              className="rounded-md border border-border bg-surface-primary px-3 py-2 text-sm"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm md:col-span-2">
            <span className="text-text-secondary">Failure mode contains</span>
            <input
              value={failureMode}
              onChange={(e) => setFailureMode(e.target.value)}
              className="rounded-md border border-border bg-surface-primary px-3 py-2 text-sm"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-text-secondary">Date from</span>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="rounded-md border border-border bg-surface-primary px-3 py-2 text-sm"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-text-secondary">Date to</span>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="rounded-md border border-border bg-surface-primary px-3 py-2 text-sm"
            />
          </label>
          <div className="flex flex-col gap-2 text-sm md:col-span-3">
            <label className="inline-flex items-center gap-2">
              <input type="checkbox" checked={includeMissing} onChange={(e) => setIncludeMissing(e.target.checked)} />
              Include missing FMEA themes
            </label>
            <label className="inline-flex items-center gap-2">
              <input type="checkbox" checked={includeTrend} onChange={(e) => setIncludeTrend(e.target.checked)} />
              Include trend summary
            </label>
            <label className="inline-flex items-center gap-2">
              <input type="checkbox" checked={includeOutcomes} onChange={(e) => setIncludeOutcomes(e.target.checked)} />
              Include outcome breakdown
            </label>
          </div>
          <div className="md:col-span-3 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => void runReport()}
              disabled={loading}
              className="rounded-md bg-text-primary text-surface-primary px-4 py-2 text-sm font-medium hover:opacity-90 disabled:opacity-50"
            >
              {loading ? 'Generating…' : 'Generate report'}
            </button>
          </div>
        </CardContent>
      </Card>

      {loading && (
        <div className="flex items-center gap-3 rounded-lg border border-border px-4 py-6" role="status">
          <span className="inline-block h-5 w-5 animate-spin rounded-full border-2 border-border border-t-text-primary" />
          <span className="text-sm text-text-secondary">Building report…</span>
        </div>
      )}

      {error && !loading && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-900" role="alert">
          {error}
        </div>
      )}

      {docSyncNotice && !loading && (
        <div className="rounded-lg border border-emerald-200 bg-emerald-50/80 px-4 py-3 text-sm text-emerald-950" role="status">
          {docSyncNotice}
        </div>
      )}

      {addNotice && (
        <div className="rounded-lg border border-border bg-surface-secondary/40 px-4 py-3 text-sm text-text-primary">
          {addNotice}
        </div>
      )}

      {!loading && !report && !error && (
        <Card>
          <CardContent className="py-10 text-center text-sm text-text-secondary">
            Set filters and click <strong>Generate report</strong> to load MAUDE-derived evidence for this project.
          </CardContent>
        </Card>
      )}

      {report && !loading && (
        <div className="space-y-6 print:shadow-none">
          <Card
            className={cn(
              'border-border',
              reportModeResolved === 'draft'
                ? 'border-amber-200 bg-amber-50/40'
                : 'border-emerald-200/80 bg-emerald-50/30'
            )}
          >
            <CardHeader>
              <CardTitle>{report.report_title}</CardTitle>
              <p className="text-xs text-text-secondary mt-2 font-normal">
                Project ID:{' '}
                <span className="text-text-primary font-mono">{report.project_summary.project_id}</span>
                {' · '}
                Project: <span className="text-text-primary font-medium">{report.project_summary.project_name}</span>
                {' · '}
                Mode:{' '}
                <span className="font-medium text-text-primary">
                  {reportModeResolved === 'populated' ? 'Data-backed' : 'Draft (no qualifying corpus)'}
                </span>
                {' · '}
                Last refreshed:{' '}
                <time dateTime={report.generated_at}>
                  {new Date(report.generated_at).toLocaleString()}
                </time>
              </p>
              {report.reporting_period?.label && (
                <p className="text-xs text-text-secondary mt-1 font-normal">
                  Reporting period: {report.reporting_period.label}
                  {report.reporting_period.markets_regions_note
                    ? ` · Markets/regions: ${report.reporting_period.markets_regions_note}`
                    : ''}
                </p>
              )}
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Scope / filters applied</CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-1 text-text-secondary">
              <p>
                Device type filter:{' '}
                <span className="text-text-primary font-medium">{report.filter_summary.device_type_used}</span>
              </p>
              {report.filter_summary.device_name_label && (
                <p>Label: {report.filter_summary.device_name_label}</p>
              )}
              {report.filter_summary.component_filter && <p>Component: {report.filter_summary.component_filter}</p>}
              {report.filter_summary.failure_mode_filter && (
                <p>Failure mode: {report.filter_summary.failure_mode_filter}</p>
              )}
              <p>
                Dates: {formatDateLabel(report.filter_summary.date_from)} →{' '}
                {formatDateLabel(report.filter_summary.date_to)}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Summary of data reviewed</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
                <div className="rounded-lg border border-border bg-surface-secondary/30 p-3">
                  <p className="text-xs uppercase text-text-secondary">MAUDE NLP-linked</p>
                  <p className="text-xl font-semibold tabular-nums text-text-primary">
                    {report.summary?.maude_nlp_linked_records_reviewed ??
                      report.evidence_summary.total_maude_records_analyzed}
                  </p>
                </div>
                <div className="rounded-lg border border-border bg-surface-secondary/30 p-3">
                  <p className="text-xs uppercase text-text-secondary">PMS signals (project)</p>
                  <p className="text-xl font-semibold tabular-nums text-text-primary">
                    {report.summary?.pms_signal_records_in_scope ?? 0}
                  </p>
                </div>
                <div className="rounded-lg border border-border bg-surface-secondary/30 p-3">
                  <p className="text-xs uppercase text-text-secondary">Unique failure modes</p>
                  <p className="text-xl font-semibold tabular-nums text-text-primary">
                    {report.summary?.unique_normalized_failure_modes ?? 0}
                  </p>
                </div>
                <div className="rounded-lg border border-border bg-surface-secondary/30 p-3">
                  <p className="text-xs uppercase text-text-secondary">Outcomes (M/A/I)</p>
                  <p className="text-sm tabular-nums text-text-primary mt-1">
                    malfunction {report.summary?.malfunction_outcome_events ?? 0} · injury{' '}
                    {report.summary?.injury_outcome_events ?? 0} · death{' '}
                    {report.summary?.death_outcome_events ?? 0}
                  </p>
                </div>
              </div>
              <div className="rounded-lg border border-border bg-surface-secondary/30 p-4">
                <p className="text-xs uppercase text-text-secondary">Date range in analyzed MAUDE rows</p>
                <p className="text-sm text-text-primary mt-1">
                  {formatDateLabel(
                    report.summary?.date_range_analyzed_start ?? report.evidence_summary.date_range_analyzed_start
                  )}{' '}
                  →{' '}
                  {formatDateLabel(
                    report.summary?.date_range_analyzed_end ?? report.evidence_summary.date_range_analyzed_end
                  )}
                </p>
              </div>
              <p className="text-sm leading-relaxed text-text-primary border-l-2 border-border pl-3">
                {report.evidence_summary.qualitative_summary}
              </p>
              {report.evidence_summary.component_focus_note && (
                <p className="text-sm text-text-secondary">{report.evidence_summary.component_focus_note}</p>
              )}
            </CardContent>
          </Card>

          {reportModeResolved === 'populated' && report.top_findings && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Top findings</CardTitle>
                <p className="text-xs text-text-secondary font-normal mt-1">
                  Ranked counts from the current filter — descriptive only.
                </p>
              </CardHeader>
              <CardContent className="grid md:grid-cols-2 gap-6 text-sm">
                <div>
                  <p className="text-xs font-semibold text-text-secondary mb-2">Failure modes</p>
                  <ul className="space-y-1">
                    {(report.top_findings.top_failure_modes || []).slice(0, 12).map((r) => (
                      <li key={r.phrase} className="flex justify-between gap-2">
                        <span className="truncate">{r.phrase}</span>
                        <span className="tabular-nums text-text-secondary">{r.count}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="text-xs font-semibold text-text-secondary mb-2">Top components</p>
                  <ul className="space-y-1">
                    {(report.top_findings.top_components || []).slice(0, 12).map((r) => (
                      <li key={r.phrase} className="flex justify-between gap-2">
                        <span className="truncate">{r.phrase}</span>
                        <span className="tabular-nums text-text-secondary">{r.count}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                {report.top_findings.trend_qualitative && (
                  <div className="md:col-span-2 text-text-secondary text-xs border-t border-border pt-3">
                    {report.top_findings.trend_qualitative}
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {report.signals_identified && report.signals_identified.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Signals identified</CardTitle>
                <p className="text-xs text-text-secondary font-normal mt-1">
                  Formal PMS signals and MAUDE-derived theme rows — expert review required before risk-file changes.
                </p>
              </CardHeader>
              <CardContent className="overflow-x-auto">
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="border-b border-border text-left text-xs text-text-secondary">
                      <th className="py-2 pr-3 font-medium">Signal ID</th>
                      <th className="py-2 pr-3 font-medium">Description</th>
                      <th className="py-2 pr-3 font-medium">Source</th>
                      <th className="py-2 pr-3 font-medium">Status</th>
                      <th className="py-2 font-medium">Notes</th>
                    </tr>
                  </thead>
                  <tbody>
                    {report.signals_identified.map((s) => (
                      <tr key={`${s.signal_id}-${s.description.slice(0, 24)}`} className="border-b border-border/60 align-top">
                        <td className="py-2 pr-3 font-mono text-xs whitespace-nowrap">{s.signal_id}</td>
                        <td className="py-2 pr-3 max-w-md">{s.description}</td>
                        <td className="py-2 pr-3 text-text-secondary whitespace-nowrap">{s.source}</td>
                        <td className="py-2 pr-3 capitalize whitespace-nowrap">{s.status.replace(/_/g, ' ')}</td>
                        <td className="py-2 text-text-secondary">{s.notes || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </CardContent>
            </Card>
          )}

          {includeOutcomes && report.outcome_breakdown.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Outcome breakdown</CardTitle>
                <p className="text-xs text-text-secondary font-normal mt-1">
                  NLP outcome labels in analyzed records (not clinical adjudication).
                </p>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-3">
                    {report.outcome_breakdown.map((o) => (
                      <div key={o.outcome}>
                        <div className="flex justify-between text-xs mb-1 capitalize">
                          <span className="text-text-primary">{o.outcome}</span>
                          <span className="text-text-secondary tabular-nums">
                            {o.count} ({o.percentage.toFixed(1)}%)
                          </span>
                        </div>
                        <div className="h-3 rounded-full bg-surface-secondary overflow-hidden">
                          <div
                            className={cn('h-full rounded-full', outcomeBarClass(o.outcome))}
                            style={{ width: `${Math.min(100, o.percentage)}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {includeTrend && report.trend_summary && report.trend_summary.periods.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Trend summary</CardTitle>
                <p className="text-xs text-text-secondary font-normal mt-1">
                  {report.trend_summary.granularity} counts — descriptive only.
                </p>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-text-primary mb-4">{report.trend_summary.qualitative_summary}</p>
                <div className="max-h-64 overflow-y-auto pr-1">
                  {report.trend_summary.periods.map((p) => (
                    <HorizontalBarRow
                      key={p.period_label}
                      label={p.period_label}
                      value={p.event_count}
                      max={maxTrend}
                    />
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Top failure modes</CardTitle>
            </CardHeader>
            <CardContent>
              {report.top_failure_modes.length === 0 ? (
                <p className="text-sm text-text-secondary">No failure-mode themes in this filter.</p>
              ) : (
                <div className="space-y-6">
                  <div className="md:hidden space-y-2">
                    {report.top_failure_modes.slice(0, 5).map((f) => (
                      <HorizontalBarRow
                        key={f.normalized_failure_mode}
                        label={f.normalized_failure_mode}
                        value={f.supporting_event_count}
                        max={maxFm}
                      />
                    ))}
                  </div>
                  <div className="space-y-8">
                    {report.top_failure_modes.map((f) => (
                      <div
                        key={f.normalized_failure_mode}
                        className="border border-border rounded-lg p-4 bg-surface-secondary/20"
                      >
                        <div className="flex flex-wrap items-baseline justify-between gap-2">
                          <h4 className="font-medium text-text-primary">{f.normalized_failure_mode}</h4>
                          <span className="text-xs text-text-secondary tabular-nums">
                            {f.supporting_event_count} events · weighted {f.weighted_event_count.toFixed(2)}
                            {f.suggested_probability_score != null ? ` · P̂ ${f.suggested_probability_score}` : ''}
                          </span>
                        </div>
                        <p className="text-xs text-text-secondary mt-2">{f.evidence_language_note}</p>
                        <div className="grid md:grid-cols-3 gap-4 mt-4 text-sm">
                          <div>
                            <p className="text-xs font-semibold text-text-secondary mb-1">Components</p>
                            <ul className="space-y-1">
                              {f.top_related_components.map((c) => (
                                <li key={c.phrase} className="flex justify-between gap-2">
                                  <span className="truncate">{c.phrase}</span>
                                  <span className="tabular-nums text-text-secondary">{c.count}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                          <div>
                            <p className="text-xs font-semibold text-text-secondary mb-1">Effects</p>
                            <ul className="space-y-1">
                              {f.top_related_effects.map((c) => (
                                <li key={c.phrase} className="flex justify-between gap-2">
                                  <span className="truncate">{c.phrase}</span>
                                  <span className="tabular-nums text-text-secondary">{c.count}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                          <div>
                            <p className="text-xs font-semibold text-text-secondary mb-1">Causes</p>
                            <ul className="space-y-1">
                              {f.top_related_causes.map((c) => (
                                <li key={c.phrase} className="flex justify-between gap-2">
                                  <span className="truncate">{c.phrase}</span>
                                  <span className="tabular-nums text-text-secondary">{c.count}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <div className="grid lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Top causes (corpus)</CardTitle>
              </CardHeader>
              <CardContent>
                {report.top_causes.length === 0 ? (
                  <p className="text-sm text-text-secondary">—</p>
                ) : (
                  <ul className="text-sm space-y-2">
                    {report.top_causes.map((c) => (
                      <li key={c.phrase} className="flex justify-between gap-2">
                        <span className="truncate">{c.phrase}</span>
                        <span className="tabular-nums text-text-secondary">{c.count}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Top effects (corpus)</CardTitle>
              </CardHeader>
              <CardContent>
                {report.top_effects.length === 0 ? (
                  <p className="text-sm text-text-secondary">—</p>
                ) : (
                  <ul className="text-sm space-y-2">
                    {report.top_effects.map((c) => (
                      <li key={c.phrase} className="flex justify-between gap-2">
                        <span className="truncate">{c.phrase}</span>
                        <span className="tabular-nums text-text-secondary">{c.count}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </CardContent>
            </Card>
          </div>

          {includeMissing && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Missing real-world risks</CardTitle>
                  <p className="text-xs text-text-secondary font-normal mt-1">
                    Themes in analyzed post-market data with weak FMEA coverage — expert review required.
                  </p>
                </CardHeader>
                <CardContent className="space-y-4">
                  {report.missing_real_world_risks.length === 0 ? (
                    <p className="text-sm text-text-secondary">None flagged for this scope.</p>
                  ) : (
                    report.missing_real_world_risks.map((r, i) => (
                      <div
                        key={`${r.normalized_failure_mode}-${i}`}
                        className="flex flex-col sm:flex-row sm:items-start gap-3 border border-border rounded-lg p-4"
                      >
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-text-primary">{r.normalized_failure_mode}</p>
                          <p className="text-xs text-text-secondary mt-1">{r.supporting_event_count} events</p>
                          <p className="text-sm mt-2 text-text-primary">{r.rationale}</p>
                          {r.requires_expert_review !== false && (
                            <p className="text-xs text-amber-900 mt-2 font-medium">Expert review required</p>
                          )}
                        </div>
                        {r.add_to_fmea_available && (
                          <button
                            type="button"
                            disabled={addBusy === r.normalized_failure_mode}
                            onClick={() => void handleAdd(r.normalized_failure_mode, r.component)}
                            className="print:hidden shrink-0 rounded-md border border-border px-3 py-2 text-sm font-medium hover:bg-surface-secondary disabled:opacity-50"
                          >
                            {addBusy === r.normalized_failure_mode ? 'Adding…' : 'Add to FMEA'}
                          </button>
                        )}
                      </div>
                    ))
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Recommended FMEA draft additions</CardTitle>
                  <p className="text-xs text-text-secondary font-normal mt-1">
                    Draft rows only — do not finalize without severity, detection, and controls analysis.
                  </p>
                </CardHeader>
                <CardContent className="space-y-4">
                  {report.recommended_fmea_drafts.length === 0 ? (
                    <p className="text-sm text-text-secondary">None for this scope.</p>
                  ) : (
                    report.recommended_fmea_drafts.map((r, i) => (
                      <div
                        key={`draft-${r.normalized_failure_mode}-${i}`}
                        className="flex flex-col sm:flex-row sm:items-start gap-3 border border-amber-200 bg-amber-50/40 rounded-lg p-4"
                      >
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-text-primary">{r.normalized_failure_mode}</p>
                          <p className="text-xs text-text-secondary mt-1">
                            {r.supporting_event_count} events
                            {r.weighted_event_count != null ? ` · weighted ${r.weighted_event_count}` : ''}
                          </p>
                          <p className="text-sm mt-2">{r.rationale}</p>
                          {r.requires_expert_review && (
                            <p className="text-xs text-amber-900 mt-2 font-medium">Expert review required</p>
                          )}
                        </div>
                        {r.add_to_fmea_available && (
                          <button
                            type="button"
                            disabled={addBusy === r.normalized_failure_mode}
                            onClick={() => void handleAdd(r.normalized_failure_mode, component)}
                            className="print:hidden shrink-0 rounded-md border border-border bg-surface-primary px-3 py-2 text-sm font-medium hover:bg-surface-secondary disabled:opacity-50"
                          >
                            {addBusy === r.normalized_failure_mode ? 'Adding…' : 'Add to FMEA'}
                          </button>
                        )}
                      </div>
                    ))
                  )}
                </CardContent>
              </Card>
            </>
          )}

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Recommended actions</CardTitle>
              <p className="text-xs text-text-secondary font-normal mt-1">
                Evidence-based prompts — not decisions.
              </p>
            </CardHeader>
            <CardContent>
              <ul className="text-sm space-y-2 list-disc pl-5 text-text-primary">
                {(report.recommended_actions || []).map((line, idx) => (
                  <li key={`${idx}-${line.slice(0, 64)}`}>{line}</li>
                ))}
              </ul>
              {(!report.recommended_actions || report.recommended_actions.length === 0) && (
                <p className="text-sm text-text-secondary">—</p>
              )}
            </CardContent>
          </Card>

          <Card className="border-amber-200 bg-amber-50/80">
            <CardHeader>
              <CardTitle className="text-base text-amber-950">Disclaimer & expert review</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-amber-950 space-y-3 leading-relaxed">
              <p>{report.disclaimer}</p>
              <p className="text-xs text-amber-900 border-t border-amber-200 pt-3">{report.future_data_sources_placeholder}</p>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default PostMarketReport;
