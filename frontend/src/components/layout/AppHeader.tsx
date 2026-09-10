import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useProject } from '../../contexts/ProjectContext';
import { HeaderProjectSelector } from './HeaderProjectSelector';
import { NavIcon } from './NavIcon';
import { SmartRiskLogo } from './SmartRiskLogo';
import { UserAvatarButton } from './UserAvatarButton';

export function AppHeader({
  onOpenNavigation,
}: {
  onOpenNavigation: () => void;
}) {
  const { currentProject } = useProject();
  const navigate = useNavigate();
  const projectId = currentProject?.id;

  return (
    <header className="h-header bg-white border-b border-gray-200 shadow-header flex items-center px-3 sm:px-4 lg:px-6 gap-3 flex-shrink-0 z-30 min-w-0">
      <Link
        to={projectId ? `/projects/${projectId}/dashboard` : '/'}
        className="inline-flex items-center text-brand min-w-0 flex-shrink-0"
        aria-label="SmartRisk home"
      >
        <SmartRiskLogo />
      </Link>

      <div className="flex-1 min-w-0 flex items-center justify-center lg:justify-start">
        <HeaderProjectSelector />
      </div>

      <div className="hidden md:flex items-center gap-2 flex-shrink-0">
        <button
          type="button"
          className="inline-flex items-center justify-center min-h-control px-3 rounded-control border border-gray-200 bg-white text-sm font-medium text-navy hover:bg-gray-50"
          onClick={() =>
            navigate(projectId ? `/projects/${projectId}/documents` : '/projects')
          }
        >
          Project documents
        </button>
        <button
          type="button"
          className="inline-flex items-center justify-center min-h-control px-3 rounded-control bg-brand text-white text-sm font-medium hover:bg-brand-hover"
          onClick={() => navigate('/export')}
        >
          Export report
        </button>
      </div>

      <div className="flex-shrink-0">
        <UserAvatarButton />
      </div>

      <button
        type="button"
        className="lg:hidden inline-flex items-center justify-center w-11 h-11 rounded-control text-navy hover:bg-gray-50"
        aria-label="Open navigation"
        onClick={onOpenNavigation}
      >
        <NavIcon name="menu" className="w-6 h-6" />
      </button>
    </header>
  );
}
