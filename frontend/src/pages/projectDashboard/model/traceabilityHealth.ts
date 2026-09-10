import type { Document } from '../../../types';
import { inferDocStatus } from '../DocumentRow';
import { toPresentationUnknown } from './presentationLabels';
import type { TraceabilityHealthView } from './types';

const SUPPORTING_TEXT =
  'If detailed trace data isn’t available, values remain Not evaluated yet.';

/**
 * Traceability health is honest about missing link-level telemetry.
 * Link counts stay "Not evaluated yet" until a real trace metric exists.
 * Matrix approval is used only for the plain-language status heading.
 */
export function selectTraceabilityHealth(
  documents: Document[] | null | undefined
): TraceabilityHealthView {
  const matrix = (documents || []).find((doc) => doc.type === 'traceability_matrix') || null;
  const matrixStatus = matrix
    ? inferDocStatus({ status: matrix.status, content: matrix.content })
    : null;

  let statusLabel: TraceabilityHealthView['statusLabel'] = 'Not evaluated yet';
  let statusKind: TraceabilityHealthView['statusKind'] = 'neutral';

  if (!matrix || matrixStatus !== 'approved') {
    statusLabel = 'Needs attention';
    statusKind = 'attention';
  } else {
    statusLabel = 'Approved';
    statusKind = 'healthy';
  }

  return {
    statusLabel,
    statusKind,
    missingLinksLabel: toPresentationUnknown('Unknown'),
    brokenLinksLabel: toPresentationUnknown('Unknown'),
    supportingText: SUPPORTING_TEXT,
    matrixStatus,
  };
}
