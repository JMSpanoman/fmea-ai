import type { Document } from '../../../types';
import { docTypeById } from '../../../features/docs/docsRegistry';
import { inferDocStatus, primaryCta } from '../DocumentRow';
import { REQUIRED_RISK_DOC_TYPES, documentsByType, type RecommendedAction } from './types';

const STALE_DRAFT_DAYS = 30;

function daysSince(iso?: string | null): number | null {
  if (!iso) return null;
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return null;
  return Math.floor((Date.now() - date.getTime()) / (1000 * 60 * 60 * 24));
}

function docName(type: string): string {
  return docTypeById[type]?.name || type;
}

function documentHref(projectId: string, doc?: Document | null): string {
  if (doc?.id) return `/projects/${projectId}/documents/${doc.id}`;
  return `/projects/${projectId}/documents`;
}

export interface RecommendedActionInput {
  projectId: string;
  documents: Document[] | null | undefined;
  setupComplete?: boolean;
}

/**
 * Deterministic recommended-action selection.
 *
 * Priority (lowest number wins):
 * 1. Complete project setup when intended use or components are missing.
 * 2. Create a required risk artifact that has no content yet.
 * 3. Complete the Traceability Matrix when it exists but is not approved.
 * 4. Continue a draft that has not been updated in more than 30 days.
 * 5. Continue remaining required drafts / in-review artifacts.
 *
 * Same inputs always produce the same primary action and remaining list.
 * This is a presentation helper; it does not persist or invent backend records.
 */
export function selectRecommendedActions(input: RecommendedActionInput): RecommendedAction[] {
  const { projectId } = input;
  const documents = input.documents || [];
  const byType = documentsByType(documents);
  const items: RecommendedAction[] = [];

  if (input.setupComplete === false) {
    items.push({
      id: 'complete-setup',
      title: 'Complete Project Setup',
      reason: 'Add an intended use and at least one component to unlock deterministic prefill.',
      cta: 'Continue',
      href: `/projects/${projectId}/setup`,
      priority: 1,
    });
  }

  for (const type of REQUIRED_RISK_DOC_TYPES) {
    const doc = byType[type];
    const status = inferDocStatus({ status: doc?.status, content: doc?.content });
    if (status === 'not_started') {
      items.push({
        id: `create-${type}`,
        title: `Create ${docName(type)}`,
        reason: 'This required artifact has no content yet.',
        cta: 'Create',
        href: documentHref(projectId, doc),
        priority: 2,
      });
    }
  }

  const traceability = byType['traceability_matrix'];
  if (traceability) {
    const status = inferDocStatus({
      status: traceability.status,
      content: traceability.content,
    });
    if (status !== 'approved') {
      items.push({
        id: 'complete-traceability-matrix',
        title: 'Complete the Traceability Matrix',
        reason: 'Traceability is not approved yet; gaps may exist.',
        cta: 'Continue',
        href: documentHref(projectId, traceability),
        priority: 3,
      });
    }
  } else {
    items.push({
      id: 'complete-traceability-matrix',
      title: 'Complete the Traceability Matrix',
      reason: 'Traceability is not approved yet; gaps may exist.',
      cta: 'Continue',
      href: `/projects/${projectId}/documents`,
      priority: 3,
    });
  }

  for (const doc of documents) {
    const status = inferDocStatus({ status: doc.status, content: doc.content });
    if (status !== 'draft') continue;
    const age = daysSince(doc.updated_at || doc.created_at);
    if (age !== null && age > STALE_DRAFT_DAYS) {
      items.push({
        id: `stale-${doc.id}`,
        title: doc.name || docName(doc.type),
        reason: `Draft has not been updated in ${age} days.`,
        cta: 'Continue',
        href: documentHref(projectId, doc),
        priority: 4,
      });
    }
  }

  for (const type of REQUIRED_RISK_DOC_TYPES) {
    if (type === 'traceability_matrix') continue;
    const doc = byType[type];
    if (!doc) continue;
    const status = inferDocStatus({ status: doc.status, content: doc.content });
    if (status === 'draft' || status === 'in_review') {
      items.push({
        id: `continue-${type}`,
        title: `${primaryCta(status)} ${docName(type)}`,
        reason:
          status === 'in_review'
            ? 'This required artifact is waiting for review.'
            : 'This required artifact is still a draft.',
        cta: primaryCta(status),
        href: documentHref(projectId, doc),
        priority: 5,
      });
    }
  }

  const seen = new Set<string>();
  return items
    .slice()
    .sort((a, b) => a.priority - b.priority || a.id.localeCompare(b.id))
    .filter((item) => {
      if (seen.has(item.id)) return false;
      seen.add(item.id);
      return true;
    });
}

export function selectPrimaryRecommendedAction(
  input: RecommendedActionInput
): { primary: RecommendedAction | null; remaining: RecommendedAction[] } {
  const [primary = null, ...remaining] = selectRecommendedActions(input);
  return { primary, remaining };
}
