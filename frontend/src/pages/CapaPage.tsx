import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useProject } from '../contexts/ProjectContext';
import ProjectDataViewer from '../components/ProjectDataViewer';
import { generateCapa as generateCapaAPI } from '../services/apiService';
import { exportCapaData } from '../utils/exportUtils';
import { UpstreamLinksPanel } from '../components/Traceability/UpstreamLinksPanel';

interface CapaRow {
  id: string;
  issueDescription: string;
  source: string;
  detectionDate: string;
  severity: string;
  rootCause: string;
  correctiveAction: string;
  preventiveAction: string;
  actionOwner: string;
  dueDate: string;
  status: string;
  effectivenessCheckPlan: string;
  fmeaLink: string;
  regulatoryImpact: string;
  closureSummary: string;
  milestones: string;
  riskControlsUpdate: string;
  analysis_timestamp?: string;
  version?: string;
}

const CAPA_TYPES = [
  { key: 'corrective', label: 'Corrective Action' },
];

const CapaPage: React.FC = () => {
  const navigate = useNavigate();
  const { capaId } = useParams<{ capaId?: string }>();
  const { currentProject } = useProject();
  const [issueDescription, setIssueDescription] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [capaType, setCapaType] = useState('corrective');
  const [capaData, setCapaData] = useState<{ [key: string]: CapaRow[] }>({});
  const [showTable, setShowTable] = useState(false);
  const [showProjectModal, setShowProjectModal] = useState(false);
  const [projects, setProjects] = useState<any[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');
  const [newProjectName, setNewProjectName] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState('');
  const [creatingNew, setCreatingNew] = useState(false);
  const [mockFlag, setMockFlag] = useState<boolean | null>(null);
  const [showProjectDataViewer, setShowProjectDataViewer] = useState(false);
  const [selectedProjectForViewer, setSelectedProjectForViewer] = useState<any>(null);

  const generateCapa = async () => {
    if (!issueDescription.trim()) {
      alert('Please enter an issue description');
      return;
    }
    setIsGenerating(true);
    try {
      // Call backend API
      const response = await generateCapaAPI(issueDescription, capaType);
      
      // Transform the response data to match our interface
      const transformedData: CapaRow[] = response.capa_data.map((item: any) => ({
        id: item.id,
        issueDescription: item.issue_description,
        source: item.source,
        detectionDate: item.detection_date,
        severity: item.severity,
        rootCause: item.root_cause,
        correctiveAction: item.corrective_action,
        preventiveAction: item.preventive_action,
        actionOwner: item.action_owner,
        dueDate: item.due_date,
        status: item.status,
        effectivenessCheckPlan: item.effectiveness_check_plan,
        fmeaLink: item.fmea_link,
        regulatoryImpact: item.regulatory_impact,
        closureSummary: item.closure_summary,
        milestones: item.milestones,
        riskControlsUpdate: item.risk_controls_update,
        analysis_timestamp: item.analysis_timestamp,
        version: item.version
      }));

      setCapaData({
        [capaType]: transformedData,
      });
      setMockFlag(response.mock);
      setShowTable(true);
      setIsGenerating(false);
    } catch (error) {
      console.error('Error generating CAPA:', error);
      alert('Failed to generate CAPA. Please try again.');
      setIsGenerating(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'open': return 'bg-red-100 text-red-800';
      case 'in progress': return 'bg-yellow-100 text-yellow-800';
      case 'closed': return 'bg-green-100 text-green-800';
      case 'ineffective': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleOpenProjectModal = async () => {
    try {
      const api = window.fmeaApi;
      console.log('Fetching projects...');
      console.log('fmeaApi token:', api.token);
      console.log('fmeaApi available:', !!api);
      
      const response = await api.getProjects();
      console.log('Projects response:', response);
      
      // API returns array directly
      const projectList = Array.isArray(response) ? response : [];
      
      console.log('Final project list:', projectList);
      console.log('Projects count:', projectList.length);
      setProjects(projectList);
      setShowProjectModal(true);
    } catch (error) {
      console.error('Error fetching projects:', error);
      console.error('Error details:', error instanceof Error ? error.message : 'Unknown error');
      alert('Failed to fetch projects. Please check if you are authenticated.');
    }
  };

  const handleViewProjectData = (project: any) => {
    setSelectedProjectForViewer(project);
    setShowProjectDataViewer(true);
  };

  const handleSaveToProject = async () => {
    if (!selectedProjectId && !newProjectName.trim()) {
      alert('Please select a project or enter a new project name');
      return;
    }
    setIsSaving(true);
    setSaveError('');
    try {
      const api = window.fmeaApi;
      let projectId = selectedProjectId;
      
      // Create new project if needed
      if (!projectId && newProjectName.trim()) {
        const createResponse = await api.createProject({
          name: newProjectName,
          description: `CAPA for: ${issueDescription}`
        });
        projectId = createResponse.id;
      }
      
      if (!projectId) {
        setSaveError('Please select a project or create a new one');
        setIsSaving(false);
        return;
      }
      
      // Get the current CAPA data
      const currentData = capaData[capaType] || [];
      if (currentData.length === 0) {
        setSaveError('No CAPA data to save. Please generate data first.');
        setIsSaving(false);
        return;
      }
      
      // Save each CAPA entry to the project
      const savePromises = currentData.map(async (row) => {
        const capaData = {
          issue_description: row.issueDescription,
          source: row.source,
          detection_date: row.detectionDate,
          severity: row.severity,
          root_cause: row.rootCause,
          corrective_action: row.correctiveAction,
          preventive_action: row.preventiveAction,
          action_owner: row.actionOwner,
          due_date: row.dueDate,
          status: row.status,
          effectiveness_check_plan: row.effectivenessCheckPlan,
          fmea_link: row.fmeaLink,
          regulatory_impact: row.regulatoryImpact,
          closure_summary: row.closureSummary,
          milestones: row.milestones,
          risk_controls_update: row.riskControlsUpdate,
          analysis_timestamp: row.analysis_timestamp || new Date().toISOString(),
          version: row.version || '1.0'
        };
        
        return api.saveCapaToProject(projectId, capaData);
      });
      
      const results = await Promise.all(savePromises);
      console.log('CAPA save results:', results);
      
      const failedSaves = results.filter(result => {
        return result && (result.error || result.detail || !result.id);
      });
      
      if (failedSaves.length === 0) {
        setShowProjectModal(false);
        setSelectedProjectId('');
        setNewProjectName('');
        alert(`Successfully saved ${currentData.length} CAPA entries to project!`);
      } else {
        console.error('Failed saves:', failedSaves);
        setSaveError(`Failed to save ${failedSaves.length} entries. Please try again.`);
      }
    } catch (error) {
      console.error('Error saving to project:', error);
      setSaveError('Failed to save to project. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddMoreRows = async () => {
    try {
      const api = window.fmeaApi;
      const additionalCapa: CapaRow = {
        id: `CAPA-${Date.now().toString().slice(-6)}`,
        issueDescription: "Additional CAPA entry",
        source: "Manual Entry",
        detectionDate: new Date().toISOString().slice(0, 10),
        severity: "Low",
        rootCause: "Additional root cause analysis.",
        correctiveAction: "Additional corrective action.",
        preventiveAction: "Additional preventive action.",
        actionOwner: "Quality Team",
        dueDate: "2025-12-31",
        status: "Open",
        effectivenessCheckPlan: "Additional effectiveness check.",
        fmeaLink: "Link to FMEA-002",
        regulatoryImpact: "No regulatory impact.",
        closureSummary: "Additional closure summary.",
        milestones: "Additional milestones.",
        riskControlsUpdate: "Additional risk controls update.",
        analysis_timestamp: new Date().toISOString(),
        version: "1.1"
      };

      setCapaData(prev => ({
        ...prev,
        [capaType]: [...(prev[capaType] || []), additionalCapa]
      }));
    } catch (error) {
      console.error('Error adding more rows:', error);
      alert('Failed to add more rows. Please try again.');
    }
  };

  const handleExportCapa = (format: 'csv' | 'pdf') => {
    const data = capaData[capaType] || [];
    if (data.length === 0) {
      alert('No data to export');
      return;
    }
    exportCapaData(data, format);
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Create New CAPA</h1>
        <p className="text-gray-600">Enter issue details and generate an AI-powered CAPA analysis</p>
      </div>

      {/* Upstream Links Panel - Show if viewing a specific CAPA */}
      {capaId && currentProject?.id && (
        <div className="mb-6">
          <UpstreamLinksPanel
            projectId={currentProject.id}
            artifactType="capa"
            artifactId={capaId}
            onNavigate={(route) => navigate(route)}
          />
        </div>
      )}

      {/* CAPA Type Tabs - always visible */}
      <div className="flex space-x-2 mb-6">
        {CAPA_TYPES.map(type => (
          <button
            key={type.key}
            onClick={() => { setCapaType(type.key); setShowTable(!!capaData[type.key]); }}
            className={`px-4 py-2 rounded-t-md font-medium border-b-2 ${capaType === type.key ? 'bg-blue-100 border-blue-600 text-blue-800' : 'bg-gray-100 border-transparent text-gray-600'}`}
          >
            {type.label}
          </button>
        ))}
      </div>

      {/* Issue Input Form */}
      {!showTable && (
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="max-w-2xl">
            <label htmlFor="issueDescription" className="block text-sm font-medium text-gray-700 mb-2">
              Issue Description
            </label>
            <textarea
              id="issueDescription"
              value={issueDescription}
              onChange={(e) => setIssueDescription(e.target.value)}
              placeholder="e.g., Customer complaint about device malfunction, Quality control failure, Regulatory non-compliance"
              className="w-full px-4 py-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              rows={3}
            />
            <div className="mt-6">
              <button
                onClick={generateCapa}
                disabled={isGenerating || !issueDescription.trim()}
                className="bg-blue-600 text-white px-6 py-3 rounded-md font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center"
              >
                {isGenerating ? (
                  <>
                    <i className="fa-solid fa-spinner fa-spin mr-2"></i>
                    Generating...
                  </>
                ) : (
                  <>
                    <i className="fa-solid fa-magic mr-2"></i>
                    Generate AI CAPA
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* CAPA Table */}
      {showTable && (
        <div className="mb-4">
          {mockFlag === true && (
            <div className="bg-yellow-100 text-yellow-800 px-4 py-2 rounded mb-2 font-semibold">
              Mock Data (not AI generated)
            </div>
          )}
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-900">CAPA Analysis ({capaData[capaType]?.length || 0} entries)</h3>
                <div className="flex space-x-2">
                  <div className="relative group">
                    <button className="bg-blue-600 text-white px-4 py-2 rounded-md font-medium hover:bg-blue-700 flex items-center">
                      <i className="fa-solid fa-download mr-2"></i>
                      Export CAPA
                      <i className="fa-solid fa-chevron-down ml-2"></i>
                    </button>
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                      <div className="py-1">
                        <button
                          onClick={() => handleExportCapa('csv')}
                          className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          <i className="fa-solid fa-file-csv mr-2"></i>
                          Export as CSV
                        </button>
                        <button
                          onClick={() => handleExportCapa('pdf')}
                          className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          <i className="fa-solid fa-file-pdf mr-2"></i>
                          Export as PDF
                        </button>
                      </div>
                    </div>
                  </div>
                  <button className="bg-green-600 text-white px-4 py-2 rounded-md font-medium hover:bg-green-700" onClick={handleOpenProjectModal}>
                    <i className="fa-solid fa-save mr-2"></i>
                    Save to Project
                  </button>
                  <button className="bg-gray-600 text-white px-4 py-2 rounded-md font-medium hover:bg-gray-700" onClick={handleAddMoreRows}>
                    <i className="fa-solid fa-plus mr-2"></i>
                    Add More CAPA
                  </button>
                </div>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Issue Description</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Source</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Detection Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Root Cause</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Corrective Action</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Preventive Action</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action Owner</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Due Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {capaData[capaType]?.map((row) => (
                    <tr key={row.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                        <div className="truncate" title={row.issueDescription}>
                          {row.issueDescription}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">{row.source}</td>
                      <td className="px-6 py-4 text-sm text-gray-900">{row.detectionDate}</td>
                      <td className="px-6 py-4 text-sm">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getSeverityColor(row.severity)}`}>
                          {row.severity}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                        <div className="truncate" title={row.rootCause}>
                          {row.rootCause}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                        <div className="truncate" title={row.correctiveAction}>
                          {row.correctiveAction}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                        <div className="truncate" title={row.preventiveAction}>
                          {row.preventiveAction}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">{row.actionOwner}</td>
                      <td className="px-6 py-4 text-sm text-gray-900">{row.dueDate}</td>
                      <td className="px-6 py-4 text-sm">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(row.status)}`}>
                          {row.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <h3 className="text-sm font-medium text-gray-500">Total CAPAs</h3>
              <p className="text-2xl font-bold text-blue-600">{capaData[capaType]?.length || 0}</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <h3 className="text-sm font-medium text-gray-500">High Severity</h3>
              <p className="text-2xl font-bold text-red-600">
                {capaData[capaType]?.filter(row => row.severity.toLowerCase() === 'high').length || 0}
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <h3 className="text-sm font-medium text-gray-500">Open Status</h3>
              <p className="text-2xl font-bold text-orange-600">
                {capaData[capaType]?.filter(row => row.status.toLowerCase() === 'open').length || 0}
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <h3 className="text-sm font-medium text-gray-500">Completion Rate</h3>
              <p className="text-2xl font-bold text-blue-600">
                {Math.round((capaData[capaType]?.filter(row => row.status.toLowerCase() === 'closed').length || 0) / (capaData[capaType]?.length || 1) * 100)}%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Project Modal */}
      {showProjectModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Save to Project</h3>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Select Existing Project</label>
                <div className="space-y-2">
                  {projects.length === 0 ? (
                    <div className="text-center py-4 text-gray-500">
                      <p>No projects found. Create a new project to save your data.</p>
                      <p className="text-sm mt-2">Debug: Projects array length: {projects.length}</p>
                    </div>
                  ) : (
                    <>
                      <div className="text-sm text-gray-600 mb-2">Debug: Found {projects.length} projects</div>
                      <div className="text-xs text-gray-500 mb-2">
                        Project IDs: {projects.map(p => p.id).join(', ')}
                      </div>
                      {projects.map((project) => (
                        <div 
                          key={project.id} 
                          className="flex items-center justify-between p-3 border border-gray-200 rounded-md hover:bg-gray-50 cursor-pointer"
                          onClick={() => {
                            console.log('Project row clicked:', project.id);
                            setSelectedProjectId(project.id.toString());
                          }}
                        >
                          <div className="flex items-center space-x-3">
                            <input
                              type="radio"
                              id={`project-${project.id}`}
                              name="selectedProject"
                              value={project.id.toString()}
                              checked={selectedProjectId === project.id.toString()}
                              onChange={(e) => {
                                console.log('Project selected:', e.target.value);
                                setSelectedProjectId(e.target.value);
                              }}
                              className="text-blue-600 focus:ring-blue-500 cursor-pointer"
                              onClick={(e) => e.stopPropagation()}
                            />
                            <label htmlFor={`project-${project.id}`} className="text-sm font-medium text-gray-900 cursor-pointer">
                              {project.name}
                            </label>
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleViewProjectData(project);
                            }}
                            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                          >
                            View Data
                          </button>
                        </div>
                      ))}
                    </>
                  )}
                </div>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Or Create New Project</label>
                <input
                  type="text"
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  placeholder="Enter new project name..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              {saveError && (
                <div className="mb-4 text-sm text-red-600 bg-red-50 px-3 py-2 rounded-md">
                  {saveError}
                </div>
              )}

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowProjectModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveToProject}
                  disabled={isSaving}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {isSaving ? 'Saving...' : 'Save'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Project Data Viewer Modal */}
      {showProjectDataViewer && selectedProjectForViewer && (
        <ProjectDataViewer
          selectedProject={selectedProjectForViewer}
          onClose={() => {
            setShowProjectDataViewer(false);
            setSelectedProjectForViewer(null);
          }}
        />
      )}
    </div>
  );
};

export default CapaPage;

declare global {
  interface Window {
    fmeaApi: any;
  }
} 