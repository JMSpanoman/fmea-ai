import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { RecommendedAction } from './model';

export function RecommendedActionCard({
  primary,
  remaining,
  loading = false,
}: {
  primary: RecommendedAction | null;
  remaining: RecommendedAction[];
  loading?: boolean;
}) {
  const navigate = useNavigate();
  const [showRemaining, setShowRemaining] = useState(false);

  return (
    <section
      id="next-recommended-action"
      aria-labelledby="next-recommended-action-heading"
      className="sr-card p-5 sm:p-6 bg-attention-muted border-attention/20"
    >
      <div className="flex items-start gap-3">
        <span
          className="mt-0.5 inline-flex items-center justify-center w-8 h-8 rounded-full bg-white text-attention border border-attention/30 flex-shrink-0"
          aria-hidden="true"
        >
          <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
            <path d="M10.9 3.2 17 14.3A1.8 1.8 0 0 1 15.4 17H4.6A1.8 1.8 0 0 1 3 14.3L9.1 3.2a1.8 1.8 0 0 1 1.8 0z" />
            <path d="M10 7.5v4" stroke="white" strokeWidth="1.8" strokeLinecap="round" fill="none" />
            <circle cx="10" cy="13.4" r="0.8" fill="white" />
          </svg>
        </span>
        <div className="min-w-0 flex-1">
          <p
            id="next-recommended-action-heading"
            className="text-[0.7rem] font-semibold tracking-[0.12em] uppercase text-attention"
          >
            Next recommended action
          </p>
          {loading ? (
            <p className="mt-2 text-sm text-muted">Loading recommended action…</p>
          ) : primary ? (
            <>
              <h2 className="mt-1 text-lg sm:text-xl font-semibold text-navy">{primary.title}</h2>
              <p className="mt-1 text-sm text-muted">{primary.reason}</p>
            </>
          ) : (
            <p className="mt-2 text-sm text-navy">No urgent actions detected.</p>
          )}
        </div>
      </div>
      {!loading && primary ? (
        <button
          type="button"
          className="mt-4 w-full inline-flex items-center justify-center min-h-control-lg px-4 rounded-control bg-brand text-white text-sm font-semibold hover:bg-brand-hover"
          onClick={() => navigate(primary.href)}
        >
          Continue
        </button>
      ) : null}

      {!loading && remaining.length > 0 && (
        <div className="mt-4">
          <button
            type="button"
            className="text-sm text-muted hover:text-navy underline-offset-2 hover:underline"
            aria-expanded={showRemaining}
            onClick={() => setShowRemaining((value) => !value)}
          >
            {showRemaining ? 'Hide other actions' : `View ${remaining.length} other action${remaining.length === 1 ? '' : 's'}`}
          </button>
          {showRemaining && (
            <ul className="mt-3 divide-y divide-attention/15">
              {remaining.map((action) => (
                <li key={action.id} className="py-3 flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-navy">{action.title}</p>
                    <p className="text-sm text-muted mt-0.5">{action.reason}</p>
                  </div>
                  <button
                    type="button"
                    className="flex-shrink-0 text-sm font-medium text-brand hover:underline min-h-control"
                    onClick={() => navigate(action.href)}
                  >
                    {action.cta}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </section>
  );
}
