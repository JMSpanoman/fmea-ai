import React, { useState } from 'react';
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

interface CacheClearButtonProps {
  variant?: 'default' | 'minimal' | 'detailed';
  className?: string;
}

const CacheClearButton: React.FC<CacheClearButtonProps> = ({ 
  variant = 'default', 
  className = '' 
}) => {
  const [isClearing, setIsClearing] = useState(false);
  const [showOptions, setShowOptions] = useState(false);
  const [cacheStatus, setCacheStatus] = useState<any>(null);

  const handleClearAll = async () => {
    setIsClearing(true);
    try {
      await clearAllCache();
      // Show success message
      alert('All cache cleared successfully! The page will reload in a moment.');
    } catch (error) {
      console.error('Error clearing cache:', error);
      alert('Error clearing cache. Please check console for details.');
    } finally {
      setIsClearing(false);
    }
  };

  const handleClearSpecific = async (options: CacheClearOptions) => {
    setIsClearing(true);
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
      console.error('Error clearing specific cache:', error);
      alert('Error clearing cache. Please check console for details.');
    } finally {
      setIsClearing(false);
    }
  };

  const handleShowStatus = () => {
    const status = getCacheStatus();
    setCacheStatus(status);
    setShowOptions(!showOptions);
  };

  if (variant === 'minimal') {
    return (
      <button
        onClick={handleClearAll}
        disabled={isClearing}
        className={`px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50 ${className}`}
        title="Clear all cache"
      >
        {isClearing ? '🧹' : '🗑️'}
      </button>
    );
  }

  if (variant === 'detailed') {
    return (
      <div className={`relative ${className}`}>
        <button
          onClick={handleShowStatus}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Cache Status
        </button>
        
        {showOptions && (
          <div className="absolute right-0 mt-2 w-80 bg-white border border-gray-300 rounded-lg shadow-lg z-50 p-4">
            <div className="mb-4">
              <h3 className="font-semibold text-gray-800 mb-2">Cache Status</h3>
              {cacheStatus && (
                <div className="text-sm text-gray-600 space-y-1">
                  <div>Local Storage: {cacheStatus.localStorage.totalKeys} items</div>
                  <div>Session Storage: {cacheStatus.sessionStorage.totalKeys} items</div>
                  <div>Token: {cacheStatus.localStorage.token ? '✅' : '❌'}</div>
                  <div>User: {cacheStatus.localStorage.user ? '✅' : '❌'}</div>
                  <div>FMEA Data: {cacheStatus.localStorage.fmeaData ? '✅' : '❌'}</div>
                </div>
              )}
            </div>
            
            <div className="space-y-2">
              <button
                onClick={() => handleClearSpecific({ localStorage: true, sessionStorage: true })}
                disabled={isClearing}
                className="w-full px-3 py-2 text-sm bg-yellow-500 text-white rounded hover:bg-yellow-600 disabled:opacity-50"
              >
                Clear App Data
              </button>
              
              <button
                onClick={() => handleClearSpecific({ localStorage: true, sessionStorage: true, browserCache: true })}
                disabled={isClearing}
                className="w-full px-3 py-2 text-sm bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50"
              >
                Clear All & Reload
              </button>
              
              <button
                onClick={() => handleClearSpecific({ localStorage: true })}
                disabled={isClearing}
                className="w-full px-3 py-2 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
              >
                Clear Local Storage Only
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Default variant
  return (
    <div className={`flex flex-col space-y-2 ${className}`}>
      <button
        onClick={handleClearAll}
        disabled={isClearing}
        className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50 flex items-center justify-center space-x-2"
      >
        <span>{isClearing ? '🧹' : '🗑️'}</span>
        <span>{isClearing ? 'Clearing...' : 'Clear All Cache'}</span>
      </button>
      
      <div className="flex space-x-2">
        <button
          onClick={() => handleClearSpecific({ localStorage: true, sessionStorage: true })}
          disabled={isClearing}
          className="flex-1 px-3 py-2 text-sm bg-yellow-500 text-white rounded hover:bg-yellow-600 disabled:opacity-50"
        >
          App Data
        </button>
        
        <button
          onClick={() => handleClearSpecific({ localStorage: true })}
          disabled={isClearing}
          className="flex-1 px-3 py-2 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          Auth Only
        </button>
      </div>
    </div>
  );
};

export default CacheClearButton;
