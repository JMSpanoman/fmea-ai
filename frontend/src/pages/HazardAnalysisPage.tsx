import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ProjectDataViewer from '../components/ProjectDataViewer';
import { exportHazardAnalysisData } from '../utils/exportUtils';

interface HazardAnalysisRow {
  id: string;
  hazardDescription: string;
  hazardType: string;
  severity: string;
  probability: string;
  riskLevel: string;
  affectedComponents: string;
  potentialConsequences: string;
  existingControls: string;
  riskAssessment: string;
  mitigationMeasures: string;
  responsibleParty: string;
  targetDate: string;
  status: string;
  monitoringPlan: string;
  fmeaLink: string;
  regulatoryRequirements: string;
  closureSummary: string;
  milestones: string;
  riskControlsUpdate: string;
  analysis_timestamp?: string;
  version?: string;
}

const HAZARD_TYPES = [
  { key: 'electrical', label: 'Electrical Hazard' },
  { key: 'mechanical', label: 'Mechanical Hazard' },
  { key: 'chemical', label: 'Chemical Hazard' },
  { key: 'thermal', label: 'Thermal Hazard' },
  { key: 'biological', label: 'Biological Hazard' },
  { key: 'ergonomic', label: 'Ergonomic Hazard' },
  { key: 'environmental', label: 'Environmental Hazard' },
  { key: 'operational', label: 'Operational Hazard' },
];

