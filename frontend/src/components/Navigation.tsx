import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const Navigation: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Home', icon: 'fa-home' },
    { path: '/projects', label: 'Projects', icon: 'fa-folder-tree' },
    { path: '/dashboard', label: 'Dashboard', icon: 'fa-chart-line' },
    { path: '/capa', label: 'CAPA', icon: 'fa-clipboard-check' },
    { path: '/change-control', label: 'Change Control', icon: 'fa-arrows-rotate' },
    { path: '/nonconformance', label: 'Non-Conformance', icon: 'fa-triangle-exclamation' },
    { path: '/hazard-analysis', label: 'Hazard Analysis', icon: 'fa-exclamation-triangle' },
    { path: '/fault-tree-report', label: 'Fault Tree', icon: 'fa-sitemap' },
    { path: '/risk-management-report', label: 'Risk Management', icon: 'fa-shield-halved' },
    { path: '/export', label: 'Export', icon: 'fa-download' },
    { path: '/help', label: 'Help', icon: 'fa-question-circle' }
  ];

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            {/* Logo */}
            <div className="flex-shrink-0 flex items-center">
              <div className="flex items-center">
                <i className="fa-solid fa-shield-halved text-blue-600 text-2xl mr-3"></i>
                <span className="text-xl font-bold text-gray-900">FMEA Builder</span>
              </div>
            </div>

            {/* Navigation Items */}
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              {navItems.map((item) => (
                <button
                  key={item.path}
                  onClick={() => navigate(item.path)}
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors ${
                    isActive(item.path)
                      ? 'border-blue-500 text-gray-900'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                  }`}
                >
                  <i className={`${item.icon} mr-2`}></i>
                  {item.label}
                </button>
              ))}
            </div>
          </div>

          {/* Right side - User menu placeholder */}
          <div className="flex items-center">
            <div className="flex items-center space-x-3">
              <span className="text-sm text-gray-500">Welcome, User</span>
              <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                <i className="fa-solid fa-user text-gray-600"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile navigation */}
      <div className="sm:hidden">
        <div className="pt-2 pb-3 space-y-1">
          {navItems.map((item) => (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={`block pl-3 pr-4 py-2 border-l-4 text-base font-medium transition-colors ${
                isActive(item.path)
                  ? 'bg-blue-50 border-blue-500 text-blue-700'
                  : 'border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800'
              }`}
            >
              <i className={`${item.icon} mr-3`}></i>
              {item.label}
            </button>
          ))}
        </div>
      </div>
    </nav>
  );
};

export default Navigation; 