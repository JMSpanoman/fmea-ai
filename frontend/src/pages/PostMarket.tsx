import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useProject } from '../contexts/ProjectContext';

const PostMarket: React.FC = () => {
  const { currentProject } = useProject();
  const [deviceName, setDeviceName] = useState('CardioStent XR');
  const [deviceModel, setDeviceModel] = useState('CS-XR-2025');
  const [reportPeriodStart, setReportPeriodStart] = useState('2025-01-01');
  const [reportPeriodEnd, setReportPeriodEnd] = useState('2025-06-30');
  const [regions, setRegions] = useState('eu');
  const [riskAnalysis, setRiskAnalysis] = useState('Based on the data collected during this reporting period, the benefit-risk profile of CardioStent XR remains favorable. The observed adverse events are consistent with the known safety profile of the device and within expected rates for this class of medical devices. The CAPA related to packaging integrity is being addressed, with implementation expected in Q3 2025. No new safety signals were identified that would warrant additional risk mitigation measures at this time.');

  const handleGenerateReport = () => {
    // Handle report generation logic
    console.log('Generating report...');
  };

  const handleEditReport = () => {
    // Handle edit report logic
    console.log('Editing report...');
  };

  const handleExport = (format: string) => {
    // Handle export logic
    console.log(`Exporting to ${format}...`);
  };

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl text-neutral-800">
            Post Market Report Generator
          </h1>
          <p className="text-neutral-600 text-sm mt-1">
            Fill in minimal fields and let AI pull real-world data to pre-populate your PSUR.
          </p>
          {currentProject?.id ? (
            <p className="mt-3">
              <Link
                to={`/projects/${currentProject.id}/postmarket-report`}
                className="text-sky-700 text-sm font-medium hover:underline"
              >
                Open structured MAUDE evidence report (Smart Risk) →
              </Link>
            </p>
          ) : (
            <p className="mt-3 text-neutral-500 text-sm">
              Select a project from the sidebar, then use{' '}
              <span className="font-medium text-neutral-700">SmartQS Post Market → MAUDE evidence report</span> for the
              regulatory-style MAUDE summary.
            </p>
          )}
        </div>

        <div id="report-form" className="border border-neutral-200 rounded-md mb-6">
          <div className="bg-neutral-50 px-4 py-3 border-b border-neutral-200">
            <h2 className="text-lg text-neutral-800">Basic Information</h2>
          </div>
          <div className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm text-neutral-700 mb-1" htmlFor="device-name">
                  Medical Device Name*
                </label>
                <input 
                  id="device-name" 
                  className="w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-1 focus:ring-neutral-500" 
                  type="text" 
                  placeholder="e.g. CardioStent XR"
                  value={deviceName}
                  onChange={(e) => setDeviceName(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm text-neutral-700 mb-1" htmlFor="device-model">
                  Model/Reference Number
                </label>
                <input 
                  id="device-model" 
                  className="w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-1 focus:ring-neutral-500" 
                  type="text" 
                  placeholder="e.g. CS-XR-2025"
                  value={deviceModel}
                  onChange={(e) => setDeviceModel(e.target.value)}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div>
                <label className="block text-sm text-neutral-700 mb-1" htmlFor="report-start">
                  Report Period Start*
                </label>
                <input 
                  id="report-start" 
                  className="w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-1 focus:ring-neutral-500" 
                  type="date" 
                  value={reportPeriodStart}
                  onChange={(e) => setReportPeriodStart(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm text-neutral-700 mb-1" htmlFor="report-end">
                  Report Period End*
                </label>
                <input 
                  id="report-end" 
                  className="w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-1 focus:ring-neutral-500" 
                  type="date" 
                  value={reportPeriodEnd}
                  onChange={(e) => setReportPeriodEnd(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm text-neutral-700 mb-1" htmlFor="regions">
                  Regions*
                </label>
                <select 
                  id="regions" 
                  className="w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-1 focus:ring-neutral-500"
                  value={regions}
                  onChange={(e) => setRegions(e.target.value)}
                >
                  <option value="eu">European Union</option>
                  <option value="us">United States</option>
                  <option value="ca">Canada</option>
                  <option value="au">Australia</option>
                  <option value="jp">Japan</option>
                  <option value="global">Global</option>
                </select>
              </div>
            </div>

            <div className="mb-4">
              <label className="block text-sm text-neutral-700 mb-1" htmlFor="risk-analysis">
                Risk Analysis Summary
              </label>
              <textarea 
                id="risk-analysis" 
                className="w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-1 focus:ring-neutral-500" 
                rows={4}
                placeholder="Enter risk analysis summary or let AI generate one..."
                value={riskAnalysis}
                onChange={(e) => setRiskAnalysis(e.target.value)}
              />
            </div>

            <div className="flex space-x-3">
              <button 
                onClick={handleGenerateReport}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Generate Report
              </button>
              <button 
                onClick={handleEditReport}
                className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                Edit Report
              </button>
              <button 
                onClick={() => handleExport('pdf')}
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                Export PDF
              </button>
              <button 
                onClick={() => handleExport('word')}
                className="bg-purple-300 text-gray-900 px-4 py-2 rounded-md hover:bg-purple-400 focus:outline-none focus:ring-2 focus:ring-purple-300"
              >
                Export Word
              </button>
            </div>
          </div>
        </div>

        {/* Placeholder for generated report content */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Generated Report Preview</h3>
          <p className="text-gray-600">
            Report content will be generated here when you click "Generate Report".
          </p>
        </div>
      </div>
    </div>
  );
};

export default PostMarket;
