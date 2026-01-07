import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useProject } from '../../contexts/ProjectContext';
import {
  generatePMSSignalReport,
  exportPMSSignalReport,
  getProjects,
  createProject,
  ComponentFilter,
  Project
} from '../../services/apiService';
import api from '../../axios';

const PmsSignalReportPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { currentProject } = useProject();
  const [components, setComponents] = useState<string[]>([]);
  const [componentInput, setComponentInput] = useState('');
  const [selectedComponents, setSelectedComponents] = useState<string[]>([]);
  const [availableComponents, setAvailableComponents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Options
  const [dateFrom, setDateFrom] = useState<string>('');
  const [dateTo, setDateTo] = useState<string>('');
  const [includeOpenOnly, setIncludeOpenOnly] = useState(false);
  const [includeTraceability, setIncludeTraceability] = useState(true);
  const [includeActions, setIncludeActions] = useState(true);
  
  // Preview
  const [showPreview, setShowPreview] = useState(false);
  const [previewHtml, setPreviewHtml] = useState<string>('');
  const [summary, setSummary] = useState<any>(null);
  
  // Save to Project
  const [showProjectModal, setShowProjectModal] = useState(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');
  const [newProjectName, setNewProjectName] = useState('');
  const [creatingNew, setCreatingNew] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string>('');

  const finalProjectId = projectId || currentProject?.id;

  useEffect(() => {
    if (finalProjectId) {
      loadComponents();
    }
  }, [finalProjectId]);

  const loadComponents = async () => {
    if (!finalProjectId) return;
    try {
      const projectIdStr = typeof finalProjectId === 'string' ? finalProjectId : String(finalProjectId);
      const response = await api.get(`/projects/${projectIdStr}/components`);
      setAvailableComponents(response.data || []);
    } catch (err: any) {
      console.error('Error loading components:', err);
      setAvailableComponents([]);
    }
  };

  const handleAddComponent = () => {
    if (componentInput.trim() && !components.includes(componentInput.trim())) {
      setComponents([...components, componentInput.trim()]);
      setComponentInput('');
    }
  };

  const handleRemoveComponent = (component: string) => {
    setComponents(components.filter(c => c !== component));
  };

  const handleToggleComponent = (componentId: string) => {
    if (selectedComponents.includes(componentId)) {
      setSelectedComponents(selectedComponents.filter(id => id !== componentId));
    } else {
      setSelectedComponents([...selectedComponents, componentId]);
    }
  };

  const handleGeneratePreview = async () => {
    if (!finalProjectId) {
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
        if (comp.trim()) {
          componentFilter.push({ name: comp });
        }
      }
      
      const request = {
        components: componentFilter.length > 0 ? componentFilter : undefined,
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
        include_open_only: includeOpenOnly,
        include_traceability: includeTraceability,
        include_actions: includeActions,
        format: 'html'
      };

      const response = await generatePMSSignalReport(finalProjectId, request);
      setPreviewHtml(response.pms_report_html);
      setSummary(response.summary);
      setShowPreview(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate PMS Signal Report');
    } finally {
      setLoading(false);
    }
  };

  const handleExportHTML = async () => {
    if (!finalProjectId) return;

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
        if (comp.trim()) {
          componentFilter.push({ name: comp });
        }
      }
      
      const componentsStr = componentFilter.map(c => c.name).join(',');
      const html = await exportPMSSignalReport(
        finalProjectId,
        componentsStr || undefined,
        dateFrom || undefined,
        dateTo || undefined,
        includeOpenOnly,
        includeTraceability,
        includeActions
      );
      
      // Open in new tab
      const blob = new Blob([html], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const newWindow = window.open(url, '_blank');
      if (newWindow) {
        newWindow.onload = () => URL.revokeObjectURL(url);
      } else {
        // Fallback to download
        const a = document.createElement('a');
        a.href = url;
        a.download = `PMS_Signal_Feedback_Report_${currentProject?.name || 'report'}_${new Date().toISOString().split('T')[0]}.html`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to export PMS Signal Report');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenProjectModal = async () => {
    if (!previewHtml) {
      setError('Please generate the PMS Signal Report preview first');
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
      setSaveError('No PMS Signal Report content to save. Please generate preview first.');
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
          description: `PMS Signal Feedback Report for ${newProjectName}`
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
        summary: summary,
        generatedAt: new Date().toISOString(),
        components: components.length > 0 ? components : selectedComponents,
        options: {
          dateFrom,
          dateTo,
          includeOpenOnly,
          includeTraceability,
          includeActions
        }
      };
      localStorage.setItem(`pms_signal_report_${targetProjectId}_${Date.now()}`, JSON.stringify(reportData));
      
      alert('PMS Signal Report saved to project successfully!');
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

  if (!finalProjectId) {
    return (
      <div className="p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">Please select a project first to generate PMS Signal Report.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="bg-gray-200 rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">PMS Signal Feedback Report</h1>
        <p className="text-gray-600">Generate signal feedback report for {currentProject?.name || 'selected project'}</p>
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
          <div className="flex gap-2 mb-2">
            <input
              type="text"
              value={componentInput}
              onChange={(e) => setComponentInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddComponent()}
              placeholder="Component name"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleAddComponent}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Add
            </button>
          </div>
          {components.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-2">
              {components.map((comp, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                >
                  {comp}
                  <button
                    onClick={() => handleRemoveComponent(comp)}
                    className="ml-2 text-blue-600 hover:text-blue-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          )}
          <p className="text-sm text-gray-500 mt-2">
            Leave empty to include all components
          </p>
        </div>
      </div>

      <div className="bg-gray-200 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Date Range</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date From</label>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date To</label>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
        </div>
      </div>

      <div className="bg-gray-200 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Options</h2>
        <div className="space-y-3">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={includeOpenOnly}
              onChange={(e) => setIncludeOpenOnly(e.target.checked)}
              className="rounded border-gray-300"
            />
            <span className="text-sm text-gray-900">Include Open Only</span>
          </label>
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
              checked={includeActions}
              onChange={(e) => setIncludeActions(e.target.checked)}
              className="rounded border-gray-300"
            />
            <span className="text-sm text-gray-900">Include Actions (CAPA/Change)</span>
          </label>
        </div>
      </div>

      {summary && (
        <div className="bg-gray-200 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Summary</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Total Signals</p>
              <p className="text-2xl font-bold text-gray-900">{summary.total_signals || 0}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Under Review</p>
              <p className="text-2xl font-bold text-gray-900">{summary.signals_under_review || 0}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Confirmed Trends</p>
              <p className="text-2xl font-bold text-gray-900">{summary.signals_confirmed || 0}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Triggered Risk</p>
              <p className="text-2xl font-bold text-gray-900">{summary.signals_triggered_risk || 0}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Resulted in CAPA</p>
              <p className="text-2xl font-bold text-gray-900">{summary.signals_resulted_capa || 0}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Resulted in Change</p>
              <p className="text-2xl font-bold text-gray-900">{summary.signals_resulted_change || 0}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Missing Risk Link</p>
              <p className="text-2xl font-bold text-red-600">{summary.signals_no_risk_link || 0}</p>
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
              onClick={handleExportHTML}
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
              <h3 className="text-xl font-semibold text-gray-900">PMS Signal Feedback Report Preview</h3>
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
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Save PMS Signal Report to Project</h3>
            
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

export default PmsSignalReportPage;

