import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const TestAuth: React.FC = () => {
  const navigate = useNavigate();
  const [authStatus, setAuthStatus] = useState<string>('Checking...');
  const [token, setToken] = useState<string>('');
  const [user, setUser] = useState<string>('');

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    
    setToken(storedToken || 'No token found');
    setUser(storedUser || 'No user found');
    
    if (storedToken && storedUser) {
      setAuthStatus('Authenticated');
    } else {
      setAuthStatus('Not authenticated');
    }
  }, []);

  const handleDevLogin = async () => {
    try {
      const response = await fetch('http://localhost:8000/auth/dev-login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        setAuthStatus('Development login successful!');
        setToken(data.access_token);
        setUser(JSON.stringify(data.user, null, 2));
      } else {
        setAuthStatus('Development login failed');
      }
    } catch (error) {
      setAuthStatus(`Error: ${error}`);
    }
  };

  const handleClearAuth = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setAuthStatus('Authentication cleared');
    setToken('No token found');
    setUser('No user found');
  };

  const handleTestNavigation = () => {
    navigate('/builder');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Authentication Test Page</h1>
        
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Authentication Status</h2>
          <div className="space-y-4">
            <div>
              <strong>Status:</strong> 
              <span className={`ml-2 px-2 py-1 rounded text-sm ${
                authStatus.includes('Authenticated') || authStatus.includes('successful') 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {authStatus}
              </span>
            </div>
            
            <div>
              <strong>Token:</strong>
              <div className="mt-1 p-2 bg-gray-100 rounded text-xs font-mono break-all">
                {token}
              </div>
            </div>
            
            <div>
              <strong>User:</strong>
              <div className="mt-1 p-2 bg-gray-100 rounded text-xs font-mono break-all">
                {user}
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Actions</h2>
          <div className="space-y-4">
            <button
              onClick={handleDevLogin}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 mr-4"
            >
              Development Login
            </button>
            
            <button
              onClick={handleClearAuth}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 mr-4"
            >
              Clear Authentication
            </button>
            
            <button
              onClick={handleTestNavigation}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              Test Navigation to /builder
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Instructions</h2>
          <ol className="list-decimal list-inside space-y-2 text-gray-700">
            <li>Click "Development Login" to authenticate</li>
            <li>Check that the status shows "Authenticated"</li>
            <li>Click "Test Navigation to /builder" to test the FMEA builder</li>
            <li>If it works, you should see the FMEA builder interface</li>
            <li>If it doesn't work, check the browser console for errors</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default TestAuth; 