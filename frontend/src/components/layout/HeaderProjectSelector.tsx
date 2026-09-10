import React, { useEffect, useId, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useProject } from '../../contexts/ProjectContext';
import projectService, { type Project } from '../../services/projectService';

function projectDashboardPath(projectId: string, currentPath: string): string {
  const match = currentPath.match(/^\/projects\/[^/]+(\/.*)?$/);
  if (match && match[1] && match[1] !== '') {
    return `/projects/${projectId}${match[1]}`;
  }
  return `/projects/${projectId}/dashboard`;
}

export function HeaderProjectSelector() {
  const { currentProject, setCurrentProject } = useProject();
  const navigate = useNavigate();
  const location = useLocation();
  const [open, setOpen] = useState(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const rootRef = useRef<HTMLDivElement | null>(null);
  const listId = useId();

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        setLoading(true);
        const data = await projectService.getProjects();
        if (!cancelled) {
          setProjects(Array.isArray(data) ? data : []);
          setError(null);
        }
      } catch {
        if (!cancelled) setError('Failed to load projects');
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!open) return;
    const onPointer = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    };
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setOpen(false);
    };
    document.addEventListener('mousedown', onPointer);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onPointer);
      document.removeEventListener('keydown', onKey);
    };
  }, [open]);

  const selectProject = (project: Project) => {
    setCurrentProject(project);
    setOpen(false);
    navigate(projectDashboardPath(project.id, location.pathname));
  };

  const label = currentProject?.name || 'Select project';

  return (
    <div className="relative min-w-0" ref={rootRef}>
      <button
        type="button"
        className="inline-flex items-center gap-2 max-w-[12rem] sm:max-w-[18rem] min-h-control px-3 rounded-control border border-gray-200 bg-white text-sm font-medium text-navy hover:bg-gray-50"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={listId}
        aria-label={`Current project: ${label}`}
        onClick={() => setOpen((value) => !value)}
      >
        <span className="truncate">{label}</span>
        <svg
          className={`w-4 h-4 flex-shrink-0 text-muted transition-transform ${open ? 'rotate-180' : ''}`}
          viewBox="0 0 20 20"
          fill="none"
          aria-hidden="true"
        >
          <path d="M5 7.5L10 12.5L15 7.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        </svg>
      </button>

      {open && (
        <ul
          id={listId}
          role="listbox"
          aria-label="Projects"
          className="absolute z-50 mt-2 w-72 max-h-72 overflow-y-auto rounded-card border border-gray-200 bg-white py-1 shadow-elevated"
        >
          {loading ? (
            <li className="px-3 py-2 text-sm text-muted">Loading projects…</li>
          ) : error ? (
            <li className="px-3 py-2 text-sm text-red-700">{error}</li>
          ) : projects.length === 0 ? (
            <li className="px-3 py-2 text-sm text-muted">No projects available.</li>
          ) : (
            projects.map((project) => {
              const selected = currentProject?.id === project.id;
              return (
                <li key={project.id} role="option" aria-selected={selected}>
                  <button
                    type="button"
                    className={`w-full text-left px-3 py-2.5 text-sm min-h-control ${
                      selected ? 'bg-brand-muted text-brand font-medium' : 'text-navy hover:bg-gray-50'
                    }`}
                    onClick={() => selectProject(project)}
                  >
                    <span className="truncate block">{project.name}</span>
                  </button>
                </li>
              );
            })
          )}
        </ul>
      )}
    </div>
  );
}
