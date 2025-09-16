import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ProjectDataViewer from '../components/ProjectDataViewer';
import { exportNonConformanceData } from '../utils/exportUtils';

interface NonConformanceRow {
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

const NONCONFORMANCE_TYPES = [
  { key: 'product', label: 'Product Non-Conformance' },
  { key: 'process', label: 'Process Non-Conformance' },
  { key: 'system', label: 'System Non-Conformance' },
];

const NonConformancePage: React.FC = () => {
  const navigate = useNavigate();
  const [issueDescription, setIssueDescription] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [nonConformanceType, setNonConformanceType] = useState('product');
  const [nonConformanceData, setNonConformanceData] = useState<{ [key: string]: NonConformanceRow[] }>({});
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

  const generateNonConformance = async () => {
    console.log('generateNonConformance called');
    console.log('issueDescription:', issueDescription);
    
    if (!issueDescription.trim()) {
      console.log('No issue description provided, using default');
      setIssueDescription('Default non-conformance issue for testing');
    }
    
    setIsGenerating(true);
    console.log('Setting isGenerating to true');
    
    try {
      // Call backend API
      console.log('Starting AI generation via backend API...');
      const api = window.fmeaApi;
      
      const response = await api.generateNonConformance({
        issue_description: issueDescription || 'Default non-conformance issue',
        nonconformance_type: nonConformanceType
      });
      
      console.log('Backend API response:', response);
      
      if (response.nonconformance_data && response.nonconformance_data.length > 0) {
        // Convert backend data to frontend format
        const convertedData = response.nonconformance_data.map((item: any) => ({
          id: item.id || `NC-${Date.now().toString().slice(-6)}`,
          issueDescription: item.issue_description || 'Default non-conformance issue',
          source: item.source || "AI Generated",
          detectionDate: item.detection_date || new Date().toISOString().slice(0, 10),
          severity: item.severity || "Medium",
          rootCause: item.root_cause || "AI generated root cause analysis",
          correctiveAction: item.corrective_action || "AI generated corrective action",
          preventiveAction: item.preventive_action || "AI generated preventive action",
          actionOwner: item.action_owner || "AI Assistant",
          dueDate: item.due_date || "2025-12-31",
          status: item.status || "Open",
          effectivenessCheckPlan: item.investigation_details || "AI generated investigation details",
          fmeaLink: item.fmea_link || "Link to FMEA-001",
          regulatoryImpact: item.regulatory_impact || "No immediate regulatory filing.",
          closureSummary: item.closure_summary || "AI generated closure summary.",
          milestones: item.milestones || "Phase 1 complete by 2025-09-30",
          riskControlsUpdate: item.risk_controls_update || "Updated risk control document RC-005.",
          analysis_timestamp: item.analysis_timestamp || new Date().toISOString(),
          version: item.version || "1.0"
        }));

        console.log('Converted non-conformance data:', convertedData);
        
        setNonConformanceData({
          [nonConformanceType]: convertedData,
        });
        setMockFlag(response.mock);
        setShowTable(true);
        setIsGenerating(false);
      } else {
        console.log('No data received from backend');
        setIsGenerating(false);
      }
    } catch (error: any) {
      console.error('Error generating Non-Conformance:', error);
      console.error('Error details:', error.response?.data || error.message);
      alert('Failed to generate Non-Conformance. Please try again.');
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
      case 'open': return 'bg-yellow-100 text-yellow-800';
      case 'in progress': return 'bg-blue-100 text-blue-800';
      case 'closed': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-orange-100 text-orange-800';
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
          description: `Non-Conformance for: ${issueDescription}`
        });
        projectId = createResponse.id;
      }

      if (!projectId) {
        setSaveError('Please select a project or create a new one');
        setIsSaving(false);
        return;
      }

      // Get the current Non-Conformance data
      const currentData = nonConformanceData[nonConformanceType] || [];
      if (currentData.length === 0) {
        setSaveError('No Non-Conformance data to save. Please generate data first.');
        setIsSaving(false);
        return;
      }

      // Save each Non-Conformance entry to the project
      const savePromises = currentData.map(async (row) => {
        const nonconformanceData = {
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
          investigation_details: row.effectivenessCheckPlan,
          regulatory_impact: row.regulatoryImpact,
          closure_summary: row.closureSummary,
          analysis_timestamp: row.analysis_timestamp || new Date().toISOString(),
          version: row.version || '1.0'
        };

        return api.saveNonConformanceToProject(projectId, nonconformanceData);
      });

      const results = await Promise.all(savePromises);
      console.log('Non-Conformance save results:', results);

      const failedSaves = results.filter(result => {
        return result && (result.error || result.detail || !result.id);
      });

      if (failedSaves.length === 0) {
        setShowProjectModal(false);
        setSelectedProjectId('');
        setNewProjectName('');
        alert(`Successfully saved ${currentData.length} Non-Conformance entries to project!`);
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
    if (!issueDescription.trim()) {
      alert('Please enter an issue description first');
      return;
    }
    await generateNonConformance();
  };

