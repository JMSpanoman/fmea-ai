import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useProject } from '../../contexts/ProjectContext';
import { isProPlan } from '../../config/features';
import { NavIcon } from './NavIcon';
import {
  PRIMARY_NAV_ITEMS,
  isNavItemActive,
  resolveNavHref,
  type PrimaryNavItem,
} from './navConfig';

export function PrimaryNavigation({
  items = PRIMARY_NAV_ITEMS,
  onNavigate,
}: {
  items?: PrimaryNavItem[];
  onNavigate?: () => void;
}) {
  const navigate = useNavigate();
  const location = useLocation();
  const { currentProject } = useProject();
  const { user } = useAuth();
  const isPro = isProPlan(user?.plan ?? 'lite');
  const visibleItems = isPro ? items : items.filter((item) => !item.requiresPro);

  return (
    <ul className="space-y-1">
      {visibleItems.map((item) => {
        const href = resolveNavHref(item.destination, currentProject?.id);
        const active = isNavItemActive(item.destination, location.pathname, location.hash);
        return (
          <li key={item.id}>
            <button
              type="button"
              onClick={() => {
                navigate(href);
                onNavigate?.();
              }}
              aria-current={active ? 'page' : undefined}
              className={`w-full flex items-center gap-3 min-h-control-lg px-3 rounded-control text-sm font-medium text-left transition-smooth ${
                active
                  ? 'bg-brand-muted text-brand shadow-[inset_3px_0_0_0_var(--sr-color-brand)]'
                  : 'text-navy hover:bg-gray-50'
              }`}
            >
              <NavIcon name={item.icon} className="w-5 h-5 flex-shrink-0" />
              <span>{item.label}</span>
            </button>
          </li>
        );
      })}
    </ul>
  );
}
