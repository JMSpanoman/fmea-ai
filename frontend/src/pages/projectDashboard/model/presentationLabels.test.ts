import { describe, expect, it } from 'vitest';
import { NOT_EVALUATED_YET, toPresentationUnknown } from './presentationLabels';

describe('toPresentationUnknown', () => {
  it('maps Unknown to Not evaluated yet without changing other values', () => {
    expect(toPresentationUnknown('Unknown')).toBe(NOT_EVALUATED_YET);
    expect(toPresentationUnknown('unknown')).toBe(NOT_EVALUATED_YET);
    expect(toPresentationUnknown('UNKNOWN')).toBe(NOT_EVALUATED_YET);
    expect(toPresentationUnknown(null)).toBe(NOT_EVALUATED_YET);
    expect(toPresentationUnknown(undefined)).toBe(NOT_EVALUATED_YET);
    expect(toPresentationUnknown('')).toBe(NOT_EVALUATED_YET);
    expect(toPresentationUnknown('Approved')).toBe('Approved');
    expect(toPresentationUnknown('12')).toBe('12');
  });
});
