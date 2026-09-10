import React from 'react';
import type { ProjectProgressStage } from './model';

export function ProjectProgressPath({
  stages,
}: {
  stages: ProjectProgressStage[];
}) {
  return (
    <ol
      className="flex items-start justify-between gap-2 overflow-x-auto pb-1"
      aria-label="Project progress"
    >
      {stages.map((stage, index) => {
        const complete = stage.state === 'complete';
        const current = stage.state === 'current';
        return (
          <li
            key={stage.id}
            className="flex-1 min-w-[4.75rem] sm:min-w-[5.25rem] flex flex-col items-center text-center relative"
          >
            {index < stages.length - 1 && (
              <span
                aria-hidden="true"
                className={`absolute top-4 left-[calc(50%+1.1rem)] right-[calc(-50%+1.1rem)] h-px ${
                  complete ? 'bg-healthy' : 'bg-gray-200'
                }`}
              />
            )}
            <span
              className={`relative z-[1] inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-semibold border ${
                complete
                  ? 'bg-healthy text-white border-healthy'
                  : current
                    ? 'bg-white text-brand border-brand ring-2 ring-brand/20'
                    : 'bg-gray-100 text-muted border-gray-200'
              }`}
              aria-current={current ? 'step' : undefined}
            >
              {complete ? (
                <svg className="w-4 h-4" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                  <path
                    d="M5 10.5L8.2 13.7L15 6.5"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              ) : (
                index + 1
              )}
            </span>
            <span
              className={`mt-2 text-[11px] sm:text-xs leading-tight whitespace-nowrap ${
                complete || current ? 'text-navy font-medium' : 'text-muted'
              }`}
            >
              {stage.label}
              <span className="sr-only">
                {complete ? ' (complete)' : current ? ' (current)' : ' (upcoming)'}
              </span>
            </span>
          </li>
        );
      })}
    </ol>
  );
}
