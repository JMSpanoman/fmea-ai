import type { Document } from '../../../types';
import { inferDocStatus } from '../DocumentRow';
import {
  documentsByType,
  percentApproved,
  READINESS_CATEGORIES,
  statusesForTypes,
  type ProjectReadiness,
  type RiskStatusCounts,
} from './types';

/**
 * Category readiness: share of configured document types that are approved.
 * Overall readiness is the unweighted mean of category percentages.
 * Empty/unavailable document lists must not be coerced by callers into a loaded 0%.
 */
export function selectProjectReadiness(documents: Document[] | null | undefined): ProjectReadiness {
  const byType = documentsByType(documents);
  const breakdown = READINESS_CATEGORIES.map((category) => ({
    name: category.name,
    pct: percentApproved(statusesForTypes(category.types, byType)),
  }));
  const overallPct = breakdown.length
    ? Math.round(breakdown.reduce((sum, item) => sum + item.pct, 0) / breakdown.length)
    : 0;
  return { overallPct, breakdown };
}

/**
 * Counts every project document by inferred workflow status.
 * Missing documents for a type are not invented; only existing rows are counted.
 */
export function selectRiskStatusCounts(documents: Document[] | null | undefined): RiskStatusCounts {
  const list = documents || [];
  const statuses = list.map((doc) => inferDocStatus({ status: doc.status, content: doc.content }));
  const approved = statuses.filter((status) => status === 'approved').length;
  const inReview = statuses.filter((status) => status === 'in_review').length;
  const draft = statuses.filter((status) => status === 'draft').length;
  const notStarted = statuses.filter((status) => status === 'not_started').length;
  return {
    approved,
    inReview,
    draft,
    notStarted,
    total: statuses.length,
  };
}
