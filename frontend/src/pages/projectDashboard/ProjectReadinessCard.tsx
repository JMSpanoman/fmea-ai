import React from 'react';
import type { LoadAvailability, ProjectReadiness } from './model';

function ReadinessRing({ pct }: { pct: number }) {
  const size = 108;
  const stroke = 10;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.max(0, Math.min(100, pct));
  const offset = circumference - (clamped / 100) * circumference;

  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      role="img"
      aria-label={`Overall readiness ${clamped} percent`}
      className="flex-shrink-0"
    >
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="#e6edf2"
        strokeWidth={stroke}
      />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="var(--sr-color-healthy)"
        strokeWidth={stroke}
        strokeLinecap="round"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
      />
      <text
        x="50%"
        y="50%"
        textAnchor="middle"
        dominantBaseline="central"
        className="fill-navy"
        fontSize="22"
        fontWeight="700"
      >
        {clamped}%
      </text>
    </svg>
  );
}

export function ProjectReadinessCard({
  readiness,
  availability,
}: {
  readiness: ProjectReadiness | null;
  availability: LoadAvailability;
}) {
  return (
    <section className="sr-card p-5 h-full" aria-labelledby="project-readiness-heading">
      <div className="flex items-center justify-between gap-3">
        <h2 id="project-readiness-heading" className="text-base font-semibold text-navy">
          Project readiness
        </h2>
        {availability === 'ready' && readiness ? (
          <span className="text-sm font-semibold text-navy">{readiness.overallPct}%</span>
        ) : null}
      </div>

      {availability === 'loading' ? (
        <p className="mt-4 text-sm text-muted">Loading readiness…</p>
      ) : availability === 'error' ? (
        <p className="mt-4 text-sm text-red-700">Readiness is unavailable.</p>
      ) : availability === 'empty' || !readiness ? (
        <p className="mt-4 text-sm text-muted">No documents available to evaluate readiness.</p>
      ) : (
        <div className="mt-4 flex items-center gap-5">
          <ReadinessRing pct={readiness.overallPct} />
          <div className="flex-1 min-w-0 space-y-3">
            {readiness.breakdown.map((item) => (
              <div key={item.name}>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-navy">{item.name}</span>
                  <span className="text-muted tabular-nums">{item.pct}%</span>
                </div>
                <div
                  className="mt-1 h-1.5 w-full rounded-full bg-gray-100 overflow-hidden"
                  role="progressbar"
                  aria-valuenow={item.pct}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label={`${item.name} ${item.pct} percent`}
                >
                  <div
                    className="h-full rounded-full bg-healthy"
                    style={{ width: `${Math.max(0, Math.min(100, item.pct))}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
