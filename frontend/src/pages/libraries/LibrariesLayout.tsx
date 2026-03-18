import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';

const LIBRARY_LINKS = [
  { to: '/libraries/hazards', label: 'Hazard Library' },
  { to: '/libraries/harms', label: 'Harm Library' },
  { to: '/libraries/risk-controls', label: 'Risk Control Library' },
  { to: '/libraries/verifications', label: 'Verification Library' },
  { to: '/libraries/hazard-rules', label: 'Hazard Generation Rules' },
];

export const LibrariesLayout: React.FC = () => {
  return (
    <div className="flex flex-col h-full">
      <nav className="border-b border-border bg-surface-secondary/50 px-4 py-2 flex flex-wrap gap-2">
        {LIBRARY_LINKS.map(({ to, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `px-4 py-2 rounded-lg text-sm font-medium transition-smooth ${
                isActive
                  ? 'bg-primary text-white'
                  : 'text-text-secondary hover:bg-surface-secondary hover:text-text-primary'
              }`
            }
          >
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="flex-1 overflow-auto">
        <Outlet />
      </div>
    </div>
  );
};
