import React, { useState, useEffect } from 'react';
import { useProject } from '../contexts/ProjectContext';
import {
  generateRMF,
  exportRMF,
  getRMFEvidence,
  ComponentFilter,
  RMFGenerateRequest
} from '../services/apiService';
import api from '../axios';

const RmfExportPage: React.FC = () => {
  const { currentProject } = useProject();
  const [components, setComponents] = useState<ComponentFilter[]>([]);
  const [selectedComponents, setSelectedComponents] = useState<string[]>([]);
  const [availableComponents, setAvailableComponents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Options
  const [includeTraceability, setIncludeTraceability] = useState(true);
  const [includeApprovals, setIncludeApprovals] = useState(true);
  const [includeAiEvents, setIncludeAiEvents] = useState(true);
  const [includeAuditLog, setIncludeAuditLog] = useState(true);
  
  // Preview
  const [showPreview, setShowPreview] = useState(false);
  const [previewHtml, setPreviewHtml] = useState<string>('');
  const [evidence, setEvidence] = useState<any>(null);

  useEffect(() => {
    if (currentProject?.id) {
      loadComponents();
    }
  }, [currentProject?.id]);

  const loadComponents = async () => {
    if (!currentProject?.id) return;
    
    try {
      // Try to get project ID as string (UUID)
      const projectId = typeof currentProject.id === 'string' ? currentProject.id : String(currentProject.id);
      const response = await api.get(`/projects/${projectId}/components`);
      setAvailableComponents(response.data || []);
    } catch (err: any) {
      console.error('Error loading components:', err);
      // If components endpoint doesn't exist or fails, continue without components
      setAvailableComponents([]);
    }
  };

  const handleAddComponent = () => {
    setComponents([...components, { name: '' }]);
  };

  const handleRemoveComponent = (index: number) => {
    setComponents(components.filter((_, i) => i !== index));
  };

  const handleComponentChange = (index: number, field: 'id' | 'name', value: string) => {
    const updated = [...components];
    updated[index] = { ...updated[index], [field]: value };
    setComponents(updated);
  };

  const handleToggleComponent = (componentId: string) => {
    if (selectedComponents.includes(componentId)) {
      setSelectedComponents(selectedComponents.filter(id => id !== componentId));
    } else {
      setSelectedComponents([...selectedComponents, componentId]);
    }
  };

  const handleGeneratePreview = async () => {
    if (!currentProject?.id) {
      setError('Please select a project first');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // Build component filter from both selected and manually entered
      const componentFilter: ComponentFilter[] = [];
      
      // Add selected components
      for (const compId of selectedComponents) {
        const comp = availableComponents.find(c => c.id === compId);
        if (comp) {
          componentFilter.push({ id: comp.id, name: comp.name });
        }
      }
      
      // Add manually entered components
      for (const comp of components) {
        if (comp.name.trim()) {
          componentFilter.push(comp);
        }
      }
      
      const request: RMFGenerateRequest = {
        components: componentFilter.length > 0 ? componentFilter : undefined,
        include_ai_events: includeAiEvents,
        include_audit_log: includeAuditLog,
        include_traceability: includeTraceability,
        format: 'html'
      };

      const response = await generateRMF(currentProject.id, request);
      setPreviewHtml(response.rmf_html);
      setShowPreview(true);
      
      // Also get evidence for summary
      const evidenceData = await getRMFEvidence(
        currentProject.id,
        componentFilter.map(c => c.name).join(','),
        includeAiEvents,
        includeAuditLog,
        includeTraceability
      );
      setEvidence(evidenceData);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate RMF');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadHTML = async () => {
    if (!currentProject?.id) return;

    try {
      setLoading(true);
      setError(null);
      
      // Build component filter
      const componentFilter: ComponentFilter[] = [];
      for (const compId of selectedComponents) {
        const comp = availableComponents.find(c => c.id === compId);
        if (comp) {
          componentFilter.push({ id: comp.id, name: comp.name });
        }
      }
      for (const comp of components) {
        if (comp.name.trim()) {
          componentFilter.push(comp);
        }
      }
      
      const componentsStr = componentFilter.map(c => c.name).join(',');
      const html = await exportRMF(
        currentProject.id,
        componentsStr || undefined,
        includeAiEvents,
        includeAuditLog,
        includeTraceability
      );
      
      const blob = new Blob([html], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `RMF_${currentProject.name}_${new Date().toISOString().split('T')[0]}.html`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to export RMF');
    } finally {
      setLoading(false);
    }
  };

  if (!currentProject) {
    return (
      <div className="p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">Please select a project first to generate a Risk Management File.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="bg-gray-200 rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Risk Management File (RMF) Export</h1>
        <p className="text-gray-600">Generate an audit-ready Risk Management File package for {currentProject.name}</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      <div className="bg-gray-200 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Component Selection</h2>
        
        {/* Available Components */}
        {availableComponents.length > 0 && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Select from Project Components</label>
            <div className="space-y-2 max-h-40 overflow-y-auto border border-gray-300 rounded-md p-3">
              {availableComponents.map((comp) => (
                <label key={comp.id} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={selectedComponents.includes(comp.id)}
                    onChange={() => handleToggleComponent(comp.id)}
                    className="rounded border-gray-300"
                  />
                  <span className="text-sm text-gray-900">{comp.name}</span>
                </label>
              ))}
            </div>
          </div>
        )}
        
        {/* Manual Component Entry */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Or Enter Component Names</label>
          <div className="space-y-2">
            {components.map((comp, index) => (
              <div key={index} className="flex gap-2">
                <input
                  type="text"
                  value={comp.name}
                  onChange={(e) => handleComponentChange(index, 'name', e.target.value)}
                  placeholder="Component name"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={() => handleRemoveComponent(index)}
                  className="px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                >
                  Remove
                </button>
              </div>
            ))}
            <button
              onClick={handleAddComponent}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              + Add Component
            </button>
          </div>
          <p className="text-sm text-gray-500 mt-2">
            Leave empty to include all components
          </p>
        </div>
      </div>

      <div className="bg-gray-200 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Export Options</h2>
        
        <div className="space-y-3">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={includeTraceability}
              onChange={(e) => setIncludeTraceability(e.target.checked)}
              className="rounded border-gray-300"
            />
            <span className="text-sm text-gray-900">Include Traceability</span>
          </label>
          
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={includeApprovals}
              onChange={(e) => setIncludeApprovals(e.target.checked)}
              className="rounded border-gray-300"
            />
            <span className="text-sm text-gray-900">Include Approvals</span>
          </label>
          
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={includeAiEvents}
              onChange={(e) => setIncludeAiEvents(e.target.checked)}
              className="rounded border-gray-300"
            />
            <span className="text-sm text-gray-900">Include AI Events</span>
          </label>
          
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={includeAuditLog}
              onChange={(e) => setIncludeAuditLog(e.target.checked)}
              className="rounded border-gray-300"
            />
            <span className="text-sm text-gray-900">Include Audit Log</span>
          </label>
        </div>
      </div>

      {evidence && (
        <div className="bg-gray-200 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Summary</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Risk Items</p>
              <p className="text-2xl font-bold text-gray-900">{evidence.summaries?.risk_count || 0}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Versions</p>
              <p className="text-2xl font-bold text-gray-900">{evidence.summaries?.total_versions || 0}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Controls</p>
              <p className="text-2xl font-bold text-gray-900">{evidence.summaries?.total_controls || 0}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Approvals</p>
              <p className="text-2xl font-bold text-gray-900">{evidence.summaries?.total_approvals || 0}</p>
            </div>
          </div>
        </div>
      )}

      <div className="flex gap-4">
        <button
          onClick={handleGeneratePreview}
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Generating...' : 'Generate RMF Preview'}
        </button>
        {previewHtml && (
          <button
            onClick={handleDownloadHTML}
            disabled={loading}
            className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
          >
            Download HTML
          </button>
        )}
      </div>

      {/* Preview Dialog */}
      {showPreview && previewHtml && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-200 rounded-lg p-6 max-w-6xl w-full max-h-[90vh] overflow-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-semibold text-gray-900">RMF Preview</h3>
              <button
                onClick={() => setShowPreview(false)}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
              >
                Close
              </button>
            </div>
            <div
              className="bg-white p-6 rounded-lg"
              dangerouslySetInnerHTML={{ __html: previewHtml }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default RmfExportPage;

