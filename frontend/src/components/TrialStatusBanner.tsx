import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import usageTrackingService from '../services/usageTrackingService';

const TrialStatusBanner: React.FC = () => {
  const { user } = useAuth();
  const [trialStatus, setTrialStatus] = useState<any>(null);
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    if (user) {
      const status = usageTrackingService.getTrialStatus(user.email);
      setTrialStatus(status);
    }
  }, [user]);

  if (!user || !trialStatus || !isVisible) {
    return null;
  }

  const getStatusColor = () => {
    if (!trialStatus.isTrialUser) {
      return 'bg-green-100 border-green-200 text-green-800';
    }
    if (trialStatus.isLimitReached) {
      return 'bg-red-100 border-red-200 text-red-800';
    }
    if (trialStatus.remainingToday <= 2) {
      return 'bg-yellow-100 border-yellow-200 text-yellow-800';
    }
    return 'bg-blue-100 border-blue-200 text-blue-800';
  };

  const getStatusIcon = () => {
    if (!trialStatus.isTrialUser) {
      return '👑';
    }
    if (trialStatus.isLimitReached) {
      return '🚫';
    }
    if (trialStatus.remainingToday <= 2) {
      return '⚠️';
    }
    return '✅';
  };

  const getProgressPercentage = () => {
    if (!trialStatus.isTrialUser) {
      return 100;
    }
    return (trialStatus.usedToday / trialStatus.dailyLimit) * 100;
  };

  const formatResetTime = (resetTime: string) => {
    const resetDate = new Date(resetTime);
    const now = new Date();
    const diffMs = resetDate.getTime() - now.getTime();
    const diffHours = Math.ceil(diffMs / (1000 * 60 * 60));
    
    if (diffHours < 1) {
      const diffMinutes = Math.ceil(diffMs / (1000 * 60));
      return `${diffMinutes} minutes`;
    }
    return `${diffHours} hours`;
  };

  return (
    <div className={`border-l-4 p-4 mb-4 rounded-r-lg ${getStatusColor()}`}>
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <span className="text-2xl">{getStatusIcon()}</span>
        </div>
        <div className="ml-3 flex-1">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium">
              {trialStatus.isTrialUser ? 'Trial Usage Status' : 'Admin Access'}
            </h3>
            <button
              onClick={() => setIsVisible(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div className="mt-2">
            {trialStatus.isTrialUser ? (
              <div>
                <p className="text-sm">
                  {trialStatus.isLimitReached ? (
                    <span className="font-semibold">
                      Trial limit reached! You've used all {trialStatus.dailyLimit} AI generations for today.
                    </span>
                  ) : (
                    <span>
                      You have <span className="font-semibold">{trialStatus.remainingToday}</span> AI generations remaining today.
                    </span>
                  )}
                </p>
                
                {/* Progress Bar */}
                <div className="mt-2">
                  <div className="flex justify-between text-xs mb-1">
                    <span>Used: {trialStatus.usedToday}/{trialStatus.dailyLimit}</span>
                    <span>Resets in: {formatResetTime(trialStatus.resetTime)}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-300 ${
                        trialStatus.isLimitReached 
                          ? 'bg-red-500' 
                          : trialStatus.remainingToday <= 2 
                            ? 'bg-yellow-500' 
                            : 'bg-blue-500'
                      }`}
                      style={{ width: `${Math.min(getProgressPercentage(), 100)}%` }}
                    ></div>
                  </div>
                </div>

                {trialStatus.isLimitReached && (
                  <div className="mt-3 p-3 bg-red-50 rounded-md border border-red-200">
                    <p className="text-sm font-medium text-red-800">
                      🚫 Daily trial limit reached
                    </p>
                    <p className="text-xs text-red-600 mt-1">
                      Contact your administrator for additional or unlimited access.
                    </p>
                  </div>
                )}

                {!trialStatus.isLimitReached && trialStatus.remainingToday <= 2 && (
                  <div className="mt-3 p-3 bg-yellow-50 rounded-md border border-yellow-200">
                    <p className="text-sm font-medium text-yellow-800">
                      ⚠️ Warning: Low usage remaining
                    </p>
                    <p className="text-xs text-yellow-600 mt-1">
                      Consider contacting your administrator for additional access.
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div>
                <p className="text-sm font-semibold">
                  You have unlimited AI generations as an admin user.
                </p>
                <p className="text-xs mt-1 opacity-75">
                  Admin users are not subject to trial limits.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrialStatusBanner;
