/**
 * Compact post-market report snapshot for dashboards.
 * FUTURE_PDF: same JSON can feed a one-page executive PDF; keep section order stable.
 */
import React, { useEffect, useState } from 'react';
import { isAxiosError } from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import {
  type PostmarketReportResponsePayload,
  postPostmarketReport,
} from '../../api/postmarketRiskScore';

function formatSummaryLoadError(e: unknown): string {
  if (isAxiosError(e)) {
    const d = e.response?.data as { detail?: unknown } | undefined;
    if (typeof d?.detail === 'string' && d.detail.trim()) return d.detail;
    if (e.response?.status === 403) return 'This feature requires a Pro plan.';
    if (e.response?.status === 404) return 'Project not found or access denied.';
    if (e.message) return e.message;
  }
  if (e instanceof Error && e.message) return e.message;
  return 'Could not load summary';
}

export interface PostMarketReportSummaryCardProps {
  projectId: string;
  deviceType?: string;
  className?: string;
  autoRefresh?: boolean;
}

export const PostMarketReportSummaryCard: React.FC<PostMarketReportSummaryCardProps> = ({
  projectId,
  deviceType,
  className = '',
  autoRefresh = true,
}) => {
  const [data, setData] = useState<PostmarketReportResponsePayload | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (!autoRefresh || !projectId) return;
    let cancelled = false;
    (async () => {
      setLoading(true);
      setErr(null);
      try {
        const r = await postPostmarketReport({
          project_id: projectId,
          device_type: deviceType?.trim() || undefined,
          include_missing_risks: false,
          include_trend_summary: true,
          include_outcome_breakdown: true,
          max_failure_modes: 5,
          max_phrase_rows: 5,
        });
        if (!cancelled) setData(r);
      } catch (e: unknown) {
        if (!cancelled) {
          setData(null);
          setErr(formatSummaryLoadError(e));
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [projectId, deviceType, autoRefresh]);

  const maxO = data?.outcome_breakdown?.length
    ? Math.max(...data.outcome_breakdown.map((o) => o.count), 1)
    : 1;

  const modeResolved =
    data == null
      ? 'draft'
      : data.report_mode ??
        (data.evidence_summary.total_maude_records_analyzed > 0 ? 'populated' : 'draft');

  return (
    <Card className={className}>
      <CardHeader className="py-4">
        <CardTitle className="text-base">Post-market snapshot</CardTitle>
        {data && (
          <p className="text-xs text-text-secondary font-normal mt-1">
            Refreshed {new Date(data.generated_at).toLocaleString()}
          </p>
        )}
      </CardHeader>
      <CardContent className="pt-0">
        {loading && <p className="text-sm text-text-secondary">Loading…</p>}
        {err && !loading && <p className="text-sm text-red-700">{err}</p>}
        {data && !loading && (
          <div className="space-y-4 text-sm">
            <p className="text-xs text-text-secondary">
              Mode:{' '}
              <span className="font-medium text-text-primary">
                {modeResolved === 'populated' ? 'Data-backed' : 'Draft'}
              </span>
              {data.summary?.pms_signal_records_in_scope != null && data.summary.pms_signal_records_in_scope > 0 && (
                <>
                  {' · '}
                  PMS signals:{' '}
                  <span className="font-medium text-text-primary">{data.summary.pms_signal_records_in_scope}</span>
                </>
              )}
            </p>
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-md border border-border p-3 bg-surface-secondary/30">
                <p className="text-xs text-text-secondary">Analyzed (NLP-linked)</p>
                <p className="text-xl font-semibold tabular-nums text-text-primary">
                  {data.summary?.maude_nlp_linked_records_reviewed ?? data.evidence_summary.total_maude_records_analyzed}
                </p>
              </div>
              <div className="rounded-md border border-border p-3 bg-surface-secondary/30">
                <p className="text-xs text-text-secondary">Device filter</p>
                <p className="text-text-primary font-medium truncate" title={data.filter_summary.device_type_used}>
                  {data.filter_summary.device_type_used}
                </p>
              </div>
            </div>
            {data.top_failure_modes.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-text-secondary mb-2">Top failure modes</p>
                <ul className="space-y-1">
                  {data.top_failure_modes.slice(0, 3).map((f) => (
                    <li key={f.normalized_failure_mode} className="flex justify-between gap-2 text-text-primary">
                      <span className="truncate">{f.normalized_failure_mode}</span>
                      <span className="tabular-nums text-text-secondary shrink-0">{f.supporting_event_count}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {data.outcome_breakdown.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-text-secondary mb-2">Outcomes</p>
                <div className="space-y-1">
                  {data.outcome_breakdown.map((o) => (
                    <div key={o.outcome} className="flex items-center gap-2">
                      <span className="w-24 capitalize text-xs text-text-secondary shrink-0">{o.outcome}</span>
                      <div className="flex-1 h-2 rounded-full bg-surface-secondary overflow-hidden">
                        <div
                          className="h-full bg-text-primary/60 rounded-full"
                          style={{ width: `${maxO ? Math.min(100, (o.count / maxO) * 100) : 0}%` }}
                        />
                      </div>
                      <span className="text-xs tabular-nums text-text-secondary w-10 text-right">{o.count}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {data.trend_summary && data.trend_summary.periods.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-text-secondary mb-1">Trend ({data.trend_summary.granularity})</p>
                <p className="text-xs text-text-secondary line-clamp-2">{data.trend_summary.qualitative_summary}</p>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PostMarketReportSummaryCard;
