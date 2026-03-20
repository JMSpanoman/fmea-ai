import React from 'react';
import type { DiffTone } from './fmeaReportDiff';

const toneClasses: Record<DiffTone, string> = {
  neutral: 'bg-white text-neutral-800 border-neutral-200',
  added: 'bg-emerald-50/70 text-emerald-900 border-emerald-200/80',
  removed: 'bg-rose-50/70 text-rose-900 border-rose-200/80',
  improved: 'bg-emerald-50/60 text-emerald-900 border-emerald-200/70',
  worsened: 'bg-rose-50/60 text-rose-900 border-rose-200/70',
  changed: 'bg-amber-50/70 text-amber-950 border-amber-200/80',
};

export type DiffCellProps = {
  tone: DiffTone;
  children: React.ReactNode;
  secondary?: React.ReactNode;
  className?: string;
  longText?: boolean;
  title?: string;
};

export function DiffCell({ tone, children, secondary, className = '', longText, title }: DiffCellProps) {
  const base =
    'rounded-md border px-2 py-1.5 text-xs leading-snug ' +
    (longText ? 'max-h-28 overflow-y-auto whitespace-pre-wrap break-words ' : '') +
    toneClasses[tone];

  return (
    <div className={`${base} ${className}`.trim()} title={title}>
      <div className="font-medium tabular-nums">{children}</div>
      {secondary ? (
        <div className="mt-0.5 border-t border-neutral-200/90 pt-0.5 text-[11px] text-neutral-600">{secondary}</div>
      ) : null}
    </div>
  );
}
