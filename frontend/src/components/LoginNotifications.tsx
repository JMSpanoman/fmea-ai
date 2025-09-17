import React, { useState, useEffect } from 'react';
import emailNotificationService from '../services/emailNotificationService';

interface LoginNotification {
  userEmail: string;
  userName: string;
  userRole: string;
  loginTime: string;
  ipAddress?: string;
  userAgent?: string;
}

const LoginNotifications: React.FC = () => {
  const [notifications, setNotifications] = useState<LoginNotification[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = () => {
    const storedNotifications = emailNotificationService.getStoredNotifications();
    setNotifications(storedNotifications);
    setIsLoading(false);
  };

  const clearOldNotifications = () => {
    emailNotificationService.clearOldNotifications();
    loadNotifications();
  };

  const clearAllNotifications = () => {
    if (window.confirm('Are you sure you want to clear all login notifications?')) {
      localStorage.removeItem('loginNotifications');
      loadNotifications();
    }
  };

  const formatTime = (timeString: string) => {
    return new Date(timeString).toLocaleString();
  };

  const getRoleColor = (role: string) => {
    switch (role.toLowerCase()) {
      case 'admin':
        return 'bg-red-100 text-red-800';
      case 'manager':
        return 'bg-purple-100 text-purple-800';
      case 'engineer':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Login Notifications</h1>
          <div className="flex space-x-3">
            <button
              onClick={clearOldNotifications}
              className="bg-yellow-600 text-white px-4 py-2 rounded-md hover:bg-yellow-700 transition-colors"
            >
              Clear Old (7+ days)
            </button>
            <button
              onClick={clearAllNotifications}
              className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
            >
              Clear All
            </button>
            <button
              onClick={loadNotifications}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
            >
              Refresh
            </button>
          </div>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-blue-600">{notifications.length}</div>
            <div className="text-sm text-blue-800">Total Logins</div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-green-600">
              {notifications.filter(n => new Date(n.loginTime) > new Date(Date.now() - 24 * 60 * 60 * 1000)).length}
            </div>
            <div className="text-sm text-green-800">Last 24 Hours</div>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-purple-600">
              {new Set(notifications.map(n => n.userEmail)).size}
            </div>
            <div className="text-sm text-purple-800">Unique Users</div>
          </div>
        </div>

        {/* Notifications List */}
        {notifications.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 text-6xl mb-4">📧</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Login Notifications</h3>
            <p className="text-gray-500">Login notifications will appear here when users sign in.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {notifications.map((notification, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-blue-600 font-semibold text-sm">
                          {notification.userName.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{notification.userName}</h3>
                        <p className="text-sm text-gray-600">{notification.userEmail}</p>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getRoleColor(notification.userRole)}`}>
                        {notification.userRole}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                      <div>
                        <span className="font-medium">Login Time:</span>
                        <br />
                        {formatTime(notification.loginTime)}
                      </div>
                      {notification.ipAddress && (
                        <div>
                          <span className="font-medium">IP Address:</span>
                          <br />
                          {notification.ipAddress}
                        </div>
                      )}
                      <div>
                        <span className="font-medium">Status:</span>
                        <br />
                        <span className="text-green-600 font-medium">✅ Successful</span>
                      </div>
                    </div>

                    {notification.userAgent && (
                      <div className="mt-3 p-2 bg-gray-100 rounded text-xs text-gray-600">
                        <span className="font-medium">User Agent:</span> {notification.userAgent}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Footer Info */}
        <div className="mt-8 p-4 bg-blue-50 rounded-lg">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">
                📧 Email Notifications
              </h3>
              <div className="mt-2 text-sm text-blue-700">
                <p>
                  <strong>Admin Email:</strong> john@fotonconsulting.com receives detailed login notifications.
                </p>
                <p className="mt-1">
                  <strong>Note:</strong> In production, these notifications would be sent via email. Currently, they are logged to the console and stored locally for review.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginNotifications;