const HazardAnalysisPage: React.FC = () => {
  const navigate = useNavigate();
  const [hazardDescription, setHazardDescription] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [hazardType, setHazardType] = useState('electrical');
  const [hazardData, setHazardData] = useState<{ [key: string]: HazardAnalysisRow[] }>({});
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

  const generateHazardAnalysis = async () => {
    console.log('generateHazardAnalysis called');
    console.log('hazardDescription:', hazardDescription);
    
    if (!hazardDescription.trim()) {
      console.log('No hazard description provided, using default');
      setHazardDescription('Default electrical hazard for testing');
    }
    
    setIsGenerating(true);
    console.log('Setting isGenerating to true');
    
    try {
      // Call backend API
      console.log('Starting AI generation via backend API...');
      const api = window.fmeaApi;
      
      const response = await api.generateHazardAnalysis({
        hazard_description: hazardDescription || 'Default electrical hazard',
        hazard_type: hazardType
      });
      
      console.log('Backend API response:', response);
      
      if (response.hazard_data && response.hazard_data.length > 0) {
        // Convert backend data to frontend format
        const convertedData = response.hazard_data.map((item: any) => ({
          id: item.id || `HA-${Date.now().toString().slice(-6)}`,
          hazardDescription: item.hazard_description || 'Default electrical hazard',
          hazardType: item.hazard_type || "Electrical",
          severity: item.severity || "High",
          probability: item.probability || "Medium",
          riskLevel: item.risk_level || "High",
          affectedComponents: item.affected_components || "Main electrical panel, wiring",
          potentialConsequences: item.potential_consequences || "Electric shock, fire, system failure",
          existingControls: item.existing_controls || "Circuit breakers, insulation",
          riskAssessment: item.risk_assessment || "High risk due to potential for serious injury",
          mitigationMeasures: item.mitigation_measures || "Enhanced insulation, ground fault protection",
          responsibleParty: item.responsible_party || "Electrical Engineer",
          targetDate: item.target_date || "2025-12-31",
          status: item.status || "Open",
          monitoringPlan: item.monitoring_plan || "Regular inspections, testing",
          fmeaLink: item.fmea_link || "Link to FMEA-001",
          regulatoryRequirements: item.regulatory_requirements || "IEC 61010-1, UL 61010-1",
          closureSummary: item.closure_summary || "AI generated closure summary",
          milestones: item.milestones || "Phase 1 complete by 2025-09-30",
          riskControlsUpdate: item.risk_controls_update || "Updated risk control document RC-005",
          analysis_timestamp: item.analysis_timestamp || new Date().toISOString(),
          version: item.version || "1.0"
        }));

        console.log('Converted hazard analysis data:', convertedData);
        
        setHazardData({
          [hazardType]: convertedData,
        });
        setMockFlag(response.mock);
        setShowTable(true);
        setIsGenerating(false);
      } else {
        console.log('No hazard data in response, using mock data');
        // Fallback to mock data if API doesn't return data
        const mockData: HazardAnalysisRow[] = [
          {
            id: `HA-${Date.now().toString().slice(-6)}`,
            hazardDescription: hazardDescription || 'Electrical system failure',
            hazardType: hazardType,
            severity: 'High',
            probability: 'Medium',
            riskLevel: 'High',
            affectedComponents: 'Main electrical panel, wiring, control systems',
            potentialConsequences: 'Electric shock, fire, system shutdown, data loss',
            existingControls: 'Circuit breakers, insulation, grounding, emergency shutdown',
            riskAssessment: 'High risk due to potential for serious injury and equipment damage',
            mitigationMeasures: 'Enhanced insulation, ground fault protection, redundant systems',
            responsibleParty: 'Electrical Engineer',
            targetDate: '2025-12-31',
            status: 'Open',
            monitoringPlan: 'Regular inspections, testing, continuous monitoring',
            fmeaLink: 'Link to FMEA-001',
            regulatoryRequirements: 'IEC 61010-1, UL 61010-1, NFPA 70',
            closureSummary: 'Comprehensive hazard analysis completed with mitigation plan',
            milestones: 'Phase 1 complete by 2025-09-30, Phase 2 by 2025-12-31',
            riskControlsUpdate: 'Updated risk control document RC-005',
            analysis_timestamp: new Date().toISOString(),
            version: '1.0'
          }
        ];

        setHazardData({
          [hazardType]: mockData,
        });
        setMockFlag(true);
        setShowTable(true);
        setIsGenerating(false);
      }
    } catch (error) {
      console.error('Error generating hazard analysis:', error);
      console.log('Using fallback mock data due to API error');
      
      // Fallback to mock data
      const mockData: HazardAnalysisRow[] = [
        {
          id: `HA-${Date.now().toString().slice(-6)}`,
          hazardDescription: hazardDescription || 'Electrical system failure',
          hazardType: hazardType,
          severity: 'High',
          probability: 'Medium',
          riskLevel: 'High',
          affectedComponents: 'Main electrical panel, wiring, control systems',
          potentialConsequences: 'Electric shock, fire, system shutdown, data loss',
          existingControls: 'Circuit breakers, insulation, grounding, emergency shutdown',
          riskAssessment: 'High risk due to potential for serious injury and equipment damage',
          mitigationMeasures: 'Enhanced insulation, ground fault protection, redundant systems',
          responsibleParty: 'Electrical Engineer',
          targetDate: '2025-12-31',
          status: 'Open',
          monitoringPlan: 'Regular inspections, testing, continuous monitoring',
          fmeaLink: 'Link to FMEA-001',
          regulatoryRequirements: 'IEC 61010-1, UL 61010-1, NFPA 70',
          closureSummary: 'Comprehensive hazard analysis completed with mitigation plan',
          milestones: 'Phase 1 complete by 2025-09-30, Phase 2 by 2025-12-31',
          riskControlsUpdate: 'Updated risk control document RC-005',
          analysis_timestamp: new Date().toISOString(),
          version: '1.0'
        }
      ];

      setHazardData({
        [hazardType]: mockData,
      });
      setMockFlag(true);
      setShowTable(true);
      setIsGenerating(false);
    }
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel.toLowerCase()) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
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
      case 'pending': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleSaveToProject = async () => {
    if (!selectedProjectId) {
      alert('Please select a project');
      return;
    }

    setIsSaving(true);
    setSaveError('');

    try {
      const api = window.fmeaApi;
      const currentData = hazardData[hazardType] || [];
      
      // Save each hazard analysis entry
      for (const hazard of currentData) {
        await api.saveHazardAnalysis({
          project_id: selectedProjectId,
          hazard_description: hazard.hazardDescription,
          hazard_type: hazard.hazardType,
          severity: hazard.severity,
          probability: hazard.probability,
          risk_level: hazard.riskLevel,
          affected_components: hazard.affectedComponents,
          potential_consequences: hazard.potentialConsequences,
          existing_controls: hazard.existingControls,
          risk_assessment: hazard.riskAssessment,
          mitigation_measures: hazard.mitigationMeasures,
          responsible_party: hazard.responsibleParty,
          target_date: hazard.targetDate,
          status: hazard.status,
          monitoring_plan: hazard.monitoringPlan,
          fmea_link: hazard.fmeaLink,
          regulatory_requirements: hazard.regulatoryRequirements,
          closure_summary: hazard.closureSummary,
          milestones: hazard.milestones,
          risk_controls_update: hazard.riskControlsUpdate,
          analysis_timestamp: hazard.analysis_timestamp,
          version: hazard.version
        });
      }

      alert('Hazard analysis saved to project successfully!');
      setShowProjectModal(false);
    } catch (error) {
      console.error('Error saving hazard analysis:', error);
      setSaveError('Failed to save hazard analysis. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleExport = () => {
    const currentData = hazardData[hazardType] || [];
    if (currentData.length === 0) {
      alert('No data to export');
      return;
    }
    exportHazardAnalysisData(currentData, `hazard_analysis_${hazardType}_${new Date().toISOString().split('T')[0]}`);
  };

  const handleCreateNewProject = async () => {
    if (!newProjectName.trim()) {
      alert('Please enter a project name');
      return;
    }

    setCreatingNew(true);
    try {
      const api = window.fmeaApi;
      const newProject = await api.createProject(newProjectName);
      setProjects([...projects, newProject]);
      setSelectedProjectId(newProject.id);
      setNewProjectName('');
    } catch (error) {
      console.error('Error creating project:', error);
      alert('Failed to create project. Please try again.');
    } finally {
      setCreatingNew(false);
    }
  };

  const loadProjects = async () => {
    try {
      const api = window.fmeaApi;
      const loadedProjects = await api.getProjects();
      setProjects(loadedProjects);
    } catch (error) {
      console.error('Error loading projects:', error);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-800">Hazard Analysis</h1>
              <p className="text-gray-600 mt-2">
                AI-powered hazard identification and risk assessment for your FMEA projects
              </p>
            </div>
            <button
              onClick={() => navigate('/builder')}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              Back to FMEA Builder
            </button>
          </div>

          {/* Input Form */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Hazard Type
              </label>
              <select
                value={hazardType}
                onChange={(e) => setHazardType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {HAZARD_TYPES.map((type) => (
                  <option key={type.key} value={type.key}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Hazard Description
              </label>
              <input
                type="text"
                value={hazardDescription}
                onChange={(e) => setHazardDescription(e.target.value)}
                placeholder="Describe the hazard or system to analyze..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <div className="flex space-x-4">
            <button
              onClick={generateHazardAnalysis}
              disabled={isGenerating}
              className="px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
            >
              {isGenerating ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <span>🔍</span>
                  <span>Generate Hazard Analysis</span>
                </>
              )}
            </button>

            {showTable && (
              <>
                <button
                  onClick={() => setShowProjectModal(true)}
                  className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                >
                  💾 Save to Project
                </button>
                <button
                  onClick={handleExport}
                  className="px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors"
                >
                  📊 Export Data
                </button>
              </>
            )}
          </div>

          {mockFlag !== null && (
            <div className={`mt-4 p-3 rounded-lg ${mockFlag ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
              {mockFlag ? '⚠️ Using mock data (API not available)' : '✅ Data generated via AI API'}
            </div>
          )}
        </div>

        {/* Results Table */}
        {showTable && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Hazard Analysis Results - {HAZARD_TYPES.find(t => t.key === hazardType)?.label}
            </h2>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Hazard
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Risk Level
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Severity
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Probability
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {hazardData[hazardType]?.map((hazard, index) => (
                    <tr key={hazard.id} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="px-6 py-4">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {hazard.hazardDescription}
                          </div>
                          <div className="text-sm text-gray-500">
                            Type: {hazard.hazardType}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRiskLevelColor(hazard.riskLevel)}`}>
                          {hazard.riskLevel}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getSeverityColor(hazard.severity)}`}>
                          {hazard.severity}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                          {hazard.probability}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(hazard.status)}`}>
                          {hazard.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        <button
                          onClick={() => {
                            setSelectedProjectForViewer(hazard);
                            setShowProjectDataViewer(true);
                          }}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Project Selection Modal */}
        {showProjectModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Save to Project</h3>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Project
                </label>
                <select
                  value={selectedProjectId}
                  onChange={(e) => setSelectedProjectId(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Choose a project...</option>
                  {projects.map((project) => (
                    <option key={project.id} value={project.id}>
                      {project.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Or Create New Project
                </label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={newProjectName}
                    onChange={(e) => setNewProjectName(e.target.value)}
                    placeholder="New project name..."
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <button
                    onClick={handleCreateNewProject}
                    disabled={creatingNew}
                    className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50"
                  >
                    {creatingNew ? 'Creating...' : 'Create'}
                  </button>
                </div>
              </div>

              {saveError && (
                <div className="mb-4 p-3 bg-red-100 text-red-800 rounded-lg">
                  {saveError}
                </div>
              )}

              <div className="flex space-x-3">
                <button
                  onClick={handleSaveToProject}
                  disabled={isSaving || !selectedProjectId}
                  className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
                >
                  {isSaving ? 'Saving...' : 'Save'}
                </button>
                <button
                  onClick={() => setShowProjectModal(false)}
                  className="flex-1 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Project Data Viewer Modal */}
        {showProjectDataViewer && selectedProjectForViewer && (
          <ProjectDataViewer
            selectedProject={selectedProjectForViewer}
            onClose={() => setShowProjectDataViewer(false)}
          />
        )}
      </div>
    </div>
  );
};

export default HazardAnalysisPage;
