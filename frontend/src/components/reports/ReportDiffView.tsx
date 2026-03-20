import React, { useMemo } from 'react';
import { parseFmeaTableFromHtml } from '../../utils/parseFmeaTableFromHtml';
import { computeFmeaReportDiff, summarizeFmeaDiff, type FmeaDiffFieldKey, type FmeaDiffRow } from './fmeaReportDiff';
import { DiffCell } from './DiffCell';
import type { DiffTone } from './fmeaReportDiff';
import { reportUi } from './reportUi';

export type ReportDiffViewProps = {
  leftHtml: string;
  rightHtml: string;
  leftLabel: string;
  rightLabel: string;
  hideUnchanged?: boolean;
};

const FIELD_LABELS: Record<FmeaDiffFieldKey, string> = {
  s: 'S',
  o: 'O',
  d: 'D',
  rpn: 'RPN',
  mitigation: 'Mitigation',
  actionTaken: 'Action taken',
  revisedS: 'Rev. S',
  revisedO: 'Rev. O',
  revisedD: 'Rev. D',
  revisedRpn: 'Rev. RPN',
};

function statusBadge(status: FmeaDiffRow['status']): { text: string; className: string } {
  switch (status) {
    case 'added':
      return { text: 'Added', className: 'bg-emerald-50 text-emerald-900 border-emerald-200' };
    case 'removed':
      return { text: 'Removed', className: 'bg-rose-50 text-rose-900 border-rose-200' };
    case 'modified':
      return { text: 'Modified', className: 'bg-amber-50 text-amber-900 border-amber-200' };
    default:
      return { text: '—', className: 'bg-neutral-100 text-neutral-600 border-neutral-200' };
  }
}

function rowTone(status: FmeaDiffRow['status']): DiffTone {
  if (status === 'added') return 'added';
  if (status === 'removed') return 'removed';
  return 'neutral';
}

function pickMetric(row: FmeaDiffRow['left'], key: FmeaDiffFieldKey): number {
  if (!row) return 0;
  switch (key) {
    case 's':
      return row.s;
    case 'o':
      return row.o;
    case 'd':
      return row.d;
    case 'rpn':
      return row.rpn;
    case 'revisedS':
      return row.revisedS ?? row.s;
    case 'revisedO':
      return row.revisedO ?? row.o;
    case 'revisedD':
      return row.revisedD ?? row.d;
    case 'revisedRpn':
      return row.revisedRpn ?? row.residualRpn ?? row.rpn;
    default:
      return 0;
  }
}

function renderMetricCell(row: FmeaDiffRow, key: FmeaDiffFieldKey, format: (n: number) => string) {
  const fd = row.fields[key];
  const L = row.left;
  const R = row.right;

  if (row.status === 'removed' && L) {
    return (
      <DiffCell tone="removed" title="Only in baseline">
        {format(pickMetric(L, key))}
      </DiffCell>
    );
  }
  if (row.status === 'added' && R) {
    return (
      <DiffCell tone="added" title="Only in target">
        {format(pickMetric(R, key))}
      </DiffCell>
    );
  }

  if (!fd || fd.tone === 'neutral') {
    const v = R ?? L;
    if (!v) return <span className="text-neutral-400">—</span>;
    const n = pickMetric(v, key);
    return (
      <DiffCell tone="neutral" longText={false}>
        {format(n)}
      </DiffCell>
    );
  }

  return (
    <DiffCell tone={fd.tone} title={`${FIELD_LABELS[key]}: ${fd.before} → ${fd.after}`} secondary={`was ${fd.before}`}>
      {fd.after}
    </DiffCell>
  );
}

