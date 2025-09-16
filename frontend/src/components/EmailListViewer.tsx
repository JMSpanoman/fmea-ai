import React, { useState, useEffect } from 'react';
import emailRepository from '../services/emailRepository';

interface EmailRecord {
  email: string;
  name?: string;
  role?: string;
  addedDate: string;
  isActive: boolean;
}

const EmailListViewer: React.FC = () => {
  const [emails, setEmails] = useState<EmailRecord[]>([]);
  const [stats, setStats] = useState({ total: 0, active: 0, inactive: 0 });

  useEffect(() => {
    loadEmails();
  }, []);

  const loadEmails = () => {
    const allEmails = emailRepository.getAllEmails();
    setEmails(allEmails);
    setStats(emailRepository.getStats());
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert('Email list copied to clipboard!');
  };

  const exportAsText = () => {
    const emailList = emails.map(email => email.email).join('\n');
    const blob = new Blob([emailList], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'authorized-emails.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Authorized Email List</h1>
          <div className="flex space-x-3">
            <button
              onClick={() => copyToClipboard(emails.map(e => e.email).join('\n'))}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
            >
              Copy List
            </button>
            <button
              onClick={exportAsText}
              className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
            >
              Export as Text
            </button>
          </div>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-blue-600">{stats.total}</div>
            <div className="text-sm text-blue-800">Total Emails</div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-green-600">{stats.active}</div>
            <div className="text-sm text-green-800">Active</div>
          </div>
          <div className="bg-red-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-red-600">{stats.inactive}</div>
            <div className="text-sm text-red-800">Inactive</div>
          </div>
        </div>

        {/* Email List */}
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">All Authorized Emails:</h3>
          {emails.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No authorized emails found.
            </div>
          ) : (
            <div className="space-y-2">
              {emails.map((emailRecord, index) => (
                <div
                  key={index}
                  className={`p-4 rounded-lg border-l-4 ${
                    emailRecord.isActive
                      ? 'bg-green-50 border-green-400'
                      : 'bg-red-50 border-red-400'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <span className="text-lg font-medium text-gray-900">
                          {emailRecord.email}
                        </span>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          emailRecord.role === 'Admin' ? 'bg-red-100 text-red-800' :
                          emailRecord.role === 'Manager' ? 'bg-yellow-100 text-yellow-800' :
                          emailRecord.role === 'Engineer' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {emailRecord.role}
                        </span>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          emailRecord.isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {emailRecord.isActive ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                      {emailRecord.name && (
                        <div className="text-sm text-gray-600 mt-1">
                          {emailRecord.name}
                        </div>
                      )}
                      <div className="text-xs text-gray-500 mt-1">
                        Added: {new Date(emailRecord.addedDate).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Simple Text List */}
        <div className="mt-8 p-4 bg-gray-50 rounded-lg">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Simple Email List (for copying):</h4>
          <div className="text-sm text-gray-600 font-mono bg-white p-3 rounded border">
            {emails.map(email => email.email).join('\n')}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailListViewer;
