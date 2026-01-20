import React, { useState, useEffect } from 'react';
import FmeaForm from './FmeaForm';
import { FmeaRow } from '../../types';
import { exportFmeaData } from '../../utils/exportUtils';

interface FmeaFormWrapperProps {
  selectedProject?: any;
}

const FmeaFormWrapper: React.FC<FmeaFormWrapperProps> = ({ selectedProject }) => {
  const [fmeaRows, setFmeaRows] = useState<FmeaRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [componentName, setComponentName] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [fmeaType, setFmeaType] = useState('dfmea');
  const [showTable, setShowTable] = useState(false);
  const [showProjectModal, setShowProjectModal] = useState(false);
  const [projects, setProjects] = useState<any[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');
  const [newProjectName, setNewProjectName] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState('');
  const [creatingNew, setCreatingNew] = useState(false);
  const [mockFlag, setMockFlag] = useState<boolean | null>(null);
  const [loadingProjects, setLoadingProjects] = useState(false);
  const [debugInfo, setDebugInfo] = useState<string>('');

  // Debug modal state changes
  useEffect(() => {
    console.log('Modal state changed:', showProjectModal);
  }, [showProjectModal]);

  // Check if fmeaApi is available
  useEffect(() => {
    console.log('FmeaFormWrapper mounted');
    console.log('window.fmeaApi available:', !!window.fmeaApi);
    console.log('Authentication token:', localStorage.getItem('token'));
    
    // Wait a bit for fmeaApi to be available
    const checkFmeaApi = () => {
      if (window.fmeaApi) {
        console.log('fmeaApi is now available');
        setDebugInfo('fmeaApi is available');
        setError(null);
      } else {
        console.log('fmeaApi not yet available, retrying...');
        setError('FMEA API not available. Please check if the backend is running.');
        setDebugInfo('fmeaApi not found on window object - retrying...');
        setTimeout(checkFmeaApi, 100);
      }
    };
    
    checkFmeaApi();
  }, []);

  const FMEA_TYPES = [
    { key: 'dfmea', label: 'DFMEA' },
    { key: 'pfmea', label: 'PFMEA' },
    { key: 'ufmea', label: 'UFMEA' },
  ];

  // Load saved FMEA data when a project is selected
  useEffect(() => {
    if (selectedProject?.id) {
      loadSavedFmeaData(selectedProject.id);
    } else {
      setFmeaRows([]);
    }
  }, [selectedProject?.id]);

  const loadSavedFmeaData = async (projectId: number) => {
    setLoading(true);
    setError(null);
    try {
      console.log('Loading FMEA data for project:', projectId);
      const fmeaData = await window.fmeaApi.getFMEAs(projectId);
      console.log('Loaded FMEA data:', fmeaData);
      setFmeaRows(fmeaData || []);
    } catch (err) {
      console.error('Error loading FMEA data:', err);
      setError('Failed to load FMEA data');
      setFmeaRows([]);
    } finally {
      setLoading(false);
    }
  };

  const generateFmea = async () => {
    if (!componentName.trim()) {
      alert('Please enter a component name');
      return;
    }
    console.log('=== GENERATING FMEA ===');
    console.log('Component name:', componentName);
    console.log('FMEA type:', fmeaType);
    
    setIsGenerating(true);
    try {
      const api = window.fmeaApi;
      let dfmeaData, pfmeaData, ufmeaData;
      let mock = false;
      // Always generate DFMEA and UFMEA from dfmea endpoint for now
      const dfmeaResult = await api.getFMEAByType('dfmea', componentName);
      console.log('DFMEA result:', dfmeaResult);
      dfmeaData = dfmeaResult.fmea_data;
      ufmeaData = dfmeaResult.fmea_data;
      mock = dfmeaResult.mock;
      if (fmeaType === 'pfmea') {
        const pfmeaResult = await api.getFMEAByType('pfmea', componentName);
        console.log('PFMEA result:', pfmeaResult);
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
      
      console.log('Raw DFMEA data:', dfmeaData);
      console.log('Raw PFMEA data:', pfmeaData);
      
      const transformedData = dfmeaData.map((row: any) => ({
        id: row.id || Date.now(),
        location: row.location || row.function || '',
        component: row.component || componentName,
        failure_mode: row.failure_mode || row.failureMode || '',
        effect: row.effect || row.potentialEffect || '',
        cause: row.cause || row.potentialCauses || '',
        severity: row.severity || 1,
        probability: row.probability || row.occurrence || 1,
        detection: row.detection || 1,
        rpn: row.rpn || (row.severity || 1) * (row.probability || 1) * (row.detection || 1),
        mitigation: row.mitigation || row.recommendedActions || '',
        action_taken: row.action_taken || row.actionsTaken || '',
        revised_severity: row.revised_severity || row.finalSeverity || row.severity || 1,
        revised_probability: row.revised_probability || row.finalOccurrence || row.probability || 1,
        revised_detection: row.revised_detection || row.finalDetection || row.detection || 1,
        revised_rpn: row.revised_rpn || row.finalRpn || row.rpn || 1
      }));

      console.log('Transformed FMEA data:', transformedData);
      console.log('Number of FMEA rows:', transformedData.length);

      setFmeaRows(transformedData);
      setMockFlag(mock);
      setShowTable(true);
      setIsGenerating(false);

      // Automatically export first 10 FMEA rows to MasterControl (creates 10 separate forms)
      if (transformedData && transformedData.length > 0) {
        try {
          const rowsToExport = transformedData.slice(0, 10); // Get first 10 rows
          console.log(`Auto-exporting first ${rowsToExport.length} FMEA rows to MasterControl (creating ${rowsToExport.length} forms)`);
          
          const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api';
          
          // Export each row separately to create individual MasterControl forms
          for (let i = 0; i < rowsToExport.length; i++) {
            const row = rowsToExport[i];
            console.log(`Exporting row ${i + 1} of ${rowsToExport.length} to MasterControl:`, row);
            
            // Transform FMEA row to MasterControl format
            const mcRow = {
              "COMPONENT": row.component || componentName,
              "FUNCTION": row.location || row.function || '',
              "FAILURE MODE": row.failure_mode || '',
              "EFFECTS": row.effect || '',
              "SEVERITY": row.severity || 1,
              "CAUSES": row.cause || '',
              "OCCURRENCE": row.probability || row.occurrence || 1,
              "CONTROLS": row.mitigation || '',
              "DETECTION": row.detection || 1,
              "RPN": row.rpn || (row.severity || 1) * (row.probability || row.occurrence || 1) * (row.detection || 1),
              "ACTIONS": row.action_taken || '',
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

  const getRpnColor = (rpn: number) => {
    if (rpn >= 200) return 'text-red-600 font-bold';
    if (rpn >= 100) return 'text-orange-600 font-semibold';
    if (rpn >= 50) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getSeverityColor = (severity: number) => {
    if (severity >= 9) return 'bg-red-100 text-red-800';
    if (severity >= 7) return 'bg-orange-100 text-orange-800';
    if (severity >= 5) return 'bg-yellow-100 text-yellow-800';
    return 'bg-green-100 text-green-800';
  };

  const handleOpenProjectModal = async () => {
    console.log('=== SAVE TO PROJECT CLICKED ===');
    console.log('Current projects state:', projects);
    console.log('Modal should open:', !showProjectModal);
    
    setLoadingProjects(true);
    setSaveError('');
    try {
      // Ensure API is available
      if (!window.fmeaApi) {
        throw new Error('FMEA API not available. Please refresh the page.');
      }
      
      console.log('=== DEBUG: Starting project loading ===');
      console.log('window.fmeaApi available:', !!window.fmeaApi);
      console.log('Current token:', window.fmeaApi.token ? 'Token present' : 'No token');
      
      // Always attempt to login first to ensure we have a fresh token
      console.log('Attempting to login...');
      const loginResponse = await window.fmeaApi.devLogin();
      console.log('Login successful, token set:', window.fmeaApi.token);
      console.log('Login response:', loginResponse);
      
      // Double-check token is set
      if (!window.fmeaApi.token) {
        throw new Error('Authentication failed - no token available after login');
      }
      
      // Test backend connectivity first
      try {
        await window.fmeaApi.healthCheck();
        console.log('Backend is reachable');
      } catch (healthError) {
        console.error('Backend health check failed:', healthError);
        throw new Error('Backend server is not responding. Please ensure the server is running.');
      }
      
      console.log('Making projects request with token:', window.fmeaApi.token ? 'Token present' : 'No token');
      console.log('Token value:', window.fmeaApi.token);
      const response = await window.fmeaApi.getProjects();
      console.log('Projects response:', response);
      
      // Handle different response formats
      let projectList = [];
      if (Array.isArray(response)) {
        projectList = response;
      } else if (response && Array.isArray(response.projects)) {
        projectList = response.projects;
      } else if (response && response.data && Array.isArray(response.data)) {
        projectList = response.data;
      } else {
        console.warn('Unexpected projects response format:', response);
        projectList = [];
      }
      
      console.log('Processed project list:', projectList);
      setProjects(projectList);
      setShowProjectModal(true);
      console.log('=== DEBUG: Project loading completed successfully ===');
    } catch (error: any) {
      console.error('Error loading projects:', error);
      setSaveError(`Failed to load projects: ${error.message || 'Unknown error'}. Please try again.`);
    } finally {
      setLoadingProjects(false);
    }
  };

  const handleSaveToProject = async () => {
    console.log('=== FMEA SAVE TO PROJECT CLICKED ===');
    console.log('isSaving:', isSaving);
    console.log('selectedProjectId:', selectedProjectId);
    console.log('newProjectName:', newProjectName);
    console.log('fmeaRows.length:', fmeaRows.length);
    console.log('fmeaRows:', fmeaRows);
    
    if (!selectedProjectId && !newProjectName.trim()) {
      setSaveError('Please select a project or create a new one');
      return;
    }

    if (fmeaRows.length === 0) {
      setSaveError('No FMEA data to save. Please generate FMEA data first.');
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
          description: `FMEA Analysis for ${componentName}`
        });
        projectId = createResponse.id;
      }

      if (!projectId) {
        setSaveError('Please select a project or create a new one');
        setIsSaving(false);
        return;
      }

      // Save each FMEA row to the project
      const savePromises = fmeaRows.map(async (row, index) => {
        console.log(`Processing FMEA row ${index + 1}:`, row);
        
        const fmeaData = {
          component: row.component,
          function_description: row.location || '',
          potential_failure_mode: row.failure_mode,
          potential_effects: row.effect,
          potential_causes: row.cause,
          severity: row.severity,
          occurrence: row.probability,
          current_controls: row.mitigation || '',
          detection: row.detection,
          risk_priority_number: row.rpn,
          recommended_actions: row.mitigation,
          responsible_party: '',
          target_completion_date: null,
          actions_taken: row.action_taken,
          final_severity: row.revised_severity,
          final_occurrence: row.revised_probability,
          final_detection: row.revised_detection,
          final_risk_priority_number: row.revised_rpn
        };

        console.log(`Saving FMEA row ${index + 1} with data:`, fmeaData);
        
        try {
          const result = await api.createFMEA(projectId, fmeaData);
          console.log(`FMEA row ${index + 1} save result:`, result);
          return result;
        } catch (error: any) {
          console.error(`Error saving FMEA row ${index + 1}:`, error);
          return { error: error.message || 'Unknown error' };
        }
      });

      const results = await Promise.all(savePromises);
      console.log('All FMEA save results:', results);

      const failedSaves = results.filter(result => {
        return result && (result.error || result.detail || !result.id);
      });

      if (failedSaves.length === 0) {
        setShowProjectModal(false);
        setSelectedProjectId('');
        setNewProjectName('');
        alert(`Successfully saved ${fmeaRows.length} FMEA entries to project!`);
      } else {
        console.error('Failed saves:', failedSaves);
        setSaveError(`Failed to save ${failedSaves.length} entries. Please try again.`);
      }
    } catch (error) {
      console.error('Error saving FMEA data:', error);
      setSaveError('Failed to save FMEA data. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddMoreRows = async () => {
    setShowTable(false);
    setComponentName('');
  };

  const handleViewProjectData = async (project: any) => {
    console.log('=== VIEW PROJECT DATA CLICKED ===');
    console.log('Project to view:', project);
    setSelectedProjectId(project.id.toString());
    await loadSavedFmeaData(project.id);
    setShowTable(true);
    setShowProjectModal(false); // Close modal after viewing
  };

  const handleExportFmea = (format: 'csv' | 'pdf') => {
    if (fmeaRows.length === 0) {
      alert('No FMEA data to export');
      return;
    }
    exportFmeaData(fmeaRows, format);
  };

  return (
    <div className="space-y-6">
      {/* Loading State */}
      {!window.fmeaApi && (
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <i className="fa-solid fa-spinner fa-spin text-blue-400"></i>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">Loading FMEA Builder</h3>
              <p className="text-sm text-blue-700">Initializing API connection...</p>
            </div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <i className="fa-solid fa-exclamation-triangle text-red-400"></i>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Debug Info */}
      {debugInfo && (
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <i className="fa-solid fa-info-circle text-blue-400"></i>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">Debug Info</h3>
              <div className="mt-2 text-sm text-blue-700">
                <p>{debugInfo}</p>
                <p className="mt-1">Token: {localStorage.getItem('token') ? 'Present' : 'Missing'}</p>
                <p className="mt-1">fmeaApi: {window.fmeaApi ? 'Available' : 'Not available'}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Project Info */}
      {selectedProject && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">FMEA Analysis</h2>
              <p className="text-sm text-gray-500 mt-1">
                Project: {selectedProject.name}
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500">Status:</span>
              <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                {selectedProject.status}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* FMEA Type Tabs */}
      <div className="flex space-x-2 mb-6">
        {FMEA_TYPES.map(type => (
          <button
            key={type.key}
            onClick={() => { setFmeaType(type.key); setShowTable(!!fmeaRows.length); }}
            className={`px-4 py-2 rounded-t-md font-medium border-b-2 ${fmeaType === type.key ? 'bg-blue-100 border-blue-600 text-blue-800' : 'bg-gray-100 border-transparent text-gray-600'}`}
          >
            {type.label}
          </button>
        ))}
      </div>

      {/* Component Input Form */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center space-x-4 mb-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Component Name
            </label>
            <input
              type="text"
              value={componentName}
              onChange={(e) => setComponentName(e.target.value)}
              placeholder="Enter component name..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div className="flex items-end">
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

      {/* FMEA Table */}
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
                <h3 className="text-lg font-semibold text-gray-900">FMEA Analysis ({fmeaRows.length} entries)</h3>
                <div className="flex space-x-2">
                  <div className="relative group">
                    <button className="bg-blue-600 text-white px-4 py-2 rounded-md font-medium hover:bg-blue-700 flex items-center">
                      <i className="fa-solid fa-download mr-2"></i>
                      Export FMEA
                      <i className="fa-solid fa-chevron-down ml-2"></i>
                    </button>
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                      <div className="py-1">
                        <button
                          onClick={() => handleExportFmea('csv')}
                          className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          <i className="fa-solid fa-file-csv mr-2"></i>
                          Export as CSV
                        </button>
                        <button
                          onClick={() => handleExportFmea('pdf')}
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
                    Add More FMEA
                  </button>
                </div>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Component</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Location</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Failure Mode</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Effect</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Probability</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Detection</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RPN</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mitigation</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action Taken</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Post-Mitigation Severity</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Post-Mitigation Probability</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Post-Mitigation Detection</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Post-Mitigation RPN</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {fmeaRows.map((row) => (
                    <tr key={row.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{row.component}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{row.location}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{row.failure_mode}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{row.effect}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getSeverityColor(row.severity)}`}>
                          {row.severity}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{row.probability}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{row.detection}</td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getRpnColor(row.rpn)}`}>
                        {row.rpn}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 max-w-xs">
                        <div className="truncate" title={row.mitigation}>
                          {row.mitigation}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 max-w-xs">
                        <div className="truncate" title={row.action_taken}>
                          {row.action_taken}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getSeverityColor(row.revised_severity)}`}>
                          {row.revised_severity}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{row.revised_probability}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{row.revised_detection}</td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getRpnColor(row.revised_rpn)}`}>
                        {row.revised_rpn}
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
              <h3 className="text-sm font-medium text-gray-500">Total FMEA Entries</h3>
              <p className="text-2xl font-bold text-blue-600">{fmeaRows.length}</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <h3 className="text-sm font-medium text-gray-500">High Severity</h3>
              <p className="text-2xl font-bold text-red-600">
                {fmeaRows.filter(row => row.severity >= 7).length}
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <h3 className="text-sm font-medium text-gray-500">High RPN</h3>
              <p className="text-2xl font-bold text-orange-600">
                {fmeaRows.filter(row => row.rpn >= 100).length}
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <h3 className="text-sm font-medium text-gray-500">Risk Reduction</h3>
              <p className="text-2xl font-bold text-green-600">
                {fmeaRows.length > 0 ? 
                  Math.round(
                    (fmeaRows.reduce((sum, row) => sum + row.rpn, 0) - 
                     fmeaRows.reduce((sum, row) => sum + row.revised_rpn, 0)) / fmeaRows.length
                  ) : 0
                }
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Avg reduction per entry
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
    </div>
  );
};

export default FmeaFormWrapper; 