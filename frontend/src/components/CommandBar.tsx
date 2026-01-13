import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProject } from '../contexts/ProjectContext';
import { docsGroups, docTypeById } from '../features/docs/docsRegistry';

type CmdItem = { id: string; label: string; href: string };

export function CommandBar({
  isOpen,
  onClose,
}: {
  isOpen: boolean;
  onClose: () => void;
}) {
  const navigate = useNavigate();
  const { currentProject } = useProject();
  const [q, setQ] = useState('');
  const [idx, setIdx] = useState(0);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const pid = currentProject?.id;

  const items: CmdItem[] = useMemo(() => {
    const base: CmdItem[] = [];

    if (pid) {
      base.push({ id: 'proj-dashboard', label: 'Project Dashboard', href: `/projects/${pid}/dashboard` });
      base.push({ id: 'proj-docs', label: 'Project Documents', href: `/projects/${pid}/documents` });
      base.push({ id: 'proj-docs-reg', label: 'Documentation (Registry)', href: `/projects/${pid}/docs` });

      // Key doc deep links into registry
      const docTargets = [
        'fmea',
        'hazard_analysis',
        'rmf',
        'residual_risk',
        'risk_controls_doc',
        'design_inputs_doc',
        'design_outputs_doc',
        'vv_evidence',
        'traceability_matrix',
      ];
      for (const t of docTargets) {
        const def = docTypeById[t];
        if (def) {
          base.push({
            id: `doc:${t}`,
            label: `${def.name} (${t})`,
            href: `/projects/${pid}/docs/${def.groupId}/${t}`,
          });
        }
      }

      for (const g of docsGroups) {
        base.push({
          id: `group:${g.id}`,
          label: `Documentation: ${g.name}`,
          href: `/projects/${pid}/docs/${g.id}`,
        });
      }
    } else {
      base.push({ id: 'projects', label: 'Projects', href: '/projects' });
    }

    return base;
  }, [pid]);

  const filtered = useMemo(() => {
    const term = q.trim().toLowerCase();
    const list = term ? items.filter((i) => i.label.toLowerCase().includes(term)) : items;
    return list.slice(0, 12);
  }, [items, q]);

  useEffect(() => {
    if (!isOpen) return;
    setQ('');
    setIdx(0);
    const t = setTimeout(() => inputRef.current?.focus(), 0);
    return () => clearTimeout(t);
  }, [isOpen]);

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      const isMac = navigator.platform.toLowerCase().includes('mac');
      const combo = (isMac ? e.metaKey : e.ctrlKey) && e.key.toLowerCase() === 'k';
      if (combo) {
        e.preventDefault();
        if (isOpen) onClose();
        else {
          // opening is controlled by parent; ignore here
        }
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 p-4"
      role="dialog"
      aria-modal="true"
      onMouseDown={onClose}
    >
      <div
        className="w-full max-w-2xl rounded-lg border border-gray-200 bg-white shadow-xl"
        onMouseDown={(e) => e.stopPropagation()}
      >
        <div className="p-3 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <input
              ref={inputRef}
              value={q}
              onChange={(e) => {
                setQ(e.target.value);
                setIdx(0);
              }}
              onKeyDown={(e) => {
                if (e.key === 'Escape') {
                  e.preventDefault();
                  onClose();
                } else if (e.key === 'ArrowDown') {
                  e.preventDefault();
                  setIdx((x) => Math.min(x + 1, Math.max(0, filtered.length - 1)));
                } else if (e.key === 'ArrowUp') {
                  e.preventDefault();
                  setIdx((x) => Math.max(0, x - 1));
                } else if (e.key === 'Enter') {
                  e.preventDefault();
                  const item = filtered[idx];
                  if (item) {
                    navigate(item.href);
                    onClose();
                  }
                }
              }}
              placeholder={pid ? 'Search… (e.g., FMEA, Hazard, Traceability)' : 'Select a project first…'}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
            />
            <div className="text-xs text-gray-500 whitespace-nowrap">⌘K / Ctrl+K</div>
          </div>
        </div>

        <div className="max-h-[420px] overflow-auto">
          {filtered.length ? (
            <ul className="p-2">
              {filtered.map((i, n) => (
                <li key={i.id}>
                  <button
                    type="button"
                    onClick={() => {
                      navigate(i.href);
                      onClose();
                    }}
                    className={`w-full text-left px-3 py-2 rounded-md text-sm ${
                      n === idx ? 'bg-primary/10 text-primary' : 'hover:bg-gray-50 text-gray-900'
                    }`}
                  >
                    {i.label}
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <div className="p-4 text-sm text-gray-700">No results.</div>
          )}
        </div>
      </div>
    </div>
  );
}