  const handleExportNonConformance = (format: 'csv' | 'pdf') => {
    const data = nonConformanceData[nonConformanceType] || [];
    if (data.length === 0) {
      alert('No data to export');
      return;
    }
    exportNonConformanceData(data, format);
  };

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Create Non-Conformance</h2>
          <p className="text-gray-600">Generate comprehensive non-conformance analysis using AI-powered insights</p>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {NONCONFORMANCE_TYPES.map((type) => (
                <button
                  key={type.key}
                  onClick={() => setNonConformanceType(type.key)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    nonConformanceType === type.key
                      ? 'border-purple-500 text-purple-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {type.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Input Form */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <div className="mb-6">
            <label htmlFor="issueDescription" className="block text-sm font-medium text-gray-700 mb-2">
              Issue Description
            </label>
            <textarea
              id="issueDescription"
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-purple-500 focus:border-purple-500"
              placeholder="Describe the non-conformance issue in detail..."
              value={issueDescription}
              onChange={(e) => setIssueDescription(e.target.value)}
            />
          </div>

          <div className="flex justify-center">
            <button
              onClick={() => {
                console.log('Generate Non-Conformance button clicked');
                generateNonConformance();
              }}
              disabled={isGenerating}
              className="bg-purple-600 text-white px-8 py-3 rounded-md font-medium hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {isGenerating ? (
                <>
                  <i className="fa-solid fa-spinner fa-spin mr-2"></i>
                  Generating Non-Conformance...
                </>
              ) : (
                <>
                  <i className="fa-solid fa-magic mr-2"></i>
                  Generate Non-Conformance
                </>
              )}
            </button>
          </div>
        </div>

        {/* Results Table */}
        {showTable && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">Non-Conformance Analysis Results</h3>
                <div className="flex space-x-2">
                  <div className="relative group">
                    <button className="bg-purple-600 text-white px-4 py-2 rounded-md font-medium hover:bg-purple-700 flex items-center">
                      <i className="fa-solid fa-download mr-2"></i>
                      Export
                      <i className="fa-solid fa-chevron-down ml-2"></i>
                    </button>
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                      <div className="py-1">
                        <button
                          onClick={() => handleExportNonConformance('csv')}
                          className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          <i className="fa-solid fa-file-csv mr-2"></i>
                          Export as CSV
                        </button>
                        <button
                          onClick={() => handleExportNonConformance('pdf')}
                          className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          <i className="fa-solid fa-file-pdf mr-2"></i>
                          Export as PDF
                        </button>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={handleOpenProjectModal}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
                  >
                    Save to Project
                  </button>
                  <button
                    onClick={handleAddMoreRows}
                    className="bg-purple-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-purple-700"
                  >
                    Add More Rows
                  </button>
                </div>
              </div>
              {mockFlag && (
                <div className="mt-2 text-sm text-yellow-600 bg-yellow-50 px-3 py-2 rounded-md">
                  <i className="fa-solid fa-exclamation-triangle mr-1"></i>
                  This is mock data for demonstration purposes
                </div>
              )}
              {mockFlag === false && (
                <div className="mt-2 text-sm text-green-600 bg-green-50 px-3 py-2 rounded-md">
                  <i className="fa-solid fa-check-circle mr-1"></i>
                  Generated using real AI
                </div>
              )}
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Issue Description
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Source
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Detection Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Severity
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Root Cause
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Corrective Action
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Preventive Action
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Action Owner
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Due Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Effectiveness Check Plan
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      FMEA Link
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Regulatory Impact
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Closure Summary
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Milestones
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Risk Controls Update
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {nonConformanceData[nonConformanceType]?.map((row, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {row.id}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                        {row.issueDescription}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {row.source}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {row.detectionDate}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getSeverityColor(row.severity)}`}>
                          {row.severity}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                        {row.rootCause}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                        {row.correctiveAction}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                        {row.preventiveAction}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {row.actionOwner}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {row.dueDate}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(row.status)}`}>
                          {row.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                        {row.effectivenessCheckPlan}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {row.fmeaLink}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                        {row.regulatoryImpact}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                        {row.closureSummary}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                        {row.milestones}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                        {row.riskControlsUpdate}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Summary Statistics */}
        {showTable && (
          <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                    <i className="fa-solid fa-exclamation-triangle text-purple-600"></i>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Total Non-Conformances</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {nonConformanceData[nonConformanceType]?.length || 0}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                    <i className="fa-solid fa-clock text-yellow-600"></i>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">In Progress</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {nonConformanceData[nonConformanceType]?.filter(row => row.status.toLowerCase() === 'in progress').length || 0}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                    <i className="fa-solid fa-check-circle text-green-600"></i>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Closed</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {nonConformanceData[nonConformanceType]?.filter(row => row.status.toLowerCase() === 'closed').length || 0}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                    <i className="fa-solid fa-exclamation-triangle text-red-600"></i>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">High Severity</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {nonConformanceData[nonConformanceType]?.filter(row => row.severity.toLowerCase() === 'high').length || 0}
                  </p>
                </div>
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
    </div>
  );
};

declare global {
  interface Window {
    fmeaApi: any;
  }
}

export default NonConformancePage; 