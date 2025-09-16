import React, { useState, useEffect } from 'react';

interface VersionInfo {
  id: number;
  version_number: string;
  version_label: string;
  version_status: string;
  change_summary: string;
  created_at: string;
  created_by: string;
  approval_required: boolean;
  approved_by?: string;
  approved_at?: string;
}

interface ExportInfo {
  id: number;
  document_type: string;
  document_id: number;
  version_number: string;
  export_format: string;
  export_filename: string;
  exported_at: string;
  export_file_size?: number;
  export_hash?: string;
}

interface VersionControlPanelProps {
  documentType: string;
  documentId: number;
  projectId: number;
  currentVersion?: string;
  onVersionChange?: (version: string) => void;
  onExport?: (format: string, version: string) => void;
}

const VersionControlPanel: React.FC<VersionControlPanelProps> = ({
  documentType,
  documentId,
  projectId,
  currentVersion = "1.0",
  onVersionChange,
  onExport
}) => {
  const [activeTab, setActiveTab] = useState<'versions' | 'exports' | 'compare'>('versions');
  const [versions, setVersions] = useState<VersionInfo[]>([]);
  const [exports, setExports] = useState<ExportInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedVersions, setSelectedVersions] = useState<number[]>([]);
  const [comparisonResult, setComparisonResult] = useState<any>(null);
  const [newVersionData, setNewVersionData] = useState({
    change_summary: '',
    change_type: 'patch',
    approval_required: false
  });

  // Mock data for demonstration - replace with actual API calls
  useEffect(() => {
    loadVersions();
    loadExports();
  }, [documentType, documentId, projectId]);

  const loadVersions = async () => {
    setLoading(true);
    try {
      // Mock API call - replace with actual implementation
      const mockVersions: VersionInfo[] = [
        {
          id: 1,
          version_number: "1.0",
          version_label: "Draft",
          version_status: "draft",
          change_summary: "Initial version",
          created_at: new Date().toISOString(),
          created_by: "john.smith@foton.com",
          approval_required: false
        },
        {
          id: 2,
          version_number: "1.1",
          version_label: "Review",
          version_status: "review",
          change_summary: "Updated component analysis",
          created_at: new Date(Date.now() - 86400000).toISOString(),
          created_by: "john.smith@foton.com",
          approval_required: true
        }
      ];
      setVersions(mockVersions);
    } catch (error) {
      console.error('Failed to load versions:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadExports = async () => {
    try {
      // Mock API call - replace with actual implementation
      const mockExports: ExportInfo[] = [
        {
          id: 1,
          document_type: documentType,
          document_id: documentId,
          version_number: "1.0",
          export_format: "pdf",
          export_filename: `${documentType}_v1.0_${new Date().toISOString().split('T')[0]}.pdf`,
          exported_at: new Date().toISOString(),
          export_file_size: 1024000,
          export_hash: "abc123..."
        }
      ];
      setExports(mockExports);
    } catch (error) {
      console.error('Failed to load exports:', error);
    }
  };

  const handleVersionSelect = (versionId: number) => {
    setSelectedVersions(prev => 
      prev.includes(versionId) 
        ? prev.filter(id => id !== versionId)
        : [...prev, versionId]
    );
  };

  const handleCompareVersions = async () => {
    if (selectedVersions.length !== 2) {
      alert('Please select exactly 2 versions to compare');
      return;
    }

    try {
      // Mock API call - replace with actual implementation
      const mockComparison = {
        added: { "new_field": "New value" },
        modified: { "existing_field": { old: "Old value", new: "New value" } },
        deleted: { "removed_field": "Removed value" },
        summary: {
          version1: versions.find(v => v.id === selectedVersions[0])?.version_number,
          version2: versions.find(v => v.id === selectedVersions[1])?.version_number,
          change_summary: "Updated analysis and added new fields",
          changed_by: "john.smith@foton.com",
          changed_at: new Date().toISOString()
        }
      };
      setComparisonResult(mockComparison);
      setActiveTab('compare');
    } catch (error) {
      console.error('Failed to compare versions:', error);
    }
  };

  const handleCreateVersion = async () => {
    if (!newVersionData.change_summary.trim()) {
      alert('Please provide a change summary');
      return;
    }

    try {
      // Mock API call - replace with actual implementation
      const newVersion: VersionInfo = {
        id: versions.length + 1,
        version_number: "1.2",
        version_label: "Draft",
        version_status: "draft",
        change_summary: newVersionData.change_summary,
        created_at: new Date().toISOString(),
        created_by: "john.smith@foton.com",
        approval_required: newVersionData.approval_required
      };

      setVersions(prev => [newVersion, ...prev]);
      setNewVersionData({ change_summary: '', change_type: 'patch', approval_required: false });
      alert('New version created successfully');
    } catch (error) {
      console.error('Failed to create version:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'bg-gray-100 text-gray-800';
      case 'review': return 'bg-yellow-100 text-yellow-800';
      case 'approved': return 'bg-green-100 text-green-800';
      case 'published': return 'bg-blue-100 text-blue-800';
      case 'superseded': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getVersionColor = (version: string) => {
    const [major, minor] = version.split('.').map(Number);
    if (major > 1) return 'bg-red-100 text-red-800';
    if (minor > 0) return 'bg-yellow-100 text-yellow-800';
    return 'bg-green-100 text-green-800';
  };

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Version Control</h3>
            <p className="text-sm text-gray-500">
              {documentType.toUpperCase()} - Project {projectId}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">Current:</span>
            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getVersionColor(currentVersion)}`}>
              v{currentVersion}
            </span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8 px-6">
          <button
            onClick={() => setActiveTab('versions')}
            className={`py-3 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'versions'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Versions ({versions.length})
          </button>
          <button
            onClick={() => setActiveTab('exports')}
            className={`py-3 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'exports'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Exports ({exports.length})
          </button>
          <button
            onClick={() => setActiveTab('compare')}
            className={`py-3 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'compare'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Compare
          </button>
        </nav>
      </div>

      {/* Content */}
      <div className="p-6">
        {activeTab === 'versions' && (
          <div className="space-y-4">
            {/* Create New Version */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="text-sm font-medium text-gray-900 mb-3">Create New Version</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Change Summary
                  </label>
                  <input
                    type="text"
                    value={newVersionData.change_summary}
                    onChange={(e) => setNewVersionData(prev => ({ ...prev, change_summary: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Describe changes..."
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Change Type
                  </label>
                  <select
                    value={newVersionData.change_type}
                    onChange={(e) => setNewVersionData(prev => ({ ...prev, change_type: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="patch">Patch</option>
                    <option value="minor">Minor</option>
                    <option value="major">Major</option>
                  </select>
                </div>
                <div className="flex items-center">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={newVersionData.approval_required}
                      onChange={(e) => setNewVersionData(prev => ({ ...prev, approval_required: e.target.checked }))}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-xs text-gray-700">Requires Approval</span>
                  </label>
                </div>
              </div>
              <div className="mt-3">
                <button
                  onClick={handleCreateVersion}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  Create Version
                </button>
              </div>
            </div>

            {/* Version List */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-medium text-gray-900">Version History</h4>
                <button
                  onClick={handleCompareVersions}
                  disabled={selectedVersions.length !== 2}
                  className={`px-3 py-1 text-xs rounded-md ${
                    selectedVersions.length === 2
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  }`}
                >
                  Compare Selected
                </button>
              </div>
              
              <div className="space-y-3">
                {versions.map((version) => (
                  <div
                    key={version.id}
                    className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                      selectedVersions.includes(version.id)
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => handleVersionSelect(version.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <input
                          type="checkbox"
                          checked={selectedVersions.includes(version.id)}
                          onChange={() => handleVersionSelect(version.id)}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <div>
                          <div className="flex items-center space-x-2">
                            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getVersionColor(version.version_number)}`}>
                              v{version.version_number}
                            </span>
                            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(version.version_status)}`}>
                              {version.version_status}
                            </span>
                            {version.approval_required && (
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                                Approval Required
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-900 mt-1">{version.change_summary}</p>
                        </div>
                      </div>
                      <div className="text-right text-xs text-gray-500">
                        <div>{version.created_by}</div>
                        <div>{new Date(version.created_at).toLocaleDateString()}</div>
                        {version.approved_by && (
                          <div className="text-green-600">
                            Approved by {version.approved_by}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'exports' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-medium text-gray-900">Export History</h4>
              <button
                onClick={() => onExport?.('pdf', currentVersion)}
                className="bg-green-600 text-white px-4 py-2 rounded-md text-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                Export Current Version
              </button>
            </div>
            
            <div className="space-y-3">
              {exports.map((export_item) => (
                <div key={export_item.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        export_item.export_format === 'pdf' ? 'bg-red-100 text-red-800' :
                        export_item.export_format === 'word' ? 'bg-blue-100 text-blue-800' :
                        export_item.export_format === 'excel' ? 'bg-green-100 text-green-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {export_item.export_format.toUpperCase()}
                      </span>
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getVersionColor(export_item.version_number)}`}>
                        v{export_item.version_number}
                      </span>
                      <div>
                        <div className="text-sm font-medium text-gray-900">{export_item.export_filename}</div>
                        <div className="text-xs text-gray-500">
                          {export_item.export_file_size && `${(export_item.export_file_size / 1024).toFixed(1)} KB`}
                          {export_item.export_hash && ` • Hash: ${export_item.export_hash.substring(0, 8)}...`}
                        </div>
                      </div>
                    </div>
                    <div className="text-right text-xs text-gray-500">
                      <div>{new Date(export_item.exported_at).toLocaleDateString()}</div>
                      <div>{new Date(export_item.exported_at).toLocaleTimeString()}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'compare' && (
          <div className="space-y-4">
            <h4 className="text-sm font-medium text-gray-900">Version Comparison</h4>
            
            {comparisonResult ? (
              <div className="space-y-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h5 className="text-sm font-medium text-blue-900 mb-2">Comparison Summary</h5>
                  <div className="text-sm text-blue-800">
                    <div>Comparing v{comparisonResult.summary.version1} → v{comparisonResult.summary.version2}</div>
                    <div>Changed by: {comparisonResult.summary.changed_by}</div>
                    <div>Change Summary: {comparisonResult.summary.change_summary}</div>
                  </div>
                </div>

                {Object.keys(comparisonResult.added).length > 0 && (
                  <div className="bg-green-50 p-4 rounded-lg">
                    <h5 className="text-sm font-medium text-green-900 mb-2">Added Fields</h5>
                    <div className="space-y-1">
                      {Object.entries(comparisonResult.added).map(([key, value]) => (
                        <div key={key} className="text-sm text-green-800">
                          <span className="font-medium">{key}:</span> {String(value)}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {Object.keys(comparisonResult.modified).length > 0 && (
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <h5 className="text-sm font-medium text-yellow-900 mb-2">Modified Fields</h5>
                    <div className="space-y-1">
                      {Object.entries(comparisonResult.modified).map(([key, value]: [string, any]) => (
                        <div key={key} className="text-sm text-yellow-800">
                          <span className="font-medium">{key}:</span>
                          <div className="ml-4">
                            <div className="line-through text-red-600">{value.old}</div>
                            <div className="text-green-600">{value.new}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {Object.keys(comparisonResult.deleted).length > 0 && (
                  <div className="bg-red-50 p-4 rounded-lg">
                    <h5 className="text-sm font-medium text-red-900 mb-2">Deleted Fields</h5>
                    <div className="space-y-1">
                      {Object.entries(comparisonResult.deleted).map(([key, value]) => (
                        <div key={key} className="text-sm text-red-800">
                          <span className="font-medium">{key}:</span> {String(value)}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8">
                <p>Select two versions to compare their differences</p>
                <p className="text-sm mt-1">Go to the Versions tab to select versions</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default VersionControlPanel;
