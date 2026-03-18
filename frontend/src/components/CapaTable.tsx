import React from 'react';

interface Capa {
  id: string;
  issueDescription: string;
  source: string;
  detectionDate: string;
  severity: string;
  rootCause: string;
  correctiveAction: string;
  preventiveAction: string;
  actionOwner: string;
  dueDate: string;
  status: string;
  effectivenessCheckPlan: string;
  fmeaLink: string;
  regulatoryImpact: string;
  closureSummary: string;
  milestones: string;
  riskControlsUpdate: string;
}

interface CapaTableProps {
  capas: Capa[];
}

const CapaTable: React.FC<CapaTableProps> = ({ capas }) => {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'open':
        return 'bg-red-100 text-red-800';
      case 'in progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'closed':
        return 'bg-green-100 text-green-800';
      case 'ineffective':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-red-100 text-red-800';
      case 'high':
        return 'bg-orange-100 text-orange-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="mt-6 max-w-7xl mx-auto">
      <h2 className="text-xl font-semibold mb-4 text-gray-800">CAPA Records</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full border rounded-xl bg-white shadow-sm text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="p-3 border text-left font-medium text-gray-700">CAPA ID</th>
              <th className="p-3 border text-left font-medium text-gray-700">Issue Description</th>
              <th className="p-3 border text-left font-medium text-gray-700">Source</th>
              <th className="p-3 border text-left font-medium text-gray-700">Detection Date</th>
              <th className="p-3 border text-left font-medium text-gray-700">Severity</th>
              <th className="p-3 border text-left font-medium text-gray-700">Status</th>
              <th className="p-3 border text-left font-medium text-gray-700">Action Owner</th>
              <th className="p-3 border text-left font-medium text-gray-700">Due Date</th>
              <th className="p-3 border text-left font-medium text-gray-700">FMEA Link</th>
              <th className="p-3 border text-left font-medium text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody>
            {capas.map((capa) => (
              <tr key={capa.id} className="hover:bg-gray-50 border-b">
                <td className="p-3 border font-medium text-gray-900">CAPA-{capa.id.slice(-6)}</td>
                <td className="p-3 border">
                  <div className="max-w-xs">
                    <p className="text-gray-900 font-medium truncate">{capa.issueDescription}</p>
                    {capa.rootCause && (
                      <p className="text-gray-500 text-xs mt-1 truncate">Root Cause: {capa.rootCause}</p>
                    )}
                  </div>
                </td>
                <td className="p-3 border">
                  <span className="px-2 py-1 text-xs rounded bg-blue-100 text-blue-800">{capa.source}</span>
                </td>
                <td className="p-3 border text-gray-600">{capa.detectionDate}</td>
                <td className="p-3 border">
                  <span className={`px-2 py-1 text-xs rounded font-medium ${getSeverityColor(capa.severity)}`}>
                    {capa.severity}
                  </span>
                </td>
                <td className="p-3 border">
                  <span className={`px-2 py-1 text-xs rounded font-medium ${getStatusColor(capa.status)}`}>
                    {capa.status}
                  </span>
                </td>
                <td className="p-3 border text-gray-600">{capa.actionOwner}</td>
                <td className="p-3 border text-gray-600">{capa.dueDate}</td>
                <td className="p-3 border">
                  {capa.fmeaLink ? (
                    <span className="px-2 py-1 text-xs rounded bg-purple-200 text-purple-800">{capa.fmeaLink}</span>
                  ) : (
                    <span className="text-gray-400">-</span>
                  )}
                </td>
                <td className="p-3 border">
                  <button className="text-blue-600 hover:text-blue-800 font-medium text-sm">
                    <i className="fa-solid fa-eye mr-1"></i> View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Detailed CAPA Information Modal/Expansion */}
      {capas.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">Detailed CAPA Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {capas.map((capa) => (
              <div key={capa.id} className="bg-white p-6 rounded-lg border shadow-sm">
                <div className="flex justify-between items-start mb-4">
                  <h4 className="text-lg font-semibold text-gray-800">CAPA-{capa.id.slice(-6)}</h4>
                  <span className={`px-3 py-1 text-sm rounded font-medium ${getStatusColor(capa.status)}`}>
                    {capa.status}
                  </span>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <h5 className="font-medium text-gray-700 mb-1">Issue Description</h5>
                    <p className="text-gray-600 text-sm">{capa.issueDescription}</p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h5 className="font-medium text-gray-700 mb-1">Corrective Actions</h5>
                      <p className="text-gray-600 text-sm">{capa.correctiveAction}</p>
                    </div>
                    <div>
                      <h5 className="font-medium text-gray-700 mb-1">Preventive Actions</h5>
                      <p className="text-gray-600 text-sm">{capa.preventiveAction || 'Not specified'}</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h5 className="font-medium text-gray-700 mb-1">Action Owner</h5>
                      <p className="text-gray-600 text-sm">{capa.actionOwner}</p>
                    </div>
                    <div>
                      <h5 className="font-medium text-gray-700 mb-1">Due Date</h5>
                      <p className="text-gray-600 text-sm">{capa.dueDate}</p>
                    </div>
                  </div>

                  {capa.milestones && (
                    <div>
                      <h5 className="font-medium text-gray-700 mb-1">Milestones</h5>
                      <p className="text-gray-600 text-sm">{capa.milestones}</p>
                    </div>
                  )}

                  {capa.effectivenessCheckPlan && (
                    <div>
                      <h5 className="font-medium text-gray-700 mb-1">Effectiveness Check Plan</h5>
                      <p className="text-gray-600 text-sm">{capa.effectivenessCheckPlan}</p>
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-4">
                    {capa.fmeaLink && (
                      <div>
                        <h5 className="font-medium text-gray-700 mb-1">FMEA Link</h5>
                        <span className="px-2 py-1 text-xs rounded bg-purple-200 text-purple-800">{capa.fmeaLink}</span>
                      </div>
                    )}
                    {capa.riskControlsUpdate && (
                      <div>
                        <h5 className="font-medium text-gray-700 mb-1">Risk Controls Update</h5>
                        <p className="text-gray-600 text-sm">{capa.riskControlsUpdate}</p>
                      </div>
                    )}
                  </div>

                  {capa.regulatoryImpact && (
                    <div>
                      <h5 className="font-medium text-gray-700 mb-1">Regulatory Impact</h5>
                      <p className="text-gray-600 text-sm">{capa.regulatoryImpact}</p>
                    </div>
                  )}

                  {capa.closureSummary && (
                    <div>
                      <h5 className="font-medium text-gray-700 mb-1">Closure Summary</h5>
                      <p className="text-gray-600 text-sm">{capa.closureSummary}</p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default CapaTable; 