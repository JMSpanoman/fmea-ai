import { describe, expect, it } from 'vitest';
import { selectProjectProgress } from './projectProgress';
import { makeDocument } from './testFixtures';

describe('selectProjectProgress', () => {
  it('marks only setup complete when later categories are not approved', () => {
    const stages = selectProjectProgress({
      setupComplete: true,
      documents: [
        makeDocument({ id: '1', type: 'design_inputs_doc', status: 'draft', content: 'x' }),
        makeDocument({ id: '2', type: 'traceability_matrix', status: 'draft', content: 'x' }),
      ],
    });
    expect(stages.map((s) => s.state)).toEqual([
      'complete',
      'current',
      'upcoming',
      'upcoming',
      'upcoming',
    ]);
  });

  it('does not fabricate setup completion', () => {
    const stages = selectProjectProgress({ setupComplete: false, documents: [] });
    expect(stages[0].state).toBe('current');
    expect(stages[0].complete).toBe(false);
  });

  it('requires earlier stages before marking later stages complete', () => {
    const stages = selectProjectProgress({
      setupComplete: false,
      documents: [
        makeDocument({ id: '1', type: 'design_inputs_doc', status: 'approved', content: 'x' }),
        makeDocument({ id: '2', type: 'design_outputs_doc', status: 'approved', content: 'x' }),
      ],
    });
    expect(stages.find((s) => s.id === 'documents')?.complete).toBe(false);
  });
});
