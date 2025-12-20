import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useProject } from '../../contexts/ProjectContext';
import { useAuth } from '../../contexts/AuthContext';
import { AiAssistantPanel } from '../ai/AiAssistantPanel';

interface AppShellProps {
  children: React.ReactNode;
}

interface NavItem {
  path: string;
  label: string;
  icon: string;
  group?: string;
}

const navItems: NavItem[] = [
  // Core
  { path: '/', label: 'Dashboard', icon: '📊', group: 'Core' },
  { path: '/projects', label: 'Projects', icon: '📁', group: 'Core' },
  
  // Risk
  { path: '/dfmea', label: 'FMEA', icon: '🛡️', group: 'Risk' },
  { path: '/risk-items', label: 'Risk (SmartQS)', icon: '⚠️', group: 'Risk' },
  
  // Quality Intelligence (Phase 2)
  { path: '/design-controls', label: 'Design Controls', icon: '📋', group: 'Quality Intelligence' },
  { path: '/vv', label: 'V&V Tests', icon: '✅', group: 'Quality Intelligence' },
  { path: '/capa', label: 'CAPA', icon: '🔧', group: 'Quality Intelligence' },
  { path: '/pms', label: 'PMS', icon: '📈', group: 'Quality Intelligence' },
  { path: '/traceability-matrix', label: 'Traceability', icon: '🔗', group: 'Quality Intelligence' },
  
  // QMS (Phase 3)
  { path: '/documents', label: 'Documents', icon: '📄', group: 'QMS' },
  { path: '/training', label: 'Training', icon: '🎓', group: 'QMS' },
  { path: '/change-control', label: 'Changes', icon: '🔄', group: 'QMS' },
  { path: '/audits', label: 'Audits', icon: '🔍', group: 'QMS' },
  { path: '/suppliers', label: 'Suppliers', icon: '🏭', group: 'QMS' },
  { path: '/ncrs', label: 'NCRs', icon: '⚠️', group: 'QMS' },
  { path: '/complaints', label: 'Complaints', icon: '📢', group: 'QMS' },
  { path: '/equipment', label: 'Equipment', icon: '⚙️', group: 'QMS' },
  { path: '/events', label: 'Events', icon: '📅', group: 'QMS' },
];

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [showAiPanel, setShowAiPanel] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { currentProject } = useProject();
  const { user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  const groupedNav = navItems.reduce((acc, item) => {
    const group = item.group || 'Other';
    if (!acc[group]) acc[group] = [];
    acc[group].push(item);
    return acc;
  }, {} as Record<string, NavItem[]>);

  return (
    <div className="flex h-screen overflow-hidden bg-background-main">
      {/* Sidebar */}
      <aside
        className={`
          ${sidebarCollapsed ? 'w-18' : 'w-64'}
          bg-surface-primary border-r border-border
          flex flex-col transition-smooth-slow
          flex-shrink-0
        `}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-border">
          {!sidebarCollapsed && (
            <div className="flex items-center gap-2">
              <span className="text-2xl">✨</span>
              <span className="text-h3 font-bold text-text-primary">Smart Risk</span>
            </div>
          )}
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="text-text-secondary hover:text-text-primary transition-smooth"
          >
            {sidebarCollapsed ? '→' : '←'}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4">
          {Object.entries(groupedNav).map(([group, items]) => (
            <div key={group} className="mb-6">
              {!sidebarCollapsed && (
                <div className="px-4 mb-2">
                  <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
                    {group}
                  </h3>
                </div>
              )}
              {items.map((item) => (
                <button
                  key={item.path}
                  onClick={() => navigate(item.path)}
                  className={`
                    w-full flex items-center gap-3 px-4 py-2.5
                    transition-smooth
                    ${isActive(item.path)
                      ? 'bg-primary/20 text-primary border-r-2 border-primary'
                      : 'text-text-secondary hover:bg-surface-secondary hover:text-text-primary'
                    }
                  `}
                >
                  <span className="text-lg">{item.icon}</span>
                  {!sidebarCollapsed && (
                    <span className="text-sm font-medium">{item.label}</span>
                  )}
                </button>
              ))}
            </div>
          ))}
        </nav>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="h-16 bg-surface-primary/80 backdrop-blur-glass border-b border-border flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            {currentProject && (
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-text-primary">
                  {currentProject.name}
                </span>
                <span className="text-xs text-text-secondary">•</span>
                <button className="text-xs text-primary hover:underline">
                  Switch Project
                </button>
              </div>
            )}
          </div>

          <div className="flex items-center gap-4">
            {/* AI Assistant Toggle */}
            <button
              onClick={() => setShowAiPanel(!showAiPanel)}
              className={`
                px-4 py-2 rounded-button text-sm font-medium transition-smooth
                ${showAiPanel
                  ? 'bg-primary text-white'
                  : 'bg-surface-secondary text-text-secondary hover:bg-surface-primary'
                }
              `}
            >
              ✨ AI Assistant
            </button>

            {/* User Menu */}
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-surface-secondary transition-smooth"
              >
                <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white text-sm font-medium">
                  {user?.email?.substring(0, 2).toUpperCase() || 'U'}
                </div>
                {user?.email && (
                  <span className="text-sm text-text-secondary">{user.email}</span>
                )}
              </button>

              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-surface-primary border border-border rounded-card shadow-elevated py-2">
                  <button
                    onClick={logout}
                    className="w-full text-left px-4 py-2 text-sm text-text-secondary hover:bg-surface-secondary hover:text-text-primary transition-smooth"
                  >
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>

      {/* AI Assistant Panel */}
      {showAiPanel && (
        <AiAssistantPanel
          isOpen={showAiPanel}
          onClose={() => setShowAiPanel(false)}
          context={location.pathname}
        />
      )}
    </div>
  );
};

