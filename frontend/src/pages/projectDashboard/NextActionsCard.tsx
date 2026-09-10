import React from 'react';
import { selectPrimaryRecommendedAction } from './model';
import { RecommendedActionCard } from './RecommendedActionCard';
import type { Document } from '../../types';

/** Back-compat wrapper around the shared recommended-action selector. */
export function NextActionsCard({
  projectId,
  documents,
}: {
  projectId: string;
  documents: Document[];
}) {
  const { primary, remaining } = selectPrimaryRecommendedAction({ projectId, documents });
  return <RecommendedActionCard primary={primary} remaining={remaining} />;
}
