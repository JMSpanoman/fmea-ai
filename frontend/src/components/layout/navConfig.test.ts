import { describe, expect, it } from 'vitest';
import {
  DOCUMENT_LIBRARY_GROUPS,
  PRIMARY_NAV_ITEMS,
  isDocumentGroupActive,
  isNavItemActive,
  resolveNavHref,
} from './navConfig';

describe('navConfig', () => {
  it('includes the simplified primary destinations', () => {
    expect(PRIMARY_NAV_ITEMS.map((item) => item.id)).toEqual([
      'dashboard',
      'projects',
      'documents',
      'traceability',
      'actions',
      'reports',
    ]);
  });

  it('maps to existing routes rather than invented modules', () => {
    const pid = 'abc';
    expect(resolveNavHref('dashboard', pid)).toBe('/projects/abc/dashboard');
    expect(resolveNavHref('projects', pid)).toBe('/projects');
    expect(resolveNavHref('documents', pid)).toBe('/projects/abc/documents');
    expect(resolveNavHref('traceability', pid)).toBe('/traceability-matrix');
    expect(resolveNavHref('reports', pid)).toBe('/export');
    expect(resolveNavHref('actions', pid)).toBe(
      '/projects/abc/dashboard#next-recommended-action'
    );
  });

  it('does not send users to a fake Actions or Reports application', () => {
    expect(resolveNavHref('actions', 'abc')).not.toContain('/actions');
    expect(resolveNavHref('reports', 'abc')).not.toContain('/smart-risk-2');
  });

  it('marks the active destination from the current path', () => {
    expect(isNavItemActive('dashboard', '/projects/abc/dashboard')).toBe(true);
    expect(isNavItemActive('documents', '/projects/abc/documents/xyz')).toBe(true);
    expect(isNavItemActive('traceability', '/traceability-matrix')).toBe(true);
    expect(isNavItemActive('reports', '/export')).toBe(true);
    expect(isNavItemActive('actions', '/projects/abc/dashboard', '#next-recommended-action')).toBe(
      true
    );
    expect(isNavItemActive('dashboard', '/projects/abc/dashboard', '#next-recommended-action')).toBe(
      false
    );
  });

  it('preserves existing document library group destinations', () => {
    expect(DOCUMENT_LIBRARY_GROUPS.map((g) => g.label)).toEqual([
      'Risk Management Core',
      'Design Controls',
      'Verification, Validation & Clinical',
      'Traceability & Impact',
      'Post-Market & CAPA',
      'Usability & Human Factors',
      'Quality System & Governance',
      'Regulatory & Audit Outputs',
    ]);
    expect(isDocumentGroupActive('/projects/abc/docs/risk_management_core', 'risk_management_core')).toBe(
      true
    );
  });
});
