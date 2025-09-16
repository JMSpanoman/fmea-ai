// src/components/Auth/Login.tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import Footer from '../Footer';

const Login = () => {
  const navigate = useNavigate();

  return (
    <div className="p-4 max-w-md mx-auto mt-20">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold mb-4 text-center">Welcome to FMEA Builder</h1>
        <p className="text-gray-600 mb-6 text-center">
          Get started with your FMEA analysis
        </p>
        <div className="space-y-3">
          <button
            onClick={() => navigate('/builder')}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Start Building FMEA
          </button>
      <button
            onClick={() => navigate('/dashboard')}
            className="w-full px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
      >
            Go to Dashboard
      </button>
        </div>
      </div>
      
      {/* Footer */}
      <Footer />
    </div>
  );
};

export default Login;
