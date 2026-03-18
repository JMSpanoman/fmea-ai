import React, { useState } from 'react';
import { exportRiskEvaluationReportData } from '../utils/exportUtils';

interface RiskEvaluationReportRow {
  id: string;
  riskDescription: string;
  riskCategory: string;
  riskLevel: string;
  probability: string;
  severity: string;
  exposureFrequency: string;
  riskScore: string;
  affectedStakeholders: string;
  businessImpact: string;
  financialImpact: string;
  operationalImpact: string;
  complianceImpact: string;
  riskControls: string;
  controlEffectiveness: string;
  residualRisk: string;
  riskOwner: string;
  targetDate: string;
  status: string;
  riskAssessmentMethod: string;
  fmeaLink: string;
  regulatoryRequirements: string;
  closureSummary: string;
  milestones: string;
  riskControlsUpdate: string;
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

const RiskEvaluationReportPage: React.FC = () => {
  const [riskDescription, setRiskDescription] = useState('');
  const [riskCategory, setRiskCategory] = useState('Information Security');
  const [isGenerating, setIsGenerating] = useState(false);
  const [riskData, setRiskData] = useState<{ [key: string]: RiskEvaluationReportRow[] }>({});
  const [showTable, setShowTable] = useState(false);
  const [mockFlag, setMockFlag] = useState(false);

  const handleGenerateReport = async () => {
    if (!riskDescription.trim()) {
      alert('Please enter a risk description');
      return;
    }

    setIsGenerating(true);
    console.log('Setting isGenerating to true');
    
    try {
      // Call backend API
      console.log('Starting AI generation via backend API...');
      const api = window.fmeaApi;
      
      const response = await api.generateRiskEvaluationReport({
        risk_description: riskDescription || 'Default cybersecurity risk',
        risk_category: riskCategory
      });
      
      console.log('Backend API response:', response);
      
      if (response.risk_evaluation_data && response.risk_evaluation_data.length > 0) {
        // Convert backend data to frontend format
        const convertedData = response.risk_evaluation_data.map((item: any) => ({
          id: item.id || `RE-${Date.now().toString().slice(-6)}`,
          riskDescription: item.risk_description || 'Default cybersecurity risk',
          riskCategory: item.risk_category || "Information Security",
          riskLevel: item.risk_level || "High",
          probability: item.probability || "Medium",
          severity: item.severity || "High",
          exposureFrequency: item.exposure_frequency || "Continuous",
          riskScore: item.risk_score || "High",
          affectedStakeholders: item.affected_stakeholders || "Employees, customers, shareholders",
          businessImpact: item.business_impact || "Significant disruption to operations",
          financialImpact: item.financial_impact || "Potential loss of $500K-$1M annually",
          operationalImpact: item.operational_impact || "Reduced efficiency, increased costs",
          complianceImpact: item.compliance_impact || "Regulatory violations, fines",
          riskControls: item.risk_controls || "Regular monitoring, training, procedures",
          controlEffectiveness: item.control_effectiveness || "Moderate",
          residualRisk: item.residual_risk || "Medium",
          riskOwner: item.risk_owner || "Risk Manager",
          targetDate: item.target_date || "2025-12-31",
          status: item.status || "Open",
          riskAssessmentMethod: item.risk_assessment_method || "Risk Matrix, FMEA, Monte Carlo",
          fmeaLink: item.fmea_link || "Link to FMEA-001",
          regulatoryRequirements: item.regulatory_requirements || "ISO 31000, COSO, Basel III",
          closureSummary: item.closure_summary || "AI generated closure summary",
          milestones: item.milestones || "Phase 1 complete by 2025-09-30",
          riskControlsUpdate: item.risk_controls_update || "Updated risk control document RC-006",
          analysis_timestamp: item.analysis_timestamp || new Date().toISOString(),
          version: item.version || "1.0"
        }));

        console.log('Converted risk evaluation data:', convertedData);
        
        setRiskData({
          [riskCategory]: convertedData,
        });
        setMockFlag(response.mock);
        setShowTable(true);
        setIsGenerating(false);
      } else {
        console.log('No risk evaluation data in response, using mock data');
        // Fallback to mock data if API doesn't return data
        const mockData: RiskEvaluationReportRow[] = [
          {
            id: `RE-${Date.now().toString().slice(-6)}`,
            riskDescription: riskDescription || 'Cybersecurity breach leading to data loss',
            riskCategory: riskCategory,
            riskLevel: 'High',
            probability: 'Medium',
            severity: 'High',
            exposureFrequency: 'Continuous',
            riskScore: 'High',
            affectedStakeholders: 'Employees, customers, shareholders, suppliers',
            businessImpact: 'Significant disruption to operations, potential revenue loss',
            financialImpact: 'Potential loss of $500K-$1M annually, increased insurance costs',
            operationalImpact: 'Reduced efficiency, increased operational costs, process delays',
            complianceImpact: 'Regulatory violations, potential fines, legal action',
            riskControls: 'Regular monitoring, employee training, documented procedures, insurance coverage',
            controlEffectiveness: 'Moderate',
            residualRisk: 'Medium',
            riskOwner: 'Risk Manager',
            targetDate: '2025-12-31',
            status: 'Open',
            riskAssessmentMethod: 'Risk Matrix, FMEA, Monte Carlo Simulation, Expert Judgment',
            fmeaLink: 'Link to FMEA-001',
            regulatoryRequirements: 'ISO 31000, COSO Framework, Basel III, Sarbanes-Oxley',
            closureSummary: 'Comprehensive risk evaluation completed with detailed mitigation plan',
            milestones: 'Phase 1 complete by 2025-09-30, Phase 2 by 2025-12-31',
            riskControlsUpdate: 'Updated risk control document RC-006',
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
      console.error('Error generating risk evaluation report:', error);
      console.log('Using fallback mock data due to API error');
      
      // Fallback to mock data
      const mockData: RiskEvaluationReportRow[] = [
        {
          id: `RE-${Date.now().toString().slice(-6)}`,
          riskDescription: riskDescription || 'Cybersecurity breach leading to data loss',
          riskCategory: riskCategory,
          riskLevel: 'High',
          probability: 'Medium',
          severity: 'High',
          exposureFrequency: 'Continuous',
          riskScore: 'High',
          affectedStakeholders: 'Employees, customers, shareholders, suppliers',
          businessImpact: 'Significant disruption to operations, potential revenue loss',
          financialImpact: 'Potential loss of $500K-$1M annually, increased insurance costs',
          operationalImpact: 'Reduced efficiency, increased operational costs, process delays',
          complianceImpact: 'Regulatory violations, potential fines, legal action',
          riskControls: 'Regular monitoring, employee training, documented procedures, insurance coverage',
          controlEffectiveness: 'Moderate',
          residualRisk: 'Medium',
          riskOwner: 'Risk Manager',
          targetDate: '2025-12-31',
          status: 'Open',
          riskAssessmentMethod: 'Risk Matrix, FMEA, Monte Carlo Simulation, Expert Judgment',
          fmeaLink: 'Link to FMEA-001',
          regulatoryRequirements: 'ISO 31000, COSO Framework, Basel III, Sarbanes-Oxley',
          closureSummary: 'Comprehensive risk evaluation completed with detailed mitigation plan',
          milestones: 'Phase 1 complete by 2025-09-30, Phase 2 by 2025-12-31',
          riskControlsUpdate: 'Updated risk control document RC-006',
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
        // Save each risk evaluation report
        for (const report of currentData) {
          await api.saveRiskEvaluationReport({
            risk_description: report.riskDescription,
            risk_category: report.riskCategory,
            risk_level: report.riskLevel,
            probability: report.probability,
            severity: report.severity,
            exposure_frequency: report.exposureFrequency,
            risk_score: report.riskScore,
            affected_stakeholders: report.affectedStakeholders,
            business_impact: report.businessImpact,
            financial_impact: report.financialImpact,
            operational_impact: report.operationalImpact,
            compliance_impact: report.complianceImpact,
            risk_controls: report.riskControls,
            control_effectiveness: report.controlEffectiveness,
            residual_risk: report.residualRisk,
            risk_owner: report.riskOwner,
            target_date: report.targetDate,
            status: report.status,
            risk_assessment_method: report.riskAssessmentMethod,
            fmea_link: report.fmeaLink,
            regulatory_requirements: report.regulatoryRequirements,
            closure_summary: report.closureSummary,
            milestones: report.milestones,
            risk_controls_update: report.riskControlsUpdate,
            analysis_timestamp: report.analysis_timestamp,
            version: report.version,
            project_id: 1 // Default project ID
          });
        }
        
        alert('Risk evaluation reports saved to project successfully!');
      }
    } catch (error) {
      console.error('Error saving to project:', error);
      alert('Failed to save to project. Please try again.');
    }
  };

  const handleExportData = () => {
    const currentData = riskData[riskCategory];
    if (currentData && currentData.length > 0) {
      exportRiskEvaluationReportData(currentData, `risk_evaluation_report_${riskCategory}_${new Date().toISOString().split('T')[0]}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Risk Evaluation Report</h1>
        <p className="text-gray-600">Generate comprehensive risk evaluation reports using AI-powered analysis</p>
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
              Risk Description
            </label>
            <textarea
              value={riskDescription}
              onChange={(e) => setRiskDescription(e.target.value)}
              placeholder="Describe the risk you want to evaluate..."
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
        </div>
        
        <button
          onClick={handleGenerateReport}
          disabled={isGenerating || !riskDescription.trim()}
          className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isGenerating ? (
            <>
              <i className="fa-solid fa-spinner fa-spin mr-2"></i>
              Generating Report...
            </>
          ) : (
            <>
              <i className="fa-solid fa-magic mr-2"></i>
              Generate Risk Evaluation Report
            </>
          )}
        </button>
      </div>

      {/* Results Table */}
      {showTable && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Risk Evaluation Results</h2>
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
                  className="bg-purple-300 text-gray-900 px-4 py-2 rounded-md hover:bg-purple-400"
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
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk Details</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Impact Assessment</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Controls & Status</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {riskData[riskCategory]?.map((report) => (
                  <tr key={report.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="space-y-2">
                        <div>
                          <span className="font-medium text-gray-900">Description:</span>
                          <p className="text-sm text-gray-600">{report.riskDescription}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-900">Category:</span>
                          <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {report.riskCategory}
                          </span>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          <div>
                            <span className="font-medium text-gray-700">Risk Level:</span>
                            <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${
                              report.riskLevel === 'High' ? 'bg-red-100 text-red-800' :
                              report.riskLevel === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-green-100 text-green-800'
                            }`}>
                              {report.riskLevel}
                            </span>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">Probability:</span>
                            <span className="ml-2 text-gray-600">{report.probability}</span>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">Severity:</span>
                            <span className="ml-2 text-gray-600">{report.severity}</span>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">Risk Score:</span>
                            <span className="ml-2 text-gray-600">{report.riskScore}</span>
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="space-y-2 text-sm">
                        <div>
                          <span className="font-medium text-gray-700">Business Impact:</span>
                          <p className="text-gray-600">{report.businessImpact}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Financial Impact:</span>
                          <p className="text-gray-600">{report.financialImpact}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Operational Impact:</span>
                          <p className="text-gray-600">{report.operationalImpact}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Compliance Impact:</span>
                          <p className="text-gray-600">{report.complianceImpact}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Affected Stakeholders:</span>
                          <p className="text-gray-600">{report.affectedStakeholders}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="space-y-2 text-sm">
                        <div>
                          <span className="font-medium text-gray-700">Risk Controls:</span>
                          <p className="text-gray-600">{report.riskControls}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Control Effectiveness:</span>
                          <span className="ml-2 text-gray-600">{report.controlEffectiveness}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Residual Risk:</span>
                          <span className="ml-2 text-gray-600">{report.residualRisk}</span>
                        </div>
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

export default RiskEvaluationReportPage;