function renderTextCell(row: FmeaDiffRow, key: 'mitigation' | 'actionTaken') {
  const fd = row.fields[key];
  const L = row.left;
  const R = row.right;

  if (row.status === 'removed' && L) {
    const t = key === 'mitigation' ? L.mitigation : L.actionTaken ?? '';
    return (
      <DiffCell tone="removed" longText title="Baseline only">
        {t || '—'}
      </DiffCell>
    );
  }
  if (row.status === 'added' && R) {
    const t = key === 'mitigation' ? R.mitigation : R.actionTaken ?? '';
    return (
      <DiffCell tone="added" longText title="Target only">
        {t || '—'}
      </DiffCell>
    );
  }

  if (!fd || fd.tone === 'neutral') {
    const v = R ?? L;
    if (!v) return <span className="text-neutral-400">—</span>;
    const t = key === 'mitigation' ? v.mitigation : v.actionTaken ?? '';
    return (
      <DiffCell tone="neutral" longText>
        {t || '—'}
      </DiffCell>
    );
  }

  return (
    <DiffCell tone={fd.tone} longText title={`Updated ${FIELD_LABELS[key]}`} secondary={`Before: ${fd.before || '—'}`}>
      {fd.after || '—'}
    </DiffCell>
  );
}

export function ReportDiffView({ leftHtml, rightHtml, leftLabel, rightLabel, hideUnchanged = false }: ReportDiffViewProps) {
  const { diffRows, summary, hasExtendedCols, emptyLeft, emptyRight } = useMemo(() => {
    const leftRows = parseFmeaTableFromHtml(leftHtml);
    const rightRows = parseFmeaTableFromHtml(rightHtml);
    const raw = computeFmeaReportDiff(leftRows, rightRows);
    const filtered = hideUnchanged ? raw.filter((r) => r.status !== 'unchanged') : raw;
    const summaryInner = summarizeFmeaDiff(raw);
    const hasExtendedColsInner =
      leftRows.some((r) => r.cellCount > 11) || rightRows.some((r) => r.cellCount > 11);
    return {
      diffRows: filtered,
      summary: summaryInner,
      hasExtendedCols: hasExtendedColsInner,
      emptyLeft: leftRows.length === 0,
      emptyRight: rightRows.length === 0,
    };
  }, [leftHtml, rightHtml, hideUnchanged]);

  const thSticky =
    'sticky top-0 z-20 border-b border-neutral-300 bg-neutral-100 px-2 py-2 text-left text-[11px] font-semibold uppercase tracking-wide text-neutral-600 shadow-[0_1px_0_0_#d4d4d4] print:static print:shadow-none';
  const thFirst = `${thSticky} left-0 z-30 min-w-[3.5rem] print:static`;

  return (
    <div className={reportUi.stackSection}>
      <div className={`${reportUi.panelMuted} p-4 print:break-inside-avoid`}>
        <div className="flex flex-col gap-4 sm:flex-row sm:flex-wrap sm:items-start sm:justify-between">
          <div className="min-w-0">
            <h4 className={reportUi.titleSm}>Comparison summary</h4>
            <p className={`mt-1 ${reportUi.captionLead}`}>
              Baseline: <span className="font-medium text-neutral-800">{leftLabel}</span>
              <span className="mx-1 text-neutral-400">→</span>
              Target: <span className="font-medium text-neutral-800">{rightLabel}</span>
            </p>
          </div>
          <dl className="grid grid-cols-2 gap-x-6 gap-y-1 text-xs sm:grid-cols-4">
            <div>
              <dt className="text-neutral-500">Added rows</dt>
              <dd className="font-semibold text-emerald-800">{summary.added}</dd>
            </div>
            <div>
              <dt className="text-neutral-500">Removed rows</dt>
              <dd className="font-semibold text-rose-800">{summary.removed}</dd>
            </div>
            <div>
              <dt className="text-neutral-500">Modified rows</dt>
              <dd className="font-semibold text-amber-900">{summary.modified}</dd>
            </div>
            <div>
              <dt className="text-neutral-500">Unchanged</dt>
              <dd className="font-semibold text-neutral-800">{summary.unchanged}</dd>
            </div>
          </dl>
        </div>
        <div className={`mt-3 flex flex-wrap gap-x-4 gap-y-2 border-t border-neutral-200 pt-3 ${reportUi.caption} text-neutral-600`}>
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-sm bg-emerald-200/90 ring-1 ring-emerald-300/60" />
            Lower risk / added
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-sm bg-rose-200/90 ring-1 ring-rose-300/60" />
            Higher risk / removed
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-sm bg-amber-200/90 ring-1 ring-amber-300/60" />
            Text or other change
          </span>
        </div>
      </div>

      {(emptyLeft || emptyRight) && (
        <div className="rounded-lg border border-amber-200/90 bg-amber-50/80 px-3 py-2 text-xs text-amber-950 print:break-inside-avoid">
          {emptyLeft && emptyRight
            ? 'No FMEA table rows found in either snapshot. Ensure both versions contain generated FMEA HTML.'
            : emptyLeft
              ? 'Baseline snapshot has no parseable FMEA rows.'
              : 'Target snapshot has no parseable FMEA rows.'}
        </div>
      )}

      <div className="min-w-0 overflow-x-auto rounded-lg border border-neutral-200 bg-white print:overflow-visible print:break-inside-avoid">
        <table className="min-w-[1100px] w-full border-collapse text-left text-xs">
          <thead className="print:table-header-group">
            <tr>
              <th className={thFirst}>Δ</th>
              <th className={thSticky}>ID</th>
              <th className={thSticky}>Component</th>
              <th className={`${thSticky} min-w-[120px]`}>Failure mode</th>
              <th className={`${thSticky} min-w-[100px]`}>Effect</th>
              <th className={thSticky}>S</th>
              <th className={thSticky}>O</th>
              <th className={thSticky}>D</th>
              <th className={thSticky}>RPN</th>
              <th className={`${thSticky} min-w-[200px]`}>Mitigation</th>
              {hasExtendedCols ? (
                <>
                  <th className={`${thSticky} min-w-[160px]`}>Action taken</th>
                  <th className={thSticky}>Rev. RPN</th>
                </>
              ) : null}
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100 bg-white">
            {diffRows.map((row) => {
              const badge = statusBadge(row.status);
              const display = row.right ?? row.left;
              const rt = rowTone(row.status);
              return (
                <tr key={row.matchKey} className="group align-top hover:bg-neutral-50/80 print:hover:bg-transparent">
                  <td className="sticky left-0 z-10 bg-white px-2 py-2 shadow-[2px_0_4px_-2px_rgba(0,0,0,0.08)] group-hover:bg-neutral-50 print:static print:shadow-none">
                    <span className={`inline-block rounded border px-1.5 py-0.5 text-[10px] font-semibold ${badge.className}`}>
                      {badge.text}
                    </span>
                  </td>
                  <td className="px-2 py-2 font-mono text-[11px] text-neutral-700">{display?.rowId || '—'}</td>
                  <td className="px-2 py-2">
                    <DiffCell tone={row.status === 'removed' || row.status === 'added' ? rt : 'neutral'} longText>
                      {display?.component || '—'}
                    </DiffCell>
                  </td>
                  <td className="px-2 py-2">
                    <DiffCell tone="neutral" longText>
                      {display?.failureMode || '—'}
                    </DiffCell>
                  </td>
                  <td className="px-2 py-2">
                    <DiffCell tone="neutral" longText>
                      {display?.effect || '—'}
                    </DiffCell>
                  </td>
                  <td className="px-2 py-2">{renderMetricCell(row, 's', String)}</td>
                  <td className="px-2 py-2">{renderMetricCell(row, 'o', String)}</td>
                  <td className="px-2 py-2">{renderMetricCell(row, 'd', String)}</td>
                  <td className="px-2 py-2">{renderMetricCell(row, 'rpn', String)}</td>
                  <td className="px-2 py-2">{renderTextCell(row, 'mitigation')}</td>
                  {hasExtendedCols ? (
                    <>
                      <td className="px-2 py-2">{renderTextCell(row, 'actionTaken')}</td>
                      <td className="px-2 py-2">{renderMetricCell(row, 'revisedRpn', String)}</td>
                    </>
                  ) : null}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <p className={`${reportUi.captionLead} print:break-inside-avoid`}>
        Row matching uses display ID (FMEA-##) when present; otherwise component + failure mode + effect + cause. For
        regulatory audit trails, prefer backend snapshots keyed by stable risk-item IDs — see{' '}
        <code className={reportUi.inlineCode}>parseFmeaTableFromHtml.ts</code> and{' '}
        <code className={reportUi.inlineCode}>fmeaReportDiff.ts</code> integration notes.
      </p>
    </div>
  );
}
