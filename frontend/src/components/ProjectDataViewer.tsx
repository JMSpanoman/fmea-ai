import React, { useState, useEffect } from 'react';
import { exportFmeaData, exportCapaData, exportNonConformanceData, exportChangeControlData } from '../utils/exportUtils';

interface ProjectDataViewerProps {
  selectedProject: any;
  onClose: () => void;
}

interface FmeaData {
  id: number;
  component: string;
  potential_failure_mode: string;
  potential_effects: string;
  potential_causes: string;
  severity: number;
  occurrence: number;
  detection: number;
  risk_priority_number: number;
  recommended_actions: string;
  actions_taken: string;
  final_severity: number;
  final_occurrence: number;
  final_detection: number;
  final_risk_priority_number: number;
  created_at: string;
}

interface CapaData {
  id: number;
  issue_description: string;
  root_cause: string;
  corrective_action: string;
  preventive_action: string;
  action_owner: string;
  due_date: string;
  status: string;
  effectiveness_check: string;
  created_at: string;
}

interface NonConformanceData {
  id: number;
  issue_description: string;
  source: string;
  detection_date: string;
  severity: string;
  root_cause: string;
  corrective_action: string;
  preventive_action: string;
  action_owner: string;
  due_date: string;
  status: string;
  created_at: string;
}

interface ChangeControlData {
  id: number;
  change_description: string;
  change_type: string;
  requestor: string;
  request_date: string;
  priority: string;
  impact_level: string;
  affected_components: string;
  justification: string;
  proposed_solution: string;
  risk_assessment: string;
  approval_status: string;
  approved_by: string;
  approval_date: string;
  implementation_plan: string;
  verification_plan: string;
  linked_fmea: string;
  linked_capa: string;
  linked_non_conformance: string;
  regulatory_impact: string;
  closure_summary: string;
  created_at: string;
}

