import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ProjectDataViewer from '../components/ProjectDataViewer';
import { exportFaultTreeReportData } from '../utils/exportUtils';

interface FaultTreeReportRow {
  id: string;
  topEvent: string;
  faultTreeType: string;
  complexity: string;
  riskLevel: string;
  rootCauses: string;
  intermediateEvents: string;
  basicEvents: string;
  probability: string;
  cutSets: string;
  minimalCutSets: string;
  riskAssessment: string;
  mitigationStrategies: string;
  responsibleParty: string;
  targetDate: string;
  status: string;
  analysisMethod: string;
  fmeaLink: string;
  regulatoryRequirements: string;
  closureSummary: string;
  milestones: string;
  riskControlsUpdate: string;
  analysis_timestamp?: string;
  version?: string;
}

const FAULT_TREE_TYPES = [
  { key: 'system', label: 'System Fault Tree' },
  { key: 'component', label: 'Component Fault Tree' },
  { key: 'functional', label: 'Functional Fault Tree' },
  { key: 'operational', label: 'Operational Fault Tree' },
  { key: 'maintenance', label: 'Maintenance Fault Tree' },
  { key: 'safety', label: 'Safety Fault Tree' },
  { key: 'reliability', label: 'Reliability Fault Tree' },
  { key: 'quality', label: 'Quality Fault Tree' },
];

