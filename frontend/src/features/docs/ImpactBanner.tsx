import React from 'react';

export function ImpactBanner({
  title,
  message,
  actions,
}: {
  title: string;
  message: string;
  actions?: React.ReactNode;
}) {
  return (
    <div className="border border-amber-300 bg-amber-50 rounded-lg p-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-sm font-semibold text-amber-900">{title}</div>
          <div className="text-sm text-amber-900/90 mt-1">{message}</div>
        </div>
        {actions ? <div className="flex-shrink-0">{actions}</div> : null}
      </div>
    </div>
  );
}

