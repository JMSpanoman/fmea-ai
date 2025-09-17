import React from 'react';

const LocalStorageInfo: React.FC = () => {
  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3">
          <h3 className="text-sm font-medium text-blue-800">
            💾 Local PC Folder Storage
          </h3>
          <div className="mt-2 text-sm text-blue-700">
            <p className="mb-2">
              <strong>How it works:</strong> Your email list is automatically saved to your PC's Downloads folder whenever you make changes.
            </p>
            <ul className="list-disc list-inside space-y-1">
              <li><strong>Auto-save:</strong> Every time you add/remove an email, a new file is downloaded</li>
              <li><strong>File format:</strong> JSON files with names like <code>authorized-emails-2024-01-15.json</code></li>
              <li><strong>Load from PC:</strong> Use "Load from PC" to restore emails from a previous file</li>
              <li><strong>Backup:</strong> Keep multiple versions in your Downloads folder for safety</li>
            </ul>
            <p className="mt-2 text-xs text-blue-600">
              💡 <strong>Tip:</strong> Create a dedicated folder like "FMEA-Emails" in your Downloads to organize your email files.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LocalStorageInfo;
