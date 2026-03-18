import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getProjects, Project } from '../services/apiService';
import authService from '../services/authService';
import Footer from './Footer';
import Sidebar from './Sidebar';

// NOTE: For icons, install FontAwesome React: npm install @fortawesome/react-fontawesome @fortawesome/free-solid-svg-icons @fortawesome/free-regular-svg-icons @fortawesome/free-brands-svg-icons

// For charts, install Highcharts and highcharts-react-official if you want interactive charts
// import HighchartsReact from 'highcharts-react-official';
// import Highcharts from 'highcharts';

const Dashboard: React.FC = () => {
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
    <div className="min-h-screen bg-gray-50">
      {/* Header / Top Navigation */}
      <header id="header" className="bg-white shadow-sm fixed top-0 left-0 right-0 z-50">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center">
            <div className="mr-2">
              <svg className="h-8 w-8" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="18" height="18" rx="4" fill="#0ea5e9" />
                <rect x="22" width="18" height="18" rx="4" fill="#8b5cf6" />
                <rect y="22" width="18" height="18" rx="4" fill="#10b981" />
                <rect x="22" y="22" width="18" height="18" rx="4" fill="#f59e0b" />
              </svg>
            </div>
            <span className="text-xl font-bold text-gray-800">Foton aiQMS Platform</span>
          </div>
          <div className="flex items-center">
            <div className="relative group">
              <button className="flex items-center space-x-2 text-gray-700 hover:text-gray-900">
                <img src="https://storage.googleapis.com/uxpilot-auth.appspot.com/avatars/avatar-3.jpg" alt="User" className="w-8 h-8 rounded-full border border-gray-200" />
                <span className="hidden md:block font-medium">John Spanomanolis</span>
                <i className="fa-solid fa-chevron-down text-xs"></i>
              </button>
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 hidden group-hover:block">
                <span className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer">Profile</span>
                <span className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer">Logout</span>
              </div>
            </div>
          </div>
        </div>
      </header>
      <div className="flex pt-20">
        <Sidebar />
        <div className="flex-1">
          {/* MAIN CONTENT */}
          <main id="main-content" className="pb-8">
            {/* Top Panel Widgets */}
            <section id="dashboard-widgets" className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
                {/* High-Risk Items Widget */}
                <div id="high-risk-widget" className="bg-white rounded-lg shadow p-4 border-l-4 border-red-500">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-sm font-semibold text-gray-500">HIGH-RISK ITEMS</h3>
                    <span className="text-red-500 text-xs font-medium px-2 py-0.5 bg-red-50 rounded-full">+3 new</span>
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
                <div id="capa-widget" className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-sm font-semibold text-gray-500">OPEN CAPAs</h3>
                    <span className="text-blue-500 text-xs font-medium px-2 py-0.5 bg-blue-50 rounded-full">4 due soon</span>
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
                <div id="nc-trends-widget" className="bg-white rounded-lg shadow p-4 border-l-4 border-yellow-500">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-sm font-semibold text-gray-500">NC TRENDS</h3>
                    <span className="text-yellow-500 text-xs font-medium px-2 py-0.5 bg-yellow-50 rounded-full">-12% month</span>
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
                <div id="ai-widget" className="bg-white rounded-lg shadow p-4 border-l-4 border-purple-300">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-sm font-semibold text-gray-500">AI RECOMMENDATIONS</h3>
                    <span className="text-purple-700 text-xs font-medium px-2 py-0.5 bg-purple-100 rounded-full">7 new</span>
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
                <div id="change-widget" className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-sm font-semibold text-gray-500">CHANGE CONTROL</h3>
                    <span className="text-green-500 text-xs font-medium px-2 py-0.5 bg-green-50 rounded-full">3 today</span>
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
                      <span className="text-yellow-600 font-medium">CC-2024-015</span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-600">Battery Life Sensor</span>
                      <span className="text-blue-600 font-medium">CC-2024-018</span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-600">Thermal Management</span>
                      <span className="text-green-600 font-medium">CC-2024-022</span>
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
                    <button className="px-3 py-1 text-sm bg-blue-500 text-white rounded-md">60d</button>
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
                              <div className="h-full bg-red-500 rounded-full" style={{width: '85%'}}></div>
                            </div>
                            <span className="text-xs font-medium text-red-600">85</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-600">Battery Life Sensor</span>
                          <div className="flex items-center space-x-2">
                            <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                              <div className="h-full bg-yellow-500 rounded-full" style={{width: '72%'}}></div>
                            </div>
                            <span className="text-xs font-medium text-yellow-600">72</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-600">Signal Processing Unit</span>
                          <div className="flex items-center space-x-2">
                            <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                              <div className="h-full bg-blue-500 rounded-full" style={{width: '64%'}}></div>
                            </div>
                            <span className="text-xs font-medium text-blue-600">64</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-600">Thermal Management</span>
                          <div className="flex items-center space-x-2">
                            <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                              <div className="h-full bg-green-500 rounded-full" style={{width: '48%'}}></div>
                            </div>
                            <span className="text-xs font-medium text-green-600">48</span>
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
                            <span className="text-xs font-medium text-red-600">RPN: 85</span>
                            <p className="text-xs text-gray-500">Linked to FM-002</p>
                          </div>
                        </div>
                        <div className="flex items-center justify-between p-2 bg-white rounded border">
                          <div>
                            <span className="text-xs font-medium text-gray-900">CAPA-2024-003</span>
                            <p className="text-xs text-gray-600">Battery life below specification</p>
                          </div>
                          <div className="text-right">
                            <span className="text-xs font-medium text-yellow-600">RPN: 72</span>
                            <p className="text-xs text-gray-500">Linked to FM-005</p>
                          </div>
                        </div>
                        <div className="flex items-center justify-between p-2 bg-white rounded border">
                          <div>
                            <span className="text-xs font-medium text-gray-900">CAPA-2024-007</span>
                            <p className="text-xs text-gray-600">Signal processing delay</p>
                          </div>
                          <div className="text-right">
                            <span className="text-xs font-medium text-blue-600">RPN: 64</span>
                            <p className="text-xs text-gray-500">Linked to FM-008</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Risk Trend Summary */}
                  <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-gradient-to-r from-red-50 to-red-100 p-3 rounded-lg">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-red-700">High Risk Items</span>
                        <span className="text-lg font-bold text-red-600">3</span>
                      </div>
                      <p className="text-xs text-red-600 mt-1">RPN &gt; 70</p>
                    </div>
                    <div className="bg-gradient-to-r from-yellow-50 to-yellow-100 p-3 rounded-lg">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-yellow-700">Medium Risk Items</span>
                        <span className="text-lg font-bold text-yellow-600">7</span>
                      </div>
                      <p className="text-xs text-yellow-600 mt-1">RPN 40-70</p>
                    </div>
                    <div className="bg-gradient-to-r from-green-50 to-green-100 p-3 rounded-lg">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-green-700">Low Risk Items</span>
                        <span className="text-lg font-bold text-green-600">12</span>
                      </div>
                      <p className="text-xs text-green-600 mt-1">RPN &lt; 40</p>
                    </div>
                  </div>
                  
                  {/* AI Risk Insights */}
                  <div className="mt-4 bg-purple-50 border border-purple-200 rounded-lg p-4">
                    <div className="flex items-start">
                      <div className="flex-shrink-0 bg-purple-200 rounded-full p-2 mr-3">
                        <i className="fa-solid fa-robot text-purple-700 text-sm"></i>
                      </div>
                      <div>
                        <h4 className="text-sm font-semibold text-purple-800 mb-2">AI Risk Analysis Insights</h4>
                        <div className="space-y-2 text-xs text-purple-800">
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
                  <i className="fa-solid fa-shield-halved text-2xl text-blue-600 mr-3"></i>
                  <h2 className="text-xl font-bold">FMEA Risk Matrix</h2>
                </div>
                <div className="flex space-x-3">
                  <button className="px-3 py-2 bg-white border border-gray-300 rounded-md text-sm flex items-center hover:bg-gray-50">
                    <i className="fa-solid fa-filter mr-2"></i>Filter
                  </button>
                  <button className="px-3 py-2 bg-white border border-gray-300 rounded-md text-sm flex items-center hover:bg-gray-50">
                    <i className="fa-solid fa-file-export mr-2"></i>Export
                  </button>
                  <button className="px-3 py-2 bg-blue-600 text-white rounded-md text-sm flex items-center hover:bg-blue-700">
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
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium"><span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full">24</span></td>
                        <td className="px-6 py-4 text-sm text-gray-500">Calibration routine, redundant sensors</td>
                        <td className="px-6 py-4 whitespace-nowrap"><span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Mitigated</span></td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <div className="flex space-x-2">
                            <button className="text-gray-500 hover:text-blue-600"><i className="fa-solid fa-pencil"></i></button>
                            <button className="text-gray-500 hover:text-blue-600"><i className="fa-solid fa-link"></i></button>
                            <button className="text-gray-500 hover:text-red-600"><i className="fa-solid fa-trash"></i></button>
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
                    <button className="px-3 py-1 bg-blue-50 border border-blue-500 rounded-md text-sm text-blue-600">1</button>
                    <button className="px-3 py-1 border border-gray-300 rounded-md text-sm text-gray-500 hover:bg-gray-50">2</button>
                    <button className="px-3 py-1 border border-gray-300 rounded-md text-sm text-gray-500 hover:bg-gray-50">3</button>
                    <button className="px-3 py-1 border border-gray-300 rounded-md text-sm text-gray-500 hover:bg-gray-50">Next</button>
                  </div>
                </div>
              </div>
            </section>
            
            {/* 5x5 Risk Matrix */}
            <section id="risk-matrix" className="px-6 mb-8">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <i className="fa-solid fa-table-cells text-2xl text-purple-700 mr-3"></i>
                  <h2 className="text-xl font-bold">5x5 Risk Matrix</h2>
                </div>
                <div className="flex space-x-3">
                  <button className="px-3 py-2 bg-white border border-gray-300 rounded-md text-sm flex items-center hover:bg-gray-50">
                    <i className="fa-solid fa-info-circle mr-2"></i>Legend
                  </button>
                  <button className="px-3 py-2 bg-white border border-gray-300 rounded-md text-sm flex items-center hover:bg-gray-50">
                    <i className="fa-solid fa-file-export mr-2"></i>Export
                  </button>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="grid grid-cols-7 gap-1 mb-4">
                  {/* Header row with Occurrence levels */}
                  <div className="text-center text-xs font-medium text-gray-500"></div>
                  <div className="text-center text-xs font-medium text-gray-500 bg-gray-100 p-2 rounded">1<br/>Very Low</div>
                  <div className="text-center text-xs font-medium text-gray-500 bg-gray-100 p-2 rounded">2<br/>Low</div>
                  <div className="text-center text-xs font-medium text-gray-500 bg-gray-100 p-2 rounded">3<br/>Medium</div>
                  <div className="text-center text-xs font-medium text-gray-500 bg-gray-100 p-2 rounded">4<br/>High</div>
                  <div className="text-center text-xs font-medium text-gray-500 bg-gray-100 p-2 rounded">5<br/>Very High</div>
                </div>
                
                {/* Risk Matrix Grid */}
                <div className="grid grid-cols-7 gap-1">
                  {/* Severity column labels */}
                  <div className="space-y-1">
                    <div className="text-xs font-medium text-gray-500 bg-gray-100 p-2 rounded text-center">5<br/>Very High</div>
                    <div className="text-xs font-medium text-gray-500 bg-gray-100 p-2 rounded text-center">4<br/>High</div>
                    <div className="text-xs font-medium text-gray-500 bg-gray-100 p-2 rounded text-center">3<br/>Medium</div>
                    <div className="text-xs font-medium text-gray-500 bg-gray-100 p-2 rounded text-center">2<br/>Low</div>
                    <div className="text-xs font-medium text-gray-500 bg-gray-100 p-2 rounded text-center">1<br/>Very Low</div>
                  </div>
                  
                  {/* Risk Matrix Cells */}
                  {/* Row 5 (Severity 5) */}
                  <div className="bg-red-600 text-white text-xs font-bold p-2 rounded text-center flex items-center justify-center">25<br/>Critical</div>
                  <div className="bg-red-500 text-white text-xs font-bold p-2 rounded text-center flex items-center justify-center">20<br/>Critical</div>
                  <div className="bg-red-400 text-white text-xs font-bold p-2 rounded text-center flex items-center justify-center">15<br/>High</div>
                  <div className="bg-orange-400 text-white text-xs font-bold p-2 rounded text-center flex items-center justify-center">12<br/>High</div>
                  <div className="bg-yellow-400 text-white text-xs font-bold p-2 rounded text-center flex items-center justify-center">10<br/>Medium</div>
                  
                  {/* Row 4 (Severity 4) */}
                  <div className="bg-red-500 text-white text-xs font-bold p-2 rounded text-center flex items-center justify-center">20<br/>Critical</div>
                  <div className="bg-red-400 text-white text-xs font-bold p-2 rounded text-center flex items-center justify-center">16<br/>High</div>
                  <div className="bg-orange-400 text-white text-xs font-bold p-2 rounded text-center flex items-center justify-center">12<br/>High</div>
                  <div className="bg-yellow-400 text-white text-xs font-bold p-2 rounded text-center flex items-center justify-center">8<br/>Medium</div>
                  <div className="bg-green-400 text-white text-xs font-bold p-2 rounded text-center flex items-center justify-center">4<br/>Low</div>
                  
                  {/* Row 3 (Severity 3) */}
                  <div className="bg-red-400 text-white text-xs font-bold p-2 rounded text-center flex items-center justify-center">15<br/>High</div>
                  <div className="bg-orange-400 text-white text-xs font-bold p-2 rounded text-center flex items-center justify-center">12<br/>High</div>
                  <div className="bg-yellow-400 text-white text-xs font-bold p-2 rounded text-center flex items-center justify-center">9<br/>Medium</div>
                  <div className="bg-green-400 text-white text-xs font-bold p-2 rounded text-center flex items-center justify-center">6<br/>Low</div>
                  <div className="bg-green-300 text-white text-xs font-bold p-2 rounded text-center flex items-center justify-center">3<br/>Low</div>
                  
                  {/* Row 2 (Severity 2) */}
                  <div className="bg-orange-400 text-white text-xs font-bold p-2 rounded text-center flex items-center justify-center">10<br/>Medium</div>
                  <div className="bg-yellow-400 text-white text-xs font-bold p-2 rounded text-center flex items-center justify-center">8<br/>Medium</div>
                  <div className="bg-green-400 text-white text-xs font-bold p-2 rounded text-center flex items-center justify-center">6<br/>Low</div>
                  <div className="bg-green-300 text-white text-xs font-bold p-2 rounded text-center flex items-center justify-center">4<br/>Low</div>
                  <div className="bg-green-200 text-green-800 text-xs font-bold p-2 rounded text-center flex items-center justify-center">2<br/>Very Low</div>
                  
                  {/* Row 1 (Severity 1) */}
                  <div className="bg-yellow-400 text-white text-xs font-bold p-2 rounded text-center flex items-center justify-center">5<br/>Medium</div>
                  <div className="bg-green-400 text-white text-xs font-bold p-2 rounded text-center flex items-center justify-center">4<br/>Low</div>
                  <div className="bg-green-300 text-white text-xs font-bold p-2 rounded text-center flex items-center justify-center">3<br/>Low</div>
                  <div className="bg-green-200 text-green-800 text-xs font-bold p-2 rounded text-center flex items-center justify-center">2<br/>Very Low</div>
                  <div className="bg-green-100 text-green-800 text-xs font-bold p-2 rounded text-center flex items-center justify-center">1<br/>Very Low</div>
                </div>
                
                {/* Risk Level Legend */}
                <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-4 h-4 bg-red-600 rounded"></div>
                    <div>
                      <span className="text-sm font-medium text-gray-900">Critical Risk</span>
                      <p className="text-xs text-gray-500">RPN 15-25</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-4 h-4 bg-orange-400 rounded"></div>
                    <div>
                      <span className="text-sm font-medium text-gray-900">High Risk</span>
                      <p className="text-xs text-gray-500">RPN 8-14</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-4 h-4 bg-yellow-400 rounded"></div>
                    <div>
                      <span className="text-sm font-medium text-gray-900">Medium Risk</span>
                      <p className="text-xs text-gray-500">RPN 4-7</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-4 h-4 bg-green-400 rounded"></div>
                    <div>
                      <span className="text-sm font-medium text-gray-900">Low Risk</span>
                      <p className="text-xs text-gray-500">RPN 1-3</p>
                    </div>
                  </div>
                </div>
                
                {/* Current Risk Distribution */}
                <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                  <h4 className="text-sm font-semibold text-gray-700 mb-3">Current Risk Distribution</h4>
                  <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-600">3</div>
                      <div className="text-xs text-gray-500">Critical</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-orange-600">7</div>
                      <div className="text-xs text-gray-500">High</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-yellow-600">12</div>
                      <div className="text-xs text-gray-500">Medium</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">18</div>
                      <div className="text-xs text-gray-500">Low</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-700">5</div>
                      <div className="text-xs text-gray-500">Very Low</div>
                    </div>
                  </div>
                </div>
              </div>
            </section>
            
            {/* Nonconformance Tracker Module */}
            <section id="nc-module" className="px-6 mb-8">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <i className="fa-solid fa-triangle-exclamation text-2xl text-yellow-600 mr-3"></i>
                  <h2 className="text-xl font-bold">Nonconformance (NC) Tracker</h2>
                </div>
                <div className="flex space-x-3">
                  <button className="px-3 py-2 bg-white border border-gray-300 rounded-md text-sm flex items-center hover:bg-gray-50">
                    <i className="fa-solid fa-filter mr-2"></i>Filter
                  </button>
                  <button className="px-3 py-2 bg-white border border-gray-300 rounded-md text-sm flex items-center hover:bg-gray-50">
                    <i className="fa-solid fa-file-export mr-2"></i>Export
                  </button>
                  <button className="px-3 py-2 bg-yellow-600 text-white rounded-md text-sm flex items-center hover:bg-yellow-700">
                    <i className="fa-solid fa-plus mr-2"></i>Report NC
                  </button>
                </div>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Open NCs */}
                <div className="bg-white rounded-lg shadow">
                  <div className="px-4 py-3 bg-gray-50 border-b border-gray-200 rounded-t-lg">
                    <h3 className="font-semibold text-gray-700 flex items-center">
                      <span className="inline-block w-3 h-3 bg-red-500 rounded-full mr-2"></span>Open (4)
                    </h3>
                  </div>
                  <div className="p-4">
                    <div className="space-y-4">
                      {/* Example NC card, repeat as needed */}
                      <div className="p-3 border border-gray-200 rounded-md hover:border-blue-500 cursor-pointer transition-colors">
                        <div className="flex justify-between items-start mb-2">
                          <span className="font-medium text-gray-900">NC-2023-042</span>
                          <span className="text-xs font-medium text-red-600 bg-red-50 px-2 py-0.5 rounded-full">High</span>
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
                      <span className="inline-block w-3 h-3 bg-yellow-500 rounded-full mr-2"></span>Under Review (3)
                    </h3>
                  </div>
                  <div className="p-4">
                    <div className="space-y-4">
                      {/* Example NC card, repeat as needed */}
                      <div className="p-3 border border-gray-200 rounded-md hover:border-blue-500 cursor-pointer transition-colors">
                        <div className="flex justify-between items-start mb-2">
                          <span className="font-medium text-gray-900">NC-2023-037</span>
                          <span className="text-xs font-medium text-red-600 bg-red-50 px-2 py-0.5 rounded-full">High</span>
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
                      <span className="inline-block w-3 h-3 bg-green-500 rounded-full mr-2"></span>Closed (5)
                    </h3>
                  </div>
                  <div className="p-4">
                    <div className="space-y-4">
                      {/* Example NC card, repeat as needed */}
                      <div className="p-3 border border-gray-200 rounded-md hover:border-blue-500 cursor-pointer transition-colors">
                        <div className="flex justify-between items-start mb-2">
                          <span className="font-medium text-gray-900">NC-2023-033</span>
                          <span className="text-xs font-medium text-yellow-600 bg-yellow-50 px-2 py-0.5 rounded-full">Medium</span>
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
                  <i className="fa-solid fa-arrows-rotate text-2xl text-green-600 mr-3"></i>
                  <h2 className="text-xl font-bold">Change Control Manager</h2>
                </div>
                <div className="flex space-x-3">
                  <button className="px-3 py-2 bg-white border border-gray-300 rounded-md text-sm flex items-center hover:bg-gray-50">
                    <i className="fa-solid fa-filter mr-2"></i>Filter
                  </button>
                  <button className="px-3 py-2 bg-white border border-gray-300 rounded-md text-sm flex items-center hover:bg-gray-50">
                    <i className="fa-solid fa-file-export mr-2"></i>Export
                  </button>
                  <button className="px-3 py-2 bg-green-600 text-white rounded-md text-sm flex items-center hover:bg-green-700">
                    <i className="fa-solid fa-plus mr-2"></i>New Change Request
                  </button>
                </div>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Pending Approval */}
                <div className="bg-white rounded-lg shadow">
                  <div className="px-4 py-3 bg-gray-50 border-b border-gray-200 rounded-t-lg">
                    <h3 className="font-semibold text-gray-700 flex items-center">
                      <span className="inline-block w-3 h-3 bg-yellow-500 rounded-full mr-2"></span>Pending Approval (3)
                    </h3>
                  </div>
                  <div className="p-4">
                    <div className="space-y-4">
                      <div className="p-3 border border-gray-200 rounded-md hover:border-green-500 cursor-pointer transition-colors">
                        <div className="flex justify-between items-start mb-2">
                          <span className="font-medium text-gray-900">CC-2024-015</span>
                          <span className="text-xs font-medium text-yellow-600 bg-yellow-50 px-2 py-0.5 rounded-full">High Priority</span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">Power Management IC thermal monitoring enhancement</p>
                        <div className="flex justify-between items-center text-xs text-gray-500">
                          <span>Submitted: Jan 15, 2024</span>
                          <span>Linked: CAPA-2024-001</span>
                        </div>
                      </div>
                      <div className="p-3 border border-gray-200 rounded-md hover:border-green-500 cursor-pointer transition-colors">
                        <div className="flex justify-between items-start mb-2">
                          <span className="font-medium text-gray-900">CC-2024-018</span>
                          <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">Medium Priority</span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">Battery life sensor calibration algorithm update</p>
                        <div className="flex justify-between items-center text-xs text-gray-500">
                          <span>Submitted: Jan 18, 2024</span>
                          <span>Linked: CAPA-2024-003</span>
                        </div>
                      </div>
                      <div className="p-3 border border-gray-200 rounded-md hover:border-green-500 cursor-pointer transition-colors">
                        <div className="flex justify-between items-start mb-2">
                          <span className="font-medium text-gray-900">CC-2024-022</span>
                          <span className="text-xs font-medium text-green-600 bg-green-50 px-2 py-0.5 rounded-full">Low Priority</span>
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
                      <span className="inline-block w-3 h-3 bg-blue-500 rounded-full mr-2"></span>Under Review (2)
                    </h3>
                  </div>
                  <div className="p-4">
                    <div className="space-y-4">
                      <div className="p-3 border border-gray-200 rounded-md hover:border-green-500 cursor-pointer transition-colors">
                        <div className="flex justify-between items-start mb-2">
                          <span className="font-medium text-gray-900">CC-2024-012</span>
                          <span className="text-xs font-medium text-red-600 bg-red-50 px-2 py-0.5 rounded-full">Critical</span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">Signal processing unit firmware update</p>
                        <div className="flex justify-between items-center text-xs text-gray-500">
                          <span>Review: Jan 20, 2024</span>
                          <span>Linked: CAPA-2024-007</span>
                        </div>
                      </div>
                      <div className="p-3 border border-gray-200 rounded-md hover:border-green-500 cursor-pointer transition-colors">
                        <div className="flex justify-between items-start mb-2">
                          <span className="font-medium text-gray-900">CC-2024-019</span>
                          <span className="text-xs font-medium text-yellow-600 bg-yellow-50 px-2 py-0.5 rounded-full">High Priority</span>
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
                      <span className="inline-block w-3 h-3 bg-green-500 rounded-full mr-2"></span>Approved (1)
                    </h3>
                  </div>
                  <div className="p-4">
                    <div className="space-y-4">
                      <div className="p-3 border border-gray-200 rounded-md hover:border-green-500 cursor-pointer transition-colors">
                        <div className="flex justify-between items-start mb-2">
                          <span className="font-medium text-gray-900">CC-2024-010</span>
                          <span className="text-xs font-medium text-green-600 bg-green-50 px-2 py-0.5 rounded-full">Completed</span>
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
      </div>
      {/* Footer */}
      <Footer />
    </div>
  );
};

export default Dashboard;
