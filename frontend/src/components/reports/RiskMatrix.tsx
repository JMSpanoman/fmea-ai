import React, { useMemo } from 'react';
import { reportUi } from './reportUi';

export type RiskMatrixProps = {
  grid: number[][];
  empty?: boolean;
  docTypeLabel?: string;
};

const BUCKET_LABELS = ['1–2', '3–4', '5–6', '7–8', '9–10'];

export function RiskMatrix({ grid, empty, docTypeLabel }: RiskMatrixProps) {
  const max = useMemo(() => Math.max(1, ...grid.flat()), [grid]);

  if (empty || !grid.length) {
    return (
      <div className={`${reportUi.emptyDashed} p-4 sm:p-5 print:break-inside-avoid`}>
        <p className={reportUi.titleSm}>Risk concentration matrix</p>
        <p className={`mt-2 ${reportUi.captionLead}`}>
          {docTypeLabel ? (
            <>
              No Severity × Occurrence data parsed for <span className="font-medium text-neutral-800">{docTypeLabel}</span>{' '}
              in this preview.{' '}
            </>
          ) : null}
          When FMEA rows include <span className="font-mono text-[11px]">S</span> and{' '}
          <span className="font-mono text-[11px]">O</span> columns, this matrix shows where failure modes cluster.
        </p>
        <div className="mt-4 grid grid-cols-6 gap-1 text-[10px] font-medium uppercase tracking-wider text-neutral-500">
          <div />
          {BUCKET_LABELS.map((l) => (
            <div key={l} className="text-center">
              O {l}
            </div>
          ))}
        </div>
        {Array.from({ length: 5 }).map((_, ri) => (
          <div key={ri} className="mt-1 grid grid-cols-6 gap-1">
            <div className="flex items-center justify-end pr-1 text-[10px] font-medium uppercase tracking-wider text-neutral-500">
              S {BUCKET_LABELS[4 - ri]}
            </div>
            {Array.from({ length: 5 }).map((_, ci) => (
              <div
                key={ci}
                className="flex aspect-square min-h-[2rem] items-center justify-center rounded border border-neutral-200 bg-neutral-50 text-[10px] text-neutral-400"
              >
                —
              </div>
            ))}
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className={`${reportUi.card} p-4 print:break-inside-avoid`}>
      <p className={reportUi.titleSm}>Severity × Occurrence (bucketed)</p>
      <p className={`mt-1 ${reportUi.captionLead}`}>
        Cell counts = FMEA rows in each S/O band. Does not replace formal risk matrix acceptability — see RAC / project
        policy.
      </p>
      <div className="mt-4 overflow-x-auto">
        <div className="inline-block min-w-full">
          <div className="grid grid-cols-6 gap-1 text-[10px] font-semibold uppercase tracking-wider text-neutral-600">
            <div />
            {BUCKET_LABELS.map((l) => (
              <div key={l} className="text-center">
                O {l}
              </div>
            ))}
          </div>
          {Array.from({ length: 5 }).map((_, ri) => {
            const severityBucket = 4 - ri;
            const row = grid[severityBucket] ?? [0, 0, 0, 0, 0];
            return (
              <div key={ri} className="mt-1 grid grid-cols-6 gap-1">
                <div className="flex items-center justify-end pr-1 text-[10px] font-semibold uppercase tracking-wider text-neutral-600">
                  S {BUCKET_LABELS[severityBucket]}
                </div>
                {row.map((count, ci) => {
                  const intensity = count <= 0 ? 0 : Math.min(1, 0.25 + (count / max) * 0.75);
                  const bg =
                    count === 0
                      ? 'bg-neutral-50 border-neutral-200 text-neutral-400'
                      : intensity > 0.65
                        ? 'bg-red-100/90 border-red-200 text-red-900'
                        : intensity > 0.35
                          ? 'bg-amber-50 border-amber-200 text-amber-900'
                          : 'bg-emerald-50 border-emerald-200 text-emerald-900';
                  return (
                    <div
                      key={ci}
                      className={`flex aspect-square min-h-[2rem] min-w-[2rem] items-center justify-center rounded border text-xs font-semibold tabular-nums ${bg}`}
                      title={`${count} row(s)`}
                    >
                      {count || '·'}
                    </div>
                  );
                })}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export function bucket10(n: number): number {
  if (!Number.isFinite(n)) return 0;
  const v = Math.max(1, Math.min(10, Math.round(n)));
  return Math.min(4, Math.floor((v - 1) / 2));
}

export function buildFmeaSoGrid(rows: { s: number; o: number }[]): number[][] {
  const g = Array.from({ length: 5 }, () => Array.from({ length: 5 }, () => 0));
  for (const { s, o } of rows) {
    const si = bucket10(s);
    const oi = bucket10(o);
    g[si][oi] += 1;
  }
  return g;
}
