import React from 'react';
import { useNavigate } from 'react-router-dom';

const ConsistentHeader: React.FC = () => {
  const navigate = useNavigate();

  return (
    <header id="header" className="bg-white border-b border-gray-200 fixed w-full z-10">
      <div className="flex items-center justify-between px-6 py-3">
        <div className="flex items-center">
          <div className="flex items-center mr-8">
            <svg className="h-8 w-8 mr-2" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="18" height="18" rx="4" fill="#0ea5e9" />
              <rect x="22" width="18" height="18" rx="4" fill="#8b5cf6" />
              <rect y="22" width="18" height="18" rx="4" fill="#10b981" />
              <rect x="22" y="22" width="18" height="18" rx="4" fill="#f59e0b" />
            </svg>
            <span className="text-primary-600 font-bold text-2xl">Foton aiQMS Platform</span>
          </div>
          <nav className="hidden md:flex space-x-6">
            <span className="text-gray-800 font-medium hover:text-primary-600 flex items-center cursor-pointer">
              <i className="fa-solid fa-shield-halved mr-2"></i>FMEA
            </span>
            <span className="text-gray-800 font-medium hover:text-primary-600 flex items-center cursor-pointer">
              <i className="fa-solid fa-triangle-exclamation mr-2"></i>Nonconformance
            </span>
            <span 
              onClick={() => navigate('/capa')}
              className="text-gray-800 font-medium hover:text-primary-600 flex items-center cursor-pointer"
            >
              <i className="fa-solid fa-check-double mr-2"></i>CAPA
            </span>

            <span className="text-gray-800 font-medium hover:text-primary-600 flex items-center cursor-pointer">
              <i className="fa-solid fa-arrows-rotate mr-2"></i>Change Control
            </span>
          </nav>
        </div>
        <div className="flex items-center space-x-4">
          <button className="text-gray-500 hover:text-gray-700">
            <i className="fa-solid fa-bell"></i>
          </button>
          <div className="relative">
            <button className="flex items-center text-gray-700 hover:text-gray-900">
              <img src="https://storage.googleapis.com/uxpilot-auth.appspot.com/avatars/avatar-3.jpg" alt="User" className="w-8 h-8 rounded-full mr-2" />
              <span className="font-medium">John Spanomanolis</span>
              <i className="fa-solid fa-chevron-down ml-2 text-xs"></i>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default ConsistentHeader; 