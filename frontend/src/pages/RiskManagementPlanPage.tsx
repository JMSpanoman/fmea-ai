import React, { useState, useEffect } from 'react';
import { useProject } from '../contexts/ProjectContext';
import authService from '../services/authService';
import {
  generateRMP,
  getRMP,
  updateRMP,
  approveRMP,
  exportRMPHTML,
  ComponentInput,
  RMPOut,
  RMPGenerateRequest,
  RMPApprovalRequest
} from '../services/apiService';

const RiskManagementPlanPage: React.FC = () => {
  const { currentProject } = useProject();
  const [rmp, setRmp] = useState<RMPOut | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticating, setIsAuthenticating] = useState(true);
  
  // Form state
  const [scope, setScope] = useState('');
  const [intendedUse, setIntendedUse] = useState('');
  const [components, setComponents] = useState<ComponentInput[]>([{ name: '', description: '' }]);
  const [acceptabilityProfile, setAcceptabilityProfile] = useState('default_med_device');
  const [reviewRoles, setReviewRoles] = useState<{ [key: string]: string }>({
    risk_manager: 'required',
    design_lead: 'required',
    quality_lead: 'required',
    approver: 'required'
  });
  
  // Approval state
  const [showApprovalDialog, setShowApprovalDialog] = useState(false);
  const [approvalDecision, setApprovalDecision] = useState<'approved' | 'rejected'>('approved');
  const [approvalRationale, setApprovalRationale] = useState('');
  
  // Preview state
  const [showPreview, setShowPreview] = useState(false);
  const [previewHtml, setPreviewHtml] = useState<string>('');

  useEffect(() => {
    const initAuth = async () => {
      try {
        if (!authService.isAuthenticated()) {
          await authService.authenticate();
        }
      } catch (error) {
        console.error('Failed to authenticate:', error);
        setError('Failed to authenticate. Please refresh the page.');
      } finally {
        setIsAuthenticating(false);
      }
    };

    initAuth();
  }, []);

  useEffect(() => {
    if (!isAuthenticating && currentProject?.id) {
      loadRMP();
    }
  }, [currentProject?.id, isAuthenticating]);

  const loadRMP = async () => {
    if (!currentProject?.id) return;
    
    // Ensure authentication before making API calls
    if (!authService.isAuthenticated()) {
      try {
        await authService.authenticate();
      } catch (error) {
        setError('Failed to authenticate. Please refresh the page.');
        return;
      }
    }
    
    try {
      setLoading(true);
      const rmpData = await getRMP(currentProject.id);
      setRmp(rmpData);
      // Populate form with existing data
      setScope(rmpData.scope);
      setIntendedUse(rmpData.intended_use);
      try {
        const parsedComponents = JSON.parse(rmpData.components_json || '[]');
        setComponents(parsedComponents.length > 0 ? parsedComponents : [{ name: '', description: '' }]);
      } catch {
        setComponents([{ name: '', description: '' }]);
      }
      try {
        const parsedRoles = JSON.parse(rmpData.review_roles_json || '{}');
        setReviewRoles(parsedRoles);
      } catch {
        setReviewRoles({});
      }
    } catch (err: any) {
      if (err.response?.status === 404) {
        // RMP doesn't exist yet, that's okay
        setRmp(null);
      } else {
        setError(err.message || 'Failed to load Risk Management Plan');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAddComponent = () => {
    setComponents([...components, { name: '', description: '' }]);
  };

  const handleRemoveComponent = (index: number) => {
    if (components.length > 1) {
      setComponents(components.filter((_, i) => i !== index));
    }
  };

  const handleComponentChange = (index: number, field: 'name' | 'description', value: string) => {
    const updated = [...components];
    updated[index] = { ...updated[index], [field]: value };
    setComponents(updated);
  };

  const handleGenerate = async () => {
    if (!currentProject?.id) {
      setError('Please select a project first');
      return;
    }

    // Validate
    if (!scope.trim()) {
      setError('Scope is required');
      return;
    }
    if (!intendedUse.trim()) {
      setError('Intended use is required');
      return;
    }
    if (components.length === 0 || components.every(c => !c.name.trim())) {
      setError('At least one component is required');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const request: RMPGenerateRequest = {
        scope: scope.trim(),
        intended_use: intendedUse.trim(),
        components: components.filter(c => c.name.trim()),
        acceptability_profile: acceptabilityProfile,
        review_roles: reviewRoles,
        ai_assistance_enabled: true
      };

      const rmpData = await generateRMP(currentProject.id, request);
      setRmp(rmpData);
      setShowPreview(true);
      setPreviewHtml(rmpData.rendered_html);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate Risk Management Plan');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async () => {
    if (!currentProject?.id || !rmp) {
      setError('RMP not found');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const request: Partial<RMPGenerateRequest> = {
        scope: scope.trim(),
        intended_use: intendedUse.trim(),
        components: components.filter(c => c.name.trim()),
        review_roles: reviewRoles
      };

      const updatedRmp = await updateRMP(currentProject.id, rmp.id, request);
      setRmp(updatedRmp);
      setPreviewHtml(updatedRmp.rendered_html);
      alert('Risk Management Plan updated successfully. New version created.');
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to update Risk Management Plan');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!currentProject?.id || !rmp) return;

    try {
      setLoading(true);
      setError(null);
      
      const request: RMPApprovalRequest = {
        decision: approvalDecision,
        rationale: approvalRationale
      };

      await approveRMP(currentProject.id, rmp.id, request);
      setShowApprovalDialog(false);
      setApprovalRationale('');
      await loadRMP(); // Reload to get updated status
      alert(`Risk Management Plan ${approvalDecision} successfully`);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to approve Risk Management Plan');
    } finally {
      setLoading(false);
    }
  };

  const handleExportHTML = async () => {
    if (!currentProject?.id || !rmp) return;

    try {
      const html = await exportRMPHTML(currentProject.id, rmp.id);
      const blob = new Blob([html], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `RMP_${currentProject.name}_v${rmp.current_version_no}.html`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to export HTML');
    }
  };

  const handleViewPreview = async () => {
    if (!rmp) return;
    setPreviewHtml(rmp.rendered_html);
    setShowPreview(true);
  };

  if (isAuthenticating) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <span className="ml-4 text-gray-600">Authenticating...</span>
        </div>
      </div>
    );
  }

  if (!currentProject) {
    return (
      <div className="p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">Please select a project first to generate a Risk Management Plan.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="bg-gray-200 rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Risk Management Plan (RMP)</h1>
        <p className="text-gray-600">Generate a comprehensive Risk Management Plan for {currentProject.name}</p>
        {rmp && (
          <div className="mt-4 flex items-center gap-4">
            <span className="text-sm text-gray-600">Status: <strong>{rmp.status}</strong></span>
            <span className="text-sm text-gray-600">Version: <strong>{rmp.current_version_no}</strong></span>
          </div>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      <div className="bg-gray-200 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">RMP Details</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Scope *</label>
            <textarea
              value={scope}
              onChange={(e) => setScope(e.target.value)}
              placeholder="Enter the scope of the Risk Management Plan..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={4}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Intended Use *</label>
            <textarea
              value={intendedUse}
              onChange={(e) => setIntendedUse(e.target.value)}
              placeholder="Enter the intended use of the device/system..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={4}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Components *</label>
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
                  <input
                    type="text"
                    value={comp.description || ''}
                    onChange={(e) => handleComponentChange(index, 'description', e.target.value)}
                    placeholder="Description (optional)"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  {components.length > 1 && (
                    <button
                      onClick={() => handleRemoveComponent(index)}
                      className="px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                    >
                      Remove
                    </button>
                  )}
                </div>
              ))}
              <button
                onClick={handleAddComponent}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                + Add Component
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Acceptability Profile</label>
            <select
              value={acceptabilityProfile}
              onChange={(e) => setAcceptabilityProfile(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="default_med_device">Default Medical Device</option>
              <option value="custom">Custom</option>
            </select>
          </div>
        </div>

        <div className="mt-6 flex gap-4">
          {!rmp ? (
            <button
              onClick={handleGenerate}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Generating...' : 'Generate RMP'}
            </button>
          ) : (
            <>
              <button
                onClick={handleUpdate}
                disabled={loading}
                className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
              >
                {loading ? 'Updating...' : 'Save New Version'}
              </button>
              <button
                onClick={handleViewPreview}
                className="px-6 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
              >
                View Preview
              </button>
              <button
                onClick={handleExportHTML}
                className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
              >
                Download HTML
              </button>
              {rmp.status !== 'approved' && (
                <button
                  onClick={() => setShowApprovalDialog(true)}
                  className="px-6 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700"
                >
                  Approve
                </button>
              )}
            </>
          )}
        </div>
      </div>

      {/* Approval Dialog */}
      {showApprovalDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-200 rounded-lg p-6 max-w-md w-full">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Approve Risk Management Plan</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Decision</label>
                <select
                  value={approvalDecision}
                  onChange={(e) => setApprovalDecision(e.target.value as 'approved' | 'rejected')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="approved">Approve</option>
                  <option value="rejected">Reject</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Rationale *</label>
                <textarea
                  value={approvalRationale}
                  onChange={(e) => setApprovalRationale(e.target.value)}
                  placeholder="Enter approval rationale..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  rows={4}
                  required
                />
              </div>
              <div className="flex gap-4">
                <button
                  onClick={handleApprove}
                  disabled={loading || !approvalRationale.trim()}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  Submit
                </button>
                <button
                  onClick={() => {
                    setShowApprovalDialog(false);
                    setApprovalRationale('');
                  }}
                  className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Preview Dialog */}
      {showPreview && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-200 rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-semibold text-gray-900">RMP Preview</h3>
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

export default RiskManagementPlanPage;
