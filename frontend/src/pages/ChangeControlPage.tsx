import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ProjectDataViewer from '../components/ProjectDataViewer';
import { exportChangeControlData } from '../utils/exportUtils';

interface ChangeControlRow {
  id: string;
  changeDescription: string;
  changeType: string;
  requestor: string;
  requestDate: string;
  priority: string;
  impactLevel: string;
  affectedComponents: string;
  justification: string;
  proposedSolution: string;
  riskAssessment: string;
  approvalStatus: string;
  approvedBy: string;
  approvalDate: string;
  implementationPlan: string;
  verificationPlan: string;
  linkedFmea: string;
  linkedCapa: string;
  linkedNonConformance: string;
  regulatoryImpact: string;
  closureSummary: string;
  analysis_timestamp?: string;
  version?: string;
}

const CHANGE_CONTROL_TYPES = [
  { key: 'design', label: 'Design Change Control' },
];

const ChangeControlPage: React.FC = () => {
  const navigate = useNavigate();
  const [changeDescription, setChangeDescription] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [changeControlType, setChangeControlType] = useState('design');
  const [changeControlData, setChangeControlData] = useState<{ [key: string]: ChangeControlRow[] }>({});
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

  const handleGenerateChangeControl = async () => {
    if (!changeDescription.trim()) {
      alert('Please enter a change description');
      return;
    }
    setIsGenerating(true);
    try {
      console.log('Calling Change Control API with description:', changeDescription);
      // Call the real AI API using window.fmeaApi
      const response = await window.fmeaApi.generateChangeControl({
        change_description: changeDescription
      });
      console.log('API Response:', response);
      
      // Convert the API response to the local format
      const convertedData: ChangeControlRow[] = response.change_control_data.map((item: any) => ({
        id: item.id,
        changeDescription: item.change_description,
        changeType: "AI Generated",
        requestor: item.initiator,
        requestDate: item.date_initiated,
        priority: "Medium", // Default since API doesn't provide this
        impactLevel: "Medium", // Default since API doesn't provide this
        affectedComponents: item.impact_assessment,
        justification: item.actions_required,
        proposedSolution: item.actions_required,
        riskAssessment: item.impact_assessment,
        approvalStatus: item.status,
        approvedBy: item.action_owner,
        approvalDate: item.due_date,
        implementationPlan: item.actions_required,
        verificationPlan: item.closure_summary,
        linkedFmea: "Link to FMEA-001",
        linkedCapa: "Link to CAPA-002",
        linkedNonConformance: "Link to NC-003",
        regulatoryImpact: item.impact_assessment,
        closureSummary: item.closure_summary,
        analysis_timestamp: item.analysis_timestamp,
        version: item.version
      }));

      console.log('Converted data:', convertedData);
      setChangeControlData({
        design: convertedData,
      });
      setMockFlag(response.mock);
      setShowTable(true);
      setIsGenerating(false);
    } catch (error: any) {
      console.error('Error generating Change Control:', error);
      console.error('Error details:', error.response?.data || error.message);
      alert('Failed to generate Change Control. Please try again.');
      setIsGenerating(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'approved': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'implemented': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact.toLowerCase()) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
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
    console.log('View Project Data clicked for project:', project);
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
          description: `Change Control for: ${changeDescription}`
        });
        projectId = createResponse.id;
      }
      
      if (!projectId) {
        setSaveError('Please select a project or create a new one');
        setIsSaving(false);
        return;
      }
      
      // Get the current change control data
      const currentData = changeControlData[changeControlType] || [];
      if (currentData.length === 0) {
        setSaveError('No change control data to save. Please generate data first.');
        setIsSaving(false);
        return;
      }
      
      // Save each change control entry to the project
      const savePromises = currentData.map(async (row) => {
        const changeControlData = {
          change_description: row.changeDescription,
          initiator: row.requestor,
          date_initiated: row.requestDate,
          status: row.approvalStatus,
          impact_assessment: row.affectedComponents,
          actions_required: row.justification,
          action_owner: row.approvedBy,
          due_date: row.approvalDate,
          closure_summary: row.closureSummary,
          analysis_timestamp: row.analysis_timestamp || new Date().toISOString(),
          version: row.version || '1.0'
        };
        
        return api.saveChangeControlToProject(projectId, changeControlData);
      });
      
      const results = await Promise.all(savePromises);
      console.log('Change Control save results:', results);
      
      const failedSaves = results.filter(result => {
        return result && (result.error || result.detail || !result.id);
      });
      
      if (failedSaves.length === 0) {
        setShowProjectModal(false);
        setSelectedProjectId('');
        setNewProjectName('');
        alert(`Successfully saved ${currentData.length} Change Control entries to project!`);
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
    if (!changeDescription.trim()) {
      alert('Please enter a change description first');
      return;
    }
    await handleGenerateChangeControl();
  };

  const handleExportChangeControl = (format: 'csv' | 'pdf') => {
    const data = changeControlData[changeControlType] || [];
    if (data.length === 0) {
      alert('No data to export');
      return;
    }
    exportChangeControlData(data, format);
  };

  return (
    <>
      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          {/* Header Section */}
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Create Change Control</h2>
            <p className="text-gray-600">Generate comprehensive change control analysis using AI-powered insights</p>
          </div>

          {/* Tabs */}
          <div className="mb-6">
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex space-x-8">
                {CHANGE_CONTROL_TYPES.map((type) => (
                  <button
                    key={type.key}
                    onClick={() => setChangeControlType(type.key)}
                    className={`py-2 px-1 border-b-2 font-medium text-sm ${
                      changeControlType === type.key
                        ? 'border-blue-500 text-blue-600'
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
              <label htmlFor="changeDescription" className="block text-sm font-medium text-gray-700 mb-2">
                Change Description
              </label>
              <textarea
                id="changeDescription"
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Describe the change request in detail..."
                value={changeDescription}
                onChange={(e) => setChangeDescription(e.target.value)}
              />
            </div>

            <div className="flex justify-center">
              <button
                onClick={handleGenerateChangeControl}
                disabled={isGenerating}
                className="bg-blue-600 text-white px-8 py-3 rounded-md font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                {isGenerating ? (
                  <>
                    <i className="fa-solid fa-spinner fa-spin mr-2"></i>
                    Generating Change Control...
                  </>
                ) : (
                  <>
                    <i className="fa-solid fa-magic mr-2"></i>
                    Generate Change Control
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
                  <h3 className="text-lg font-medium text-gray-900">Change Control Analysis Results</h3>
                  <div className="flex space-x-2">
                    <div className="relative group">
                      <button className="bg-blue-600 text-white px-4 py-2 rounded-md font-medium hover:bg-blue-700 flex items-center">
                        <i className="fa-solid fa-download mr-2"></i>
                        Export
                        <i className="fa-solid fa-chevron-down ml-2"></i>
                      </button>
                      <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                        <div className="py-1">
                          <button
                            onClick={() => handleExportChangeControl('csv')}
                            className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          >
                            <i className="fa-solid fa-file-csv mr-2"></i>
                            Export as CSV
                          </button>
                          <button
                            onClick={() => handleExportChangeControl('pdf')}
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
                      className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
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
                        Change ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Change Description
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Change Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Requestor
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Request Date
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Priority
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Impact Level
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Affected Components
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Justification
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Proposed Solution
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Risk Assessment
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Approval Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Approved By
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Approval Date
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Implementation Plan
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Verification Plan
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Linked FMEA
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Linked CAPA
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Linked Non-Conformance
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Regulatory Impact
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Closure Summary
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {changeControlData[changeControlType]?.map((row, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {row.id}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                          {row.changeDescription}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {row.changeType}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {row.requestor}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {row.requestDate}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getPriorityColor(row.priority)}`}>
                            {row.priority}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getImpactColor(row.impactLevel)}`}>
                            {row.impactLevel}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                          {row.affectedComponents}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                          {row.justification}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                          {row.proposedSolution}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                          {row.riskAssessment}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(row.approvalStatus)}`}>
                            {row.approvalStatus}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {row.approvedBy}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {row.approvalDate}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                          {row.implementationPlan}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                          {row.verificationPlan}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {row.linkedFmea}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {row.linkedCapa}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {row.linkedNonConformance}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                          {row.regulatoryImpact}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                          {row.closureSummary}
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
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <i className="fa-solid fa-exchange-alt text-blue-600"></i>
                    </div>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Total Change Requests</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {changeControlData[changeControlType]?.length || 0}
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
                    <p className="text-sm font-medium text-gray-500">Pending Approval</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {changeControlData[changeControlType]?.filter(row => row.approvalStatus.toLowerCase() === 'pending').length || 0}
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
                    <p className="text-sm font-medium text-gray-500">Approved</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {changeControlData[changeControlType]?.filter(row => row.approvalStatus.toLowerCase() === 'approved').length || 0}
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
                    <p className="text-sm font-medium text-gray-500">High Priority</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {changeControlData[changeControlType]?.filter(row => row.priority.toLowerCase() === 'high').length || 0}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

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
    </>
  );
};

declare global {
  interface Window {
    fmeaApi: any;
  }
}

export default ChangeControlPage; 