import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ProjectDataViewer from '../components/ProjectDataViewer';
import { exportRiskTraceabilityMatrixData } from '../utils/exportUtils';

interface RiskTraceabilityMatrixRow {
  id: string;
  requirementId: string;
  requirementDescription: string;
  riskId: string;
  riskDescription: string;
  riskLevel: string;
  controlId: string;
  controlDescription: string;
  controlEffectiveness: string;
  verificationMethod: string;
  verificationStatus: string;
  responsibleParty: string;
  verificationDate: string;
  matrixOwner: string;
  lastUpdated: string;
  version: string;
}

const TRACEABILITY_TYPES = [
  { key: 'requirements_to_risks', label: 'Requirements to Risks' },
  { key: 'risks_to_controls', label: 'Risks to Controls' },
  { key: 'controls_to_verification', label: 'Controls to Verification' },
  { key: 'end_to_end', label: 'End-to-End Traceability' },
  { key: 'regulatory_compliance', label: 'Regulatory Compliance' },
  { key: 'quality_assurance', label: 'Quality Assurance' },
  { key: 'safety_requirements', label: 'Safety Requirements' },
  { key: 'security_requirements', label: 'Security Requirements' },
];

const RiskTraceabilityMatrixPage: React.FC = () => {
  const navigate = useNavigate();
  const [projectName, setProjectName] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [traceabilityType, setTraceabilityType] = useState('requirements_to_risks');
  const [matrixData, setMatrixData] = useState<{ [key: string]: RiskTraceabilityMatrixRow[] }>({});
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

  const generateTraceabilityMatrix = async () => {
    console.log('generateTraceabilityMatrix called');
    console.log('projectName:', projectName);
    
    if (!projectName.trim()) {
      console.log('No project name provided, using default');
      setProjectName('Default Project for Testing');
    }
    
    setIsGenerating(true);
    console.log('Setting isGenerating to true');
    
    try {
      // Call backend API
      console.log('Starting AI generation via backend API...');
      const api = window.fmeaApi;
      
      const response = await api.generateRiskTraceabilityMatrix({
        project_name: projectName || 'Default Project',
        traceability_type: traceabilityType
      });
      
      console.log('Backend API response:', response);
      
      if (response.traceability_matrix_data && response.traceability_matrix_data.length > 0) {
        // Convert backend data to frontend format
        const convertedData = response.traceability_matrix_data.map((item: any) => ({
          id: item.id || `RTM-${Date.now().toString().slice(-6)}`,
          requirementId: item.requirement_id || 'REQ-001',
          requirementDescription: item.requirement_description || 'Default requirement',
          riskId: item.risk_id || 'RISK-001',
          riskDescription: item.risk_description || 'Default risk',
          riskLevel: item.risk_level || "High",
          controlId: item.control_id || 'CTRL-001',
          controlDescription: item.control_description || 'Default control',
          controlEffectiveness: item.control_effectiveness || "High",
          verificationMethod: item.verification_method || 'Default verification',
          verificationStatus: item.verification_status || "Pass",
          responsibleParty: item.responsible_party || "Default Engineer",
          verificationDate: item.verification_date || "2025-01-15",
          matrixOwner: item.matrix_owner || "Risk Manager",
          lastUpdated: item.last_updated || new Date().toISOString(),
          version: item.version || "1.0"
        }));

        console.log('Converted traceability matrix data:', convertedData);
        
        setMatrixData({
          [traceabilityType]: convertedData,
        });
        setMockFlag(response.mock);
        setShowTable(true);
        setIsGenerating(false);
      } else {
        console.log('No traceability matrix data in response, using mock data');
        // Fallback to mock data if API doesn't return data
        const mockData: RiskTraceabilityMatrixRow[] = [
          {
            id: `RTM-${Date.now().toString().slice(-6)}`,
            requirementId: 'REQ-001',
            requirementDescription: 'System must maintain data integrity',
            riskId: 'RISK-001',
            riskDescription: 'Data corruption during transmission',
            riskLevel: 'High',
            controlId: 'CTRL-001',
            controlDescription: 'Data validation and checksums',
            controlEffectiveness: 'High',
            verificationMethod: 'Data integrity testing',
            verificationStatus: 'Pass',
            responsibleParty: 'Data Engineer',
            verificationDate: '2025-01-15',
            matrixOwner: 'Risk Manager',
            lastUpdated: new Date().toISOString(),
            version: '1.0'
          }
        ];

        setMatrixData({
          [traceabilityType]: mockData,
        });
        setMockFlag(true);
        setShowTable(true);
        setIsGenerating(false);
      }
    } catch (error) {
      console.error('Error generating traceability matrix:', error);
      console.log('Using fallback mock data due to API error');
      
      // Fallback to mock data
      const mockData: RiskTraceabilityMatrixRow[] = [
        {
          id: `RTM-${Date.now().toString().slice(-6)}`,
          requirementId: 'REQ-001',
          requirementDescription: 'System must maintain data integrity',
          riskId: 'RISK-001',
          riskDescription: 'Data corruption during transmission',
          riskLevel: 'High',
          controlId: 'CTRL-001',
          controlDescription: 'Data validation and checksums',
          controlEffectiveness: 'High',
          verificationMethod: 'Data integrity testing',
          verificationStatus: 'Pass',
          responsibleParty: 'Data Engineer',
          verificationDate: '2025-01-15',
          matrixOwner: 'Risk Manager',
          lastUpdated: new Date().toISOString(),
          version: '1.0'
        }
      ];

      setMatrixData({
        [traceabilityType]: mockData,
      });
      setMockFlag(true);
      setShowTable(true);
      setIsGenerating(false);
    }
  };

  const handleSaveToProject = async () => {
    try {
      const api = window.fmeaApi;
      const currentData = matrixData[traceabilityType];
      
      if (currentData && currentData.length > 0) {
        // Save each traceability matrix row
        for (const row of currentData) {
          await api.saveRiskTraceabilityMatrix({
            requirement_id: row.requirementId,
            requirement_description: row.requirementDescription,
            risk_id: row.riskId,
            risk_description: row.riskDescription,
            risk_level: row.riskLevel,
            control_id: row.controlId,
            control_description: row.controlDescription,
            control_effectiveness: row.controlEffectiveness,
            verification_method: row.verificationMethod,
            verification_status: row.verificationStatus,
            responsible_party: row.responsibleParty,
            verification_date: row.verificationDate,
            matrix_owner: row.matrixOwner,
            last_updated: row.lastUpdated,
            version: row.version,
            project_id: 1 // Default project ID
          });
        }
        
        alert('Risk traceability matrix saved to project successfully!');
      }
    } catch (error) {
      console.error('Error saving to project:', error);
      alert('Failed to save to project. Please try again.');
    }
  };

  const handleExportData = () => {
    const currentData = matrixData[traceabilityType];
    if (currentData && currentData.length > 0) {
      exportRiskTraceabilityMatrixData(currentData, `risk_traceability_matrix_${traceabilityType}_${new Date().toISOString().split('T')[0]}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Risk Traceability Matrix</h1>
        <p className="text-gray-600">Generate comprehensive risk traceability matrices using AI-powered analysis</p>
        {mockFlag && (
          <div className="mt-4 p-3 bg-yellow-100 border border-yellow-400 rounded-md">
            <p className="text-yellow-800 text-sm">
              <i className="fa-solid fa-info-circle mr-2"></i>
              Using mock data (AI service unavailable)
            </p>
          </div>
        )}
      </div>

      {/* Input Form */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Project Name
            </label>
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="Enter project name..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Traceability Type
            </label>
            <select
              value={traceabilityType}
              onChange={(e) => setTraceabilityType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {TRACEABILITY_TYPES.map((type) => (
                <option key={type.key} value={type.key}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>
        </div>
        
        <button
          onClick={generateTraceabilityMatrix}
          disabled={isGenerating || !projectName.trim()}
          className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isGenerating ? (
            <>
              <i className="fa-solid fa-spinner fa-spin mr-2"></i>
              Generating Matrix...
            </>
          ) : (
            <>
              <i className="fa-solid fa-magic mr-2"></i>
              Generate Risk Traceability Matrix
            </>
          )}
        </button>
      </div>

      {/* Results Table */}
      {showTable && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Risk Traceability Matrix Results</h2>
              <div className="space-x-2">
                <button
                  onClick={handleSaveToProject}
                  className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
                >
                  <i className="fa-solid fa-save mr-2"></i>
                  Save to Project
                </button>
                <button
                  onClick={handleExportData}
                  className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700"
                >
                  <i className="fa-solid fa-download mr-2"></i>
                  Export Data
                </button>
              </div>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Requirements & Risks</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Controls & Verification</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status & Management</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {matrixData[traceabilityType]?.map((row) => (
                  <tr key={row.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="space-y-2">
                        <div>
                          <span className="font-medium text-gray-900">Requirement ID:</span>
                          <span className="ml-2 text-gray-600">{row.requirementId}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-900">Requirement:</span>
                          <p className="text-sm text-gray-600">{row.requirementDescription}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-900">Risk ID:</span>
                          <span className="ml-2 text-gray-600">{row.riskId}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-900">Risk:</span>
                          <p className="text-sm text-gray-600">{row.riskDescription}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-900">Risk Level:</span>
                          <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${
                            row.riskLevel === 'High' ? 'bg-red-100 text-red-800' :
                            row.riskLevel === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {row.riskLevel}
                          </span>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="space-y-2 text-sm">
                        <div>
                          <span className="font-medium text-gray-700">Control ID:</span>
                          <span className="ml-2 text-gray-600">{row.controlId}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Control:</span>
                          <p className="text-gray-600">{row.controlDescription}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Effectiveness:</span>
                          <span className="ml-2 text-gray-600">{row.controlEffectiveness}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Verification Method:</span>
                          <p className="text-gray-600">{row.verificationMethod}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Verification Status:</span>
                          <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            row.verificationStatus === 'Pass' ? 'bg-green-100 text-green-800' :
                            row.verificationStatus === 'Fail' ? 'bg-red-100 text-red-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {row.verificationStatus}
                          </span>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="space-y-2 text-sm">
                        <div>
                          <span className="font-medium text-gray-700">Responsible Party:</span>
                          <span className="ml-2 text-gray-600">{row.responsibleParty}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Verification Date:</span>
                          <span className="ml-2 text-gray-600">{row.verificationDate}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Matrix Owner:</span>
                          <span className="ml-2 text-gray-600">{row.matrixOwner}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Last Updated:</span>
                          <span className="ml-2 text-gray-600">{new Date(row.lastUpdated).toLocaleDateString()}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Version:</span>
                          <span className="ml-2 text-gray-600">{row.version}</span>
                        </div>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default RiskTraceabilityMatrixPage;
