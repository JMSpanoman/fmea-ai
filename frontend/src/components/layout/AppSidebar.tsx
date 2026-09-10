import React, { useEffect, useRef } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { isProPlan } from '../../config/features';
import { DocumentLibraryNav } from './DocumentLibraryNav';
import { NavIcon } from './NavIcon';
import { PrimaryNavigation } from './PrimaryNavigation';

function SidebarNav({
  onNavigate,
  showDocumentLibrary,
}: {
  onNavigate: () => void;
  showDocumentLibrary: boolean;
}) {
  return (
    <nav aria-label="Primary" className="flex-1 overflow-y-auto px-3 py-4">
      <PrimaryNavigation onNavigate={onNavigate} />
      {showDocumentLibrary ? <DocumentLibraryNav onNavigate={onNavigate} /> : null}
    </nav>
  );
}

export function AppSidebar({
  mobileOpen,
  onClose,
}: {
  mobileOpen: boolean;
  onClose: () => void;
}) {
  const closeRef = useRef<HTMLButtonElement | null>(null);
  const { user } = useAuth();
  const isPro = isProPlan(user?.plan ?? 'lite');

  useEffect(() => {
    if (!mobileOpen) return;
    closeRef.current?.focus();
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKey);
    const previous = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = previous;
    };
  }, [mobileOpen, onClose]);

  return (
    <>
      <aside className="hidden lg:flex w-sidebar flex-shrink-0 flex-col bg-white border-r border-gray-200">
        <SidebarNav onNavigate={onClose} showDocumentLibrary={isPro} />
      </aside>

      {mobileOpen && (
        <div className="lg:hidden fixed inset-0 z-40">
          <button
            type="button"
            className="absolute inset-0 bg-navy/40"
            aria-label="Dismiss navigation"
            onClick={onClose}
          />
          <aside
            className="relative z-10 h-full w-[min(100%,20rem)] bg-white shadow-elevated flex flex-col"
            role="dialog"
            aria-modal="true"
            aria-label="Navigation"
          >
            <div className="h-header flex items-center justify-between px-3 border-b border-gray-200">
              <span className="text-sm font-semibold text-navy px-1">Menu</span>
              <button
                ref={closeRef}
                type="button"
                className="inline-flex items-center justify-center w-11 h-11 rounded-control text-navy hover:bg-gray-50"
                aria-label="Close navigation"
                onClick={onClose}
              >
                <NavIcon name="close" className="w-5 h-5" />
              </button>
            </div>
            <SidebarNav onNavigate={onClose} showDocumentLibrary={isPro} />
          </aside>
        </div>
      )}
    </>
  );
}
