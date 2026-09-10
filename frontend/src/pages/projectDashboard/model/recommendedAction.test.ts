import { describe, expect, it } from 'vitest';
import { selectPrimaryRecommendedAction, selectRecommendedActions } from './recommendedAction';
import { makeDocument, pacemakerLikeDocuments } from './testFixtures';

describe('selectRecommendedActions', () => {
  it('selects Complete the Traceability Matrix for a pacemaker-like project', () => {
    const documents = pacemakerLikeDocuments();
    const { primary, remaining } = selectPrimaryRecommendedAction({
      projectId: 'proj-1',
      documents,
      setupComplete: true,
    });

    expect(primary?.id).toBe('complete-traceability-matrix');
    expect(primary?.title).toBe('Complete the Traceability Matrix');
    expect(primary?.reason).toBe('Traceability is not approved yet; gaps may exist.');
    expect(primary?.cta).toBe('Continue');
    expect(primary?.href).toBe(
      `/projects/proj-1/documents/${documents.find((d) => d.type === 'traceability_matrix')?.id}`
    );
    expect(remaining.length).toBeGreaterThan(0);
    expect(remaining.some((item) => item.id === 'complete-traceability-matrix')).toBe(false);
  });

  it('prioritizes setup over traceability when setup is incomplete', () => {
    const documents = pacemakerLikeDocuments();
    const { primary } = selectPrimaryRecommendedAction({
      projectId: 'proj-1',
      documents,
      setupComplete: false,
    });
    expect(primary?.id).toBe('complete-setup');
    expect(primary?.href).toBe('/projects/proj-1/setup');
  });

  it('prioritizes creating a missing required artifact over traceability', () => {
    const documents = pacemakerLikeDocuments().filter((d) => d.type !== 'rmp');
    const { primary } = selectPrimaryRecommendedAction({
      projectId: 'proj-1',
      documents,
      setupComplete: true,
    });
    expect(primary?.id).toBe('create-rmp');
    expect(primary?.title).toMatch(/Create/i);
  });

  it('is deterministic for the same inputs', () => {
    const documents = pacemakerLikeDocuments();
    const a = selectRecommendedActions({ projectId: 'proj-1', documents, setupComplete: true });
    const b = selectRecommendedActions({ projectId: 'proj-1', documents, setupComplete: true });
    expect(a).toEqual(b);
  });

  it('uses the project id from input rather than a hardcoded project', () => {
    const documents = [
      makeDocument({ id: 'rmp-1', type: 'rmp', status: 'draft', content: 'x' }),
      makeDocument({ id: 'ha-1', type: 'hazard_analysis', status: 'draft', content: 'x' }),
      makeDocument({ id: 'fmea-1', type: 'fmea', status: 'draft', content: 'x' }),
      makeDocument({ id: 'rc-1', type: 'risk_controls_doc', status: 'draft', content: 'x' }),
      makeDocument({ id: 'rr-1', type: 'residual_risk', status: 'draft', content: 'x' }),
      makeDocument({ id: 'rmf-1', type: 'rmf', status: 'draft', content: 'x' }),
      makeDocument({
        id: 'tm-9',
        type: 'traceability_matrix',
        status: 'draft',
        content: 'matrix draft',
      }),
    ];
    const { primary } = selectPrimaryRecommendedAction({
      projectId: 'other-project',
      documents,
      setupComplete: true,
    });
    expect(primary?.href).toBe('/projects/other-project/documents/tm-9');
  });
});
