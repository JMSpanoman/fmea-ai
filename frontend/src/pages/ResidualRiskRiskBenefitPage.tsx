import React, { useState } from 'react';
import { exportResidualRiskRiskBenefitData } from '../utils/exportUtils';

interface ResidualRiskRiskBenefitRow {
  id: string;
  riskDescription: string;
  riskCategory: string;
  benefitDescription: string;
  residualRiskLevel: string;
  residualProbability: string;
  residualSeverity: string;
  riskReductionEffectiveness: string;
  riskOwner: string;
  targetDate: string;
  status: string;
  analysis_timestamp: string;
  version: string;
}

const RISK_CATEGORIES = [
  "Information Security",
  "Financial Risk",
  "Operational Risk",
  "Compliance Risk",
  "Strategic Risk",
  "Market Risk",
  "Credit Risk",
  "Liquidity Risk",
  "Technology Risk",
  "Environmental Risk",
  "Health and Safety",
  "Reputational Risk"
];

const ResidualRiskRiskBenefitPage: React.FC = () => {
  const [riskDescription, setRiskDescription] = useState('');
  const [riskCategory, setRiskCategory] = useState('Information Security');
  const [benefitDescription, setBenefitDescription] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [riskData, setRiskData] = useState<{ [key: string]: ResidualRiskRiskBenefitRow[] }>({});
  const [showTable, setShowTable] = useState(false);
  const [mockFlag, setMockFlag] = useState(false);

  const handleGenerateReport = async () => {
    if (!riskDescription.trim() || !benefitDescription.trim()) {
      alert('Please enter both risk description and benefit description');
      return;
    }

    setIsGenerating(true);
    console.log('Setting isGenerating to true');
    
    try {
      // Call backend API
      console.log('Starting AI generation via backend API...');
      const api = window.fmeaApi;
      
      const response = await api.generateResidualRiskRiskBenefit({
        risk_description: riskDescription || 'Default cybersecurity risk',
        risk_category: riskCategory,
        benefit_description: benefitDescription || 'Default benefit description'
      });
      
      console.log('Backend API response:', response);
      
      if (response.residual_risk_benefit_data && response.residual_risk_benefit_data.length > 0) {
        // Convert backend data to frontend format
        const convertedData = response.residual_risk_benefit_data.map((item: any) => ({
          id: item.id || `RR-${Date.now().toString().slice(-6)}`,
          riskDescription: item.risk_description || 'Default cybersecurity risk',
          riskCategory: item.risk_category || "Information Security",
          benefitDescription: item.benefit_description || 'Default benefit description',
          residualRiskLevel: item.residual_risk_level || "High",
          residualProbability: item.residual_probability || "Medium",
          residualSeverity: item.residual_severity || "High",
          riskReductionEffectiveness: item.risk_reduction_effectiveness || "Moderate",
          riskOwner: item.risk_owner || "Risk Manager",
          targetDate: item.target_date || "2025-12-31",
          status: item.status || "Open",
          analysis_timestamp: item.analysis_timestamp || new Date().toISOString(),
          version: item.version || "1.0"
        }));

        console.log('Converted residual risk risk-benefit data:', convertedData);
        
        setRiskData({
          [riskCategory]: convertedData,
        });
        setMockFlag(response.mock);
        setShowTable(true);
        setIsGenerating(false);
      } else {
        console.log('No residual risk risk-benefit data in response, using mock data');
        // Fallback to mock data if API doesn't return data
        const mockData: ResidualRiskRiskBenefitRow[] = [
          {
            id: `RR-${Date.now().toString().slice(-6)}`,
            riskDescription: riskDescription || 'Cybersecurity breach leading to data loss',
            riskCategory: riskCategory,
            benefitDescription: benefitDescription || 'Enhanced security measures and compliance',
            residualRiskLevel: 'Medium',
            residualProbability: 'Low',
            residualSeverity: 'Medium',
            riskReductionEffectiveness: 'High',
            riskOwner: 'Risk Manager',
            targetDate: '2025-12-31',
            status: 'Open',
            analysis_timestamp: new Date().toISOString(),
            version: '1.0'
          }
        ];

        setRiskData({
          [riskCategory]: mockData,
        });
        setMockFlag(true);
        setShowTable(true);
        setIsGenerating(false);
      }
    } catch (error) {
      console.error('Error generating residual risk risk-benefit report:', error);
      console.log('Using fallback mock data due to API error');
      
      // Fallback to mock data
      const mockData: ResidualRiskRiskBenefitRow[] = [
        {
          id: `RR-${Date.now().toString().slice(-6)}`,
          riskDescription: riskDescription || 'Cybersecurity breach leading to data loss',
          riskCategory: riskCategory,
          benefitDescription: benefitDescription || 'Enhanced security measures and compliance',
          residualRiskLevel: 'Medium',
          residualProbability: 'Low',
          residualSeverity: 'Medium',
          riskReductionEffectiveness: 'High',
          riskOwner: 'Risk Manager',
          targetDate: '2025-12-31',
          status: 'Open',
          analysis_timestamp: new Date().toISOString(),
          version: '1.0'
        }
      ];

      setRiskData({
        [riskCategory]: mockData,
      });
      setMockFlag(true);
      setShowTable(true);
      setIsGenerating(false);
    }
  };

  const handleSaveToProject = async () => {
    try {
      const api = window.fmeaApi;
      const currentData = riskData[riskCategory];
      
      if (currentData && currentData.length > 0) {
        // Save each residual risk risk-benefit report
        for (const report of currentData) {
          await api.saveResidualRiskRiskBenefit({
            risk_description: report.riskDescription,
            risk_category: report.riskCategory,
            benefit_description: report.benefitDescription,
            residual_risk_level: report.residualRiskLevel,
            residual_probability: report.residualProbability,
            residual_severity: report.residualSeverity,
            risk_reduction_effectiveness: report.riskReductionEffectiveness,
            risk_owner: report.riskOwner,
            target_date: report.targetDate,
            status: report.status,
            analysis_timestamp: report.analysis_timestamp,
            version: report.version,
            project_id: 1 // Default project ID
          });
        }
        
        alert('Residual risk and risk-benefit analysis saved to project successfully!');
      }
    } catch (error) {
      console.error('Error saving to project:', error);
      alert('Failed to save to project. Please try again.');
    }
  };

  const handleExportData = () => {
    const currentData = riskData[riskCategory];
    if (currentData && currentData.length > 0) {
      exportResidualRiskRiskBenefitData(currentData, `residual_risk_risk_benefit_${riskCategory}_${new Date().toISOString().split('T')[0]}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Residual Risk & Risk-Benefit Analysis</h1>
        <p className="text-gray-600">Generate comprehensive residual risk and risk-benefit analysis using AI-powered assessment</p>
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
              Risk Description
            </label>
            <textarea
              value={riskDescription}
              onChange={(e) => setRiskDescription(e.target.value)}
              placeholder="Describe the risk you want to analyze..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Risk Category
            </label>
            <select
              value={riskCategory}
              onChange={(e) => setRiskCategory(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {RISK_CATEGORIES.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Benefit Description
            </label>
            <textarea
              value={benefitDescription}
              onChange={(e) => setBenefitDescription(e.target.value)}
              placeholder="Describe the expected benefit..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
            />
          </div>
        </div>
        
        <button
          onClick={handleGenerateReport}
          disabled={isGenerating || !riskDescription.trim() || !benefitDescription.trim()}
          className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isGenerating ? (
            <>
              <i className="fa-solid fa-spinner fa-spin mr-2"></i>
              Generating Analysis...
            </>
          ) : (
            <>
              <i className="fa-solid fa-magic mr-2"></i>
              Generate Residual Risk & Risk-Benefit Analysis
            </>
          )}
        </button>
      </div>

      {/* Results Table */}
      {showTable && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Residual Risk & Risk-Benefit Analysis Results</h2>
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
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk & Benefit Details</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Residual Risk Assessment</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status & Management</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {riskData[riskCategory]?.map((report) => (
                  <tr key={report.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="space-y-2">
                        <div>
                          <span className="font-medium text-gray-900">Risk Description:</span>
                          <p className="text-sm text-gray-600">{report.riskDescription}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-900">Benefit Description:</span>
                          <p className="text-sm text-gray-600">{report.benefitDescription}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-900">Category:</span>
                          <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {report.riskCategory}
                          </span>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="space-y-2 text-sm">
                        <div>
                          <span className="font-medium text-gray-700">Residual Risk Level:</span>
                          <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${
                            report.residualRiskLevel === 'High' ? 'bg-red-100 text-red-800' :
                            report.residualRiskLevel === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {report.residualRiskLevel}
                          </span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Residual Probability:</span>
                          <span className="ml-2 text-gray-600">{report.residualProbability}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Residual Severity:</span>
                          <span className="ml-2 text-gray-600">{report.residualSeverity}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Risk Reduction Effectiveness:</span>
                          <span className="ml-2 text-gray-600">{report.riskReductionEffectiveness}</span>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="space-y-2 text-sm">
                        <div>
                          <span className="font-medium text-gray-700">Risk Owner:</span>
                          <span className="ml-2 text-gray-600">{report.riskOwner}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Status:</span>
                          <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            report.status === 'Open' ? 'bg-red-100 text-red-800' :
                            report.status === 'In Progress' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {report.status}
                          </span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Target Date:</span>
                          <span className="ml-2 text-gray-600">{report.targetDate}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Version:</span>
                          <span className="ml-2 text-gray-600">{report.version}</span>
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

export default ResidualRiskRiskBenefitPage;
