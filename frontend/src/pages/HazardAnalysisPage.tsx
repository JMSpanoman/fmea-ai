import React, { useState, useEffect } from 'react';
import { useProject } from '../contexts/ProjectContext';
import {
  generateHazardAnalysis,
  exportHazardAnalysis,
  getHazardAnalysisData,
  getProjects,
  createProject,
  ComponentFilter,
  HazardAnalysisGenerateRequest,
  HazardAnalysisRow,
  Project,
  syncHazardAnalysisFromFmea,
  fillGapsHazardAnalysisItem
} from '../services/apiService';
import api from '../axios';

const HazardAnalysisPage: React.FC = () => {
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
  const [previewData, setPreviewData] = useState<HazardAnalysisRow[]>([]);
  const [counts, setCounts] = useState<any>(null);
  
  // Save to Project
  const [showProjectModal, setShowProjectModal] = useState(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');
  const [newProjectName, setNewProjectName] = useState('');
  const [creatingNew, setCreatingNew] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string>('');
  // Filters and expandable row
  const [filterApproval, setFilterApproval] = useState<string>('');
  const [filterHazardCategory, setFilterHazardCategory] = useState<string>('');
  const [expandedRowId, setExpandedRowId] = useState<string | null>(null);
  const [syncingFmea, setSyncingFmea] = useState(false);
  const [fillGapsId, setFillGapsId] = useState<string | null>(null);

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
      
      const request: HazardAnalysisGenerateRequest = {
        components: componentFilter.length > 0 ? componentFilter : undefined,
        version_scope: versionScope,
        include_unapproved: includeUnapproved,
        include_metadata: true,
        format: 'html'
      };

      const response = await generateHazardAnalysis(currentProject.id, request);
      setPreviewHtml(response.hazard_analysis_html);
      setCounts(response.counts);
      setShowPreview(true);
      
      // Also get data for table preview
      const componentsStr = componentFilter.map(c => c.name).join(',');
      const data = await getHazardAnalysisData(
        currentProject.id,
        componentsStr || undefined,
        versionScope,
        includeUnapproved
      );
      setPreviewData(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate Hazard Analysis');
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
      const html = await exportHazardAnalysis(
        currentProject.id,
        componentsStr || undefined,
        versionScope,
        includeUnapproved
      );
      
      const blob = new Blob([html], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Hazard_Analysis_${currentProject.name}_${new Date().toISOString().split('T')[0]}.html`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to export Hazard Analysis');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenProjectModal = async () => {
    if (!previewHtml) {
      setError('Please generate the Hazard Analysis preview first');
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
      setSaveError('No Hazard Analysis content to save. Please generate preview first.');
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
          description: `Hazard Analysis for ${newProjectName}`
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
      localStorage.setItem(`hazard_analysis_${targetProjectId}_${Date.now()}`, JSON.stringify(reportData));
      
      alert('Hazard Analysis saved to project successfully!');
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
          <p className="text-yellow-800">Please select a project first to generate a Hazard Analysis.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="bg-gray-200 rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Hazard Analysis</h1>
        <p className="text-gray-600">Generate a systematic hazard analysis from SmartQS risk data for {currentProject.name}</p>
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
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-600">Risk Items</p>
              <p className="text-2xl font-bold text-gray-900">{counts.risk_items || 0}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Versions Included</p>
              <p className="text-2xl font-bold text-gray-900">{counts.versions_included || 0}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Unapproved Excluded</p>
              <p className="text-2xl font-bold text-gray-900">{counts.unapproved_excluded || 0}</p>
            </div>
          </div>
        </div>
      )}

      {/* Sync from FMEA */}
      <div className="bg-gray-200 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Hazard Analysis Items</h2>
        <p className="text-sm text-gray-600 mb-4">Sync from FMEA to prefill hazard analysis items, or generate preview from risk data.</p>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={async () => {
              if (!currentProject?.id) return;
              setSyncingFmea(true);
              try {
                const res = await syncHazardAnalysisFromFmea(currentProject.id);
                setError(null);
                alert(`Created ${res.created} hazard analysis item(s) from ${res.fmea_rows_processed} FMEA row(s).`);
                handleGeneratePreview();
              } catch (e: any) {
                setError(e.response?.data?.detail || e.message || 'Sync failed');
              } finally {
                setSyncingFmea(false);
              }
            }}
            disabled={syncingFmea || !currentProject?.id}
            className="px-4 py-2 bg-purple-300 text-gray-900 rounded-md hover:bg-purple-400 disabled:opacity-50"
          >
            {syncingFmea ? 'Syncing...' : 'Sync from FMEA'}
          </button>
        </div>
      </div>

      {/* Preview Table */}
      {previewData.length > 0 && (
        <div className="bg-gray-200 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Preview Table</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase w-8"></th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Component</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Risk Key</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Hazard</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Failure Mode</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Init S/P</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Residual</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">AI</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {previewData.map((row, index) => {
                  const rowId = (row as any).id || `row-${row.risk_key}-${row.version_no}-${index}`;
                  const isExpanded = expandedRowId === rowId;
                  return (
                    <React.Fragment key={rowId}>
                      <tr
                        className={isExpanded ? 'bg-gray-50' : ''}
                        onClick={() => setExpandedRowId(isExpanded ? null : rowId)}
                      >
                        <td className="px-2 py-2 text-gray-500">{isExpanded ? '▼' : '▶'}</td>
                        <td className="px-4 py-3 text-sm text-gray-900">{row.component_name}</td>
                        <td className="px-4 py-3 text-sm text-gray-900">{row.risk_key}</td>
                        <td className="px-4 py-3 text-sm text-gray-900">{(row as any).hazard_category || '—'}</td>
                        <td className="px-4 py-3 text-sm text-gray-900 max-w-[200px] truncate" title={row.hazard || ''}>{row.hazard || '—'}</td>
                        <td className="px-4 py-3 text-sm text-gray-900 max-w-[160px] truncate" title={row.failure_mode || ''}>{row.failure_mode || '—'}</td>
                        <td className="px-4 py-3 text-sm text-gray-900">{(row as any).initial_severity ?? '—'}/{(row as any).initial_probability ?? '—'}</td>
                        <td className="px-4 py-3 text-sm text-gray-900">{(row as any).residual_risk_level || (row as any).residual_risk_acceptability || '—'}</td>
                        <td className="px-4 py-3 text-sm">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            row.approved ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                          }`}>
                            {(row as any).approval_status || (row.approved ? 'Approved' : 'Draft')}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm">
                          {(row as any).ai_generated && (
                            <span className="px-2 py-0.5 rounded bg-purple-100 text-purple-800 text-xs" title="AI-generated">
                              AI {(row as any).ai_confidence || ''}
                            </span>
                          )}
                        </td>
                      </tr>
                      {isExpanded && (
                        <tr>
                          <td colSpan={10} className="px-4 py-4 bg-gray-50 border-b border-gray-200 text-sm">
                            <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-gray-700">
                              <div><span className="font-medium">Sequence of events:</span> {(row as any).foreseeable_sequence_of_events || row.sequence_of_events || '—'}</div>
                              <div><span className="font-medium">Hazardous situation:</span> {row.hazardous_situation || '—'}</div>
                              <div><span className="font-medium">Harm:</span> {row.harm || '—'}</div>
                              <div><span className="font-medium">Cause:</span> {(row as any).cause_of_failure || '—'}</div>
                              <div><span className="font-medium">Risk controls:</span> {Array.isArray((row as any).risk_control_measures) ? (row as any).risk_control_measures.join('; ') : '—'}</div>
                              <div><span className="font-medium">Traceability:</span> {[].concat((row as any).verification_reference || [], (row as any).validation_reference || []).join('; ') || '—'}</div>
                            </div>
                            {(row as any).id && !row.approved && (
                              <div className="mt-3">
                                <button
                                  onClick={async (e) => {
                                    e.stopPropagation();
                                    if (!currentProject?.id || !(row as any).id) return;
                                    setFillGapsId((row as any).id);
                                    try {
                                      await fillGapsHazardAnalysisItem(currentProject.id, (row as any).id);
                                      handleGeneratePreview();
                                    } finally {
                                      setFillGapsId(null);
                                    }
                                  }}
                                  disabled={fillGapsId !== null}
                                  className="px-3 py-1 rounded bg-purple-300 text-gray-900 text-xs hover:bg-purple-400 disabled:opacity-50"
                                >
                                  {fillGapsId === (row as any).id ? 'Filling...' : 'Fill gaps with AI'}
                                </button>
                              </div>
                            )}
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
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
              className="px-6 py-2 bg-purple-300 text-gray-900 rounded-md hover:bg-purple-400"
            >
              View HTML Preview
            </button>
            <button
              onClick={handleOpenProjectModal}
              disabled={loading}
              className="px-6 py-2 bg-purple-300 text-gray-900 rounded-md hover:bg-purple-400 disabled:opacity-50"
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
              <h3 className="text-xl font-semibold text-gray-900">Hazard Analysis Preview</h3>
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
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Save Hazard Analysis to Project</h3>
            
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

export default HazardAnalysisPage;
