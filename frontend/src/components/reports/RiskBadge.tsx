import React from 'react';

export type RiskLevel = 'high' | 'medium' | 'low' | 'neutral';

export function rpnToLevel(rpn: number): RiskLevel {
  if (!Number.isFinite(rpn) || rpn <= 0) return 'neutral';
  if (rpn >= 100) return 'high';
  if (rpn >= 50) return 'medium';
  return 'low';
}

/** Subtle QMS-style badge — low contrast fills, neutral-friendly for print. */
export function RiskBadge({
  level,
  label,
  compact = false,
}: {
  level: RiskLevel;
  label: string;
  compact?: boolean;
}) {
  const cls =
    level === 'high'
      ? 'bg-red-50/90 text-red-800 border-red-100'
      : level === 'medium'
        ? 'bg-amber-50/90 text-amber-900 border-amber-100'
        : level === 'low'
          ? 'bg-emerald-50/90 text-emerald-800 border-emerald-100'
          : 'bg-neutral-100 text-neutral-700 border-neutral-200';

  return (
    <span
      className={`inline-flex items-center rounded border font-medium ${compact ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-xs'} ${cls}`}
      title={label}
    >
      {label}
    </span>
  );
}

export function RpnRiskBadge({ rpn, labelPrefix = 'RPN' }: { rpn: number; labelPrefix?: string }) {
  const level = rpnToLevel(rpn);
  const label = `${labelPrefix} ${Number.isFinite(rpn) ? rpn : '—'}`;
  return <RiskBadge level={level} label={label} compact />;
}
