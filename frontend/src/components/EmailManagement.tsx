import React, { useState, useEffect } from 'react';
import emailRepository from '../services/emailRepository';
import LocalStorageInfo from './LocalStorageInfo';

interface EmailRecord {
  email: string;
  name?: string;
  role?: string;
  addedDate: string;
  isActive: boolean;
}

const EmailManagement: React.FC = () => {
  const [emails, setEmails] = useState<EmailRecord[]>([]);
  const [newEmail, setNewEmail] = useState('');
  const [newName, setNewName] = useState('');
  const [newRole, setNewRole] = useState('User');
  const [showAddForm, setShowAddForm] = useState(false);
  const [stats, setStats] = useState({ total: 0, active: 0, inactive: 0 });

  useEffect(() => {
    loadEmails();
  }, []);

  const loadEmails = () => {
    const allEmails = emailRepository.getAllEmails();
    setEmails(allEmails);
    setStats(emailRepository.getStats());
  };

  const handleAddEmail = () => {
    if (emailRepository.addEmail(newEmail, newName, newRole)) {
      setNewEmail('');
      setNewName('');
      setNewRole('User');
      setShowAddForm(false);
      loadEmails();
    } else {
      alert('Failed to add email. It may already exist or be invalid.');
    }
  };

  const handleRemoveEmail = (email: string) => {
    if (window.confirm(`Are you sure you want to remove ${email}?`)) {
      if (emailRepository.removeEmail(email)) {
        loadEmails();
      }
    }
  };

  const handleExport = () => {
    const data = emailRepository.exportEmails();
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'authorized-emails.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (await emailRepository.loadFromFile(file)) {
        loadEmails();
        alert('Emails loaded from local file successfully!');
      } else {
        alert('Failed to load emails from file. Please check the file format.');
      }
    }
  };

  const handleSaveToLocalFolder = () => {
    emailRepository.saveToLocalFolder();
    alert(`Email list saved to Downloads folder as: ${emailRepository.getFileName()}`);
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Email Management</h1>
          <div className="flex space-x-3">
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
            >
              Add Email
            </button>
            <button
              onClick={handleSaveToLocalFolder}
              className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
            >
              Save to PC
            </button>
            <label className="bg-purple-300 text-gray-900 px-4 py-2 rounded-md hover:bg-purple-400 transition-colors cursor-pointer">
              Load from PC
              <input
                type="file"
                accept=".json"
                onChange={handleImport}
                className="hidden"
              />
            </label>
            <button
              onClick={handleExport}
              className="bg-orange-600 text-white px-4 py-2 rounded-md hover:bg-orange-700 transition-colors"
            >
              Export JSON
            </button>
          </div>
        </div>

        {/* Local Storage Info */}
        <LocalStorageInfo />

        {/* Statistics */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{stats.total}</div>
            <div className="text-sm text-blue-800">Total Emails</div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{stats.active}</div>
            <div className="text-sm text-green-800">Active</div>
          </div>
          <div className="bg-red-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-red-600">{stats.inactive}</div>
            <div className="text-sm text-red-800">Inactive</div>
          </div>
        </div>

        {/* Add Email Form */}
        {showAddForm && (
          <div className="bg-gray-50 p-4 rounded-lg mb-6">
            <h3 className="text-lg font-semibold mb-4">Add New Email</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <input
                type="email"
                placeholder="Email address"
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="text"
                placeholder="Name (optional)"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <select
                value={newRole}
                onChange={(e) => setNewRole(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="User">User</option>
                <option value="Engineer">Engineer</option>
                <option value="Manager">Manager</option>
                <option value="Admin">Admin</option>
              </select>
            </div>
            <div className="flex space-x-3 mt-4">
              <button
                onClick={handleAddEmail}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
              >
                Add Email
              </button>
              <button
                onClick={() => setShowAddForm(false)}
                className="bg-gray-500 text-white px-4 py-2 rounded-md hover:bg-gray-600 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Email List */}
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Added Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {emails.map((emailRecord, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {emailRecord.email}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {emailRecord.name || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      emailRecord.role === 'Admin' ? 'bg-red-100 text-red-800' :
                      emailRecord.role === 'Manager' ? 'bg-yellow-100 text-yellow-800' :
                      emailRecord.role === 'Engineer' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {emailRecord.role}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(emailRecord.addedDate).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      emailRecord.isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {emailRecord.isActive ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <button
                      onClick={() => handleRemoveEmail(emailRecord.email)}
                      className="text-red-600 hover:text-red-900 font-medium"
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {emails.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No authorized emails found. Add some emails to get started.
          </div>
        )}
      </div>
    </div>
  );
};

export default EmailManagement;