const ProjectDataViewer: React.FC<ProjectDataViewerProps> = ({ selectedProject, onClose }) => {
  const [activeTab, setActiveTab] = useState('fmea');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [fmeaData, setFmeaData] = useState<FmeaData[]>([]);
  const [capaData, setCapaData] = useState<CapaData[]>([]);
  const [nonConformanceData, setNonConformanceData] = useState<NonConformanceData[]>([]);
  const [changeControlData, setChangeControlData] = useState<ChangeControlData[]>([]);

  useEffect(() => {
    if (selectedProject?.id) {
      loadProjectData();
    }
  }, [selectedProject?.id]);

  const loadProjectData = async () => {
    setLoading(true);
    setError(null);
    
    console.log('=== PROJECT DATA VIEWER: Loading data for project ===');
    console.log('Project ID:', selectedProject?.id);
    
    try {
      const api = window.fmeaApi;
      
      // Ensure we have a valid token before loading data
      console.log('Ensuring valid token...');
      await api.ensureValidToken();
      console.log('Token validated successfully');
      
      // Load FMEA data
      try {
        console.log('Loading FMEA data...');
        const fmeaResponse = await api.getFMEAs(selectedProject.id);
        console.log('FMEA response:', fmeaResponse);
        setFmeaData(Array.isArray(fmeaResponse) ? fmeaResponse : []);
        console.log('FMEA data loaded:', fmeaData.length, 'items');
      } catch (e) {
        console.log('No FMEA data found for this project:', e);
        setFmeaData([]);
      }

      // Load CAPA data
      try {
        console.log('Loading CAPA data...');
        const capaResponse = await api.getCapasFromProject(selectedProject.id);
        console.log('CAPA response:', capaResponse);
        setCapaData(Array.isArray(capaResponse) ? capaResponse : []);
        console.log('CAPA data loaded:', capaData.length, 'items');
      } catch (e) {
        console.log('No CAPA data found for this project:', e);
        setCapaData([]);
      }

      // Load Non-Conformance data
      try {
        console.log('Loading Non-Conformance data...');
        const nonConformanceResponse = await api.getNonConformancesFromProject(selectedProject.id);
        console.log('Non-Conformance response:', nonConformanceResponse);
        setNonConformanceData(Array.isArray(nonConformanceResponse) ? nonConformanceResponse : []);
        console.log('Non-Conformance data loaded:', nonConformanceData.length, 'items');
      } catch (e) {
        console.log('No Non-Conformance data found for this project:', e);
        setNonConformanceData([]);
      }

      // Load Change Control data
      try {
        console.log('Loading Change Control data...');
        const changeControlResponse = await api.getChangeControlsFromProject(selectedProject.id);
        console.log('Change Control response:', changeControlResponse);
        setChangeControlData(Array.isArray(changeControlResponse) ? changeControlResponse : []);
        console.log('Change Control data loaded:', changeControlData.length, 'items');
      } catch (e) {
        console.log('No Change Control data found for this project:', e);
        setChangeControlData([]);
      }

    } catch (err) {
      console.error('Error loading project data:', err);
      setError('Failed to load project data');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: number) => {
    if (severity >= 8) return 'bg-red-100 text-red-800';
    if (severity >= 6) return 'bg-orange-100 text-orange-800';
    if (severity >= 4) return 'bg-yellow-100 text-yellow-800';
    return 'bg-green-100 text-green-800';
  };

  const getStatusColor = (status: string) => {
    if (!status) return 'bg-gray-100 text-gray-800';
    
    switch (status.toLowerCase()) {
      case 'open': return 'bg-red-100 text-red-800';
      case 'in progress': return 'bg-yellow-100 text-yellow-800';
      case 'closed': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRpnColor = (rpn: number) => {
    if (rpn >= 100) return 'bg-orange-100 text-orange-800';
    if (rpn >= 50) return 'bg-yellow-100 text-yellow-800';
    return 'bg-green-100 text-green-800';
  };

  const tabs = [
    { id: 'fmea', label: 'FMEA', count: fmeaData.length },
    { id: 'capa', label: 'CAPA', count: capaData.length },
    { id: 'nonconformance', label: 'Non-Conformance', count: nonConformanceData.length },
    { id: 'changecontrol', label: 'Change Control', count: changeControlData.length },
  ];

  const renderFmeaTable = () => (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Component</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Failure Mode</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Effect</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Occurrence</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Detection</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RPN</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mitigation</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action Taken</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Post-Mitigation Severity</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Post-Mitigation Probability</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Post-Mitigation Detection</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Post-Mitigation RPN</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {fmeaData.map((item) => (
            <tr key={item.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.component}</td>
              <td className="px-6 py-4 text-sm text-gray-900">{item.potential_failure_mode}</td>
              <td className="px-6 py-4 text-sm text-gray-900">{item.potential_effects}</td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getSeverityColor(item.severity)}`}>
                  {item.severity}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.occurrence}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.detection}</td>
              <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getRpnColor(item.risk_priority_number)}`}>
                {item.risk_priority_number}
              </td>
              <td className="px-6 py-4 text-sm text-gray-900">{item.recommended_actions}</td>
              <td className="px-6 py-4 text-sm text-gray-900">{item.actions_taken || 'N/A'}</td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getSeverityColor(item.final_severity || 0)}`}>
                  {item.final_severity || 'N/A'}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.final_occurrence || 'N/A'}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.final_detection || 'N/A'}</td>
              <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getRpnColor(item.final_risk_priority_number || 0)}`}>
                {item.final_risk_priority_number || 'N/A'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      
      {/* FMEA Statistics */}
      <div className="bg-gray-50 px-6 py-4 border-t border-gray-200">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="font-medium text-gray-700">Total Entries:</span>
            <span className="ml-2 text-gray-900">{fmeaData.length}</span>
          </div>
          <div>
            <span className="font-medium text-gray-700">High Severity (8-10):</span>
            <span className="ml-2 text-red-600 font-medium">{fmeaData.filter(item => item.severity >= 8).length}</span>
          </div>
          <div>
            <span className="font-medium text-gray-700">High RPN (≥100):</span>
            <span className="ml-2 text-orange-600 font-medium">{fmeaData.filter(item => item.risk_priority_number >= 100).length}</span>
          </div>
          <div>
            <span className="font-medium text-gray-700">Avg RPN:</span>
            <span className="ml-2 text-gray-900">
              {fmeaData.length > 0 ? Math.round(fmeaData.reduce((sum, item) => sum + item.risk_priority_number, 0) / fmeaData.length) : 0}
            </span>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCapaTable = () => (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Issue</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Root Cause</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Corrective Action</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Owner</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Due Date</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {capaData.map((item) => (
            <tr key={item.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 text-sm text-gray-900">{item.issue_description}</td>
              <td className="px-6 py-4 text-sm text-gray-900">{item.root_cause}</td>
              <td className="px-6 py-4 text-sm text-gray-900">{item.corrective_action}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.action_owner}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.due_date}</td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(item.status)}`}>
                  {item.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      
      {/* CAPA Statistics */}
      <div className="bg-gray-50 px-6 py-4 border-t border-gray-200">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="font-medium text-gray-700">Total CAPAs:</span>
            <span className="ml-2 text-gray-900">{capaData.length}</span>
          </div>
          <div>
            <span className="font-medium text-gray-700">Open Status:</span>
            <span className="ml-2 text-red-600 font-medium">
              {capaData.filter(item => item.status?.toLowerCase() === 'open').length}
            </span>
          </div>
          <div>
            <span className="font-medium text-gray-700">In Progress:</span>
            <span className="ml-2 text-yellow-600 font-medium">
              {capaData.filter(item => item.status?.toLowerCase() === 'in progress').length}
            </span>
          </div>
          <div>
            <span className="font-medium text-gray-700">Closed:</span>
            <span className="ml-2 text-green-600 font-medium">
              {capaData.filter(item => item.status?.toLowerCase() === 'closed').length}
            </span>
          </div>
        </div>
      </div>
    </div>
  );

  const renderNonConformanceTable = () => (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Issue</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Source</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Root Cause</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Owner</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {nonConformanceData.map((item) => (
            <tr key={item.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 text-sm text-gray-900">{item.issue_description}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.source}</td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(item.severity)}`}>
                  {item.severity}
                </span>
              </td>
              <td className="px-6 py-4 text-sm text-gray-900">{item.root_cause}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.action_owner}</td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(item.status)}`}>
                  {item.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      
      {/* Non-Conformance Statistics */}
      <div className="bg-gray-50 px-6 py-4 border-t border-gray-200">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="font-medium text-gray-700">Total NCs:</span>
            <span className="ml-2 text-gray-900">{nonConformanceData.length}</span>
          </div>
          <div>
            <span className="font-medium text-gray-700">High Severity:</span>
            <span className="ml-2 text-red-600 font-medium">
              {nonConformanceData.filter(item => item.severity?.toLowerCase() === 'high').length}
            </span>
          </div>
          <div>
            <span className="font-medium text-gray-700">Open Status:</span>
            <span className="ml-2 text-orange-600 font-medium">
              {nonConformanceData.filter(item => item.status?.toLowerCase() === 'open').length}
            </span>
          </div>
          <div>
            <span className="font-medium text-gray-700">Resolved:</span>
            <span className="ml-2 text-green-600 font-medium">
              {nonConformanceData.filter(item => item.status?.toLowerCase() === 'closed' || item.status?.toLowerCase() === 'resolved').length}
            </span>
          </div>
        </div>
      </div>
    </div>
  );

  const renderChangeControlTable = () => (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Change Description</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Priority</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Impact</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Owner</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {changeControlData.map((item) => (
            <tr key={item.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 text-sm text-gray-900">{item.change_description}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.change_type}</td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(item.priority)}`}>
                  {item.priority}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(item.impact_level)}`}>
                  {item.impact_level}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(item.approval_status)}`}>
                  {item.approval_status}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.approved_by}</td>
            </tr>
          ))}
        </tbody>
      </table>
      
      {/* Change Control Statistics */}
      <div className="bg-gray-50 px-6 py-4 border-t border-gray-200">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="font-medium text-gray-700">Total Changes:</span>
            <span className="ml-2 text-gray-900">{changeControlData.length}</span>
          </div>
          <div>
            <span className="font-medium text-gray-700">High Priority:</span>
            <span className="ml-2 text-red-600 font-medium">
              {changeControlData.filter(item => item.priority?.toLowerCase() === 'high').length}
            </span>
          </div>
          <div>
            <span className="font-medium text-gray-700">Pending Approval:</span>
            <span className="ml-2 text-yellow-600 font-medium">
              {changeControlData.filter(item => item.approval_status?.toLowerCase() === 'pending').length}
            </span>
          </div>
          <div>
            <span className="font-medium text-gray-700">Approved:</span>
            <span className="ml-2 text-green-600 font-medium">
              {changeControlData.filter(item => item.approval_status?.toLowerCase() === 'approved').length}
            </span>
          </div>
        </div>
      </div>
    </div>
  );

  const renderEmptyState = (type: string) => (
    <div className="text-center py-12">
      <div className="text-gray-400 mb-4">
        <i className="fas fa-inbox text-4xl"></i>
      </div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">No {type} Data</h3>
      <p className="text-gray-500">No {type.toLowerCase()} entries have been saved to this project yet.</p>
    </div>
  );

  const handleExportData = (dataType: string, format: 'csv' | 'pdf') => {
    let data: any[] = [];
    let exportFunction: any = null;
    let title = '';

    switch (dataType) {
      case 'fmea':
        data = fmeaData;
        exportFunction = exportFmeaData;
        title = 'FMEA Analysis Report';
        break;
      case 'capa':
        data = capaData;
        exportFunction = exportCapaData;
        title = 'CAPA Analysis Report';
        break;
      case 'nonconformance':
        data = nonConformanceData;
        exportFunction = exportNonConformanceData;
        title = 'Non-Conformance Analysis Report';
        break;
      case 'changecontrol':
        data = changeControlData;
        exportFunction = exportChangeControlData;
        title = 'Change Control Analysis Report';
        break;
      default:
        return;
    }

    if (data.length === 0) {
      alert(`No ${dataType.toUpperCase()} data to export`);
      return;
    }

    exportFunction(data, format);
  };

  const renderContent = () => {
    if (loading) {
      return (
        <div className="flex justify-center items-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Loading project data...</span>
        </div>
      );
    }

    if (error) {
      return (
        <div className="text-center py-8">
          <p className="text-red-600">{error}</p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {/* Export Buttons */}
        <div className="flex justify-end space-x-2">
          {fmeaData.length > 0 && (
            <div className="relative group">
              <button className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 flex items-center">
                <i className="fa-solid fa-download mr-1"></i>
                Export FMEA
                <i className="fa-solid fa-chevron-down ml-1"></i>
              </button>
              <div className="absolute right-0 mt-2 w-40 bg-white rounded-md shadow-lg z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                <div className="py-1">
                  <button
                    onClick={() => handleExportData('fmea', 'csv')}
                    className="block w-full text-left px-3 py-1 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <i className="fa-solid fa-file-csv mr-1"></i>
                    CSV
                  </button>
                  <button
                    onClick={() => handleExportData('fmea', 'pdf')}
                    className="block w-full text-left px-3 py-1 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <i className="fa-solid fa-file-pdf mr-1"></i>
                    PDF
                  </button>
                </div>
              </div>
            </div>
          )}
          {capaData.length > 0 && (
            <div className="relative group">
              <button className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 flex items-center">
                <i className="fa-solid fa-download mr-1"></i>
                Export CAPA
                <i className="fa-solid fa-chevron-down ml-1"></i>
              </button>
              <div className="absolute right-0 mt-2 w-40 bg-white rounded-md shadow-lg z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                <div className="py-1">
                  <button
                    onClick={() => handleExportData('capa', 'csv')}
                    className="block w-full text-left px-3 py-1 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <i className="fa-solid fa-file-csv mr-1"></i>
                    CSV
                  </button>
                  <button
                    onClick={() => handleExportData('capa', 'pdf')}
                    className="block w-full text-left px-3 py-1 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <i className="fa-solid fa-file-pdf mr-1"></i>
                    PDF
                  </button>
                </div>
              </div>
            </div>
          )}
          {nonConformanceData.length > 0 && (
            <div className="relative group">
              <button className="bg-purple-300 text-gray-900 px-3 py-1 rounded text-sm hover:bg-purple-400 flex items-center">
                <i className="fa-solid fa-download mr-1"></i>
                Export NC
                <i className="fa-solid fa-chevron-down ml-1"></i>
              </button>
              <div className="absolute right-0 mt-2 w-40 bg-white rounded-md shadow-lg z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                <div className="py-1">
                  <button
                    onClick={() => handleExportData('nonconformance', 'csv')}
                    className="block w-full text-left px-3 py-1 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <i className="fa-solid fa-file-csv mr-1"></i>
                    CSV
                  </button>
                  <button
                    onClick={() => handleExportData('nonconformance', 'pdf')}
                    className="block w-full text-left px-3 py-1 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <i className="fa-solid fa-file-pdf mr-1"></i>
                    PDF
                  </button>
                </div>
              </div>
            </div>
          )}
          {changeControlData.length > 0 && (
            <div className="relative group">
              <button className="bg-orange-600 text-white px-3 py-1 rounded text-sm hover:bg-orange-700 flex items-center">
                <i className="fa-solid fa-download mr-1"></i>
                Export CC
                <i className="fa-solid fa-chevron-down ml-1"></i>
              </button>
              <div className="absolute right-0 mt-2 w-40 bg-white rounded-md shadow-lg z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                <div className="py-1">
                  <button
                    onClick={() => handleExportData('changecontrol', 'csv')}
                    className="block w-full text-left px-3 py-1 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <i className="fa-solid fa-file-csv mr-1"></i>
                    CSV
                  </button>
                  <button
                    onClick={() => handleExportData('changecontrol', 'pdf')}
                    className="block w-full text-left px-3 py-1 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <i className="fa-solid fa-file-pdf mr-1"></i>
                    PDF
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Tab Content */}
        {activeTab === 'fmea' && (fmeaData.length > 0 ? renderFmeaTable() : renderEmptyState('FMEA'))}
        {activeTab === 'capa' && (capaData.length > 0 ? renderCapaTable() : renderEmptyState('CAPA'))}
        {activeTab === 'nonconformance' && (nonConformanceData.length > 0 ? renderNonConformanceTable() : renderEmptyState('Non-Conformance'))}
        {activeTab === 'changecontrol' && (changeControlData.length > 0 ? renderChangeControlTable() : renderEmptyState('Change Control'))}
        
        {/* Project Summary */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mt-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Project Summary</h3>
          </div>
          <div className="px-6 py-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{fmeaData.length}</div>
                <div className="text-sm text-gray-600">FMEA Entries</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{capaData.length}</div>
                <div className="text-sm text-gray-600">CAPA Items</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-700">{nonConformanceData.length}</div>
                <div className="text-sm text-gray-600">Non-Conformances</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">{changeControlData.length}</div>
                <div className="text-sm text-gray-600">Change Controls</div>
              </div>
            </div>
            
            {/* Risk Indicators */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h4 className="text-sm font-medium text-gray-700 mb-3">Risk Indicators</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">High Severity FMEA:</span>
                  <span className="font-medium text-red-600">
                    {fmeaData.filter(item => item.severity >= 8).length}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Open CAPAs:</span>
                  <span className="font-medium text-orange-600">
                    {capaData.filter(item => item.status?.toLowerCase() === 'open').length}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Pending Changes:</span>
                  <span className="font-medium text-yellow-600">
                    {changeControlData.filter(item => item.approval_status?.toLowerCase() === 'pending').length}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-10 mx-auto p-5 border w-11/12 max-w-6xl shadow-lg rounded-md bg-white">
        <div className="mt-3">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-2xl font-bold text-gray-900">
                Project Data: {selectedProject?.name}
              </h3>
              <p className="text-sm text-gray-500 mt-1">
                View all saved data for this project
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <i className="fas fa-times text-xl"></i>
            </button>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200 mb-6">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.label}
                  {tab.count > 0 && (
                    <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      {tab.count}
                    </span>
                  )}
                </button>
              ))}
            </nav>
          </div>

          {/* Content */}
          <div className="max-h-96 overflow-y-auto">
            {renderContent()}
          </div>

          {/* Footer */}
          <div className="flex justify-end mt-6 pt-4 border-t border-gray-200">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectDataViewer; 