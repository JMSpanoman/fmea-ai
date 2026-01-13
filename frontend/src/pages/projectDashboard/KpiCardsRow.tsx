import React from 'react';

export function KpiCard({
  title,
  value,
  subtitle,
  footer,
}: {
  title: string;
  value: string;
  subtitle?: string;
  footer?: React.ReactNode;
}) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="text-xs font-semibold text-gray-700 uppercase tracking-wider">{title}</div>
      <div className="mt-2 text-2xl font-bold text-gray-900">{value}</div>
      {subtitle ? <div className="mt-1 text-sm text-gray-600">{subtitle}</div> : null}
      {footer ? <div className="mt-3">{footer}</div> : null}
    </div>
  );
}

export function MiniBreakdown({
  items,
}: {
  items: Array<{ label: string; value: string }>;
}) {
  return (
    <div className="mt-2 grid grid-cols-2 gap-2">
      {items.map((i) => (
        <div key={i.label} className="rounded-md bg-gray-50 border border-gray-100 px-2 py-1">
          <div className="text-[11px] text-gray-600">{i.label}</div>
          <div className="text-xs font-semibold text-gray-900">{i.value}</div>
        </div>
      ))}
    </div>
  );
}

export function KpiCardsRow({
  children,
}: {
  children: React.ReactNode;
}) {
  return <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">{children}</div>;
}

