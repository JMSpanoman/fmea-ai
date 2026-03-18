import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '../components/DashboardLayout';

const WelcomePage: React.FC = () => {
  const navigate = useNavigate();
  const [authStatus, setAuthStatus] = useState<string>('Checking...');

  useEffect(() => {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    if (token && user) {
      setAuthStatus('Authenticated');
    } else {
      setAuthStatus('Not authenticated');
    }
  }, []);

  const features = [
    {
      title: 'FMEA Builder',
      description: 'Create and manage Failure Mode and Effects Analysis documents with AI assistance.',
      icon: 'fa-solid fa-shield-halved',
      color: 'bg-blue-500',
      action: 'Get Started →',
      path: '/builder'
    },
    {
      title: 'CAPA Management',
      description: 'Track and manage Corrective and Preventive Actions with automated workflows.',
      icon: 'fa-solid fa-check-double',
      color: 'bg-green-500',
      action: 'View CAPAs →',
      path: '/capa'
    },
    {
      title: 'Change Control',
      description: 'Manage design and process changes with comprehensive approval workflows.',
      icon: 'fa-solid fa-arrows-rotate',
      color: 'bg-purple-300',
      action: 'Manage Changes →',
      path: '/change-control'
    },
    {
      title: 'Non-Conformance',
      description: 'Track and resolve non-conformances with detailed investigation tools.',
      icon: 'fa-solid fa-triangle-exclamation',
      color: 'bg-red-500',
      action: 'View NCs →',
      path: '/non-conformance'
    },
    {
      title: 'Risk Management',
      description: 'Comprehensive risk assessment and mitigation planning tools.',
      icon: 'fa-solid fa-chart-line',
      color: 'bg-orange-500',
      action: 'Risk Analysis →',
      path: '/risk-management'
    },
    {
      title: 'Post-Market',
      description: 'Monitor and analyze post-market surveillance data and trends.',
      icon: 'fa-solid fa-chart-bar',
      color: 'bg-purple-300',
      action: 'Market Data →',
      path: '/post-market'
    }
  ];

  const quickActions = [
    {
      title: 'Start New FMEA',
      description: 'Begin a new Failure Mode and Effects Analysis',
      icon: 'fa-solid fa-plus',
      color: 'bg-blue-600',
      path: '/builder'
    },
    {
      title: 'Design Control',
      description: 'Manage design control processes and documentation',
      icon: 'fa-solid fa-cogs',
      color: 'bg-green-600',
      path: '/design-control'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Authentication Status */}
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-800">
            <strong>Status:</strong> {authStatus}
          </p>
        </div>

        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Welcome to Foton aiQMS Platform
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Your comprehensive quality management system for medical device development
          </p>
        </div>

        {/* Quick Actions */}
        <div className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {quickActions.map((action, index) => (
              <div
                key={index}
                onClick={() => {
                  console.log('Navigating to:', action.path);
                  console.log('Current authentication state:', localStorage.getItem('token') ? 'Authenticated' : 'Not authenticated');
                  navigate(action.path);
                }}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer border border-gray-200"
              >
                <div className="flex items-center mb-4">
                  <div className={`w-12 h-12 rounded-lg ${action.color} flex items-center justify-center mr-4`}>
                    <i className={`${action.icon} text-white text-xl`}></i>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{action.title}</h3>
                    <p className="text-gray-600">{action.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Features Grid */}
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Quality Management Tools</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <div
                key={index}
                onClick={() => navigate(feature.path)}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer border border-gray-200"
              >
                <div className="flex items-center mb-4">
                  <div className={`w-12 h-12 rounded-lg ${feature.color} flex items-center justify-center mr-4`}>
                    <i className={`${feature.icon} text-white text-xl`}></i>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900">{feature.title}</h3>
                </div>
                <p className="text-gray-600 mb-4">{feature.description}</p>
                <button className="text-blue-600 hover:text-blue-800 font-medium flex items-center">
                  {feature.action}
                  <i className="fa-solid fa-arrow-right ml-2"></i>
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Stats Section */}
        <div className="mt-16 bg-gray-50 rounded-lg p-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6 text-center">Platform Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">6</div>
              <div className="text-gray-600">Quality Tools</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">AI</div>
              <div className="text-gray-600">Powered Analysis</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-700 mb-2">FDA</div>
              <div className="text-gray-600">Compliant</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600 mb-2">24/7</div>
              <div className="text-gray-600">Available</div>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="mt-16 text-center">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Ready to Get Started?</h2>
          <p className="text-gray-600 mb-6">Choose a tool to begin your quality management journey</p>
          <div className="flex flex-wrap justify-center gap-4">
            <button
              onClick={() => navigate('/builder')}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Start FMEA Builder
            </button>
            <button
              onClick={() => navigate('/capa')}
              className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors font-medium"
            >
              View CAPAs
            </button>
            <button
              onClick={() => navigate('/change-control')}
              className="bg-purple-300 text-gray-900 px-6 py-3 rounded-lg hover:bg-purple-400 transition-colors font-medium"
            >
              Manage Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomePage;