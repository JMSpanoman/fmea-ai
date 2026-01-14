import React, { useState, useEffect } from 'react';

interface TemplateInfo {
  filename: string;
  size: number;
  upload_date: string;
  template_type: string;
}

interface TemplateManagerProps {
  onTemplateSelect?: (template: TemplateInfo) => void;
  showUpload?: boolean;
  showList?: boolean;
  showActions?: boolean;
}

const TemplateManager: React.FC<TemplateManagerProps> = ({
  onTemplateSelect,
  showUpload = true,
  showList = true,
  showActions = true
}) => {
  const [templates, setTemplates] = useState<TemplateInfo[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [templateType, setTemplateType] = useState('risk_management_report');
  const [isUploading, setIsUploading] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error' | ''>('');

  const createSampleTemplate = async () => {
    try {
      // Create a simple sample template content
      const sampleContent = `
Risk Management Report Template

Project: {{ project_name }}
Report Type: {{ report_type }}
Reporting Period: {{ reporting_period }}
Generation Date: {{ generation_date }}

Executive Summary:
{{ executive_summary }}

Risk Overview:
{{ risk_overview }}

Risk Assessment Results:
{{ risk_assessment }}

Risk Response Status:
{{ risk_response }}

Key Findings:
{{ key_findings }}

Recommendations:
{{ recommendations }}

Report Data:
{% for item in report_data %}
Section: {{ item.report_section }}
Content: {{ item.section_content }}
Risk Metrics: {{ item.risk_metrics }}
Risk Trends: {{ item.risk_trends }}
Risk Incidents: {{ item.risk_incidents }}
Compliance Status: {{ item.compliance_status }}
Action Items: {{ item.action_items }}
Responsible Party: {{ item.responsible_party }}
Target Completion Date: {{ item.target_completion_date }}
Status: {{ item.status }}
Report Owner: {{ item.report_owner }}
Last Updated: {{ item.last_updated }}
Version: {{ item.version }}

{% endfor %}
      `.trim();

      // Create a blob with the template content
      const blob = new Blob([sampleContent], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'Risk_Management_Report_Template.txt';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setMessage('Sample template downloaded. Convert to .docx format and upload.');
      setMessageType('success');
    } catch (error) {
      console.error('Error creating sample template:', error);
      setMessage('Failed to create sample template');
      setMessageType('error');
    }
  };

  const templateTypes = [
    { key: 'risk_management_report', label: 'Risk Management Report' },
    { key: 'fmea_report', label: 'FMEA Report' },
    { key: 'hazard_analysis', label: 'Hazard Analysis' },
    { key: 'risk_evaluation', label: 'Risk Evaluation' },
    { key: 'general', label: 'General' }
  ];

  useEffect(() => {
    if (showList) {
      loadTemplates();
    }
  }, [showList]);

  const loadTemplates = async () => {
    setIsLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/templates/list', {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      });
      if (response.ok) {
        const data = await response.json();
        setTemplates(data);
      } else {
        throw new Error('Failed to load templates');
      }
    } catch (error) {
      console.error('Error loading templates:', error);
      setMessage('Failed to load templates');
      setMessageType('error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.name.toLowerCase().endsWith('.docx') && !file.name.toLowerCase().endsWith('.doc')) {
        setMessage('Please select a Word document (.docx or .doc)');
        setMessageType('error');
        return;
      }
      
      // Validate file size (10MB)
      if (file.size > 10 * 1024 * 1024) {
        setMessage('File size must be less than 10MB');
        setMessageType('error');
        return;
      }
      
      setSelectedFile(file);
      setMessage('');
      setMessageType('');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setMessage('Please select a file to upload');
      setMessageType('error');
      return;
    }

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('template_type', templateType);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/templates/upload', {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setMessage(data.message);
        setMessageType('success');
        setSelectedFile(null);
        if (showList) {
          loadTemplates();
        }
        // Reset file input
        const fileInput = document.getElementById('template-file') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      setMessage(error instanceof Error ? error.message : 'Upload failed');
      setMessageType('error');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDownload = async (filename: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/templates/download/${filename}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        throw new Error('Download failed');
      }
    } catch (error) {
      console.error('Download error:', error);
      setMessage('Failed to download template');
      setMessageType('error');
    }
  };

  const handleDelete = async (filename: string) => {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/templates/delete/${filename}`, {
        method: 'DELETE',
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      });

      if (response.ok) {
        setMessage('Template deleted successfully');
        setMessageType('success');
        if (showList) {
          loadTemplates();
        }
      } else {
        throw new Error('Delete failed');
      }
    } catch (error) {
      console.error('Delete error:', error);
      setMessage('Failed to delete template');
      setMessageType('error');
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (timestamp: string): string => {
    return new Date(parseFloat(timestamp) * 1000).toLocaleDateString();
  };

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      {showUpload && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Word Template</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Template Type
              </label>
              <select
                value={templateType}
                onChange={(e) => setTemplateType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {templateTypes.map((type) => (
                  <option key={type.key} value={type.key}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Word Document
              </label>
              <input
                id="template-file"
                type="file"
                accept=".docx,.doc"
                onChange={handleFileSelect}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-sm text-gray-500 mt-1">
                Supported formats: .docx, .doc (Max size: 10MB)
              </p>
            </div>

            <button
              onClick={handleUpload}
              disabled={!selectedFile || isUploading}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isUploading ? (
                <>
                  <i className="fa-solid fa-spinner fa-spin mr-2"></i>
                  Uploading...
                </>
              ) : (
                <>
                  <i className="fa-solid fa-upload mr-2"></i>
                  Upload Template
                </>
              )}
            </button>
            
            <button
              onClick={createSampleTemplate}
              className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700"
            >
              <i className="fa-solid fa-download mr-2"></i>
              Download Sample Template
            </button>
          </div>
        </div>
      )}

      {/* Message Display */}
      {message && (
        <div className={`p-4 rounded-md ${
          messageType === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          <p className="text-sm">
            <i className={`fa-solid ${messageType === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'} mr-2`}></i>
            {message}
          </p>
        </div>
      )}

      {/* Templates List */}
      {showList && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Available Templates</h3>
          </div>
          
          {isLoading ? (
            <div className="p-6 text-center">
              <i className="fa-solid fa-spinner fa-spin text-2xl text-gray-400"></i>
              <p className="text-gray-500 mt-2">Loading templates...</p>
            </div>
          ) : templates.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              <i className="fa-solid fa-file-word text-3xl text-gray-300 mb-2"></i>
              <p>No templates available</p>
              <p className="text-sm">Upload a Word template to get started</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Template
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Size
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Upload Date
                    </th>
                    {showActions && (
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    )}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {templates.map((template) => (
                    <tr key={template.filename} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <i className="fa-solid fa-file-word text-blue-500 mr-3 text-lg"></i>
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {template.filename}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {template.template_type.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {formatFileSize(template.size)}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {formatDate(template.upload_date)}
                      </td>
                      {showActions && (
                        <td className="px-6 py-4 text-sm font-medium space-x-2">
                          <button
                            onClick={() => onTemplateSelect?.(template)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            <i className="fa-solid fa-check mr-1"></i>
                            Select
                          </button>
                          <button
                            onClick={() => handleDownload(template.filename)}
                            className="text-green-600 hover:text-green-900"
                          >
                            <i className="fa-solid fa-download mr-1"></i>
                            Download
                          </button>
                          <button
                            onClick={() => handleDelete(template.filename)}
                            className="text-red-600 hover:text-red-900"
                          >
                            <i className="fa-solid fa-trash mr-1"></i>
                            Delete
                          </button>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TemplateManager;
