import { docsGroups } from '../../features/docs/docsRegistry';

export type PrimaryNavId =
  | 'dashboard'
  | 'projects'
  | 'documents'
  | 'traceability'
  | 'actions'
  | 'reports';

export interface PrimaryNavItem {
  id: PrimaryNavId;
  label: string;
  /**
   * Logical destination key. Resolved against the current project at click time.
   * `unsupported` items are omitted from the rendered nav (documented gap).
   */
  destination: 'dashboard' | 'projects' | 'documents' | 'traceability' | 'reports' | 'actions';
  icon: NavIconName;
  requiresPro?: boolean;
}

export type NavIconName =
  | 'dashboard'
  | 'projects'
  | 'documents'
  | 'traceability'
  | 'actions'
  | 'reports';

/**
 * Primary navigation for SmartRisk 1.
 *
 * Route mapping (existing destinations only):
 * - Dashboard     → `/projects/:id/dashboard` (or `/` when no project)
 * - Projects      → `/projects`
 * - Documents     → `/projects/:id/documents`
 * - Traceability  → `/traceability-matrix` (existing workflow page)
 * - Reports       → `/export` (existing Export Center; header "Export report" uses the same destination)
 *
 * Actions gap:
 * There is no standalone Actions module or route in SmartRisk 1.
 * The closest supported surface is the project overview recommended-action card.
 * The Actions item therefore opens the current project dashboard and targets
 * `#next-recommended-action`. This is a presentation mapping, not a new feature.
 */
export const PRIMARY_NAV_ITEMS: PrimaryNavItem[] = [
  { id: 'dashboard', label: 'Dashboard', destination: 'dashboard', icon: 'dashboard', requiresPro: true },
  { id: 'projects', label: 'Projects', destination: 'projects', icon: 'projects', requiresPro: true },
  { id: 'documents', label: 'Documents', destination: 'documents', icon: 'documents', requiresPro: true },
  { id: 'traceability', label: 'Traceability', destination: 'traceability', icon: 'traceability', requiresPro: true },
  { id: 'actions', label: 'Actions', destination: 'actions', icon: 'actions', requiresPro: true },
  { id: 'reports', label: 'Reports', destination: 'reports', icon: 'reports', requiresPro: false },
];

export const DOCUMENT_LIBRARY_GROUPS = docsGroups.map((group) => ({
  id: group.id,
  label: group.name,
}));

export function resolveNavHref(
  destination: PrimaryNavItem['destination'],
  projectId?: string | null
): string {
  switch (destination) {
    case 'dashboard':
      return projectId ? `/projects/${projectId}/dashboard` : '/';
    case 'projects':
      return '/projects';
    case 'documents':
      return projectId ? `/projects/${projectId}/documents` : '/projects';
    case 'traceability':
      return '/traceability-matrix';
    case 'actions':
      return projectId
        ? `/projects/${projectId}/dashboard#next-recommended-action`
        : '/';
    case 'reports':
      return '/export';
    default:
      return '/';
  }
}

export function isNavItemActive(
  destination: PrimaryNavItem['destination'],
  pathname: string,
  hash = ''
): boolean {
  if (destination === 'dashboard') {
    return pathname.includes('/dashboard') && hash !== '#next-recommended-action';
  }
  if (destination === 'actions') {
    return pathname.includes('/dashboard') && hash === '#next-recommended-action';
  }
  if (destination === 'projects') {
    return pathname === '/projects' || pathname === '/projects/';
  }
  if (destination === 'documents') {
    return /\/projects\/[^/]+\/documents/.test(pathname);
  }
  if (destination === 'traceability') {
    return (
      pathname.startsWith('/traceability-matrix') ||
      pathname.startsWith('/tracability') ||
      pathname.includes('/risk-traceability')
    );
  }
  if (destination === 'reports') {
    return pathname.startsWith('/export') || pathname.includes('/reports/');
  }
  return false;
}

export function isDocumentLibraryPath(pathname: string): boolean {
  return /\/projects\/[^/]+\/docs(\/|$)/.test(pathname);
}

export function isDocumentGroupActive(pathname: string, groupId: string): boolean {
  return pathname.includes(`/docs/${groupId}`);
}
