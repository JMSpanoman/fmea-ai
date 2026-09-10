import React from 'react';

export function SmartRiskLogo({
  compact = false,
  className = '',
}: {
  compact?: boolean;
  className?: string;
}) {
  return (
    <span className={`inline-flex items-center gap-2 min-w-0 ${className}`}>
      <svg
        width="28"
        height="28"
        viewBox="0 0 28 28"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
        className="flex-shrink-0"
      >
        <rect x="4" y="14" width="5" height="10" rx="1.5" fill="currentColor" />
        <rect x="11.5" y="8" width="5" height="16" rx="1.5" fill="currentColor" />
        <rect x="19" y="4" width="5" height="20" rx="1.5" fill="currentColor" />
      </svg>
      {!compact && (
        <span className="text-[1.15rem] font-semibold tracking-tight text-navy truncate">
          SmartRisk
        </span>
      )}
    </span>
  );
}
