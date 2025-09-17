import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import usageTrackingService from '../services/usageTrackingService';

interface UsageRecord {
  userEmail: string;
  date: string;
  aiGenerations: number;
  lastReset: string;
}

interface UserUsageSummary {
  userEmail: string;
  totalGenerations: number;
  todayGenerations: number;
  isTrialUser: boolean;
  isLimitReached: boolean;
  lastActive: string;
}

const UsageDashboard: React.FC = () => {
  const { user } = useAuth();
  const [userUsage, setUserUsage] = useState<{ [userEmail: string]: UsageRecord[] }>({});
  const [userSummaries, setUserSummaries] = useState<UserUsageSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState<string | null>(null);

  useEffect(() => {
    loadUsageData();
  }, []);

  const loadUsageData = () => {
    const allUsage = usageTrackingService.getAllUsersUsage();
    setUserUsage(allUsage);

    // Create user summaries
    const summaries: UserUsageSummary[] = Object.keys(allUsage).map(userEmail => {
      const records = allUsage[userEmail];
      const today = new Date().toISOString().split('T')[0];
      const todayRecord = records.find(r => r.date === today);
      const totalGenerations = records.reduce((sum, record) => sum + record.aiGenerations, 0);
      const todayGenerations = todayRecord ? todayRecord.aiGenerations : 0;
      const trialStatus = usageTrackingService.getTrialStatus(userEmail);
      const lastActive = records.length > 0 ? records[0].lastReset : 'Never';

      return {
        userEmail,
        totalGenerations,
        todayGenerations,
        isTrialUser: trialStatus.isTrialUser,
        isLimitReached: trialStatus.isLimitReached,
        lastActive
      };
    });

    // Sort by total generations (descending)
    summaries.sort((a, b) => b.totalGenerations - a.totalGenerations);
    setUserSummaries(summaries);
    setIsLoading(false);
  };

  const resetUserUsage = (userEmail: string) => {
    if (window.confirm(`Reset daily usage for ${userEmail}?`)) {
      usageTrackingService.resetDailyUsage(userEmail);
      loadUsageData();
    }
  };

  const cleanupOldData = () => {
    if (window.confirm('Clean up usage data older than 90 days?')) {
      usageTrackingService.cleanupOldData();
      loadUsageData();
    }
  };

  const getStatusColor = (summary: UserUsageSummary) => {
    if (!summary.isTrialUser) {
      return 'bg-green-100 text-green-800';
    }
    if (summary.isLimitReached) {
      return 'bg-red-100 text-red-800';
    }
    return 'bg-blue-100 text-blue-800';
  };

  const getStatusText = (summary: UserUsageSummary) => {
    if (!summary.isTrialUser) {
      return 'Admin';
    }
    if (summary.isLimitReached) {
      return 'Limit Reached';
    }
    return 'Active';
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Usage Dashboard</h1>
          <div className="flex space-x-3">
            <button
              onClick={loadUsageData}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
            >
              Refresh
            </button>
            <button
              onClick={cleanupOldData}
              className="bg-yellow-600 text-white px-4 py-2 rounded-md hover:bg-yellow-700 transition-colors"
            >
              Cleanup Old Data
            </button>
          </div>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-blue-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-blue-600">{userSummaries.length}</div>
            <div className="text-sm text-blue-800">Total Users</div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-green-600">
              {userSummaries.filter(u => !u.isTrialUser).length}
            </div>
            <div className="text-sm text-green-800">Admin Users</div>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-purple-600">
              {userSummaries.reduce((sum, u) => sum + u.todayGenerations, 0)}
            </div>
            <div className="text-sm text-purple-800">Today's Generations</div>
          </div>
          <div className="bg-red-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-red-600">
              {userSummaries.filter(u => u.isLimitReached).length}
            </div>
            <div className="text-sm text-red-800">Users at Limit</div>
          </div>
        </div>

        {/* User Usage Table */}
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Today's Usage
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total Usage
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Active
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {userSummaries.map((summary) => (
                <tr key={summary.userEmail} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                        <span className="text-blue-600 font-semibold text-sm">
                          {summary.userEmail.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {summary.userEmail}
                        </div>
                        <div className="text-sm text-gray-500">
                          {summary.isTrialUser ? 'Trial User' : 'Admin User'}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(summary)}`}>
                      {getStatusText(summary)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {summary.todayGenerations}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {summary.totalGenerations}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(summary.lastActive).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => setSelectedUser(summary.userEmail)}
                      className="text-blue-600 hover:text-blue-900 mr-3"
                    >
                      View Details
                    </button>
                    <button
                      onClick={() => resetUserUsage(summary.userEmail)}
                      className="text-yellow-600 hover:text-yellow-900"
                    >
                      Reset Today
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* User Details Modal */}
        {selectedUser && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
              <div className="mt-3">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    Usage Details: {selectedUser}
                  </h3>
                  <button
                    onClick={() => setSelectedUser(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                
                <div className="space-y-4">
                  {userUsage[selectedUser]?.map((record, index) => (
                    <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <div>
                        <div className="font-medium">{record.date}</div>
                        <div className="text-sm text-gray-500">
                          Last reset: {new Date(record.lastReset).toLocaleString()}
                        </div>
                      </div>
                      <div className="text-lg font-semibold text-blue-600">
                        {record.aiGenerations} generations
                      </div>
                    </div>
                  ))}
                  
                  {(!userUsage[selectedUser] || userUsage[selectedUser].length === 0) && (
                    <div className="text-center py-8 text-gray-500">
                      No usage data found for this user.
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UsageDashboard;
