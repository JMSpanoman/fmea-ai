import React, { useState } from 'react';
import { CommandBar } from '../CommandBar';
import { AppFooter } from './AppFooter';
import { AppHeader } from './AppHeader';
import { AppSidebar } from './AppSidebar';

interface AppShellProps {
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [commandOpen, setCommandOpen] = useState(false);

  React.useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      const isMac = navigator.platform.toLowerCase().includes('mac');
      const combo = (isMac ? event.metaKey : event.ctrlKey) && event.key.toLowerCase() === 'k';
      if (combo) {
        event.preventDefault();
        setCommandOpen(true);
      } else if (event.key === 'Escape') {
        setCommandOpen(false);
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, []);

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-canvas text-ink">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:bg-white focus:px-3 focus:py-2 focus:rounded-control focus:text-sm"
      >
        Skip to main content
      </a>
      <AppHeader onOpenNavigation={() => setMobileNavOpen(true)} />
      <div className="flex flex-1 min-h-0">
        <AppSidebar mobileOpen={mobileNavOpen} onClose={() => setMobileNavOpen(false)} />
        <div className="flex-1 flex flex-col min-w-0">
          <main id="main-content" className="flex-1 overflow-y-auto">
            {children}
            <AppFooter />
          </main>
        </div>
      </div>
      <CommandBar isOpen={commandOpen} onClose={() => setCommandOpen(false)} />
    </div>
  );
};
