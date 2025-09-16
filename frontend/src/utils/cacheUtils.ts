/**
 * Cache clearing utilities for the FMEA application
 */

export interface CacheClearOptions {
  localStorage?: boolean;
  sessionStorage?: boolean;
  browserCache?: boolean;
  applicationState?: boolean;
}

/**
 * Clear all types of cache
 */
export const clearAllCache = (options: CacheClearOptions = {}) => {
  const {
    localStorage: clearLocalStorage = true,
    sessionStorage: clearSessionStorage = true,
    browserCache: clearBrowserCache = true,
    applicationState: clearAppState = true
  } = options;

  console.log('🧹 Starting cache clearing process...');

  // Clear localStorage
  if (clearLocalStorage) {
    clearLocalStorageCache();
  }

  // Clear sessionStorage
  if (clearSessionStorage) {
    clearSessionStorageCache();
  }

  // Clear browser cache (requires page reload)
  if (clearBrowserCache) {
    clearBrowserCacheAndReload();
  }

  // Clear application state
  if (clearAppState) {
    clearApplicationState();
  }

  console.log('✅ Cache clearing process completed');
};

/**
 * Clear localStorage cache (authentication, user data, etc.)
 */
export const clearLocalStorageCache = () => {
  try {
    const keysToRemove = [
      'token',
      'user',
      'fmeaData',
      'projectData',
      'formData',
      'settings'
    ];

    keysToRemove.forEach(key => {
      if (localStorage.getItem(key)) {
        localStorage.removeItem(key);
        console.log(`🗑️ Removed localStorage key: ${key}`);
      }
    });

    // Also clear any other localStorage items that might contain cached data
    const allKeys = Object.keys(localStorage);
    allKeys.forEach(key => {
      if (key.includes('cache') || key.includes('temp') || key.includes('fmea')) {
        localStorage.removeItem(key);
        console.log(`🗑️ Removed cached localStorage key: ${key}`);
      }
    });

    console.log('✅ localStorage cache cleared');
  } catch (error) {
    console.error('❌ Error clearing localStorage cache:', error);
  }
};

/**
 * Clear sessionStorage cache
 */
export const clearSessionStorageCache = () => {
  try {
    sessionStorage.clear();
    console.log('✅ sessionStorage cache cleared');
  } catch (error) {
    console.error('❌ Error clearing sessionStorage cache:', error);
  }
};

/**
 * Clear browser cache by reloading the page
 */
export const clearBrowserCacheAndReload = () => {
  try {
    // Force reload without cache
    if (navigator.serviceWorker) {
      navigator.serviceWorker.getRegistrations().then(registrations => {
        registrations.forEach(registration => {
          registration.unregister();
          console.log('🗑️ Service worker unregistered');
        });
      });
    }

    // Clear any cached API responses
    if ('caches' in window) {
      caches.keys().then(names => {
        names.forEach(name => {
          caches.delete(name);
          console.log(`🗑️ Cache deleted: ${name}`);
        });
      });
    }

    console.log('✅ Browser cache cleared, page will reload');
    
    // Reload the page to ensure fresh start
    setTimeout(() => {
      window.location.reload();
    }, 1000);
  } catch (error) {
    console.error('❌ Error clearing browser cache:', error);
  }
};

/**
 * Clear application state cache
 */
export const clearApplicationState = () => {
  try {
    // Clear any global variables or window properties
    if (window.fmeaApi) {
      // Reset fmeaApi state if possible
      if (typeof window.fmeaApi.reset === 'function') {
        window.fmeaApi.reset();
        console.log('🔄 fmeaApi state reset');
      }
    }

    // Clear any other global state
    const globalKeys = ['appState', 'userState', 'projectState'] as const;
    globalKeys.forEach(key => {
      if (key in window) {
        delete (window as any)[key];
        console.log(`🗑️ Removed global state: ${key}`);
      }
    });

    console.log('✅ Application state cache cleared');
  } catch (error) {
    console.error('❌ Error clearing application state:', error);
  }
};

/**
 * Clear only authentication cache
 */
export const clearAuthCache = () => {
  try {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    
    // Clear any auth-related session storage
    sessionStorage.removeItem('authState');
    sessionStorage.removeItem('userSession');
    
    console.log('✅ Authentication cache cleared');
  } catch (error) {
    console.error('❌ Error clearing authentication cache:', error);
  }
};

/**
 * Clear only FMEA data cache
 */
export const clearFmeaDataCache = () => {
  try {
    const fmeaKeys = [
      'fmeaData',
      'projectData',
      'formData',
      'componentData',
      'hazardData'
    ];

    fmeaKeys.forEach(key => {
      if (localStorage.getItem(key)) {
        localStorage.removeItem(key);
        console.log(`🗑️ Removed FMEA data: ${key}`);
      }
    });

    console.log('✅ FMEA data cache cleared');
  } catch (error) {
    console.error('❌ Error clearing FMEA data cache:', error);
  }
};

/**
 * Get cache status information
 */
export const getCacheStatus = () => {
  const status = {
    localStorage: {
      token: !!localStorage.getItem('token'),
      user: !!localStorage.getItem('user'),
      fmeaData: !!localStorage.getItem('fmeaData'),
      projectData: !!localStorage.getItem('projectData'),
      totalKeys: Object.keys(localStorage).length
    },
    sessionStorage: {
      totalKeys: Object.keys(sessionStorage).length
    },
    browserCache: {
      hasServiceWorker: !!navigator.serviceWorker,
      hasCaches: 'caches' in window
    }
  };

  console.log('📊 Cache status:', status);
  return status;
};
