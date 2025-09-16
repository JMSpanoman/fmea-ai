import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ProjectDataViewer from '../components/ProjectDataViewer';
import TemplateManager from '../components/TemplateManager';
import { exportRiskManagementReportData } from '../utils/exportUtils';

interface RiskManagementReportRow {
  id: string;
  reportSection: string;
  sectionContent: string;
  riskMetrics: string;
  riskTrends: string;
  riskIncidents: string;
  complianceStatus: string;
  actionItems: string;
  responsibleParty: string;
  targetCompletionDate: string;
  status: string;
  reportOwner: string;
  lastUpdated: string;
  version: string;
}

interface TemplateInfo {
  filename: string;
  size: number;
  upload_date: string;
  template_type: string;
}

const REPORT_TYPES = [
  { key: 'executive', label: 'Executive Risk Report' },
  { key: 'operational', label: 'Operational Risk Report' },
  { key: 'quarterly', label: 'Quarterly Risk Report' },
  { key: 'annual', label: 'Annual Risk Report' },
  { key: 'compliance', label: 'Compliance Risk Report' },
  { key: 'incident', label: 'Incident Risk Report' },
  { key: 'trend', label: 'Risk Trend Report' },
  { key: 'dashboard', label: 'Risk Dashboard Report' },
];

const REPORTING_PERIODS = [
  { key: 'daily', label: 'Daily' },
  { key: 'weekly', label: 'Weekly' },
  { key: 'monthly', label: 'Monthly' },
  { key: 'quarterly', label: 'Quarterly' },
  { key: 'semi_annual', label: 'Semi-Annual' },
  { key: 'annual', label: 'Annual' },
  { key: 'ad_hoc', label: 'Ad Hoc' },
  { key: 'incident_based', label: 'Incident-Based' },
];

