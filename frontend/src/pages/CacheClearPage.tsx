import React, { useState, useEffect } from 'react';
import { 
  clearAllCache, 
  clearLocalStorageCache, 
  clearSessionStorageCache, 
  clearBrowserCacheAndReload, 
  clearAuthCache, 
  clearFmeaDataCache,
  getCacheStatus,
  type CacheClearOptions 
} from '../utils/cacheUtils';

const CacheClearPage: React.FC = () => {
  const [isClearing, setIsClearing] = useState(false);
  const [cacheStatus, setCacheStatus] = useState<any>(null);
  const [lastAction, setLastAction] = useState<string>('');

  useEffect(() => {
    // Load initial cache status
    setCacheStatus(getCacheStatus());
  }, []);

  const handleClearCache = async (options: CacheClearOptions, actionName: string) => {
    setIsClearing(true);
    setLastAction(actionName);
    
    try {
      await clearAllCache(options);
      
      if (options.browserCache) {
        alert('Cache cleared successfully! The page will reload in a moment.');
      } else {
        alert('Cache cleared successfully!');
        // Refresh cache status
        setCacheStatus(getCacheStatus());
      }
    } catch (error) {
      console.error('Error clearing cache:', error);
      alert('Error clearing cache. Please check console for details.');
    } finally {
      setIsClearing(false);
    }
  };

  const refreshStatus = () => {
    setCacheStatus(getCacheStatus());
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Cache Management</h1>
          <p className="text-gray-600 mb-6">
            Clear different types of cache to resolve issues or start fresh.
          </p>
          
          <div className="flex items-center space-x-4 mb-6">
            <button
              onClick={refreshStatus}
              className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
            >
              🔄 Refresh Status
            </button>
            
            {lastAction && (
              <span className="text-sm text-gray-600">
                Last action: {lastAction}
              </span>
            )}
          </div>
        </div>

        {/* Cache Status */}
        {cacheStatus && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Current Cache Status</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-medium text-blue-800 mb-2">Local Storage</h3>
                <div className="space-y-1 text-sm text-blue-700">
                  <div>Total items: {cacheStatus.localStorage.totalKeys}</div>
                  <div>Token: {cacheStatus.localStorage.token ? '✅ Present' : '❌ Missing'}</div>
                  <div>User: {cacheStatus.localStorage.user ? '✅ Present' : '❌ Missing'}</div>
                  <div>FMEA Data: {cacheStatus.localStorage.fmeaData ? '✅ Present' : '❌ Missing'}</div>
                  <div>Project Data: {cacheStatus.localStorage.projectData ? '✅ Present' : '❌ Missing'}</div>
                </div>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="font-medium text-green-800 mb-2">Session Storage</h3>
                <div className="space-y-1 text-sm text-green-700">
                  <div>Total items: {cacheStatus.sessionStorage.totalKeys}</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Cache Clearing Options */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <button
                onClick={() => handleClearCache({ localStorage: true, sessionStorage: true, browserCache: true }, 'Clear All Cache & Reload')}
                disabled={isClearing}
                className="w-full px-4 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50 font-medium"
              >
                🗑️ Clear All Cache & Reload
              </button>
              
              <button
                onClick={() => handleClearCache({ localStorage: true, sessionStorage: true }, 'Clear App Data')}
                disabled={isClearing}
                className="w-full px-4 py-3 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 disabled:opacity-50 font-medium"
              >
                📱 Clear App Data
              </button>
              
              <button
                onClick={() => handleClearCache({ localStorage: true }, 'Clear Authentication')}
                disabled={isClearing}
                className="w-full px-4 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 font-medium"
              >
                🔐 Clear Authentication
              </button>
            </div>
          </div>

          {/* Specific Cache Types */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Specific Cache Types</h2>
            <div className="space-y-3">
              <button
                onClick={() => handleClearCache({ localStorage: true }, 'Clear Local Storage')}
                disabled={isClearing}
                className="w-full px-4 py-3 bg-purple-300 text-gray-900 rounded-lg hover:bg-purple-400 disabled:opacity-50 font-medium"
              >
                💾 Clear Local Storage
              </button>
              
              <button
                onClick={() => handleClearCache({ sessionStorage: true }, 'Clear Session Storage')}
                disabled={isClearing}
                className="w-full px-4 py-3 bg-purple-300 text-gray-900 rounded-lg hover:bg-purple-400 disabled:opacity-50 font-medium"
              >
                🗂️ Clear Session Storage
              </button>
              
              <button
                onClick={() => handleClearCache({ browserCache: true }, 'Clear Browser Cache')}
                disabled={isClearing}
                className="w-full px-4 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:opacity-50 font-medium"
              >
                🌐 Clear Browser Cache
              </button>
            </div>
          </div>
        </div>

        {/* FMEA Specific Cache */}
        <div className="bg-white rounded-lg shadow-lg p-6 mt-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">FMEA Data Cache</h2>
          <p className="text-gray-600 mb-4">
            Clear specific FMEA-related cached data without affecting authentication.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <button
              onClick={() => {
                clearFmeaDataCache();
                setLastAction('Clear FMEA Data');
                setTimeout(() => setCacheStatus(getCacheStatus()), 500);
              }}
              disabled={isClearing}
              className="px-4 py-3 bg-teal-500 text-white rounded-lg hover:bg-teal-600 disabled:opacity-50 font-medium"
            >
              📊 Clear FMEA Data
            </button>
            
            <button
              onClick={() => {
                clearAuthCache();
                setLastAction('Clear Auth Data');
                setTimeout(() => setCacheStatus(getCacheStatus()), 500);
              }}
              disabled={isClearing}
              className="px-4 py-3 bg-pink-500 text-white rounded-lg hover:bg-pink-600 disabled:opacity-50 font-medium"
            >
              🔑 Clear Auth Data
            </button>
            
            <button
              onClick={() => {
                clearSessionStorageCache();
                setLastAction('Clear Session Data');
                setTimeout(() => setCacheStatus(getCacheStatus()), 500);
              }}
              disabled={isClearing}
              className="px-4 py-3 bg-cyan-500 text-white rounded-lg hover:bg-cyan-600 disabled:opacity-50 font-medium"
            >
              ⏰ Clear Session Data
            </button>
          </div>
        </div>

        {/* Loading State */}
        {isClearing && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Clearing cache...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CacheClearPage;
