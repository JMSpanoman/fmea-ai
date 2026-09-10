import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useProject } from '../../contexts/ProjectContext';
import { NavIcon } from './NavIcon';
import {
  DOCUMENT_LIBRARY_GROUPS,
  isDocumentGroupActive,
  isDocumentLibraryPath,
} from './navConfig';

export function DocumentLibraryNav({ onNavigate }: { onNavigate?: () => void }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { currentProject } = useProject();
  const libraryActive = isDocumentLibraryPath(location.pathname);
  const [open, setOpen] = useState(libraryActive);

  return (
    <div className="mt-6">
      <button
        type="button"
        className={`w-full flex items-center justify-between gap-2 min-h-control-lg px-3 rounded-control text-sm font-semibold text-left ${
          libraryActive ? 'bg-brand-muted text-brand' : 'text-navy hover:bg-gray-50'
        }`}
        aria-expanded={open}
        aria-controls="document-library-nav"
        onClick={() => setOpen((value) => !value)}
      >
        <span className="inline-flex items-center gap-3">
          <NavIcon name="library" className="w-5 h-5 flex-shrink-0" />
          Document library
        </span>
        <NavIcon
          name="chevron"
          className={`w-4 h-4 flex-shrink-0 transition-transform ${open ? 'rotate-180' : ''}`}
        />
      </button>
      {open && (
        <ul id="document-library-nav" className="mt-1 ml-2 space-y-0.5 border-l border-gray-200 pl-2">
          {DOCUMENT_LIBRARY_GROUPS.map((group) => {
            const href = currentProject?.id
              ? `/projects/${currentProject.id}/docs/${group.id}`
              : '/projects';
            const active = isDocumentGroupActive(location.pathname, group.id);
            return (
              <li key={group.id}>
                <button
                  type="button"
                  onClick={() => {
                    navigate(href);
                    onNavigate?.();
                  }}
                  aria-current={active ? 'page' : undefined}
                  className={`w-full text-left px-3 py-2 rounded-control text-sm min-h-control ${
                    active
                      ? 'bg-brand-muted text-brand font-medium shadow-[inset_3px_0_0_0_var(--sr-color-brand)]'
                      : 'text-muted hover:bg-gray-50 hover:text-navy'
                  }`}
                >
                  {group.label}
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
