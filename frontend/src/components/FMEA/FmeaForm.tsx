import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ProjectDataViewer from '../ProjectDataViewer';
import DashboardLayout from '../DashboardLayout';
// FMEAApi is attached to window by fmea.js, so we will use it from window

interface FmeaRow {
  id: string;
  component: string;
  function: string;
  failureMode: string;
  potentialEffect: string;
  severity: number;
  potentialCauses: string;
  occurrence: number;
  currentControls: string;
  detection: number;
  rpn: number;
  recommendedActions: string;
  responsible: string;
  targetDate: string;
  actionsTaken: string;
  finalSeverity: number;
  finalOccurrence: number;
  finalDetection: number;
  finalRpn: number;
  analysis_timestamp?: string;
  version?: string;
  processStep?: string;
  processRequirements?: string;
}

const FMEA_TYPES = [
  { key: 'dfmea', label: 'DFMEA' },
  { key: 'pfmea', label: 'PFMEA' },
  { key: 'ufmea', label: 'UFMEA' },
];

const FmeaForm: React.FC = () => {
  const navigate = useNavigate();
  const [componentName, setComponentName] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [fmeaType, setFmeaType] = useState('dfmea');
  const [fmeaData, setFmeaData] = useState<{ [key: string]: FmeaRow[] }>({});
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

  const generateFmea = async () => {
    if (!componentName.trim()) {
      alert('Please enter a component name');
      return;
    }
    setIsGenerating(true);
    try {
      const api = window.fmeaApi;
      let dfmeaData, pfmeaData, ufmeaData;
      let mock = false;
      // Always generate DFMEA and UFMEA from dfmea endpoint for now
      const dfmeaResult = await api.getFMEAByType('dfmea', componentName);
      dfmeaData = dfmeaResult.fmea_data;
      ufmeaData = dfmeaResult.fmea_data;
      mock = dfmeaResult.mock;
      if (fmeaType === 'pfmea') {
        const pfmeaResult = await api.getFMEAByType('pfmea', componentName);
        pfmeaData = pfmeaResult.fmea_data.map((row: any) => {
          const processStep = row.processStep || row.function;
          const processRequirements = row.processRequirements || row.failureMode;
          const { function: _func, failureMode, ...rest } = row;
          return { ...rest, processStep, processRequirements };
        });
        mock = pfmeaResult.mock;
      } else {
        pfmeaData = dfmeaData.map((row: any) => {
          const processStep = row.processStep || row.function;
          const processRequirements = row.processRequirements || row.failureMode;
          const { function: _func, failureMode, ...rest } = row;
          return { ...rest, processStep, processRequirements };
        });
      }
      setFmeaData({
        dfmea: dfmeaData,
        pfmea: pfmeaData,
        ufmea: ufmeaData,
      });
      setMockFlag(mock);
      setShowTable(true);
      setIsGenerating(false);

      // Automatically export first 10 FMEA rows to MasterControl (creates 10 separate forms)
      if (dfmeaData && dfmeaData.length > 0) {
        try {
          const rowsToExport = dfmeaData.slice(0, 10); // Get first 10 rows
          console.log(`Auto-exporting first ${rowsToExport.length} FMEA rows to MasterControl (creating ${rowsToExport.length} forms)`);
          
          const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
          
          // Export each row separately to create individual MasterControl forms
          for (let i = 0; i < rowsToExport.length; i++) {
            const row = rowsToExport[i];
            console.log(`Exporting row ${i + 1} of ${rowsToExport.length} to MasterControl:`, row);
            
            // Transform FMEA row to MasterControl format
            const mcRow = {
              "COMPONENT": row.component || componentName,
              "FUNCTION": row.function || '',
              "FAILURE MODE": row.failureMode || '',
              "EFFECTS": row.potentialEffect || '',
              "SEVERITY": row.severity || 1,
              "CAUSES": row.potentialCauses || '',
              "OCCURRENCE": row.occurrence || 1,
              "CONTROLS": row.recommendedActions || '',
              "DETECTION": row.detection || 1,
              "RPN": row.rpn || (row.severity || 1) * (row.occurrence || 1) * (row.detection || 1),
              "ACTIONS": row.actionsTaken || '',
              "OWNER": '',
              "DUE DATE": '',
              "STATUS": '',
              "DOC LINK": ''
            };

            try {
              // Call MasterControl export endpoint for this row
              const response = await fetch(`${apiBaseUrl}/integrations/mastercontrol/export`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                  rows: [mcRow],
                  rate_limit_sec: 0.0
                })
              });

              if (response.ok) {
                const result = await response.json();
                if (result.summary && result.summary.success > 0) {
                  console.log(`✅ Row ${i + 1} exported to MasterControl (form ${i + 1} created)`);
                } else {
                  console.warn(`⚠️ Row ${i + 1} export completed but may have issues:`, result);
                }
              } else {
                const errorText = await response.text();
                console.error(`❌ Row ${i + 1} export failed:`, response.status, errorText);
              }
            } catch (rowError) {
              console.error(`Error exporting row ${i + 1} to MasterControl:`, rowError);
            }
            
            // Small delay between exports to avoid rate limiting
            if (i < rowsToExport.length - 1) {
              await new Promise(resolve => setTimeout(resolve, 100));
            }
          }
          
          console.log(`✅ Completed exporting ${rowsToExport.length} FMEA rows to MasterControl (${rowsToExport.length} forms created)`);
        } catch (exportError) {
          // Don't fail FMEA generation if MasterControl export fails
          console.error('Error exporting to MasterControl (non-blocking):', exportError);
        }
      }
    } catch (error) {
      console.error('Error generating FMEA:', error);
      alert('Failed to generate FMEA. Please try again.');
      setIsGenerating(false);
    }
  };

  const getSeverityColor = (severity: number) => {
    if (severity >= 9) return 'bg-red-100 text-red-800';
    if (severity >= 7) return 'bg-orange-100 text-orange-800';
    if (severity >= 5) return 'bg-yellow-100 text-yellow-800';
    return 'bg-green-100 text-green-800';
  };

  const getRpnColor = (rpn: number) => {
    if (rpn >= 200) return 'bg-red-100 text-red-800';
    if (rpn >= 100) return 'bg-orange-100 text-orange-800';
    if (rpn >= 50) return 'bg-yellow-100 text-yellow-800';
    return 'bg-green-100 text-green-800';
  };

  const getImprovementColor = (originalRpn: number, finalRpn: number) => {
    const improvement = originalRpn - finalRpn;
    const percentage = (improvement / originalRpn) * 100;
    if (percentage >= 50) return 'bg-green-100 text-green-800';
    if (percentage >= 25) return 'bg-yellow-100 text-yellow-800';
    return 'bg-gray-100 text-gray-800';
  };

  const handleOpenProjectModal = async () => {
    setSaveError('');
    setCreatingNew(false);
    setNewProjectName('');
    setSelectedProjectId('');
    setShowProjectModal(true);
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
    } catch (e) {
      console.error('Error fetching projects:', e);
      console.error('Error details:', e instanceof Error ? e.message : 'Unknown error');
      setSaveError('Failed to fetch projects. Please check if you are authenticated.');
    }
  };

  const handleViewProjectData = (project: any) => {
    setSelectedProjectForViewer(project);
    setShowProjectDataViewer(true);
  };

  const handleSaveToProject = async () => {
    setIsSaving(true);
    setSaveError('');
    let projectId = selectedProjectId;
    const api = window.fmeaApi;
    try {
      if (creatingNew) {
        const projectNameToUse = newProjectName.trim() ? newProjectName : "Untitled Project";
        const newProject = await api.createProject({ name: projectNameToUse, description: "" });
        projectId = newProject.id;
      }
      if (!projectId) {
        setSaveError('Please select or create a project');
        setIsSaving(false);
        return;
      }
      for (const row of fmeaData[fmeaType]) {
        // Map frontend row to backend schema
        const backendRow = {
          component: row.component,
          failure_mode: row.failureMode,
          effect: row.potentialEffect,
          cause: row.potentialCauses,
          severity: row.severity,
          occurrence: row.occurrence,
          detection: row.detection,
          rpn: row.rpn,
          mitigation: row.currentControls, // or row.mitigation if available
          action_taken: row.actionsTaken,
          revised_severity: row.finalSeverity,
          revised_occurrence: row.finalOccurrence,
          revised_detection: row.finalDetection,
          revised_rpn: row.finalRpn,
          analysis_timestamp: row.analysis_timestamp,
          version: row.version,
          analyst_name: (row as any).analyst_name,
          analyst_email: (row as any).analyst_email,
          analyst_role: (row as any).analyst_role,
        };
        await api.createFMEA(projectId, backendRow);
      }
      setShowProjectModal(false);
      alert('FMEA rows saved to project!');
    } catch (e) {
      setSaveError('Failed to save FMEA rows');
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddMoreRows = async () => {
    const newComponent = window.prompt('Enter another component name to generate FMEA rows:');
    if (!newComponent || !newComponent.trim()) return;
    setIsGenerating(true);
    try {
      const api = window.fmeaApi;
      const data = await api.getFMEAByType(fmeaType, newComponent.trim());
      setFmeaData(prev => ({
        ...prev,
        [fmeaType]: prev[fmeaType] ? [...prev[fmeaType], ...data.fmea_data] : [...data.fmea_data],
      }));
      setShowTable(true);
    } catch (error) {
      console.error('Error generating FMEA:', error);
      alert('Failed to generate FMEA. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <DashboardLayout>
      {/* Header / Top Navigation */}
      <header id="header" className="bg-white shadow-sm fixed top-0 left-0 right-0 z-50">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center">
            <div className="mr-2">
              <svg className="h-8 w-8" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="18" height="18" rx="4" fill="#0ea5e9" />
                <rect x="22" width="18" height="18" rx="4" fill="#8b5cf6" />
                <rect y="22" width="18" height="18" rx="4" fill="#10b981" />
                <rect x="22" y="22" width="18" height="18" rx="4" fill="#f59e0b" />
              </svg>
            </div>
            <span className="text-xl font-bold text-gray-800">Foton aiQMS Platform</span>
          </div>
          <div className="flex items-center">
            <div className="relative group">
              <button className="flex items-center space-x-2 text-gray-700 hover:text-gray-900">
                <img src="https://storage.googleapis.com/uxpilot-auth.appspot.com/avatars/avatar-3.jpg" alt="User" className="w-8 h-8 rounded-full border border-gray-200" />
                <span className="hidden md:block font-medium">John Spanomanolis</span>
                <i className="fa-solid fa-chevron-down text-xs"></i>
              </button>
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 hidden group-hover:block">
                <span className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer">Profile</span>
                <span className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer">Logout</span>
              </div>
            </div>
          </div>
        </div>
      </header>
      <div className="flex pt-20">
        {/* Sidebar */}
        <div className="flex-1 p-6 max-w-full mx-auto">
          {/* Header */}
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Create New FMEA</h1>
            <p className="text-gray-600">Enter component details and generate an AI-powered FMEA analysis</p>
          </div>

          {/* FMEA Type Tabs - always visible */}
          <div className="flex space-x-2 mb-6">
            {FMEA_TYPES.map(type => (
              <button
                key={type.key}
                onClick={() => { setFmeaType(type.key); setShowTable(!!fmeaData[type.key]); }}
                className={`px-4 py-2 rounded-t-md font-medium border-b-2 ${fmeaType === type.key ? 'bg-blue-100 border-blue-600 text-blue-800' : 'bg-gray-100 border-transparent text-gray-600'}`}
              >
                {type.label}
              </button>
            ))}
            <button
              onClick={() => navigate('/traceability-matrix')}
              className="px-4 py-2 rounded-t-md font-medium border-b-2 bg-gray-100 border-transparent text-gray-600 hover:bg-blue-100 hover:text-blue-800"
              data-testid="trace-matrix-tab"
            >
              Trace Matrix
            </button>
          </div>

          {/* Component Input Form */}
          {!showTable && (
            <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
              <div className="max-w-2xl">
                <label htmlFor="component" className="block text-sm font-medium text-gray-700 mb-2">
                  Component Name
                </label>
                <input
                  type="text"
                  id="component"
                  value={componentName}
                  onChange={(e) => setComponentName(e.target.value)}
                  placeholder="e.g., Steel Beam, Hydraulic Pump, Circuit Board"
                  className="w-full px-4 py-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <div className="mt-6">
                  <button
                    onClick={generateFmea}
                    disabled={isGenerating || !componentName.trim()}
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
                        Generate AI FMEA
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* FMEA Table */}
          {showTable && (
            <div className="mb-4">
              {mockFlag === true && (
                <div className="bg-yellow-100 text-yellow-800 px-4 py-2 rounded mb-2 font-semibold">
                  Mock Data (not AI generated)
                </div>
              )}
              {mockFlag === false && (
                <div className="bg-blue-100 text-blue-800 px-4 py-2 rounded mb-2 font-semibold">
                  AI Generated Data
                </div>
              )}
            </div>
          )}
          {showTable && fmeaData[fmeaType] && (
            <div className="bg-white rounded-lg shadow-sm overflow-hidden">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">
                      {FMEA_TYPES.find(t => t.key === fmeaType)?.label} Analysis: {componentName}
                    </h2>
                    <div className="flex space-x-4 mt-2 text-sm text-gray-600">
                      {fmeaData[fmeaType]?.[0]?.analysis_timestamp && (
                        <div>
                          <span className="font-medium">Analysis Date:</span> {new Date(fmeaData[fmeaType][0].analysis_timestamp).toLocaleString()}
                        </div>
                      )}
                      {fmeaData[fmeaType]?.[0]?.version && (
                        <div>
                          <span className="font-medium">Version:</span> {fmeaData[fmeaType][0].version}
                        </div>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => setShowTable(false)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    <i className="fa-solid fa-edit mr-1"></i>
                    Edit Component
                  </button>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {fmeaType === 'pfmea' ? 'Process Step' : 'Function'}
                      </th>
                      {fmeaType === 'pfmea' && (
                        <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Failure Mode
                        </th>
                      )}
                      <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {fmeaType === 'pfmea' ? 'Process Requirements' : 'Failure Mode'}
                      </th>
                      <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Potential Effect
                      </th>
                      <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        S
                      </th>
                      <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Potential Causes
                      </th>
                      <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        O
                      </th>
                      <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Current Controls
                      </th>
                      <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        D
                      </th>
                      <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        RPN
                      </th>
                      <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Recommended Actions
                      </th>
                      <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions Taken
                      </th>
                      <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        S'
                      </th>
                      <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        O'
                      </th>
                      <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        D'
                      </th>
                      <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        RPN'
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {fmeaData[fmeaType].map((row) => (
                      <tr key={row.id} className="hover:bg-gray-50">
                        <td className="px-3 py-4 text-sm text-gray-900 max-w-xs">
                          {fmeaType === 'pfmea' ? row.processStep : row.function}
                        </td>
                        {fmeaType === 'pfmea' && (
                          <td className="px-3 py-4 text-sm text-gray-900 max-w-xs">
                            {row.failureMode}
                          </td>
                        )}
                        <td className="px-3 py-4 text-sm text-gray-900 max-w-xs">
                          {fmeaType === 'pfmea' ? row.processRequirements : row.failureMode}
                        </td>
                        <td className="px-3 py-4 text-sm text-gray-900 max-w-xs">
                          {row.potentialEffect}
                        </td>
                        <td className="px-3 py-4 text-sm">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(row.severity)}`}>
                            {row.severity}
                          </span>
                        </td>
                        <td className="px-3 py-4 text-sm text-gray-900 max-w-xs">
                          {row.potentialCauses}
                        </td>
                        <td className="px-3 py-4 text-sm">
                          <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            {row.occurrence}
                          </span>
                        </td>
                        <td className="px-3 py-4 text-sm text-gray-900 max-w-xs">
                          {row.currentControls}
                        </td>
                        <td className="px-3 py-4 text-sm">
                          <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            {row.detection}
                          </span>
                        </td>
                        <td className="px-3 py-4 text-sm">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRpnColor(row.rpn)}`}>
                            {row.rpn}
                          </span>
                        </td>
                        <td className="px-3 py-4 text-sm text-gray-900 max-w-xs">
                          {row.recommendedActions}
                        </td>
                        <td className="px-3 py-4 text-sm text-gray-900 max-w-xs">
                          <span className="text-green-600 font-medium">{row.actionsTaken}</span>
                        </td>
                        <td className="px-3 py-4 text-sm">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(row.finalSeverity)}`}>
                            {row.finalSeverity}
                          </span>
                        </td>
                        <td className="px-3 py-4 text-sm">
                          <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            {row.finalOccurrence}
                          </span>
                        </td>
                        <td className="px-3 py-4 text-sm">
                          <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            {row.finalDetection}
                          </span>
                        </td>
                        <td className="px-3 py-4 text-sm">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRpnColor(row.finalRpn)}`}>
                            {row.finalRpn}
                          </span>
                          <div className="text-xs text-gray-500 mt-1">
                            {row.rpn > row.finalRpn && (
                              <span className={`px-1 py-0.5 rounded text-xs ${getImprovementColor(row.rpn, row.finalRpn)}`}>
                                ↓{row.rpn - row.finalRpn}
                              </span>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Summary Statistics */}
              <div className="p-6 border-t border-gray-200 bg-gray-50">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h3 className="text-sm font-medium text-gray-500">Total Rows</h3>
                    <p className="text-2xl font-bold text-gray-900">{fmeaData[fmeaType].length}</p>
                  </div>
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h3 className="text-sm font-medium text-gray-500">Average Initial RPN</h3>
                    <p className="text-2xl font-bold text-orange-600">
                      {Math.round(fmeaData[fmeaType].reduce((sum, row) => sum + row.rpn, 0) / fmeaData[fmeaType].length)}
                    </p>
                  </div>
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h3 className="text-sm font-medium text-gray-500">Average Final RPN</h3>
                    <p className="text-2xl font-bold text-green-600">
                      {Math.round(fmeaData[fmeaType].reduce((sum, row) => sum + row.finalRpn, 0) / fmeaData[fmeaType].length)}
                    </p>
                  </div>
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h3 className="text-sm font-medium text-gray-500">Risk Reduction</h3>
                    <p className="text-2xl font-bold text-blue-600">
                      {Math.round(((fmeaData[fmeaType].reduce((sum, row) => sum + row.rpn, 0) - fmeaData[fmeaType].reduce((sum, row) => sum + row.finalRpn, 0)) / fmeaData[fmeaType].reduce((sum, row) => sum + row.rpn, 0)) * 100)}%
                    </p>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-4">
                  <button className="bg-blue-600 text-white px-4 py-2 rounded-md font-medium hover:bg-blue-700">
                    <i className="fa-solid fa-download mr-2"></i>
                    Export FMEA
                  </button>
                  <button className="bg-green-600 text-white px-4 py-2 rounded-md font-medium hover:bg-green-700" onClick={handleOpenProjectModal}>
                    <i className="fa-solid fa-save mr-2"></i>
                    Save to Project
                  </button>
                  <button className="bg-gray-600 text-white px-4 py-2 rounded-md font-medium hover:bg-gray-700" onClick={handleAddMoreRows}>
                    <i className="fa-solid fa-plus mr-2"></i>
                    Add More Rows
                  </button>
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
      
      {/* Footer */}
      <footer className="bg-white shadow-sm fixed bottom-0 left-0 right-0 z-50">
        <div className="container mx-auto px-4 py-3 text-center text-gray-600">
          &copy; {new Date().getFullYear()} Foton aiQMS Platform. All rights reserved.
        </div>
      </footer>
    </DashboardLayout>
  );
};

export default FmeaForm;

declare global {
  interface Window {
    fmeaApi: any;
  }
}