const FaultTreeReportPage: React.FC = () => {
  const navigate = useNavigate();
  const [topEvent, setTopEvent] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [faultTreeType, setFaultTreeType] = useState('system');
  const [faultTreeData, setFaultTreeData] = useState<{ [key: string]: FaultTreeReportRow[] }>({});
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

  const generateFaultTreeReport = async () => {
    console.log('generateFaultTreeReport called');
    console.log('topEvent:', topEvent);
    
    if (!topEvent.trim()) {
      console.log('No top event provided, using default');
      setTopEvent('System failure causing complete shutdown');
    }
    
    setIsGenerating(true);
    console.log('Setting isGenerating to true');
    
    try {
      // Call backend API
      console.log('Starting AI generation via backend API...');
      const api = window.fmeaApi;
      
      const response = await api.generateFaultTreeReport({
        top_event: topEvent || 'System failure causing complete shutdown',
        fault_tree_type: faultTreeType
      });
      
      console.log('Backend API response:', response);
      
      if (response.fault_tree_data && response.fault_tree_data.length > 0) {
        // Convert backend data to frontend format
        const convertedData = response.fault_tree_data.map((item: any) => ({
          id: item.id || `FT-${Date.now().toString().slice(-6)}`,
          topEvent: item.top_event || 'System failure causing complete shutdown',
          faultTreeType: item.fault_tree_type || "System",
          complexity: item.complexity || "High",
          riskLevel: item.risk_level || "High",
          rootCauses: item.root_causes || "Component failure, design flaw, human error",
          intermediateEvents: item.intermediate_events || "Subsystem failure, control system failure",
          basicEvents: item.basic_events || "Sensor failure, power loss, software bug",
          probability: item.probability || "Medium",
          cutSets: item.cut_sets || "Multiple failure paths identified",
          minimalCutSets: item.minimal_cut_sets || "Critical path: Sensor + Power + Software",
          riskAssessment: item.risk_assessment || "High risk due to multiple failure modes",
          mitigationStrategies: item.mitigation_strategies || "Redundancy, monitoring, maintenance",
          responsibleParty: item.responsible_party || "Systems Engineer",
          targetDate: item.target_date || "2025-12-31",
          status: item.status || "Open",
          analysisMethod: item.analysis_method || "FTA, FMEA, Risk Matrix",
          fmeaLink: item.fmea_link || "Link to FMEA-001",
          regulatoryRequirements: item.regulatory_requirements || "ISO 14971, IEC 61025",
          closureSummary: item.closure_summary || "AI generated closure summary",
          milestones: item.milestones || "Phase 1 complete by 2025-09-30",
          riskControlsUpdate: item.risk_controls_update || "Updated risk control document RC-005",
          analysis_timestamp: item.analysis_timestamp || new Date().toISOString(),
          version: item.version || "1.0"
        }));

        console.log('Converted fault tree report data:', convertedData);
        
        setFaultTreeData({
          [faultTreeType]: convertedData,
        });
        setMockFlag(response.mock);
        setShowTable(true);
        setIsGenerating(false);
      } else {
        console.log('No fault tree data in response, using mock data');
        // Fallback to mock data if API doesn't return data
        const mockData: FaultTreeReportRow[] = [
          {
            id: `FT-${Date.now().toString().slice(-6)}`,
            topEvent: topEvent || 'System failure causing complete shutdown',
            faultTreeType: faultTreeType,
            complexity: 'High',
            riskLevel: 'High',
            rootCauses: 'Component failure, design flaw, human error, environmental factors',
            intermediateEvents: 'Subsystem failure, control system failure, communication failure',
            basicEvents: 'Sensor failure, power loss, software bug, mechanical wear',
            probability: 'Medium',
            cutSets: 'Multiple failure paths identified with varying probabilities',
            minimalCutSets: 'Critical path: Sensor + Power + Software, Secondary: Mechanical + Human',
            riskAssessment: 'High risk due to multiple failure modes and system complexity',
            mitigationStrategies: 'Redundancy, monitoring, maintenance, training, design improvements',
            responsibleParty: 'Systems Engineer',
            targetDate: '2025-12-31',
            status: 'Open',
            analysisMethod: 'FTA, FMEA, Risk Matrix, Event Tree Analysis',
            fmeaLink: 'Link to FMEA-001',
            regulatoryRequirements: 'ISO 14971, IEC 61025, MIL-STD-882',
            closureSummary: 'Comprehensive fault tree analysis completed with mitigation plan',
            milestones: 'Phase 1 complete by 2025-09-30, Phase 2 by 2025-12-31',
            riskControlsUpdate: 'Updated risk control document RC-005',
            analysis_timestamp: new Date().toISOString(),
            version: '1.0'
          }
        ];

        setFaultTreeData({
          [faultTreeType]: mockData,
        });
        setMockFlag(true);
        setShowTable(true);
        setIsGenerating(false);
      }
    } catch (error) {
      console.error('Error generating fault tree report:', error);
      console.log('Using fallback mock data due to API error');
      
      // Fallback to mock data
      const mockData: FaultTreeReportRow[] = [
        {
          id: `FT-${Date.now().toString().slice(-6)}`,
          topEvent: topEvent || 'System failure causing complete shutdown',
          faultTreeType: faultTreeType,
          complexity: 'High',
          riskLevel: 'High',
          rootCauses: 'Component failure, design flaw, human error, environmental factors',
          intermediateEvents: 'Subsystem failure, control system failure, communication failure',
          basicEvents: 'Sensor failure, power loss, software bug, mechanical wear',
          probability: 'Medium',
          cutSets: 'Multiple failure paths identified with varying probabilities',
          minimalCutSets: 'Critical path: Sensor + Power + Software, Secondary: Mechanical + Human',
          riskAssessment: 'High risk due to multiple failure modes and system complexity',
          mitigationStrategies: 'Redundancy, monitoring, maintenance, training, design improvements',
          responsibleParty: 'Systems Engineer',
          targetDate: '2025-12-31',
          status: 'Open',
          analysisMethod: 'FTA, FMEA, Risk Matrix, Event Tree Analysis',
          fmeaLink: 'Link to FMEA-001',
          regulatoryRequirements: 'ISO 14971, IEC 61025, MIL-STD-882',
          closureSummary: 'Comprehensive fault tree analysis completed with mitigation plan',
          milestones: 'Phase 1 complete by 2025-09-30, Phase 2 by 2025-12-31',
          riskControlsUpdate: 'Updated risk control document RC-005',
          analysis_timestamp: new Date().toISOString(),
          version: '1.0'
        }
      ];

      setFaultTreeData({
        [faultTreeType]: mockData,
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

  const getComplexityColor = (complexity: string) => {
    switch (complexity.toLowerCase()) {
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
      const currentData = faultTreeData[faultTreeType] || [];
      
      // Save each fault tree report entry
      for (const faultTree of currentData) {
        await api.saveFaultTreeReport({
          project_id: selectedProjectId,
          top_event: faultTree.topEvent,
          fault_tree_type: faultTree.faultTreeType,
          complexity: faultTree.complexity,
          risk_level: faultTree.riskLevel,
          root_causes: faultTree.rootCauses,
          intermediate_events: faultTree.intermediateEvents,
          basic_events: faultTree.basicEvents,
          probability: faultTree.probability,
          cut_sets: faultTree.cutSets,
          minimal_cut_sets: faultTree.minimalCutSets,
          risk_assessment: faultTree.riskAssessment,
          mitigation_strategies: faultTree.mitigationStrategies,
          responsible_party: faultTree.responsibleParty,
          target_date: faultTree.targetDate,
          status: faultTree.status,
          analysis_method: faultTree.analysisMethod,
          fmea_link: faultTree.fmeaLink,
          regulatory_requirements: faultTree.regulatoryRequirements,
          closure_summary: faultTree.closureSummary,
          milestones: faultTree.milestones,
          risk_controls_update: faultTree.riskControlsUpdate,
          analysis_timestamp: faultTree.analysis_timestamp,
          version: faultTree.version
        });
      }

      alert('Fault tree report saved to project successfully!');
      setShowProjectModal(false);
    } catch (error) {
      console.error('Error saving fault tree report:', error);
      setSaveError('Failed to save fault tree report. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleExport = () => {
    const currentData = faultTreeData[faultTreeType] || [];
    if (currentData.length === 0) {
      alert('No data to export');
      return;
    }
    exportFaultTreeReportData(currentData, `fault_tree_report_${faultTreeType}_${new Date().toISOString().split('T')[0]}`);
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
              <h1 className="text-3xl font-bold text-gray-800">Fault Tree Report</h1>
              <p className="text-gray-600 mt-2">
                AI-powered fault tree analysis and system failure modeling for your FMEA projects
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
                Fault Tree Type
              </label>
              <select
                value={faultTreeType}
                onChange={(e) => setFaultTreeType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {FAULT_TREE_TYPES.map((type) => (
                  <option key={type.key} value={type.key}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Top Event
              </label>
              <input
                type="text"
                value={topEvent}
                onChange={(e) => setTopEvent(e.target.value)}
                placeholder="Describe the top-level failure event to analyze..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <div className="flex space-x-4">
            <button
              onClick={generateFaultTreeReport}
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
                  <span>🌳</span>
                  <span>Generate Fault Tree Report</span>
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
              Fault Tree Report Results - {FAULT_TREE_TYPES.find(t => t.key === faultTreeType)?.label}
            </h2>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Top Event
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Risk Level
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Complexity
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
                  {faultTreeData[faultTreeType]?.map((faultTree, index) => (
                    <tr key={faultTree.id} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="px-6 py-4">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {faultTree.topEvent}
                          </div>
                          <div className="text-sm text-gray-500">
                            Type: {faultTree.faultTreeType}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRiskLevelColor(faultTree.riskLevel)}`}>
                          {faultTree.riskLevel}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getComplexityColor(faultTree.complexity)}`}>
                          {faultTree.complexity}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                          {faultTree.probability}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(faultTree.status)}`}>
                          {faultTree.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        <button
                          onClick={() => {
                            setSelectedProjectForViewer(faultTree);
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

export default FaultTreeReportPage;
