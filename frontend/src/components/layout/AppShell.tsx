import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useProject } from '../../contexts/ProjectContext';
import { useAuth } from '../../contexts/AuthContext';
import { AiAssistantPanel } from '../ai/AiAssistantPanel';
import GenerateDesignInputsModal from '../GenerateDesignInputsModal';
import GenerateDesignOutputsModal from '../GenerateDesignOutputsModal';

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
  { path: '/dfmea', label: 'FMEA', icon: '🛡️', group: 'SmartQS: Risk' },
  { path: '/capa', label: 'CAPA', icon: '🔧', group: 'SmartQS: Risk' },
  { path: '/pms', label: 'PMS', icon: '📈', group: 'SmartQS: Risk' },
  
  // Quality Intelligence (Phase 2)
  { path: '/design-inputs', label: 'Design Inputs', icon: '📥', group: 'SmartQS: Design' },
  { path: '/design-outputs', label: 'Design Outputs', icon: '📤', group: 'SmartQS: Design' },
  { path: '/design-controls', label: 'Design Controls', icon: '📋', group: 'SmartQS: Design' },
  { path: '/vv', label: 'V&V Tests', icon: '✅', group: 'SmartQS: Design' },
  { path: '/traceability-matrix', label: 'Traceability', icon: '🔗', group: 'SmartQS: Design' },
  
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
  const [showGenerateDesignInputsModal, setShowGenerateDesignInputsModal] = useState(false);
  const [showGenerateDesignOutputsModal, setShowGenerateDesignOutputsModal] = useState(false);

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
    <div className="flex h-screen overflow-hidden bg-gray-200">
      {/* Sidebar */}
      <aside
        className={`
          ${sidebarCollapsed ? 'w-18' : 'w-64'}
          bg-gray-200 border-r border-gray-300
          flex flex-col transition-smooth-slow
          flex-shrink-0
        `}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-border">
          {!sidebarCollapsed && (
            <div className="flex items-center gap-2">
              <span className="text-2xl">✨</span>
              <span className="text-h3 font-bold text-gray-900">Smart Risk</span>
            </div>
          )}
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="text-gray-900 hover:text-gray-900 transition-smooth"
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
                  <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wider">
                    {group}
                  </h3>
                </div>
              )}
              {items.map((item) => (
                <button
                  key={item.path}
                  onClick={() => {
                    if (item.path === '/design-inputs') {
                      setShowGenerateDesignInputsModal(true);
                    } else if (item.path === '/design-outputs') {
                      setShowGenerateDesignOutputsModal(true);
                    } else {
                      navigate(item.path);
                    }
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
        <header className="h-16 bg-gray-200 border-b border-gray-300 flex items-center justify-between px-6">
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
            {/* AI Assistant Toggle */}
            <button
              onClick={() => setShowAiPanel(!showAiPanel)}
              className={`
                px-4 py-2 rounded-button text-sm font-medium transition-smooth
                ${showAiPanel
                  ? 'bg-primary text-white'
                  : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
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
                <div className="absolute right-0 mt-2 w-48 bg-gray-200 border border-gray-300 rounded-card shadow-elevated py-2">
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

