import React, { useState } from "react";
import CapaForm from "../components/CapaForm";

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

const exportFields = [
  { label: "CAPA ID", key: "id" },
  { label: "Corrective Actions", key: "correctiveAction" },
  { label: "Preventive Actions", key: "preventiveAction" },
  { label: "Action Owner(s)", key: "actionOwner" },
  { label: "Due Dates and Milestones", key: "dueDate" },
  { label: "Effectiveness Check Plan", key: "effectivenessCheckPlan" },
  { label: "Status Tracking", key: "status" },
  { label: "Link to FMEA or Risk Controls Update", key: "fmeaLink" },
  { label: "Regulatory Impact", key: "regulatoryImpact" },
  { label: "Closure Summary", key: "closureSummary" },
];

const CapaPage: React.FC = () => {
  const [issueDescription, setIssueDescription] = useState("");
  const [lastCapa, setLastCapa] = useState<Capa | null>(null);

  const handleCapaSubmit = (capa: Capa) => {
    setLastCapa(capa);
  };

  const handleExport = () => {
    if (!lastCapa) return;
    const row = exportFields.map(f => {
      let value = lastCapa[f.key as keyof Capa] || "";
      if (f.key === "dueDate" && lastCapa.milestones) {
        value = value + (lastCapa.milestones ? ", " + lastCapa.milestones : "");
      }
      if (f.key === "fmeaLink" && lastCapa.riskControlsUpdate) {
        value = value + (lastCapa.riskControlsUpdate ? ", " + lastCapa.riskControlsUpdate : "");
      }
      return `"${String(value).replace(/"/g, '""')}"`;
    });
    const csv = exportFields.map(f => f.label).join(",") + "\n" + row.join(",");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `capa_${lastCapa.id}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex pt-0">
      {/* Sidebar from HomePage */}
      <aside id="explorer-bar" className="w-64 bg-white border-r border-gray-200 overflow-y-auto">
        <div className="p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-gray-500">Medica Inc.</h2>
            <button className="text-gray-400 hover:text-gray-600">
              <i className="fa-solid fa-gear"></i>
            </button>
          </div>
          {/* Product A */}
          <div id="product-a" className="mb-3">
            <div className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-md cursor-pointer">
                <div className="flex items-center">
                <i className="fa-solid fa-chevron-down text-xs mr-2 text-gray-500"></i>
                <span className="text-base font-semibold">Pacemaker2025</span>
              </div>
              <div className="text-gray-400">
                <i className="fa-solid fa-ellipsis-vertical"></i>
              </div>
            </div>
            {/* Risk Management Folder */}
            <div className="ml-4 mt-2 mb-2">
              <div className="flex items-center text-sm font-semibold text-gray-700 mb-1">
                <i className="fa-solid fa-folder-open mr-2 text-blue-400"></i>
                <i className="fa-solid fa-chevron-down text-xs mr-2 text-gray-500"></i>
                Risk Management
              </div>
              <div className="ml-6 space-y-1">
                <div className="flex items-center py-1 px-3 text-blue-700 bg-blue-50 rounded">
                  <i className="fa-regular fa-file-lines mr-2"></i>
                  <span>Design FMEA</span>
                </div>
                <div className="flex items-center py-1 px-3 text-gray-700 hover:bg-gray-50 rounded">
                  <i className="fa-regular fa-file-lines mr-2"></i>
                  <span>Process FMEA</span>
                </div>
                <div className="flex items-center py-1 px-3 text-gray-700 hover:bg-gray-50 rounded">
                  <i className="fa-regular fa-file-lines mr-2"></i>
                  <span>User FMEA</span>
                </div>
              </div>
            </div>
          </div>
          {/* Design Control Section (styled like Risk Management) */}
          <div className="ml-0 mt-2 mb-4">
            <div className="flex items-center text-sm font-semibold text-gray-700 mb-1">
              <i className="fa-solid fa-folder-open mr-2 text-blue-400"></i>
              <i className="fa-solid fa-chevron-down text-xs mr-2 text-gray-500"></i>
              Design Control
            </div>
            <div className="ml-6 space-y-1">
              <div className="flex items-center py-1 px-3 text-blue-700 bg-blue-50 rounded">
                <i className="fa-regular fa-file-lines mr-2"></i>
                <span>Traceability Matrix</span>
              </div>
              <div className="flex items-center py-1 px-3 text-gray-700 hover:bg-gray-50 rounded">
                <i className="fa-regular fa-file-lines mr-2"></i>
                <span>Design Inputs</span>
              </div>
              <div className="flex items-center py-1 px-3 text-gray-700 hover:bg-gray-50 rounded">
                <i className="fa-regular fa-file-lines mr-2"></i>
                <span>Design Outputs</span>
              </div>
            </div>
          </div>
        </div>
      </aside>
      {/* Main Content */}
      <div className="flex-1 pt-14 flex flex-col items-center">
        <div className="w-full max-w-3xl mx-auto mb-8">
          <div className="bg-white rounded-2xl shadow-md p-8 mb-6">
            <h1 className="text-2xl font-bold mb-2 text-primary-700">Create New CAPA</h1>
            <p className="text-gray-600 mb-4">Document and manage Corrective and Preventive Actions (CAPA) for quality events.</p>
            <label className="block mb-2 font-medium text-gray-700" htmlFor="issueDescriptionInput">
              Issue Description
            </label>
            <textarea
              id="issueDescriptionInput"
              className="w-full p-3 border rounded-lg mb-2 focus:outline-none focus:ring-2 focus:ring-primary-300"
              placeholder="Describe the issue or nonconformity..."
              value={issueDescription}
              onChange={e => setIssueDescription(e.target.value)}
              rows={3}
            />
            <button
              className="mt-2 bg-primary-600 hover:bg-primary-700 text-white px-6 py-2 rounded-lg font-semibold shadow"
              onClick={() => {
                const form = document.getElementById('capa-form');
                if (form) {
                  form.scrollIntoView({ behavior: 'smooth', block: 'start' });
                  const firstInput = form.querySelector('input, textarea, select') as HTMLElement;
                  if (firstInput) firstInput.focus();
                }
              }}
            >
              Generate CAPA
            </button>
          </div>
          <div className="bg-white rounded-2xl shadow-md p-8">
            <CapaForm prefillIssueDescription={issueDescription} onSubmit={handleCapaSubmit} />
              </div>
          {lastCapa && (
            <div className="bg-white rounded-2xl shadow-md p-8 mt-8">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-primary-700">Latest CAPA Summary</h2>
                <button
                  onClick={handleExport}
                  className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm font-medium shadow"
                >
                  Export CAPA
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full border rounded-xl bg-white shadow-sm text-sm">
                  <thead className="bg-gray-100">
                    <tr>
                      {exportFields.map(f => (
                        <th key={f.key} className="p-2 border">{f.label}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      {exportFields.map(f => {
                        let value = lastCapa[f.key as keyof Capa] || "";
                        if (f.key === "dueDate" && lastCapa.milestones) {
                          value = value + (lastCapa.milestones ? ", " + lastCapa.milestones : "");
                        }
                        if (f.key === "fmeaLink" && lastCapa.riskControlsUpdate) {
                          value = value + (lastCapa.riskControlsUpdate ? ", " + lastCapa.riskControlsUpdate : "");
                        }
                        return <td key={f.key} className="p-2 border">{value}</td>;
                      })}
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CapaPage; 