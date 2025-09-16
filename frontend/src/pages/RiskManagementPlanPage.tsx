import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ProjectDataViewer from '../components/ProjectDataViewer';
import { exportRiskManagementPlanData } from '../utils/exportUtils';

interface RiskManagementPlanRow {
  id: string;
  planSection: string;
  sectionDescription: string;
  keyObjectives: string;
  riskCategories: string;
  riskAssessmentMethod: string;
  riskResponseStrategies: string;
  monitoringFrequency: string;
  responsibleParty: string;
  targetCompletionDate: string;
  status: string;
  planOwner: string;
  lastUpdated: string;
  version: string;
}

const PLAN_TYPES = [
  { key: 'strategic', label: 'Strategic Risk Management Plan' },
  { key: 'operational', label: 'Operational Risk Management Plan' },
  { key: 'project', label: 'Project Risk Management Plan' },
  { key: 'enterprise', label: 'Enterprise Risk Management Plan' },
  { key: 'compliance', label: 'Compliance Risk Management Plan' },
  { key: 'financial', label: 'Financial Risk Management Plan' },
  { key: 'technology', label: 'Technology Risk Management Plan' },
  { key: 'cybersecurity', label: 'Cybersecurity Risk Management Plan' },
];

const INDUSTRY_SECTORS = [
  { key: 'manufacturing', label: 'Manufacturing' },
  { key: 'healthcare', label: 'Healthcare' },
  { key: 'financial_services', label: 'Financial Services' },
  { key: 'technology', label: 'Technology' },
  { key: 'energy', label: 'Energy' },
  { key: 'construction', label: 'Construction' },
  { key: 'transportation', label: 'Transportation' },
  { key: 'retail', label: 'Retail' },
  { key: 'pharmaceuticals', label: 'Pharmaceuticals' },
  { key: 'aerospace', label: 'Aerospace' },
];

