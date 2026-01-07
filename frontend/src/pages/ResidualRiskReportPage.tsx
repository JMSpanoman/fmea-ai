import React, { useState, useEffect } from 'react';
import { useProject } from '../contexts/ProjectContext';
import {
  generateResidualRisk,
  exportResidualRisk,
  getResidualRiskData,
  getProjects,
  createProject,
  ComponentFilter,
  ResidualRiskGenerateRequest,
  ResidualRiskRow,
  Project
} from '../services/apiService';
import api from '../axios';

const ResidualRiskReportPage: React.FC = () => {
  const { currentProject } = useProject();
  const [components, setComponents] = useState<ComponentFilter[]>([]);
  const [selectedComponents, setSelectedComponents] = useState<string[]>([]);
  const [availableComponents, setAvailableComponents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Options
  const [versionScope, setVersionScope] = useState<'approved_only' | 'current' | 'all'>('approved_only');
  const [includeUnapproved, setIncludeUnapproved] = useState(false);
  
  // Preview
  const [showPreview, setShowPreview] = useState(false);
  const [previewHtml, setPreviewHtml] = useState<string>('');
  const [previewData, setPreviewData] = useState<ResidualRiskRow[]>([]);
  const [counts, setCounts] = useState<any>(null);
  
  // Save to Project
  const [showProjectModal, setShowProjectModal] = useState(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');
  const [newProjectName, setNewProjectName] = useState('');
  const [creatingNew, setCreatingNew] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string>('');

  useEffect(() => {
    if (currentProject?.id) {
      loadComponents();
    }
  }, [currentProject?.id]);

  const loadComponents = async () => {
    if (!currentProject?.id) return;
    
    try {
      const projectId = typeof currentProject.id === 'string' ? currentProject.id : String(currentProject.id);
      const response = await api.get(`/projects/${projectId}/components`);
      setAvailableComponents(response.data || []);
    } catch (err: any) {
      console.error('Error loading components:', err);
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
      
      const request: ResidualRiskGenerateRequest = {
        components: componentFilter.length > 0 ? componentFilter : undefined,
        version_scope: versionScope,
        include_unapproved: includeUnapproved,
        acceptability_profile: 'default_med_device',
        format: 'html'
      };

      const response = await generateResidualRisk(currentProject.id, request);
      setPreviewHtml(response.residual_risk_html);
      setCounts(response.counts);
      setShowPreview(true);
      
      // Get data for table preview
      const componentsStr = componentFilter.map(c => c.name).join(',');
      const data = await getResidualRiskData(
        currentProject.id,
        componentsStr || undefined,
        versionScope,
        includeUnapproved
      );
      setPreviewData(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate Residual Risk Evaluation');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadHTML = async () => {
    if (!currentProject?.id) return;

    try {
      setLoading(true);
      setError(null);
      
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
      const html = await exportResidualRisk(
        currentProject.id,
        componentsStr || undefined,
        versionScope,
        includeUnapproved
      );
      
      const blob = new Blob([html], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Residual_Risk_Evaluation_${currentProject.name}_${new Date().toISOString().split('T')[0]}.html`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to export Residual Risk Evaluation');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenProjectModal = async () => {
    if (!previewHtml) {
      setError('Please generate the Residual Risk Evaluation preview first');
      return;
    }
    try {
      const projectList = await getProjects();
      setProjects(projectList);
      setShowProjectModal(true);
    } catch (err: any) {
      setError('Failed to load projects');
    }
  };

  const handleSaveToProject = async () => {
    if (!previewHtml) {
      setSaveError('No Residual Risk Evaluation content to save. Please generate preview first.');
      return;
    }

    if (!selectedProjectId && !newProjectName.trim()) {
      setSaveError('Please select a project or enter a new project name');
      return;
    }

    setIsSaving(true);
    setSaveError('');

    try {
      let targetProjectId = selectedProjectId;

      if (creatingNew && newProjectName.trim()) {
        const newProject = await createProject({
          name: newProjectName,
          description: `Residual Risk Evaluation for ${newProjectName}`
        });
        targetProjectId = newProject.id;
      }

      if (!targetProjectId) {
        setSaveError('Please select or create a project');
        setIsSaving(false);
        return;
      }

      const reportData = {
        projectId: targetProjectId,
        html: previewHtml,
        data: previewData,
        generatedAt: new Date().toISOString(),
        components: components.map(c => c.name).filter(n => n),
        options: {
          versionScope,
          includeUnapproved
        }
      };
      localStorage.setItem(`residual_risk_${targetProjectId}_${Date.now()}`, JSON.stringify(reportData));
      
      alert('Residual Risk Evaluation saved to project successfully!');
      setShowProjectModal(false);
      setSelectedProjectId('');
      setNewProjectName('');
      setCreatingNew(false);
    } catch (error: any) {
      console.error('Error saving to project:', error);
      setSaveError('Failed to save to project. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  if (!currentProject) {
    return (
      <div className="p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">Please select a project first to generate a Residual Risk Evaluation.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="bg-gray-200 rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Residual Risk Evaluation</h1>
        <p className="text-gray-600">Generate a residual risk evaluation report from SmartQS risk data for {currentProject.name}</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      <div className="bg-gray-200 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Component Selection</h2>
        
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
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Version Scope</h2>
        
        <div className="space-y-3">
          <label className="flex items-center space-x-2">
            <input
              type="radio"
              name="version_scope"
              value="approved_only"
              checked={versionScope === 'approved_only'}
              onChange={(e) => {
                setVersionScope('approved_only');
                setIncludeUnapproved(false);
              }}
              className="border-gray-300"
            />
            <span className="text-sm text-gray-900">Approved Only (Default)</span>
          </label>
          
          <label className="flex items-center space-x-2">
            <input
              type="radio"
              name="version_scope"
              value="current"
              checked={versionScope === 'current'}
              onChange={(e) => setVersionScope('current')}
              className="border-gray-300"
            />
            <span className="text-sm text-gray-900">Current Versions</span>
          </label>
          
          <label className="flex items-center space-x-2">
            <input
              type="radio"
              name="version_scope"
              value="all"
              checked={versionScope === 'all'}
              onChange={(e) => setVersionScope('all')}
              className="border-gray-300"
            />
            <span className="text-sm text-gray-900">All Versions</span>
          </label>
          
          {versionScope === 'approved_only' && (
            <label className="flex items-center space-x-2 ml-6">
              <input
                type="checkbox"
                checked={includeUnapproved}
                onChange={(e) => setIncludeUnapproved(e.target.checked)}
                className="rounded border-gray-300"
              />
              <span className="text-sm text-gray-900">Include Unapproved (Draft) Entries</span>
            </label>
          )}
        </div>
      </div>

      {counts && (
        <div className="bg-gray-200 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Summary</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Versions Included</p>
              <p className="text-2xl font-bold text-gray-900">{counts.versions_included || 0}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Missing Residual Fields</p>
              <p className="text-2xl font-bold text-gray-900">{counts.missing_residual_fields || 0}</p>
            </div>
          </div>
        </div>
      )}

      {/* Preview Table */}
      {previewData.length > 0 && (
        <div className="bg-gray-200 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Preview Table</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Risk Key</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Version</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Residual Severity</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Residual Probability</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Residual Score</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acceptability</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Source</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {previewData.map((row, index) => (
                  <tr key={index}>
                    <td className="px-4 py-3 text-sm text-gray-900">{row.risk_key}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{row.version_no}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{row.residual_severity ?? 'N/A'}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{row.residual_probability_of_harm ?? 'N/A'}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{row.residual_risk_score ?? 'N/A'}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{row.residual_acceptability || 'N/A'}</td>
                    <td className="px-4 py-3 text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        row.acceptability_source === 'stored'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {row.acceptability_source}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        row.approved 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {row.approved ? 'Approved' : 'Draft'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="flex gap-4">
        <button
          onClick={handleGeneratePreview}
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Generating...' : 'Generate Preview'}
        </button>
        {previewHtml && (
          <>
            <button
              onClick={() => setShowPreview(true)}
              className="px-6 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
            >
              View HTML Preview
            </button>
            <button
              onClick={handleOpenProjectModal}
              disabled={loading}
              className="px-6 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50"
            >
              Save to Project
            </button>
            <button
              onClick={handleDownloadHTML}
              disabled={loading}
              className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              Export HTML
            </button>
          </>
        )}
      </div>

      {/* HTML Preview Dialog */}
      {showPreview && previewHtml && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-200 rounded-lg p-6 max-w-6xl w-full max-h-[90vh] overflow-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-semibold text-gray-900">Residual Risk Evaluation Preview</h3>
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

      {/* Save to Project Modal */}
      {showProjectModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Save Residual Risk Evaluation to Project</h3>
            
            {saveError && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                <p className="text-red-800 text-sm">{saveError}</p>
              </div>
            )}

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {creatingNew ? 'New Project Name' : 'Select Project'}
              </label>
              
              {!creatingNew ? (
                <>
                  <select
                    value={selectedProjectId}
                    onChange={(e) => setSelectedProjectId(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select a project...</option>
                    {projects.map((project) => (
                      <option key={project.id} value={project.id}>
                        {project.name}
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={() => setCreatingNew(true)}
                    className="mt-2 text-sm text-blue-600 hover:text-blue-800"
                  >
                    + Create New Project
                  </button>
                </>
              ) : (
                <>
                  <input
                    type="text"
                    value={newProjectName}
                    onChange={(e) => setNewProjectName(e.target.value)}
                    placeholder="Enter project name"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={() => {
                      setCreatingNew(false);
                      setNewProjectName('');
                    }}
                    className="mt-2 text-sm text-gray-600 hover:text-gray-800"
                  >
                    ← Select Existing Project
                  </button>
                </>
              )}
            </div>

            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowProjectModal(false);
                  setSelectedProjectId('');
                  setNewProjectName('');
                  setCreatingNew(false);
                  setSaveError('');
                }}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveToProject}
                disabled={isSaving}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {isSaving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResidualRiskReportPage;

