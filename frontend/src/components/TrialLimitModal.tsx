import React from 'react';

interface TrialLimitModalProps {
  isOpen: boolean;
  onClose: () => void;
  userEmail: string;
  remainingGenerations: number;
  dailyLimit: number;
}

const TrialLimitModal: React.FC<TrialLimitModalProps> = ({
  isOpen,
  onClose,
  userEmail,
  remainingGenerations,
  dailyLimit
}) => {
  if (!isOpen) return null;

  const formatResetTime = () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(0, 0, 0, 0);
    const now = new Date();
    const diffMs = tomorrow.getTime() - now.getTime();
    const diffHours = Math.ceil(diffMs / (1000 * 60 * 60));
    
    if (diffHours < 1) {
      const diffMinutes = Math.ceil(diffMs / (1000 * 60));
      return `${diffMinutes} minutes`;
    }
    return `${diffHours} hours`;
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-2/3 lg:w-1/2 shadow-lg rounded-md bg-white">
        <div className="mt-3">
          {/* Header */}
          <div className="flex items-center justify-center mb-4">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
              <span className="text-4xl">🚫</span>
            </div>
          </div>

          <div className="text-center">
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              Trial Limit Reached
            </h3>
            <p className="text-gray-600 mb-6">
              You've used all {dailyLimit} AI generations for today.
            </p>
          </div>

          {/* Usage Summary */}
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-red-600 mb-2">
                {dailyLimit - remainingGenerations} / {dailyLimit}
              </div>
              <div className="text-sm text-gray-600 mb-3">AI Generations Used Today</div>
              
              {/* Progress Bar */}
              <div className="w-full bg-gray-200 rounded-full h-3 mb-3">
                <div
                  className="bg-red-500 h-3 rounded-full transition-all duration-300"
                  style={{ width: '100%' }}
                ></div>
              </div>
              
              <div className="text-xs text-gray-500">
                Resets in: {formatResetTime()}
              </div>
            </div>
          </div>

          {/* Trial Information */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <h4 className="font-semibold text-blue-900 mb-2">📋 Trial Information</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Trial users get {dailyLimit} AI generations per day</li>
              <li>• Usage resets at midnight every day</li>
              <li>• Admin users have unlimited access</li>
              <li>• Contact your administrator for additional access</li>
            </ul>
          </div>

          {/* Contact Information */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <h4 className="font-semibold text-yellow-900 mb-2">📞 Need More Access?</h4>
            <div className="text-sm text-yellow-800">
              <p className="mb-2">
                Contact your administrator to request:
              </p>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li>Additional daily generations</li>
                <li>Unlimited access</li>
                <li>Admin privileges</li>
              </ul>
            </div>
          </div>

          {/* Admin Contact */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <h4 className="font-semibold text-green-900 mb-2">👑 Administrator Contact</h4>
            <div className="text-sm text-green-800">
              <p className="mb-2">
                <strong>Primary Admin:</strong> john@fotonconsulting.com
              </p>
              <p>
                <strong>System Admin:</strong> admin@foton.com
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-center space-x-4">
            <button
              onClick={onClose}
              className="bg-gray-600 text-white px-6 py-2 rounded-md hover:bg-gray-700 transition-colors"
            >
              Close
            </button>
            <button
              onClick={() => {
                // In a real app, this would open an email client or contact form
                window.open(`mailto:john@fotonconsulting.com?subject=Request for Additional AI Access&body=Hello, I would like to request additional AI generations for my account (${userEmail}). Please let me know about available options.`, '_blank');
              }}
              className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors"
            >
              Contact Admin
            </button>
          </div>

          {/* Footer */}
          <div className="mt-6 text-center text-xs text-gray-500">
            <p>
              This is a trial version of the Foton aiQMS system.<br />
              For full access, please contact your administrator.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrialLimitModal;
