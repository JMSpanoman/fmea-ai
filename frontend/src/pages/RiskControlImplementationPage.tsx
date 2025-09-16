import React, { useState } from 'react';
import { exportRiskControlImplementationData } from '../utils/exportUtils';

interface RiskControlImplementationRow {
  id: string;
  controlName: string;
  controlType: string;
  riskCategory: string;
  riskLevel: string;
  controlPriority: string;
  implementationStatus: string;
  controlDescription: string;
  controlObjectives: string;
  controlMechanisms: string;
  controlFrequency: string;
  controlEffectiveness: string;
  controlOwner: string;
  responsibleTeam: string;
  targetCompletionDate: string;
  actualCompletionDate: string;
  implementationCost: string;
  resourceRequirements: string;
  trainingRequirements: string;
  monitoringPlan: string;
  keyPerformanceIndicators: string;
  successCriteria: string;
  riskAssessmentMethod: string;
  fmeaLink: string;
  regulatoryRequirements: string;
  implementationSummary: string;
  lessonsLearned: string;
  nextSteps: string;
  controlDocumentation: string;
  analysis_timestamp: string;
  version: string;
}

const CONTROL_TYPES = [
  "Technical",
  "Administrative",
  "Physical",
  "Preventive",
  "Detective",
  "Corrective",
  "Compensating",
  "Deterrent"
];

