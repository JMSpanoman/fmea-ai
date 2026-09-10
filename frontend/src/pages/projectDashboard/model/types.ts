import type { Document } from '../../../types';
import { inferDocStatus, type DocRowStatus } from '../DocumentRow';

export type LoadAvailability = 'loading' | 'ready' | 'empty' | 'error' | 'unavailable';

export type ReadinessCategoryName =
  | 'Risk Management'
  | 'Design Controls'
  | 'V&V'
  | 'Traceability';

export const READINESS_CATEGORIES: Array<{ name: ReadinessCategoryName; types: string[] }> = [
  {
    name: 'Risk Management',
    types: ['rmp', 'hazard_analysis', 'fmea', 'risk_controls_doc', 'residual_risk', 'rmf'],
  },
  { name: 'Design Controls', types: ['design_inputs_doc', 'design_outputs_doc'] },
  { name: 'V&V', types: ['vv_evidence'] },
  { name: 'Traceability', types: ['traceability_matrix'] },
];

export const REQUIRED_RISK_DOC_TYPES = [
  'rmp',
  'hazard_analysis',
  'fmea',
  'risk_controls_doc',
  'residual_risk',
  'rmf',
  'traceability_matrix',
] as const;

export type ProjectProgressStageId =
  | 'setup'
  | 'documents'
  | 'risk_analysis'
  | 'traceability'
  | 'review_export';

export type ProjectProgressStageState = 'complete' | 'current' | 'upcoming';

export interface ProjectProgressStage {
  id: ProjectProgressStageId;
  label: string;
  state: ProjectProgressStageState;
  complete: boolean;
}

export interface RecommendedAction {
  id: string;
  title: string;
  reason: string;
  cta: string;
  href: string;
  priority: number;
}

export interface ReadinessBreakdownItem {
  name: ReadinessCategoryName;
  pct: number;
}

export interface ProjectReadiness {
  overallPct: number;
  breakdown: ReadinessBreakdownItem[];
}

export interface RiskStatusCounts {
  approved: number;
  inReview: number;
  draft: number;
  notStarted: number;
  total: number;
}

export interface TraceabilityHealthView {
  statusLabel: 'Needs attention' | 'Approved' | 'Not evaluated yet';
  statusKind: 'attention' | 'healthy' | 'neutral';
  missingLinksLabel: string;
  brokenLinksLabel: string;
  supportingText: string;
  matrixStatus: DocRowStatus | null;
}

export function documentsByType(documents: Document[] | null | undefined): Record<string, Document> {
  const map: Record<string, Document> = {};
  for (const doc of documents || []) {
    if (doc?.type) map[doc.type] = doc;
  }
  return map;
}

export function statusesForTypes(
  types: string[],
  byType: Record<string, Document>
): DocRowStatus[] {
  return types.map((type) => {
    const doc = byType[type];
    return inferDocStatus({ status: doc?.status, content: doc?.content });
  });
}

export function percentApproved(statuses: DocRowStatus[]): number {
  if (!statuses.length) return 0;
  const approved = statuses.filter((status) => status === 'approved').length;
  return Math.round((approved / statuses.length) * 100);
}
