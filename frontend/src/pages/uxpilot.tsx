// src/pages/UxPilot.tsx
import React from "react";
import { useNavigate } from "react-router-dom";
import Footer from '../components/Footer';

export default function UxPilot() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-gray-900">Smart FMEA Builder</h1>
              </div>
            </div>
            <nav className="hidden md:flex space-x-8">
              <button
                onClick={() => navigate('/builder')}
                className="text-gray-500 hover:text-gray-900 px-3 py-2 text-sm font-medium"
              >
                FMEA Builder
              </button>
              <button
                onClick={() => navigate('/dashboard')}
                className="text-gray-500 hover:text-gray-900 px-3 py-2 text-sm font-medium"
              >
                Dashboard
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h2 className="text-4xl font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
            Build Accurate FMEAs in Minutes, Not Hours
          </h2>
          <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
            Streamline your risk analysis process with AI-powered suggestions, real-time scoring, and export-ready reports.
          </p>
          <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
            <div className="rounded-md shadow">
              <button
                onClick={() => navigate('/builder')}
                className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 md:py-4 md:text-lg md:px-10"
              >
                Start New FMEA
              </button>
            </div>
            <div className="mt-3 rounded-md shadow sm:mt-0 sm:ml-3">
              <button
                onClick={() => navigate('/dashboard')}
                className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-blue-600 bg-white hover:bg-gray-50 md:py-4 md:text-lg md:px-10"
              >
                View Dashboard
              </button>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="mt-16">
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <span className="text-blue-600 font-bold text-xl">1</span>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Define Components</h3>
              <p className="text-gray-600 text-sm">
                Start by identifying and describing the component or system you want to analyze.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <span className="text-blue-600 font-bold text-xl">2</span>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">AI-Powered Analysis</h3>
              <p className="text-gray-600 text-sm">
                Our AI suggests failure modes, effects, and mitigation strategies based on your inputs.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <span className="text-blue-600 font-bold text-xl">3</span>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Export & Share</h3>
              <p className="text-gray-600 text-sm">
                Export your FMEA analysis in multiple formats including CSV, PDF, and Excel.
              </p>
            </div>
          </div>
        </div>
      </main>
      
      {/* Footer */}
      <Footer />
    </div>
  );
}