/**
 * Console commands for cache clearing
 * Run these commands directly in your browser's developer console
 */

// Make cache clearing functions available globally for console use
declare global {
  interface Window {
    clearAllCache: () => void;
    clearAuthCache: () => void;
    clearFmeaCache: () => void;
    clearBrowserCache: () => void;
    getCacheStatus: () => any;
    cacheUtils: any;
  }
}

// Import the cache utilities
import { 
  clearAllCache, 
  clearLocalStorageCache, 
  clearSessionStorageCache, 
  clearBrowserCacheAndReload, 
  clearAuthCache, 
  clearFmeaDataCache,
  getCacheStatus 
} from './cacheUtils';

// Make functions available globally
window.clearAllCache = clearAllCache;
window.clearAuthCache = clearAuthCache;
window.clearFmeaCache = clearFmeaDataCache;
window.clearBrowserCache = clearBrowserCacheAndReload;
window.getCacheStatus = getCacheStatus;

// Store the entire cacheUtils object for advanced usage
window.cacheUtils = {
  clearAllCache,
  clearLocalStorageCache,
  clearSessionStorageCache,
  clearBrowserCacheAndReload,
  clearAuthCache,
  clearFmeaDataCache,
  getCacheStatus
};

console.log(`
🚀 Cache clearing commands are now available in the console!

Available commands:
• clearAllCache() - Clear all cache and reload page
• clearAuthCache() - Clear authentication data only
• clearFmeaCache() - Clear FMEA data only
• clearBrowserCache() - Clear browser cache and reload
• getCacheStatus() - Show current cache status

Advanced usage:
• window.cacheUtils - Access all cache utility functions

Examples:
• clearAuthCache() - Quick auth reset
• clearAllCache() - Nuclear option (clears everything)
• getCacheStatus() - Check what's cached
`);

export {};
