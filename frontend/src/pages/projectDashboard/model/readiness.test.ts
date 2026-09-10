import { describe, expect, it } from 'vitest';
import { selectProjectReadiness, selectRiskStatusCounts } from './readiness';
import { makeDocument, pacemakerLikeDocuments } from './testFixtures';

describe('selectProjectReadiness', () => {
  it('computes overall and category percentages from live document status', () => {
    const documents = [
      makeDocument({ id: '1', type: 'design_inputs_doc', status: 'approved', content: 'a' }),
      makeDocument({ id: '2', type: 'design_outputs_doc', status: 'approved', content: 'a' }),
      makeDocument({ id: '3', type: 'rmp', status: 'draft', content: 'a' }),
      makeDocument({ id: '4', type: 'hazard_analysis', status: 'draft', content: 'a' }),
      makeDocument({ id: '5', type: 'fmea', status: 'draft', content: 'a' }),
      makeDocument({ id: '6', type: 'risk_controls_doc', status: 'draft', content: 'a' }),
      makeDocument({ id: '7', type: 'residual_risk', status: 'draft', content: 'a' }),
      makeDocument({ id: '8', type: 'rmf', status: 'draft', content: 'a' }),
      makeDocument({ id: '9', type: 'vv_evidence', status: 'draft', content: 'a' }),
      makeDocument({ id: '10', type: 'traceability_matrix', status: 'draft', content: 'a' }),
    ];
    const result = selectProjectReadiness(documents);
    expect(result.breakdown.find((b) => b.name === 'Design Controls')?.pct).toBe(100);
    expect(result.breakdown.find((b) => b.name === 'Risk Management')?.pct).toBe(0);
    expect(result.breakdown.find((b) => b.name === 'V&V')?.pct).toBe(0);
    expect(result.breakdown.find((b) => b.name === 'Traceability')?.pct).toBe(0);
    expect(result.overallPct).toBe(25);
  });

  it('does not invent documents for missing types', () => {
    const result = selectProjectReadiness([]);
    expect(result.overallPct).toBe(0);
    expect(result.breakdown).toHaveLength(4);
  });
});

describe('selectRiskStatusCounts', () => {
  it('counts inferred statuses for existing documents only', () => {
    const counts = selectRiskStatusCounts(pacemakerLikeDocuments());
    expect(counts.approved).toBe(6);
    expect(counts.inReview).toBe(0);
    expect(counts.draft).toBe(24);
    expect(counts.notStarted).toBe(0);
    expect(counts.total).toBe(30);
  });

  it('treats empty content as not started', () => {
    const counts = selectRiskStatusCounts([
      makeDocument({ id: '1', type: 'rmp', status: 'draft', content: '' }),
    ]);
    expect(counts.notStarted).toBe(1);
    expect(counts.draft).toBe(0);
  });
});