const RiskManagementPlanPage: React.FC = () => {
  const navigate = useNavigate();
  const [projectName, setProjectName] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [planType, setPlanType] = useState('strategic');
  const [industrySector, setIndustrySector] = useState('manufacturing');
  const [planData, setPlanData] = useState<{ [key: string]: RiskManagementPlanRow[] }>({});
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

  const generateRiskManagementPlan = async () => {
    console.log('generateRiskManagementPlan called');
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
      
      const response = await api.generateRiskManagementPlan({
        project_name: projectName || 'Default Project',
        plan_type: planType,
        industry_sector: industrySector
      });
      
      console.log('Backend API response:', response);
      
      if (response.risk_management_plan_data && response.risk_management_plan_data.length > 0) {
        // Convert backend data to frontend format
        const convertedData = response.risk_management_plan_data.map((item: any) => ({
          id: item.id || `RMP-${Date.now().toString().slice(-6)}`,
          planSection: item.plan_section || 'Default Section',
          sectionDescription: item.section_description || 'Default description',
          keyObjectives: item.key_objectives || 'Default objectives',
          riskCategories: item.risk_categories || 'Default categories',
          riskAssessmentMethod: item.risk_assessment_method || 'Default method',
          riskResponseStrategies: item.risk_response_strategies || 'Default strategies',
          monitoringFrequency: item.monitoring_frequency || 'Default frequency',
          responsibleParty: item.responsible_party || 'Default party',
          targetCompletionDate: item.target_completion_date || '2025-12-31',
          status: item.status || 'Draft',
          planOwner: item.plan_owner || 'Default Owner',
          lastUpdated: item.last_updated || new Date().toISOString(),
          version: item.version || '1.0'
        }));

        console.log('Converted risk management plan data:', convertedData);
        
        setPlanData({
          [planType]: convertedData,
        });
        setMockFlag(response.mock);
        setShowTable(true);
        setIsGenerating(false);
      } else {
        console.log('No risk management plan data in response, using mock data');
        // Fallback to mock data if API doesn't return data
        const mockData: RiskManagementPlanRow[] = [
          {
            id: `RMP-${Date.now().toString().slice(-6)}`,
            planSection: 'Executive Summary',
            sectionDescription: 'High-level overview of the risk management approach and governance structure for the project',
            keyObjectives: 'Establish comprehensive risk management framework and governance structure',
            riskCategories: 'Strategic, Operational, Financial, Compliance, Technology',
            riskAssessmentMethod: 'Qualitative and quantitative analysis with expert judgment',
            riskResponseStrategies: 'Avoid, Transfer, Mitigate, Accept with monitoring',
            monitoringFrequency: 'Monthly',
            responsibleParty: 'Risk Manager',
            targetCompletionDate: '2025-03-31',
            status: 'Draft',
            planOwner: 'Chief Risk Officer',
            lastUpdated: new Date().toISOString(),
            version: '1.0'
          }
        ];

        setPlanData({
          [planType]: mockData,
        });
        setMockFlag(true);
        setShowTable(true);
        setIsGenerating(false);
      }
    } catch (error) {
      console.error('Error generating risk management plan:', error);
      console.log('Using fallback mock data due to API error');
      
      // Fallback to mock data
      const mockData: RiskManagementPlanRow[] = [
        {
          id: `RMP-${Date.now().toString().slice(-6)}`,
          planSection: 'Executive Summary',
          sectionDescription: 'High-level overview of the risk management approach and governance structure for the project',
          keyObjectives: 'Establish comprehensive risk management framework and governance structure',
          riskCategories: 'Strategic, Operational, Financial, Compliance, Technology',
          riskAssessmentMethod: 'Qualitative and quantitative analysis with expert judgment',
          riskResponseStrategies: 'Avoid, Transfer, Mitigate, Accept with monitoring',
          monitoringFrequency: 'Monthly',
          responsibleParty: 'Risk Manager',
          targetCompletionDate: '2025-03-31',
          status: 'Draft',
          planOwner: 'Chief Risk Officer',
          lastUpdated: new Date().toISOString(),
          version: '1.0'
        }
      ];

      setPlanData({
        [planType]: mockData,
      });
      setMockFlag(true);
      setShowTable(true);
      setIsGenerating(false);
    }
  };

  const handleSaveToProject = async () => {
    try {
      const api = window.fmeaApi;
      const currentData = planData[planType];
      
      if (currentData && currentData.length > 0) {
        // Save each risk management plan row
        for (const row of currentData) {
          await api.saveRiskManagementPlan({
            plan_section: row.planSection,
            section_description: row.sectionDescription,
            key_objectives: row.keyObjectives,
            risk_categories: row.riskCategories,
            risk_assessment_method: row.riskAssessmentMethod,
            risk_response_strategies: row.riskResponseStrategies,
            monitoring_frequency: row.monitoringFrequency,
            responsible_party: row.responsibleParty,
            target_completion_date: row.targetCompletionDate,
            status: row.status,
            plan_owner: row.planOwner,
            last_updated: row.lastUpdated,
            version: row.version,
            project_id: 1 // Default project ID
          });
        }
        
        alert('Risk management plan saved to project successfully!');
      }
    } catch (error) {
      console.error('Error saving to project:', error);
      alert('Failed to save to project. Please try again.');
    }
  };

  const handleExportData = () => {
    const currentData = planData[planType];
    if (currentData && currentData.length > 0) {
      exportRiskManagementPlanData(currentData, `risk_management_plan_${planType}_${new Date().toISOString().split('T')[0]}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Risk Management Plan</h1>
        <p className="text-gray-600">Generate comprehensive risk management plans using AI-powered analysis</p>
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
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
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
              Plan Type
            </label>
            <select
              value={planType}
              onChange={(e) => setPlanType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {PLAN_TYPES.map((type) => (
                <option key={type.key} value={type.key}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Industry Sector
            </label>
            <select
              value={industrySector}
              onChange={(e) => setIndustrySector(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {INDUSTRY_SECTORS.map((sector) => (
                <option key={sector.key} value={sector.key}>
                  {sector.label}
                </option>
              ))}
            </select>
          </div>
        </div>
        
        <button
          onClick={generateRiskManagementPlan}
          disabled={isGenerating || !projectName.trim()}
          className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isGenerating ? (
            <>
              <i className="fa-solid fa-spinner fa-spin mr-2"></i>
              Generating Plan...
            </>
          ) : (
            <>
              <i className="fa-solid fa-magic mr-2"></i>
              Generate Risk Management Plan
            </>
          )}
        </button>
      </div>

      {/* Results Table */}
      {showTable && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Risk Management Plan Results</h2>
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
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Plan Section & Objectives</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk Categories & Methods</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Implementation & Status</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {planData[planType]?.map((row) => (
                  <tr key={row.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="space-y-2">
                        <div>
                          <span className="font-medium text-gray-900">Section:</span>
                          <span className="ml-2 text-gray-600">{row.planSection}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-900">Description:</span>
                          <p className="text-sm text-gray-600">{row.sectionDescription}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-900">Key Objectives:</span>
                          <p className="text-sm text-gray-600">{row.keyObjectives}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="space-y-2 text-sm">
                        <div>
                          <span className="font-medium text-gray-700">Risk Categories:</span>
                          <p className="text-gray-600">{row.riskCategories}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Assessment Method:</span>
                          <p className="text-gray-600">{row.riskAssessmentMethod}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Response Strategies:</span>
                          <p className="text-gray-600">{row.riskResponseStrategies}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Monitoring Frequency:</span>
                          <span className="ml-2 text-gray-600">{row.monitoringFrequency}</span>
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
                          <span className="font-medium text-gray-700">Target Date:</span>
                          <span className="ml-2 text-gray-600">{row.targetCompletionDate}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Status:</span>
                          <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            row.status === 'Complete' ? 'bg-green-100 text-green-800' :
                            row.status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
                            row.status === 'Under Review' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {row.status}
                          </span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Plan Owner:</span>
                          <span className="ml-2 text-gray-600">{row.planOwner}</span>
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

export default RiskManagementPlanPage;
