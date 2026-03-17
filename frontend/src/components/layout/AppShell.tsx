import React, { useMemo, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useProject } from '../../contexts/ProjectContext';
import { useAuth } from '../../contexts/AuthContext';
import { getFeatures, isProPlan } from '../../config/features';
import { AiAssistantPanel } from '../ai/AiAssistantPanel';
import GenerateDesignInputsModal from '../GenerateDesignInputsModal';
import GenerateDesignOutputsModal from '../GenerateDesignOutputsModal';
import { docsGroups } from '../../features/docs/docsRegistry';
import { CommandBar } from '../CommandBar';

interface AppShellProps {
  children: React.ReactNode;
}

interface NavItem {
  path: string;
  label: string;
  icon: string;
  section: 'Project' | 'Documentation';
  kind: 'static' | 'doc_group';
  groupId?: string;
  requiresPro?: boolean;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    try {
      const v = localStorage.getItem('ui.sidebarCollapsed');
      if (v === 'true') return true;
      if (v === 'false') return false;
    } catch {
      // ignore
    }
    return true; // default minimized
  });
  const [showAiPanel, setShowAiPanel] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { currentProject } = useProject();
  const { user, logout } = useAuth();
  const plan = user?.plan ?? 'lite';
  const features = getFeatures(plan);
  const isPro = isProPlan(plan);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showGenerateDesignInputsModal, setShowGenerateDesignInputsModal] = useState(false);
  const [showGenerateDesignOutputsModal, setShowGenerateDesignOutputsModal] = useState(false);
  const [commandOpen, setCommandOpen] = useState(false);

  const navItems: NavItem[] = useMemo(() => {
    const projectItems: NavItem[] = [
      { path: '/project-dashboard', label: 'Dashboard', icon: '📊', section: 'Project', kind: 'static', requiresPro: true },
      { path: '/projects', label: 'Projects', icon: '📁', section: 'Project', kind: 'static', requiresPro: true },
      { path: '/project-docs', label: 'Documents', icon: '📄', section: 'Project', kind: 'static', requiresPro: true },
      { path: '/traceability-matrix', label: 'Traceability', icon: '🔗', section: 'Project', kind: 'static', requiresPro: true },
      { path: '/export', label: 'Export', icon: '⬇️', section: 'Project', kind: 'static', requiresPro: false }, // Lite has CSV export
      { path: '/admin', label: 'History', icon: '🕒', section: 'Project', kind: 'static', requiresPro: true },
    ];

    const docItems: NavItem[] = docsGroups.map((g) => ({
      path: `/docs/${g.id}`,
      label: g.name,
      icon: '📘',
      section: 'Documentation',
      kind: 'doc_group',
      groupId: g.id,
      requiresPro: true,
    }));

    const all = [...projectItems, ...docItems];
    // Filter out Pro-only items for Lite users
    return isPro ? all : all.filter((item) => !(item as { requiresPro?: boolean }).requiresPro);
  }, [isPro]);

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    if (path === '/project-dashboard') {
      return location.pathname.includes('/dashboard');
    }
    return location.pathname.startsWith(path);
  };

  // Cmd+K handler (global)
  React.useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      const isMac = navigator.platform.toLowerCase().includes('mac');
      const combo = (isMac ? e.metaKey : e.ctrlKey) && e.key.toLowerCase() === 'k';
      if (combo) {
        e.preventDefault();
        setCommandOpen(true);
      } else if (e.key === 'Escape') {
        setCommandOpen(false);
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, []);

  const groupedNav = useMemo(() => {
    return navItems.reduce((acc, item) => {
      const section = item.section;
      if (!acc[section]) acc[section] = [];
      acc[section].push(item);
      return acc;
    }, {} as Record<'Project' | 'Documentation', NavItem[]>);
  }, [navItems]);

  return (
    <div className="flex h-screen overflow-hidden bg-sky-50">
      {/* Sidebar */}
      <aside
        className={`
          ${sidebarCollapsed ? 'w-18' : 'w-80'}
          bg-sky-50 border-r border-sky-100
          flex flex-col transition-smooth-slow
          flex-shrink-0
        `}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-sky-100">
          {!sidebarCollapsed && (
            <div className="flex items-center gap-2">
              <span className="text-2xl">✨</span>
              <span className="text-h3 font-bold text-gray-900">Smart Risk</span>
              {!isPro && (
                <span className="text-xs px-2 py-0.5 rounded bg-gray-200 text-gray-600 font-medium">Lite</span>
              )}
            </div>
          )}
          <button
            onClick={() => {
              const next = !sidebarCollapsed;
              setSidebarCollapsed(next);
              try {
                localStorage.setItem('ui.sidebarCollapsed', String(next));
              } catch {
                // ignore
              }
            }}
            className="text-gray-900 hover:text-gray-900 transition-smooth"
          >
            {sidebarCollapsed ? '→' : '←'}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4">
          {Object.entries(groupedNav)
            .filter(([, items]) => items.length > 0)
            .map(([section, items]) => (
              <div key={section} className="mb-6">
                {!sidebarCollapsed && (
                  <div className="px-4 mb-2">
                    <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wider">
                      {section}
                    </h3>
                  </div>
                )}
                {items.map((item) => (
                  <button
                    key={item.path}
                    onClick={() => {
                      const pid = currentProject?.id;

                      if (item.path === '/project-dashboard') {
                        if (pid) navigate(`/projects/${pid}/dashboard`);
                        else navigate('/');
                        return;
                      }

                      if (item.path === '/project-docs') {
                        if (pid) navigate(`/projects/${pid}/documents`);
                        else navigate('/projects');
                        return;
                      }

                      if (item.kind === 'doc_group') {
                        if (pid && item.groupId) navigate(`/projects/${pid}/docs/${item.groupId}`);
                        else navigate('/projects');
                        return;
                      }

                      navigate(item.path);
                    }}
                    className={`
                      w-full flex items-center gap-3 px-4 py-2.5
                      transition-smooth
                      ${isActive(item.path)
                        ? 'bg-primary/20 text-primary border-r-2 border-primary'
                        : 'text-gray-900 hover:bg-gray-100 hover:text-gray-900'
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
        <header className="h-16 bg-sky-50 border-b border-sky-100 flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            {currentProject && (
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-900">
                  {currentProject.name}
                </span>
                <span className="text-xs text-gray-900">•</span>
                <button className="text-xs text-primary hover:underline">
                  Switch Project
                </button>
              </div>
            )}
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={() => setCommandOpen(true)}
              className="hidden md:inline-flex items-center gap-2 px-3 py-1.5 rounded-md border border-gray-200 bg-white text-xs text-gray-700 hover:bg-gray-50"
              type="button"
              title="Command bar"
            >
              ⌘K
              <span className="text-gray-400">Jump</span>
            </button>
            {/* AI Assistant Toggle */}
            <button
              onClick={() => setShowAiPanel(!showAiPanel)}
              className={`
                px-4 py-2 rounded-button text-sm font-medium transition-smooth
                ${showAiPanel
                  ? 'bg-primary text-white'
                  : 'bg-white text-gray-900 hover:bg-sky-100'
                }
              `}
            >
              ✨ AI Assistant
            </button>

            {/* User Menu */}
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-gray-100 transition-smooth"
              >
                <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white text-sm font-medium">
                  {user?.email?.substring(0, 2).toUpperCase() || 'U'}
                </div>
                {user?.email && (
                  <span className="text-sm text-gray-900">{user.email}</span>
                )}
              </button>

              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white border border-sky-100 rounded-card shadow-elevated py-2">
                  <button
                    onClick={logout}
                    className="w-full text-left px-4 py-2 text-sm text-gray-900 hover:bg-gray-100 hover:text-gray-900 transition-smooth"
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

      <CommandBar isOpen={commandOpen} onClose={() => setCommandOpen(false)} />

      {/* AI Assistant Panel */}
      {showAiPanel && (
        <AiAssistantPanel
          isOpen={showAiPanel}
          onClose={() => setShowAiPanel(false)}
          context={location.pathname}
        />
      )}

      {/* Generate Design Inputs Modal */}
      <GenerateDesignInputsModal
        isOpen={showGenerateDesignInputsModal}
        onClose={() => setShowGenerateDesignInputsModal(false)}
        onDesignInputsGenerated={(designInputs) => {
          console.log('Generated design inputs:', designInputs);
          // Optionally navigate to a page showing the generated inputs
        }}
      />

      {/* Generate Design Outputs Modal */}
      <GenerateDesignOutputsModal
        isOpen={showGenerateDesignOutputsModal}
        onClose={() => setShowGenerateDesignOutputsModal(false)}
        onDesignOutputsGenerated={(designOutputs) => {
          console.log('Generated design outputs:', designOutputs);
          // Optionally navigate to a page showing the generated outputs
        }}
      />
    </div>
  );
};