const RiskControlImplementationPage: React.FC = () => {
  const [controlName, setControlName] = useState('');
  const [controlType, setControlType] = useState('Technical');
  const [isGenerating, setIsGenerating] = useState(false);
  const [controlData, setControlData] = useState<{ [key: string]: RiskControlImplementationRow[] }>({});
  const [showTable, setShowTable] = useState(false);
  const [mockFlag, setMockFlag] = useState(false);

  const handleGenerateReport = async () => {
    if (!controlName.trim()) {
      alert('Please enter a control name');
      return;
    }

    setIsGenerating(true);
    console.log('Setting isGenerating to true');
    
    try {
      // Call backend API
      console.log('Starting AI generation via backend API...');
      const api = window.fmeaApi;
      
      const response = await api.generateRiskControlImplementation({
        control_name: controlName || 'Default cybersecurity control',
        control_type: controlType
      });
      
      console.log('Backend API response:', response);
      
      if (response.risk_control_data && response.risk_control_data.length > 0) {
        // Convert backend data to frontend format
        const convertedData = response.risk_control_data.map((item: any) => ({
          id: item.id || `RC-${Date.now().toString().slice(-6)}`,
          controlName: item.control_name || 'Default cybersecurity control',
          controlType: item.control_type || "Technical",
          riskCategory: item.risk_category || "Information Security",
          riskLevel: item.risk_level || "High",
          controlPriority: item.control_priority || "High",
          implementationStatus: item.implementation_status || "Not Started",
          controlDescription: item.control_description || "Comprehensive cybersecurity control implementation",
          controlObjectives: item.control_objectives || "Reduce cybersecurity risk exposure",
          controlMechanisms: item.control_mechanisms || "Multi-layered security approach",
          controlFrequency: item.control_frequency || "Continuous",
          controlEffectiveness: item.control_effectiveness || "High",
          controlOwner: item.control_owner || "Chief Information Security Officer",
          responsibleTeam: item.responsible_team || "IT Security Team",
          targetCompletionDate: item.target_completion_date || "2025-12-31",
          actualCompletionDate: item.actual_completion_date || "TBD",
          implementationCost: item.implementation_cost || "$50K-$100K",
          resourceRequirements: item.resource_requirements || "Security software, hardware, training",
          trainingRequirements: item.training_requirements || "Cybersecurity awareness training",
          monitoringPlan: item.monitoring_plan || "24/7 security monitoring",
          keyPerformanceIndicators: item.key_performance_indicators || "Reduction in security incidents",
          successCriteria: item.success_criteria || "Zero major security breaches",
          riskAssessmentMethod: item.risk_assessment_method || "Risk Matrix, FMEA",
          fmeaLink: item.fmea_link || "Link to FMEA-001",
          regulatoryRequirements: item.regulatory_requirements || "ISO 27001, NIST, GDPR",
          implementationSummary: item.implementation_summary || "AI generated implementation summary",
          lessonsLearned: item.lessons_learned || "Early stakeholder engagement critical",
          nextSteps: item.next_steps || "Stakeholder approval, resource allocation",
          controlDocumentation: item.control_documentation || "Control procedures, user guides",
          analysis_timestamp: item.analysis_timestamp || new Date().toISOString(),
          version: item.version || "1.0"
        }));

        console.log('Converted risk control implementation data:', convertedData);
        
        setControlData({
          [controlType]: convertedData,
        });
        setMockFlag(response.mock);
        setShowTable(true);
        setIsGenerating(false);
      } else {
        console.log('No risk control data in response, using mock data');
        // Fallback to mock data if API doesn't return data
        const mockData: RiskControlImplementationRow[] = [
          {
            id: `RC-${Date.now().toString().slice(-6)}`,
            controlName: controlName || 'Comprehensive Cybersecurity Control Implementation',
            controlType: controlType,
            riskCategory: 'Information Security',
            riskLevel: 'High',
            controlPriority: 'High',
            implementationStatus: 'Not Started',
            controlDescription: 'Comprehensive cybersecurity control implementation including technical, administrative, and physical controls',
            controlObjectives: 'Reduce cybersecurity risk exposure, ensure compliance with regulations, protect sensitive data and systems',
            controlMechanisms: 'Multi-layered security approach including firewalls, intrusion detection, access controls, encryption, monitoring',
            controlFrequency: 'Continuous',
            controlEffectiveness: 'High',
            controlOwner: 'Chief Information Security Officer',
            responsibleTeam: 'IT Security Team, Risk Management Team, Compliance Team',
            targetCompletionDate: '2025-12-31',
            actualCompletionDate: 'TBD',
            implementationCost: '$50K-$100K',
            resourceRequirements: 'Security software licenses, hardware upgrades, staff training, external consultants',
            trainingRequirements: 'Cybersecurity awareness training, technical training for IT staff, management training',
            monitoringPlan: '24/7 security monitoring, regular vulnerability assessments, incident response procedures',
            keyPerformanceIndicators: 'Reduction in security incidents, compliance score improvement, risk assessment scores',
            successCriteria: 'Zero major security breaches, 100% regulatory compliance, reduced risk exposure by 80%',
            riskAssessmentMethod: 'Risk Matrix, FMEA, Control Assessment, Threat Modeling',
            fmeaLink: 'Link to FMEA-001',
            regulatoryRequirements: 'ISO 27001, NIST Cybersecurity Framework, GDPR, SOX',
            implementationSummary: 'Comprehensive risk control implementation plan with phased approach and clear milestones',
            lessonsLearned: 'Early stakeholder engagement critical, phased implementation reduces risk, regular communication essential',
            nextSteps: 'Stakeholder approval, resource allocation, project kickoff, detailed project planning',
            controlDocumentation: 'Control procedures, user guides, training materials, compliance documentation',
            analysis_timestamp: new Date().toISOString(),
            version: '1.0'
          }
        ];

        setControlData({
          [controlType]: mockData,
        });
        setMockFlag(true);
        setShowTable(true);
        setIsGenerating(false);
      }
    } catch (error) {
      console.error('Error generating risk control implementation:', error);
      console.log('Using fallback mock data due to API error');
      
      // Fallback to mock data
      const mockData: RiskControlImplementationRow[] = [
        {
          id: `RC-${Date.now().toString().slice(-6)}`,
          controlName: controlName || 'Comprehensive Cybersecurity Control Implementation',
          controlType: controlType,
          riskCategory: 'Information Security',
          riskLevel: 'High',
          controlPriority: 'High',
          implementationStatus: 'Not Started',
          controlDescription: 'Comprehensive cybersecurity control implementation including technical, administrative, and physical controls',
          controlObjectives: 'Reduce cybersecurity risk exposure, ensure compliance with regulations, protect sensitive data and systems',
          controlMechanisms: 'Multi-layered security approach including firewalls, intrusion detection, access controls, encryption, monitoring',
          controlFrequency: 'Continuous',
          controlEffectiveness: 'High',
          controlOwner: 'Chief Information Security Officer',
          responsibleTeam: 'IT Security Team, Risk Management Team, Compliance Team',
          targetCompletionDate: '2025-12-31',
          actualCompletionDate: 'TBD',
          implementationCost: '$50K-$100K',
          resourceRequirements: 'Security software licenses, hardware upgrades, staff training, external consultants',
          trainingRequirements: 'Cybersecurity awareness training, technical training for IT staff, management training',
          monitoringPlan: '24/7 security monitoring, regular vulnerability assessments, incident response procedures',
          keyPerformanceIndicators: 'Reduction in security incidents, compliance score improvement, risk assessment scores',
          successCriteria: 'Zero major security breaches, 100% regulatory compliance, reduced risk exposure by 80%',
          riskAssessmentMethod: 'Risk Matrix, FMEA, Control Assessment, Threat Modeling',
          fmeaLink: 'Link to FMEA-001',
          regulatoryRequirements: 'ISO 27001, NIST Cybersecurity Framework, GDPR, SOX',
          implementationSummary: 'Comprehensive risk control implementation plan with phased approach and clear milestones',
          lessonsLearned: 'Early stakeholder engagement critical, phased implementation reduces risk, regular communication essential',
          nextSteps: 'Stakeholder approval, resource allocation, project kickoff, detailed project planning',
          controlDocumentation: 'Control procedures, user guides, training materials, compliance documentation',
          analysis_timestamp: new Date().toISOString(),
          version: '1.0'
        }
      ];

      setControlData({
        [controlType]: mockData,
      });
      setMockFlag(true);
      setShowTable(true);
      setIsGenerating(false);
    }
  };

  const handleSaveToProject = async () => {
    try {
      const api = window.fmeaApi;
      const currentData = controlData[controlType];
      
      if (currentData && currentData.length > 0) {
        // Save each risk control implementation
        for (const control of currentData) {
          await api.saveRiskControlImplementation({
            control_name: control.controlName,
            control_type: control.controlType,
            risk_category: control.riskCategory,
            risk_level: control.riskLevel,
            control_priority: control.controlPriority,
            implementation_status: control.implementationStatus,
            control_description: control.controlDescription,
            control_objectives: control.controlObjectives,
            control_mechanisms: control.controlMechanisms,
            control_frequency: control.controlFrequency,
            control_effectiveness: control.controlEffectiveness,
            control_owner: control.controlOwner,
            responsible_team: control.responsibleTeam,
            target_completion_date: control.targetCompletionDate,
            actual_completion_date: control.actualCompletionDate,
            implementation_cost: control.implementationCost,
            resource_requirements: control.resourceRequirements,
            training_requirements: control.trainingRequirements,
            monitoring_plan: control.monitoringPlan,
            key_performance_indicators: control.keyPerformanceIndicators,
            success_criteria: control.successCriteria,
            risk_assessment_method: control.riskAssessmentMethod,
            fmea_link: control.fmeaLink,
            regulatory_requirements: control.regulatoryRequirements,
            implementation_summary: control.implementationSummary,
            lessons_learned: control.lessonsLearned,
            next_steps: control.nextSteps,
            control_documentation: control.controlDocumentation,
            analysis_timestamp: control.analysis_timestamp,
            version: control.version,
            project_id: 1 // Default project ID
          });
        }
        
        alert('Risk control implementations saved to project successfully!');
      }
    } catch (error) {
      console.error('Error saving to project:', error);
      alert('Failed to save to project. Please try again.');
    }
  };

  const handleExportData = () => {
    const currentData = controlData[controlType];
    if (currentData && currentData.length > 0) {
      exportRiskControlImplementationData(currentData, `risk_control_implementation_${controlType}_${new Date().toISOString().split('T')[0]}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Risk Control Implementation</h1>
        <p className="text-gray-600">Generate comprehensive risk control implementation plans using AI-powered analysis</p>
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
              Control Name
            </label>
            <textarea
              value={controlName}
              onChange={(e) => setControlName(e.target.value)}
              placeholder="Describe the risk control you want to implement..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Control Type
            </label>
            <select
              value={controlType}
              onChange={(e) => setControlType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {CONTROL_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>
        </div>
        
        <button
          onClick={handleGenerateReport}
          disabled={isGenerating || !controlName.trim()}
          className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isGenerating ? (
            <>
              <i className="fa-solid fa-spinner fa-spin mr-2"></i>
              Generating Implementation Plan...
            </>
          ) : (
            <>
              <i className="fa-solid fa-magic mr-2"></i>
              Generate Risk Control Implementation Plan
            </>
          )}
        </button>
      </div>

      {/* Results Table */}
      {showTable && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Risk Control Implementation Results</h2>
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
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Control Details</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Implementation Plan</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Resources & Status</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {controlData[controlType]?.map((control) => (
                  <tr key={control.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="space-y-2">
                        <div>
                          <span className="font-medium text-gray-900">Control Name:</span>
                          <p className="text-sm text-gray-600">{control.controlName}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-900">Type:</span>
                          <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {control.controlType}
                          </span>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          <div>
                            <span className="font-medium text-gray-700">Risk Level:</span>
                            <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${
                              control.riskLevel === 'High' ? 'bg-red-100 text-red-800' :
                              control.riskLevel === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-green-100 text-green-800'
                            }`}>
                              {control.riskLevel}
                            </span>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">Priority:</span>
                            <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${
                              control.controlPriority === 'High' ? 'bg-red-100 text-red-800' :
                              control.controlPriority === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-green-100 text-green-800'
                            }`}>
                              {control.controlPriority}
                            </span>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">Status:</span>
                            <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${
                              control.implementationStatus === 'Not Started' ? 'bg-red-100 text-red-800' :
                              control.implementationStatus === 'In Progress' ? 'bg-yellow-100 text-yellow-800' :
                              control.implementationStatus === 'Completed' ? 'bg-green-100 text-green-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              {control.implementationStatus}
                            </span>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">Effectiveness:</span>
                            <span className="ml-2 text-gray-600">{control.controlEffectiveness}</span>
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="space-y-2 text-sm">
                        <div>
                          <span className="font-medium text-gray-700">Description:</span>
                          <p className="text-gray-600">{control.controlDescription}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Objectives:</span>
                          <p className="text-gray-600">{control.controlObjectives}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Mechanisms:</span>
                          <p className="text-gray-600">{control.controlMechanisms}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Frequency:</span>
                          <span className="ml-2 text-gray-600">{control.controlFrequency}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Success Criteria:</span>
                          <p className="text-gray-600">{control.successCriteria}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="space-y-2 text-sm">
                        <div>
                          <span className="font-medium text-gray-700">Control Owner:</span>
                          <span className="ml-2 text-gray-600">{control.controlOwner}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Responsible Team:</span>
                          <span className="ml-2 text-gray-600">{control.responsibleTeam}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Target Date:</span>
                          <span className="ml-2 text-gray-600">{control.targetCompletionDate}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Implementation Cost:</span>
                          <span className="ml-2 text-gray-600">{control.implementationCost}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Resource Requirements:</span>
                          <p className="text-gray-600">{control.resourceRequirements}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Training Requirements:</span>
                          <p className="text-gray-600">{control.trainingRequirements}</p>
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

export default RiskControlImplementationPage;
