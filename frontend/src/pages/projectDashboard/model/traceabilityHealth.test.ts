import { describe, expect, it } from 'vitest';
import { selectTraceabilityHealth } from './traceabilityHealth';
import { NOT_EVALUATED_YET } from './presentationLabels';
import { makeDocument } from './testFixtures';

describe('selectTraceabilityHealth', () => {
  it('uses Not evaluated yet for missing link metrics', () => {
    const health = selectTraceabilityHealth([
      makeDocument({ id: 'tm', type: 'traceability_matrix', status: 'draft', content: 'x' }),
    ]);
    expect(health.missingLinksLabel).toBe(NOT_EVALUATED_YET);
    expect(health.brokenLinksLabel).toBe(NOT_EVALUATED_YET);
    expect(health.statusLabel).toBe('Needs attention');
    expect(health.supportingText).toContain('Not evaluated yet');
    expect(health.supportingText.toLowerCase()).not.toContain('unknown');
  });

  it('keeps approved matrix status distinct from link metrics', () => {
    const health = selectTraceabilityHealth([
      makeDocument({ id: 'tm', type: 'traceability_matrix', status: 'approved', content: 'x' }),
    ]);
    expect(health.statusLabel).toBe('Approved');
    expect(health.missingLinksLabel).toBe(NOT_EVALUATED_YET);
  });
});