const RiskManagementReportPage: React.FC = () => {
  const navigate = useNavigate();
  const [projectName, setProjectName] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [reportType, setReportType] = useState('quarterly');
  const [reportingPeriod, setReportingPeriod] = useState('monthly');
  const [reportData, setReportData] = useState<{ [key: string]: RiskManagementReportRow[] }>({});
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
  const [templates, setTemplates] = useState<TemplateInfo[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateInfo | null>(null);
  const [showTemplateManager, setShowTemplateManager] = useState(false);
  const [isGeneratingWord, setIsGeneratingWord] = useState(false);
  const [wordReportInfo, setWordReportInfo] = useState<any>(null);

  const generateRiskManagementReport = async () => {
    console.log('generateRiskManagementReport called');
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
      
      const response = await api.generateRiskManagementReport({
        project_name: projectName || 'Default Project',
        report_type: reportType,
        reporting_period: reportingPeriod
      });
      
      console.log('Backend API response:', response);
      
      if (response.risk_management_report_data && response.risk_management_report_data.length > 0) {
        // Convert backend data to frontend format
        const convertedData = response.risk_management_report_data.map((item: any) => ({
          id: item.id || `RMR-${Date.now().toString().slice(-6)}`,
          reportSection: item.report_section || 'Default Section',
          sectionContent: item.section_content || 'Default content',
          riskMetrics: item.risk_metrics || 'Default metrics',
          riskTrends: item.risk_trends || 'Default trends',
          riskIncidents: item.risk_incidents || 'Default incidents',
          complianceStatus: item.compliance_status || 'Default compliance',
          actionItems: item.action_items || 'Default actions',
          responsibleParty: item.responsible_party || 'Default party',
          targetCompletionDate: item.target_completion_date || '2025-12-31',
          status: item.status || 'Draft',
          reportOwner: item.report_owner || 'Default Owner',
          lastUpdated: item.last_updated || new Date().toISOString(),
          version: item.version || '1.0'
        }));

        console.log('Converted risk management report data:', convertedData);
        
        setReportData({
          [reportType]: convertedData,
        });
        setMockFlag(response.mock);
        setShowTable(true);
        setIsGenerating(false);
      } else {
        console.log('No risk management report data in response, using mock data');
        // Fallback to mock data if API doesn't return data
        const mockData: RiskManagementReportRow[] = [
          {
            id: `RMR-${Date.now().toString().slice(-6)}`,
            reportSection: 'Executive Summary',
            sectionContent: 'Comprehensive overview of risk management performance, key achievements, and strategic objectives for the reporting period',
            riskMetrics: 'Risk reduction: 15%, Incident rate: 2.3 per month, Risk maturity level: 4.2/5.0',
            riskTrends: 'Decreasing trend in high-risk incidents, improving risk culture across organization',
            riskIncidents: '3 major incidents reported and resolved, 12 minor incidents managed proactively',
            complianceStatus: 'Fully compliant with ISO 31000, SOC 2 Type II certification maintained',
            actionItems: 'Implement enhanced monitoring system, conduct risk awareness training',
            responsibleParty: 'Risk Manager',
            targetCompletionDate: '2025-03-31',
            status: 'Complete',
            reportOwner: 'Chief Risk Officer',
            lastUpdated: new Date().toISOString(),
            version: '1.0'
          }
        ];

        setReportData({
          [reportType]: mockData,
        });
        setMockFlag(true);
        setShowTable(true);
        setIsGenerating(false);
      }
    } catch (error) {
      console.error('Error generating risk management report:', error);
      console.log('Using fallback mock data due to API error');
      
      // Fallback to mock data
      const mockData: RiskManagementReportRow[] = [
        {
          id: `RMR-${Date.now().toString().slice(-6)}`,
          reportSection: 'Executive Summary',
          sectionContent: 'Comprehensive overview of risk management performance, key achievements, and strategic objectives for the reporting period',
          riskMetrics: 'Risk reduction: 15%, Incident rate: 2.3 per month, Risk maturity level: 4.2/5.0',
          riskTrends: 'Decreasing trend in high-risk incidents, improving risk culture across organization',
          riskIncidents: '3 major incidents reported and resolved, 12 minor incidents managed proactively',
          complianceStatus: 'Fully compliant with ISO 31000, SOC 2 Type II certification maintained',
          actionItems: 'Implement enhanced monitoring system, conduct risk awareness training',
          responsibleParty: 'Risk Manager',
          targetCompletionDate: '2025-03-31',
          status: 'Complete',
          reportOwner: 'Chief Risk Officer',
          lastUpdated: new Date().toISOString(),
          version: '1.0'
        }
      ];

      setReportData({
        [reportType]: mockData,
      });
      setMockFlag(true);
      setShowTable(true);
      setIsGenerating(false);
    }
  };

  const handleSaveToProject = async () => {
    try {
      const api = window.fmeaApi;
      const currentData = reportData[reportType];
      
      if (currentData && currentData.length > 0) {
        // Save each risk management report row
        for (const row of currentData) {
          await api.saveRiskManagementReport({
            report_section: row.reportSection,
            section_content: row.sectionContent,
            risk_metrics: row.riskMetrics,
            risk_trends: row.riskTrends,
            risk_incidents: row.riskIncidents,
            compliance_status: row.complianceStatus,
            action_items: row.actionItems,
            responsible_party: row.responsibleParty,
            target_completion_date: row.targetCompletionDate,
            status: row.status,
            report_owner: row.reportOwner,
            last_updated: row.lastUpdated,
            version: row.version,
            project_id: 1 // Default project ID
          });
        }
        
        alert('Risk management report saved to project successfully!');
      }
    } catch (error) {
      console.error('Error saving to project:', error);
      alert('Failed to save to project. Please try again.');
    }
  };

  const handleExportData = () => {
    const currentData = reportData[reportType];
    if (currentData && currentData.length > 0) {
      exportRiskManagementReportData(currentData, `risk_management_report_${reportType}_${new Date().toISOString().split('T')[0]}`);
    }
  };

  const handleGenerateWordReport = async () => {
    if (!selectedTemplate) {
      alert('Please select a Word template first');
      return;
    }

    const currentData = reportData[reportType];
    if (!currentData || currentData.length === 0) {
      alert('Please generate a risk management report first');
      return;
    }

    setIsGeneratingWord(true);
    try {
      const api = window.fmeaApi;
      
      const response = await api.generateWordReport({
        project_name: projectName || 'Default Project',
        report_type: reportType,
        reporting_period: reportingPeriod,
        risk_management_report_data: currentData
      });

      setWordReportInfo(response);
      alert('Word report generated successfully! You can now download it.');
    } catch (error) {
      console.error('Error generating Word report:', error);
      alert('Failed to generate Word report. Please try again.');
    } finally {
      setIsGeneratingWord(false);
    }
  };

  const handleDownloadWordReport = async () => {
    if (!wordReportInfo) {
      alert('No Word report available for download');
      return;
    }

    try {
      const api = window.fmeaApi;
      await api.downloadWordReport(wordReportInfo.output_filename);
    } catch (error) {
      console.error('Error downloading Word report:', error);
      alert('Failed to download Word report. Please try again.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Risk Management Report</h1>
        <p className="text-gray-600">Generate comprehensive risk management reports using AI-powered analysis</p>
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
              Report Type
            </label>
            <select
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {REPORT_TYPES.map((type) => (
                <option key={type.key} value={type.key}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Reporting Period
            </label>
            <select
              value={reportingPeriod}
              onChange={(e) => setReportingPeriod(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {REPORTING_PERIODS.map((period) => (
                <option key={period.key} value={period.key}>
                  {period.label}
                </option>
              ))}
            </select>
          </div>
        </div>
        
        <button
          onClick={generateRiskManagementReport}
          disabled={isGenerating || !projectName.trim()}
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
              Generate Risk Management Report
            </>
          )}
        </button>
      </div>

      {/* Template Selection */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Word Template</h2>
          <button
            onClick={() => setShowTemplateManager(!showTemplateManager)}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            {showTemplateManager ? 'Hide Template Manager' : 'Manage Templates'}
          </button>
        </div>
        
        {selectedTemplate && (
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <i className="fa-solid fa-file-word text-blue-500 mr-2"></i>
                <span className="text-sm font-medium text-blue-900">
                  Selected Template: {selectedTemplate.filename}
                </span>
              </div>
              <button
                onClick={() => setSelectedTemplate(null)}
                className="text-blue-600 hover:text-blue-700 text-sm"
              >
                <i className="fa-solid fa-times mr-1"></i>
                Clear
              </button>
            </div>
          </div>
        )}
        
        {showTemplateManager && (
          <TemplateManager
            onTemplateSelect={(template) => {
              setSelectedTemplate(template);
              setShowTemplateManager(false);
            }}
            showUpload={true}
            showList={true}
            showActions={true}
          />
        )}
      </div>

      {/* Results Table */}
      {showTable && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Risk Management Report Results</h2>
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
                {selectedTemplate && (
                  <>
                    <button
                      onClick={handleGenerateWordReport}
                      disabled={isGeneratingWord}
                      className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isGeneratingWord ? (
                        <>
                          <i className="fa-solid fa-spinner fa-spin mr-2"></i>
                          Generating Word...
                        </>
                      ) : (
                        <>
                          <i className="fa-solid fa-file-word mr-2"></i>
                          Generate Word Report
                        </>
                      )}
                    </button>
                    {wordReportInfo && (
                      <button
                        onClick={handleDownloadWordReport}
                        className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                      >
                        <i className="fa-solid fa-download mr-2"></i>
                        Download Word Report
                      </button>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Report Section & Content</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk Metrics & Trends</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status & Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {reportData[reportType]?.map((row) => (
                  <tr key={row.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="space-y-2">
                        <div>
                          <span className="font-medium text-gray-900">Section:</span>
                          <span className="ml-2 text-gray-600">{row.reportSection}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-900">Content:</span>
                          <p className="text-sm text-gray-600">{row.sectionContent}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-900">Risk Incidents:</span>
                          <p className="text-sm text-gray-600">{row.riskIncidents}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-900">Compliance Status:</span>
                          <p className="text-sm text-gray-600">{row.complianceStatus}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="space-y-2 text-sm">
                        <div>
                          <span className="font-medium text-gray-700">Risk Metrics:</span>
                          <p className="text-gray-600">{row.riskMetrics}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Risk Trends:</span>
                          <p className="text-gray-600">{row.riskTrends}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Action Items:</span>
                          <p className="text-gray-600">{row.actionItems}</p>
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
                          <span className="font-medium text-gray-700">Report Owner:</span>
                          <span className="ml-2 text-gray-600">{row.reportOwner}</span>
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

export default RiskManagementReportPage;
