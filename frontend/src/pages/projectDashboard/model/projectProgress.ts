import type { Document } from '../../../types';
import { inferDocStatus } from '../DocumentRow';
import { percentApproved, READINESS_CATEGORIES, documentsByType, statusesForTypes } from './types';
import type { ProjectProgressStage, ProjectProgressStageId } from './types';

export const PROJECT_PROGRESS_STAGE_DEFS: Array<{ id: ProjectProgressStageId; label: string }> = [
  { id: 'setup', label: 'Setup' },
  { id: 'documents', label: 'Documents' },
  { id: 'risk_analysis', label: 'Risk analysis' },
  { id: 'traceability', label: 'Traceability' },
  { id: 'review_export', label: 'Review & export' },
];

export interface ProjectProgressInput {
  /**
   * True when intended use is present and the project has at least one component.
   * Same rule as the existing Mission Control setup check.
   * If setup has not been evaluated, pass false (do not fabricate completion).
   */
  setupComplete: boolean;
  documents: Document[] | null | undefined;
}

function categoryPct(
  name: (typeof READINESS_CATEGORIES)[number]['name'],
  documents: Document[] | null | undefined
): number {
  const def = READINESS_CATEGORIES.find((category) => category.name === name);
  if (!def) return 0;
  return percentApproved(statusesForTypes(def.types, documentsByType(documents)));
}

function overallPct(documents: Document[] | null | undefined): number {
  const scores = READINESS_CATEGORIES.map((category) =>
    percentApproved(statusesForTypes(category.types, documentsByType(documents)))
  );
  if (!scores.length) return 0;
  return Math.round(scores.reduce((sum, value) => sum + value, 0) / scores.length);
}

/**
 * Presentation-layer workflow mapping (not a backend workflow engine):
 *
 * 1. Setup — complete when intended use + ≥1 component (existing setup rule).
 * 2. Documents — complete when Design Controls category is fully approved.
 * 3. Risk analysis — complete when Risk Management category is fully approved.
 * 4. Traceability — complete when the traceability matrix document is approved.
 * 5. Review & export — complete when overall category readiness is 100%.
 *
 * Stages are sequential: a later stage is never marked complete if an earlier
 * stage is incomplete. Unavailable setup data must be passed as setupComplete=false.
 */
export function selectProjectProgress(input: ProjectProgressInput): ProjectProgressStage[] {
  const documents = input.documents || [];
  const tm = documents.find((doc) => doc.type === 'traceability_matrix');
  const tmApproved = tm
    ? inferDocStatus({ status: tm.status, content: tm.content }) === 'approved'
    : false;

  const completion: Record<ProjectProgressStageId, boolean> = {
    setup: Boolean(input.setupComplete),
    documents: categoryPct('Design Controls', documents) === 100,
    risk_analysis: categoryPct('Risk Management', documents) === 100,
    traceability: tmApproved,
    review_export: overallPct(documents) === 100,
  };

  let blocked = false;
  const sequential: Record<ProjectProgressStageId, boolean> = {
    setup: false,
    documents: false,
    risk_analysis: false,
    traceability: false,
    review_export: false,
  };
  for (const def of PROJECT_PROGRESS_STAGE_DEFS) {
    if (blocked) {
      sequential[def.id] = false;
      continue;
    }
    sequential[def.id] = completion[def.id];
    if (!completion[def.id]) blocked = true;
  }

  const firstIncomplete = PROJECT_PROGRESS_STAGE_DEFS.find((def) => !sequential[def.id])?.id;

  return PROJECT_PROGRESS_STAGE_DEFS.map((def) => {
    const complete = sequential[def.id];
    let state: ProjectProgressStage['state'] = 'upcoming';
    if (complete) state = 'complete';
    else if (def.id === firstIncomplete) state = 'current';
    return { ...def, complete, state };
  });
}
