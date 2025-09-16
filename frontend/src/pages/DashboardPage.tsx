import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getProjects, Project } from '../services/apiService';
import authService from '../services/authService';

// NOTE: For icons, install FontAwesome React: npm install @fortawesome/react-fontawesome @fortawesome/free-solid-svg-icons @fortawesome/free-regular-svg-icons @fortawesome/free-brands-svg-icons
// For charts, install Highcharts and highcharts-react-official if you want interactive charts
// import HighchartsReact from 'highcharts-react-official';
// import Highcharts from 'highcharts';

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedProjects, setExpandedProjects] = useState(false);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    initializeAuthAndFetchProjects();
  }, []);

  const initializeAuthAndFetchProjects = async () => {
    try {
      setLoading(true);
      console.log('DashboardPage: Starting authentication and projects fetch...');
      
      // First authenticate
      if (!authService.isAuthenticated()) {
        console.log('DashboardPage: Not authenticated, attempting to authenticate...');
        await authService.authenticate();
        setIsAuthenticated(true);
        console.log('DashboardPage: Authentication successful');
      } else {
        console.log('DashboardPage: Already authenticated');
        setIsAuthenticated(true);
      }
      
      // Then fetch projects
      console.log('DashboardPage: Fetching projects...');
      await fetchProjects();
    } catch (err) {
      console.error('DashboardPage: Failed to initialize:', err);
      setError('Failed to authenticate or load projects');
    } finally {
      setLoading(false);
    }
  };

  const fetchProjects = async () => {
    try {
      console.log('DashboardPage: Calling getProjects()...');
      const data = await getProjects();
      console.log('DashboardPage: Projects loaded successfully:', data);
      setProjects(data);
      setError(null);
    } catch (err) {
      console.error('DashboardPage: Error fetching projects:', err);
      setError('Failed to load projects');
    }
  };

  const handleProjectSelect = (project: Project) => {
    setSelectedProject(project);
    // You can add navigation logic here if needed
  };

  const toggleProjectsExpansion = () => {
    setExpandedProjects(!expandedProjects);
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-lg text-gray-600 mt-2">Overview of your quality management activities</p>
      </div>
      
      {/* MAIN CONTENT */}
      <main id="main-content" className="pb-8">
        {/* Top Panel Widgets */}
        <section id="dashboard-widgets" className="mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
            {/* High-Risk Items Widget */}
            <div id="high-risk-widget" className="bg-white rounded-lg shadow p-4 border-l-4 border-danger-500">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-sm font-semibold text-gray-500">HIGH-RISK ITEMS</h3>
                <span className="text-danger-500 text-xs font-medium px-2 py-0.5 bg-danger-50 rounded-full">+3 new</span>
              </div>
              <div className="flex items-end">
                <span className="text-3xl font-bold">12</span>
                <span className="text-sm text-gray-500 ml-2">RPN &gt; 100</span>
              </div>
              <div className="mt-3 text-xs text-gray-500">
                <span>Last updated: Today, 09:45 AM</span>
              </div>
            </div>
            {/* Open CAPAs Widget */}
            <div id="capa-widget" className="bg-white rounded-lg shadow p-4 border-l-4 border-primary-500">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-sm font-semibold text-gray-500">OPEN CAPAs</h3>
                <span className="text-primary-500 text-xs font-medium px-2 py-0.5 bg-primary-50 rounded-full">4 due soon</span>
              </div>
              <div className="flex items-end">
                <span className="text-3xl font-bold">8</span>
                <span className="text-sm text-gray-500 ml-2">by project</span>
              </div>
              <div className="mt-3 text-xs text-gray-500">
                <span>Last updated: Today, 10:15 AM</span>
              </div>
            </div>
            {/* NC Trends Widget */}
            <div id="nc-trends-widget" className="bg-white rounded-lg shadow p-4 border-l-4 border-warning-500">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-sm font-semibold text-gray-500">NC TRENDS</h3>
                <span className="text-warning-500 text-xs font-medium px-2 py-0.5 bg-warning-50 rounded-full">-12% month</span>
              </div>
              <div className="flex items-end">
                <span className="text-3xl font-bold">23</span>
                <span className="text-sm text-gray-500 ml-2">last 30 days</span>
              </div>
              <div className="mt-3 text-xs text-gray-500">
                <span>Last updated: Today, 08:30 AM</span>
              </div>
            </div>
            {/* AI Recommendations Widget */}
            <div id="ai-widget" className="bg-white rounded-lg shadow p-4 border-l-4 border-indigo-500">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-sm font-semibold text-gray-500">AI RECOMMENDATIONS</h3>
                <span className="text-indigo-500 text-xs font-medium px-2 py-0.5 bg-indigo-50 rounded-full">7 new</span>
              </div>
              <div className="flex items-end">
                <span className="text-3xl font-bold">15</span>
                <span className="text-sm text-gray-500 ml-2">need review</span>
              </div>
              <div className="mt-3 text-xs text-gray-500">
                <span>Last updated: Today, 11:20 AM</span>
              </div>
            </div>
            {/* Change Review Widget */}
            <div id="change-widget" className="bg-white rounded-lg shadow p-4 border-l-4 border-success-500">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-sm font-semibold text-gray-500">CHANGE CONTROL</h3>
                <span className="text-success-500 text-xs font-medium px-2 py-0.5 bg-success-50 rounded-full">3 today</span>
              </div>
              <div className="flex items-end">
                <span className="text-3xl font-bold">7</span>
                <span className="text-sm text-gray-500 ml-2">pending approval</span>
              </div>
              <div className="mt-3 text-xs text-gray-500">
                <span>Last updated: Today, 09:15 AM</span>
              </div>
              <div className="mt-2 space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-600">Power Management IC</span>
                  <span className="text-warning-600 font-medium">CC-2024-015</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-600">Battery Life Sensor</span>
                  <span className="text-primary-600 font-medium">CC-2024-018</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-600">Thermal Management</span>
                  <span className="text-success-600 font-medium">CC-2024-022</span>
                </div>
              </div>
            </div>
          </div>
          {/* Trends Chart */}
          <div id="trends-chart" className="bg-white rounded-lg shadow p-6 mb-8">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-semibold">Risk Trends</h2>
              <div className="flex space-x-2">
                <button className="px-3 py-1 text-sm bg-gray-100 rounded-md hover:bg-gray-200">30d</button>
                <button className="px-3 py-1 text-sm bg-primary-500 text-white rounded-md">60d</button>
                <button className="px-3 py-1 text-sm bg-gray-100 rounded-md hover:bg-gray-200">90d</button>
                <button className="px-3 py-1 text-sm bg-gray-100 rounded-md hover:bg-gray-200">All</button>
              </div>
            </div>
            <div id="trend-chart-container" className="h-[300px]">
              {/* Risk Trends Visualization */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
                {/* Risk Trend Chart */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-sm font-semibold text-gray-700 mb-4">Risk Priority Number (RPN) Trends</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">Power Management IC</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div className="h-full bg-danger-500 rounded-full" style={{width: '85%'}}></div>
                        </div>
                        <span className="text-xs font-medium text-danger-600">85</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">Battery Life Sensor</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div className="h-full bg-warning-500 rounded-full" style={{width: '72%'}}></div>
                        </div>
                        <span className="text-xs font-medium text-warning-600">72</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">Signal Processing Unit</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div className="h-full bg-primary-500 rounded-full" style={{width: '64%'}}></div>
                        </div>
                        <span className="text-xs font-medium text-primary-600">64</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">Thermal Management</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div className="h-full bg-success-500 rounded-full" style={{width: '48%'}}></div>
                        </div>
                        <span className="text-xs font-medium text-success-600">48</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* CAPA Correlation Chart */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-sm font-semibold text-gray-700 mb-4">CAPA-Risk Correlation</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-2 bg-white rounded border">
                      <div>
                        <span className="text-xs font-medium text-gray-900">CAPA-2024-001</span>
                        <p className="text-xs text-gray-600">Power supply voltage fluctuation</p>
                      </div>
                      <div className="text-right">
                        <span className="text-xs font-medium text-danger-600">RPN: 85</span>
                        <p className="text-xs text-gray-500">Linked to FM-002</p>
                      </div>
                    </div>
                    <div className="flex items-center justify-between p-2 bg-white rounded border">
                      <div>
                        <span className="text-xs font-medium text-gray-900">CAPA-2024-003</span>
                        <p className="text-xs text-gray-600">Battery life below specification</p>
                      </div>
                      <div className="text-right">
                        <span className="text-xs font-medium text-warning-600">RPN: 72</span>
                        <p className="text-xs text-gray-500">Linked to FM-005</p>
                      </div>
                    </div>
                    <div className="flex items-center justify-between p-2 bg-white rounded border">
                      <div>
                        <span className="text-xs font-medium text-gray-900">CAPA-2024-007</span>
                        <p className="text-xs text-gray-600">Signal processing delay</p>
                      </div>
                      <div className="text-right">
                        <span className="text-xs font-medium text-primary-600">RPN: 64</span>
                        <p className="text-xs text-gray-500">Linked to FM-008</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Risk Trend Summary */}
              <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gradient-to-r from-danger-50 to-danger-100 p-3 rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-danger-700">High Risk Items</span>
                    <span className="text-lg font-bold text-danger-600">3</span>
                  </div>
                  <p className="text-xs text-danger-600 mt-1">RPN &gt; 70</p>
                </div>
                <div className="bg-gradient-to-r from-warning-50 to-warning-100 p-3 rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-warning-700">Medium Risk Items</span>
                    <span className="text-lg font-bold text-warning-600">7</span>
                  </div>
                  <p className="text-xs text-warning-600 mt-1">RPN 40-70</p>
                </div>
                <div className="bg-gradient-to-r from-success-50 to-success-100 p-3 rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-success-700">Low Risk Items</span>
                    <span className="text-lg font-bold text-success-600">12</span>
                  </div>
                  <p className="text-xs text-success-600 mt-1">RPN &lt; 40</p>
                </div>
              </div>
              
              {/* AI Risk Insights */}
              <div className="mt-4 bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                <div className="flex items-start">
                  <div className="flex-shrink-0 bg-indigo-100 rounded-full p-2 mr-3">
                    <i className="fa-solid fa-robot text-indigo-600 text-sm"></i>
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-indigo-900 mb-2">AI Risk Analysis Insights</h4>
                    <div className="space-y-2 text-xs text-indigo-800">
                      <p><strong>Trend:</strong> Power management risks increased 23% this quarter, correlating with 3 new CAPA reports.</p>
                      <p><strong>Recommendation:</strong> Implement enhanced thermal monitoring for Power Management IC (FM-002).</p>
                      <p><strong>Prediction:</strong> Battery life sensor failures expected to decrease 15% after current mitigation implementation.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
        {/* FMEA Risk Matrix Module */}
        <section id="fmea-module" className="px-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <i className="fa-solid fa-shield-halved text-2xl text-primary-600 mr-3"></i>
              <h2 className="text-xl font-bold">FMEA Risk Matrix</h2>
            </div>
            <div className="flex space-x-3">
              <button className="px-3 py-2 bg-white border border-gray-300 rounded-md text-sm flex items-center hover:bg-gray-50">
                <i className="fa-solid fa-filter mr-2"></i>Filter
              </button>
              <button className="px-3 py-2 bg-white border border-gray-300 rounded-md text-sm flex items-center hover:bg-gray-50">
                <i className="fa-solid fa-file-export mr-2"></i>Export
              </button>
              <button className="px-3 py-2 bg-primary-600 text-white rounded-md text-sm flex items-center hover:bg-primary-700">
                <i className="fa-solid fa-plus mr-2"></i>Add Entry
              </button>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Component</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Failure Mode</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Effect</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">S</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">O</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">D</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RPN</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mitigation</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {/* Example rows, repeat or map from data as needed */}
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">FM-001</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Sensor Assembly</td>
                    <td className="px-6 py-4 text-sm text-gray-500">Signal drift over time</td>
                    <td className="px-6 py-4 text-sm text-gray-500">Incorrect readings leading to misdiagnosis</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500"><input type="number" value={4} min={1} max={5} className="w-12 border border-gray-300 rounded p-1 text-center" readOnly /></td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500"><input type="number" value={3} min={1} max={5} className="w-12 border border-gray-300 rounded p-1 text-center" readOnly /></td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500"><input type="number" value={2} min={1} max={5} className="w-12 border border-gray-300 rounded p-1 text-center" readOnly /></td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium"><span className="bg-warning-100 text-warning-800 px-2 py-1 rounded-full">24</span></td>
                    <td className="px-6 py-4 text-sm text-gray-500">Calibration routine, redundant sensors</td>
                    <td className="px-6 py-4 whitespace-nowrap"><span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Mitigated</span></td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex space-x-2">
                        <button className="text-gray-500 hover:text-primary-600"><i className="fa-solid fa-pencil"></i></button>
                        <button className="text-gray-500 hover:text-primary-600"><i className="fa-solid fa-link"></i></button>
                        <button className="text-gray-500 hover:text-danger-600"><i className="fa-solid fa-trash"></i></button>
                      </div>
                    </td>
                  </tr>
                  {/* ...more rows */}
                </tbody>
              </table>
            </div>
            <div className="px-6 py-3 flex items-center justify-between border-t border-gray-200">
              <div className="flex items-center">
                <span className="text-sm text-gray-700">
                  Showing <span className="font-medium">1</span> to <span className="font-medium">3</span> of <span className="font-medium">45</span> entries
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <button className="px-3 py-1 border border-gray-300 rounded-md text-sm text-gray-500 hover:bg-gray-50 disabled:opacity-50" disabled>Previous</button>
                <button className="px-3 py-1 bg-primary-50 border border-primary-500 rounded-md text-sm text-primary-600">1</button>
                <button className="px-3 py-1 border border-gray-300 rounded-md text-sm text-gray-500 hover:bg-gray-50">2</button>
                <button className="px-3 py-1 border border-gray-300 rounded-md text-sm text-gray-500 hover:bg-gray-50">3</button>
                <button className="px-3 py-1 border border-gray-300 rounded-md text-sm text-gray-500 hover:bg-gray-50">Next</button>
              </div>
            </div>
          </div>
        </section>
        {/* Nonconformance Tracker Module */}
        <section id="nc-module" className="px-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <i className="fa-solid fa-triangle-exclamation text-2xl text-warning-600 mr-3"></i>
              <h2 className="text-xl font-bold">Nonconformance (NC) Tracker</h2>
            </div>
            <div className="flex space-x-3">
              <button className="px-3 py-2 bg-white border border-gray-300 rounded-md text-sm flex items-center hover:bg-gray-50">
                <i className="fa-solid fa-filter mr-2"></i>Filter
              </button>
              <button className="px-3 py-2 bg-white border border-gray-300 rounded-md text-sm flex items-center hover:bg-gray-50">
                <i className="fa-solid fa-file-export mr-2"></i>Export
              </button>
              <button className="px-3 py-2 bg-warning-600 text-white rounded-md text-sm flex items-center hover:bg-warning-700">
                <i className="fa-solid fa-plus mr-2"></i>Report NC
              </button>
            </div>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Open NCs */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-4 py-3 bg-gray-50 border-b border-gray-200 rounded-t-lg">
                <h3 className="font-semibold text-gray-700 flex items-center">
                  <span className="inline-block w-3 h-3 bg-danger-500 rounded-full mr-2"></span>Open (4)
                </h3>
              </div>
              <div className="p-4">
                <div className="space-y-4">
                  {/* Example NC card, repeat as needed */}
                  <div className="p-3 border border-gray-200 rounded-md hover:border-primary-500 cursor-pointer transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-medium text-gray-900">NC-2023-042</span>
                      <span className="text-xs font-medium text-danger-600 bg-danger-50 px-2 py-0.5 rounded-full">High</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">Sensor calibration out of specification</p>
                    <div className="flex justify-between items-center text-xs text-gray-500">
                      <span>Reported: Jul 18, 2023</span>
                      <span>Linked: FM-002</span>
                    </div>
                  </div>
                  {/* ...more NC cards */}
                </div>
              </div>
            </div>
            {/* Under Review NCs */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-4 py-3 bg-gray-50 border-b border-gray-200 rounded-t-lg">
                <h3 className="font-semibold text-gray-700 flex items-center">
                  <span className="inline-block w-3 h-3 bg-warning-500 rounded-full mr-2"></span>Under Review (3)
                </h3>
              </div>
              <div className="p-4">
                <div className="space-y-4">
                  {/* Example NC card, repeat as needed */}
                  <div className="p-3 border border-gray-200 rounded-md hover:border-primary-500 cursor-pointer transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-medium text-gray-900">NC-2023-037</span>
                      <span className="text-xs font-medium text-danger-600 bg-danger-50 px-2 py-0.5 rounded-full">High</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">Unexpected device shutdown</p>
                    <div className="flex justify-between items-center text-xs text-gray-500">
                      <span>Reported: Jul 8, 2023</span>
                      <span>Linked: FM-002</span>
                    </div>
                  </div>
                  {/* ...more NC cards */}
                </div>
              </div>
            </div>
            {/* Closed NCs */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-4 py-3 bg-gray-50 border-b border-gray-200 rounded-t-lg">
                <h3 className="font-semibold text-gray-700 flex items-center">
                  <span className="inline-block w-3 h-3 bg-success-500 rounded-full mr-2"></span>Closed (5)
                </h3>
              </div>
              <div className="p-4">
                <div className="space-y-4">
                  {/* Example NC card, repeat as needed */}
                  <div className="p-3 border border-gray-200 rounded-md hover:border-primary-500 cursor-pointer transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-medium text-gray-900">NC-2023-033</span>
                      <span className="text-xs font-medium text-warning-600 bg-warning-50 px-2 py-0.5 rounded-full">Medium</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">Error in data export function</p>
                    <div className="flex justify-between items-center text-xs text-gray-500">
                      <span>Closed: Jul 17, 2023</span>
                      <span>Linked: FM-003</span>
                    </div>
                  </div>
                  {/* ...more NC cards */}
                </div>
              </div>
            </div>
          </div>
        </section>
        
        {/* Change Control Module */}
        <section id="change-control-module" className="px-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <i className="fa-solid fa-arrows-rotate text-2xl text-success-600 mr-3"></i>
              <h2 className="text-xl font-bold">Change Control Manager</h2>
            </div>
            <div className="flex space-x-3">
              <button className="px-3 py-2 bg-white border border-gray-300 rounded-md text-sm flex items-center hover:bg-gray-50">
                <i className="fa-solid fa-filter mr-2"></i>Filter
              </button>
              <button className="px-3 py-2 bg-white border border-gray-300 rounded-md text-sm flex items-center hover:bg-gray-50">
                <i className="fa-solid fa-file-export mr-2"></i>Export
              </button>
              <button className="px-3 py-2 bg-success-600 text-white rounded-md text-sm flex items-center hover:bg-success-700">
                <i className="fa-solid fa-plus mr-2"></i>New Change Request
              </button>
            </div>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Pending Approval */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-4 py-3 bg-gray-50 border-b border-gray-200 rounded-t-lg">
                <h3 className="font-semibold text-gray-700 flex items-center">
                  <span className="inline-block w-3 h-3 bg-warning-500 rounded-full mr-2"></span>Pending Approval (3)
                </h3>
              </div>
              <div className="p-4">
                <div className="space-y-4">
                  <div className="p-3 border border-gray-200 rounded-md hover:border-success-500 cursor-pointer transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-medium text-gray-900">CC-2024-015</span>
                      <span className="text-xs font-medium text-warning-600 bg-warning-50 px-2 py-0.5 rounded-full">High Priority</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">Power Management IC thermal monitoring enhancement</p>
                    <div className="flex justify-between items-center text-xs text-gray-500">
                      <span>Submitted: Jan 15, 2024</span>
                      <span>Linked: CAPA-2024-001</span>
                    </div>
                  </div>
                  <div className="p-3 border border-gray-200 rounded-md hover:border-success-500 cursor-pointer transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-medium text-gray-900">CC-2024-018</span>
                      <span className="text-xs font-medium text-primary-600 bg-primary-50 px-2 py-0.5 rounded-full">Medium Priority</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">Battery life sensor calibration algorithm update</p>
                    <div className="flex justify-between items-center text-xs text-gray-500">
                      <span>Submitted: Jan 18, 2024</span>
                      <span>Linked: CAPA-2024-003</span>
                    </div>
                  </div>
                  <div className="p-3 border border-gray-200 rounded-md hover:border-success-500 cursor-pointer transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-medium text-gray-900">CC-2024-022</span>
                      <span className="text-xs font-medium text-success-600 bg-success-50 px-2 py-0.5 rounded-full">Low Priority</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">Thermal management system optimization</p>
                    <div className="flex justify-between items-center text-xs text-gray-500">
                      <span>Submitted: Jan 22, 2024</span>
                      <span>Linked: FM-008</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Under Review */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-4 py-3 bg-gray-50 border-b border-gray-200 rounded-t-lg">
                <h3 className="font-semibold text-gray-700 flex items-center">
                  <span className="inline-block w-3 h-3 bg-primary-500 rounded-full mr-2"></span>Under Review (2)
                </h3>
              </div>
              <div className="p-4">
                <div className="space-y-4">
                  <div className="p-3 border border-gray-200 rounded-md hover:border-success-500 cursor-pointer transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-medium text-gray-900">CC-2024-012</span>
                      <span className="text-xs font-medium text-danger-600 bg-danger-50 px-2 py-0.5 rounded-full">Critical</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">Signal processing unit firmware update</p>
                    <div className="flex justify-between items-center text-xs text-gray-500">
                      <span>Review: Jan 20, 2024</span>
                      <span>Linked: CAPA-2024-007</span>
                    </div>
                  </div>
                  <div className="p-3 border border-gray-200 rounded-md hover:border-success-500 cursor-pointer transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-medium text-gray-900">CC-2024-019</span>
                      <span className="text-xs font-medium text-warning-600 bg-warning-50 px-2 py-0.5 rounded-full">High Priority</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">Battery management system redesign</p>
                    <div className="flex justify-between items-center text-xs text-gray-500">
                      <span>Review: Jan 25, 2024</span>
                      <span>Linked: FM-005</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Approved */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-4 py-3 bg-gray-50 border-b border-gray-200 rounded-t-lg">
                <h3 className="font-semibold text-gray-700 flex items-center">
                  <span className="inline-block w-3 h-3 bg-success-500 rounded-full mr-2"></span>Approved (1)
                </h3>
              </div>
              <div className="p-4">
                <div className="space-y-4">
                  <div className="p-3 border border-gray-200 rounded-md hover:border-success-500 cursor-pointer transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-medium text-gray-900">CC-2024-010</span>
                      <span className="text-xs font-medium text-success-600 bg-success-50 px-2 py-0.5 rounded-full">Completed</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">User interface improvements</p>
                    <div className="flex justify-between items-center text-xs text-gray-500">
                      <span>Approved: Jan 10, 2024</span>
                      <span>Linked: FM-001</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default DashboardPage; 